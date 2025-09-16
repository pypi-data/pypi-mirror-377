"""
MongoDB生物入侵研究MCP服务器包
提供自然语言查询MongoDB数据库的功能
"""

from .mcp_mongodb_server import main, run_server

__version__ = "0.1.1"
__all__ = ["main", "run_server"]
