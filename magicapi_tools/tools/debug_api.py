"""断点调试相关的MCP工具，包括超时处理和断点状态轮询功能。

此模块提供：
- 超时控制的API调用
- 断点状态轮询
- 步过/单步调试功能
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Annotated, Any, Dict, Optional

from pydantic import Field

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import error_response
from magicapi_tools.ws.debug_service import WebSocketDebugService

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('tools.debug_api')


class DebugAPITools:
    """断点调试工具模块，提供超时控制和状态轮询功能。"""

    def __init__(self):
        self.timeout_duration = 1.0  # 默认1秒超时

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册断点调试相关工具。"""

        @mcp_app.tool(
            name="call_magic_api_with_timeout",
            description="调用 Magic-API 接口并返回请求结果，如果指定时间内没有响应则返回提示信息让客户端轮询断点状态。",
            tags={"api", "call", "timeout", "debug"},
        )
        def call_with_timeout(
            method: Annotated[
                str,
                Field(description="HTTP请求方法，如'GET'、'POST'、'PUT'、'DELETE'等")
            ],
            path: Annotated[
                Optional[str],
                Field(description="API请求路径，如'/api/users'或'GET /api/users'")
            ] = None,
            api_id: Annotated[
                Optional[str],
                Field(description="可选的接口ID，如果提供则会自动获取对应的method和path")
            ] = None,
            params: Annotated[
                Optional[Any],
                Field(description="URL查询参数")
            ] = None,
            data: Annotated[
                Optional[Any],
                Field(description="请求体数据")
            ] = None,
            headers: Annotated[
                Optional[Any],
                Field(description="HTTP请求头")
            ] = None,
            timeout: Annotated[
                float,
                Field(description="超时时间（秒），默认为1秒")
            ] = 1.0,
        ) -> Dict[str, Any]:
            """
            调用 Magic-API 接口，如果在指定时间内没有完成则返回提示信息，
            让客户端调用 get_latest_breakpoint_status 工具来轮询断点状态。
            """
            import threading
            from concurrent.futures import ThreadPoolExecutor, TimeoutError

            # 更新超时时间
            self.timeout_duration = timeout

            # 准备调用参数
            actual_method = method or "GET"
            actual_path = path

            # 如果提供了api_id，则优先使用api_id获取详细信息
            if api_id:
                ok, payload = context.http_client.api_detail(api_id)
                if ok and payload:
                    api_method = payload.get("method", "").upper()
                    api_path = payload.get("path", "")
                    if api_method and api_path:
                        actual_method = api_method
                        actual_path = api_path
                    else:
                        return error_response("invalid_id", f"接口ID {api_id} 无法获取有效的路径信息")
                else:
                    return error_response("id_not_found", f"无法找到接口ID {api_id} 的详细信息")

            # 检查路径是否有效
            if not actual_path:
                return error_response("invalid_path", "无法确定请求路径，请提供 path 或 api_id")

            # 整理headers
            provided_headers = headers or {}
            if isinstance(provided_headers, str):
                # 如果是字符串，尝试解析为JSON
                import json
                try:
                    provided_headers = json.loads(provided_headers)
                except json.JSONDecodeError:
                    return error_response("invalid_headers", "提供的headers不是有效的JSON格式")

            # 启动一个线程来执行API调用
            def execute_api_call():
                try:
                    context.ws_manager.ensure_running_sync()

                    # 构建请求头
                    script_id = provided_headers.get("Magic-Request-Script-Id") or api_id
                    if not script_id:
                        from magicapi_tools.ws.utils import resolve_script_id_by_path
                        script_id = resolve_script_id_by_path(context.http_client, actual_path)

                    breakpoint_header = provided_headers.get("Magic-Request-Breakpoints")
                    from magicapi_tools.ws.utils import normalize_breakpoints
                    normalized_breakpoints = normalize_breakpoints(breakpoint_header) if breakpoint_header else ""

                    base_headers = {
                        "Magic-Request-Script-Id": script_id,
                        "Magic-Request-Breakpoints": normalized_breakpoints,
                    }

                    request_headers = context.ws_manager.build_request_headers(base_headers)
                    request_headers.update({k: v for k, v in provided_headers.items() if v is not None})

                    # 执行API调用
                    ok, payload = context.http_client.call_api(
                        actual_method,
                        actual_path,
                        params=params,
                        data=data,
                        headers=request_headers,
                    )

                    if not ok:
                        detail_message = payload if isinstance(payload, str) else payload.get("detail") if isinstance(payload, dict) else None
                        error_message = payload.get("message") if isinstance(payload, dict) else payload if isinstance(payload, str) else "调用接口失败"
                        error_code = payload.get("code") if isinstance(payload, dict) else "api_error"
                        return error_response(error_code, error_message, detail_message)

                    # 等待一段时间以确保断点信息被处理
                    time.sleep(0.1)

                    # 检查断点状态
                    debug_service: WebSocketDebugService = context.ws_debug_service
                    status = debug_service.get_debug_status_tool()
                    if status.get("success"):
                        # 如果存在断点，返回断点状态
                        if status.get("status", {}).get("breakpoints"):
                            return {
                                "message": "API调用已启动并遇到断点，请使用 get_latest_breakpoint_status 工具查询最新断点状态。",
                                "status": "breakpoint_hit",
                                "timeout": timeout,
                                "breakpoint_status": status,
                                "expected_next_action": "get_latest_breakpoint_status"
                            }

                    return {
                        "success": True,
                        "response": payload,
                        "duration": 0.0,  # 实际持续时间未精确计算
                    }
                except Exception as e:
                    logger.error(f"API调用执行错误: {e}")
                    return error_response("api_execution_error", str(e))

            # 在线程池中执行API调用
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_api_call)
                try:
                    # 等待结果，但不超过指定的超时时间
                    result = future.result(timeout=timeout)
                    return result
                except TimeoutError:
                    # 超时情况下，返回提示信息让客户端轮询断点状态
                    return {
                        "message": "API调用已启动，正在等待响应。请使用 get_latest_breakpoint_status 工具查询最新断点状态。",
                        "status": "pending",
                        "timeout": timeout,
                        "expected_next_action": "get_latest_breakpoint_status"
                    }

        @mcp_app.tool(
            name="get_latest_breakpoint_status",
            description="获取最新的断点调试状态，用于轮询断点执行情况。",
            tags={"debug", "breakpoint", "status", "polling"},
        )
        def get_breakpoint_status() -> Dict[str, Any]:
            """获取最新的断点调试状态，用于轮询断点执行情况。"""
            try:
                context.ws_manager.ensure_running_sync()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 获取调试状态
                status = debug_service.get_debug_status_tool()

                if status.get("success"):
                    # 增加一个标记，表示这是一个断点状态检查
                    status["is_breakpoint_status"] = True
                    status["timestamp"] = time.time()
                    return status
                else:
                    return error_response("status_check_failed", "获取断点状态失败", status.get("error"))
            except Exception as e:
                logger.error(f"获取断点状态时出错: {e}")
                return error_response("status_check_error", f"获取断点状态时出错: {str(e)}")

        @mcp_app.tool(
            name="resume_from_breakpoint",
            description="从当前断点恢复执行。",
            tags={"debug", "breakpoint", "resume"},
        )
        async def resume_breakpoint() -> Dict[str, Any]:
            """从当前断点恢复执行。"""
            try:
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 执行恢复操作
                result = await debug_service.resume_breakpoint_tool()
                return result
            except Exception as e:
                logger.error(f"恢复断点执行时出错: {e}")
                return error_response("resume_error", f"恢复断点执行时出错: {str(e)}")

        @mcp_app.tool(
            name="step_over_breakpoint",
            description="单步执行，跳过当前断点。",
            tags={"debug", "breakpoint", "step", "over"},
        )
        async def step_over() -> Dict[str, Any]:
            """单步执行，跳过当前断点。"""
            try:
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 执行单步跳过操作
                result = await debug_service.step_over_tool()
                return result
            except Exception as e:
                logger.error(f"单步跳过断点时出错: {e}")
                return error_response("step_over_error", f"单步跳过断点时出错: {str(e)}")

        @mcp_app.tool(
            name="step_into_breakpoint",
            description="步入当前断点（进入函数/方法内部）。",
            tags={"debug", "breakpoint", "step", "into"},
        )
        async def step_into() -> Dict[str, Any]:
            """步入当前断点（进入函数/方法内部）。"""
            try:
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 发送步入指令 (step type 2)
                script_id = debug_service._current_script_id()
                if not script_id:
                    return {"error": {"code": "script_id_missing", "message": "无法确定当前调试脚本"}}
                
                await context.ws_manager.send_step_into(script_id, sorted(debug_service.breakpoints))
                return {"success": True, "script_id": script_id, "step_type": "into"}
            except Exception as e:
                logger.error(f"步入断点时出错: {e}")
                return error_response("step_into_error", f"步入断点时出错: {str(e)}")

        @mcp_app.tool(
            name="step_out_breakpoint",
            description="步出当前函数/方法（执行到当前函数结束）。",
            tags={"debug", "breakpoint", "step", "out"},
        )
        async def step_out() -> Dict[str, Any]:
            """步出当前函数/方法（执行到当前函数结束）。"""
            try:
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 发送步出指令 (step type 3)
                script_id = debug_service._current_script_id()
                if not script_id:
                    return {"error": {"code": "script_id_missing", "message": "无法确定当前调试脚本"}}
                
                await context.ws_manager.send_step_out(script_id, sorted(debug_service.breakpoints))
                return {"success": True, "script_id": script_id, "step_type": "out"}
            except Exception as e:
                logger.error(f"步出断点时出错: {e}")
                return error_response("step_out_error", f"步出断点时出错: {str(e)}")

        @mcp_app.tool(
            name="set_breakpoint",
            description="在指定行号设置断点。",
            tags={"debug", "breakpoint", "set"},
        )
        def set_breakpoint(
            line_number: Annotated[
                int,
                Field(description="要设置断点的行号")
            ],
        ) -> Dict[str, Any]:
            """在指定行号设置断点。"""
            try:
                context.ws_manager.ensure_running_sync()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 设置断点
                result = debug_service.set_breakpoint_tool(line_number=line_number)
                return result
            except Exception as e:
                logger.error(f"设置断点时出错: {e}")
                return error_response("set_breakpoint_error", f"设置断点时出错: {str(e)}")

        @mcp_app.tool(
            name="remove_breakpoint",
            description="移除指定行号的断点。",
            tags={"debug", "breakpoint", "remove"},
        )
        def remove_breakpoint(
            line_number: Annotated[
                int,
                Field(description="要移除断点的行号")
            ],
        ) -> Dict[str, Any]:
            """移除指定行号的断点。"""
            try:
                context.ws_manager.ensure_running_sync()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 移除断点
                result = debug_service.remove_breakpoint_tool(line_number=line_number)
                return result
            except Exception as e:
                logger.error(f"移除断点时出错: {e}")
                return error_response("remove_breakpoint_error", f"移除断点时出错: {str(e)}")

        @mcp_app.tool(
            name="list_breakpoints",
            description="列出当前所有断点。",
            tags={"debug", "breakpoint", "list"},
        )
        def list_breakpoints() -> Dict[str, Any]:
            """列出当前所有断点。"""
            try:
                context.ws_manager.ensure_running_sync()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 列出断点
                result = debug_service.list_breakpoints_tool()
                return result
            except Exception as e:
                logger.error(f"列出断点时出错: {e}")
                return error_response("list_breakpoints_error", f"列出断点时出错: {str(e)}")