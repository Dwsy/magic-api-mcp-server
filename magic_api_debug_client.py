#!/usr/bin/env python3
"""Magic-API 调试客户端 CLI。"""

from __future__ import annotations

import asyncio
import json
import sys
import threading
import time

from magicapi_tools import MagicAPISettings
from magicapi_tools import MagicAPIDebugClient, setup_readline


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
    settings = MagicAPISettings.from_env()
    WS_URL = settings.ws_url
    API_BASE_URL = settings.base_url
    USERNAME = settings.username or 'guest'
    PASSWORD = settings.password or ''

    print("🚀 Magic-API 调试客户端启动")
    print(f"📡 WebSocket URL: {WS_URL}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"👤 用户名: {USERNAME}")
    print("-" * 50)

    # 设置readline支持方向键和自动补全
    setup_readline()

    # 创建调试客户端
    client = MagicAPIDebugClient(
        WS_URL,
        API_BASE_URL,
        USERNAME if settings.auth_enabled else None,
        PASSWORD if settings.auth_enabled else None,
    )

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
                            breakpoints=breakpoints,
                            script_id="e411103cbd334af9b264fe3fe55d1a42"
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


async def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print_usage()
        sys.exit(0)

    # 启动交互式调试会话
    await interactive_debug_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        sys.exit(1)
