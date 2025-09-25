"""Magic-API 资源树提取与查询工具函数。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .http_client import MagicAPIHTTPClient


class MagicAPIExtractorError(RuntimeError):
    """资源树提取或解析失败时抛出的异常。"""


@dataclass(slots=True)
class ResourceTree:
    raw: Dict[str, Any]

    @property
    def api_nodes(self) -> Iterable[Dict[str, Any]]:
        api_data = self.raw.get("api", {})
        return api_data.get("children", []) or []


def _clean_path(path: str) -> str:
    if not path:
        return ""
    path = path.strip("/")
    while "//" in path:
        path = path.replace("//", "/")
    return path


def _traverse_api_tree(node: Dict[str, Any], parent_path: str, results: List[str]) -> None:
    node_info = node.get("node", {})
    current_path = node_info.get("path", "")
    method = node_info.get("method")
    name = node_info.get("name", "")

    if current_path and parent_path:
        full_path = f"{parent_path}/{current_path}"
    elif current_path:
        full_path = current_path
    else:
        full_path = parent_path

    full_path = _clean_path(full_path)

    if method and full_path:
        display = f"{method} {full_path}"
        if name and name != current_path:
            display += f" [{name}]"
        results.append(display)

    for child in node.get("children", []) or []:
        _traverse_api_tree(child, full_path, results)


def _normalize_path(path: str) -> str:
    return _clean_path(path)


def _find_api_by_path(node: Dict[str, Any], target_path: str, parent_path: str, results: List[Dict[str, Any]]) -> None:
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

    full_path = _clean_path(full_path)
    normalized_target = _normalize_path(target_path)

    if method and full_path and api_id:
        normalized_full_path = _normalize_path(full_path)
        if (
            normalized_full_path == normalized_target
            or normalized_full_path.startswith(normalized_target + "/")
            or normalized_target.startswith(normalized_full_path + "/")
        ):
            results.append({
                "id": api_id,
                "path": full_path,
                "method": method,
                "name": name,
                "groupId": node_info.get("groupId"),
            })

    for child in node.get("children", []) or []:
        _find_api_by_path(child, target_path, full_path, results)


def load_resource_tree(
    source: Optional[str] = None,
    *,
    client: Optional[MagicAPIHTTPClient] = None,
) -> ResourceTree:
    """加载资源树数据。"""
    if client is not None:
        ok, payload = client.resource_tree()
        if not ok:
            raise MagicAPIExtractorError(payload)
        return ResourceTree(raw=payload or {})

    if not source:
        raise MagicAPIExtractorError("必须提供资源树数据源或 HTTP 客户端")

    path = Path(source)
    if not path.exists():
        raise MagicAPIExtractorError(f"找不到资源文件: {source}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MagicAPIExtractorError(f"JSON 解析失败: {exc}") from exc

    return ResourceTree(raw=data.get("data", {}))


def extract_api_endpoints(tree: ResourceTree) -> List[str]:
    results: List[str] = []
    for child in tree.api_nodes:
        _traverse_api_tree(child, "", results)
    return sorted(results)


def find_api_id_by_path(tree: ResourceTree, target_path: str) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for child in tree.api_nodes:
        _find_api_by_path(child, target_path, "", matches)
    return matches


def find_api_detail_by_path(
    path: str,
    *,
    client: MagicAPIHTTPClient,
    fuzzy: bool = True,
) -> List[Dict[str, Any]]:
    """通过路径获取接口详情列表。"""
    tree = load_resource_tree(client=client)
    matches = find_api_id_by_path(tree, path)
    if not matches:
        return []

    details: List[Dict[str, Any]] = []
    for match in matches:
        file_id = match.get("id")
        if not file_id:
            continue
        ok, payload = client.api_detail(file_id)
        if ok:
            details.append({"meta": match, "detail": payload})
        else:
            details.append({"meta": match, "error": payload})
        if not fuzzy:
            break
    return details


def filter_endpoints(
    endpoints: List[str],
    *,
    path_filter: Optional[str] = None,
    name_filter: Optional[str] = None,
    method_filter: Optional[str] = None,
    query_filter: Optional[str] = None,
) -> List[str]:
    filtered = endpoints

    if method_filter:
        method_filter = method_filter.upper()
        filtered = [ep for ep in filtered if ep.startswith(f"{method_filter} ")]

    if query_filter:
        try:
            pattern = re.compile(query_filter, re.IGNORECASE)
        except re.error as exc:
            raise MagicAPIExtractorError(f"查询过滤器正则错误: {exc}") from exc
        filtered = [
            ep for ep in filtered
            if pattern.search(ep.split(" ", 1)[1]) or (pattern.search(ep) if "[" in ep else False)
        ]

    if path_filter:
        try:
            pattern = re.compile(path_filter, re.IGNORECASE)
        except re.error as exc:
            raise MagicAPIExtractorError(f"路径过滤器正则错误: {exc}") from exc
        filtered = [ep for ep in filtered if pattern.search(ep.split(" ", 1)[1])]

    if name_filter:
        try:
            pattern = re.compile(name_filter, re.IGNORECASE)
        except re.error as exc:
            raise MagicAPIExtractorError(f"名称过滤器正则错误: {exc}") from exc
        filtered = [ep for ep in filtered if "[" in ep and pattern.search(ep)]

    return filtered


def _flatten_tree(
    tree_data: Mapping[str, Any],
    allowed_types: List[str],
    max_depth: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """展平资源树结构为节点列表。"""
    nodes: List[Dict[str, Any]] = []

    def walk(children: List[Mapping[str, Any]], depth: int) -> None:
        if max_depth is not None and depth > max_depth:
            return
        for child in children or []:
            node_info = child.get("node", {})
            node_type = node_info.get("type")
            method = node_info.get("method")
            path = node_info.get("path")
            full_path = node_info.get("full_path", path)  # 优先使用full_path
            name = node_info.get("name")
            file_id = node_info.get("id")

            # 确定节点类型：优先使用原始类型，但要根据是否有子节点调整为分组类型
            has_children = child.get("children") and len(child["children"]) > 0

            if has_children:
                # 有子节点的一定是分组
                final_type = f"{folder_type}-group" if folder_type else "unknown-group"
            elif node_type:
                # 有原始类型但没有子节点，使用原始类型
                final_type = node_type
            elif method:
                # 有method的是API端点
                final_type = "api"
            else:
                # 既没有type也没有method也没有子节点
                final_type = folder_type or "unknown"

            entry = {
                "name": name,
                "type": final_type,
                "path": full_path,  # 使用完整路径
                "method": method,
                "id": file_id,
                "original_path": path,  # 保留原始路径以备后用
            }
            # 过滤逻辑：检查节点是否应该被包含
            should_include = False
            if allowed_types == ["all"]:
                should_include = True
            elif entry["type"] in allowed_types:
                should_include = True
            elif method and "api" in allowed_types:
                should_include = True

            # 特殊规则：如果节点既没有method也没有子节点，则不包含（除非它是分组）
            if should_include and not method:
                has_children = child.get("children") and len(child["children"]) > 0
                if not has_children:
                    should_include = False

            if should_include:
                nodes.append(entry)

            child_children = child.get("children", [])
            if child_children:
                walk(child_children, depth + 1)

    for folder_type, subtree in tree_data.items():
        if allowed_types != ["all"] and folder_type not in allowed_types:
            continue
        root_children = subtree.get("children", []) if isinstance(subtree, Mapping) else []
        walk(root_children, depth=1)

    return nodes


def _filter_nodes(
    nodes: List[Dict[str, Any]],
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """过滤节点列表。"""
    if not search:
        return nodes
    try:
        pattern = re.compile(search, re.IGNORECASE)
        return [
            node for node in nodes
            if (node.get("name") and pattern.search(node["name"]))
            or (node.get("path") and pattern.search(node["path"]))
        ]
    except re.error:
        term = search.lower()
        return [
            node for node in nodes
            if term in (node.get("name") or "").lower()
            or term in (node.get("path") or "").lower()
        ]


def _nodes_to_csv(nodes: List[Dict[str, Any]]) -> str:
    """将节点列表转换为CSV格式。"""
    if not nodes:
        return ""
    headers = ["name", "path", "method", "type", "id", "full_path"]
    rows = [",".join(headers)]
    for node in nodes:
        row = []
        for key in headers:
            if key == "full_path":
                # full_path是新加的字段，可能不存在，使用path作为后备
                value = node.get(key, node.get("path"))
            else:
                value = node.get(key)
            text = "" if value is None else str(value)
            if "," in text or '"' in text:
                text = '"' + text.replace('"', '""') + '"'
            row.append(text)
        rows.append(",".join(row))
    return "\n".join(rows)


def format_file_detail(file_data: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=== API接口详情 ===")
    lines.append(f"ID: {file_data.get('id', 'N/A')}")
    lines.append(f"名称: {file_data.get('name', 'N/A')}")
    lines.append(f"路径: {file_data.get('path', 'N/A')}")
    lines.append(f"方法: {file_data.get('method', 'N/A')}")
    lines.append(f"分组ID: {file_data.get('groupId', 'N/A')}")
    lines.append("")

    script = file_data.get("script", "")
    lines.append("=== 脚本内容 ===")
    lines.append(script or "(无脚本内容)")
    lines.append("")

    lines.append("=== 元数据信息 ===")
    lines.append(f"创建时间: {file_data.get('createTime', 'N/A')}")
    lines.append(f"更新时间: {file_data.get('updateTime', 'N/A')}")
    lines.append(f"创建者: {file_data.get('createBy', 'N/A')}")
    lines.append(f"更新者: {file_data.get('updateBy', 'N/A')}")

    description = file_data.get("description")
    if description:
        lines.append("=== 接口描述 ===")
        lines.append(description)
        lines.append("")

    def _format_items(title: str, items: Optional[List[Dict[str, Any]]]) -> None:
        if not items:
            return
        lines.append(title)
        for item in items:
            required = "✓" if item.get("required", False) else "○"
            lines.append(
                f"  {required} {item.get('name', '')}: {item.get('value', '')} "
                f"({item.get('dataType', 'String')})"
            )
        lines.append("")

    _format_items("请求头 (Headers):", file_data.get("headers"))
    _format_items("路径参数 (Path Parameters):", file_data.get("paths"))
    _format_items("查询参数 (Query Parameters):", file_data.get("parameters"))

    request_body = file_data.get("requestBody")
    if request_body:
        lines.append("请求体 (Request Body):")
        if isinstance(request_body, str):
            lines.append(request_body)
        else:
            lines.append(json.dumps(request_body, ensure_ascii=False, indent=2))
        lines.append("")

    properties = file_data.get("properties", {})
    if properties:
        lines.append("属性配置 (Properties):")
        for key, value in properties.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

    options = file_data.get("options", [])
    if options:
        lines.append("选项配置 (Options):")
        for option in options:
            lines.append(f"  {option}")
        lines.append("")

    for key, value in file_data.items():
        if key in {
            "id",
            "name",
            "path",
            "method",
            "groupId",
            "script",
            "createTime",
            "updateTime",
            "createBy",
            "updateBy",
            "description",
            "headers",
            "paths",
            "parameters",
            "requestBody",
            "properties",
            "options",
        }:
            continue
        if isinstance(value, (list, dict)) and not value:
            continue
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


__all__ = [
    "MagicAPIExtractorError",
    "ResourceTree",
    "load_resource_tree",
    "extract_api_endpoints",
    "find_api_id_by_path",
    "find_api_detail_by_path",
    "filter_endpoints",
    "format_file_detail",
    "_flatten_tree",
    "_filter_nodes",
    "_nodes_to_csv",
]
