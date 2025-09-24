#!/usr/bin/env python3
"""测试 MCP 工具列表功能"""

import json
import subprocess
import sys

def test_mcp_tools():
    """测试 MCP 工具列表"""

    # MCP 初始化请求
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    # 工具列表请求
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }

    # 启动 MCP 服务器进程
    cmd = [
        sys.executable, "-m", "uv", "run", "fastmcp", "run",
        "magicapi_mcp/magicapi_assistant.py:tools",
        "--transport", "stdio"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            cwd="/Users/dengwenyu/Dev/code/company/Jly/sfm_back/med-pms/src/main/resources/magic-api-tools",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 发送初始化请求
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # 读取初始化响应
        init_response = process.stdout.readline().strip()
        print("初始化响应:", init_response)

        # 发送 initialized 通知
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()

        # 发送工具列表请求
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()

        # 读取工具列表响应
        tools_response = process.stdout.readline().strip()
        print("工具列表响应:", tools_response)

        # 解析并显示工具
        try:
            response_data = json.loads(tools_response)
            if "result" in response_data and "tools" in response_data["result"]:
                tools = response_data["result"]["tools"]
                print(f"\n🎯 发现 {len(tools)} 个工具:")
                for tool in tools:
                    print(f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            else:
                print("❌ 响应中没有找到工具列表")
                print("完整响应:", response_data)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析错误: {e}")
            print("原始响应:", tools_response)

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        if 'process' in locals():
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_mcp_tools()
