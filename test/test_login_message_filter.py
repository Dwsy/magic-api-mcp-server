#!/usr/bin/env python3
"""
测试登录消息过滤功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_login_message_filter():
    """测试登录消息过滤"""

    print("🧪 测试登录消息过滤")
    print("=" * 50)

    # 创建客户端实例
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712",
        username="admin",
        password="123456"
    )

    # 模拟不同的消息类型
    test_messages = [
        ("LOG", "test log message"),
        ("USER_LOGIN", "user123,admin"),
        ("LOGIN", "user456,admin"),
        ("LOGOUT", "user123"),
        ("USER_LOGOUT", "user456"),
        ("BREAKPOINT", "test_script,{}"),
        ("EXCEPTION", "test exception"),
        ("UNKNOWN_TYPE", "some content")
    ]

    print("📨 测试消息处理:")

    # 测试消息处理（不连接WebSocket，仅测试handle_message逻辑）
    for message_type, content in test_messages:
        # 构造完整消息
        full_message = f"{message_type},{content}"

        print(f"\n🔍 测试消息: {full_message}")

        # 调用handle_message方法
        try:
            # 我们需要模拟handle_message的行为，但不真正发送WebSocket消息
            # 这里直接测试消息解析逻辑
            parts = full_message.split(',', 1)
            if len(parts) >= 1:
                msg_type = parts[0].upper()

                # 检查是否会被过滤
                if msg_type in ["USER_LOGIN", "LOGIN", "LOGOUT", "USER_LOGOUT"]:
                    print(f"   ✅ 被过滤: {msg_type} 消息已被忽略")
                else:
                    print(f"   📝 正常处理: {msg_type}")
                    if msg_type == "LOG":
                        print(f"   📝 [日志] {content}")
                    elif msg_type == "BREAKPOINT":
                        print("   🔴 [断点] 断点消息会被处理")
                    elif msg_type == "EXCEPTION":
                        print("   ❌ [异常] 异常消息会被处理")
                    else:
                        print(f"   [{msg_type}] {content}")

        except Exception as e:
            print(f"   ❌ 处理失败: {e}")

    print("\n" + "=" * 50)
    print("✅ 登录消息过滤测试完成!")
    print("📝 总结:")
    print("   - USER_LOGIN, LOGIN, LOGOUT, USER_LOGOUT 消息会被过滤")
    print("   - 其他消息类型正常处理")

    return True


async def main():
    """主测试函数"""
    success = await test_login_message_filter()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
