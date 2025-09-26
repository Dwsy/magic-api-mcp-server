#!/usr/bin/env python3
"""测试search_api_scripts工具是否正确返回API名称和完整路径。"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magicapi_tools.tools.search import SearchTools
from magicapi_mcp.tool_registry import ToolContext
from magicapi_mcp.settings import MagicAPISettings


def test_search_with_name_and_path():
    """测试搜索功能是否返回名称和完整路径。"""

    # 创建工具上下文
    settings = MagicAPISettings()
    context = ToolContext(settings=settings)

    # 创建搜索工具实例并注册
    search_tools = SearchTools()

    # 创建一个简单的MCP应用模拟
    class MockMCPApp:
        def __init__(self):
            self.tools = {}

        def tool(self, *args, **kwargs):
            def decorator(func):
                # 将函数绑定到MockMCPApp实例
                self.tools[kwargs.get('name', func.__name__)] = func
                return func
            return decorator

    mcp_app = MockMCPApp()
    search_tools.register_tools(mcp_app, context)

    # 测试搜索关键词 "set"
    try:
        # 调用注册的工具函数
        search_func = mcp_app.tools.get('search_api_scripts')
        if not search_func:
            print("❌ 找不到search_api_scripts工具")
            return

        result = search_func(keyword="set", limit=3)
        print("搜索结果:")
        print(f"关键词: {result.get('keyword')}")
        print(f"总结果数: {result.get('total_results')}")
        print(f"限制: {result.get('limit')}")

        results = result.get('results', [])
        if results:
            print("\n前3个结果:")
            for i, item in enumerate(results, 1):
                print(f"{i}. ID: {item.get('id')}")
                print(f"   名称: {item.get('name')}")
                print(f"   完整路径: {item.get('full_path')}")
                print(f"   行号: {item.get('line')}")
                print(f"   文本: {item.get('text')[:100]}...")
                print()
        else:
            print("没有找到搜索结果")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_search_with_name_and_path()
