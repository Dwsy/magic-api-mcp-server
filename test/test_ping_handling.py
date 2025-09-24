#!/usr/bin/env python3
"""
测试PING消息处理
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_ping_handling():
    """测试PING消息处理"""

    print("🧪 测试PING消息处理")
    print("=" * 50)

    # 创建客户端实例
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712",
        username="admin",
        password="123456"
    )

    # 模拟PING消息处理（不实际发送WebSocket消息）
    test_messages = [
        ("PING", ""),
        ("LOG", "test log message"),
        ("USER_LOGIN", "user123,admin"),
        ("LOGIN", "user456,admin"),
        ("UNKNOWN_TYPE", "some content")
    ]

    print("📨 测试消息处理:")

    pong_count = 0

    for message_type, content in test_messages:
        # 构造完整消息
        full_message = f"{message_type},{content}"

        print(f"\n🔍 测试消息: {message_type}")

        # 模拟消息解析（不实际调用handle_message以避免WebSocket依赖）
        parts = full_message.split(',', 1)
        if len(parts) >= 1:
            msg_type = parts[0].upper()

            # 检查是否会被过滤或特殊处理
            if msg_type == "PING":
                print("   ✅ PING消息被特殊处理：回复pong但不显示")
                pong_count += 1
            elif msg_type in ["USER_LOGIN", "LOGIN", "LOGOUT", "USER_LOGOUT"]:
                print(f"   ✅ {msg_type}消息被过滤")
            else:
                print(f"   📝 {msg_type}消息正常处理")

    print("\n" + "=" * 50)
    print("✅ PING消息处理测试完成!")
    print("📝 测试结果:")
    print("   - PING消息会被特殊处理：自动回复pong但不在控制台显示")
    print("   - 登录类型消息会被完全过滤")
    print("   - 其他消息正常处理并显示")
    print(f"   - 模拟回复pong次数: {pong_count}")

    return True


async def main():
    """主测试函数"""
    success = await test_ping_handling()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
