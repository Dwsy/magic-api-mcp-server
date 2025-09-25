"""WebSocket 相关通用工具函数。"""

from __future__ import annotations

from typing import Optional

from magicapi_tools.utils.extractor import find_api_detail_by_path
from magicapi_tools.utils.http_client import MagicAPIHTTPClient


def resolve_script_id_by_path(http_client: MagicAPIHTTPClient, path: str) -> Optional[str]:
    """根据接口路径解析脚本 ID。"""
    try:
        details = find_api_detail_by_path(path, client=http_client, fuzzy=False)
    except Exception:
        return None
    if not details:
        return None
    record = details[0]
    if isinstance(record, dict):
        meta = record.get("meta") or {}
        if isinstance(meta, dict):
            value = meta.get("id")
            return str(value) if value else None
        detail = record.get("detail") or {}
        if isinstance(detail, dict):
            value = detail.get("id")
            return str(value) if value else None
    return None


def normalize_breakpoints(breakpoints) -> str:
    """将断点集合或序列格式化为请求头所需字符串。"""
    if not breakpoints:
        return ""
    return ",".join(str(int(line)) for line in sorted({int(line) for line in breakpoints}))


__all__ = ["resolve_script_id_by_path", "normalize_breakpoints"]
