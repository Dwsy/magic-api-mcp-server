#!/usr/bin/env python3
"""
Magic-API WebSocket客户端和API调用工具
用于连接Magic-API WebSocket控制台，监听日志并调用API接口

功能特性:
1. WebSocket连接和日志监听
2. 灵活的API调用功能
3. 支持GET/POST/PUT/DELETE方法
4. 支持传递查询参数和请求体
5. 实时日志显示

使用方法:
# 连接WebSocket并运行默认测试
python3 magic_api_client.py

# 调用指定API
python3 magic_api_client.py --call "GET /test00/test0001"

# 传递查询参数
python3 magic_api_client.py --call "GET /api/search" --params "key=value&limit=10"

# POST请求传递JSON数据
python3 magic_api_client.py --call "POST /api/create" --data '{"name":"test","value":123}'

# 仅连接WebSocket监听日志
python3 magic_api_client.py --listen-only
"""

import asyncio
import websockets
import json
import requests
import time
import sys


class MagicAPIWebSocketClient:
    def __init__(self, ws_url, api_base_url, username=None, password=None):
        self.ws_url = ws_url
        self.api_base_url = api_base_url
        self.username = username
        self.password = password
        self.websocket = None
        self.client_id = f"python_client_{int(time.time())}"
        self.connected = False

    async def connect(self):
        """连接到 WebSocket"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            print(f"✅ 已连接到 WebSocket: {self.ws_url}")

            # 发送登录消息
            await self.login()

            # 启动消息监听
            await self.listen_messages()
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            self.connected = False

    async def login(self):
        """发送登录消息"""
        # 构建登录消息，基于 MagicWorkbenchHandler.onLogin 的实现
        login_message = f"login,{self.username or 'guest'},{self.client_id}"
        await self.websocket.send(login_message)


    async def listen_messages(self):
        """监听 WebSocket 消息"""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket 连接已关闭")
            self.connected = False
        except Exception as e:
            print(f"❌ 消息监听错误: {e}")
            self.connected = False

    async def handle_message(self, message):
        """处理接收到的消息"""
        try:
            parts = message.split(',', 1)
            if len(parts) < 1:
                return

            message_type = parts[0].upper()
            content = parts[1] if len(parts) > 1 else ""

            # 处理不同类型的消息，基于 MessageType 枚举
            if message_type == "LOG":
                print(f"📝 [日志] {content}")
            elif message_type == "LOGS":
                # 多条日志消息
                try:
                    logs = json.loads(content)
                    for log in logs:
                        print(f"📝 [日志] {log}")
                except json.JSONDecodeError:
                    print(f"📝 [日志] {content}")

            elif message_type == "PING":
                # 响应心跳
                await self.websocket.send("pong")
                print("💓 心跳响应已发送")
            elif message_type  in ["LOGIN_RESPONSE", "ONLINE_USERS"]:
                pass
            else:
                print(f"📨 [{message_type}] {content}")
        except Exception as e:
            print(f"❌ 消息处理错误: {e}")

    def call_api(self, api_path, method="GET", data=None, params=None, headers=None):
        """调用 API 并触发日志输出"""
        if not self.connected:
            print("⚠️ WebSocket未连接，API调用可能无法显示实时日志")

        url = f"{self.api_base_url.rstrip('/')}{api_path}"

        # 默认请求头
        default_headers = {
            "X-MAGIC-CLIENT-ID": self.client_id,
            "X-MAGIC-SCRIPT-ID": "test_script",
            "Content-Type": "application/json"
        }

        # 合并自定义headers
        if headers:
            default_headers.update(headers)

        try:
            print(f"🌐 调用API: {method} {url}")

            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=default_headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, headers=default_headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, params=params, headers=default_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, headers=default_headers, timeout=30)
            else:
                print(f"❌ 不支持的HTTP方法: {method}")
                return None

            print(f"📊 响应状态: {response.status_code}")

            try:
                response_json = response.json()
                print(f"📄 响应内容: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
                return response_json
            except json.JSONDecodeError:
                print(f"📄 响应内容: {response.text}")
                return response.text

        except requests.exceptions.Timeout:
            print("⏰ API调用超时 (30秒)")
            return None
        except requests.exceptions.ConnectionError:
            print("🔌 API连接失败")
            return None
        except Exception as e:
            print(f"❌ API调用异常: {e}")
            return None

    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 连接已关闭")




def parse_call_arg(call_arg):
    """解析--call参数，返回(method, path)"""
    parts = call_arg.strip().split(None, 1)  # 按空格分割，最大分割1次
    if len(parts) != 2:
        raise ValueError(f"无效的--call参数格式: {call_arg}，应为 'METHOD PATH'")
    return parts[0].upper(), parts[1]


def run_custom_api_call(client, method, path, params=None, data=None, enable_websocket=False):
    """运行自定义API调用"""
    print(f"\n🌐 自定义API调用: {method} {path}")

    # 解析查询参数
    query_params = {}
    if params:
        try:
            # 解析key=value&key2=value2格式的参数
            for param in params.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
                else:
                    query_params[param] = ''  # 没有值的参数
        except Exception as e:
            print(f"⚠️ 解析查询参数失败: {e}，使用原始字符串")
            query_params = params

    # 解析请求体数据
    request_data = None
    if data:
        try:
            request_data = json.loads(data)
        except json.JSONDecodeError:
            print(f"⚠️ 解析JSON数据失败，使用原始字符串: {data}")
            request_data = data

    # 如果启用WebSocket，先连接再调用API
    if enable_websocket:
        print("📡 连接WebSocket进行实时日志监听...")

        async def call_with_websocket():
            # 在后台启动WebSocket连接进行监听
            listen_task = asyncio.create_task(client.connect())

            # 等待连接建立
            await asyncio.sleep(2)

            # 执行自定义API调用
            result = client.call_api(
                api_path=path,
                method=method,
                params=query_params if isinstance(query_params, dict) else None,
                data=request_data
            )

            # 等待一段时间让日志输出完成
            await asyncio.sleep(2)

            # 取消监听任务
            listen_task.cancel()
            try:
                await listen_task
            except asyncio.CancelledError:
                pass

            await client.close()
            return result

        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(call_with_websocket())
            loop.close()

            if result:
                print("✅ API调用完成")
            else:
                print("❌ API调用失败")
            return result

        except Exception as e:
            print(f"❌ WebSocket调用异常: {e}")
            # 降级到普通API调用
            print("🔄 降级到普通API调用...")

    # 普通API调用（不使用WebSocket）
    result = client.call_api(
        api_path=path,
        method=method,
        params=query_params if isinstance(query_params, dict) else None,
        data=request_data
    )

    if result:
        print("✅ API调用完成")
    else:
        print("❌ API调用失败")

    return result


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print_usage()
        sys.exit(0)

    # 解析命令行参数
    call_method = None
    call_path = None
    call_params = None
    call_data = None
    listen_only = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--call' and i + 1 < len(sys.argv):
            try:
                call_method, call_path = parse_call_arg(sys.argv[i + 1])
            except ValueError as e:
                print(f"❌ 参数错误: {e}")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == '--params' and i + 1 < len(sys.argv):
            call_params = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--data' and i + 1 < len(sys.argv):
            call_data = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--listen-only':
            listen_only = True
            i += 1
        else:
            print(f"❌ 未知参数: {sys.argv[i]}")
            print_usage()
            sys.exit(1)

    # 配置连接信息
    WS_URL = "ws://127.0.0.1:10712/magic/web/console"
    API_BASE_URL = "http://127.0.0.1:10712"
    USERNAME = "admin"
    PASSWORD = "123456"


    print(f"📡 WebSocket URL: {WS_URL}🌐 API Base URL: {API_BASE_URL}")


    if call_method and call_path:
        print(f"🎯 目标API: {call_method} {call_path}")
        if call_params:
            print(f"📋 查询参数: {call_params}")
        if call_data:
            print(f"📦 请求数据: {call_data}")
    elif listen_only:
        print("👂 监听模式: 仅监听日志，不执行API调用")
    else:
        print("❌ 错误：必须指定--call参数或--listen-only参数")
        sys.exit(1)

    print("-" * 50)

    # 创建客户端
    client = MagicAPIWebSocketClient(WS_URL, API_BASE_URL, USERNAME, PASSWORD)

    if listen_only:
        # 仅监听模式
        print("👂 启动仅监听模式...")

        async def listen_only_mode():
            try:
                await client.connect()
            except KeyboardInterrupt:
                print("\n⏹️ 监听已停止")
            except Exception as e:
                print(f"❌ 连接异常: {e}")
            finally:
                await client.close()

        return listen_only_mode()

    elif call_method and call_path:
        # 自定义API调用模式（必须连接WebSocket进行日志监听）
        print("🎯 启动自定义API调用模式...")

        async def custom_call_with_websocket():
            try:
                # 启动WebSocket监听（后台）
                listen_task = asyncio.create_task(client.connect())

                # 等待连接建立
                await asyncio.sleep(2)

                # 执行自定义API调用
                result = run_custom_api_call(client, call_method, call_path, call_params, call_data, enable_websocket=False)

                # 等待一段时间让日志输出完成
                await asyncio.sleep(3)

                if result:
                    pass
                else:
                    print("❌ 操作失败")

            except KeyboardInterrupt:
                print("\n⏹️ 操作被用户中断")
            except Exception as e:
                print(f"❌ 执行异常: {e}")
            finally:
                # 取消监听任务
                listen_task.cancel()
                try:
                    await listen_task
                except asyncio.CancelledError:
                    pass
                await client.close()

        return custom_call_with_websocket()


def print_usage():
    """打印使用说明"""
    print("Magic-API WebSocket客户端和API调用工具")
    print("=" * 50)
    print("功能: 连接Magic-API WebSocket控制台，监听日志并灵活调用API")
    print("依赖: pip install websockets requests")
    print("")
    print("基本使用:")
    print("  python3 magic_api_client.py --call 'GET /api/test'    # 调用API")
    print("  python3 magic_api_client.py --listen-only            # 仅监听模式")
    print("")
    print("API调用:")
    print("  python3 magic_api_client.py --call 'GET /api/test'")
    print("  python3 magic_api_client.py --call 'POST /api/create' --data '{\"name\":\"test\"}'")
    print("  python3 magic_api_client.py --call 'GET /api/search' --params 'key=value'")
    print("")
    print("命令行选项:")
    print("  --call METHOD PATH          指定要调用的API (如: 'GET /api/test')")
    print("  --data JSON_STRING          POST/PUT请求的JSON数据")
    print("  --params QUERY_STRING       GET请求的查询参数 (如: 'key=value&limit=10')")
    print("  --listen-only               仅连接WebSocket监听日志，不执行API调用")
    print("  --help, -h                  显示此帮助信息")
    print("")
    print("配置:")
    print("  WebSocket URL: ws://127.0.0.1:10712/magic/web/console")
    print("  API Base URL: http://127.0.0.1:10712")
    print("")
    print("功能特性:")
    print("  ✅ WebSocket连接和认证")
    print("  ✅ 实时日志监听")
    print("  ✅ 灵活的API调用")
    print("  ✅ 支持GET/POST/PUT/DELETE")
    print("  ✅ 参数传递支持")
    print("  ✅ 自动心跳响应")


if __name__ == "__main__":
    try:
        # 获取要运行的协程
        coro = main()
        if coro:  # 如果有协程要运行
            asyncio.run(coro)
        else:  # 如果main()已经处理了help或错误，直接退出
            pass
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        sys.exit(1)
