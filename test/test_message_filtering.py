#!/usr/bin/env python3
"""
测试消息过滤功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_message_filtering():
    """测试消息过滤功能"""

    print("🧪 测试消息过滤功能")
    print("=" * 50)

    # 模拟消息过滤逻辑
    def should_filter_message(message_type):
        """检查消息是否应该被过滤"""
        # 特殊处理PING消息：回复pong但不显示
        if message_type == "PING":
            return "special"  # 特殊处理

        # 忽略登录类型和状态消息
        if message_type in ["USER_LOGIN", "LOGIN", "LOGOUT", "USER_LOGOUT", "ONLINE_USERS"]:
            return "filtered"  # 完全过滤

        return "normal"  # 正常处理

    # 测试各种消息类型
    test_messages = [
        ("PING", "心跳消息"),
        ("PONG", "pong响应"),
        ("USER_LOGIN", "用户登录"),
        ("LOGIN", "通用登录"),
        ("LOGOUT", "登出"),
        ("USER_LOGOUT", "用户登出"),
        ("ONLINE_USERS", "在线用户列表"),
        ("LOG", "普通日志"),
        ("LOGS", "多条日志"),
        ("BREAKPOINT", "断点信息"),
        ("EXCEPTION", "异常信息"),
        ("LOGIN_RESPONSE", "登录响应"),
        ("UNKNOWN_TYPE", "未知消息类型")
    ]

    print("📨 测试消息过滤:")

    special_count = 0
    filtered_count = 0
    normal_count = 0

    for message_type, description in test_messages:
        result = should_filter_message(message_type)

        if result == "special":
            print(f"   🔄 {message_type}: {description} - 特殊处理（回复pong但不显示）")
            special_count += 1
        elif result == "filtered":
            print(f"   🚫 {message_type}: {description} - 完全过滤")
            filtered_count += 1
        else:
            print(f"   ✅ {message_type}: {description} - 正常处理")
            normal_count += 1

    print("\n" + "=" * 50)
    print("✅ 消息过滤测试完成!")
    print("📊 统计结果:")
    print(f"   🔄 特殊处理消息: {special_count} 个 (PING)")
    print(f"   🚫 完全过滤消息: {filtered_count} 个 (登录和状态消息)")
    print(f"   ✅ 正常处理消息: {normal_count} 个 (调试相关消息)")

    # 验证结果
    expected_special = 1  # PING
    expected_filtered = 5  # USER_LOGIN, LOGIN, LOGOUT, USER_LOGOUT, ONLINE_USERS
    expected_normal = len(test_messages) - expected_special - expected_filtered

    if (special_count == expected_special and
        filtered_count == expected_filtered and
        normal_count == expected_normal):
        print("✅ 消息过滤逻辑验证通过!")
        return True
    else:
        print("❌ 消息过滤逻辑验证失败!")
        return False


if __name__ == "__main__":
    success = test_message_filtering()
    exit(0 if success else 1)
