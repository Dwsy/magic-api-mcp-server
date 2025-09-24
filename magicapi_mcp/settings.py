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


@dataclass(slots=True)
class MagicAPISettings:
    """封装 Magic-API 服务相关的环境配置。"""

    base_url: str = DEFAULT_BASE_URL
    ws_url: str = DEFAULT_WS_URL
    username: str | None = None
    password: str | None = None
    token: str | None = None
    auth_enabled: bool = False
    timeout_seconds: float = DEFAULT_TIMEOUT
    log_level: str = DEFAULT_LOG_LEVEL
    transport: str = DEFAULT_TRANSPORT

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

        timeout_raw = env.get("MAGIC_API_TIMEOUT_SECONDS")
        try:
            timeout_seconds = float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT
        except (TypeError, ValueError):
            timeout_seconds = DEFAULT_TIMEOUT

        return cls(
            base_url=base_url,
            ws_url=ws_url,
            username=username,
            password=password,
            token=token,
            auth_enabled=auth_enabled,
            timeout_seconds=timeout_seconds,
            log_level=log_level,
            transport=transport,
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
