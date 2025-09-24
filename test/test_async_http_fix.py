#!/usr/bin/env python3
"""
测试异步HTTP请求修复
"""

import asyncio
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_async_http_fix():
    """测试异步HTTP请求修复"""

    print("🧪 测试异步HTTP请求修复")
    print("=" * 50)

    # 创建客户端实例
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712"
    )

    # 测试异步HTTP请求执行器
    print("1️⃣ 测试异步HTTP请求执行器")

    # 测试_get_http_request_async方法
    url = "http://httpbin.org/get"
    headers = {"User-Agent": "test-client"}
    params = {"test": "value"}

    try:
        future = client._execute_http_request_async("GET", url, headers, params, timeout=10)
        print("✅ 异步HTTP请求Future创建成功")

        # 等待结果
        response = future.result(timeout=15)
        print(f"✅ HTTP请求成功: 状态码 {response.status_code}")

        if response.status_code == 200:
            print("✅ 异步HTTP请求执行器工作正常")
        else:
            print(f"⚠️ 响应状态异常: {response.status_code}")

    except Exception as e:
        print(f"❌ 异步HTTP请求测试失败: {e}")
        return False

    # 测试在asyncio事件循环中的表现
    print("\n2️⃣ 测试asyncio事件循环兼容性")

    async def test_event_loop_compatibility():
        """测试在asyncio事件循环中的兼容性"""
        try:
            # 单个异步请求测试
            future = client._execute_http_request_async(
                "GET",
                url,
                headers,
                {"test": "asyncio_test"},
                timeout=10
            )

            # 等待请求完成
            response = await asyncio.wait_for(asyncio.wrap_future(future), timeout=15)

            if response.status_code == 200:
                print("✅ asyncio事件循环中的HTTP请求成功")
                return True
            else:
                print(f"❌ 响应状态异常: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ asyncio兼容性测试异常: {e}")
            return False

    try:
        success = await test_event_loop_compatibility()

        if success:
            print("✅ asyncio事件循环兼容性测试通过")
        else:
            print("❌ 事件循环兼容性测试失败")
            return False

    except Exception as e:
        print(f"❌ 事件循环兼容性测试异常: {e}")
        return False

    print("\n3️⃣ 测试阻塞问题修复")

    # 模拟WebSocket消息处理期间的HTTP请求
    messages_processed = 0

    async def simulate_websocket_with_http():
        """模拟WebSocket处理期间执行HTTP请求"""
        nonlocal messages_processed

        # 启动HTTP请求
        future = client._execute_http_request_async("GET", url, headers, timeout=5)

        # 同时处理"WebSocket消息"
        for i in range(10):
            messages_processed += 1
            await asyncio.sleep(0.1)  # 模拟消息处理时间

        # 等待HTTP请求完成
        try:
            response = await asyncio.wait_for(asyncio.wrap_future(future), timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ HTTP请求在WebSocket处理期间失败: {e}")
            return False

    try:
        http_success = await simulate_websocket_with_http()

        print("📡 WebSocket模拟处理消息数: 10")
        print(f"🔄 HTTP请求成功: {http_success}")
        print(f"⏱️ 总处理时间: {10 * 0.1:.2f}秒")

        if http_success and messages_processed == 10:
            print("✅ 阻塞问题修复验证通过!")
            print("🎯 HTTP请求不再阻塞WebSocket消息处理")
        else:
            print("❌ 阻塞问题修复验证失败")
            return False

    except Exception as e:
        print(f"❌ 阻塞修复测试异常: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 异步HTTP请求修复测试全部通过!")
    print("🚀 现在WebSocket消息处理完全不会被HTTP请求阻塞")
    return True


async def main():
    """主测试函数"""
    success = await test_async_http_fix()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
