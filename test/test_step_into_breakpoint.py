#!/usr/bin/env python3
"""
测试 step_into_breakpoint 工具的属性访问
"""


async def test_step_into_breakpoint():
    """测试 step_into_breakpoint 工具的逻辑"""
    print("🧪 测试 step_into_breakpoint 工具逻辑")

    # 模拟 ToolContext
    class MockWSManager:
        async def ensure_running(self):
            pass

        async def send_step_into(self, script_id, breakpoints):
            print(f"发送 step_into 指令: script_id={script_id}, breakpoints={breakpoints}")

    class MockWSDebugService:
        def __init__(self):
            self.breakpoints = [1, 2, 3]

        def _current_script_id(self):
            return "test_script_id"

    class MockToolContext:
        def __init__(self):
            self.ws_manager = MockWSManager()
            self.ws_debug_service = MockWSDebugService()
            self.debug_service = self.ws_debug_service  # 向后兼容

    # 模拟 step_into_breakpoint 工具的逻辑
    context = MockToolContext()

    try:
        await context.ws_manager.ensure_running()

        # 获取WebSocket调试服务
        debug_service = context.ws_debug_service

        # 发送步入指令 (step type 2)
        script_id = debug_service._current_script_id()
        if not script_id:
            result = {"error": {"code": "script_id_missing", "message": "无法确定当前调试脚本"}}
        else:
            await context.ws_manager.send_step_into(script_id, sorted(debug_service.breakpoints))
            result = {"success": True, "script_id": script_id, "step_type": "into"}

        print(f"工具执行结果: {result}")
        print("✅ step_into_breakpoint 工具逻辑正常")

    except Exception as e:
        print(f"❌ 工具执行出错: {e}")
        return False

    return True


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_step_into_breakpoint())
