"""MCP 工具通用辅助函数。

此模块提供所有工具共享的通用功能函数，包括：
- 路径到ID的转换逻辑
- API查找和匹配算法
- 错误响应格式化
- 资源树处理工具

主要函数：
- path_to_id_impl: 根据路径查找资源ID的实现
- find_api_ids_by_path_impl: 查找路径对应的API ID列表
- find_api_details_by_path_impl: 查找路径对应的API详细信息
- error_response: 统一的错误响应格式化

此模块被其他工具模块导入使用，不直接提供MCP工具。
"""

from __future__ import annotations

from typing import Any, Dict, List

from magicapi_tools.utils.extractor import (
    MagicAPIExtractorError,
    find_api_detail_by_path,
    find_api_id_by_path,
    load_resource_tree,
    _flatten_tree,
)
from magicapi_tools.utils.http_client import MagicAPIHTTPClient
from magicapi_tools.utils import error_response


def path_to_id_impl(http_client: MagicAPIHTTPClient, path: str, fuzzy: bool = True) -> Dict[str, Any]:
    """根据路径查找资源 ID，支持全路径搜索。"""
    try:
        # 使用与 search_endpoints 相同的逻辑获取完整路径信息
        from magicapi_tools.utils.extractor import load_resource_tree
        from magicapi_tools.tools.query import _collect_all_endpoints

        tree = load_resource_tree(client=http_client)
        all_endpoint_details = []
        for child in tree.api_nodes:
            _collect_all_endpoints(child, "", all_endpoint_details)

        # 标准化输入路径
        normalized = path if path.startswith("/") else f"/{path}"
        target_lower = normalized.lower()
        matches: List[Dict[str, Any]] = []

        for detail in all_endpoint_details:
            detail_path = detail.get("path", "")
            detail_id = detail.get("id")
            detail_method = detail.get("method", "")
            detail_name = detail.get("name", "")

            if not detail_path or not detail_id:
                continue

            # 同时检查完整路径和部分路径
            detail_path_lower = detail_path.lower()
            node_path_lower = (detail.get("path") or "").lower()  # 兼容旧逻辑

            # 检查是否匹配
            path_matches = False
            if fuzzy:
                # 模糊匹配：目标路径包含在完整路径中，或者完整路径包含在目标路径中
                path_matches = (target_lower in detail_path_lower or
                               detail_path_lower in target_lower)
            else:
                # 精确匹配
                path_matches = detail_path_lower == target_lower

            if path_matches:
                # 构建匹配结果，包含完整信息
                match = {
                    "id": detail_id,
                    "path": detail_path,  # 完整路径
                    "method": detail_method,
                    "name": detail_name,
                    "groupId": detail.get("groupId"),
                    "type": "api"
                }
                matches.append(match)

        if not matches:
            return error_response("not_found", f"未在资源树中找到路径 {path}")

        return {"path": path, "normalized_path": normalized, "matches": matches}

    except Exception as exc:
        # 如果新逻辑失败，回退到旧逻辑
        ok, payload = http_client.resource_tree()
        if not ok:
            return error_response(payload.get("code"), payload.get("message", "无法获取资源树"), payload.get("detail"))

        nodes = _flatten_tree(payload, ["api"])
        normalized = path if path.startswith("/") else f"/{path}"
        target_lower = normalized.lower()
        matches: List[Dict[str, Any]] = []

        for node in nodes:
            node_path = (node.get("path") or "").lower()
            if not node_path:
                continue
            if (fuzzy and target_lower in node_path) or (not fuzzy and node_path == target_lower):
                matches.append(node)

        if not matches:
            return error_response("not_found", f"未在资源树中找到路径 {path}")

        return {"path": path, "normalized_path": normalized, "matches": matches}


def find_api_ids_by_path_impl(http_client: MagicAPIHTTPClient, path: str, limit: int = 10) -> Dict[str, Any]:
    """查找路径对应的 API ID 列表。"""
    try:
        tree = load_resource_tree(client=http_client)
        matches = find_api_id_by_path(tree, path)
        if not matches:
            return error_response("not_found", f"未找到路径为 '{path}' 的 API 端点")

        # 应用 limit 限制
        original_count = len(matches)
        if limit > 0:
            matches = matches[:limit]

        return {
            "path": path,
            "total_count": original_count,
            "returned_count": len(matches),
            "limit": limit,
            "matches": matches
        }
    except MagicAPIExtractorError as exc:
        return error_response("extraction_error", f"查找API ID失败: {exc}")


def find_api_details_by_path_impl(http_client: MagicAPIHTTPClient, path: str, fuzzy: bool = True, limit: int = 10) -> Dict[str, Any]:
    """查找路径对应的 API 详情列表。"""
    try:
        details = find_api_detail_by_path(path, client=http_client, fuzzy=fuzzy)
        if not details:
            return error_response("not_found", f"未找到路径为 '{path}' 的 API 端点")

        # 应用 limit 限制
        original_count = len(details)
        if limit > 0:
            details = details[:limit]

        return {
            "path": path,
            "fuzzy": fuzzy,
            "total_count": original_count,
            "returned_count": len(details),
            "limit": limit,
            "results": details
        }
    except MagicAPIExtractorError as exc:
        return error_response("extraction_error", f"查找API详情失败: {exc}")

