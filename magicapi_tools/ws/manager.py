"""WebSocket 管理器：协调客户端、状态与观察者。"""

from __future__ import annotations

import asyncio
import threading
from typing import List, Optional, Sequence

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils.resource_manager import MagicAPIResourceManager

from magicapi_mcp.settings import MagicAPISettings

from .client import WSClient
from .messages import MessageType, WSMessage
from .observers import BaseObserver
from .state import EnvironmentState, IDEEnvironment, LogBuffer, ResourceResolver


class _ResourceResolver(ResourceResolver):
    """默认资源解析器，基于 `MagicAPIResourceManager`。"""

    def __init__(self, manager: MagicAPIResourceManager):
        self._manager = manager
        self._cache: dict[str, dict] = {}

    def resolve_file(self, file_id: str):  # type: ignore[override]
        if not file_id:
            return None
        if file_id in self._cache:
            return self._cache[file_id]
        detail = self._manager.get_file_detail(file_id)
        if detail:
            self._cache[file_id] = detail
        return detail


class WSManager:
    """Magic-API WebSocket 上下文管理器。"""

    def __init__(
        self,
        settings: MagicAPISettings,
        resource_manager: MagicAPIResourceManager,
        *,
        auto_start: Optional[bool] = None,
    ) -> None:
        self.settings = settings
        self.resource_manager = resource_manager
        self.auto_start = settings.ws_auto_start if auto_start is None else auto_start

        self.log_buffer = LogBuffer(maxlen=settings.ws_log_history_size)
        self.state = EnvironmentState(resource_resolver=_ResourceResolver(resource_manager))
        self.client = WSClient(
            ws_url=settings.ws_url,
            username=settings.username if settings.auth_enabled else None,
            password=settings.password if settings.auth_enabled else None,
            token=settings.token,
            reconnect_interval=settings.ws_reconnect_interval,
        )
        self.state.set_primary_client(self.client.client_id)

        self._logger = get_logger("ws.manager")
        self._observers: set[BaseObserver] = set()
        self._listen_task: Optional[asyncio.Task[None]] = None
        self._stop_event = asyncio.Event()
        self._lock: Optional[asyncio.Lock] = None

        # 独立事件循环线程，支持同步/异步调用
        self._loop = asyncio.new_event_loop()
        self._loop_ready = threading.Event()

        def _run_loop() -> None:
            asyncio.set_event_loop(self._loop)
            self._lock = asyncio.Lock()
            self._loop_ready.set()
            self._loop.run_forever()

        self._loop_thread = threading.Thread(target=_run_loop, name="ws-manager-loop", daemon=True)
        self._loop_thread.start()
        self._loop_ready.wait()

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        await asyncio.wrap_future(self._submit(self._start_internal()), loop=loop)

    async def ensure_running(self) -> None:
        if self.auto_start:
            await self.start()

    async def stop(self) -> None:
        loop = asyncio.get_running_loop()
        await asyncio.wrap_future(self._submit(self._stop_internal()), loop=loop)

    def start_sync(self) -> None:
        self._submit(self._start_internal()).result()

    def ensure_running_sync(self) -> None:
        if self.auto_start:
            try:
                self._submit(self._start_internal()).result()
            except Exception as exc:  # pragma: no cover
                self._logger.error(f"启动 WebSocket 监听失败: {exc}")

    def stop_sync(self) -> None:
        self._submit(self._stop_internal()).result()

    async def _start_internal(self) -> None:
        assert self._lock is not None
        async with self._lock:
            if self._listen_task and not self._listen_task.done():
                return
            self._stop_event.clear()
            self._listen_task = asyncio.create_task(self._listen_loop(), name="ws-manager-listener")
            self._logger.info("WSManager 已启动监听任务")

    async def _stop_internal(self) -> None:
        self._stop_event.set()
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:  # pragma: no cover - 正常取消
                pass
            self._listen_task = None
        await self.client.close()
        self._logger.info("WSManager 已停止")

    # ------------------------------------------------------------------
    # 观察者管理
    # ------------------------------------------------------------------
    def add_observer(self, observer: BaseObserver) -> None:
        self._observers.add(observer)

    def remove_observer(self, observer: BaseObserver) -> None:
        self._observers.discard(observer)

    # ------------------------------------------------------------------
    # 查询接口
    # ------------------------------------------------------------------
    def list_environments(self):
        return self.state.list_environments()

    def get_environment(self, ide_key: str):
        return self.state.get_environment(ide_key)

    def recent_logs(self, limit: Optional[int] = None) -> List[WSMessage]:
        return list(self.log_buffer.iter_recent(limit))

    def capture_logs_around(self, timestamp: float, pre: float | None = None, post: float | None = None) -> List[WSMessage]:
        pre = self.settings.ws_log_capture_window if pre is None else pre
        post = self.settings.ws_log_capture_window if post is None else post
        return self.log_buffer.window(timestamp, pre=pre, post=post)

    def capture_logs_between(
        self,
        start_ts: float,
        end_ts: float,
        *,
        pre: float | None = None,
        post: float | None = None,
    ) -> List[WSMessage]:
        pre = self.settings.ws_log_capture_window if pre is None else pre
        post = self.settings.ws_log_capture_window if post is None else post
        return self.log_buffer.between(start_ts - pre, end_ts + post)

    # ------------------------------------------------------------------
    # 调试指令封装
    # ------------------------------------------------------------------
    async def send_resume(self, script_id: str, breakpoints: Optional[Sequence[int]] = None) -> None:
        await self._send_step_command(script_id, 0, breakpoints)

    async def send_step_over(self, script_id: str, breakpoints: Optional[Sequence[int]] = None) -> None:
        await self._send_step_command(script_id, 1, breakpoints)

    async def send_step_into(self, script_id: str, breakpoints: Optional[Sequence[int]] = None) -> None:
        await self._send_step_command(script_id, 2, breakpoints)

    async def send_step_out(self, script_id: str, breakpoints: Optional[Sequence[int]] = None) -> None:
        await self._send_step_command(script_id, 3, breakpoints)

    async def send_set_file_id(self, file_id: str) -> None:
        await self.client.send_command(MessageType.SET_FILE_ID, file_id)

    # ------------------------------------------------------------------
    # 内部监听逻辑
    # ------------------------------------------------------------------
    async def _listen_loop(self) -> None:
        try:
            async for message in self.client.iter_messages():
                if self._logger.isEnabledFor(10):
                    self._logger.debug("收到消息: %s", message.type.value)
                self.log_buffer.append(message)
                environment = self.state.handle_message(message, default_client_id=self.client.client_id)
                await self._notify_observers(message, environment)
                if self._stop_event.is_set():
                    break
        except asyncio.CancelledError:  # pragma: no cover - 取消时直接退出
            pass
        except Exception as exc:  # pragma: no cover - 兜底异常
            await self._notify_error(exc)
            self._logger.error(f"WebSocket 监听出现异常: {exc}")
        finally:
            await self._notify_disconnect()

    async def _notify_observers(self, message: WSMessage, environment: Optional[IDEEnvironment]) -> None:
        effective_env = environment or self.state.get_environment_by_client(self.client.client_id)
        tasks = [observer.on_message(message, effective_env) for observer in self._observers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _notify_error(self, exc: Exception) -> None:
        tasks = [observer.on_error(exc) for observer in self._observers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _notify_disconnect(self) -> None:
        tasks = [observer.on_disconnect() for observer in self._observers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_step_command(self, script_id: str, step_type: int, breakpoints: Optional[Sequence[int]]) -> None:
        breakpoint_str = "|".join(str(b) for b in breakpoints) if breakpoints else ""
        await self.client.send_command(MessageType.RESUME_BREAKPOINT, script_id, step_type, breakpoint_str)

    # ------------------------------------------------------------------
    # HTTP Header 辅助
    # ------------------------------------------------------------------
    def build_request_headers(self, extra: Optional[dict] = None) -> dict:
        headers = self.client.build_http_headers()
        if extra:
            headers.update(extra)
        return headers

    # ------------------------------------------------------------------
    # 线程安全调度
    # ------------------------------------------------------------------
    def _submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop)


__all__ = ["WSManager"]
