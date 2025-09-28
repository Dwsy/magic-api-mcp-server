"""Magic-API 调试相关 MCP 工具。

此模块提供强大的调试功能，支持：
- 断点设置和管理
- 单步执行控制
- 变量检查和状态监控
- 调试会话管理
- WebSocket连接状态监控
- 异步断点调试和超时处理
- 断点状态轮询
- 会话ID管理

主要工具：
- call_magic_api_with_debug: 异步调用API并监听断点，返回会话ID
- get_latest_breakpoint_status: 获取最新断点状态
- resume_from_breakpoint: 恢复断点执行
- step_over_breakpoint: 单步执行，越过当前断点
- step_into_breakpoint: 步入当前断点
- step_out_breakpoint: 步出当前函数
- set_breakpoint: 在指定行号设置断点
- remove_breakpoint: 移除指定断点
- list_breakpoints: 列出所有断点
- execute_debug_session: 执行完整的调试会话
- get_debug_status: 获取当前调试状态
- inspect_ws_environments: 检查WebSocket环境
- get_websocket_status: 获取WebSocket连接状态
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional, Union

from pydantic import Field

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import error_response
from magicapi_tools.ws import IDEEnvironment, MessageType, OpenFileContext
from magicapi_tools.ws.debug_service import WebSocketDebugService
from magicapi_tools.ws.observers import MCPObserver

try:  # pragma: no cover - 运行环境缺失 fastmcp 时回退 Any
    from fastmcp import Context, FastMCP
except ImportError:  # pragma: no cover
    Context = Any  # type: ignore[assignment]
    FastMCP = Any  # type: ignore[assignment]

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('tools.debug_api')


class DebugAPITools:
    """统一的调试工具模块，整合基础调试和高级断点控制功能。"""

    def __init__(self):
        self.timeout_duration = 10.0  # 默认10秒超时
        self.debug_sessions = {}  # 存储调试会话信息

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册断点调试相关工具。"""

        @mcp_app.tool(
            name="call_magic_api_with_debug",
            description="异步调用Magic-API接口并监听断点，返回会话ID用于后续操作。支持10秒超时监听，遇到断点时返回断点信息和操作提示。",
            tags={"api", "call", "debug", "async", "session"},
        )
        async def call_with_debug(
            path: Annotated[
                str,
                Field(description="API请求路径，如'/api/users'或'GET /api/users'")
            ] = '/algorithms/narcissistic/narcissistic-algorithm-v2',
            method: Annotated[
                str,
                Field(description="HTTP请求方法，如'GET'、'POST'、'PUT'、'DELETE'等")
            ] = "GET",
            data: Annotated[
                Optional[Union[Any, str]],
                Field(description="请求体数据，适用于POST/PUT等方法")
            ] = None,
            params: Annotated[
                Optional[Union[Any, str]],
                Field(description="URL查询参数")
            ] = None,
            breakpoints: Annotated[
                Optional[Union[List[int], str]],
                Field(description="断点行号列表，用于调试，如'[5,10,15]'")
            ] = [5,6,7],
            timeout: Annotated[
                float,
                Field(description="超时时间（秒），默认为10秒")
            ] = 10.0,
            ctx: "Context" = None,
        ) -> Dict[str, Any]:
            """异步调用API并监听断点，返回会话ID用于后续操作。"""
            # 生成4位会话ID
            session_id = str(uuid.uuid4())[:4]
            
            # 参数清理：将空字符串转换为 None
            if isinstance(data, str) and data.strip() == "":
                data = None
            if isinstance(params, str) and params.strip() == "":
                params = None
            if isinstance(breakpoints, str) and breakpoints.strip() == "":
                breakpoints = None

            # 初始化会话信息
            self.debug_sessions[session_id] = {
                "status": "starting",
                "path": path,
                "method": method,
                "start_time": time.time(),
                "timeout": timeout,
                "breakpoints_hit": [],
                "current_breakpoint": None,
                "api_completed": False
            }

            observer = MCPObserver(ctx) if ctx else None
            if observer:
                context.ws_manager.add_observer(observer)
            
            try:
                if ctx:
                    await ctx.info("🧪 启动异步调试会话", extra={"session_id": session_id, "path": path, "method": method})
                    await ctx.report_progress(progress=0, total=100)
                
                # 异步调用API并监听断点
                result = await self._async_debug_call(
                    context, session_id, path, method, data, params, breakpoints, timeout, ctx
                )
                
                if ctx:
                    await ctx.report_progress(progress=100, total=100)
                
                return result
                
            except Exception as e:
                logger.error(f"异步调试调用失败: {e}")
                self.debug_sessions[session_id]["status"] = "error"
                self.debug_sessions[session_id]["error"] = str(e)
                return error_response("async_debug_error", f"异步调试调用失败: {str(e)}", {"session_id": session_id})
            finally:
                if observer:
                    await asyncio.sleep(context.settings.ws_log_capture_window)
                    context.ws_manager.remove_observer(observer)

        @mcp_app.tool(
            name="get_latest_breakpoint_status",
            description="获取最新的断点调试状态，用于轮询断点执行情况。需要传入会话ID。",
            tags={"debug", "breakpoint", "status", "polling"},
        )
        def get_breakpoint_status(
            session_id: Annotated[
                str,
                Field(description="调试会话ID，由call_magic_api_with_debug返回")
            ]
        ) -> Dict[str, Any]:
            """获取指定会话的最新断点调试状态。"""
            try:
                # 检查会话是否存在
                if session_id not in self.debug_sessions:
                    return error_response("session_not_found", f"调试会话 {session_id} 不存在")
                
                session = self.debug_sessions[session_id]
                context.ws_manager.ensure_running_sync()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 获取调试状态
                status = debug_service.get_debug_status_tool()

                if status.get("success"):
                    # 增加会话信息
                    status["session_id"] = session_id
                    status["session_info"] = session
                    status["is_breakpoint_status"] = True
                    status["timestamp"] = time.time()
                    
                    # 检查是否有断点
                    breakpoints = status.get("status", {}).get("breakpoints", [])
                    if breakpoints:
                        session["current_breakpoint"] = breakpoints[0] if breakpoints else None
                        session["status"] = "breakpoint_hit"
                        status["available_actions"] = [
                            "resume_from_breakpoint",
                            "step_over_breakpoint", 
                            "step_into_breakpoint",
                            "step_out_breakpoint"
                        ]
                        status["message"] = "遇到断点，可以选择恢复执行或单步调试"
                    elif session["api_completed"]:
                        session["status"] = "completed"
                        status["message"] = "断点调试结束，API返回完成"
                    else:
                        session["status"] = "running"
                        status["message"] = "API正在执行中，请继续轮询"
                    
                    return status
                else:
                    return error_response("status_check_failed", "获取断点状态失败", status.get("error"))
            except Exception as e:
                logger.error(f"获取断点状态时出错: {e}")
                return error_response("status_check_error", f"获取断点状态时出错: {str(e)}")

        @mcp_app.tool(
            name="resume_from_breakpoint",
            description="从当前断点恢复执行，继续10秒超时监听。需要传入会话ID。",
            tags={"debug", "breakpoint", "resume"},
        )
        async def resume_breakpoint(
            session_id: Annotated[
                str,
                Field(description="调试会话ID")
            ]
        ) -> Dict[str, Any]:
            """从当前断点恢复执行，继续监听。"""
            try:
                # 检查会话是否存在
                if session_id not in self.debug_sessions:
                    return error_response("session_not_found", f"调试会话 {session_id} 不存在")
                
                session = self.debug_sessions[session_id]
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 执行恢复操作
                result = await debug_service.resume_breakpoint_tool()
                
                if result.get("success"):
                    session["status"] = "resumed"
                    # 继续监听10秒
                    monitor_result = await self._monitor_breakpoint_with_timeout(context, session_id, 10.0)
                    result.update(monitor_result)
                
                return result
            except Exception as e:
                logger.error(f"恢复断点执行时出错: {e}")
                return error_response("resume_error", f"恢复断点执行时出错: {str(e)}")

        @mcp_app.tool(
            name="step_over_breakpoint",
            description="单步执行，跳过当前断点，继续10秒超时监听。需要传入会话ID。",
            tags={"debug", "breakpoint", "step", "over"},
        )
        async def step_over(
            session_id: Annotated[
                str,
                Field(description="调试会话ID")
            ]
        ) -> Dict[str, Any]:
            """单步执行，跳过当前断点，继续监听。"""
            try:
                # 检查会话是否存在
                if session_id not in self.debug_sessions:
                    return error_response("session_not_found", f"调试会话 {session_id} 不存在")
                
                session = self.debug_sessions[session_id]
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 执行单步跳过操作
                result = await debug_service.step_over_tool()
                
                if result.get("success"):
                    session["status"] = "stepped_over"
                    # 继续监听10秒
                    monitor_result = await self._monitor_breakpoint_with_timeout(context, session_id, 10.0)
                    result.update(monitor_result)
                
                return result
            except Exception as e:
                logger.error(f"单步跳过断点时出错: {e}")
                return error_response("step_over_error", f"单步跳过断点时出错: {str(e)}")

        @mcp_app.tool(
            name="step_into_breakpoint",
            description="步入当前断点（进入函数/方法内部），继续10秒超时监听。需要传入会话ID。",
            tags={"debug", "breakpoint", "step", "into"},
        )
        async def step_into(
            session_id: Annotated[
                str,
                Field(description="调试会话ID")
            ]
        ) -> Dict[str, Any]:
            """步入当前断点（进入函数/方法内部），继续监听。"""
            try:
                # 检查会话是否存在
                if session_id not in self.debug_sessions:
                    return error_response("session_not_found", f"调试会话 {session_id} 不存在")
                
                session = self.debug_sessions[session_id]
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 发送步入指令 (step type 2)
                script_id = debug_service._current_script_id()
                if not script_id:
                    return error_response("script_id_missing", "无法确定当前调试脚本")
                
                await context.ws_manager.send_step_into(script_id, sorted(debug_service.breakpoints))
                session["status"] = "stepped_into"
                
                # 继续监听10秒
                monitor_result = await self._monitor_breakpoint_with_timeout(context, session_id, 10.0)
                result = {"success": True, "script_id": script_id, "step_type": "into", "session_id": session_id}
                result.update(monitor_result)
                
                return result
            except Exception as e:
                logger.error(f"步入断点时出错: {e}")
                return error_response("step_into_error", f"步入断点时出错: {str(e)}")

        @mcp_app.tool(
            name="step_out_breakpoint",
            description="步出当前函数/方法（执行到当前函数结束），继续10秒超时监听。需要传入会话ID。",
            tags={"debug", "breakpoint", "step", "out"},
        )
        async def step_out(
            session_id: Annotated[
                str,
                Field(description="调试会话ID")
            ]
        ) -> Dict[str, Any]:
            """步出当前函数/方法（执行到当前函数结束），继续监听。"""
            try:
                # 检查会话是否存在
                if session_id not in self.debug_sessions:
                    return error_response("session_not_found", f"调试会话 {session_id} 不存在")
                
                session = self.debug_sessions[session_id]
                await context.ws_manager.ensure_running()

                # 获取WebSocket调试服务
                debug_service: WebSocketDebugService = context.ws_debug_service

                # 发送步出指令 (step type 3)
                script_id = debug_service._current_script_id()
                if not script_id:
                    return error_response("script_id_missing", "无法确定当前调试脚本")
                
                await context.ws_manager.send_step_out(script_id, sorted(debug_service.breakpoints))
                session["status"] = "stepped_out"
                
                # 继续监听10秒
                monitor_result = await self._monitor_breakpoint_with_timeout(context, session_id, 10.0)
                result = {"success": True, "script_id": script_id, "step_type": "out", "session_id": session_id}
                result.update(monitor_result)
                
                return result
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

        # 从 debug.py 合并过来的工具
        @mcp_app.tool(
            name="execute_debug_session",
            description="执行完整的调试会话，包括断点设置和状态监控。",
            tags={"debug", "session", "execution"},
        )
        def execute_debug_session(
            script_id: Annotated[
                str,
                Field(description="要调试的脚本文件ID，如'1234567890'")
            ],
            breakpoints: Annotated[
                str,
                Field(description="断点配置，JSON数组格式如'[5,10,15]'，指定在哪些行设置断点")
            ] = "[]"
        ) -> Dict[str, Any]:
            try:
                breakpoints_list = json.loads(breakpoints)
            except json.JSONDecodeError:
                return error_response("invalid_json", f"breakpoints 格式错误: {breakpoints}")

            result = context.ws_debug_service.execute_debug_session_tool(script_id, breakpoints_list)
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="get_debug_status",
            description="获取当前调试状态，包括断点信息和连接状态。",
            tags={"debug", "status", "monitoring"},
        )
        def get_debug_status() -> Dict[str, Any]:
            result = context.ws_debug_service.get_debug_status_tool()
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="inspect_ws_environments",
            description="列出当前MCP会话感知到的IDE环境、客户端与打开的文件上下文。",
            tags={"debug", "status", "websocket"},
        )
        def inspect_ws_environments() -> Dict[str, Any]:
            environments = [
                _serialize_environment(env)
                for env in context.ws_manager.state.list_environments()
            ]
            return {"success": True, "environments": environments}

        @mcp_app.tool(
            name="get_websocket_status",
            description="检查WebSocket连接状态和配置信息。",
            tags={"websocket", "status", "connection"},
        )
        def websocket_status() -> Dict[str, Any]:
            return {
                "success": True,
                "status": "ready",
                "ws_url": context.settings.ws_url,
                "base_url": context.settings.base_url,
                "auth_enabled": context.settings.auth_enabled,
                "note": "WebSocket连接在需要时自动建立，可通过调试工具进行实时操作",
            }

    async def _async_debug_call(
        self, 
        context, 
        session_id: str, 
        path: str, 
        method: str, 
        data: Any, 
        params: Any, 
        breakpoints: Any, 
        timeout: float,
        ctx: "Context" = None
    ) -> Dict[str, Any]:
        """异步调用API并监听断点。"""
        try:
            # 调用API并设置断点
            result = await context.ws_debug_service.call_api_with_debug_tool(
                path=path,
                method=method,
                data=data,
                params=params,
                breakpoints=breakpoints,
            )
            
            # 更新会话状态
            session = self.debug_sessions[session_id]
            session["api_call_result"] = result
            
            if "success" in result:
                session["status"] = "api_called"
                # 监听断点
                monitor_result = await self._monitor_breakpoint_with_timeout(context, session_id, timeout)
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": "异步调试会话已启动",
                    "api_result": result,
                    "monitor_result": monitor_result,
                    "timeout": timeout
                }
            else:
                session["status"] = "api_failed"
                session["error"] = result.get("error", {})
                return error_response(
                    result["error"]["code"], 
                    result["error"]["message"], 
                    {"session_id": session_id, "api_result": result}
                )
                
        except Exception as e:
            logger.error(f"异步调试调用失败: {e}")
            session = self.debug_sessions[session_id]
            session["status"] = "error"
            session["error"] = str(e)
            return error_response("async_debug_call_error", str(e), {"session_id": session_id})

    async def _monitor_breakpoint_with_timeout(
        self, 
        context, 
        session_id: str, 
        timeout: float
    ) -> Dict[str, Any]:
        """在指定超时时间内监听断点。"""
        start_time = time.time()
        session = self.debug_sessions[session_id]
        
        try:
            while time.time() - start_time < timeout:
                # 检查断点状态
                debug_service: WebSocketDebugService = context.ws_debug_service
                status = debug_service.get_debug_status_tool()
                
                if status.get("success"):
                    breakpoints = status.get("status", {}).get("breakpoints", [])
                    
                    if breakpoints:
                        # 遇到断点
                        session["current_breakpoint"] = breakpoints[0]
                        session["status"] = "breakpoint_hit"
                        session["breakpoints_hit"].append({
                            "breakpoint": breakpoints[0],
                            "timestamp": time.time()
                        })
                        
                        return {
                            "status": "breakpoint_hit",
                            "breakpoint": breakpoints[0],
                            "message": f"遇到断点在第 {breakpoints[0]} 行，可以选择恢复执行或单步调试",
                            "available_actions": [
                                "resume_from_breakpoint",
                                "step_over_breakpoint", 
                                "step_into_breakpoint",
                                "step_out_breakpoint"
                            ],
                            "session_id": session_id,
                            "elapsed_time": time.time() - start_time
                        }
                    
                    # 检查API是否完成
                    if self._is_api_completed(status):
                        session["api_completed"] = True
                        session["status"] = "completed"
                        return {
                            "status": "completed",
                            "message": "断点调试结束，API返回完成",
                            "session_id": session_id,
                            "elapsed_time": time.time() - start_time
                        }
                
                # 等待一段时间再检查
                await asyncio.sleep(0.5)
            
            # 超时
            session["status"] = "timeout"
            return {
                "status": "timeout",
                "message": f"监听超时 ({timeout}秒)，请使用 get_latest_breakpoint_status 查询最新状态",
                "session_id": session_id,
                "timeout": timeout,
                "expected_next_action": "get_latest_breakpoint_status"
            }
            
        except Exception as e:
            logger.error(f"监听断点时出错: {e}")
            session["status"] = "monitor_error"
            session["error"] = str(e)
            return {
                "status": "error",
                "message": f"监听断点时出错: {str(e)}",
                "session_id": session_id
            }
    
    def _is_api_completed(self, status: Dict[str, Any]) -> bool:
        """检查API是否已完成。"""
        # 这里需要根据实际的状态结构来判断
        # 可能需要检查是否没有正在执行的请求或者其他标志
        return False  # 暂时返回false，需要根据实际情况调整


# 从 debug.py 合并过来的辅助函数
async def _emit_ws_notifications(ctx: "Context", logs: List[Dict[str, Any]]) -> None:
    for entry in logs or []:
        msg_type = (entry.get("type") or "log").upper()
        text = entry.get("text") or entry.get("payload") or ""
        extra = {k: v for k, v in entry.items() if k not in {"text", "payload"}}
        try:
            level = MessageType(msg_type)
        except ValueError:
            level = MessageType.LOG

        if level == MessageType.BREAKPOINT:
            await ctx.warning(text, extra=extra)
        elif level == MessageType.EXCEPTION:
            await ctx.error(text, extra=extra)
        elif level in {MessageType.LOG, MessageType.LOGS}:
            await ctx.debug(text, extra=extra)
        else:
            await ctx.info(text, extra=extra)


def _serialize_environment(env: IDEEnvironment) -> Dict[str, Any]:
    opened = {}
    for client_id, ctx in env.opened_files.items():
        opened[client_id] = _serialize_open_file_context(ctx)
    return {
        "ide_key": env.ide_key,
        "primary_ip": env.primary_ip,
        "client_ids": sorted(env.client_ids),
        "latest_user": env.latest_user,
        "opened_files": opened,
        "last_active_at": env.last_active_at,
    }


def _serialize_open_file_context(ctx: OpenFileContext) -> Dict[str, Any]:
    return {
        "file_id": ctx.file_id,
        "resolved_at": ctx.resolved_at,
        "method": ctx.method,
        "path": ctx.path,
        "name": ctx.name,
        "group_chain": ctx.group_chain,
        "headers": ctx.headers,
        "last_breakpoint_range": ctx.last_breakpoint_range,
        "detail": ctx.detail,
    }