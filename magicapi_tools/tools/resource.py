"""Magic-API 资源管理工具模块。

此模块提供完整的Magic-API资源管理系统，包括：
- 资源树浏览和查询
- 资源创建、更新、删除操作
- 分组管理和组织
- 资源导入导出功能
- 资源统计和分析

主要工具：
- get_resource_tree: 获取资源树，支持多种过滤和导出格式
- get_resource_detail: 获取特定资源的详细信息
- create_resource_group: 创建新的资源分组
- create_api_resource: 创建新的API资源
- copy_resource: 复制现有资源
- move_resource: 移动资源到其他分组
- delete_resource: 删除资源（支持软删除）
- lock_resource: 锁定资源防止修改
- unlock_resource: 解锁资源
- list_resource_groups: 列出所有资源分组
- export_resource_tree: 导出完整的资源树结构
- get_resource_stats: 获取资源统计信息
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Annotated, Any, Dict, Literal, Optional

from pydantic import Field

from magicapi_tools.utils.extractor import (
    MagicAPIExtractorError,
    filter_endpoints,
    _filter_nodes,
    _flatten_tree,
    _nodes_to_csv,
)
from magicapi_tools.utils import error_response

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class ResourceManagementTools:
    """资源管理工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:
        """注册资源管理相关工具。"""

        @mcp_app.tool(
            name="get_resource_tree",
            description="获取 Magic-API 资源树，支持多种过滤和导出格式。",
            tags={"resource", "tree", "api", "filtering"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def resource_tree(
            kind: Annotated[
                Literal["api", "function", "task", "datasource", "all"],
                Field(description="资源类型过滤器：api（API接口）、function（函数）、task（任务）、datasource（数据源）或all（全部）")
            ] = "api",
            search: Annotated[
                Optional[str],
                Field(description="简单搜索关键词，支持部分匹配（兼容性保留参数）")
            ] = None,
            csv: Annotated[
                bool,
                Field(description="是否以CSV格式输出资源信息")
            ] = False,
            depth: Annotated[
                Optional[int],
                Field(description="限制显示的资源树深度，正整数", ge=1, le=10)
            ] = None,
            method_filter: Annotated[
                Optional[str],
                Field(description="HTTP方法过滤器，如'GET'、'POST'、'PUT'、'DELETE'")
            ] = None,
            path_filter: Annotated[
                Optional[str],
                Field(description="路径正则表达式过滤器，用于匹配API路径")
            ] = None,
            name_filter: Annotated[
                Optional[str],
                Field(description="名称正则表达式过滤器，用于匹配资源名称")
            ] = None,
            query_filter: Annotated[
                Optional[str],
                Field(description="通用查询过滤器，支持复杂的搜索条件")
            ] = None,
        ) -> Dict[str, Any]:
            """获取 Magic-API 资源树。"""

            try:
                # 获取资源树数据
                ok, payload = context.http_client.resource_tree()
                if not ok:
                    return error_response(payload.get("code"), payload.get("message", "无法获取资源树"), payload.get("detail"))

                # 过滤资源类型
                kind_normalized = kind if kind in {"api", "function", "task", "datasource", "all"} else "api"
                allowed = [kind_normalized] if kind_normalized != "all" else ["all"]

                # 使用原有的树形结构处理方式，但增强过滤功能
                nodes = _flatten_tree(payload, allowed, depth)

                # 如果有高级过滤器，转换为端点列表进行过滤
                if method_filter or path_filter or name_filter or query_filter:
                    # 转换为端点字符串格式进行过滤
                    endpoints = []
                    for node in nodes:
                        method = node.get("method", "")
                        path = node.get("path", "")
                        name = node.get("name", "")
                        if method and path:
                            endpoint_str = f"{method} {path}"
                            if name:
                                endpoint_str += f" [{name}]"
                            endpoints.append(endpoint_str)

                    # 应用高级过滤器
                    filtered_endpoints = filter_endpoints(
                        endpoints,
                        path_filter=path_filter,
                        name_filter=name_filter,
                        method_filter=method_filter,
                        query_filter=query_filter or search,
                    )

                    # 转换回节点格式
                    filtered_nodes = []
                    for endpoint in filtered_endpoints:
                        if "[" in endpoint and "]" in endpoint:
                            method_path, name = endpoint.split(" [", 1)
                            name = name.rstrip("]")
                        else:
                            method_path, name = endpoint, ""

                        method, path = method_path.split(" ", 1)

                        # 从原始节点中找到匹配的节点（保留ID等信息）
                        for original_node in nodes:
                            if (original_node.get("method") == method and
                                original_node.get("path") == path and
                                original_node.get("name") == name):
                                filtered_nodes.append(original_node)
                                break

                    nodes = filtered_nodes
                else:
                    # 使用原有搜索逻辑保持兼容性
                    nodes = _filter_nodes(nodes, search)

                result: Dict[str, Any] = {
                    "kind": kind_normalized,
                    "count": len(nodes),
                    "nodes": nodes,
                    "filters_applied": {
                        "method": method_filter,
                        "path": path_filter,
                        "name": name_filter,
                        "query": query_filter or search,
                        "depth": depth,
                    }
                }

                if csv:
                    result["csv"] = _nodes_to_csv(nodes)

                return result

            except MagicAPIExtractorError as e:
                return error_response("extraction_error", f"资源树提取失败: {str(e)}")
            except Exception as e:
                return error_response("unexpected_error", f"意外错误: {str(e)}")

        @mcp_app.tool(
            name="create_resource_group",
            description="创建资源分组，支持单个分组创建或批量分组创建。",
            tags={"resource", "group", "create", "management"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def create_group(
            name: Annotated[
                Optional[str],
                Field(description="分组名称（单个分组创建时必需）")
            ] = None,
            parent_id: Annotated[
                str,
                Field(description="父分组ID，根分组使用'0'")
            ] = "0",
            group_type: Annotated[
                Literal["api", "function", "task", "datasource"],
                Field(description="分组类型：api（API接口组）、function（函数组）、task（任务组）、datasource（数据源组）")
            ] = "api",
            path: Annotated[
                Optional[str],
                Field(description="分组路径，可选的URL路径前缀")
            ] = None,
            options: Annotated[
                Optional[str],
                Field(description="分组选项配置，JSON格式字符串")
            ] = None,
            groups_data: Annotated[
                Optional[str],
                Field(description="批量分组数据，JSON数组格式，每个对象包含name等字段（批量操作时使用）")
            ] = None,
        ) -> Dict[str, Any]:
            """创建分组（支持单个和批量操作）。"""

            groups_list = None
            if groups_data:
                import json
                try:
                    groups_list = json.loads(groups_data)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"groups_data 格式错误: {groups_data}")

            result = context.resource_tools.create_group_tool(
                name=name,
                parent_id=parent_id,
                group_type=group_type,
                path=path,
                options=options,
                groups_data=groups_list,
            )
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="create_api_endpoint",
            description="创建API接口，支持单个接口创建或批量接口创建。",
            tags={"api", "endpoint", "create", "management"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def create_api(
            group_id: Annotated[
                Optional[str],
                Field(description="分组ID（单个API创建时必需），指定API所属的分组")
            ] = None,
            name: Annotated[
                Optional[str],
                Field(description="API接口名称（单个API创建时必需）")
            ] = None,
            method: Annotated[
                Optional[Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]],
                Field(description="HTTP请求方法（单个API创建时必需）")
            ] = None,
            path: Annotated[
                Optional[str],
                Field(description="API路径，如'/api/users'（单个API创建时必需）")
            ] = None,
            script: Annotated[
                Optional[str],
                Field(description="API执行脚本，Magic-Script代码（单个API创建时必需）")
            ] = None,
            apis_data: Annotated[
                Optional[str],
                Field(description="批量API数据，JSON数组格式，每个对象包含group_id,name,method,path,script字段（批量操作时使用）")
            ] = None,
        ) -> Dict[str, Any]:
            """创建API接口（支持单个和批量操作）。"""

            apis_list = None
            if apis_data:
                import json
                try:
                    apis_list = json.loads(apis_data)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"apis_data 格式错误: {apis_data}")

            result = context.resource_tools.create_api_tool(
                group_id=group_id,
                name=name,
                method=method,
                path=path,
                script=script,
                apis_data=apis_list,
            )
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="copy_resource",
            description="复制资源到指定的目标位置。",
            tags={"resource", "copy", "management"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def copy_resource(src_id: str, target_id: str) -> Dict[str, Any]:
            """复制资源到指定位置。"""

            result = context.resource_tools.copy_resource_tool(src_id, target_id)
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="move_resource",
            description="移动资源到指定的目标位置。",
            tags={"resource", "move", "management"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def move_resource(src_id: str, target_id: str) -> Dict[str, Any]:
            """移动资源到指定位置。"""

            result = context.resource_tools.move_resource_tool(src_id, target_id)
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="delete_resource",
            description="删除资源，支持单个资源删除或批量资源删除。",
            tags={"resource", "delete", "management"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def delete_resource(
            resource_id: Annotated[
                Optional[str],
                Field(description="单个资源ID（单个删除操作时使用）")
            ] = None,
            resource_ids: Annotated[
                Optional[str],
                Field(description="资源ID列表，JSON数组格式如['id1','id2','id3']（批量删除操作时使用）")
            ] = None,
        ) -> Dict[str, Any]:
            """删除资源（支持单个和批量操作）。"""

            ids_list = None
            if resource_ids:
                import json
                try:
                    ids_list = json.loads(resource_ids)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"resource_ids 格式错误: {resource_ids}")

            result = context.resource_tools.delete_resource_tool(
                resource_id=resource_id,
                resource_ids=ids_list,
            )
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="lock_resource",
            description="锁定资源，防止其他用户修改，支持单个和批量操作。",
            tags={"resource", "lock", "management"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def lock_resource(
            resource_id: Annotated[
                Optional[str],
                Field(description="单个资源ID（单个锁定操作时使用）")
            ] = None,
            resource_ids: Annotated[
                Optional[str],
                Field(description="资源ID列表，JSON数组格式如['id1','id2','id3']（批量锁定操作时使用）")
            ] = None,
        ) -> Dict[str, Any]:
            """锁定资源（支持单个和批量操作）。"""

            ids_list = None
            if resource_ids:
                import json
                try:
                    ids_list = json.loads(resource_ids)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"resource_ids 格式错误: {resource_ids}")

            result = context.resource_tools.lock_resource_tool(
                resource_id=resource_id,
                resource_ids=ids_list,
            )
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="unlock_resource",
            description="解锁资源，允许其他用户修改，支持单个和批量操作。",
            tags={"resource", "unlock", "management"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def unlock_resource(
            resource_id: Annotated[
                Optional[str],
                Field(description="单个资源ID（单个解锁操作时使用）")
            ] = None,
            resource_ids: Annotated[
                Optional[str],
                Field(description="资源ID列表，JSON数组格式如['id1','id2','id3']（批量解锁操作时使用）")
            ] = None,
        ) -> Dict[str, Any]:
            """解锁资源（支持单个和批量操作）。"""

            ids_list = None
            if resource_ids:
                import json
                try:
                    ids_list = json.loads(resource_ids)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"resource_ids 格式错误: {resource_ids}")

            result = context.resource_tools.unlock_resource_tool(
                resource_id=resource_id,
                resource_ids=ids_list,
            )
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])

        @mcp_app.tool(
            name="list_resource_groups",
            description="列出所有资源分组及其基本信息，支持搜索和数量限制。",
            tags={"resource", "group", "list", "search", "filter"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def list_groups(
            search: Annotated[
                Optional[str],
                Field(description="搜索关键词，支持分组名称、路径、类型的模糊匹配")
            ] = None,
            limit: Annotated[
                int,
                Field(description="返回结果的最大数量，默认50条")
            ] = 50,
        ) -> Dict[str, Any]:
            """列出所有分组，支持搜索和数量限制。"""

            result = context.resource_tools.list_groups_tool()
            if "error" in result:
                return error_response(result["error"]["code"], result["error"]["message"])

            groups = result.get("groups", [])

            # 应用搜索过滤（在Python端完成）
            if search:
                search_lower = search.lower()
                filtered_groups = []
                for group in groups:
                    # 搜索多个字段
                    searchable_fields = [
                        group.get('name', ''),
                        group.get('path', ''),
                        group.get('type', ''),
                        group.get('comment', ''),
                    ]

                    # 检查是否匹配搜索关键词
                    if any(search_lower in str(field).lower() for field in searchable_fields if field):
                        filtered_groups.append(group)

                groups = filtered_groups

            # 应用数量限制
            total_count = len(groups)
            if limit > 0:
                groups = groups[:limit]

            return {
                "total_count": total_count,
                "returned_count": len(groups),
                "limit": limit,
                "search_applied": search,
                "groups": groups,
            }

        @mcp_app.tool(
            name="export_resource_tree",
            description="导出资源树结构，支持JSON和CSV格式。",
            tags={"resource", "export", "tree"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def export_resource_tree(kind: str = "api", format: str = "json") -> Dict[str, Any]:
            """导出资源树。"""
            try:
                result = context.resource_tools.export_resource_tree_tool(kind=kind, format=format)
                return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])
            except Exception as e:
                print(f"DEBUG MCP: export_resource_tree error: {e}")
                import traceback
                traceback.print_exc()
                return error_response("unexpected_error", f"意外错误: {str(e)}")

        @mcp_app.tool(
            name="get_resource_statistics",
            description="获取资源统计信息，包括各类资源数量和分布。",
            tags={"resource", "statistics", "analytics"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def get_resource_stats() -> Dict[str, Any]:
            """获取资源统计信息。"""

            result = context.resource_tools.get_resource_stats_tool()
            return result if "success" in result else error_response(result["error"]["code"], result["error"]["message"])
