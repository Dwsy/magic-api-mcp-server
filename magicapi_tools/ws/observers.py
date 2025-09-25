"""WebSocket 消息观察者。"""

from __future__ import annotations

import asyncio
from typing import Optional

from magicapi_tools.logging_config import get_logger

from .messages import MessageType, WSMessage
from .state import IDEEnvironment

try:  # pragma: no cover - fastmcp 在测试环境下可能不存在
    from fastmcp import Context
except ImportError:  # pragma: no cover
    Context = None  # type: ignore[misc]


class BaseObserver:
    """观察者基类，定义可重写的钩子。"""

    async def on_message(self, message: WSMessage, environment: Optional[IDEEnvironment]) -> None:
        return None

    async def on_error(self, exc: Exception) -> None:
        return None

    async def on_disconnect(self) -> None:
        return None


class CLIObserver(BaseObserver):
    """默认 CLI 输出观察者，保持现有体验。"""

    def __init__(self) -> None:
        self._logger = get_logger("ws.cli_observer")

    async def on_message(self, message: WSMessage, environment: Optional[IDEEnvironment]) -> None:
        prefix = {
            MessageType.LOG: "📝",
            MessageType.LOGS: "📝",
            MessageType.BREAKPOINT: "🔴",
            MessageType.EXCEPTION: "❌",
        }.get(message.type, "📨")
        env_label = f"[{environment.ide_key}] " if environment else ""
        text = message.text or message.raw
        self._logger.info(f"{prefix} {env_label}{text}")

    async def on_error(self, exc: Exception) -> None:
        self._logger.error(f"WebSocket 观察者异常: {exc}")


class MCPObserver(BaseObserver):
    """集成 FastMCP `Context` 的观察者。"""

    def __init__(self, ctx: "Context") -> None:
        if Context is None:
            raise RuntimeError("未安装 fastmcp，无法使用 MCPObserver")
        self.ctx = ctx
        self._lock = asyncio.Lock()

    async def on_message(self, message: WSMessage, environment: Optional[IDEEnvironment]) -> None:
        async with self._lock:
            extra = {
                "message_type": message.type.value,
                "ide_key": getattr(environment, "ide_key", None),
                "client_ids": list(getattr(environment, "client_ids", []) or []),
                "timestamp": message.timestamp,
            }
            if environment and environment.opened_files:
                extra["opened_files"] = {
                    cid: {
                        "file_id": ctx.file_id,
                        "method": ctx.method,
                        "path": ctx.path,
                        "name": ctx.name,
                        "group_chain": ctx.group_chain,
                        "last_breakpoint_range": ctx.last_breakpoint_range,
                    }
                    for cid, ctx in environment.opened_files.items()
                }
            if message.type in {MessageType.LOG, MessageType.LOGS}:
                await self.ctx.debug(message.text, extra=extra)
            elif message.type == MessageType.BREAKPOINT:
                await self.ctx.warning(message.text, extra=extra)
            elif message.type == MessageType.EXCEPTION:
                await self.ctx.error(message.text, extra=extra)
            else:
                await self.ctx.info(message.text, extra=extra)

    async def on_error(self, exc: Exception) -> None:
        async with self._lock:
            await self.ctx.error(f"WebSocket 监听异常: {exc}")


__all__ = ["BaseObserver", "CLIObserver", "MCPObserver"]
