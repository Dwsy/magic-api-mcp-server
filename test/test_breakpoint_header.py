#!/usr/bin/env python3
"""
测试断点请求头发送功能
"""

import asyncio
import requests
import sys
import os

# 添加当前目录到Python路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_breakpoint_header():
    """测试断点请求头是否正确发送"""

    print("🧪 测试断点请求头发送功能")
    print("=" * 50)

    # 创建客户端
    client = MagicAPIDebugClient(
        ws_url="ws://127.0.0.1:10712/magic/web/console",
        api_base_url="http://127.0.0.1:10712",
        username="admin",
        password="123456"
    )

    # 模拟连接状态
    client.connected = True

    # 测试断点设置
    print("1. 设置断点 3 和 4...")
    await client.set_breakpoint(3)
    await client.set_breakpoint(4)
    print(f"   当前断点: {client.breakpoints}")

    # 测试API调用时的断点头信息发送
    print("\n2. 测试API调用时断点头信息...")

    # 拦截requests.get来检查请求头
    original_get = requests.get
    captured_headers = None

    def mock_get(url, **kwargs):
        nonlocal captured_headers
        captured_headers = kwargs.get('headers', {})
        print(f"   请求URL: {url}")
        print(f"   请求头: {captured_headers}")

        # 创建一个模拟响应
        class MockResponse:
            status_code = 200
            text = '{"code":200,"message":"success","data":"test response"}'

        return MockResponse()

    # 替换requests.get
    requests.get = mock_get

    try:
        # 调用带断点的API
        result = await client.call_api_with_debug(
            "/test00/test0001",
            "GET",
            breakpoints=[3, 4]
        )

        # 检查请求头是否包含断点信息
        if captured_headers and 'magic-request-breakpoints' in captured_headers:
            breakpoint_header = captured_headers['magic-request-breakpoints']
            print(f"   ✅ 断点请求头: {breakpoint_header}")

            if breakpoint_header == "3,4":
                print("   ✅ 断点格式正确!")
                return True
            else:
                print(f"   ❌ 断点格式错误，期望 '3,4'，实际 '{breakpoint_header}'")
                return False
        else:
            print("   ❌ 缺少断点请求头")
            return False

    finally:
        # 恢复原始的requests.get
        requests.get = original_get


async def main():
    """主测试函数"""
    success = await test_breakpoint_header()

    print("\n" + "=" * 50)
    if success:
        print("🎉 断点请求头测试通过！")
        print("断点信息将通过 'magic-request-breakpoints' 请求头发送，格式: 3,4,5,6")
        return True
    else:
        print("❌ 测试失败！")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
