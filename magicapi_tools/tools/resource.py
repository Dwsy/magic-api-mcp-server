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
- save_group: 保存资源分组，支持创建和更新
- create_api_resource: 创建新的API资源
- copy_resource: 复制现有资源
- move_resource: 移动资源到其他分组
- delete_resource: 删除资源（支持软删除）
- read_set_lock_status: 读取或设置资源的锁定状态（支持读取、锁定、解锁）
- list_resource_groups: 列出所有资源分组
- export_resource_tree: 导出完整的资源树结构
- get_resource_stats: 获取资源统计信息
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import re

from pydantic import Field

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils.extractor import (
    MagicAPIExtractorError,
    filter_endpoints,
    _filter_nodes,
    _flatten_tree,
    _nodes_to_csv,
)
from magicapi_tools.utils.resource_manager import build_api_save_kwargs_from_detail
from magicapi_tools.utils import (
    error_response,
    clean_string_param,
    parse_json_param,
    create_operation_error,
    handle_tool_exception,
    log_api_call_details,
    log_operation_start,
    log_operation_end,
    validate_required_params,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext

# 获取资源管理工具的logger
logger = get_logger('tools.resource')


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
                str,
                Field(
                    description="资源类型过滤器：api（API接口）、function（函数）、task（任务）、datasource（数据源）或all（全部）")
            ] = "api",
            format: Annotated[
                str,
                Field(description="输出格式：json（扁平化JSON数组）、csv（CSV格式）、tree（树形JSON结构）")
            ] = "tree",

            depth: Annotated[
                Optional[Union[int, str]],
                Field(description="限制显示的资源树深度，正整数")
            ] = None,
            group_id: Annotated[
                Optional[Union[str, int]],
                Field(description="分组ID，用于只获取指定分组下的子树，默认为'0'表示根节点")
            ] = "0",
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
                # 参数清理：将空字符串转换为 None
                if isinstance(depth, str) and depth.strip() == "":
                    depth = None
                elif isinstance(depth, str):
                    try:
                        depth = int(depth)
                        # 确保 depth 在有效范围内
                        if depth < 1 or depth > 10:
                            depth = None
                    except ValueError:
                        depth = None

                # 清理字符串过滤器参数
                if isinstance(method_filter, str) and method_filter.strip() == "":
                    method_filter = None
                if isinstance(path_filter, str) and path_filter.strip() == "":
                    path_filter = None
                if isinstance(name_filter, str) and name_filter.strip() == "":
                    name_filter = None
                if isinstance(query_filter, str) and query_filter.strip() == "":
                    query_filter = None

                # 处理 group_id 参数
                group_id_str = None
                if group_id is not None:
                    if isinstance(group_id, str) and group_id.strip() == "":
                        group_id_str = None
                    elif isinstance(group_id, str):
                        group_id_str = group_id.strip()
                    elif isinstance(group_id, int):
                        group_id_str = str(group_id)
                    else:
                        group_id_str = None

                # 获取资源树数据
                ok, payload = context.http_client.resource_tree()
                if not ok:
                    return error_response(payload.get("code"), payload.get("message", "无法获取资源树"), payload.get("detail"))

                # 过滤资源类型
                kind_normalized = kind if kind in {
                    "api", "function", "task", "datasource", "all"} else "api"
                allowed = [
                    kind_normalized] if kind_normalized != "all" else ["all"]

                # 根据format参数返回不同格式
                if format == "tree":
                    # 返回树形结构

                    def find_group_subtree(node: Dict[str, Any], target_group_id: str) -> Dict[str, Any]:
                        """递归查找指定分组ID的子树"""
                        if not node:
                            return None

                        # 检查当前节点是否匹配分组ID
                        if "node" in node:
                            node_info = node["node"]
                            current_id = node_info.get("id")
                            if current_id == target_group_id:
                                return node

                        # 递归查找子节点
                        if "children" in node:
                            for child in node["children"]:
                                result = find_group_subtree(child, target_group_id)
                                if result:
                                    return result

                        return None

                    def filter_tree_node(node: Dict[str, Any]) -> Dict[str, Any]:
                        """过滤树节点"""
                        node_copy = dict(node)

                        # 过滤node信息
                        if "node" in node_copy:
                            node_info = node_copy["node"]
                            node_type = node_info.get("type")
                            method = node_info.get("method")
                            node_name = node_info.get("name")

                            # 应用分组识别逻辑：如果有子节点，则设置为分组类型
                            has_children = "children" in node_copy and node_copy["children"]
                            if has_children and node_type:
                                # 确保分组类型以 "-group" 结尾
                                if not node_type.endswith("-group"):
                                    node_info["type"] = f"{node_type}-group"

                            # 检查是否应该包含此节点
                            should_include = True

                            # 类型过滤
                            if allowed != ["all"]:
                                if node_type and node_type not in allowed:
                                    should_include = False
                                elif method and "api" in allowed:
                                    should_include = True
                                elif not node_type and not method:
                                    # 根节点或其他无类型节点：如果是根节点（name='root'）或者有子节点，则保留
                                    if node_name == "root" or ("children" in node_copy and node_copy["children"]):
                                        should_include = True
                                    else:
                                        should_include = False

                            # 高级过滤器：name_filter, path_filter, method_filter, query_filter
                            if should_include and (name_filter or path_filter or method_filter or query_filter):
                                node_path = node_info.get("path", "")
                                node_method = node_info.get("method", "")

                                # name_filter：名称过滤
                                if name_filter and node_name:
                                    if name_filter.lower() not in node_name.lower():
                                        should_include = False

                                # path_filter：路径过滤
                                if should_include and path_filter and node_path:
                                    if path_filter.lower() not in node_path.lower():
                                        should_include = False

                                # method_filter：方法过滤
                                if should_include and method_filter and node_method:
                                    if method_filter.upper() != node_method.upper():
                                        should_include = False

                                # query_filter：通用查询过滤
                                if should_include and query_filter:
                                    # 检查是否在任何相关字段中包含查询关键词
                                    searchable_text = f"{node_name} {node_path} {node_method} {node_type or ''}".strip().lower()
                                    query_lower = query_filter.lower()
                                    if query_lower not in searchable_text:
                                        should_include = False

                            if not should_include:
                                return None

                            # 应用深度限制
                            if depth is not None and "children" in node_copy:
                                def limit_depth(children: List[Dict], current_depth: int):
                                    if current_depth >= depth:
                                        # 移除子节点
                                        for child in children:
                                            if "children" in child:
                                                child["children"] = []
                                    else:
                                        for child in children:
                                            if "children" in child:
                                                limit_depth(
                                                    child["children"], current_depth + 1)

                                limit_depth(node_copy["children"], 0)

                        # 递归过滤子节点
                        if "children" in node_copy:
                            filtered_children = []
                            for child in node_copy["children"]:
                                filtered_child = filter_tree_node(child)
                                if filtered_child is not None:
                                    filtered_children.append(filtered_child)
                            node_copy["children"] = filtered_children

                        return node_copy

                    # 获取指定类型的树
                    tree_data = payload.get(kind_normalized, {})
                    if kind_normalized != "all":
                        # 如果指定了分组ID，先找到对应的子树
                        if group_id_str and group_id_str != "0":
                            tree_data = find_group_subtree(tree_data, group_id_str) or {"node": {}, "children": []}

                        filtered_tree = filter_tree_node(tree_data)
                        result_tree = filtered_tree if filtered_tree else {
                            "node": {}, "children": []}
                    else:
                        # 对于"all"，需要处理所有类型的树
                        result_tree = {}
                        for tree_type in ["api", "function", "task", "datasource"]:
                            if tree_type in payload:
                                type_tree_data = payload[tree_type]
                                # 如果指定了分组ID，先找到对应的子树
                                if group_id_str and group_id_str != "0":
                                    type_tree_data = find_group_subtree(type_tree_data, group_id_str) or {"node": {}, "children": []}

                                filtered = filter_tree_node(type_tree_data)
                                if filtered:
                                    result_tree[tree_type] = filtered

                    return {
                        "format": "tree",
                        "kind": kind_normalized,
                        "group_id": group_id_str,
                        "tree": result_tree,
                        "filters_applied": {
                            "method": method_filter,
                            "path": path_filter,
                            "name": name_filter,
                            "query": query_filter,
                            "depth": depth,
                            "group_id": group_id_str,
                        }
                    }

                else:
                    # json 或 csv 格式：使用扁平化结构
                    # 如果指定了分组ID，先过滤树结构
                    filtered_payload = payload.copy()
                    if group_id_str and group_id_str != "0":
                        for tree_type in ["api", "function", "task", "datasource"]:
                            if tree_type in filtered_payload:
                                subtree = find_group_subtree(filtered_payload[tree_type], group_id_str)
                                filtered_payload[tree_type] = subtree if subtree else {"node": {}, "children": []}

                    nodes = _flatten_tree(filtered_payload, allowed, depth)

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
                            query_filter=query_filter,
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
                        nodes = _filter_nodes(nodes, query_filter)

                    if format == "json":
                        # 返回扁平化的JSON数组
                        return {
                            "format": "json",
                            "kind": kind_normalized,
                            "group_id": group_id_str,
                            "count": len(nodes),
                            "nodes": nodes,
                            "filters_applied": {
                                "method": method_filter,
                                "path": path_filter,
                                "name": name_filter,
                                "query": query_filter,
                                "depth": depth,
                                "group_id": group_id_str,
                            }
                        }
                    elif format == "csv":
                        # 返回CSV格式
                        return {
                            "format": "csv",
                            "kind": kind_normalized,
                            "group_id": group_id_str,
                            "count": len(nodes),
                            "csv": _nodes_to_csv(nodes),
                            "filters_applied": {
                                "method": method_filter,
                                "path": path_filter,
                                "name": name_filter,
                                "query": query_filter,
                                "depth": depth,
                                "group_id": group_id_str,
                            }
                        }

            except MagicAPIExtractorError as e:
                return error_response("extraction_error", f"资源树提取失败: {str(e)}")
            except Exception as e:
                return error_response("unexpected_error", f"意外错误: {str(e)}")

        @mcp_app.tool(
            name="save_group",
            description="保存资源分组，支持单个分组创建或更新，包含完整的分组配置选项。",
            tags={"resource", "group", "save", "create",
                  "update", "management", "full-config"},
            meta={"version": "2.1", "category": "resource-management"}
        )
        def save_group(
            # 创建操作必需参数
            name: Annotated[
                Optional[str],
                Field(description="分组名称（创建新分组时必需）")
            ],
            parent_id: Annotated[
                str,
                Field(description="父分组ID (必须提供)")
            ],
            # 更新操作必需参数
            id: Annotated[
                Optional[str],
                Field(description="分组ID（更新现有分组时必需），用于标识要更新的分组")
            ] = None,
            # 通用参数
            type: Annotated[
                str,
                Field(
                    description="分组类型：api（API接口组）、function（函数组）、task（任务组）、datasource（数据源组）")
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
                Field(description="批量分组数据，JSON数组格式，每个对象包含name,id等字段（批量操作时使用）")
            ] = None,
        ) -> Dict[str, Any]:
            """保存分组（支持单个创建/更新和批量操作）。

            - 创建操作：需要提供 name 等必需参数，不提供 id
            - 更新操作：只需要提供 id，其他参数都是可选的，只更新提供的参数
            """
            if id == "null" or id == "":
                id = None

            import json

            is_update = id is not None

            if is_update:
                # 更新操作：只必需id，其他参数都是可选的
                if not id:
                    return error_response("invalid_params", "更新操作需要提供id")
            else:
                # 创建操作：必需name
                if not name:
                    return error_response("invalid_params", "创建操作需要提供name")

            groups_list = None
            if groups_data:
                try:
                    groups_list = json.loads(groups_data)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"groups_data 格式错误: {groups_data}")

            result = context.resource_tools.save_group_tool(
                name=name,
                id=id,
                parent_id=parent_id,
                type=type,
                path=path,
                options=options,
                groups_data=groups_list,
            )
            if "success" in result:
                return result
            else:
                error_info = result.get("error", {})
                return error_response(
                    error_info.get("code", "save_group_failed"),
                    error_info.get("message", "保存分组失败"),
                    result  # 包含完整的原始错误信息
                )

        @mcp_app.tool(
            name="save_api_endpoint",
            description="保存API接口，支持单个接口创建或更新，包含完整的API配置选项。",
            tags={"api", "endpoint", "save", "create",
                  "update", "management", "full-config"},
            meta={"version": "2.2", "category": "resource-management"}
        )
        def save_api_endpoint(
            # 创建操作必需参数
            group_id: Annotated[
                Optional[str],
                Field(description="分组ID（创建新API时必需），指定API所属的分组")
            ],
            name: Annotated[
                Optional[str],
                Field(description="API接口名称（创建新API时必需）")
            ],
            method: Annotated[
                Optional[str],
                Field(description="HTTP请求方法（创建新API时必需），默认为GET")
            ],
            path: Annotated[
                Optional[str],
                Field(description="API路径，如'/api/users'（创建新API时必需）")
            ],
            script: Annotated[
                Optional[str],
                Field(description="API执行脚本，Magic-Script代码（创建新API时必需）")
            ],
            # 更新操作必需参数
            id: Annotated[
                Optional[str],
                Field(description="文件ID（更新现有API时必需），用于标识要更新的API接口")
            ] = None,
            # 扩展参数（创建和更新都可选）
            description: Annotated[
                Optional[str],
                Field(description="API接口描述")
            ] = None,
            parameters: Annotated[
                Optional[str],
                Field(description="查询参数列表，JSON数组格式，每个参数包含name,type,value等字段")
            ] = None,
            headers: Annotated[
                Optional[str],
                Field(description="请求头列表，JSON数组格式，每个请求头包含name,value等字段")
            ] = None,
            paths: Annotated[
                Optional[str],
                Field(description="路径变量列表，JSON数组格式，每个路径变量包含name,value等字段")
            ] = None,
            request_body: Annotated[
                Optional[str],
                Field(description="请求体示例内容")
            ] = None,
            request_body_definition: Annotated[
                Optional[str],
                Field(description="请求体结构定义，JSON格式")
            ] = None,
            response_body: Annotated[
                Optional[str],
                Field(description="响应体示例内容")
            ] = None,
            response_body_definition: Annotated[
                Optional[str],
                Field(description="响应体结构定义，JSON格式")
            ] = None,
            options: Annotated[
                Optional[str],
                Field(description="接口选项配置，JSON数组格式，每个选项包含name,value等字段")
            ] = None,
        ) -> Dict[str, Any]:
            """保存API接口（支持单个创建或更新操作）。

            - 创建操作：需要提供 group_id, name, method, path, script 等必需参数
            - 更新操作：只需要提供 id，其他参数都是可选的，只更新提供的参数
            """
            # 重构：使用服务层处理业务逻辑
            from magicapi_tools.domain.dtos.resource_dtos import ApiCreationRequest

            request = ApiCreationRequest(
                group_id=group_id,
                name=name,
                method=method,
                path=path,
                script=script,
                id=id,
                description=description,
                parameters=parameters,
                headers=headers,
                paths=paths,
                request_body=request_body,
                request_body_definition=request_body_definition,
                response_body=response_body,
                response_body_definition=response_body_definition,
                options=options,
            )

            response = context.resource_service.create_api(request)
            return response.to_dict()

        @mcp_app.tool(
            name="copy_resource",
            description="复制资源到指定的目标位置。",
            tags={"resource", "copy", "management"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def copy_resource(src_id: str, target_id: str) -> Dict[str, Any]:
            """复制资源到指定位置。"""
            response = context.resource_service.copy_resource(src_id, target_id)
            return response.to_dict()

        @mcp_app.tool(
            name="move_resource",
            description="移动资源到指定的目标位置。",
            tags={"resource", "move", "management"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def move_resource(src_id: str, target_id: str) -> Dict[str, Any]:
            """移动资源到指定位置。"""
            response = context.resource_service.move_resource(src_id, target_id)
            return response.to_dict()

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
                Field(
                    description="资源ID列表，JSON数组格式如['id1','id2','id3']（批量删除操作时使用）")
            ] = None,
        ) -> Dict[str, Any]:
            """删除资源（支持单个和批量操作）。"""
            # 解析resource_ids参数（如果是JSON字符串）
            parsed_resource_ids = None
            if resource_ids:
                try:
                    import json
                    parsed_resource_ids = json.loads(resource_ids)
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失败，当作单个ID处理
                    parsed_resource_ids = [resource_ids]

            response = context.resource_service.delete_resource(resource_id=resource_id, resource_ids=parsed_resource_ids)
            return response.to_dict()

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
                error_info = result["error"]
                return error_response(
                    error_info.get("code", "list_groups_failed"),
                    error_info.get("message", "获取分组列表失败"),
                    result  # 包含完整的原始错误信息
                )

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
            meta={"version": "1.0", "category": "resource-management"},
            enabled=False
        )
        def export_resource_tree(kind: str = "api", format: str = "json") -> Dict[str, Any]:
            """导出资源树。"""
            try:
                result = context.resource_tools.export_resource_tree_tool(
                    kind=kind, format=format)
                if "success" in result:
                    return result
                else:
                    error_info = result.get("error", {})
                    return error_response(
                        error_info.get("code", "export_failed"),
                        error_info.get("message", "导出资源树失败"),
                        result  # 包含完整的原始错误信息
                    )
            except Exception as e:
                print(f"DEBUG MCP: export_resource_tree error: {e}")
                import traceback
                traceback.print_exc()
                return error_response("unexpected_error", f"意外错误: {str(e)}")

        @mcp_app.tool(
            name="read_set_lock_status",
            description="读取或设置资源的锁定状态，支持读取当前锁定状态、锁定和解锁操作。",
            tags={"resource", "lock", "unlock", "status", "management"},
            meta={"version": "2.0", "category": "resource-management"}
        )
        def read_set_lock_status(
            resource_id: Annotated[
                str,
                Field(description="资源ID，用于标识要操作的资源")
            ],
            action: Annotated[
                str,
                Field(description="操作类型：read（读取锁定状态）、lock（锁定资源）、unlock（解锁资源）")
            ],
        ) -> Dict[str, Any]:
            """读取或设置资源的锁定状态。"""
            response = context.resource_service.read_set_lock_status(resource_id, action)
            return response.to_dict()

        @mcp_app.tool(
            name="get_resource_statistics",
            description="获取资源统计信息，包括各类资源数量和分布。",
            tags={"resource", "statistics", "analytics"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def get_resource_stats() -> Dict[str, Any]:
            """获取资源统计信息。"""

            result = context.resource_tools.get_resource_stats_tool()
            if "success" in result:
                return result
            else:
                error_info = result.get("error", {})
                return error_response(
                    error_info.get("code", "stats_failed"),
                    error_info.get("message", "获取资源统计信息失败"),
                    result  # 包含完整的原始错误信息
                )

        @mcp_app.tool(
            name="replace_api_script",
            description="按ID替换指定 Magic-Script 片段并保存接口，支持一次或全局替换。",
            tags={"api", "update", "script", "replace"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def replace_api_script(
            id: Annotated[
                str,
                Field(description="API 文件ID")
            ],
            search: Annotated[
                str,
                Field(description="待查找的脚本内容片段，大小写不敏感")
            ],
            replacement: Annotated[
                str,
                Field(description="用于替换的脚本内容片段")
            ],
            mode: Annotated[
                str,
                Field(description="替换模式：once为替换首次匹配；all为替换所有匹配项")
            ] = "once",
        ) -> Dict[str, Any]:
            """替换 Magic-API 接口脚本中的指定内容并保存。"""

            try:
                clean_id = str(id).strip()
                if not clean_id:
                    return error_response("invalid_params", "id 不能为空")

                if not search:
                    return error_response("invalid_params", "search 不能为空")

                # 获取接口详情
                ok_detail, payload = context.http_client.api_detail(clean_id)
                if not ok_detail or not payload:
                    detail_error = payload if isinstance(payload, dict) else {}
                    print(
                        f"❌ 获取API详情失败: {detail_error.get('message', '无法获取接口详情')}")
                    print(f"   API ID: {clean_id}")
                    print(f"   操作: 脚本替换")
                    print(f"   HTTP状态: {ok_detail}")
                    print(f"   响应数据: {payload}")
                    print(f"   原始错误: {detail_error}")

                    return error_response(
                        detail_error.get("code", "detail_error"),
                        detail_error.get("message", "无法获取接口详情"),
                        detail_error.get("detail"),
                    )

                script_content = payload.get("script", "")
                if script_content is None:
                    return error_response("invalid_state", "接口脚本为空，无法执行替换")

                # 执行替换
                count = 1 if mode == "once" else 0
                replaced_script, replaced_times = re.subn(
                    pattern=re.escape(search),
                    repl=replacement,
                    string=script_content,
                    count=count,
                    flags=re.IGNORECASE,
                )

                if replaced_times == 0:
                    return error_response("not_found", "未在脚本中找到匹配内容，未执行替换")

                # 构建保存参数
                try:
                    save_kwargs = build_api_save_kwargs_from_detail(payload)
                except ValueError as exc:
                    return error_response("invalid_detail", f"接口详情数据格式异常: {exc}")

                save_kwargs["script"] = replaced_script

                result = context.resource_tools.create_api_tool(**save_kwargs)
                if "success" not in result:
                    error_info = result.get("error", {})
                    return error_response(
                        error_info.get("code", "save_failed"),
                        error_info.get("message", "保存接口失败"),
                        result  # 包含完整的原始错误信息
                    )

                return {
                    "success": True,
                    "id": result.get("id", result.get("file_id", clean_id)),
                    "file_id": result.get("id", result.get("file_id", clean_id)),
                    "replaced_times": replaced_times,
                    "mode": mode,
                }

            except Exception as exc:
                return error_response("unexpected_error", f"替换脚本时发生异常: {exc}")
