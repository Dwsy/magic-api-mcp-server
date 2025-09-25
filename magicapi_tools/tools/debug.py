"""Magic-API 调试相关 MCP 工具。

此模块提供强大的调试功能，支持：
- 断点设置和管理
- 单步执行控制
- 变量检查和状态监控
- 调试会话管理
- WebSocket连接状态监控

主要工具：
- set_breakpoint: 在指定API脚本中设置断点
- remove_breakpoint: 移除指定的断点
- resume_breakpoint_execution: 恢复断点执行，继续运行调试脚本
- step_over_breakpoint: 单步执行，越过当前断点继续执行
- list_breakpoints: 列出所有当前设置的断点
- call_api_with_debug: 调用指定接口并在命中断点处暂停
- execute_debug_session: 执行完整的调试会话
- get_debug_status: 获取当前调试状态
- clear_all_breakpoints: 清除所有断点
- get_websocket_status: 获取WebSocket连接状态
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

from pydantic import Field

from magicapi_tools.utils import error_response
from magicapi_tools.ws import IDEEnvironment, MessageType, OpenFileContext
from magicapi_tools.ws.observers import MCPObserver

try:  # pragma: no cover - 运行环境缺失 fastmcp 时回退 Any
    from fastmcp import Context, FastMCP
except ImportError:  # pragma: no cover
    Context = Any  # type: ignore[assignment]
    FastMCP = Any  # type: ignore[assignment]

if TYPE_CHECKING:
    from magicapi_mcp.tool_registry import ToolContext


class DebugTools:
    """调试工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册调试相关工具。"""

        @mcp_app.tool(
            name="resume_breakpoint_execution",
            description="恢复断点执行，继续运行调试脚本。",
            tags={"debug", "execution", "breakpoint"},
        )
        async def resume_breakpoint(ctx: "Context") -> Dict[str, Any]:
            observer = MCPObserver(ctx)
            context.ws_manager.add_observer(observer)
            try:
                await ctx.info("▶️ 正在恢复断点执行")
                result = await context.ws_debug_service.resume_breakpoint_tool()
                return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])
            finally:
                await asyncio.sleep(context.settings.ws_log_capture_window)
                context.ws_manager.remove_observer(observer)

        @mcp_app.tool(
            name="step_over_breakpoint",
            description="单步执行，越过当前断点继续执行。",
            tags={"debug", "execution", "stepping"},
        )
        async def step_over(ctx: "Context") -> Dict[str, Any]:
            observer = MCPObserver(ctx)
            context.ws_manager.add_observer(observer)
            try:
                await ctx.info("⏭️ 单步越过当前断点")
                result = await context.ws_debug_service.step_over_tool()
                return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])
            finally:
                await asyncio.sleep(context.settings.ws_log_capture_window)
                context.ws_manager.remove_observer(observer)

        @mcp_app.tool(
            name="call_api_with_debug",
            description="调用指定接口并在命中的断点处暂停，便于调试。",
            tags={"debug", "api", "call"},
        )
        async def call_api_with_debug(
            path: Annotated[
                str,
                Field(description="API请求路径，如'/api/users'或'GET /api/users'")
            ]= '/algorithms/narcissistic/narcissistic-algorithm-v2',
            method: Annotated[
                str,
                Field(description="HTTP请求方法，如'GET'、'POST'、'PUT'、'DELETE'等")
            ] = "GET",
            data: Annotated[
                Optional[Any],
                Field(description="请求体数据，适用于POST/PUT等方法")
            ] = None,
            params: Annotated[
                Optional[Any],
                Field(description="URL查询参数")
            ] = None,
            breakpoints: Annotated[
                Optional[List[int]],
                Field(description="断点行号列表，用于调试，如'[5,10,15]'")
            ] = [5,6,7],
            ctx: "Context" = None,
        ) -> Dict[str, Any]:
            observer = MCPObserver(ctx) if ctx else None
            if observer:
                context.ws_manager.add_observer(observer)
            try:
                if ctx:
                    await ctx.info("🧪 发起调试调用", extra={"path": path, "method": method})
                    await ctx.report_progress(progress=0, total=100)
                result = await context.ws_debug_service.call_api_with_debug_tool(
                    path=path,
                    method=method,
                    data=data,
                    params=params,
                    breakpoints=breakpoints,
                )
                ws_logs = result.get("ws_logs", []) if isinstance(result, dict) else []
                if ctx:
                    await ctx.report_progress(progress=100, total=100)
                    await _emit_ws_notifications(ctx, ws_logs)
                    env_snapshot = context.ws_manager.state.get_environment_by_client(
                        context.ws_manager.client.client_id
                    )
                    if env_snapshot:
                        await ctx.info("当前调试环境", extra=_serialize_environment(env_snapshot))
                if "success" in result:
                    return result
                error_payload = error_response(result["error"]["code"], result["error"]["message"], result["error"].get("detail"))
                if ws_logs:
                    error_payload["ws_logs"] = ws_logs
                return error_payload
            finally:
                if observer:
                    await asyncio.sleep(context.settings.ws_log_capture_window)
                    context.ws_manager.remove_observer(observer)

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

            result = context.debug_tools.execute_debug_session_tool(script_id, breakpoints_list)
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
