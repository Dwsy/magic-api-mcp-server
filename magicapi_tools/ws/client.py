"""低层 WebSocket 客户端实现。"""

from __future__ import annotations

import asyncio
import json
import secrets
from typing import Any, AsyncIterator, Dict, Optional

import websockets

from magicapi_tools.logging_config import get_logger

from .messages import MessageType, WSMessage, parse_ws_message


class WSClient:
    """封装 Magic-API WebSocket 连接的异步客户端。"""

    def __init__(
        self,
        ws_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        reconnect_interval: float = 5.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.ws_url = ws_url
        self.username = username
        self.password = password
        self.token = token or "unauthorization"
        self.reconnect_interval = reconnect_interval
        self.extra_headers = headers or {}

        self.client_id = self._generate_client_id()

        self._websocket: Optional[any] = None
        self._connected = asyncio.Event()
        self._stop = asyncio.Event()
        self._send_lock = asyncio.Lock()
        self._logger = get_logger("ws.client")

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------
    async def iter_messages(self) -> AsyncIterator[WSMessage]:
        """持续迭代 WebSocket 消息，自动处理重连。"""
        while not self._stop.is_set():
            try:
                async with websockets.connect(
                    self.ws_url,
                    additional_headers=self._build_headers(),
                    proxy=None,
                    ping_interval=15,
                    ping_timeout=30,
                    close_timeout=10,
                ) as websocket:
                    self._websocket = websocket
                    self._connected.set()
                    self._logger.info(f"🔌 已连接 WebSocket: {self.ws_url}")
                    await self._send_login()

                    async for raw_message in websocket:
                        message = parse_ws_message(raw_message)
                        if message.type == MessageType.PING:
                            await self.send_text("pong")
                            continue
                        yield message
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover - 网络异常路径
                self._logger.warning(f"WebSocket 连接异常: {exc}")
                self._connected.clear()
                if self._stop.is_set():
                    break
                await asyncio.sleep(self.reconnect_interval)
            finally:
                self._websocket = None
                self._connected.clear()

        self._logger.debug("WSClient iter_messages 停止")

    async def send_text(self, message: str) -> None:
        """发送原始文本消息。"""
        await self._connected.wait()
        async with self._send_lock:
            if not self._websocket:
                raise RuntimeError("WebSocket 未连接")
            await self._websocket.send(message)
            self._logger.debug(f"➡️ 发送: {message}")

    async def send_command(self, message_type: MessageType, *values: Any) -> None:
        """构建并发送命令消息。"""
        parts = [message_type.value.lower()]
        for value in values:
            if isinstance(value, (str, int, float)):  # 简单类型
                parts.append(str(value))
            else:
                parts.append(json.dumps(value, ensure_ascii=False))
        payload = ",".join(parts)
        await self.send_text(payload)

    async def close(self) -> None:
        """关闭连接并停止监听循环。"""
        self._stop.set()
        if self._websocket and not self._websocket.closed:
            await self._websocket.close()
        self._connected.clear()

    def build_http_headers(self) -> Dict[str, str]:
        """构建 HTTP 请求头，供 API 调用复用。"""
        headers: Dict[str, str] = {
            "Magic-Request-Client-Id": self.client_id,
        }
        if self.token:
            headers["Magic-Token"] = self.token
        if self.username:
            headers["Magic-Username"] = self.username
        if self.password:
            headers["Magic-Password"] = self.password
        return headers

    # ------------------------------------------------------------------
    # 内部逻辑
    # ------------------------------------------------------------------
    async def _send_login(self) -> None:
        identifier = self.token or self.username or "unauthorization"
        login_message = f"login,{identifier},{self.client_id}"
        await self.send_text(login_message)
        self._logger.debug(f"📤 登录消息: {login_message}")

    def _build_headers(self) -> Dict[str, str]:
        headers = dict(self.extra_headers)
        if self.token:
            headers.setdefault("Magic-Token", self.token)
        if self.username:
            headers.setdefault("Magic-Username", self.username)
        if self.password:
            headers.setdefault("Magic-Password", self.password)
        headers.setdefault("User-Agent", "magicapi-ws-client/1.0")
        return headers

    def _generate_client_id(self) -> str:
        return secrets.token_hex(8)


__all__ = ["WSClient"]
