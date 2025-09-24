#!/usr/bin/env python3
"""MCP服务入口点"""

from magicapi_mcp.magicapi_assistant import create_app

# 创建全局 mcp 对象供 fastmcp 命令使用
mcp = create_app()

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)