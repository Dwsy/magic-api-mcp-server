"""WebSocket 消息类型与解析工具。"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from magicapi_tools.logging_config import get_logger


_logger = get_logger("ws.messages")


class MessageType(str, Enum):
    """Magic-API WebSocket 消息类型枚举。"""

    LOG = "LOG"
    LOGS = "LOGS"
    BREAKPOINT = "BREAKPOINT"
    EXCEPTION = "EXCEPTION"
    LOGIN_RESPONSE = "LOGIN_RESPONSE"
    REFRESH_TOKEN = "REFRESH_TOKEN"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    ONLINE_USERS = "ONLINE_USERS"
    INTO_FILE_ID = "INTO_FILE_ID"
    SET_FILE_ID = "SET_FILE_ID"
    PING = "PING"
    PONG = "PONG"
    LOGIN = "LOGIN"
    SET_BREAKPOINT = "SET_BREAKPOINT"
    RESUME_BREAKPOINT = "RESUME_BREAKPOINT"
    SEND_ONLINE = "SEND_ONLINE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_raw(cls, value: str) -> "MessageType":
        """将原始字符串映射到 `MessageType`。"""
        normalized = value.strip().upper()
        return cls.__members__.get(normalized, cls.UNKNOWN)


@dataclass(slots=True)
class WSMessage:
    """结构化的 WebSocket 消息。"""

    type: MessageType
    raw: str
    payload: Any = None
    text: str = ""
    timestamp: float = field(default_factory=lambda: time.time())
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """确保 `timestamp` 与 `text` 有默认值。"""
        if not self.text and isinstance(self.payload, str):
            self.text = self.payload


def parse_ws_message(raw: str) -> WSMessage:
    """解析原始 WebSocket 文本消息为 `WSMessage`。"""

    ts = time.time()
    stripped = raw.strip()
    if not stripped:
        return WSMessage(type=MessageType.UNKNOWN, raw=raw, text="", timestamp=ts)

    msg_type, remainder = _split_once(stripped)
    message_type = MessageType.from_raw(msg_type)

    payload: Any = None
    text = remainder
    data: Dict[str, Any] = {}

    if message_type == MessageType.LOG:
        payload = remainder
        text = remainder
        data["logs"] = [remainder] if remainder else []

    elif message_type == MessageType.LOGS:
        payload = _parse_json_safely(remainder, fallback=remainder)
        if isinstance(payload, list):
            data["logs"] = payload
            text = "\n".join(str(item) for item in payload)
        else:
            text = remainder
            data["logs"] = [payload]

    elif message_type == MessageType.LOGIN_RESPONSE:
        status_raw, extra = _split_once(remainder)
        data["status_raw"] = status_raw
        try:
            data["status"] = int(status_raw)
        except (TypeError, ValueError):
            pass
        payload = _parse_json_safely(extra) if extra else None
        data["user"] = payload
        if isinstance(payload, dict):
            client_id = payload.get("clientId") or payload.get("client_id")
            if client_id:
                data["client_id"] = str(client_id)
        if payload:
            text = f"登录状态: {data.get('status', status_raw)}"
        else:
            text = f"登录状态: {status_raw}"

    elif message_type in {MessageType.USER_LOGIN, MessageType.USER_LOGOUT, MessageType.ONLINE_USERS,
                          MessageType.REFRESH_TOKEN, MessageType.SEND_ONLINE}:
        payload = _parse_json_safely(remainder, fallback=remainder)
        data["payload"] = payload
        if isinstance(payload, dict):
            client_id = payload.get("clientId") or payload.get("client_id")
            if client_id:
                data["client_id"] = str(client_id)
        text = _format_json_summary(payload) if isinstance(payload, (dict, list)) else remainder

    elif message_type in {MessageType.SET_FILE_ID, MessageType.INTO_FILE_ID}:
        file_id, extra = _split_once(remainder)
        data["file_id"] = file_id
        payload = _parse_json_safely(extra) if extra else None
        if payload:
            data["payload"] = payload
            client_id = _extract_client_from_payload(payload)
            if client_id:
                data["client_id"] = client_id
            text = f"文件切换 -> {file_id}"
        else:
            text = file_id

    elif message_type == MessageType.BREAKPOINT:
        # 消息格式: BREAKPOINT,script_id,{json_data}
        if ',' in remainder:
            script_id, json_str = remainder.split(',', 1)
        else:
            script_id = '未知'
            json_str = remainder

        data["script_id"] = script_id
        payload = _parse_json_safely(json_str, fallback=json_str)
        data["payload"] = payload

        # 提取断点信息
        line_info = None
        if isinstance(payload, dict):
            variables = payload.get('variables', [])
            range_info = payload.get('range', [])
            data["variables"] = variables
            data["range"] = range_info

            headers = _extract_header_from_variables(variables)
            if headers:
                data["headers"] = headers
                client_from_header = headers.get("magic-request-client-id")
                if client_from_header:
                    data["client_id"] = str(client_from_header)
            if not data.get("client_id"):
                client_id = payload.get("clientId") or payload.get("client_id")
                if client_id:
                    data["client_id"] = str(client_id)

            # 从range信息提取行号 [start_line, start_col, end_line, end_col]
            if isinstance(range_info, (list, tuple)) and len(range_info) >= 1:
                line_info = range_info[0]

        text = f"断点命中 @ {script_id}"
        if line_info is not None:
            text = f"断点命中 @ {script_id}: 行 {line_info}"

    elif message_type == MessageType.EXCEPTION:
        payload = _parse_json_safely(remainder, fallback=remainder)
        data["payload"] = payload
        if isinstance(payload, dict):
            headers = payload.get("headers")
            if headers:
                parsed_headers = _parse_object_like(headers)
                if parsed_headers:
                    data["headers"] = parsed_headers
                    client_from_header = parsed_headers.get("magic-request-client-id")
                    if client_from_header:
                        data["client_id"] = str(client_from_header)
            message = payload.get("message") or payload.get("msg")
            text = f"异常: {message}" if message else "异常"
        else:
            text = str(payload)

    elif message_type in {MessageType.PING, MessageType.PONG}:
        text = message_type.value
        payload = None

    else:
        payload = remainder or None
        text = remainder

    return WSMessage(
        type=message_type,
        raw=raw,
        payload=payload,
        text=text,
        timestamp=ts,
        data=data,
    )


def _split_once(value: str) -> Tuple[str, str]:
    """按首个逗号拆分字符串。"""
    if not value:
        return "", ""
    if "," not in value:
        return value, ""
    head, tail = value.split(",", 1)
    return head, tail


def _parse_json_safely(raw: str, fallback: Any = None) -> Any:
    """尝试解析 JSON，失败时返回 `fallback`。"""
    if raw is None:
        return fallback
    text = raw.strip()
    if not text:
        return fallback
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return fallback


def _format_json_summary(payload: Any) -> str:
    """为 JSON 数据生成简要说明，避免输出过长。"""
    if payload is None:
        return ""
    if isinstance(payload, dict):
        keys = ", ".join(list(payload.keys())[:5])
        return f"{len(payload)} 字段: {keys}" if keys else "{}"
    if isinstance(payload, list):
        return f"列表，共 {len(payload)} 项"
    return str(payload)


def _extract_client_from_payload(payload: Any) -> Optional[str]:
    if isinstance(payload, dict):
        for key in ("clientId", "client_id", "id"):
            value = payload.get(key)
            if value:
                return str(value)
    return None


def _extract_header_from_variables(variables: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(variables, list):
        return None
    for item in variables:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name and name.lower() == "header":
            value = item.get("value")
            headers = _parse_object_like(value)
            if headers:
                return headers
    return None


def _parse_object_like(value: Any) -> Optional[Dict[str, Any]]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    # 去除外层引号
    if text.startswith('"') and text.endswith('"'):
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            text = text[1:-1]
            text = text.encode('utf-8').decode('unicode_escape')
    if text.startswith('{') and text.endswith('}'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            _logger.debug("解析 header JSON 失败", exc_info=True)
            return None
    return None


__all__ = ["MessageType", "WSMessage", "parse_ws_message"]
