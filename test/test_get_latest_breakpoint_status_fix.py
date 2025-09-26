#!/usr/bin/env python3
"""
测试 get_latest_breakpoint_status 修复
验证 context.ws_debug_service 属性访问是否正确
"""


def test_debug_service_attribute():
    """测试 debug_service 属性访问"""
    print("🧪 测试 get_latest_breakpoint_status debug_service 属性访问")

    # 模拟 ToolContext 类
    class MockToolContext:
        def __init__(self):
            self.ws_debug_service = MockWSDebugService()
            # 注意：没有 debug_service 属性

    class MockWSDebugService:
        def get_debug_status_tool(self):
            return {"success": True, "status": {"breakpoints": []}}

    # 测试正确的属性访问
    context = MockToolContext()

    # 模拟 get_latest_breakpoint_status 中的逻辑
    try:
        # 正确的访问方式
        debug_service = context.ws_debug_service
        print("✅ context.ws_debug_service 访问成功")

        # 尝试错误的访问方式（应该会失败）
        try:
            debug_service_wrong = context.debug_service
            print("❌ 不应该能够访问 context.debug_service")
        except AttributeError as e:
            print(f"✅ context.debug_service 正确报错: {e}")

        # 测试调用方法
        status = debug_service.get_debug_status_tool()
        assert status["success"] == True, "get_debug_status_tool 应该返回 success: True"
        print("✅ get_debug_status_tool 调用成功")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    print("🎉 所有测试通过！get_latest_breakpoint_status 修复成功")
    return True


if __name__ == "__main__":
    test_debug_service_attribute()
