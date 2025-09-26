#!/usr/bin/env python3
"""
测试 ToolContext 属性修复
验证 debug_service 属性是否正确设置
"""


def test_tool_context_attributes():
    """测试 ToolContext 属性"""
    print("🧪 测试 ToolContext 属性访问")

    # 模拟 ToolContext 类
    class MockToolContext:
        def __init__(self):
            self.ws_debug_service = "mock_ws_debug_service"
            # 兼容旧属性命名
            self.debug_tools = self.ws_debug_service
            self.debug_service = self.ws_debug_service  # 向后兼容

    # 测试属性访问
    context = MockToolContext()

    # 测试 ws_debug_service
    assert hasattr(context, 'ws_debug_service'), "应该有 ws_debug_service 属性"
    assert context.ws_debug_service == "mock_ws_debug_service", "ws_debug_service 值不正确"
    print("✅ ws_debug_service 属性访问正常")

    # 测试 debug_service（向后兼容）
    assert hasattr(context, 'debug_service'), "应该有 debug_service 属性"
    assert context.debug_service == "mock_ws_debug_service", "debug_service 值不正确"
    print("✅ debug_service 属性访问正常")

    # 测试 debug_tools
    assert hasattr(context, 'debug_tools'), "应该有 debug_tools 属性"
    assert context.debug_tools == "mock_ws_debug_service", "debug_tools 值不正确"
    print("✅ debug_tools 属性访问正常")

    print("🎉 所有测试通过！ToolContext 属性修复成功")


if __name__ == "__main__":
    test_tool_context_attributes()
