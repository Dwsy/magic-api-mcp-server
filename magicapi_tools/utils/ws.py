"""Magic-API WebSocket 客户端与调试工具。"""

from __future__ import annotations

import asyncio
import json
import threading
import time
import sys
import concurrent.futures
from typing import Any, Dict, List, Optional

try:
    import readline
except ImportError:
    # Windows 系统使用 pyreadline3
    try:
        import pyreadline3 as readline
    except ImportError:
        # 如果都没有 readline 功能，创建一个兼容层
        class MockReadline:
            def get_line_buffer(self): return ""
            def redisplay(self): pass
            def set_completer(self, completer): pass
            def set_completer_delims(self, delims): pass
            def parse_and_bind(self, binding): pass
            def read_history_file(self, filename): pass
            def write_history_file(self, filename): pass
        readline = MockReadline()

try:
    import rlcompleter
except ImportError:
    rlcompleter = None
import requests
import websockets


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



class DebugCompleter:
    """自定义命令补全器，特别支持test命令的路径补全"""

    def __init__(self):
        self.commands = [
            'test', 'call', 'breakpoint', 'bp', 'remove_bp', 'rm_bp',
            'resume', 'step', 'list_bp', 'help', 'quit'
        ]
        self.http_methods = ['GET', 'POST', 'PUT', 'DELETE']
        self.common_paths = [
            '/test00/test0001',
            '/magic/web/resource',
            '/api/test',
            '/api/search',
            '/api/create',
            '/api/update',
            '/api/delete'
        ]

    def complete(self, text, state):
        """补全函数"""
        if state == 0:
            # 第一次调用，生成补全列表
            line = readline.get_line_buffer()
            self.matches = self._get_matches(line, text)

        if not self.matches:
            return None

        try:
            result = self.matches[state]
            return result
        except IndexError:
            return None

    def _get_matches(self, line, text):
        """获取匹配的补全项"""
        matches = []

        # 如果是空行或只输入了部分命令
        if not line.strip() or ' ' not in line:
            # 补全命令
            for cmd in self.commands:
                if cmd.startswith(text):
                    matches.append(cmd)
        else:
            # 解析命令和参数
            parts = line.split()
            command = parts[0].lower()

            if command == 'test':
                # test命令的特殊处理
                if len(parts) == 1:
                    # 没有参数，补全为test
                    if text and 'test'.startswith(text):
                        matches.append('test ')
                elif len(parts) == 2:
                    # 补全断点参数或路径
                    if text.startswith('/') or not text:
                        # 补全路径
                        for path in self.common_paths:
                            if path.startswith(text):
                                matches.append(path)
                    # 不补全断点数字

            elif command in ['call', 'breakpoint', 'bp', 'remove_bp', 'rm_bp']:
                current_part_index = len(parts) - 1

                if command == 'call':
                    if current_part_index == 1:
                        # 补全HTTP方法
                        for method in self.http_methods:
                            if method.startswith(text.upper()):
                                matches.append(method)
                    elif current_part_index == 2:
                        # 补全路径
                        for path in self.common_paths:
                            if path.startswith(text):
                                matches.append(path)
                # 不补全其他命令的参数

        return matches


def setup_readline():
    """设置readline以支持方向键和自动补全"""
    # 清除任何现有的补全器设置
    readline.set_completer(None)
    readline.set_completer_delims('\t\n ')

    # 设置补全器
    completer = DebugCompleter()
    readline.set_completer(completer.complete)
    readline.set_completer_delims('\t\n')  # 只用tab和换行符作为分隔符

    # 启用Tab补全，覆盖任何现有绑定
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set show-all-if-ambiguous off')

    # 启用历史记录
    readline.parse_and_bind('set enable-keypad on')

    # 设置历史文件（可选）
    histfile = '.magic_debug_history'
    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        pass

    # 保存历史记录
    import atexit
    atexit.register(lambda: readline.write_history_file(histfile))


class MagicAPIDebugClient:
    def __init__(self, ws_url, api_base_url, username=None, password=None):
        self.ws_url = ws_url
        self.api_base_url = api_base_url
        self.username = username
        self.password = password
        self.websocket = None
        # 生成随机client_id，格式与服务器期望的一致
        self.client_id = self._generate_client_id()
        self.breakpoints = []  # 存储断点行号
        self.debug_context = None
        self.is_connected = asyncio.Event()  # 用于同步连接状态
        self.connected = False

        # 断点调试状态管理
        self.debug_mode = False  # 是否处于调试模式
        self.breakpoint_hit = asyncio.Event()  # 断点触发事件
        self.breakpoint_data = None  # 当前断点信息
        self.waiting_for_resume = False  # 是否等待恢复命令

    def _generate_client_id(self):
        """生成随机client_id，格式与服务器期望的一致（16字符十六进制）"""
        import random
        import string

        # 生成16字符的随机十六进制字符串（小写字母+数字）
        chars = string.hexdigits.lower()  # '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(16))

    async def connect(self):
        """连接到 WebSocket"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            print(f"✅ 已连接到 WebSocket: {self.ws_url}")
            self.is_connected.set()  # 设置连接成功事件

            await self.login()
            await self.listen_messages()
        except websockets.exceptions.ConnectionClosedOK:
            print("🔌 WebSocket 连接已正常关闭")
            self.connected = False
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ WebSocket 连接异常关闭: {e}")
            self.connected = False
        except Exception as e:
            print(f"❌ WebSocket 连接失败: {e}")
            self.connected = False
            raise  # 重新抛出异常以便外部捕获

    async def login(self):
        """发送登录消息"""
        login_message = f"login,{self.username or 'guest'},{self.client_id}"
        await self.websocket.send(login_message)
        print(f"📤 已发送登录消息: {login_message}")

    async def set_breakpoint(self, line_number: int):
        """设置断点 - 断点通过HTTP请求头设置，不需要WebSocket消息"""
        if line_number not in self.breakpoints:
            self.breakpoints.append(line_number)
        print(f"🔴 设置断点在第 {line_number} 行")

    async def remove_breakpoint(self, line_number: int):
        """移除断点 - 断点通过HTTP请求头设置，不需要WebSocket消息"""
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        print(f"🔵 移除断点在第 {line_number} 行")

    async def resume_breakpoint(self):
        """恢复断点执行"""
        await self._send_step_command(0)  # 0表示resume
        print("▶️ 恢复执行")

    async def step_over(self):
        """单步执行（越过）"""
        await self._send_step_command(1)  # 1表示step over
        print("⏭️ 单步执行（越过）")

    async def step_into(self):
        """单步执行（进入）"""
        await self._send_step_command(2)  # 2表示step into
        print("⏬ 单步执行（进入）")

    async def step_out(self):
        """单步执行（跳出）"""
        await self._send_step_command(3)  # 3表示step out
        print("⏫ 单步执行（跳出）")

    async def _send_step_command(self, step_type: int):
        """
        发送步进命令

        Args:
            step_type: 步进类型 (0=resume, 1=step_over, 2=step_into, 3=step_out)
        """
        try:
            # 获取当前断点信息中的script_id
            script_id = "24646387e5654d78b4898ac7ed2eb560"  # 默认值

            if hasattr(self, 'current_api_path') and self.current_api_path:
                script_id = self._get_script_id_by_path(self.current_api_path)

            # 获取当前断点信息
            breakpoints_str = ""
            if self.breakpoints:
                breakpoints_str = "|".join(map(str, sorted(self.breakpoints)))

            # 构建消息: resume_breakpoint,script_id,step_type,breakpoints
            message = f"resume_breakpoint,{script_id},{step_type},{breakpoints_str}"
            await self.websocket.send(message)

            # 清除断点暂停状态
            self.waiting_for_resume = False
            self.breakpoint_data = None
            self.breakpoint_hit.clear()

        except Exception as e:
            print(f"❌ 发送步进命令失败: {e}")

    async def listen_messages(self):
        """监听 WebSocket 消息"""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket 连接已关闭")
            self.connected = False

    async def handle_message(self, message):
        """处理接收到的消息 - 实时高效处理"""
        # 性能监控开始
        start_time = time.time()

        parts = message.split(',', 1)
        if len(parts) < 1:
            return

        message_type = parts[0].upper()
        content = parts[1] if len(parts) > 1 else ""

        # 特殊处理PING消息：回复pong但不显示
        if message_type == "PING":
            await self.websocket.send("pong")
            return

        # 忽略登录类型和状态消息
        # if message_type in ["USER_LOGIN", "LOGIN", "LOGOUT", "USER_LOGOUT", "ONLINE_USERS","INTO_FILE_ID"]:
        #     return

        # 根据消息类型进行相应处理和显示
        if message_type == "LOG":
            # 单个日志消息 - 只显示内容
            print(f"📝 {content}")
        elif message_type == "LOGS":
            # 多条日志消息 - 优化输出性能
            try:
                logs = json.loads(content)
                if len(logs) > 100:
                    # 大量日志时只显示前100条和总数
                    for log in logs[:100]:
                        print(f"📝 {log}")
                    print(f"📝 ...还有{len(logs)-100}条日志")
                else:
                    for log in logs:
                        print(f"📝 {log}")
            except json.JSONDecodeError:
                print(f"📝 {content}")
        elif message_type == "BREAKPOINT":
            # 进入断点 - 消息格式: BREAKPOINT,script_id,{json_data}
            try:
                # 解析消息格式: script_id,{json_data}
                if ',' in content:
                    script_id, json_str = content.split(',', 1)
                else:
                    script_id = '未知'
                    json_str = content

                # 解析JSON数据
                breakpoint_data = json.loads(json_str)

                # 提取断点信息
                variables = breakpoint_data.get('variables', [])
                range_info = breakpoint_data.get('range', [])

                # 从range信息提取行号 [start_line, start_col, end_line, end_col]
                if len(range_info) >= 3:
                    line_number = range_info[0]  # 开始行号
                else:
                    line_number = '未知'

                # 高效的断点信息显示
                print(f"🔴 [断点] 脚本 '{script_id}' 在第 {line_number} 行暂停")

                # 快速显示变量摘要
                if variables:
                    var_count = len(variables)
                    print(f"📊 变量: {var_count} 个")
                    # 只显示前10个重要变量，避免输出过多影响实时性
                    for var_info in variables[:10]:
                        var_name = var_info.get('name', '未知')
                        var_type = var_info.get('type', '未知').split('.')[-1]  # 简化类型名
                        var_value = str(var_info.get('value', '未知'))
                        # 截断过长的值
                        if len(var_value) > 50:
                            var_value = var_value[:1000] + "..."
                        print(f"   {var_name} ({var_type}) = {var_value}")
                    if var_count > 10:
                        print(f"   ...还有{var_count-10}个变量")

                # 简化断点范围信息
                if range_info and len(range_info) >= 6:
                    start_line, start_col, end_line, end_col = range_info[:6]
                    print(f"📍 位置: 第{start_line}行第{start_col}列")

                # 设置断点状态，等待用户恢复命令
                self.breakpoint_data = {
                    'script_id': script_id,
                    'line_number': line_number,
                    'variables': variables,
                    'range': range_info,
                    'raw_data': breakpoint_data
                }
                self.waiting_for_resume = True
                self.breakpoint_hit.set()

                print("💡 resume/step/quit")

            except (json.JSONDecodeError, ValueError) as e:
                print(f"🔴 [断点] 解析断点消息失败: {e}")
                print(f"   原始消息: {content}")
                self.breakpoint_hit.set()
        elif message_type == "EXCEPTION":
            # 请求接口发生异常 - 优化显示性能
            try:
                exception_data = json.loads(content)
                exception_type = exception_data.get('type', '未知')
                message = exception_data.get('message', '无详细信息')
                # 简化异常显示，避免输出过多堆栈信息影响实时性
                print(f"❌ 异常: {exception_type} - {message}")
                if 'stackTrace' in exception_data:
                    stack = exception_data['stackTrace']
                    if len(stack) > 100:
                        print(f"   堆栈: {stack[:97]}...")
                    else:
                        print(f"   堆栈: {stack}")
            except json.JSONDecodeError:
                print(f"❌ 异常: {content}")
        else:
            print(f"[{message_type}] {content}")

        # 性能监控结束 - 只在慢消息时警告
        end_time = time.time()
        processing_time = end_time - start_time
        if processing_time > 0.1:  # 处理时间超过100ms时警告
            print(f"⚠️ 消息处理较慢: {message_type} 耗时 {processing_time:.3f}秒")

        # 强制刷新输出缓冲区和readline状态，确保debug>提示符重新显示
        try:
            # 刷新stdout缓冲区
            sys.stdout.flush()

            # 强制重绘readline输入行
            import readline
            readline.redisplay()
        except:
            # readline不可用时至少刷新stdout
            try:
                sys.stdout.flush()
            except:
                pass

    async def call_api_with_debug(self, api_path, method="GET", data=None, params=None,
                                  breakpoints: List[int] = None, script_id: str = "debug_script"):
        """调用 API 并支持断点调试"""
        # 保存当前API路径，用于后续step命令获取script_id
        self.current_api_path = api_path

        # 构建请求URL和请求头（在所有分支中都需要）
        url = f"{self.api_base_url.rstrip('/')}{api_path}"

        headers = {
            "Magic-Request-Client-Id": self.client_id,
            "Magic-Request-Script-Id": script_id,
            "magic-token": "unauthorization",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Referer": f"{self.api_base_url}/magic/web/index.html"
        }

        if not self.connected:
            print("⚠️ WebSocket未连接，使用普通API调用")
            # 在后台线程中执行HTTP请求，避免阻塞
            future = self._execute_http_request_async(method, url, headers, params, data, timeout=30)

            # 创建异步处理结果的任务
            async def handle_response():
                try:
                    response = await asyncio.wrap_future(future)
                    print(f"📊 响应状态: {response.status_code}")
                    print(f"📄 响应内容: {response.text}")
                    return response
                except Exception as e:
                    print(f"❌ API调用异常: {e}")
                    return None

            # 启动异步任务并等待结果（但不阻塞WebSocket）
            asyncio.create_task(handle_response())
            return None

        # 如果设置了断点，进入调试模式
        if breakpoints:
            self.debug_mode = True
            print(f"🐛 进入调试模式，断点: {breakpoints}")
            # 设置断点信息，通过HTTP请求头发送
            headers["Magic-Request-Breakpoints"] = ",".join(map(str, breakpoints))
            print(f"🔴 发送断点信息: {headers['Magic-Request-Breakpoints']}")

        print(f"🐛 调用API (调试模式): {method} {url}")
        if params:
            print(f"  查询参数: {params}")
        if data:
            print(f"  请求体: {data}")

        # 在后台线程中执行HTTP请求，避免阻塞asyncio事件循环
        def execute_debug_request_in_thread():
            """在后台线程中执行HTTP请求"""
            try:
                print("🔄 发送调试请求...")
                if method.upper() == "GET":
                    response = requests.get(url, params=params, headers=headers, timeout=300)
                elif method.upper() == "POST":
                    response = requests.post(url, json=data, params=params, headers=headers, timeout=300)
                elif method.upper() == "PUT":
                    response = requests.put(url, json=data, params=params, headers=headers, timeout=300)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, params=params, headers=headers, timeout=300)
                else:
                    print(f"❌ 不支持的HTTP方法: {method}")
                    return

                print(f"📊 响应状态: {response.status_code}")
                if response.status_code == 200:
                    content = response.text
                    print(f"📄 响应内容: {content[:200]}..." if len(content) > 200 else f"📄 响应内容: {content}")
                else:
                    print(f"📄 错误响应: {response.text}")

            except requests.exceptions.Timeout:
                print("⏰ 调试请求超时 (30秒)")
            except requests.exceptions.ConnectionError:
                print("🔌 调试请求连接失败")
            except Exception as e:
                print(f"❌ 调试请求异常: {e}")
            finally:
                # 请求完成后清理调试状态
                self.debug_mode = False

        # 在后台线程中执行HTTP请求，不阻塞asyncio事件循环
        import threading
        thread = threading.Thread(target=execute_debug_request_in_thread, daemon=True)
        thread.start()

        print("✅ 调试会话已启动，断点将通过WebSocket通知")
        return None  # 立即返回，不阻塞用户界面

    def _get_script_id_by_path(self, api_path: str) -> str:
        """
        根据API路径获取对应的script_id

        Args:
            api_path: API路径

        Returns:
            script_id，如果找不到则返回默认值
        """
        try:
            # 导入extract_api_paths模块的功能
            import sys
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            extract_script = os.path.join(script_dir, 'extract_api_paths.py')

            # 使用subprocess调用extract_api_paths.py来获取ID
            import subprocess
            result = subprocess.run([
                sys.executable, extract_script,
                '--url', 'http://127.0.0.1:10712/magic/web/resource',
                '--path-to-id', api_path
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                # 解析输出，第一行为ID
                lines = result.stdout.strip().split('\n')
                if lines:
                    # 格式: id,path,method,name,groupId
                    first_line = lines[0].strip()
                    if ',' in first_line:
                        script_id = first_line.split(',')[0].strip()
                        if script_id:
                            return script_id

        except Exception as e:
            print(f"⚠️ 获取script_id失败: {e}")

        # 返回默认的script_id（如果获取失败）
        return "24646387e5654d78b4898ac7ed2eb560"

    def _execute_http_request_async(self, method, url, headers, params=None, data=None, timeout=30):
        """异步执行HTTP请求（在后台线程中），返回Future对象"""
        import concurrent.futures
        import threading

        def http_request():
            """在后台线程中执行HTTP请求"""
            try:
                if method.upper() == "GET":
                    return requests.get(url, params=params, headers=headers, timeout=timeout)
                elif method.upper() == "POST":
                    return requests.post(url, json=data, params=params, headers=headers, timeout=timeout)
                elif method.upper() == "PUT":
                    return requests.put(url, json=data, params=params, headers=headers, timeout=timeout)
                elif method.upper() == "DELETE":
                    return requests.delete(url, params=params, headers=headers, timeout=timeout)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
            except Exception as e:
                # 重新抛出异常，让调用方处理
                raise e

        # 使用线程池执行器来执行HTTP请求
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="http-request")
        future = executor.submit(http_request)

        # 确保executor在future完成后被清理
        def cleanup_executor(fut):
            executor.shutdown(wait=False)

        future.add_done_callback(cleanup_executor)

        return future

    def call_api(self, api_path, method="GET", data=None, params=None, headers=None):
        """调用 API（普通模式）"""
        url = f"{self.api_base_url.rstrip('/')}{api_path}"

        # 默认请求头，与调试API调用保持一致
        default_headers = {
            "Magic-Request-Client-Id": self.client_id,
            "Magic-Request-Script-Id": "python_client_call",
            "magic-token": "unauthorization",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Referer": f"{self.api_base_url}/magic/web/index.html"
        }

        # 合并请求头
        if headers:
            default_headers.update(headers)

        print(f"🌐 调用API: {method} {url}")
        if params:
            print(f"  查询参数: {params}")
        if data:
            print(f"  请求体: {data}")

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=default_headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, headers=default_headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, params=params, headers=default_headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, headers=default_headers, timeout=10)
            else:
                print(f"❌ 不支持的HTTP方法: {method}")
                return None

            print(f"📊 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            return response

        except requests.exceptions.Timeout:
            print("⏰ API调用超时 (10秒)")
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
            self.connected = False


def print_usage():
    """打印使用说明"""
    print("Magic-API WebSocket调试客户端")
    print("=" * 50)
    print("功能: 连接Magic-API WebSocket控制台，支持断点调试和实时日志监听")
    print("特性: 方向键导航历史命令，Tab自动补全，test命令路径自动添加'/'前缀")
    print("依赖: pip install websockets requests")
    print("")
    print("使用方法:")
    print("  python3 magic_api_debug_client.py    # 启动交互式调试会话")
    print("")
    print("交互命令:")
    print("  test [path] [breakpoints] - 执行测试API（可选路径和断点，如: test /api/test 5,10）")
    print("  call <METHOD> <PATH> [data] - 调用指定API")
    print("  breakpoint <line> - 设置断点")
    print("  remove_bp <line> - 移除断点")
    print("  resume - 恢复断点执行")
    print("  step - 单步执行")
    print("  list_bp - 列出所有断点")
    print("  help - 显示帮助")
    print("  quit - 退出程序")
    print("")
    print("快捷键:")
    print("  ↑↓ - 浏览命令历史")
    print("  ←→ - 编辑当前命令")
    print("  Tab - 自动补全命令和路径")
    print("")
    print("自动补全:")
    print("  命令: test, call, breakpoint等")
    print("  HTTP方法: GET, POST, PUT, DELETE")
    print("  路径: /test00/test0001, /magic/web/resource等")
    print("  test命令路径自动添加'/'前缀")
    print("")
    print("配置:")
    print("  WebSocket URL: ws://127.0.0.1:10712/magic/web/console")
    print("  API Base URL: http://127.0.0.1:10712")


def preprocess_command(command_line):
    """预处理命令行，自动为test命令的路径添加前缀'/'"""
    if not command_line.strip():
        return command_line

    parts = command_line.split()
    if len(parts) >= 2 and parts[0].lower() == 'test':
        # 检查第二个参数是否是路径（不以数字开头，且不包含逗号）
        path_arg = parts[1]
        if not path_arg.isdigit() and ',' not in path_arg and not path_arg.startswith('/'):
            # 这看起来是路径，自动添加'/'
            parts[1] = '/' + path_arg
            return ' '.join(parts)

    return command_line


async def interactive_debug_session():
    """交互式调试会话"""
    # 配置连接信息
    WS_URL = "ws://127.0.0.1:10712/magic/web/console"
    API_BASE_URL = "http://127.0.0.1:10712"
    USERNAME = "unauthorization"
    PASSWORD = "123456"

    print("🚀 Magic-API 调试客户端启动")
    print(f"📡 WebSocket URL: {WS_URL}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"👤 用户名: {USERNAME}")
    print("-" * 50)

    # 设置readline支持方向键和自动补全
    setup_readline()

    # 创建调试客户端
    client = MagicAPIDebugClient(WS_URL, API_BASE_URL, USERNAME, PASSWORD)

    # 获取当前事件循环，用于在线程间安全调度协程
    loop = asyncio.get_running_loop()

    # 在后台线程中处理用户输入
    def user_input_handler():
        # 快速显示界面，WebSocket连接异步建立
        print("\n=== Magic-API 断点调试客户端 ===")
        print("💡 支持方向键导航和Tab自动补全，test命令路径会自动添加'/'前缀")
        print("输入 'help' 查看可用命令")

        # 短暂等待连接状态确认，但不阻塞UI
        time.sleep(0.1)  # 减少等待时间

        while True:
            try:
                # 确保输出缓冲区已刷新，readline状态正确
                sys.stdout.flush()
                import readline
                readline.redisplay()

                command_line = input("\ndebug> ").strip()
                # 预处理命令
                command_line = preprocess_command(command_line)
                if not command_line:
                    continue

                parts = command_line.split()
                command = parts[0].lower()

                if command == "help":
                    print_usage()

                elif command == "test":
                    # 执行测试API，支持自定义路径和断点
                    path = "/test00/test0001"  # 默认路径
                    breakpoints = []

                    if len(parts) > 1:
                        # 检查第一个参数是否是路径（不是纯数字且看起来像路径）
                        first_arg = parts[1]

                        # 如果是纯数字或数字逗号组合，认为是断点
                        if first_arg.isdigit() or (',' in first_arg and all(x.strip().isdigit() for x in first_arg.split(','))):
                            try:
                                breakpoints = [int(x.strip()) for x in first_arg.split(',')]
                            except ValueError:
                                print("❌ 断点格式错误，请使用逗号分隔的数字，如: 5,10")
                                continue
                        else:
                            # 这是一个路径
                            path = first_arg
                            # 检查是否有断点参数
                            if len(parts) > 2:
                                try:
                                    breakpoints = [int(x.strip()) for x in parts[2].split(',')]
                                except ValueError:
                                    print("❌ 断点格式错误，请使用逗号分隔的数字，如: 5,10")
                                    continue

                    print(f"🧪 执行测试API: {path}")
                    if breakpoints:
                        print(f"   断点: {breakpoints}")

                    # 使用 run_coroutine_threadsafe 在主线程的事件循环中执行异步调试调用
                    future = asyncio.run_coroutine_threadsafe(
                        client.call_api_with_debug(
                            path,
                            "GET",
                            params={"debug": "true", "test_mode": "interactive"},
                            breakpoints=breakpoints
                        ), loop
                    )
                    # 等待异步调用完成
                    result = future.result(timeout=60.0)  # 最多等待60秒，包括断点等待时间
                    if result:
                        print("✅ 测试完成")
                    else:
                        print("❌ 测试失败")

                elif command == "call":
                    if len(parts) < 3:
                        print("❌ 用法: call <METHOD> <PATH> [json_data]")
                        continue

                    method = parts[1].upper()
                    path = parts[2]
                    data = None

                    if len(parts) > 3:
                        data_str = ' '.join(parts[3:])
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            print("❌ JSON数据格式错误")
                            continue

                    # call命令不支持断点调试，使用普通同步调用
                    result = client.call_api(path, method, data=data)
                    if result:
                        print("✅ API调用完成")
                    else:
                        print("❌ API调用失败")

                elif command == "breakpoint" or command == "bp":
                    if len(parts) < 2:
                        print("❌ 用法: breakpoint <line_number>")
                        continue

                    try:
                        line_number = int(parts[1])
                        # 使用 run_coroutine_threadsafe 在主线程的事件循环中执行协程
                        future = asyncio.run_coroutine_threadsafe(
                            client.set_breakpoint(line_number), loop
                        )
                        # 等待断点操作完成，确保UI正确刷新
                        future.result(timeout=5.0)
                    except ValueError:
                        print("❌ 行号必须是数字")
                    except Exception as e:
                        print(f"❌ 设置断点失败: {e}")

                elif command == "remove_bp" or command == "rm_bp":
                    if len(parts) < 2:
                        print("❌ 用法: remove_bp <line_number>")
                        continue

                    try:
                        line_number = int(parts[1])
                        # 使用 run_coroutine_threadsafe 在主线程的事件循环中执行协程
                        future = asyncio.run_coroutine_threadsafe(
                            client.remove_breakpoint(line_number), loop
                        )
                        # 等待断点操作完成，确保UI正确刷新
                        future.result(timeout=5.0)
                    except ValueError:
                        print("❌ 行号必须是数字")
                    except Exception as e:
                        print(f"❌ 移除断点失败: {e}")

                elif command == "resume":
                    # 使用 run_coroutine_threadsafe 在主线程的事件循环中执行协程
                    future = asyncio.run_coroutine_threadsafe(
                        client.resume_breakpoint(), loop
                    )
                    # 等待恢复操作完成
                    try:
                        future.result(timeout=5.0)
                    except Exception as e:
                        print(f"❌ 恢复断点失败: {e}")

                elif command == "step":
                    # 使用 run_coroutine_threadsafe 在主线程的事件循环中执行协程
                    future = asyncio.run_coroutine_threadsafe(
                        client.step_over(), loop
                    )
                    # 等待单步操作完成
                    try:
                        future.result(timeout=5.0)
                    except Exception as e:
                        print(f"❌ 单步执行失败: {e}")

                elif command == "list_bp":
                    if client.breakpoints:
                        print("🔴 当前断点:")
                        for bp in sorted(client.breakpoints):
                            print(f"   第 {bp} 行")
                    else:
                        print("📝 当前没有设置断点")

                elif command == "quit":
                    print("👋 退出调试客户端...")
                    break

                else:
                    print(f"❌ 未知命令: {command}，输入 'help' 查看可用命令")

            except KeyboardInterrupt:
                print("\n👋 程序被用户中断")
                break
            except Exception as e:
                print(f"❌ 处理命令时出错: {e}")

    # 启动用户输入处理线程
    input_thread = threading.Thread(target=user_input_handler)
    input_thread.daemon = True
    input_thread.start()

    # 连接 WebSocket 并开始监听
    try:
        await client.connect()
    except KeyboardInterrupt:
        print("\n⏹️ 程序被用户中断")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    finally:
        await client.close()



class MagicAPIDebugTools:
    """
    Magic-API 调试工具高层接口

    提供高层调试操作，封装常用的调试功能
    """

    def __init__(self, debug_client: MagicAPIDebugClient):
        """
        初始化调试工具接口

        Args:
            debug_client: MagicAPIDebugClient 实例
        """
        self.debug_client = debug_client

    def set_breakpoint_tool(
        self,
        line_number: Optional[int] = None,
        line_numbers: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        设置断点（支持单个和批量操作）。

        Args:
            line_number: 行号（单个操作）
            line_numbers: 行号列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        if line_numbers is not None:
            return self._batch_set_breakpoints(line_numbers)
        else:
            return self._set_single_breakpoint(line_number)

    def _set_single_breakpoint(self, line_number: int) -> Dict[str, Any]:
        """设置单个断点。"""
        import asyncio
        try:
            # 在新的事件循环中运行异步操作
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.debug_client.set_breakpoint(line_number))
            loop.close()
            if success:
                return {"success": True, "line_number": line_number}
            return {"error": {"code": "set_bp_failed", "message": f"设置断点 {line_number} 失败"}}
        except Exception as e:
            return {"error": {"code": "set_bp_error", "message": f"设置断点时出错: {str(e)}"}}

    def _batch_set_breakpoints(self, line_numbers: List[int]) -> Dict[str, Any]:
        """批量设置断点。"""
        results = []
        for line_number in line_numbers:
            try:
                result = self._set_single_breakpoint(line_number)
                results.append({
                    "line_number": line_number,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "line_number": line_number,
                    "result": {"error": {"code": "batch_error", "message": str(e)}}
                })

        success_count = sum(1 for r in results if r["result"].get("success"))
        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }

    def remove_breakpoint_tool(
        self,
        line_number: Optional[int] = None,
        line_numbers: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        移除断点（支持单个和批量操作）。

        Args:
            line_number: 行号（单个操作）
            line_numbers: 行号列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        if line_numbers is not None:
            return self._batch_remove_breakpoints(line_numbers)
        else:
            return self._remove_single_breakpoint(line_number)

    def _remove_single_breakpoint(self, line_number: int) -> Dict[str, Any]:
        """移除单个断点。"""
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.debug_client.remove_breakpoint(line_number))
            loop.close()
            if success:
                return {"success": True, "line_number": line_number}
            return {"error": {"code": "remove_bp_failed", "message": f"移除断点 {line_number} 失败"}}
        except Exception as e:
            return {"error": {"code": "remove_bp_error", "message": f"移除断点时出错: {str(e)}"}}

    def _batch_remove_breakpoints(self, line_numbers: List[int]) -> Dict[str, Any]:
        """批量移除断点。"""
        results = []
        for line_number in line_numbers:
            try:
                result = self._remove_single_breakpoint(line_number)
                results.append({
                    "line_number": line_number,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "line_number": line_number,
                    "result": {"error": {"code": "batch_error", "message": str(e)}}
                })

        success_count = sum(1 for r in results if r["result"].get("success"))
        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }

    def batch_set_breakpoints_tool(self, line_numbers: List[int]) -> Dict[str, Any]:
        """
        批量设置断点工具方法。

        Args:
            line_numbers: 要设置断点的行号列表

        Returns:
            批量操作结果
        """
        return self._batch_set_breakpoints(line_numbers)

    def batch_remove_breakpoints_tool(self, line_numbers: List[int]) -> Dict[str, Any]:
        """
        批量移除断点工具方法。

        Args:
            line_numbers: 要移除断点的行号列表

        Returns:
            批量操作结果
        """
        return self._batch_remove_breakpoints(line_numbers)

    def resume_breakpoint_tool(self) -> Dict[str, Any]:
        """恢复断点执行。"""
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.debug_client.resume_breakpoint())
            loop.close()
            if success:
                return {"success": True}
            return {"error": {"code": "resume_failed", "message": "恢复断点执行失败"}}
        except Exception as e:
            return {"error": {"code": "resume_error", "message": f"恢复断点时出错: {str(e)}"}}

    def step_over_tool(self) -> Dict[str, Any]:
        """单步执行（越过）。"""
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.debug_client.step_over())
            loop.close()
            if success:
                return {"success": True}
            return {"error": {"code": "step_failed", "message": "单步执行失败"}}
        except Exception as e:
            return {"error": {"code": "step_error", "message": f"单步执行时出错: {str(e)}"}}

    def list_breakpoints_tool(self) -> Dict[str, Any]:
        """列出当前所有断点。"""
        breakpoints = self.debug_client.breakpoints
        return {"success": True, "breakpoints": list(breakpoints)}

    def call_api_with_debug_tool(
        self,
        path: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        breakpoints: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """带调试功能的API调用。"""
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.debug_client.call_api_with_debug(
                    path,  # api_path 参数
                    method=method,
                    data=data,
                    params=params,
                    breakpoints=breakpoints or []
                )
            )
            loop.close()
            if result:
                return {"success": True, "result": result}
            return {"error": {"code": "debug_call_failed", "message": "带调试的API调用失败"}}
        except Exception as e:
            return {"error": {"code": "debug_call_error", "message": f"调试调用时出错: {str(e)}"}}


    def execute_debug_session_tool(self, script_id: str, breakpoints: List[int] = None) -> Dict[str, Any]:
        """执行完整的调试会话。"""
        try:
            # 设置断点
            if breakpoints:
                self.batch_set_breakpoints_tool(breakpoints)

            # 这里可以添加更多调试会话逻辑
            # 比如自动执行、收集变量状态等

            return {
                "success": True,
                "script_id": script_id,
                "breakpoints_set": breakpoints or [],
                "message": "调试会话已准备就绪"
            }

        except Exception as e:
            return {"error": {"code": "session_error", "message": f"调试会话执行失败: {str(e)}"}}

    def get_debug_status_tool(self) -> Dict[str, Any]:
        """获取调试状态信息。"""
        try:
            breakpoints = self.debug_client.breakpoints
            # 这里可以添加更多状态信息，如连接状态、当前执行位置等

            return {
                "success": True,
                "breakpoints": list(breakpoints),
                "breakpoints_count": len(breakpoints),
                "status": "active" if self.debug_client.websocket and not self.debug_client.websocket.closed else "inactive"
            }

        except Exception as e:
            return {"error": {"code": "status_error", "message": f"获取调试状态失败: {str(e)}"}}

    def clear_all_breakpoints_tool(self) -> Dict[str, Any]:
        """清除所有断点。"""
        try:
            breakpoints = list(self.debug_client.breakpoints)
            if not breakpoints:
                return {"success": True, "message": "没有断点需要清除"}

            result = self.batch_remove_breakpoints_tool(breakpoints)
            if result["failed"] == 0:
                return {"success": True, "cleared_count": result["successful"], "message": f"成功清除 {result['successful']} 个断点"}
            else:
                return {"success": False, "error": {"code": "partial_clear", "message": f"部分断点清除失败: {result['failed']} 个失败"}}

        except Exception as e:
            return {"error": {"code": "clear_error", "message": f"清除断点失败: {str(e)}"}}


__all__ = ['MagicAPIWebSocketClient', 'parse_call_arg', 'run_custom_api_call', 'DebugCompleter', 'setup_readline', 'MagicAPIDebugClient', 'MagicAPIDebugTools']
