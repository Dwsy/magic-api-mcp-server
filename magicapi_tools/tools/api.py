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
            description="调用 Magic-API 接口并返回请求结果，支持各种HTTP方法和参数。可以通过 method+path 或 api_id 方式调用。",
            tags={"api", "call", "http", "request"},
        )
        def call(
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
                Field(description="可选的接口ID，如果提供则会自动获取对应的method和path，覆盖上面的method和path参数")
            ] = None,
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
            """调用 Magic-API 接口并返回请求结果。

            支持两种调用方式：
            1. 直接传入 method 和 path: call_magic_api(method="GET", path="/api/users")
            2. 传入接口ID，会自动转换为完整路径: call_magic_api(api_id="123456")

            注意：method 和 path 参数现在都是可选的，当提供 api_id 时会自动覆盖这两个参数。
            """

            # 检查是否有api_id，如果有则获取详细信息覆盖method和path
            actual_method = method
            actual_path = path
            # 如果两者都为 null 抛出异常
            if actual_method is None and actual_path is None:
                return error_response("invalid_method_and_path", "method和path不能同时为空")

            if api_id:
                # 传入的是接口ID，先获取详细信息
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
                        print(f"🔄 使用接口ID {api_id}，已自动转换为: {actual_method} {actual_path}")
                    else:
                        return error_response("invalid_id", f"接口ID {api_id} 无法获取有效的路径信息")
                else:
                    return error_response("id_not_found", f"无法找到接口ID {api_id} 的详细信息")

            ok, payload = context.http_client.call_api(actual_method, actual_path, params=params, data=data, headers=headers)
            if not ok:
                return error_response(payload.get("code"), payload.get("message", "调用接口失败"), payload.get("detail"))
            return payload

