"""通用响应工具函数。"""

from __future__ import annotations

from typing import Any, Dict


def error_response(code: Any, message: str, detail: Any | None = None) -> Dict[str, Any]:
    """按照 MCP 约定封装错误响应。"""
    payload: Dict[str, Any] = {"code": code, "message": message}
    if detail is not None:
        payload["detail"] = detail
    return {"error": payload}
