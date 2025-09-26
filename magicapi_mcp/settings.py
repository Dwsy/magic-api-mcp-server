"""通用 Magic-API 环境配置解析。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, MutableMapping, Optional


def _get_env(env: Mapping[str, str], key: str, default: str) -> str:
    return env.get(key, default)


def _str_to_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_BASE_URL = "http://127.0.0.1:10712"
DEFAULT_WS_URL = "ws://127.0.0.1:10712/magic/web/console"
DEFAULT_TIMEOUT = 30.0
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_TRANSPORT = "stdio"
DEFAULT_WS_LOG_HISTORY_SIZE = 500
DEFAULT_WS_LOG_CAPTURE_WINDOW = 2
DEFAULT_WS_RECONNECT_INTERVAL = 5.0
DEFAULT_DEBUG_TIMEOUT = 600.0

# API响应相关默认配置
DEFAULT_SUCCESS_CODE = 1
DEFAULT_SUCCESS_MESSAGE = "success"
DEFAULT_INVALID_CODE = 0
DEFAULT_EXCEPTION_CODE = -1


@dataclass(slots=True)
class MagicAPISettings:
    """封装 Magic-API 服务相关的环境配置。"""

    base_url: str = DEFAULT_BASE_URL
    ws_url: str = DEFAULT_WS_URL
    username: str | None = None
    password: str | None = None
    token: str | None = 'unauthorization'
    auth_enabled: bool = False
    timeout_seconds: float = DEFAULT_TIMEOUT
    debug_timeout_seconds: float = DEFAULT_DEBUG_TIMEOUT
    log_level: str = DEFAULT_LOG_LEVEL
    transport: str = DEFAULT_TRANSPORT
    ws_auto_start: bool = True
    ws_log_history_size: int = DEFAULT_WS_LOG_HISTORY_SIZE
    ws_log_capture_window: float = DEFAULT_WS_LOG_CAPTURE_WINDOW
    ws_reconnect_interval: float = DEFAULT_WS_RECONNECT_INTERVAL

    # API响应状态码配置（支持自定义状态码）
    api_success_code: int = DEFAULT_SUCCESS_CODE
    api_success_message: str = DEFAULT_SUCCESS_MESSAGE
    api_invalid_code: int = DEFAULT_INVALID_CODE
    api_exception_code: int = DEFAULT_EXCEPTION_CODE

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "MagicAPISettings":
        """从环境变量加载配置。"""
        env = env or os.environ
        base_url = _get_env(env, "MAGIC_API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        ws_url = _get_env(env, "MAGIC_API_WS_URL", DEFAULT_WS_URL)
        username = env.get("MAGIC_API_USERNAME") or None
        password = env.get("MAGIC_API_PASSWORD") or None
        token = env.get("MAGIC_API_TOKEN") or None
        auth_enabled = _str_to_bool(env.get("MAGIC_API_AUTH_ENABLED"))
        log_level = env.get("LOG_LEVEL", DEFAULT_LOG_LEVEL)
        transport = env.get("FASTMCP_TRANSPORT", DEFAULT_TRANSPORT)
        ws_auto_start = _str_to_bool(env.get("MAGIC_API_WS_AUTO_START", "1"))
        ws_history_size = env.get("MAGIC_API_WS_LOG_HISTORY_SIZE")
        ws_capture_window_raw = env.get("MAGIC_API_WS_CAPTURE_WINDOW")
        ws_reconnect_raw = env.get("MAGIC_API_WS_RECONNECT_INTERVAL")
        debug_timeout_raw = env.get("MAGIC_API_DEBUG_TIMEOUT_SECONDS")

        # API响应状态码配置
        api_success_code_raw = env.get("MAGIC_API_SUCCESS_CODE")
        api_success_message = env.get("MAGIC_API_SUCCESS_MESSAGE", DEFAULT_SUCCESS_MESSAGE)
        api_invalid_code_raw = env.get("MAGIC_API_INVALID_CODE")
        api_exception_code_raw = env.get("MAGIC_API_EXCEPTION_CODE")

        timeout_raw = env.get("MAGIC_API_TIMEOUT_SECONDS")
        try:
            timeout_seconds = float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT
        except (TypeError, ValueError):
            timeout_seconds = DEFAULT_TIMEOUT

        try:
            ws_log_history_size = int(ws_history_size) if ws_history_size else DEFAULT_WS_LOG_HISTORY_SIZE
        except (TypeError, ValueError):
            ws_log_history_size = DEFAULT_WS_LOG_HISTORY_SIZE

        try:
            ws_log_capture_window = float(ws_capture_window_raw) if ws_capture_window_raw else DEFAULT_WS_LOG_CAPTURE_WINDOW
        except (TypeError, ValueError):
            ws_log_capture_window = DEFAULT_WS_LOG_CAPTURE_WINDOW

        try:
            ws_reconnect_interval = float(ws_reconnect_raw) if ws_reconnect_raw else DEFAULT_WS_RECONNECT_INTERVAL
        except (TypeError, ValueError):
            ws_reconnect_interval = DEFAULT_WS_RECONNECT_INTERVAL

        try:
            debug_timeout_seconds = float(debug_timeout_raw) if debug_timeout_raw else DEFAULT_DEBUG_TIMEOUT
        except (TypeError, ValueError):
            debug_timeout_seconds = DEFAULT_DEBUG_TIMEOUT

        # 解析API响应状态码
        try:
            api_success_code = int(api_success_code_raw) if api_success_code_raw else DEFAULT_SUCCESS_CODE
        except (TypeError, ValueError):
            api_success_code = DEFAULT_SUCCESS_CODE

        try:
            api_invalid_code = int(api_invalid_code_raw) if api_invalid_code_raw else DEFAULT_INVALID_CODE
        except (TypeError, ValueError):
            api_invalid_code = DEFAULT_INVALID_CODE

        try:
            api_exception_code = int(api_exception_code_raw) if api_exception_code_raw else DEFAULT_EXCEPTION_CODE
        except (TypeError, ValueError):
            api_exception_code = DEFAULT_EXCEPTION_CODE

        return cls(
            base_url=base_url,
            ws_url=ws_url,
            username=username,
            password=password,
            token=token,
            auth_enabled=auth_enabled,
            timeout_seconds=timeout_seconds,
            debug_timeout_seconds=debug_timeout_seconds,
            log_level=log_level,
            transport=transport,
            ws_auto_start=ws_auto_start,
            ws_log_history_size=ws_log_history_size,
            ws_log_capture_window=ws_log_capture_window,
            ws_reconnect_interval=ws_reconnect_interval,
            api_success_code=api_success_code,
            api_success_message=api_success_message,
            api_invalid_code=api_invalid_code,
            api_exception_code=api_exception_code,
        )

    def inject_auth(self, headers: MutableMapping[str, str]) -> MutableMapping[str, str]:
        """根据配置向请求头注入认证信息。"""
        if not self.auth_enabled:
            return headers

        if self.token:
            headers.setdefault("Authorization", f"Bearer {self.token}")
            headers.setdefault("Magic-Token", self.token)

        if self.username and self.password:
            headers.setdefault("Magic-Username", self.username)
            headers.setdefault("Magic-Password", self.password)

        return headers

    def to_requests_kwargs(self) -> dict:
        """生成 requests 调用所需的关键参数。"""
        headers: dict[str, str] = {
            "User-Agent": "magicapi-tools/1.0",
            "Accept": "application/json",
        }
        self.inject_auth(headers)

        return {
            "timeout": self.timeout_seconds,
            "headers": headers,
        }


DEFAULT_SETTINGS = MagicAPISettings.from_env()
"""默认按照当前进程环境解析的配置实例。"""
