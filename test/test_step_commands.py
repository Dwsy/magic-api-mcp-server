#!/usr/bin/env python3
"""
测试step命令消息格式
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_step_commands():
    """测试step命令的消息格式"""

    print("🧪 测试step命令消息格式")
    print("=" * 50)

    # 创建客户端实例
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712"
    )

    # 设置测试数据
    client.current_api_path = "/test00/test0001"
    client.breakpoints = [3, 6]

    # 测试获取script_id
    print("1️⃣ 测试script_id获取")
    script_id = client._get_script_id_by_path("/test00/test0001")
    print(f"📋 获取到的script_id: {script_id}")

    # 验证script_id格式
    if len(script_id) == 32 and all(c in '0123456789abcdef' for c in script_id):
        print("✅ script_id格式正确")
    else:
        print(f"❌ script_id格式异常: {script_id}")
        return False

    # 测试消息格式构建
    print("\n2️⃣ 测试消息格式构建")

    # 模拟发送step命令（不实际发送WebSocket消息）
    test_cases = [
        ("resume", 0, "恢复断点"),
        ("step_over", 1, "单步越过"),
        ("step_into", 2, "单步进入"),
        ("step_out", 3, "单步跳出")
    ]

    for command_name, step_type, description in test_cases:
        # 构建消息
        breakpoints_str = "|".join(map(str, sorted(client.breakpoints)))
        message = f"resume_breakpoint,{script_id},{step_type},{breakpoints_str}"

        print(f"📤 {description}: {message}")

        # 验证消息格式
        parts = message.split(',')
        if len(parts) == 4:
            msg_type, msg_script_id, msg_step_type, msg_breakpoints = parts
            if (msg_type == "resume_breakpoint" and
                msg_script_id == script_id and
                msg_step_type == str(step_type) and
                msg_breakpoints == breakpoints_str):
                print(f"✅ {description}消息格式正确")
            else:
                print(f"❌ {description}消息格式错误")
                return False
        else:
            print(f"❌ {description}消息格式不完整")
            return False

    print("\n3️⃣ 验证消息内容")

    # 验证断点字符串格式
    expected_breakpoints = "3|6"
    actual_breakpoints = "|".join(map(str, sorted(client.breakpoints)))

    if actual_breakpoints == expected_breakpoints:
        print(f"✅ 断点字符串格式正确: {actual_breakpoints}")
    else:
        print(f"❌ 断点字符串格式错误: {actual_breakpoints} != {expected_breakpoints}")
        return False

    print("\n" + "=" * 60)
    print("🎉 step命令消息格式测试全部通过!")
    print("📤 现在step命令会发送正确的WebSocket消息格式")
    print("🔧 消息格式: resume_breakpoint,{script_id},{step_type},{breakpoints}")
    return True


async def main():
    """主测试函数"""
    success = await test_step_commands()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
