#!/usr/bin/env python3
"""调试export_resource_tree问题的测试脚本"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from magicapi_tools.utils.resource_manager import MagicAPIResourceManager, MagicAPIResourceTools
from magicapi_mcp.settings import DEFAULT_SETTINGS

def test_get_resource_tree():
    """测试get_resource_tree_tool方法"""
    try:
        # 创建资源管理器
        settings = DEFAULT_SETTINGS
        manager = MagicAPIResourceManager(
            settings.base_url,
            settings.username if settings.auth_enabled else None,
            settings.password if settings.auth_enabled else None,
        )

        # 创建资源工具
        resource_tools = MagicAPIResourceTools(manager)

        # 测试get_resource_tree_tool
        print("开始测试get_resource_tree_tool...")
        result = resource_tools.get_resource_tree_tool(kind="api")
        print(f"结果类型: {type(result)}")
        if "error" in result:
            print(f"错误: {result['error']}")
        else:
            print(f"成功: kind={result.get('kind')}, count={result.get('count')}")

        # 测试export_resource_tree_tool
        print("\n开始测试export_resource_tree_tool...")
        export_result = resource_tools.export_resource_tree_tool(kind="api", format="json")
        print(f"导出结果类型: {type(export_result)}")
        if "error" in export_result:
            print(f"导出错误: {export_result['error']}")
        else:
            print(f"导出成功: format={export_result.get('format')}, success={export_result.get('success')}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_resource_tree()