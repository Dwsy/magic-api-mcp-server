"""Magic-API API 执行类 MCP 工具。

此模块提供Magic-API接口的直接调用和测试功能，支持：
- 各种HTTP方法的API调用（GET、POST、PUT、DELETE等）
- 灵活的参数传递（查询参数、请求体、请求头）
- 自动错误处理和响应格式化
- 实时API测试和调试

重要提示：
- 支持两种调用方式：
  1. 直接传入 method 和 path: call_magic_api(method="GET", path="/api/users")
  2. 传入接口ID自动转换: call_magic_api(api_id="123456")
- 推荐使用完整的调用路径格式：如 "GET /api/users" 而不是分别传入 method 和 path
- 建议先通过查询工具获取接口的 full_path，然后直接使用该路径调用

主要工具：
- call_magic_api: 调用Magic-API接口并返回请求结果，支持ID自动转换
"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Annotated, Any, Dict, Optional, Union

from pydantic import Field

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import error_response
from magicapi_tools.ws import normalize_breakpoints, resolve_script_id_by_path

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext

# 获取API工具的logger
logger = get_logger('tools.api')


class ApiTools:
    """API 执行工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册调用相关工具。"""

        @mcp_app.tool(
            name="call_magic_api",
            description="调用 Magic-API 接口并返回请求结果，支持各种HTTP方法和参数。可以通过 method+path 或 api_id 方式调用。",
            tags={"api", "call", "http", "request"},
        )
        def call(
            method: Annotated[
                str,
                Field(description="HTTP请求方法，如'GET'、'POST'、'PUT'、'DELETE'等")
            ],
            path: Annotated[
                Optional[Union[str, None]],
                Field(description="API请求路径，如'/api/users'或'GET /api/users'")
            ] = None,
            api_id: Annotated[
                Optional[Union[str, None]],
                Field(description="可选的接口ID，如果提供则会自动获取对应的method和path，覆盖上面的method和path参数")
            ] = None,
            params: Annotated[
                Optional[Union[Any, str]],
                Field(description="URL查询参数")
            ] = None,
            data: Annotated[
                Optional[Union[Any, str]],
                Field(description="请求体数据，可以是字符串或其他序列化格式")
            ] = None,
            headers: Annotated[
                Optional[Union[Any, str]],
                Field(description="HTTP请求头")
            ] = None,
            include_ws_logs: Annotated[
                Optional[Union[Dict[str, float], str]],
                Field(description="WebSocket日志捕获配置。None表示不捕获，{}表示使用默认值(前0.1秒后0.1秒)，或指定{'pre': 1.0, 'post': 2.5}自定义前后等待时间")
            ] = {"pre": 0.1, "post": 2.5},
        ) -> Dict[str, Any]:
            """调用 Magic-API 接口并返回请求结果。

            支持两种调用方式：
            1. 直接传入 method 和 path: call_magic_api(method="GET", path="/api/users")
            2. 传入接口ID，会自动转换为完整路径: call_magic_api(api_id="123456")

            注意：如果提供了 api_id，系统会优先使用接口ID获取详细信息，完全忽略 method 和 path 参数。

            WebSocket日志捕获说明：
            - include_ws_logs=None: 不捕获日志
            - include_ws_logs={}: 使用默认配置(前0.1秒，后2.5秒)
            - include_ws_logs={'pre': 0.5, 'post': 2.5}: 自定义等待时间
            """

            # 参数清理：将空字符串转换为 None
            if isinstance(path, str) and path.strip() == "":
                path = None
            if isinstance(api_id, str) and api_id.strip() == "":
                api_id = None
            if isinstance(params, str) and params.strip() == "":
                params = None
            if isinstance(data, str) and data.strip() == "":
                data = None
            if isinstance(headers, str) and headers.strip() == "":
                headers = None
            if isinstance(include_ws_logs, str) and include_ws_logs.strip() == "":
                include_ws_logs = {"pre": 0.1, "post": 2.5}

            # 检查是否有api_id，如果有则优先使用ID获取详细信息，忽略path参数
            if api_id:
                # 传入的是接口ID，先获取详细信息，完全忽略path参数
                ok, payload = context.http_client.api_detail(api_id)
                if ok and payload:
                    api_method = payload.get("method", "").upper()
                    api_path = payload.get("path", "")
                    api_name = payload.get("name", "")

                    if api_method and api_path:
                        # 使用可复用函数获取完整的资源树路径
                        from magicapi_tools.tools.query import _get_full_path_by_api_details
                        full_path = _get_full_path_by_api_details(context.http_client, api_id, api_method, api_path, api_name)

                        # 解析完整路径
                        if " " in full_path:
                            actual_method, actual_path = full_path.split(" ", 1)
                        else:
                            actual_method = api_method
                            actual_path = api_path

                        # 更新提示信息，告知用户正在使用转换后的路径
                        logger.info(f"使用接口ID {api_id}，已自动转换为: {actual_method} {actual_path}")
                    else:
                        logger.error(f"接口ID转换失败: 无法获取有效的路径信息")
                        logger.error(f"  API ID: {api_id}")
                        logger.debug(f"  获取到的数据: {payload}")
                        logger.error(f"  方法: {api_method}, 路径: {api_path}")
                        return error_response("invalid_id", f"接口ID {api_id} 无法获取有效的路径信息")
                else:
                    logger.error(f"无法找到接口ID的详细信息")
                    logger.error(f"  API ID: {api_id}")
                    logger.error(f"  获取结果: {ok}")
                    logger.debug(f"  错误详情: {payload}")
                    return error_response("id_not_found", f"无法找到接口ID {api_id} 的详细信息")
            else:
                # 没有提供api_id，使用method和path参数
                actual_method = method
                actual_path = path
                # 检查method和path是否都为空
                if actual_method is None and actual_path is None:
                    return error_response("invalid_method_and_path", "method和path不能同时为空")

            actual_method, actual_path = _normalize_method_path(actual_method, actual_path)
            if actual_path is None:
                return error_response("invalid_path", "无法确定请求路径，请提供 path 或 api_id")

            context.ws_manager.ensure_running_sync()

            try:
                provided_headers = _sanitize_headers(headers)
            except ValueError as exc:
                return error_response("invalid_headers", str(exc))

            script_id = provided_headers.get("Magic-Request-Script-Id") or api_id
            if not script_id:
                script_id = resolve_script_id_by_path(context.http_client, actual_path)
            if not script_id:
                return error_response("script_id_not_found", "无法根据路径定位接口脚本，请提供 api_id 或同步资源树")

            breakpoint_header = provided_headers.get("Magic-Request-Breakpoints")
            normalized_breakpoints = _normalize_breakpoints_value(breakpoint_header)

            base_headers = {
                "Magic-Request-Script-Id": script_id,
                "Magic-Request-Breakpoints": normalized_breakpoints,
            }

            request_headers = context.ws_manager.build_request_headers(base_headers)
            request_headers.update({k: v for k, v in provided_headers.items() if v is not None})

            capture_config = include_ws_logs
            if capture_config is None:
                pre_wait = 0.0
                post_wait = 0.0
            else:
                pre_wait = capture_config.get("pre", 0.1)
                post_wait = capture_config.get("post", 0.1)

            start_ts = time.time()
            ok, payload = context.http_client.call_api(
                actual_method,
                actual_path,
                params=params,
                data=data,
                headers=request_headers,
            )

            execution_end = time.time()

            # 等待post时间，让后续WebSocket日志能够被完全捕获
            if post_wait > 0:
                time.sleep(post_wait)

            # 获取WebSocket日志
            ws_logs = []
            if capture_config is not None:  # 只有当配置不为None时才捕获日志
                logs = context.ws_manager.capture_logs_between(
                    start_ts,
                    execution_end,
                    pre=pre_wait,
                    post=post_wait,
                )
                ws_logs = [
                    {
                        "timestamp": message.timestamp,
                        "type": message.type.value,
                        "payload": message.payload,
                    }
                    for message in logs
                ]
            duration = execution_end - start_ts
            if not ok:
                detail_message = payload if isinstance(payload, str) else payload.get("detail") if isinstance(payload, dict) else None
                error_message = payload.get("message") if isinstance(payload, dict) else "调用接口失败"
                error_code = payload.get("code") if isinstance(payload, dict) else "api_error"
                error_payload = error_response(error_code, error_message, detail_message)
                if capture_config is not None:
                    error_payload["ws_logs"] = ws_logs
                    error_payload["duration"] = duration
                return error_payload

            result = dict(payload)
            result.setdefault("duration", duration)
            if capture_config is not None:
                result["ws_logs"] = ws_logs
            return result


def _normalize_method_path(method: Optional[str], path: Optional[str]) -> tuple[str, Optional[str]]:
    """统一处理 method/path 组合，支持 `"GET /foo"` 输入。"""
    http_method = (method or "GET").upper()
    candidate = (path or "").strip() if path else None
    if candidate:
        if " " in candidate:
            head, tail = candidate.split(" ", 1)
            upper = head.upper()
            if upper in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
                http_method = upper
                candidate = tail.strip()
        if candidate and not candidate.startswith("/"):
            candidate = f"/{candidate}"
    return http_method, candidate


def _sanitize_headers(headers: Optional[Any]) -> Dict[str, str]:
    if headers is None:
        return {}
    if isinstance(headers, Mapping):
        return {str(k): str(v) for k, v in headers.items() if v is not None}
    raise ValueError("headers 参数必须是字典类型")


def _normalize_breakpoints_value(value: Optional[Any]) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Sequence):
        return normalize_breakpoints(value)
    try:
        return normalize_breakpoints(value)
    except Exception:
        return ""
