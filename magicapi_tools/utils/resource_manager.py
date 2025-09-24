"""Magic-API 资源管理器核心实现。"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import requests

from .http_client import MagicAPIHTTPClient
from magicapi_mcp.settings import MagicAPISettings


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

    def create_group_tool(
        self,
        name: Optional[str] = None,
        parent_id: str = "0",
        group_type: str = "api",
        path: Optional[str] = None,
        options: Optional[str] = None,
        groups_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        创建分组（支持单个和批量操作）。

        Args:
            name: 分组名称（单个操作）
            parent_id: 父分组ID
            group_type: 分组类型
            path: 分组路径
            options: 选项配置JSON字符串
            groups_data: 分组数据列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        # 判断是批量操作还是单个操作
        if groups_data is not None:
            return self._batch_create_groups(groups_data)
        else:
            return self._create_single_group(name, parent_id, group_type, path, options)

    def _create_single_group(
        self,
        name: str,
        parent_id: str = "0",
        group_type: str = "api",
        path: Optional[str] = None,
        options: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建单个分组。"""
        options_dict = None
        if options:
            try:
                options_dict = json.loads(options)
            except json.JSONDecodeError:
                return {"error": {"code": "invalid_json", "message": f"options 格式错误: {options}"}}

        group_id = self.manager.create_group(
            name=name,
            parent_id=parent_id,
            group_type=group_type,
            path=path,
            options=options_dict,
        )
        if group_id:
            return {"success": True, "group_id": group_id, "name": name}
        return {"error": {"code": "create_failed", "message": f"创建分组 '{name}' 失败"}}

    def _batch_create_groups(self, groups_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量创建分组。"""
        results = []
        for group_data in groups_data:
            try:
                result = self._create_single_group(
                    name=group_data["name"],
                    parent_id=group_data.get("parent_id", "0"),
                    group_type=group_data.get("group_type", "api"),
                    path=group_data.get("path"),
                    options=group_data.get("options")
                )
                results.append({
                    "name": group_data["name"],
                    "result": result
                })
            except Exception as e:
                results.append({
                    "name": group_data["name"],
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
        apis_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        创建API接口（支持单个和批量操作）。

        Args:
            group_id: 分组ID（单个操作）
            name: API名称（单个操作）
            method: HTTP方法（单个操作）
            path: API路径（单个操作）
            script: 脚本内容（单个操作）
            apis_data: API数据列表（批量操作）

        Returns:
            单个操作返回单个结果，批量操作返回汇总结果
        """
        # 判断是批量操作还是单个操作
        if apis_data is not None:
            return self._batch_create_apis(apis_data)
        else:
            return self._create_single_api(group_id, name, method, path, script)

    def _create_single_api(
        self,
        group_id: str,
        name: str,
        method: str,
        path: str,
        script: str,
    ) -> Dict[str, Any]:
        """创建单个API接口。"""
        file_id = self.manager.create_api_file(
            group_id=group_id,
            name=name,
            method=method,
            path=path,
            script=script,
        )
        if file_id:
            return {"success": True, "file_id": file_id, "name": name, "path": path}
        return {"error": {"code": "create_failed", "message": f"创建API接口 '{name}' 失败"}}

    def _batch_create_apis(self, apis_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量创建API接口。"""
        results = []
        for api_data in apis_data:
            try:
                result = self._create_single_api(
                    group_id=api_data["group_id"],
                    name=api_data["name"],
                    method=api_data["method"],
                    path=api_data["path"],
                    script=api_data["script"]
                )
                results.append({
                    "name": api_data["name"],
                    "result": result
                })
            except Exception as e:
                results.append({
                    "name": api_data["name"],
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
        new_group_id = self.manager.copy_group(src_id, target_id)
        if new_group_id:
            return {"success": True, "new_group_id": new_group_id, "src_id": src_id, "target_id": target_id}
        return {"error": {"code": "copy_failed", "message": f"复制资源 {src_id} 失败"}}

    def move_resource_tool(self, src_id: str, target_id: str) -> Dict[str, Any]:
        """移动资源到指定位置。"""
        success = self.manager.move_resource(src_id, target_id)
        if success:
            return {"success": True, "src_id": src_id, "target_id": target_id}
        return {"error": {"code": "move_failed", "message": f"移动资源 {src_id} 失败"}}

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

    def create_group(self, name: str, parent_id: str = "0", group_type: str = "api",
                    path: str = None, options: Dict = None) -> Optional[str]:
        """
        创建分组目录
        基于 MagicResourceController.saveFolder 实现

        Args:
            name: 分组名称
            parent_id: 父分组ID，默认为根目录"0"
            group_type: 分组类型，默认为"api"
            path: 分组路径
            options: 选项配置

        Returns:
            创建成功返回分组ID，失败返回None
        """
        # 构建请求数据，避免options序列化问题
        group_data = {
            "name": name,
            "parentId": parent_id,
            "type": group_type
        }

        # 只在path和options都不为空时才添加
        if path is not None:
            group_data["path"] = path

        if options is not None:
            group_data["options"] = options

        try:
            print(f"📝 创建分组请求数据: {group_data}")
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
                    print(f"✅ 创建分组成功: {name} (ID: {group_id})")
                    return group_id
                else:
                    print(f"❌ 创建分组失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 创建分组时出错: {e}")

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
            response = self.session.post(
                f"{self.base_url}/magic/web/resource/folder/copy",
                data={
                    'src': src_group_id,
                    'target': target_parent_id
                }
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
            response = self.session.post(
                f"{self.base_url}/magic/web/resource/delete",
                data={'id': resource_id}
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
            src_id: 源资源ID
            target_group_id: 目标分组ID

        Returns:
            移动成功返回True，失败返回False
        """
        try:
            response = self.session.post(
                f"{self.base_url}/magic/web/resource/move",
                data={
                    'src': src_id,
                    'groupId': target_group_id
                }
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1 and result.get('data'):
                    print(f"✅ 移动资源成功: {src_id} -> {target_group_id}")
                    return True
                else:
                    print(f"❌ 移动资源失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
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
                    print(f"❌ 获取文件详情失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 获取文件详情时出错: {e}")

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
            response = self.session.post(
                f"{self.base_url}/magic/web/resource/lock",
                data={'id': resource_id}
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
            response = self.session.post(
                f"{self.base_url}/magic/web/resource/unlock",
                data={'id': resource_id}
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

    def save_api_file(self, group_id: str, api_data: Dict, auto_save: bool = False) -> Optional[str]:
        """
        保存API文件
        基于 MagicResourceController.saveFile 实现

        Args:
            group_id: 分组ID
            api_data: API数据，包含name、method、path、script等字段
            auto_save: 是否自动保存

        Returns:
            保存成功返回文件ID，失败返回None
        """
        try:
            # 验证必要字段
            required_fields = ['name', 'method', 'path', 'script']
            for field in required_fields:
                if field not in api_data:
                    print(f"❌ 缺少必要字段: {field}")
                    return None

            # 将API数据转换为JSON字符串
            api_json = json.dumps(api_data, ensure_ascii=False)
            print(f"📝 保存API文件请求数据: {api_json[:100]}...")

            # 使用application/octet-stream类型发送
            response = self.session.post(
                f"{self.base_url}/magic/web/resource/file/api/save",
                data=api_json.encode('utf-8'),
                params={
                    'groupId': group_id,
                    'auto': '1' if auto_save else '0'
                },
                headers={'Content-Type': 'application/octet-stream'}
            )

            # 如果失败，尝试另一种格式
            if response.status_code != 200 or (response.status_code == 200 and response.json().get('code') != 1):
                print(f"⚠️  第一次尝试失败，尝试使用POST参数格式...")
                response = self.session.post(
                    f"{self.base_url}/magic/web/resource/file/api/save",
                    data={
                        'groupId': group_id,
                        'name': api_data['name'],
                        'method': api_data['method'],
                        'path': api_data['path'],
                        'script': api_data['script'],
                        'auto': '1' if auto_save else '0'
                    }
                )

            print(f"📊 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    file_id = result.get('data')
                    print(f"✅ 保存API文件成功: {api_data['name']} (ID: {file_id})")
                    return file_id
                else:
                    print(f"❌ 保存API文件失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ 保存API文件时出错: {e}")

        return None

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
                group_info = {
                    'id': node_info.get('id'),
                    'name': node_info.get('name'),
                    'type': folder_type,
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
