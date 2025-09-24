"""Magic-API API 执行类 MCP 工具。

此模块提供Magic-API接口的直接调用和测试功能，支持：
- 各种HTTP方法的API调用（GET、POST、PUT、DELETE等）
- 灵活的参数传递（查询参数、请求体、请求头）
- 自动错误处理和响应格式化
- 实时API测试和调试

主要工具：
- call_magic_api: 调用Magic-API接口并返回请求结果
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Dict, Optional

from pydantic import Field

from magicapi_tools.utils import error_response

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class ApiTools:
    """API 执行工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册调用相关工具。"""

        @mcp_app.tool(
            name="call_magic_api",
            description="调用 Magic-API 接口并返回请求结果，支持各种HTTP方法和参数。",
            tags={"api", "call", "http", "request"},
        )
        def call(
            method: Annotated[
                str,
                Field(description="HTTP请求方法，如'GET'、'POST'、'PUT'、'DELETE'等")
            ],
            path: Annotated[
                str,
                Field(description="API请求路径，如'/api/users'或'GET /api/users'")
            ],
            params: Annotated[
                Optional[Any],
                Field(description="URL查询参数")
            ] = None,
            data: Annotated[
                Optional[Any],
                Field(description="请求体数据，可以是字符串或其他序列化格式")
            ] = None,
            headers: Annotated[
                Optional[Any],
                Field(description="HTTP请求头")
            ] = None,
        ) -> Dict[str, Any]:
            """调用 Magic-API 接口并返回请求结果。"""

            ok, payload = context.http_client.call_api(method, path, params=params, data=data, headers=headers)
            if not ok:
                return error_response(payload.get("code"), payload.get("message", "调用接口失败"), payload.get("detail"))
            return payload

