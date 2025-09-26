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

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Annotated, Any, Dict, Optional, Union

from pydantic import Field

from magicapi_tools.logging_config import get_logger
from magicapi_tools.ws import normalize_breakpoints

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
            ]= "POST",
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
                Field(description="WebSocket日志捕获配置。None表示不捕获，{}表示使用默认值(前0.1秒后0.1秒)，或指定{'pre': 1.0, 'post': 1.5}自定义前后等待时间")
            ] = {"pre": 0.1, "post": 1.5},
        ) -> Dict[str, Any]:
            """调用 Magic-API 接口并返回请求结果。

            支持两种调用方式：
            1. 直接传入 method 和 path: call_magic_api(method="GET", path="/api/users")
            2. 传入接口ID，会自动转换为完整路径: call_magic_api(api_id="123456")

            参数要求：
            - 如果提供 api_id，可以只填写 api_id，系统会自动获取完整路径
            - 如果不提供 api_id，需要同时提供 method 和 path
            - 如果提供了 path，必须同时提供 method
            - api_id 优先级最高，会忽略 method 和 path 参数

            WebSocket日志捕获说明：
            - include_ws_logs=None: 不捕获日志
            - include_ws_logs={}: 使用默认配置(前0.1秒，后1.5秒)
            - include_ws_logs={'pre': 0.5, 'post': 1.5}: 自定义等待时间
            """

            # 使用业务服务层处理API调用
            from magicapi_tools.domain.dtos.api_dtos import ApiCallRequest

            request = ApiCallRequest(
                method=method,
                path=path,
                api_id=api_id,
                params=params,
                data=data,
                headers=headers,
                ws_log_config=include_ws_logs
            )

            response = context.api_service.call_api_with_details(request)
            return response.to_dict()


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
