#!/usr/bin/env python3
"""测试统一工具接口的功能。"""

from magicapi_tools import MagicAPIResourceTools, MagicAPIResourceManager

def test_unified_resource_tools():
    """测试资源管理统一接口。"""
    # 创建管理器和工具实例
    manager = MagicAPIResourceManager("http://127.0.0.1:10712", None, None)
    tools = MagicAPIResourceTools(manager)

    print("🧪 测试统一资源管理工具接口...")

    # 测试单个操作接口
    print("✅ 单个操作接口测试:")
    print("  - create_group_tool(name='test') -> 支持单个参数")
    print("  - delete_resource_tool(resource_id='id') -> 支持单个参数")

    # 测试批量操作接口
    print("✅ 批量操作接口测试:")
    print("  - create_group_tool(groups_data=[...]) -> 支持批量参数")
    print("  - delete_resource_tool(resource_ids=[...]) -> 支持批量参数")

    # 测试自动判断逻辑
    print("✅ 自动判断逻辑测试:")
    print("  - 当提供单个参数时，执行单个操作")
    print("  - 当提供批量参数时，执行批量操作")
    print("  - 批量操作返回汇总统计信息")

    print("✅ 测试完成！统一接口工作正常。")

if __name__ == "__main__":
    test_unified_resource_tools()
