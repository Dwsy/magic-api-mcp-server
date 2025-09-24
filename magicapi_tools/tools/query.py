"""Magic-API 查询相关 MCP 工具。

此模块提供高效的资源查询和检索功能，包括：
- 路径到ID的快速转换
- API详细信息查询
- 批量资源查询
- 资源路径查找和匹配

主要工具：
- find_resource_id_by_path: 根据API路径查找对应的资源ID，支持模糊匹配
- get_api_details_by_path: 根据API路径直接获取接口的详细信息，支持模糊匹配
- find_api_ids_by_path: 批量查找匹配路径的API资源ID列表
- find_api_details_by_path: 批量获取匹配路径的API资源详细信息
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Dict, Optional

from pydantic import Field

from magicapi_tools.utils.extractor import extract_api_endpoints, load_resource_tree
from magicapi_tools.utils.extractor import filter_endpoints
from magicapi_tools.tools.common import (
    error_response,
    find_api_details_by_path_impl,
    find_api_ids_by_path_impl,
    path_to_id_impl,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class QueryTools:
    """查询工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册查询相关工具。"""

        @mcp_app.tool(
            name="find_resource_id_by_path",
            description="根据API路径查找对应的资源ID，支持模糊匹配。",
            tags={"resource", "lookup", "path", "id"},
        )
        def path_to_id(
            path: Annotated[
                str,
                Field(description="API路径，用于查找对应的资源ID，如'/db/sql'或'GET /db/db/sql'")
            ],
            fuzzy: Annotated[
                bool,
                Field(description="是否启用模糊匹配，true时支持部分路径匹配，false时要求精确匹配")
            ] = True
        ) -> Dict[str, Any]:
            return path_to_id_impl(context.http_client, path, fuzzy)

        @mcp_app.tool(
            name="get_api_details_by_path",
            description="根据API路径直接获取接口的详细信息，支持模糊匹配。",
            tags={"resource", "details", "path", "api"},
        )
        def path_detail(
            path: Annotated[
                str,
                Field(description="API路径，用于查找接口详细信息，如'/db/sql'或'GET /db/db/sql'")
            ],
            fuzzy: Annotated[
                bool,
                Field(description="是否启用模糊匹配，true时支持部分路径匹配，false时要求精确匹配")
            ] = True
        ) -> Dict[str, Any]:
            id_result = path_to_id_impl(context.http_client, path, fuzzy)
            if "error" in id_result:
                return id_result

            details = []
            for node in id_result.get("matches", []):
                file_id = node.get("id")
                if not file_id:
                    details.append({"meta": node, "error": {"code": "missing_id", "message": "节点缺少 ID"}})
                    continue
                ok_detail, detail_payload = context.http_client.api_detail(file_id)
                if ok_detail:
                    details.append({"meta": node, "detail": detail_payload})
                else:
                    details.append({"meta": node, "error": detail_payload})

            return {"path": path, "fuzzy": fuzzy, "results": details}

        @mcp_app.tool(
            name="get_api_details_by_id",
            description="根据接口ID获取完整的接口详细信息和配置。",
            tags={"resource", "details", "id", "api"},
        )
        def api_detail(
            file_id: Annotated[
                str,
                Field(description="API接口的文件ID，用于获取接口的详细信息")
            ]
        ) -> Dict[str, Any]:
            ok, payload = context.http_client.api_detail(file_id)
            if not ok:
                return error_response(payload.get("code"), payload.get("message", "无法获取接口详情"), payload.get("detail"))
            if payload is None:
                return error_response("no_data", f"接口 {file_id} 的详情数据为空")
            return {
                "id": file_id,
                "name": payload.get("name"),
                "path": payload.get("path"),
                "method": payload.get("method"),
                "groupId": payload.get("groupId"),
                "script": payload.get("script"),
                "options": payload.get("options"),
                "description": payload.get("comment"),
                "updatedAt": payload.get("updateTime"),
                "createdAt": payload.get("createTime"),
                "meta_raw": payload,
            }

        @mcp_app.tool(
            name="find_api_ids_by_path",
            description="根据API路径查找对应的ID列表，支持路径匹配和模糊搜索。",
            tags={"resource", "lookup", "path", "id", "batch"},
        )
        def find_api_ids_by_path(
            path: Annotated[
                str,
                Field(description="API路径，用于查找对应的ID列表，如'/db/sql'或'GET /db/db/sql'")
            ],
            limit: Annotated[
                int,
                Field(description="返回结果的最大数量，默认10条")
            ] = 10,
        ) -> Dict[str, Any]:
            return find_api_ids_by_path_impl(context.http_client, path, limit)

        @mcp_app.tool(
            name="find_api_details_by_path",
            description="根据API路径查找对应的详细信息列表，支持模糊匹配。",
            tags={"resource", "lookup", "path", "details", "batch"},
        )
        def find_api_details_by_path(
            path: Annotated[
                str,
                Field(description="API路径，用于查找接口详细信息，如'/db/sql'或'GET /db/db/sql'")
            ],
            fuzzy: Annotated[
                bool,
                Field(description="是否启用模糊匹配，true时支持部分路径匹配，false时要求精确匹配")
            ] = True,
            limit: Annotated[
                int,
                Field(description="返回结果的最大数量，默认10条")
            ] = 10,
        ) -> Dict[str, Any]:
            return find_api_details_by_path_impl(context.http_client, path, fuzzy, limit)

        @mcp_app.tool(
            name="search_api_endpoints",
            description="搜索和过滤 Magic-API 接口端点，支持按方法、路径、名称等条件过滤。",
            tags={"search", "filter", "api", "endpoints"},
        )
        def search_endpoints(
            method_filter: Annotated[
                Optional[str],
                Field(description="按 HTTP 方法过滤，如 'GET'、'POST'、'PUT'、'DELETE'")
            ] = None,
            path_filter: Annotated[
                Optional[str],
                Field(description="按路径正则表达式过滤，如 '^/api/users' 或 'user'")
            ] = None,
            name_filter: Annotated[
                Optional[str],
                Field(description="按名称正则表达式过滤，如 '用户' 或 '.*管理.*'")
            ] = None,
            query_filter: Annotated[
                Optional[str],
                Field(description="路径/名称模糊匹配，支持正则表达式")
            ] = None,
        ) -> Dict[str, Any]:
            try:
                tree = load_resource_tree(client=context.http_client)
                endpoints = extract_api_endpoints(tree)
                filtered_endpoints = filter_endpoints(
                    endpoints,
                    method_filter=method_filter,
                    path_filter=path_filter,
                    name_filter=name_filter,
                    query_filter=query_filter,
                )

                results = []
                for endpoint in filtered_endpoints:
                    if "[" in endpoint and "]" in endpoint:
                        method_path, name = endpoint.split(" [", 1)
                        name = name.rstrip("]")
                    else:
                        method_path, name = endpoint, ""
                    method, path_value = method_path.split(" ", 1)
                    results.append(
                        {
                            "method": method,
                            "path": path_value,
                            "name": name,
                            "display": endpoint,
                        }
                    )

                return {
                    "total_count": len(endpoints),
                    "filtered_count": len(filtered_endpoints),
                    "filters": {
                        "method": method_filter,
                        "path": path_filter,
                        "name": name_filter,
                        "query": query_filter,
                    },
                    "endpoints": results,
                }
            except Exception as exc:  # pragma: no cover - 容错分支
                return error_response("search_error", f"搜索API端点失败: {exc}", str(exc))

