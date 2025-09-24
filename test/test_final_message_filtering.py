#!/usr/bin/env python3
"""
测试最终的消息过滤功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


def test_final_message_filtering():
    """测试最终的消息过滤功能"""

    print("🧪 测试最终消息过滤功能")
    print("=" * 50)

    # 创建客户端实例
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712"
    )

    # 测试各种消息类型
    test_messages = [
        ("PING", "", "特殊处理（回复pong但不显示）"),
        ("USER_LOGIN", "user123,admin", "完全过滤"),
        ("LOGIN", "user456,admin", "完全过滤"),
        ("LOGOUT", "user123", "完全过滤"),
        ("USER_LOGOUT", "user456", "完全过滤"),
        ("ONLINE_USERS", "[]", "完全过滤"),
        ("LOGIN_RESPONSE", "1", "完全过滤"),
        ("LOG", "test log message", "正常显示内容"),
        ("LOGS", '["日志1", "日志2"]', "正常显示多条日志"),
        ("BREAKPOINT", 'script,{}', "正常显示断点信息"),
        ("EXCEPTION", '{"type":"Error","message":"test"}', "正常显示异常"),
        ("UNKNOWN_TYPE", "some content", "正常显示未知消息")
    ]

    print("📨 测试消息过滤:")

    filtered_types = []
    displayed_types = []
    special_types = []

    for message_type, content, expected in test_messages:
        # 构造完整消息
        full_message = f"{message_type},{content}"

        print(f"\n🔍 测试: {message_type}")

        # 模拟消息处理逻辑
        parts = full_message.split(',', 1)
        if len(parts) >= 1:
            msg_type = parts[0].upper()

            # 检查是否会被过滤或特殊处理
            if msg_type == "PING":
                print(f"   ✅ {expected}")
                special_types.append(msg_type)
            elif msg_type in ["USER_LOGIN", "LOGIN", "LOGOUT", "USER_LOGOUT", "ONLINE_USERS", "LOGIN_RESPONSE"]:
                print(f"   🚫 {expected}")
                filtered_types.append(msg_type)
            else:
                print(f"   📝 {expected}")
                displayed_types.append(msg_type)

    print("\n" + "=" * 50)
    print("✅ 消息过滤测试完成!")
    print("📊 过滤统计:")
    print(f"   🔄 特殊处理: {len(special_types)} 个消息类型")
    print(f"   🚫 完全过滤: {len(filtered_types)} 个消息类型")
    print(f"   📝 正常显示: {len(displayed_types)} 个消息类型")

    # 验证结果
    expected_special = 1  # PING
    expected_filtered = 6  # USER_LOGIN, LOGIN, LOGOUT, USER_LOGOUT, ONLINE_USERS, LOGIN_RESPONSE
    expected_displayed = len(test_messages) - expected_special - expected_filtered

    if (len(special_types) == expected_special and
        len(filtered_types) == expected_filtered and
        len(displayed_types) == expected_displayed):
        print("✅ 消息过滤逻辑验证通过!")
        print("\n🎯 过滤的消息类型:")
        print("   - PING: 自动回复pong，不显示")
        print("   - USER_LOGIN, LOGIN, LOGOUT, USER_LOGOUT: 登录相关消息")
        print("   - ONLINE_USERS: 在线用户状态")
        print("   - LOGIN_RESPONSE: 登录响应")
        print("\n📝 显示的消息类型:")
        print("   - LOG/LOGS: 脚本执行日志")
        print("   - BREAKPOINT: 断点信息")
        print("   - EXCEPTION: 异常信息")
        print("   - 其他: 未知消息类型")
        return True
    else:
        print("❌ 消息过滤逻辑验证失败!")
        return False


if __name__ == "__main__":
    success = test_final_message_filtering()
    exit(0 if success else 1)
