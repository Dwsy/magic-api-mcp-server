#!/usr/bin/env python3
"""
测试WebSocket消息处理性能
"""

import asyncio
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_websocket_message_performance():
    """测试WebSocket消息处理性能"""

    print("⚡ 测试WebSocket消息处理性能")
    print("=" * 50)

    # 创建客户端实例
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712",
        username="admin",
        password="123456"
    )

    # 模拟各种类型的WebSocket消息
    test_messages = [
        ("LOG", "简单的日志消息"),
        ("LOGS", '["日志1", "日志2", "日志3"]'),
        ("LOGIN_RESPONSE", "1"),
        ("PING", ""),
        ("ONLINE_USERS", '{"count": 5}'),
        ("UNKNOWN_TYPE", "测试未知消息类型"),
        ("BREAKPOINT", 'debug_script,{"variables":[{"name":"test","type":"String","value":"hello"}],"range":[3,1,3,13]}'),
        ("EXCEPTION", '{"type":"RuntimeException","message":"测试异常"}'),
    ]

    print("📨 测试消息处理性能:")

    total_time = 0
    message_count = 0

    for message_type, content in test_messages:
        # 构造完整消息
        full_message = f"{message_type},{content}"

        print(f"\n🔍 测试消息: {message_type}")

        # 模拟消息处理
        start_time = time.time()
        try:
            # 调用handle_message方法
            await client.handle_message(full_message)
            end_time = time.time()
            processing_time = end_time - start_time

            print(f"⏱️ 处理时间: {processing_time:.4f}秒")
            total_time += processing_time
            message_count += 1

            # 检查是否超过阈值
            if processing_time > 0.05:  # 50ms阈值
                print("⚠️ 处理时间较长")
            elif processing_time > 0.01:  # 10ms阈值
                print("🟡 处理时间一般")
            else:
                print("✅ 处理时间优秀")
        except Exception as e:
            print(f"❌ 处理失败: {e}")

    print("\n" + "=" * 50)
    if message_count > 0:
        avg_time = total_time / message_count
        print("📊 性能总结:")
        print(f"📊 平均处理时间: {avg_time:.4f}秒")
        print(f"📈 消息总数: {message_count}")
        print(f"⏱️ 总处理时间: {total_time:.4f}秒")

        if avg_time < 0.01:  # 10ms以内算优秀
            print("✅ WebSocket消息处理性能优秀！")
            return True
        elif avg_time < 0.05:  # 50ms以内算良好
            print("🟡 WebSocket消息处理性能良好")
            return True
        else:
            print("❌ WebSocket消息处理性能需要优化")
            return False
    else:
        print("❌ 没有处理任何消息")
        return False


async def main():
    """主测试函数"""
    success = await test_websocket_message_performance()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
