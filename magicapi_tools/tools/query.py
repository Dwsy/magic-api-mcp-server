"""Magic-API 查询相关 MCP 工具。

此模块提供高效的资源查询和检索功能，包括：
- 路径到ID的快速转换
- API详细信息查询
- 批量资源查询
- 资源路径查找和匹配

重要提示：
- 调用API时请优先使用 get_api_details_by_id 获取接口的完整信息
- 返回的 full_path 字段包含完整的路径（如 "/db/advance/other/number/convert"），建议在调用时与method结合使用
- call_magic_api 工具支持传入接口ID，会自动转换为完整路径

主要工具：
- get_api_details_by_path: 根据API路径直接获取接口的详细信息，支持模糊匹配
- get_api_details_by_id: 根据接口ID获取详细信息，包含full_path字段（推荐使用）
- search_api_endpoints: 搜索和过滤Magic-API接口端点，返回包含ID的完整信息列表
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

from pydantic import Field

from magicapi_tools.utils.extractor import extract_api_endpoints, load_resource_tree
from magicapi_tools.utils.extractor import filter_endpoints, _clean_path
from magicapi_tools.logging_config import get_logger
from magicapi_tools.tools.common import (
    error_response,
    path_to_id_impl,
)

# 获取查询工具的logger
logger = get_logger('tools.query')

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


def _collect_all_endpoints(node: Dict[str, Any], parent_path: str, results: List[Dict[str, Any]]) -> None:
    """收集所有端点的详细信息（包含ID和display字符串），与 _traverse_api_tree 逻辑完全一致。"""
    node_info = node.get("node", {})
    current_path = node_info.get("path", "")
    method = node_info.get("method")
    api_id = node_info.get("id")
    name = node_info.get("name", "")

    if current_path and parent_path:
        full_path = f"{parent_path}/{current_path}"
    elif current_path:
        full_path = current_path
    else:
        full_path = parent_path

    # 使用与 _traverse_api_tree 相同的路径清理逻辑
    full_path = _clean_path(full_path)

    if method and full_path:
        # 生成与 _traverse_api_tree 完全相同的display字符串
        display = f"{method} {full_path}"
        if name and name != current_path:
            display += f" [{name}]"

        if api_id:
            results.append({
                "id": api_id,
                "path": full_path,
                "method": method,
                "name": name,
                "display": display,
                "groupId": node_info.get("groupId"),
            })

    for child in node.get("children", []) or []:
        _collect_all_endpoints(child, full_path, results)


def _get_full_path_by_api_details(client, api_id: str, method: str, path: str, name: str = "") -> str:
    """根据API详情获取完整的资源树路径，符合DRY原则。

    Args:
        client: HTTP客户端
        api_id: 接口ID
        method: HTTP方法
        path: 接口路径（可能不完整）
        name: 接口名称

    Returns:
        str: 完整的路径，如 "/db/advance/other/number/convert"
    """
    try:
        # 获取所有端点的详细信息
        tree = load_resource_tree(client=client)
        all_endpoint_details = []
        for child in tree.api_nodes:
            _collect_all_endpoints(child, "", all_endpoint_details)

        # 首先尝试通过ID直接匹配
        for detail in all_endpoint_details:
            if detail.get("id") == api_id:
                path_from_tree = detail.get("path", "")
                if path_from_tree:
                    return path_from_tree

        # 如果ID匹配失败，尝试通过method+path+name匹配
        for detail in all_endpoint_details:
            detail_method = detail.get("method", "").upper()
            detail_path = detail.get("path", "")
            detail_name = detail.get("name", "")

            if (detail_method == method.upper() and
                detail_path.endswith(path) and  # path可能是部分路径，检查结尾匹配
                (not name or detail_name == name)):
                return detail_path

        # 如果都没匹配上，返回简单格式
        return path

    except Exception as exc:  # pragma: no cover - 容错分支
        # 如果获取资源树失败，返回简单格式
        return path


class QueryTools:
    """查询工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册查询相关工具。"""


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
            description="根据接口ID获取完整的接口详细信息和配置。返回包含method、path和full_path(完整路径)的详细信息。",
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
                logger.error(f"查询API详情失败: {payload.get('message', '无法获取接口详情')}")
                logger.error(f"  API ID: {file_id}")
                logger.debug(f"  错误详情: {payload}")
                return error_response(payload.get("code"), payload.get("message", "无法获取接口详情"), payload.get("detail"))

            if payload is None:
                logger.warning(f"API详情数据为空: {file_id}")
                logger.debug(f"  原始响应: {payload}")
                return error_response("no_data", f"接口 {file_id} 的详情数据为空")

            # 获取基础信息
            method = payload.get("method", "").upper()
            path = payload.get("path", "")
            name = payload.get("name", "")

            # 使用可复用函数获取完整的资源树路径
            full_path = _get_full_path_by_api_details(context.http_client, file_id, method, path, name)

            return {
                **payload,
                "full_path": full_path  # 完整的路径，包含分组路径，如 "/db/advance/other/number/convert"
            }



        @mcp_app.tool(
            name="search_api_endpoints",
            description="搜索和过滤 Magic-API 接口端点，支持按方法、路径、名称等条件过滤。返回包含ID、方法、路径、名称等完整信息的端点列表。",
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

                # 获取所有端点的详细信息（包含ID和display字符串）
                all_endpoint_details = []
                for child in tree.api_nodes:
                    _collect_all_endpoints(child, "", all_endpoint_details)

                # 创建端点字符串到ID的映射
                endpoint_to_id_map = {}
                for detail in all_endpoint_details:
                    display = detail.get("display")
                    api_id = detail.get("id")
                    if display and api_id:
                        endpoint_to_id_map[display] = api_id

                results = []
                for endpoint in filtered_endpoints:
                    if "[" in endpoint and "]" in endpoint:
                        method_path, name = endpoint.split(" [", 1)
                        name = name.rstrip("]")
                    else:
                        method_path, name = endpoint, ""
                    method, path_value = method_path.split(" ", 1)

                    # 获取对应的ID
                    api_id = endpoint_to_id_map.get(endpoint)

                    results.append(
                        {
                            "method": method,
                            "path": path_value,
                            "name": name,
                            "id": api_id,
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

