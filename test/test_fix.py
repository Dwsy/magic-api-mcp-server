#!/usr/bin/env python3
"""
测试断点命令修复的脚本
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_breakpoint_commands():
    """测试断点命令是否正常工作"""
    print("🧪 测试断点命令修复...")

    # 创建客户端（不连接WebSocket，仅测试断点操作）
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712",
        username="admin",
        password="123456"
    )

    # 模拟连接状态和WebSocket（正常情况下WebSocket连接后会设置）
    client.connected = True
    # 创建一个模拟的WebSocket对象，避免实际网络连接
    class MockWebSocket:
        async def send(self, message):
            print(f"📤 发送消息: {message}")
            pass

    client.websocket = MockWebSocket()

    try:
        # 测试设置断点
        print("1. 测试设置断点...")
        await client.set_breakpoint(5)
        print(f"   断点列表: {client.breakpoints}")

        # 测试设置另一个断点
        print("2. 测试设置另一个断点...")
        await client.set_breakpoint(10)
        print(f"   断点列表: {client.breakpoints}")

        # 测试移除断点
        print("3. 测试移除断点...")
        await client.remove_breakpoint(5)
        print(f"   断点列表: {client.breakpoints}")

        # 测试恢复断点
        print("4. 测试恢复断点执行...")
        await client.resume_breakpoint()
        print("   恢复断点执行完成")

        # 测试单步执行
        print("5. 测试单步执行...")
        await client.step_over()
        print("   单步执行完成")

        print("✅ 所有断点命令测试通过！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_preprocessing():
    """测试命令预处理功能"""
    print("\n🧪 测试命令预处理...")

    from magic_api_debug_client import preprocess_command

    test_cases = [
        ("test api/test", "test /api/test"),
        ("test 5,10", "test 5,10"),  # 不应该改变断点参数
        ("call GET api", "call GET api"),  # 不应该改变
        ("breakpoint 15", "breakpoint 15"),  # 不应该改变
    ]

    for input_cmd, expected in test_cases:
        result = preprocess_command(input_cmd)
        if result == expected:
            print(f"✅ '{input_cmd}' -> '{result}'")
        else:
            print(f"❌ '{input_cmd}' -> '{result}' (期望: '{expected}')")
            return False

    print("✅ 命令预处理测试通过！")
    return True


async def main():
    """主测试函数"""
    print("🚀 断点命令修复测试")
    print("=" * 40)

    # 测试命令预处理
    preprocessing_ok = test_preprocessing()

    # 测试断点命令
    breakpoint_ok = await test_breakpoint_commands()

    print("\n" + "=" * 40)
    if preprocessing_ok and breakpoint_ok:
        print("🎉 所有测试通过！断点命令修复成功。")
        return True
    else:
        print("❌ 部分测试失败！")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
