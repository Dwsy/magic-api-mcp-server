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
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

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
from magicapi_tools.utils import error_response

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
                kind_normalized = kind if kind in {
                    "api", "function", "task", "datasource", "all"} else "api"
                allowed = [
                    kind_normalized] if kind_normalized != "all" else ["all"]

                # 根据format参数返回不同格式
                if format == "tree":
                    # 返回树形结构
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
                        filtered_tree = filter_tree_node(tree_data)
                        result_tree = filtered_tree if filtered_tree else {
                            "node": {}, "children": []}
                    else:
                        # 对于"all"，需要处理所有类型的树
                        result_tree = {}
                        for tree_type in ["api", "function", "task", "datasource"]:
                            if tree_type in payload:
                                filtered = filter_tree_node(payload[tree_type])
                                if filtered:
                                    result_tree[tree_type] = filtered

                    return {
                        "format": "tree",
                        "kind": kind_normalized,
                        "tree": result_tree,
                        "filters_applied": {
                            "method": method_filter,
                            "path": path_filter,
                            "name": name_filter,
                            "query": query_filter,
                            "depth": depth,
                        }
                    }

                else:
                    # json 或 csv 格式：使用扁平化结构
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
                            "count": len(nodes),
                            "nodes": nodes,
                            "filters_applied": {
                                "method": method_filter,
                                "path": path_filter,
                                "name": name_filter,
                                "query": query_filter,
                                "depth": depth,
                            }
                        }
                    elif format == "csv":
                        # 返回CSV格式
                        return {
                            "format": "csv",
                            "kind": kind_normalized,
                            "count": len(nodes),
                            "csv": _nodes_to_csv(nodes),
                            "filters_applied": {
                                "method": method_filter,
                                "path": path_filter,
                                "name": name_filter,
                                "query": query_filter,
                                "depth": depth,
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
            if id == "null":
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
            if id == "null":
                id = None

            # MCP工具调用日志
            operation_type = "更新" if id else "创建"
            logger.info(f"MCP工具调用: save_api_endpoint ({operation_type})")
            logger.info(f"  API ID: {id if id else 'N/A'}")
            logger.info(f"  API名称: {name}")
            logger.info(f"  API路径: {path}")
            logger.info(f"  HTTP方法: {method}")
            logger.info(f"  分组ID: {group_id}")
            if description:
                logger.debug(f"  描述: {description[:100]}...")
            if script:
                logger.debug(f"  脚本长度: {len(script)} 字符")

            import json

            is_update = id is not None

            if is_update:
                # 更新操作：只必需id，其他参数都是可选的
                if not id:
                    return error_response("invalid_params", "更新操作需要提供id")
            else:
                # 创建操作：必需group_id, name, method, path, script
                required_fields = {
                    "group_id": group_id,
                    "name": name,
                    "method": method,
                    "path": path,
                    "script": script
                }
                missing_fields = [
                    k for k, v in required_fields.items() if v is None]
                if missing_fields:
                    return error_response("invalid_params", f"创建操作需要提供以下必需参数: {', '.join(missing_fields)}")

                # 对于创建操作，如果没有提供method，默认设置为GET
                if method is None:
                    method = "GET"

            # 解析JSON参数
            parsed_parameters = None
            if parameters:
                try:
                    parsed_parameters = json.loads(parameters)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"parameters 格式错误: {parameters}")

            parsed_headers = None
            if headers:
                try:
                    parsed_headers = json.loads(headers)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"headers 格式错误: {headers}")

            parsed_paths = None
            if paths:
                try:
                    parsed_paths = json.loads(paths)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"paths 格式错误: {paths}")

            parsed_options = None
            if options:
                try:
                    parsed_options = json.loads(options)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"options 格式错误: {options}")

            parsed_request_body_definition = None
            if request_body_definition:
                try:
                    parsed_request_body_definition = json.loads(
                        request_body_definition)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"request_body_definition 格式错误: {request_body_definition}")

            parsed_response_body_definition = None
            if response_body_definition:
                try:
                    parsed_response_body_definition = json.loads(
                        response_body_definition)
                except json.JSONDecodeError:
                    return error_response("invalid_json", f"response_body_definition 格式错误: {response_body_definition}")

            # 调用工具方法
            result = context.resource_tools.create_api_tool(
                group_id=group_id,
                name=name,
                method=method,
                path=path,
                script=script,
                description=description,
                parameters=parsed_parameters,
                headers=parsed_headers,
                paths=parsed_paths,
                request_body=request_body,
                request_body_definition=parsed_request_body_definition,
                response_body=response_body,
                response_body_definition=parsed_response_body_definition,
                options=parsed_options,
                id=id,  # 更新操作时传入id，创建操作时为None
            )

            if "success" not in result:
                # 记录详细的原始错误信息
                error_info = result.get("error", {})
                operation_type = "更新" if id else "创建"
                logger.error(
                    f"{operation_type}API失败: {error_info.get('message', '未知错误')}")
                logger.error(f"  API ID: {id if id else 'N/A'}")
                logger.error(f"  API名称: {name}")
                logger.error(f"  API路径: {path}")
                logger.error(f"  HTTP方法: {method}")
                logger.error(f"  错误代码: {error_info.get('code', 'unknown')}")
                logger.debug(f"  原始错误信息: {result}")

                return error_response(
                    error_info.get("code", "api_save_failed"),
                    error_info.get("message", f"{operation_type}API失败"),
                    result  # 包含完整的原始错误信息
                )

            return result

        @mcp_app.tool(
            name="copy_resource",
            description="复制资源到指定的目标位置。",
            tags={"resource", "copy", "management"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def copy_resource(src_id: str, target_id: str) -> Dict[str, Any]:
            """复制资源到指定位置。"""

            try:
                # 清理参数
                clean_src_id = str(src_id).strip()
                clean_target_id = str(target_id).strip()

                if not clean_src_id or not clean_target_id:
                    return error_response("invalid_params", "src_id和target_id不能为空")

                # 调用工具方法，获取结构化的错误信息
                result = context.resource_tools.copy_resource_tool(
                    clean_src_id, clean_target_id)
                if "success" in result:
                    return result
                else:
                    error_info = result.get("error", {})
                    return error_response(
                        error_info.get("code", "copy_failed"),
                        error_info.get("message", f"复制资源 {clean_src_id} 失败"),
                        result  # 包含完整的原始错误信息
                    )
            except Exception as e:
                return error_response("unexpected_error", f"复制资源时发生异常: {str(e)}")

        @mcp_app.tool(
            name="move_resource",
            description="移动资源到指定的目标位置。",
            tags={"resource", "move", "management"},
            meta={"version": "1.0", "category": "resource-management"}
        )
        def move_resource(src_id: str, target_id: str) -> Dict[str, Any]:
            """移动资源到指定位置。"""

            try:
                # 清理参数
                clean_src_id = str(src_id).strip()
                clean_target_id = str(target_id).strip()

                if not clean_src_id or not clean_target_id:
                    return error_response("invalid_params", "src_id和target_id不能为空")

                # 调用工具方法，获取结构化的错误信息
                result = context.resource_tools.move_resource_tool(
                    clean_src_id, clean_target_id)
                if "success" in result:
                    return result
                else:
                    error_info = result.get("error", {})
                    return error_response(
                        error_info.get("code", "move_failed"),
                        error_info.get("message", f"移动资源 {clean_src_id} 失败"),
                        result  # 包含完整的原始错误信息
                    )
            except Exception as e:
                return error_response("unexpected_error", f"移动资源时发生异常: {str(e)}")

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

            import json

            try:
                # 处理批量删除
                if resource_ids:
                    try:
                        ids_list = json.loads(resource_ids)
                    except json.JSONDecodeError:
                        return error_response("invalid_json", f"resource_ids 格式错误: {resource_ids}")

                    # 调用工具方法进行批量删除
                    result = context.resource_tools.delete_resource_tool(
                        resource_ids=ids_list)
                    if "success" in result:
                        return result
                    else:
                        error_info = result.get("error", {})
                        return error_response(
                            error_info.get("code", "batch_delete_failed"),
                            error_info.get("message", "批量删除资源失败"),
                            result  # 包含完整的原始错误信息
                        )

                # 单个删除
                elif resource_id:
                    # 清理resource_id（去除前后空格）
                    clean_resource_id = str(resource_id).strip()
                    if not clean_resource_id:
                        return error_response("invalid_params", "resource_id不能为空")

                    # 调用工具方法进行单个删除
                    result = context.resource_tools.delete_resource_tool(
                        resource_id=clean_resource_id)
                    if "success" in result:
                        return result
                    else:
                        error_info = result.get("error", {})
                        return error_response(
                            error_info.get("code", "delete_failed"),
                            error_info.get(
                                "message", f"删除资源 {clean_resource_id} 失败"),
                            result  # 包含完整的原始错误信息
                        )

                else:
                    return error_response("invalid_params", "必须提供 resource_id 或 resource_ids 参数")

            except Exception as e:
                return error_response("unexpected_error", f"删除资源时发生异常: {str(e)}")

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

            try:
                # 清理参数
                clean_resource_id = str(resource_id).strip()
                if not clean_resource_id:
                    return error_response("invalid_params", "resource_id不能为空")

                if action == "read":
                    # 读取锁定状态 - 使用 GET /resource/file/{id} 接口
                    ok, payload = context.http_client.api_detail(
                        clean_resource_id)
                    if not ok:
                        return error_response(payload.get("code"), payload.get("message", "无法获取资源信息"), payload.get("detail"))

                    # 从返回的数据中提取锁定状态
                    lock_status = payload.get("lock", "0")  # 默认解锁状态
                    is_locked = lock_status == "1"

                    return {
                        "success": True,
                        "resource_id": clean_resource_id,
                        "action": "read",
                        "is_locked": is_locked,
                        "lock_status": lock_status,
                        "lock_status_description": "已锁定" if is_locked else "未锁定",
                        "resource_info": payload  # 返回完整的资源信息
                    }

                elif action == "lock":
                    # 锁定资源
                    result = context.resource_tools.lock_resource_tool(
                        resource_id=clean_resource_id)
                    if "success" in result:
                        return {
                            "success": True,
                            "resource_id": clean_resource_id,
                            "action": "lock",
                            "message": f"资源 {clean_resource_id} 已成功锁定"
                        }
                    else:
                        error_info = result.get("error", {})
                        return error_response(
                            error_info.get("code", "lock_failed"),
                            error_info.get(
                                "message", f"锁定资源 {clean_resource_id} 失败"),
                            result  # 包含完整的原始错误信息
                        )

                elif action == "unlock":
                    # 解锁资源
                    result = context.resource_tools.unlock_resource_tool(
                        resource_id=clean_resource_id)
                    if "success" in result:
                        return {
                            "success": True,
                            "resource_id": clean_resource_id,
                            "action": "unlock",
                            "message": f"资源 {clean_resource_id} 已成功解锁"
                        }
                    else:
                        error_info = result.get("error", {})
                        return error_response(
                            error_info.get("code", "unlock_failed"),
                            error_info.get(
                                "message", f"解锁资源 {clean_resource_id} 失败"),
                            result  # 包含完整的原始错误信息
                        )

                else:
                    return error_response("invalid_action", f"不支持的操作类型: {action}")

            except Exception as e:
                return error_response("unexpected_error", f"操作资源锁定状态时发生异常: {str(e)}")

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
