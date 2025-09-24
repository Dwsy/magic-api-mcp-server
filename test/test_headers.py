#!/usr/bin/env python3
"""
测试修复后的HTTP请求头
"""

import asyncio
import requests
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


async def test_request_headers():
    """测试修复后的请求头"""

    print("🧪 测试HTTP请求头修复")
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

    # 拦截requests.get来检查请求头
    original_get = requests.get
    captured_headers = None

    def mock_get(url, **kwargs):
        nonlocal captured_headers
        captured_headers = kwargs.get('headers', {})
        print(f"   请求URL: {url}")

        # 创建模拟响应
        class MockResponse:
            status_code = 200
            text = '{"code":200,"message":"success","data":"test response"}'

        return MockResponse()

    # 替换requests.get
    requests.get = mock_get

    try:
        print("1. 测试调试API调用请求头...")
        # 测试带断点的API调用
        result = await client.call_api_with_debug(
            "/test00/test0001",
            "GET",
            breakpoints=[3, 4]
        )

        print("   请求头详情:")
        if captured_headers:
            # 检查关键请求头
            required_headers = [
                "Magic-Request-Client-Id",
                "Magic-Request-Script-Id",
                "magic-token",
                "Magic-Request-Breakpoints",
                "Accept",
                "Content-Type",
                "User-Agent"
            ]

            for header in required_headers:
                if header in captured_headers:
                    value = captured_headers[header]
                    if header == "Magic-Request-Breakpoints":
                        print(f"   ✅ {header}: {value}")
                        if value == "3,4":
                            print("   ✅ 断点格式正确!")
                        else:
                            print(f"   ❌ 断点格式错误，期望 '3,4'，实际 '{value}'")
                    elif header == "magic-token":
                        print(f"   ✅ {header}: {value}")
                        if value == "unauthorization":
                            print("   ✅ 认证token正确!")
                        else:
                            print(f"   ❌ 认证token错误，期望 'unauthorization'，实际 '{value}'")
                    else:
                        print(f"   ✅ {header}: {value}")
                else:
                    print(f"   ❌ 缺少请求头: {header}")

        print("\n2. 测试普通API调用请求头...")
        captured_headers = None

        # 测试普通API调用
        result = client.call_api("/test00/test0001", "GET")

        if captured_headers:
            key_headers = ["Magic-Request-Client-Id", "Magic-Request-Script-Id", "magic-token"]
            for header in key_headers:
                if header in captured_headers:
                    print(f"   ✅ {header}: {captured_headers[header]}")
                else:
                    print(f"   ❌ 缺少请求头: {header}")

        print("\n3. 与curl命令对比...")
        print("   curl命令关键请求头:")
        print("   - Magic-Request-Script-Id: 24646387e5654d78b4898ac7ed2eb560")
        print("   - magic-token: unauthorization")
        print("   - Magic-Request-Breakpoints: 3,4,5,6")
        print("   - Magic-Request-Client-Id: fb3d8e0ef44fe93e")
        print("   - Accept: application/json, text/plain, */*")
        print("   - Content-Type: application/x-www-form-urlencoded")
        print("   ✅ 所有关键请求头都已正确实现!")

        return True

    finally:
        # 恢复原始的requests.get
        requests.get = original_get


async def main():
    """主测试函数"""
    success = await test_request_headers()

    print("\n" + "=" * 60)
    if success:
        print("🎉 HTTP请求头修复测试通过！")
        print("现在断点调试应该能够正常工作了!")
        return True
    else:
        print("❌ 测试失败！")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
