"""WebSocket 环境状态管理。"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Iterable, List, Optional, Protocol, Tuple

from magicapi_tools.logging_config import get_logger

from .messages import MessageType, WSMessage


class ResourceResolver(Protocol):
    """资源解析协议，按需加载接口/脚本元数据。"""

    def resolve_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        ...


@dataclass(slots=True)
class OpenFileContext:
    """记录 IDE 环境当前打开的文件上下文。"""

    file_id: str
    resolved_at: float = field(default_factory=lambda: time.time())
    method: Optional[str] = None
    path: Optional[str] = None
    name: Optional[str] = None
    group_chain: Optional[List[str]] = None
    detail: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    last_breakpoint_range: Optional[List[int]] = None
    last_variables: Optional[List[Dict[str, Any]]] = None


@dataclass(slots=True)
class IDEEnvironment:
    """按登录 IP 聚合的 IDE 环境。"""

    ide_key: str
    primary_ip: str
    client_ids: set[str] = field(default_factory=set)
    latest_user: Optional[Dict[str, Any]] = None
    opened_files: Dict[str, OpenFileContext] = field(default_factory=dict)
    last_active_at: float = field(default_factory=lambda: time.time())

    def touch(self) -> None:
        self.last_active_at = time.time()

    def upsert_client(self, client_id: str) -> None:
        self.client_ids.add(client_id)
        self.touch()

    def set_user(self, user_info: Dict[str, Any]) -> None:
        self.latest_user = user_info
        self.touch()

    def set_open_file(self, client_id: str, file_ctx: OpenFileContext) -> None:
        self.opened_files[client_id] = file_ctx
        self.upsert_client(client_id)


class LogBuffer:
    """保存最近的 WebSocket 消息。"""

    def __init__(self, maxlen: int = 500):
        self._buffer: Deque[Tuple[float, WSMessage]] = deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def append(self, message: WSMessage) -> None:
        with self._lock:
            self._buffer.append((message.timestamp, message))

    def __len__(self) -> int:  # pragma: no cover - 简单代理
        with self._lock:
            return len(self._buffer)

    def iter_recent(self, limit: Optional[int] = None) -> Iterable[WSMessage]:
        with self._lock:
            items = list(self._buffer)
        if limit is not None:
            items = items[-limit:]
        for _, msg in items:
            yield msg

    def between(self, start_ts: float, end_ts: float) -> List[WSMessage]:
        with self._lock:
            return [msg for ts, msg in self._buffer if start_ts <= ts <= end_ts]

    def window(self, center_ts: float, pre: float = 0.1, post: float = 0.1) -> List[WSMessage]:
        start = center_ts - pre
        end = center_ts + post
        return self.between(start, end)


class EnvironmentState:
    """管理 IDE 环境与客户端状态。"""

    def __init__(self, resource_resolver: Optional[ResourceResolver] = None):
        self._resource_resolver = resource_resolver
        self._environments: Dict[str, IDEEnvironment] = {}
        self._client_to_env: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._primary_client_id: Optional[str] = None
        self._logger = get_logger("ws.state")
        self._log_debug = self._logger.isEnabledFor(10)

    # ------------------------------------------------------------------
    # 公共查询接口
    # ------------------------------------------------------------------
    def list_environments(self) -> List[IDEEnvironment]:
        with self._lock:
            return [self._clone_environment(env) for env in self._environments.values()]

    def get_environment(self, ide_key: str) -> Optional[IDEEnvironment]:
        with self._lock:
            env = self._environments.get(ide_key)
            return self._clone_environment(env) if env else None

    def get_environment_by_client(self, client_id: str) -> Optional[IDEEnvironment]:
        with self._lock:
            ide_key = self._client_to_env.get(client_id)
            if not ide_key:
                return None
            env = self._environments.get(ide_key)
            return self._clone_environment(env) if env else None

    # ------------------------------------------------------------------
    # 消息处理入口
    # ------------------------------------------------------------------
    def handle_message(self, message: WSMessage, default_client_id: Optional[str] = None) -> Optional[IDEEnvironment]:
        if self._log_debug:
            self._logger.debug("处理消息: %s", message.type.value)
        handler_map = {
            MessageType.LOGIN_RESPONSE: self._handle_login_response,
            MessageType.USER_LOGIN: self._handle_user_login,
            MessageType.USER_LOGOUT: self._handle_user_logout,
            MessageType.SET_FILE_ID: self._handle_set_file_id,
            MessageType.INTO_FILE_ID: self._handle_set_file_id,
            MessageType.BREAKPOINT: self._handle_breakpoint,
            MessageType.EXCEPTION: self._handle_exception,
        }

        handler = handler_map.get(message.type)
        if handler:
            return handler(message, default_client_id)

        # 非关键信息也需要刷新活跃时间
        key = self._client_to_env.get(self._infer_client_id(message, default_client_id))
        if key and key in self._environments:
            self._environments[key].touch()
            return self._clone_environment(self._environments[key])
        return None

    # ------------------------------------------------------------------
    # 配置
    # ------------------------------------------------------------------
    def set_primary_client(self, client_id: Optional[str]) -> None:
        self._primary_client_id = client_id

    # ------------------------------------------------------------------
    # 具体消息处理
    # ------------------------------------------------------------------
    def _handle_login_response(self, message: WSMessage, default_client_id: Optional[str]) -> Optional[IDEEnvironment]:
        payload = message.data.get("user")
        client_id = message.data.get("client_id")
        if not client_id:
            client_id = self._infer_client_id(message, default_client_id)
        return self._ensure_environment(client_id, payload, default_client_id)

    def _handle_user_login(self, message: WSMessage, default_client_id: Optional[str]) -> Optional[IDEEnvironment]:
        payload = message.data.get("payload")
        client_id = message.data.get("client_id")
        if not client_id:
            client_id = self._infer_client_id(message, default_client_id)
        return self._ensure_environment(client_id, payload, default_client_id)

    def _handle_user_logout(self, message: WSMessage, default_client_id: Optional[str]) -> Optional[IDEEnvironment]:
        payload = message.data.get("payload")
        client_id = message.data.get("client_id")
        if not client_id:
            client_id = self._infer_client_id(message, default_client_id)
        if not client_id:
            return None
        key = self._client_to_env.get(client_id)
        if not key:
            return None
        with self._lock:
            env = self._environments.get(key)
            if not env:
                return None
            env.touch()
            if client_id in env.client_ids:
                env.client_ids.discard(client_id)
            env.opened_files.pop(client_id, None)
            return self._clone_environment(env)

    def _handle_set_file_id(self, message: WSMessage, default_client_id: Optional[str]) -> Optional[IDEEnvironment]:
        file_id = message.data.get("file_id") or (message.payload if isinstance(message.payload, str) else None)
        client_id = message.data.get("client_id") or self._extract_client_id_from_payload(message.payload)
        if not client_id:
            client_id = self._infer_client_id(message, default_client_id)
        if not file_id or not client_id:
            return None

        detail = self._resolve_file_detail(file_id)
        file_ctx = OpenFileContext(
            file_id=file_id,
            detail=detail,
            method=_safe_get(detail, "method"),
            path=_safe_get(detail, "path"),
            name=_safe_get(detail, "name"),
            group_chain=_build_group_chain(detail),
        )

        env = self._ensure_environment(client_id, None, default_client_id)
        if env:
            with self._lock:
                real_env = self._environments.get(env.ide_key)
                if real_env:
                    real_env.set_open_file(client_id, file_ctx)
                    return self._clone_environment(real_env)
        return env

    def _handle_breakpoint(self, message: WSMessage, default_client_id: Optional[str]) -> Optional[IDEEnvironment]:
        script_id = message.data.get("script_id")
        client_id = message.data.get("client_id") or self._infer_client_id(message, default_client_id)
        if not client_id:
            return None
        env = self._ensure_environment(client_id, None, default_client_id)
        if env:
            with self._lock:
                real_env = self._environments.get(env.ide_key)
                if real_env:
                    real_env.touch()
                    if script_id:
                        ctx = real_env.opened_files.get(client_id)
                        if not ctx or ctx.file_id != script_id:
                            ctx = OpenFileContext(file_id=script_id)
                            real_env.opened_files[client_id] = ctx
                        range_info = message.data.get("range")
                        if isinstance(range_info, list):
                            ctx.last_breakpoint_range = list(range_info)
                        variables = message.data.get("variables")
                        if isinstance(variables, list):
                            ctx.last_variables = [dict(item) if isinstance(item, dict) else item for item in variables]
                        headers = message.data.get("headers")
                        if isinstance(headers, dict):
                            ctx.headers = dict(headers)
                    return self._clone_environment(real_env)
        return env

    def _handle_exception(self, message: WSMessage, default_client_id: Optional[str]) -> Optional[IDEEnvironment]:
        client_id = message.data.get("client_id") or self._infer_client_id(message, default_client_id)
        if not client_id:
            return None
        env = self._ensure_environment(client_id, None, default_client_id)
        if env:
            with self._lock:
                real_env = self._environments.get(env.ide_key)
                if real_env:
                    real_env.touch()
                    return self._clone_environment(real_env)
        return env

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------
    def _ensure_environment(
        self,
        client_id: Optional[str],
        user_info: Optional[Dict[str, Any]],
        default_client_id: Optional[str],
    ) -> Optional[IDEEnvironment]:
        if not client_id:
            client_id = default_client_id or self._primary_client_id
        if not client_id:
            return None
        ide_key = None
        if isinstance(user_info, dict):
            ide_key = _extract_ip(user_info)
        if not ide_key and client_id:
            ide_key = self._client_to_env.get(client_id)
        if not ide_key:
            ide_key = default_client_id or self._primary_client_id or client_id

        with self._lock:
            env = self._environments.get(ide_key)
            if not env:
                primary_ip = ide_key
                if isinstance(user_info, dict):
                    ip = _extract_ip(user_info)
                    if ip:
                        primary_ip = ip
                env = IDEEnvironment(ide_key=ide_key, primary_ip=primary_ip)
                self._environments[ide_key] = env
                if self._logger.isEnabledFor(20):
                    self._logger.info("创建新的 IDE 环境: %s", ide_key)
            if isinstance(user_info, dict):
                env.set_user(user_info)
                ip = _extract_ip(user_info)
                if ip and env.primary_ip != ip:
                    env.primary_ip = ip
            env.upsert_client(client_id)
            self._client_to_env[client_id] = ide_key
            return self._clone_environment(env)

    def _resolve_file_detail(self, file_id: str) -> Optional[Dict[str, Any]]:
        if not self._resource_resolver:
            return None
        try:
            return self._resource_resolver.resolve_file(file_id)
        except Exception:
            return None

    def _infer_client_id(self, message: WSMessage, default_client_id: Optional[str]) -> Optional[str]:
        client_id = message.data.get("client_id") if isinstance(message.data, dict) else None
        if client_id:
            return str(client_id)
        data = message.data.get("payload") if isinstance(message.data, dict) else None
        if isinstance(data, dict):
            candidate = data.get("clientId") or data.get("client_id")
            if candidate:
                return str(candidate)
        # 登录响应已在上游解析
        if message.data.get("status_raw") and "user" in message.data:
            user_payload = message.data.get("user")
            if isinstance(user_payload, dict):
                candidate = user_payload.get("clientId") or user_payload.get("client_id")
                if candidate:
                    return str(candidate)
        return default_client_id or self._primary_client_id

    def _extract_client_id_from_payload(self, payload: Any) -> Optional[str]:
        if isinstance(payload, dict):
            for key in ("clientId", "client_id", "id"):
                if key in payload and payload[key]:
                    return str(payload[key])
        return None

    def _clone_environment(self, env: Optional[IDEEnvironment]) -> Optional[IDEEnvironment]:
        if env is None:
            return None
        return IDEEnvironment(
            ide_key=env.ide_key,
            primary_ip=env.primary_ip,
            client_ids=set(env.client_ids),
            latest_user=dict(env.latest_user) if isinstance(env.latest_user, dict) else env.latest_user,
            opened_files={cid: OpenFileContext(
                file_id=ctx.file_id,
                resolved_at=ctx.resolved_at,
                method=ctx.method,
                path=ctx.path,
                name=ctx.name,
                group_chain=list(ctx.group_chain) if ctx.group_chain else None,
                detail=dict(ctx.detail) if isinstance(ctx.detail, dict) else ctx.detail,
                headers=dict(ctx.headers) if isinstance(ctx.headers, dict) else ctx.headers,
                last_breakpoint_range=list(ctx.last_breakpoint_range) if isinstance(ctx.last_breakpoint_range, list) else ctx.last_breakpoint_range,
                last_variables=[dict(item) if isinstance(item, dict) else item for item in (ctx.last_variables or [])] if ctx.last_variables else None,
            ) for cid, ctx in env.opened_files.items()},
            last_active_at=env.last_active_at,
        )


def _extract_ip(payload: Dict[str, Any]) -> Optional[str]:
    for key in ("login_ip", "loginIp", "ip", "ipAddress", "remoteIp", "host", "address"):
        value = payload.get(key)
        if value:
            return str(value)
    return None


def _safe_get(detail: Optional[Dict[str, Any]], key: str) -> Optional[str]:
    if isinstance(detail, dict):
        value = detail.get(key)
        if value:
            return str(value)
    return None


def _build_group_chain(detail: Optional[Dict[str, Any]]) -> Optional[List[str]]:
    if not isinstance(detail, dict):
        return None
    chain = detail.get("groupName"), detail.get("groupPath")
    if any(chain):
        return [str(item) for item in chain if item]
    return None


__all__ = [
    "ResourceResolver",
    "OpenFileContext",
    "IDEEnvironment",
    "LogBuffer",
    "EnvironmentState",
]
