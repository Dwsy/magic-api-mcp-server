"""Magic-API 资源管理器核心实现。"""

from __future__ import annotations

import copy
import json
from typing import Any, Dict, List, Optional

import requests

from .http_client import MagicAPIHTTPClient
from magicapi_mcp.settings import MagicAPISettings
from magicapi_tools.logging_config import get_logger

# 获取资源管理器的logger
logger = get_logger('utils.resource_manager')


def build_api_save_kwargs_from_detail(detail: Dict[str, Any]) -> Dict[str, Any]:
    """根据接口详情构建 `create_api_tool` 所需参数映射。

    Args:
        detail: `api_detail` 接口返回的完整数据。

    Returns:
        Dict[str, Any]: 可直接传递给 `create_api_tool` 的关键字参数。
                     包含 'id' 字段用于更新操作。

    Raises:
        ValueError: 当 detail 非字典或缺少必要字段时抛出。
    """

    if not isinstance(detail, dict):
        raise ValueError("detail must be a dict containing api information")

    detail_copy = copy.deepcopy(detail)

    return {
        "group_id": detail_copy.get("groupId"),
        "name": detail_copy.get("name"),
        "method": (detail_copy.get("method") or "").upper() or None,
        "path": detail_copy.get("path"),
        "script": detail_copy.get("script"),
        "description": detail_copy.get("description"),
        "parameters": detail_copy.get("parameters"),
        "headers": detail_copy.get("headers"),
        "paths": detail_copy.get("paths"),
        "request_body": detail_copy.get("requestBody"),
        "request_body_definition": detail_copy.get("requestBodyDefinition"),
        "response_body": detail_copy.get("responseBody"),
        "response_body_definition": detail_copy.get("responseBodyDefinition"),
        "options": detail_copy.get("options"),
        "id": detail_copy.get("id"),
    }


class MagicAPIResourceTools:
    """
    Magic-API 资源管理高层工具接口

    提供高层资源管理操作，封装常用的管理功能
    """

    def __init__(self, manager: MagicAPIResourceManager):
        """
        初始化工具接口

        Args:
            manager: MagicAPIResourceManager 实例
        """
        self.manager = manager

    def save_group_tool(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        parent_id: str = "0",
        type: str = "api",
        path: Optional[str] = None,
        options: Optional[str] = None,
        groups_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        保存分组（支持创建和更新操作）。

        Args:
            name: 分组名称（创建时必需）
            id: 分组ID（更新时必需）
            parent_id: 父分组ID
            type: 分组类型
            path: 分组路径
            options: 选项配置JSON字符串
            groups_data: 分组数据列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        # 判断是批量操作还是单个操作
        if groups_data is not None:
            return self._batch_save_groups(groups_data)
        else:
            return self._save_single_group(name, id, parent_id, type, path, options)

    def _save_single_group(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        parent_id: str = "0",
        type: str = "api",
        path: Optional[str] = None,
        options: Optional[str] = None,
    ) -> Dict[str, Any]:
        """保存单个分组（支持创建和更新）。"""
        options_dict = None
        if options:
            try:
                options_dict = json.loads(options)
            except json.JSONDecodeError:
                return {"error": {"code": "invalid_json", "message": f"options 格式错误: {options}"}}

        group_id = self.manager.save_group(
            name=name,
            id=id,
            parent_id=parent_id,
            type=type,
            path=path,
            options=options_dict,
        )
        if group_id:
            operation = "更新" if id else "创建"
            return {"success": True, "group_id": group_id, "name": name, "operation": operation}
        operation = "更新" if id else "创建"
        return {"error": {"code": "save_failed", "message": f"{operation}分组 '{name}' 失败"}}

    def _batch_save_groups(self, groups_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量保存分组（支持创建和更新）。"""
        results = []
        for group_data in groups_data:
            try:
                result = self._save_single_group(
                    name=group_data.get("name"),
                    id=group_data.get("id"),
                    parent_id=group_data.get("parent_id", "0"),
                    type=group_data.get("type", "api"),
                    path=group_data.get("path"),
                    options=group_data.get("options")
                )
                results.append({
                    "name": group_data.get("name", "Unknown"),
                    "result": result
                })
            except Exception as e:
                results.append({
                    "name": group_data.get("name", "Unknown"),
                    "result": {"error": {"code": "batch_error", "message": str(e)}}
                })

        success_count = sum(1 for r in results if r["result"].get("success"))
        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }

    def create_api_tool(
        self,
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        script: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[List[Dict[str, Any]]] = None,
        paths: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[str] = None,
        request_body_definition: Optional[Dict[str, Any]] = None,
        response_body: Optional[str] = None,
        response_body_definition: Optional[Dict[str, Any]] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        apis_data: Optional[List[Dict[str, Any]]] = None,
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        保存API接口（支持单个创建或更新操作，包含完整API配置）。

        Args:
            group_id: 分组ID（创建操作必需）
            name: API名称（创建操作必需）
            method: HTTP方法（创建操作必需）
            path: API路径（创建操作必需）
            script: 脚本内容（创建操作必需）
            description: API描述（可选）
            parameters: 查询参数列表（可选）
            headers: 请求头列表（可选）
            paths: 路径变量列表（可选）
            request_body: 请求体示例（可选）
            request_body_definition: 请求体结构定义（可选）
            response_body: 响应体示例（可选）
            response_body_definition: 响应体结构定义（可选）
            options: 接口选项配置（可选）
            apis_data: API数据列表（批量操作，已废弃）
            id: 文件ID（更新操作必需，用于标识要更新的API）

        Returns:
            保存成功返回结果，失败返回错误信息
        """
        # 判断是批量操作还是单个操作
        if apis_data is not None:
            return self._batch_save_apis(apis_data)
        else:
            return self._save_single_api(
                group_id=group_id,
                name=name,
                method=method,
                path=path,
                script=script,
                description=description,
                parameters=parameters,
                headers=headers,
                paths=paths,
                request_body=request_body,
                request_body_definition=request_body_definition,
                response_body=response_body,
                response_body_definition=response_body_definition,
                options=options,
                id=id
            )

    def _save_single_api(
        self,
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        script: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[List[Dict[str, Any]]] = None,
        paths: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[str] = None,
        request_body_definition: Optional[Dict[str, Any]] = None,
        response_body: Optional[str] = None,
        response_body_definition: Optional[Dict[str, Any]] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """保存单个API接口（支持创建和更新操作）。"""
        # 构建完整的API数据对象，包含所有配置选项
        api_data = {}


        api_data["name"] = name
        api_data["method"] = method.upper()
        api_data["path"] = path
        api_data["script"] = script
        api_data["groupId"] = group_id
        api_data["id"] = id
        api_data["description"] = description
        api_data["parameters"] = parameters
        api_data["headers"] = headers
        api_data["paths"] = paths
        api_data["requestBody"] = request_body
        api_data["requestBodyDefinition"] = request_body_definition
        api_data["responseBody"] = response_body
        api_data["responseBodyDefinition"] = response_body_definition
        api_data["options"] = options


        operation = "更新" if id else "创建"

        # 保存API文件并获取详细的错误信息
        result_file_id, error_details = self.manager.save_api_file_with_error_details(
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

        if result_file_id:
            return {"success": True, "id": result_file_id, "name": name or "updated_api", "path": path or "updated_path", "operation": operation}

        # 返回详细的错误信息
        return {
            "error": {
                "code": error_details.get("code", "save_failed"),
                "message": error_details.get("message", f"{operation}API接口失败"),
                "details": error_details
            }
        }

    def _batch_save_apis(self, apis_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量保存API接口（支持创建和更新）。"""
        results = []
        for api_data in apis_data:
            try:
                result = self._save_single_api(
                    group_id=api_data.get("group_id"),
                    name=api_data.get("name"),
                    method=api_data.get("method", "GET"),
                    path=api_data.get("path"),
                    script=api_data.get("script"),
                    id=api_data.get("id"),
                    description=api_data.get("description"),
                    parameters=api_data.get("parameters"),
                    headers=api_data.get("headers"),
                    paths=api_data.get("paths"),
                    request_body=api_data.get("request_body") or api_data.get("requestBody"),
                    request_body_definition=api_data.get("request_body_definition") or api_data.get("requestBodyDefinition"),
                    response_body=api_data.get("response_body") or api_data.get("responseBody"),
                    response_body_definition=api_data.get("response_body_definition") or api_data.get("responseBodyDefinition"),
                    options=api_data.get("options")
                )
                results.append({
                    "name": api_data.get("name", "Unknown"),
                    "result": result
                })
            except Exception as e:
                results.append({
                    "name": api_data.get("name", "Unknown"),
                    "result": {"error": {"code": "batch_error", "message": str(e)}}
                })

        success_count = sum(1 for r in results if r["result"].get("success"))
        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }

    def copy_resource_tool(self, src_id: str, target_id: str) -> Dict[str, Any]:
        """复制资源到指定位置。"""
        new_resource_id = self.manager.copy_resource(src_id, target_id)
        if new_resource_id:
            return {"success": True, "new_resource_id": new_resource_id, "src_id": src_id, "target_id": target_id}
        return {"error": {"code": "copy_failed", "message": f"复制资源 {src_id} 失败"}}

    def move_resource_tool(self, src_id: str, target_id: str) -> Dict[str, Any]:
        """移动资源到指定位置。"""
        try:
            # 验证参数
            if not src_id or not target_id:
                return {"error": {"code": "invalid_params", "message": "src_id和target_id不能为空"}}

            # 检查src_id和target_id是否相同
            if src_id == target_id:
                return {"error": {"code": "invalid_params", "message": "源资源ID和目标ID不能相同"}}

            success = self.manager.move_resource(src_id, target_id)
            if success:
                return {"success": True, "src_id": src_id, "target_id": target_id}
            return {"error": {"code": "move_failed", "message": f"移动资源 {src_id} 失败"}}
        except Exception as e:
            return {"error": {"code": "move_error", "message": f"移动资源时发生异常: {str(e)}"}}

    def delete_resource_tool(
        self,
        resource_id: Optional[str] = None,
        resource_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        删除资源（支持单个和批量操作）。

        Args:
            resource_id: 资源ID（单个操作）
            resource_ids: 资源ID列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        if resource_ids is not None:
            return self._batch_delete_resources(resource_ids)
        else:
            return self._delete_single_resource(resource_id)

    def _delete_single_resource(self, resource_id: str) -> Dict[str, Any]:
        """删除单个资源。"""
        success = self.manager.delete_resource(resource_id)
        if success:
            return {"success": True, "resource_id": resource_id}
        return {"error": {"code": "delete_failed", "message": f"删除资源 {resource_id} 失败"}}

    def _batch_delete_resources(self, resource_ids: List[str]) -> Dict[str, Any]:
        """批量删除资源。"""
        results = []
        for resource_id in resource_ids:
            try:
                result = self._delete_single_resource(resource_id)
                results.append({
                    "resource_id": resource_id,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "resource_id": resource_id,
                    "result": {"error": {"code": "batch_error", "message": str(e)}}
                })

        success_count = sum(1 for r in results if r["result"].get("success"))
        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }

    def lock_resource_tool(
        self,
        resource_id: Optional[str] = None,
        resource_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        锁定资源（支持单个和批量操作）。

        Args:
            resource_id: 资源ID（单个操作）
            resource_ids: 资源ID列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        if resource_ids is not None:
            return self._batch_lock_resources(resource_ids)
        else:
            return self._lock_single_resource(resource_id)

    def _lock_single_resource(self, resource_id: str) -> Dict[str, Any]:
        """锁定单个资源。"""
        success = self.manager.lock_resource(resource_id)
        if success:
            return {"success": True, "resource_id": resource_id}
        return {"error": {"code": "lock_failed", "message": f"锁定资源 {resource_id} 失败"}}

    def _batch_lock_resources(self, resource_ids: List[str]) -> Dict[str, Any]:
        """批量锁定资源。"""
        results = []
        for resource_id in resource_ids:
            try:
                result = self._lock_single_resource(resource_id)
                results.append({
                    "resource_id": resource_id,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "resource_id": resource_id,
                    "result": {"error": {"code": "batch_error", "message": str(e)}}
                })

        success_count = sum(1 for r in results if r["result"].get("success"))
        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }

    def unlock_resource_tool(
        self,
        resource_id: Optional[str] = None,
        resource_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        解锁资源（支持单个和批量操作）。

        Args:
            resource_id: 资源ID（单个操作）
            resource_ids: 资源ID列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        if resource_ids is not None:
            return self._batch_unlock_resources(resource_ids)
        else:
            return self._unlock_single_resource(resource_id)

    def _unlock_single_resource(self, resource_id: str) -> Dict[str, Any]:
        """解锁单个资源。"""
        success = self.manager.unlock_resource(resource_id)
        if success:
            return {"success": True, "resource_id": resource_id}
        return {"error": {"code": "unlock_failed", "message": f"解锁资源 {resource_id} 失败"}}

    def _batch_unlock_resources(self, resource_ids: List[str]) -> Dict[str, Any]:
        """批量解锁资源。"""
        results = []
        for resource_id in resource_ids:
            try:
                result = self._unlock_single_resource(resource_id)
                results.append({
                    "resource_id": resource_id,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "resource_id": resource_id,
                    "result": {"error": {"code": "batch_error", "message": str(e)}}
                })

        success_count = sum(1 for r in results if r["result"].get("success"))
        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results
        }

    def list_groups_tool(self) -> Dict[str, Any]:
        """列出所有分组。"""
        groups = self.manager.list_groups()
        if groups is not None:
            return {"success": True, "groups": groups}
        return {"error": {"code": "list_failed", "message": "获取分组列表失败"}}


    def get_resource_tree_tool(self, kind: str = "api", search: Optional[str] = None,
                              csv: bool = False, depth: Optional[int] = None,
                              method_filter: Optional[str] = None,
                              path_filter: Optional[str] = None,
                              name_filter: Optional[str] = None,
                              query_filter: Optional[str] = None) -> Dict[str, Any]:
        """获取资源树（集成版本）。"""
        from magicapi_tools.utils.extractor import (
            extract_api_endpoints,
            filter_endpoints,
            load_resource_tree,
            _nodes_to_csv,
            MagicAPIExtractorError,
            ResourceTree,
        )

        try:
            # 获取资源树数据
            tree = load_resource_tree(client=self.manager.http_client)
            if not tree:
                return {"error": {"code": "no_tree", "message": "无法获取资源树"}}

            # 过滤资源类型
            kind_normalized = kind if kind in {"api", "function", "task", "datasource", "all"} else "api"
            if kind_normalized != "all":
                # 过滤非API资源类型 - 创建新的ResourceTree对象
                filtered_raw = {"api": tree.raw.get("api", {})} if kind_normalized == "api" else {}
                filtered_tree = ResourceTree(raw=filtered_raw)
            else:
                filtered_tree = tree

            # 提取端点
            endpoints = extract_api_endpoints(filtered_tree)

            # 应用各种过滤器
            endpoints = filter_endpoints(
                endpoints,
                path_filter=path_filter,
                name_filter=name_filter,
                method_filter=method_filter,
                query_filter=query_filter or search,
            )

            # 转换为节点格式
            nodes = []
            for endpoint in endpoints:
                if "[" in endpoint and "]" in endpoint:
                    method_path, name = endpoint.split(" [", 1)
                    name = name.rstrip("]")
                else:
                    method_path, name = endpoint, ""

                method, path = method_path.split(" ", 1)
                nodes.append({
                    "name": name,
                    "type": "api",
                    "path": path,
                    "method": method,
                    "id": None,  # extract_api_endpoints 不包含ID信息
                })

            # 深度限制 (简化实现)
            if depth is not None and depth > 0:
                # 这里可以根据需要实现更复杂的深度限制逻辑
                pass

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
            return {"error": {"code": "extraction_error", "message": f"资源树提取失败: {str(e)}"}}
        except Exception as e:
            return {"error": {"code": "unexpected_error", "message": f"意外错误: {str(e)}"}}

    def export_resource_tree_tool(self, kind: str = "api", format: str = "json") -> Dict[str, Any]:
        """导出资源树。"""
        print(f"DEBUG: export_resource_tree_tool called with kind={kind}, format={format}")
        result = self.get_resource_tree_tool(kind=kind)
        print(f"DEBUG: get_resource_tree_tool result type: {type(result)}")
        if "error" in result:
            print(f"DEBUG: get_resource_tree_tool returned error: {result}")
            return result

        if format.lower() == "csv":
            csv_data = result.get("csv", "")
            print(f"DEBUG: returning CSV format, csv length: {len(csv_data)}")
            return {"success": True, "format": "csv", "data": csv_data}
        else:
            print(f"DEBUG: returning JSON format, result keys: {list(result.keys())}")
            return {"success": True, "format": "json", "data": result}

    def get_resource_stats_tool(self) -> Dict[str, Any]:
        """获取资源统计信息。"""
        try:
            # 直接使用 HTTP 客户端获取资源树，避免重复调用复杂的 get_resource_tree_tool
            ok, tree_data = self.manager.http_client.resource_tree()
            if not ok:
                return {"error": {"code": "stats_error", "message": f"获取资源树失败: {tree_data.get('message', '未知错误')}", "detail": tree_data}}

            if not tree_data:
                return {"error": {"code": "stats_error", "message": "资源树数据为空"}}

            # 统计信息
            total_resources = 0
            api_endpoints = 0
            by_method = {}
            by_type = {}

            # 遍历所有资源类型
            for resource_type, type_data in tree_data.items():
                if not isinstance(type_data, dict) or "children" not in type_data:
                    continue

                # 递归统计节点
                def count_nodes(nodes, current_type):
                    nonlocal total_resources, api_endpoints, by_method, by_type
                    for node in nodes:
                        node_info = node.get("node", {})
                        total_resources += 1

                        # 统计资源类型
                        node_resource_type = node_info.get("type", current_type)
                        by_type[node_resource_type] = by_type.get(node_resource_type, 0) + 1

                        # 如果是API接口，统计方法
                        method = node_info.get("method")
                        if method:
                            api_endpoints += 1
                            by_method[method.upper()] = by_method.get(method.upper(), 0) + 1

                        # 递归处理子节点
                        children = node.get("children", [])
                        if children:
                            count_nodes(children, current_type)

                count_nodes(type_data["children"], resource_type)

            stats = {
                "total_resources": total_resources,
                "api_endpoints": api_endpoints,
                "other_resources": total_resources - api_endpoints,
                "by_method": by_method,
                "by_type": by_type,
                "resource_types": list(tree_data.keys()) if isinstance(tree_data, dict) else []
            }

            return {"success": True, "stats": stats}
        except Exception as e:
            return {"error": {"code": "stats_error", "message": f"统计资源信息时发生异常: {str(e)}"}}


class MagicAPIResourceManager:
    """
    Magic-API 资源管理器
    基于 MagicResourceController 实现
    """

    def __init__(self, base_url: str, username: str = None, password: str = None, http_client: Optional[MagicAPIHTTPClient] = None):
        """
        初始化资源管理器

        Args:
            base_url: Magic-API 基础URL
            username: 用户名
            password: 密码
            http_client: MagicAPIHTTPClient 实例，如果不提供则创建新的实例
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.username = username
        self.password = password

        # 如果提供了 http_client，则使用它，否则创建新的实例
        if http_client is not None:
            self.http_client = http_client
        else:
            # 创建默认的 HTTP 客户端
            settings = MagicAPISettings(
                base_url=base_url,
                username=username,
                password=password
            )
            self.http_client = MagicAPIHTTPClient(settings=settings)

        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        # 如果提供了认证信息，进行登录
        if username and password:
            self.login()

    def login(self):
        """登录认证"""
        login_data = {
            'username': self.username,
            'password': self.password
        }
        response = self.session.post(f"{self.base_url}/magic/web/login", json=login_data)
        if response.status_code == 200:
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.text}")

    def save_group(self, name: Optional[str] = None, id: Optional[str] = None,
                   parent_id: str = "0", type: str = "api",
                   path: Optional[str] = None, options: Optional[Dict] = None) -> Optional[str]:
        """
        保存分组目录（支持创建和更新操作）
        基于 MagicResourceController.saveFolder 实现

        系统通过是否包含 id 字段来判断是新建还是更新操作：
        - 创建操作：id 为 None 或不存在
        - 更新操作：id 存在且有效

        Args:
            name: 分组名称（创建时必需）
            id: 分组ID（更新时必需）
            parent_id: 父分组ID，默认为根目录"0"
            type: 分组类型，默认为"api"
            path: 分组路径
            options: 选项配置

        Returns:
            保存成功返回分组ID，失败返回None
        """
        
        # 构建请求数据
        group_data = {
            "parentId": parent_id,
            "type": type
        }

        # 添加必需字段
        if name is not None:
            group_data["name"] = name
        if id is not None:
            group_data["id"] = id

        # 只在path和options都不为空时才添加
        if path is not None:
            group_data["path"] = path

        if options is not None and options != {}:
            group_data["options"] = options

        is_update = id is not None
        operation = "更新" if is_update else "创建"

        try:
            print(f"📝 {operation}分组请求数据: {group_data}")
            response = self.session.post(
                f"{self.base_url}/magic/web/resource/folder/save",
                json=group_data
            )

            print(f"📊 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    group_id = result.get('data')
                    print(f"✅ {operation}分组成功: {name or 'updated_group'} (ID: {group_id})")
                    return group_id
                else:
                    print(f"❌ {operation}分组失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ {operation}分组时出错: {e}")

        return None

    def copy_resource(self, src_resource_id: str, target_id: str) -> Optional[str]:
        """
        复制资源（文件或分组）到指定位置

        Args:
            src_resource_id: 源资源ID（可以是文件ID或分组ID）
            target_id: 目标位置ID（如果是复制到分组，则为目标分组ID；如果是文件复制，则为目标分组ID）

        Returns:
            复制成功返回新资源ID，失败返回None
        """
        try:
            # 首先尝试复制分组
            new_group_id = self.copy_group(src_resource_id, target_id)
            if new_group_id:
                return new_group_id

            # 如果分组复制失败，尝试复制文件
            print(f"📄 分组复制失败，尝试复制文件: {src_resource_id}")
            new_file_id = self.copy_file(src_resource_id, target_id)
            if new_file_id:
                return new_file_id

            print(f"❌ 复制资源失败: {src_resource_id}")
            return None

        except Exception as e:
            print(f"❌ 复制资源时出错: {e}")
            return None

    def copy_group(self, src_group_id: str, target_parent_id: str = "0") -> Optional[str]:
        """
        复制分组目录
        基于 MagicResourceController.saveFolder(String src, String target) 实现

        Args:
            src_group_id: 源分组ID
            target_parent_id: 目标父分组ID，默认为根目录"0"

        Returns:
            复制成功返回新分组ID，失败返回None
        """
        try:
            # 使用与移动API相同的headers格式
            copy_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'magic-token': 'unauthorization'
            }

            response = self.session.post(
                f"{self.base_url}/magic/web/resource/folder/copy",
                data={
                    'src': src_group_id,
                    'target': target_parent_id
                },
                headers=copy_headers
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    new_group_id = result.get('data')
                    print(f"✅ 复制分组成功: {src_group_id} -> {new_group_id}")
                    return new_group_id
                else:
                    print(f"❌ 复制分组失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 复制分组时出错: {e}")

        return None

    def copy_file(self, src_file_id: str, target_group_id: str) -> Optional[str]:
        """
        复制文件到指定分组
        通过获取源文件详情并创建新文件的方式实现复制

        Args:
            src_file_id: 源文件ID
            target_group_id: 目标分组ID

        Returns:
            复制成功返回新文件ID，失败返回None
        """
        try:
            # 获取源文件详情
            file_detail = self.get_file_detail(src_file_id)
            if not file_detail:
                print(f"❌ 无法获取源文件详情: {src_file_id}")
                return None

            # 构建新的文件名（添加"副本"后缀）
            original_name = file_detail.get('name', 'Unknown')
            new_name = f"{original_name}_副本"

            # 准备API数据
            api_data = {
                'name': new_name,
                'method': file_detail.get('method', 'GET'),
                'path': file_detail.get('path', ''),
                'script': file_detail.get('script', ''),
                'groupId': target_group_id,
                'parameters': file_detail.get('parameters', []),
                'headers': file_detail.get('headers', []),
                'paths': file_detail.get('paths', []),
                'requestBody': file_detail.get('requestBody', ''),
                'responseBody': file_detail.get('responseBody', ''),
                'options': file_detail.get('options', [])
            }

            # 如果有请求体定义，也复制
            if 'requestBodyDefinition' in file_detail:
                api_data['requestBodyDefinition'] = file_detail['requestBodyDefinition']
            if 'responseBodyDefinition' in file_detail:
                api_data['responseBodyDefinition'] = file_detail['responseBodyDefinition']
            if 'description' in file_detail:
                api_data['description'] = file_detail['description']

            # 保存新文件
            new_file_id = self.save_api_file(target_group_id, api_data)
            if new_file_id:
                print(f"✅ 复制文件成功: {src_file_id} -> {new_file_id} ({new_name})")
                return new_file_id
            else:
                print(f"❌ 保存新文件失败")
                return None

        except Exception as e:
            print(f"❌ 复制文件时出错: {e}")
            return None

    def delete_resource(self, resource_id: str) -> bool:
        """
        删除资源（分组或文件）
        基于 MagicResourceController.delete 实现

        Args:
            resource_id: 资源ID

        Returns:
            删除成功返回True，失败返回False
        """
        try:
            delete_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'magic-token': 'unauthorization'
            }

            response = self.session.post(
                f"{self.base_url}/magic/web/resource/delete",
                data={'id': resource_id},
                headers=delete_headers
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1 and result.get('data'):
                    print(f"✅ 删除资源成功: {resource_id}")
                    return True
                else:
                    print(f"❌ 删除资源失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 删除资源时出错: {e}")

        return False

    def move_resource(self, src_id: str, target_group_id: str) -> bool:
        """
        移动资源到指定分组
        基于 MagicResourceController.move 实现

        Args:
            src_id: 源资源ID（可以是文件ID或分组ID）
            target_group_id: 目标分组ID

        Returns:
            移动成功返回True，失败返回False
        """
        try:
            print(f"🔄 移动资源: {src_id} -> {target_group_id}")

            # 验证目标是否为分组（如果能获取到文件详情，说明是文件；如果获取不到，可能是分组）
            target_detail = self.get_file_detail(target_group_id)
            if target_detail:
                # 目标是文件，不能作为移动目标
                print(f"❌ 移动目标必须是分组，目标ID {target_group_id} 是文件")
                return False

            # 尝试移动资源（使用form-urlencoded格式，与curl命令一致）
            move_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'magic-token': 'unauthorization'
            }

            response = self.session.post(
                f"{self.base_url}/magic/web/resource/move",
                data={
                    'src': src_id,
                    'groupId': target_group_id
                },
                headers=move_headers
            )

            print(f"📊 响应状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"📄 响应内容: {result}")

                if result.get('code') == 1 and result.get('data'):
                    print(f"✅ 移动资源成功: {src_id} -> {target_group_id}")
                    return True
                else:
                    error_msg = result.get('message', '未知错误')
                    print(f"❌ 移动资源失败: {error_msg}")

                    # 提供更详细的错误信息
                    if '找不到' in error_msg or 'not found' in error_msg.lower():
                        print("💡 提示: 请检查源资源ID和目标分组ID是否存在")
                    elif '权限' in error_msg or 'permission' in error_msg.lower():
                        print("💡 提示: 请检查是否有移动权限")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 移动资源时出错: {e}")
            return False

    def get_resource_tree(self) -> Optional[Dict]:
        """
        获取资源树结构
        基于 MagicResourceController.resources 实现

        Returns:
            资源树数据，失败返回None
        """
        try:
            print(f"📋 获取资源树...")
            response = self.session.post(f"{self.base_url}/magic/web/resource")

            print(f"📊 响应状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    tree_data = result.get('data')
                    print(f"✅ 获取资源树成功，共 {len(tree_data) if tree_data else 0} 个顶级分类")
                    return tree_data
                else:
                    print(f"❌ 获取资源树失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"❌ 错误详情: {error_detail}")
                except:
                    print(f"❌ 响应内容: {response.text}")
        except Exception as e:
            print(f"❌ 获取资源树时出错: {e}")

        return None

    def get_file_detail(self, file_id: str) -> Optional[Dict]:
        """
        获取文件详情
        基于 MagicResourceController.detail 实现

        Args:
            file_id: 文件ID

        Returns:
            文件详情数据，失败返回None
        """
        try:
            response = self.session.get(f"{self.base_url}/magic/web/resource/file/{file_id}")

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    return result.get('data')
                else:
                    error_msg = result.get('message', '未知错误')
                    error_detail = result.get('data')
                    print(f"❌ 获取文件详情失败: {error_msg}")
                    print(f"   文件ID: {file_id}")
                    print(f"   错误详情: {error_detail}")
                    print(f"   完整响应: {result}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
                print(f"   文件ID: {file_id}")
                print(f"   请求URL: {self.base_url}/magic/web/resource/file/{file_id}")
                print(f"   响应头: {dict(response.headers)}")
        except Exception as e:
            print(f"❌ 获取文件详情时出错: {e}")
            print(f"   文件ID: {file_id}")
            import traceback
            print(f"   错误堆栈: {traceback.format_exc()}")

        return None

    def lock_resource(self, resource_id: str) -> bool:
        """
        锁定资源
        基于 MagicResourceController.lock 实现

        Args:
            resource_id: 资源ID

        Returns:
            锁定成功返回True，失败返回False
        """
        try:
            lock_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'magic-token': 'unauthorization'
            }

            response = self.session.post(
                f"{self.base_url}/magic/web/resource/lock",
                data={'id': resource_id},
                headers=lock_headers
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1 and result.get('data'):
                    print(f"✅ 锁定资源成功: {resource_id}")
                    return True
                else:
                    print(f"❌ 锁定资源失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 锁定资源时出错: {e}")

        return False

    def unlock_resource(self, resource_id: str) -> bool:
        """
        解锁资源
        基于 MagicResourceController.unlock 实现

        Args:
            resource_id: 资源ID

        Returns:
            解锁成功返回True，失败返回False
        """
        try:
            unlock_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'magic-token': 'unauthorization'
            }

            response = self.session.post(
                f"{self.base_url}/magic/web/resource/unlock",
                data={'id': resource_id},
                headers=unlock_headers
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1 and result.get('data'):
                    print(f"✅ 解锁资源成功: {resource_id}")
                    return True
                else:
                    print(f"❌ 解锁资源失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 解锁资源时出错: {e}")

        return False

    def save_api_file(
        self,
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        script: Optional[str] = None,
        id: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[List[Dict[str, Any]]] = None,
        paths: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[str] = None,
        request_body_definition: Optional[Dict[str, Any]] = None,
        response_body: Optional[str] = None,
        response_body_definition: Optional[Dict[str, Any]] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        auto_save: bool = False
    ) -> Optional[str]:
        """
        保存API文件（支持创建和更新操作）
        基于 MagicResourceController.saveFile 实现

        Args:
            group_id: 分组ID（创建时必需）
            name: API名称
            method: HTTP方法
            path: API路径
            script: 脚本内容
            id: 文件ID（更新时必需）
            description: API描述
            parameters: 查询参数列表
            headers: 请求头列表
            paths: 路径变量列表
            request_body: 请求体示例
            request_body_definition: 请求体结构定义
            response_body: 响应体示例
            response_body_definition: 响应体结构定义
            options: 接口选项配置
            auto_save: 是否自动保存

        Returns:
            保存成功返回文件ID，失败返回None
        """
        try:
            is_update = id is not None

            if is_update:
                # 更新操作：获取现有数据并合并
                existing_data = self.get_file_detail(id)
                if not existing_data:
                    logger.error(f"更新API失败: 无法获取现有数据进行合并")
                    logger.error(f"  API ID: {id}")
                    logger.error(f"  操作: 更新API接口")
                    logger.error(f"  错误原因: get_file_detail返回None")
                    logger.error(f"  建议: 检查API ID是否正确，或该API是否已被删除")
                    return None

                # 合并现有数据和新数据
                full_api_data = existing_data.copy()
                # 更新提供的字段
                if name is not None:
                    full_api_data["name"] = name
                if method is not None:
                    full_api_data["method"] = method.upper()
                if path is not None:
                    full_api_data["path"] = path
                if script is not None:
                    full_api_data["script"] = script
                if description is not None:
                    full_api_data["description"] = description
                if parameters is not None:
                    full_api_data["parameters"] = parameters
                if headers is not None:
                    full_api_data["headers"] = headers
                if paths is not None:
                    full_api_data["paths"] = paths
                if request_body is not None:
                    full_api_data["requestBody"] = request_body
                if request_body_definition is not None:
                    full_api_data["requestBodyDefinition"] = request_body_definition
                if response_body is not None:
                    full_api_data["responseBody"] = response_body
                if response_body_definition is not None:
                    full_api_data["responseBodyDefinition"] = response_body_definition
                if options is not None:
                    full_api_data["options"] = options

                # 确保有必要的字段用于更新
                if "groupId" not in full_api_data and group_id:
                    full_api_data["groupId"] = group_id

            else:
                # 创建操作：验证必要字段
                required_fields = ['name', 'method', 'path', 'script']
                required_values = [name, method, path, script]
                for field, value in zip(required_fields, required_values):
                    if value is None:
                        print(f"❌ save_api_file缺少必要字段: {field}")
                        return None

                # 构建完整的API对象，基于现有API的结构
                full_api_data = {
                    "name": name,
                    "method": method.upper(),
                    "path": path,
                    "script": script,
                    "groupId": group_id,
                    "parameters": parameters or [],
                    "options": options or [],
                    "requestBody": request_body or "",
                    "headers": headers or [],
                    "paths": paths or [],
                    "responseBody": response_body or "",
                    "description": description or "",
                }

                # 添加可选的结构定义字段
                if request_body_definition:
                    full_api_data["requestBodyDefinition"] = request_body_definition
                if response_body_definition:
                    full_api_data["responseBodyDefinition"] = response_body_definition

            # 将API数据转换为JSON字符串
            api_json = json.dumps(full_api_data, ensure_ascii=False)
            print(f"📝 保存API文件请求数据: {api_json}")

            # 构建请求参数
            params = {
                'groupId': full_api_data.get("groupId"),
                'auto': '1' if auto_save else '0'
            }

            # 如果是更新操作，添加到URL中
            url = f"{self.base_url}/magic/web/resource/file/api/save"
            if is_update:
                url += f"/{id}"

            # 使用application/json类型发送完整的API对象
            response = self.session.post(
                url,
                json=full_api_data,
                params=params
            )

            print(f"📊 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    file_id = result.get('data')
                    operation = "更新" if is_update else "创建"
                    print(f"✅ {operation}API文件成功: {full_api_data['name']} (ID: {file_id})")
                    return file_id
                else:
                    operation = "更新" if is_update else "创建"
                    print(f"❌ {operation}API文件失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            operation = "更新" if is_update else "创建"
            print(f"❌ {operation}API文件时出错: {e}")

        return None

    def save_api_file_with_error_details(
        self,
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        script: Optional[str] = None,
        id: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[List[Dict[str, Any]]] = None,
        paths: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[str] = None,
        request_body_definition: Optional[Dict[str, Any]] = None,
        response_body: Optional[str] = None,
        response_body_definition: Optional[Dict[str, Any]] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        auto_save: bool = False
    ) -> tuple[Optional[str], Dict[str, Any]]:
        """
        保存API文件并返回详细的错误信息（支持创建和更新操作）
        基于 MagicResourceController.saveFile 实现

        Returns:
            tuple: (file_id, error_details) - file_id为None时error_details包含错误信息
        """
        try:
            is_update = id is not None

            if is_update:
                # 更新操作：获取现有数据并合并
                existing_data = self.get_file_detail(id)
                if not existing_data:
                    return None, {
                        "code": "file_not_found",
                        "message": "找不到要更新的API文件",
                        "details": f"API ID: {id}",
                        "suggestion": "检查API ID是否正确，或该API是否已被删除"
                    }

                # 合并现有数据和新数据
                full_api_data = existing_data.copy()
                # 更新提供的字段
                if name is not None:
                    full_api_data["name"] = name
                if method is not None:
                    full_api_data["method"] = method.upper()
                if path is not None:
                    full_api_data["path"] = path
                if script is not None:
                    full_api_data["script"] = script
                if description is not None:
                    full_api_data["description"] = description
                if parameters is not None:
                    full_api_data["parameters"] = parameters
                if headers is not None:
                    full_api_data["headers"] = headers
                if paths is not None:
                    full_api_data["paths"] = paths
                if request_body is not None:
                    full_api_data["requestBody"] = request_body
                if request_body_definition is not None:
                    full_api_data["requestBodyDefinition"] = request_body_definition
                if response_body is not None:
                    full_api_data["responseBody"] = response_body
                if response_body_definition is not None:
                    full_api_data["responseBodyDefinition"] = response_body_definition
                if options is not None:
                    full_api_data["options"] = options

                # 确保有必要的字段用于更新
                if "groupId" not in full_api_data and group_id:
                    full_api_data["groupId"] = group_id

            else:
                # 创建操作：验证必要字段
                required_fields = ['name', 'method', 'path', 'script']
                required_values = [name, method, path, script]
                missing_fields = []
                for field, value in zip(required_fields, required_values):
                    if value is None:
                        missing_fields.append(field)

                if missing_fields:
                    return None, {
                        "code": "missing_required_fields",
                        "message": f"创建API缺少必需字段: {', '.join(missing_fields)}",
                        "missing_fields": missing_fields
                    }

                # 构建完整的API对象，基于现有API的结构
                full_api_data = {
                    "name": name,
                    "method": method.upper(),
                    "path": path,
                    "script": script,
                    "groupId": group_id,
                    "parameters": parameters or [],
                    "options": options or [],
                    "requestBody": request_body or "",
                    "headers": headers or [],
                    "paths": paths or [],
                    "responseBody": response_body or "",
                    "description": description or "",
                }

                # 添加可选的结构定义字段
                if request_body_definition:
                    full_api_data["requestBodyDefinition"] = request_body_definition
                if response_body_definition:
                    full_api_data["responseBodyDefinition"] = response_body_definition

            # 将API数据转换为JSON字符串
            api_json = json.dumps(full_api_data, ensure_ascii=False)
            print(f"📝 保存API文件请求数据: {api_json}")

            # 构建请求参数
            params = {
                'groupId': full_api_data.get("groupId"),
                'auto': '1' if auto_save else '0'
            }

            # 如果是更新操作，添加到URL中
            url = f"{self.base_url}/magic/web/resource/file/api/save"
            if is_update:
                url += f"/{id}"

            # 使用application/json类型发送完整的API对象
            response = self.session.post(
                url,
                json=full_api_data,
                params=params
            )

            print(f"📊 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('code') == 1:
                        file_id = result.get('data')
                        operation = "更新" if is_update else "创建"
                        print(f"✅ {operation}API文件成功: {full_api_data['name']} (ID: {file_id})")
                        return file_id, {}
                    else:
                        operation = "更新" if is_update else "创建"
                        error_message = result.get('message', '未知错误')
                        print(f"❌ {operation}API文件失败: {error_message}")

                        # 返回完整的错误信息
                        return None, {
                            "code": str(result.get('code', 'api_error')),
                            "message": error_message,
                            "http_status": response.status_code,
                            "response_data": result,
                            "request_data": full_api_data,
                            "url": url,
                            "operation": operation
                        }
                except json.JSONDecodeError as e:
                    return None, {
                        "code": "invalid_json_response",
                        "message": f"服务器返回了无效的JSON响应: {e}",
                        "http_status": response.status_code,
                        "raw_response": response.text,
                        "url": url
                    }
            else:
                return None, {
                    "code": f"http_{response.status_code}",
                    "message": f"HTTP请求失败: {response.status_code}",
                    "http_status": response.status_code,
                    "response_text": response.text,
                    "url": url
                }

        except Exception as e:
            operation = "更新" if is_update else "创建"
            print(f"❌ {operation}API文件时出错: {e}")

            return None, {
                "code": "unexpected_error",
                "message": f"{operation}API时发生异常: {str(e)}",
                "exception_type": type(e).__name__,
                "operation": operation
            }

    def print_resource_tree(self, tree_data: Dict, indent: int = 0, filter_type: str = "api",
                          csv_format: bool = False, search_pattern: str = None, max_depth: int = None):
        """
        打印资源树结构（大模型易读格式）

        Args:
            tree_data: 树数据
            indent: 缩进级别
            filter_type: 过滤类型，默认只显示"api"类型，可选值: "all", "api", "function", "task", "datasource"
            csv_format: 是否输出CSV格式
            search_pattern: 搜索模式，支持正则表达式
            max_depth: 最大显示深度，None表示不限制
        """
        if not tree_data:
            print("  " * indent + "[暂无数据]")
            return

        # 如果是CSV格式或有搜索模式，先收集所有资源
        if csv_format or search_pattern:
            all_resources = self._collect_resources(tree_data, filter_type)
            if search_pattern:
                import re
                try:
                    pattern = re.compile(search_pattern, re.IGNORECASE)
                    all_resources = [res for res in all_resources if pattern.search(res['name']) or pattern.search(res['path'])]
                except re.error as e:
                    print(f"❌ 搜索模式错误: {e}")
                    return

            if csv_format:
                self._print_csv_resources(all_resources)
            else:
                self._print_filtered_resources(all_resources)
            return

        # 正常树形显示
        allowed_types = ["api", "function", "task", "datasource"] if filter_type == "all" else [filter_type]

        for folder_type, tree_node in tree_data.items():
            # 如果不是"all"模式，只显示指定类型的资源
            if filter_type != "all" and folder_type not in allowed_types:
                continue

            if tree_node and 'node' in tree_node:
                node_info = tree_node['node']
                name = node_info.get('name', folder_type)
                path = node_info.get('path', '')
                if path:
                    print("  " * indent + f"[目录] {name} | {path} | {folder_type}")
                else:
                    print("  " * indent + f"[目录] {name} | {folder_type}")
                if 'children' in tree_node and tree_node['children']:
                    self._print_tree_node(tree_node['children'], indent + 1, filter_type, max_depth)
            else:
                print("  " * indent + f"[目录] {folder_type}")
                if tree_node and 'children' in tree_node:
                    self._print_tree_node(tree_node['children'], indent + 1, filter_type, max_depth)

    def _print_tree_node(self, nodes: List[Dict], indent: int, filter_type: str = "api", max_depth: int = None):
        """
        递归打印树节点（大模型易读格式）

        Args:
            nodes: 节点列表
            indent: 缩进级别
            filter_type: 过滤类型
            max_depth: 最大显示深度，None表示不限制
        """
        if not nodes:
            return

        # 检查深度限制
        if max_depth is not None and indent >= max_depth:
            return

        for node in nodes:
            # 解析节点信息
            if 'node' in node:
                node_info = node['node']
                name = node_info.get('name', 'Unknown')
                node_type = node_info.get('type', '')
                method = node_info.get('method', '')
                path = node_info.get('path', '')

                # 判断节点类型并构建输出格式
                if method:
                    # API接口: [API] 名称 | 路径 | 方法
                    if path:
                        print("  " * indent + f"[API] {name} | {path} | {method}")
                    else:
                        print("  " * indent + f"[API] {name} | {method}")
                elif node_type == 'api' or node_type == 'function' or node_type == 'task' or node_type == 'datasource':
                    # 分组目录: [目录] 名称 | 路径 | 类型
                    if path:
                        print("  " * indent + f"[目录] {name} | {path} | {node_type}")
                    else:
                        print("  " * indent + f"[目录] {name} | {node_type}")
                elif 'children' in node and node['children']:
                    # 有子节点的分组
                    if path:
                        print("  " * indent + f"[目录] {name} | {path}")
                    else:
                        print("  " * indent + f"[目录] {name}")
                else:
                    # 普通文件
                    if path:
                        print("  " * indent + f"[文件] {name} | {path}")
                    else:
                        print("  " * indent + f"[文件] {name}")
            else:
                # 兼容旧格式
                name = node.get('name', 'Unknown')
                node_type = "[目录]" if node.get('children') else "[文件]"
                print("  " * indent + f"{node_type} {name}")

            # 递归处理子节点
            if 'children' in node and node['children']:
                self._print_tree_node(node['children'], indent + 1, filter_type)

    def _collect_resources(self, tree_data: Dict, filter_type: str = "api") -> List[Dict]:
        """
        收集所有资源信息

        Args:
            tree_data: 树数据
            filter_type: 过滤类型

        Returns:
            资源列表
        """
        resources = []

        # 定义要显示的类型
        allowed_types = ["api", "function", "task", "datasource"] if filter_type == "all" else [filter_type]

        for folder_type, tree_node in tree_data.items():
            # 如果不是"all"模式，只显示指定类型的资源
            if filter_type != "all" and folder_type not in allowed_types:
                continue

            if tree_node and 'children' in tree_node:
                resources.extend(self._collect_nodes(tree_node['children'], folder_type))

        return resources

    def _collect_nodes(self, nodes: List[Dict], folder_type: str) -> List[Dict]:
        """
        递归收集节点信息

        Args:
            nodes: 节点列表
            folder_type: 文件夹类型

        Returns:
            节点信息列表
        """
        resources = []

        for node in nodes:
            if 'node' in node:
                node_info = node['node']
                name = node_info.get('name', 'Unknown')
                node_type = node_info.get('type', '')
                method = node_info.get('method', '')
                path = node_info.get('path', '')

                resource_info = {
                    'name': name,
                    'path': path,
                    'type': folder_type,
                    'method': method if method else '',
                    'node_type': node_type
                }
                resources.append(resource_info)

                # 递归处理子节点
                if 'children' in node and node['children']:
                    resources.extend(self._collect_nodes(node['children'], folder_type))

        return resources

    def _print_csv_resources(self, resources: List[Dict]):
        """
        CSV格式输出资源信息

        Args:
            resources: 资源列表
        """
        # CSV头部
        print("type,name,path,method,node_type")

        # CSV数据
        for resource in resources:
            # CSV转义：处理包含逗号、引号的字段
            def escape_csv_field(field):
                if ',' in str(field) or '"' in str(field) or '\n' in str(field):
                    return f'"{str(field).replace(chr(34), chr(34) + chr(34))}"'
                return str(field)

            print(f"{escape_csv_field(resource['type'])},{escape_csv_field(resource['name'])},{escape_csv_field(resource['path'])},{escape_csv_field(resource['method'])},{escape_csv_field(resource['node_type'])}")

    def _print_filtered_resources(self, resources: List[Dict]):
        """
        打印过滤后的资源列表

        Args:
            resources: 资源列表
        """
        print(f"找到 {len(resources)} 个匹配的资源:")
        print()

        for resource in resources:
            if resource['method']:
                # API接口
                if resource['path']:
                    print(f"[API] {resource['name']} | {resource['path']} | {resource['method']}")
                else:
                    print(f"[API] {resource['name']} | {resource['method']}")
            elif resource['node_type']:
                # 分组目录
                if resource['path']:
                    print(f"[目录] {resource['name']} | {resource['path']} | {resource['node_type']}")
                else:
                    print(f"[目录] {resource['name']} | {resource['node_type']}")
            else:
                # 普通文件
                if resource['path']:
                    print(f"[文件] {resource['name']} | {resource['path']}")
                else:
                    print(f"[文件] {resource['name']}")

    def create_api_file(self, group_id: str, name: str, method: str, path: str, script: str, auto_save: bool = False) -> Optional[str]:
        """
        创建API文件（便捷方法）

        Args:
            group_id: 分组ID
            name: API名称
            method: HTTP方法 (GET, POST, PUT, DELETE)
            path: API路径
            script: 脚本内容
            auto_save: 是否自动保存

        Returns:
            创建成功返回文件ID，失败返回None
        """
        api_data = {
            "name": name,
            "method": method.upper(),
            "path": path,
            "script": script
        }

        return self.save_api_file(group_id, api_data, auto_save)

    def list_groups(self) -> List[Dict]:
        """
        获取所有分组列表

        Returns:
            分组列表
        """
        tree_data = self.get_resource_tree()
        if not tree_data:
            return []

        groups = []
        for folder_type, tree_node in tree_data.items():
            if tree_node and 'children' in tree_node:
                groups.extend(self._extract_groups_from_tree(tree_node['children'], folder_type))

        return groups

    def _extract_groups_from_tree(self, nodes: List[Dict], folder_type: str) -> List[Dict]:
        """
        从树节点中提取分组信息

        Args:
            nodes: 节点列表
            folder_type: 文件夹类型

        Returns:
            分组列表
        """
        groups = []

        for node in nodes:
            if 'node' in node:
                node_info = node['node']

                # 判断是否为分组：只要有子节点就是分组
                has_children = 'children' in node and node['children']

                if has_children:
                    # 是分组：类型设为 xxx-group 格式
                    group_type = folder_type
                    if not group_type:
                        # 如果没有类型标识，使用默认值
                        group_type = "unknown"
                    # 确保类型以 "-group" 结尾
                    if not group_type.endswith("-group"):
                        group_type = f"{group_type}-group"
                else:
                    # 不是分组：保持原有类型（可能是API端点等）
                    group_type = folder_type if folder_type else "api"

                group_info = {
                    'id': node_info.get('id'),
                    'name': node_info.get('name'),
                    'type': group_type,
                    'parentId': node_info.get('parentId'),
                    'path': node_info.get('path'),
                    'method': node_info.get('method')
                }
                groups.append(group_info)

                # 递归处理子节点
                if 'children' in node and node['children']:
                    groups.extend(self._extract_groups_from_tree(node['children'], folder_type))

        return groups



__all__ = ['MagicAPIResourceManager']
