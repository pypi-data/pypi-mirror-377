import os
import json
import requests
import torch
import asyncio
from typing import Dict, List, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
# 1. 按MCP 1.13.1规范导入Server
from mcp.server import Server
from mcp.types import Prompt, PromptArgument, PromptMessage, GetPromptResult, TextContent

# -------------------------- 环境配置与核心处理器 --------------------------
load_dotenv()

class MongoNLQueryHandler:
    """MongoDB自然语言查询核心处理器"""
    def __init__(self):
        # MongoDB配置
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("MONGO_DB_NAME", "中国生物入侵研究")
        self.col_name = os.getenv("MONGO_COLLECTION", "生物入侵研究")
        self._init_mongo()

        # 模型配置
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "dengcao/Qwen3-Embedding-8B:Q5_K_M")
        self.reranker_model_name = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-large")
        self.reranker_model = None
        self.reranker_tokenizer = None
        self._init_reranker()

        # DeepSeek API配置
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

    def _init_mongo(self):
        """初始化MongoDB连接"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.col_name]
            self.client.admin.command("ping")
            
            print(f"✅ 连接MongoDB成功：{self.db_name} -> {self.col_name}")
        except Exception as e:
            raise RuntimeError(f"MongoDB连接失败：{str(e)}")

    def _init_reranker(self):
        """初始化重排序模型"""
        try:
            self.reranker_tokenizer = AutoTokenizer.from_pretrained(self.reranker_model_name)
            self.reranker_model = AutoModelForSequenceClassification.from_pretrained(self.reranker_model_name)
            self.reranker_model.eval()
            print(f"✅ 加载重排序模型成功：{self.reranker_model_name}")
        except Exception as e:
            print(f"⚠️  重排序模型加载失败：{str(e)}（将使用原生向量排序）")

    async def get_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=10
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            raise RuntimeError(f"向量生成失败：{str(e)}")

    async def query(self, query_text: str, limit: int = 5, use_reranker: bool = True) -> Dict:
        """自然语言查询MongoDB"""
        # 生成查询向量
        query_vec = await self.get_embedding(query_text)
        
        # 向量搜索
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": query_vec,
                    "path": "embedding",
                    "limit": limit * 2
                }
            },
            {"$project": {"embedding": 0, "vector_score": {"$meta": "vectorSearchScore"}}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        # 重排序
        if use_reranker and self.reranker_model and len(results) > 1:
            doc_contents = [str(doc.get("content", "")) for doc in results]
            pairs = [[query_text, c] for c in doc_contents]
            
            with torch.no_grad():
                inputs = self.reranker_tokenizer(
                    pairs, padding=True, truncation=True, return_tensors="pt", max_length=512
                )
                scores = self.reranker_model(**inputs).logits.squeeze().tolist()
            
            for idx, score in enumerate(scores):
                results[idx]["rerank_score"] = float(score)
            results.sort(key=lambda x: x["rerank_score"], reverse=True)
            results = results[:limit]
        
        return {
            "status": "success",
            "query": query_text,
            "count": len(results),
            "results": results
        }

    async def enhance_with_deepseek(self, query: str, result: Dict) -> Dict:
        """用DeepSeek增强结果"""
        if not self.deepseek_api_key:
            result["enhance_msg"] = "未配置DeepSeek API Key，跳过增强"
            return result
        
        try:
            prompt = f"为查询「{query}」的结果添加1-2句解释（新增enhanced_info字段）：\n{json.dumps(result['results'])}"
            response = requests.post(
                self.deepseek_api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.deepseek_api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=15
            )
            response.raise_for_status()
            result["results"] = json.loads(response.json()["choices"][0]["message"]["content"])
            result["enhance_msg"] = "增强成功"
            return result
        except Exception as e:
            result["enhance_msg"] = f"增强失败：{str(e)}"
            return result

# -------------------------- 2. 实例化MCP服务器（按1.13.1规范） --------------------------
server = Server("mongodb-bio-invasion-server")

# -------------------------- 3. 初始化处理器实例 --------------------------
mongo_handler = MongoNLQueryHandler()

# -------------------------- 4. 工具注册 --------------------------
@server.list_tools()
async def list_tools() -> list:
    """返回可用工具列表"""
    return [
        {
            "name": "text_to_vector",
            "description": "将文本转换为768维嵌入向量（基于Qwen3-Embedding模型）",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "需转换的文本（建议≤512字符）"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "query_mongo_nl",
            "description": "用自然语言查询生物入侵研究数据库，支持向量搜索和结果重排序",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_text": {
                        "type": "string",
                        "description": "自然语言查询语句"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量（1-20）",
                        "default": 5
                    },
                    "use_reranker": {
                        "type": "boolean",
                        "description": "是否使用BGE模型重排序",
                        "default": True
                    },
                    "enhance": {
                        "type": "boolean",
                        "description": "是否用DeepSeek增强结果",
                        "default": False
                    }
                },
                "required": ["query_text"]
            }
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """调用工具"""
    if name == "text_to_vector":
        text = arguments.get("text", "")
        try:
            vector = await mongo_handler.get_embedding(text)
            return [{
                "type": "text",
                "text": json.dumps({
                    "status": "success",
                    "text": text,
                    "vector": vector,
                    "dimension": len(vector)
                }, ensure_ascii=False)
            }]
        except Exception as e:
            return [{
                "type": "text",
                "text": json.dumps({
                    "status": "error",
                    "error": str(e)
                }, ensure_ascii=False)
            }]
    
    elif name == "query_mongo_nl":
        query_text = arguments.get("query_text", "")
        limit = arguments.get("limit", 5)
        use_reranker = arguments.get("use_reranker", True)
        enhance = arguments.get("enhance", False)
        
        try:
            result = await mongo_handler.query(query_text, limit, use_reranker)
            if enhance:
                result = await mongo_handler.enhance_with_deepseek(query_text, result)
            return [{
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False)
            }]
        except Exception as e:
            return [{
                "type": "text",
                "text": json.dumps({
                    "status": "error",
                    "query": query_text,
                    "error": str(e)
                }, ensure_ascii=False)
            }]
    
    else:
        return [{
            "type": "text",
            "text": json.dumps({
                "status": "error",
                "error": f"工具 '{name}' 未找到"
            }, ensure_ascii=False)
        }]

# -------------------------- 5. 提示功能实现 --------------------------
@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """返回所有可用的提示模板"""
    return [
        Prompt(
            name="species_query",
            description="查询特定入侵物种的详细信息",
            arguments=[
                PromptArgument(
                    name="species_name",
                    description="入侵物种名称",
                    required=True
                )
            ]
        ),
        Prompt(
            name="invasion_path",
            description="分析入侵物种的传播路径和方式",
            arguments=[
                PromptArgument(
                    name="species_name",
                    description="入侵物种名称",
                    required=True
                )
            ]
        ),
        Prompt(
            name="impact_assessment",
            description="评估入侵物种的生态和经济影响",
            arguments=[
                PromptArgument(
                    name="species_name",
                    description="入侵物种名称",
                    required=True
                )
            ]
        ),
        Prompt(
            name="control_measures",
            description="查询入侵物种的防治措施和方法",
            arguments=[
                PromptArgument(
                    name="species_name",
                    description="入侵物种名称",
                    required=True
                )
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
    """根据提示名称和参数获取具体的提示内容"""
    if not arguments:
        arguments = {}
    
    species_name = arguments.get("species_name", "")
    
    if name == "species_query":
        return GetPromptResult(
            description=f"查询{species_name}的详细信息",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"请查询关于{species_name}的详细信息，包括其生物学特性、分布范围、入侵历史和防治措施。"
                    )
                )
            ]
        )
    
    elif name == "invasion_path":
        return GetPromptResult(
            description=f"分析{species_name}的入侵路径",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"请分析{species_name}的入侵路径和传播方式，包括其原产地、入侵途径、扩散机制和主要传播区域。"
                    )
                )
            ]
        )
    
    elif name == "impact_assessment":
        return GetPromptResult(
            description=f"评估{species_name}的影响",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"请评估{species_name}对生态系统和经济的影响，包括其对本地物种的影响、生态破坏程度、经济损失和潜在风险。"
                    )
                )
            ]
        )
    
    elif name == "control_measures":
        return GetPromptResult(
            description=f"查询{species_name}的防治措施",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"请查询{species_name}的防治措施和方法，包括物理防治、化学防治、生物防治和综合管理策略。"
                    )
                )
            ]
        )
    
    else:
        return GetPromptResult(
            description="提示未找到",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"提示 '{name}' 未找到，请使用 list_prompts 查看可用提示。"
                    )
                )
            ]
        )

# -------------------------- 6. 按规范启动服务器 --------------------------
async def run_server():
    print("\n🚀 MCP服务器启动中...")
    print(f"服务名称: {server.name}")
    print("可用工具: text_to_vector, query_mongo_nl, list_tools, get_tool_definition")
    print("可用提示: species_query, invasion_path, impact_assessment, control_measures")
    await server.run_stdio_async()  # 使用MCP 1.13.1的标准启动方式

def main():
    """主函数，用于命令行执行"""
    asyncio.run(run_server())

if __name__ == "__main__":
    main()  # 异步运行服务器
