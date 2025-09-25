"""WebSocket 调试服务，为 MCP 工具提供封装。"""

from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from magicapi_tools.utils.http_client import MagicAPIHTTPClient

from .manager import WSManager
from .messages import WSMessage
from .utils import normalize_breakpoints, resolve_script_id_by_path


@dataclass(slots=True)
class DebugStatus:
    breakpoints: List[int]
    client_id: str
    connected: bool
    environment_key: Optional[str]
    opened_file: Optional[str]
    opened_file_detail: Optional[Dict[str, Any]] = None


class WebSocketDebugService:
    """封装与断点调试相关的高层操作。"""

    def __init__(self, manager: WSManager, http_client: MagicAPIHTTPClient):
        self.manager = manager
        self.http_client = http_client
        self.breakpoints: Set[int] = set()
        self._last_script_id: Optional[str] = None

    # ------------------------------------------------------------------
    # 断点管理
    # ------------------------------------------------------------------
    def set_breakpoint_tool(self, line_number: Optional[int] = None, line_numbers: Optional[Sequence[int]] = None) -> Dict:
        if line_numbers is not None:
            return self.batch_set_breakpoints_tool(line_numbers)
        if line_number is None:
            return {"error": {"code": "invalid_line", "message": "必须提供断点行号"}}
        self.breakpoints.add(int(line_number))
        return {"success": True, "breakpoints": sorted(self.breakpoints)}

    def remove_breakpoint_tool(self, line_number: Optional[int] = None, line_numbers: Optional[Sequence[int]] = None) -> Dict:
        if line_numbers is not None:
            return self.batch_remove_breakpoints_tool(line_numbers)
        if line_number is None:
            return {"error": {"code": "invalid_line", "message": "必须提供断点行号"}}
        self.breakpoints.discard(int(line_number))
        return {"success": True, "breakpoints": sorted(self.breakpoints)}

    def batch_set_breakpoints_tool(self, line_numbers: Sequence[int]) -> Dict:
        for line in line_numbers:
            self.breakpoints.add(int(line))
        return {"success": True, "breakpoints": sorted(self.breakpoints)}

    def batch_remove_breakpoints_tool(self, line_numbers: Sequence[int]) -> Dict:
        for line in line_numbers:
            self.breakpoints.discard(int(line))
        return {"success": True, "breakpoints": sorted(self.breakpoints)}

    def clear_all_breakpoints_tool(self) -> Dict:
        count = len(self.breakpoints)
        self.breakpoints.clear()
        return {"success": True, "cleared_count": count}

    def list_breakpoints_tool(self) -> Dict:
        return {"success": True, "breakpoints": sorted(self.breakpoints)}

    # ------------------------------------------------------------------
    # 步进控制
    # ------------------------------------------------------------------
    async def resume_breakpoint_tool(self) -> Dict:
        return await self._send_step_command(0)

    async def step_over_tool(self) -> Dict:
        return await self._send_step_command(1)

    # ------------------------------------------------------------------
    # 核心操作
    # ------------------------------------------------------------------
    async def call_api_with_debug_tool(self, path: str, method: str = "GET", data: Optional[Dict] = None,
                                       params: Optional[Dict] = None, breakpoints: Optional[Sequence[int]] = None) -> Dict:
        await self.manager.ensure_running()

        actual_method, actual_path = self._normalize_method_path(method, path)

        combined_breakpoints: Set[int] = set(self.breakpoints)
        if breakpoints:
            combined_breakpoints.update(int(line) for line in breakpoints)
            self.breakpoints.update(combined_breakpoints)

        script_id = await asyncio.to_thread(resolve_script_id_by_path, self.http_client, actual_path)
        if script_id:
            self._last_script_id = script_id
        else:
            script_id = self._last_script_id
        if not script_id:
            return {
                "error": {
                    "code": "script_id_not_found",
                    "message": "无法根据路径定位接口脚本，请确认资源树已同步或传入 api_id",
                }
            }

        headers = {
            "Magic-Request-Script-Id": script_id,
            "Magic-Request-Breakpoints": normalize_breakpoints(combined_breakpoints),
            "Accept": "application/json, text/plain, */*",
        }

        request_headers = self.manager.build_request_headers(headers)

        start_ts = time.time()
        ok, payload = await asyncio.to_thread(
            self.http_client.call_api,
            actual_method,
            actual_path,
            params,
            data,
            request_headers,
            timeout=self.manager.settings.debug_timeout_seconds,
        )
        end_ts = time.time()

        logs = self._serialize_messages(
            self.manager.capture_logs_between(
                start_ts,
                end_ts,
                pre=self.manager.settings.ws_log_capture_window,
                post=self.manager.settings.ws_log_capture_window,
            )
        )

        if ok:
            return {
                "success": True,
                "response": payload,
                "ws_logs": logs,
                "duration": end_ts - start_ts,
            }
        return {
            "error": {
                "code": payload.get("code", "api_error") if isinstance(payload, dict) else "api_error",
                "message": payload.get("message", "调用接口失败") if isinstance(payload, dict) else "调用接口失败",
                "detail": payload,
            },
            "ws_logs": logs,
        }

    def execute_debug_session_tool(self, script_id: str, breakpoints: Optional[Sequence[int]] = None) -> Dict:
        if breakpoints:
            for line in breakpoints:
                self.breakpoints.add(int(line))
        return {
            "success": True,
            "script_id": script_id,
            "breakpoints": sorted(self.breakpoints),
        }

    def get_debug_status_tool(self) -> Dict:
        env = self.manager.state.get_environment_by_client(self.manager.client.client_id)
        opened_file = None
        opened_detail: Optional[Dict[str, Any]] = None
        ide_key = None
        if env:
            ide_key = env.ide_key
            ctx = env.opened_files.get(self.manager.client.client_id)
            if ctx:
                opened_file = ctx.file_id
                opened_detail = {
                    "file_id": ctx.file_id,
                    "method": ctx.method,
                    "path": ctx.path,
                    "name": ctx.name,
                    "group_chain": ctx.group_chain,
                    "last_breakpoint_range": ctx.last_breakpoint_range,
                    "headers": ctx.headers,
                    "detail": ctx.detail,
                    "resolved_at": ctx.resolved_at,
                }
        status = DebugStatus(
            breakpoints=sorted(self.breakpoints),
            client_id=self.manager.client.client_id,
            connected=self.manager.client._connected.is_set(),
            environment_key=ide_key,
            opened_file=opened_file,
            opened_file_detail=opened_detail,
        )
        return {"success": True, "status": asdict(status)}

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------
    async def _send_step_command(self, step_type: int) -> Dict:
        await self.manager.ensure_running()
        script_id = self._current_script_id()
        if not script_id:
            return {"error": {"code": "script_id_missing", "message": "无法确定当前调试脚本"}}
        await self.manager._send_step_command(script_id, step_type, sorted(self.breakpoints))
        return {"success": True, "script_id": script_id, "step": step_type}

    def _current_script_id(self) -> Optional[str]:
        env = self.manager.state.get_environment_by_client(self.manager.client.client_id)
        if not env:
            return self._last_script_id
        ctx = env.opened_files.get(self.manager.client.client_id)
        if ctx:
            return ctx.file_id
        return self._last_script_id

    def _normalize_method_path(self, method: str, path: str) -> Tuple[str, str]:
        candidate = path.strip()
        if " " in candidate:
            prefix, remainder = candidate.split(" ", 1)
            upper = prefix.upper()
            if upper in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
                return upper, remainder.strip() or "/"
        return method.upper(), candidate if candidate.startswith("/") else f"/{candidate}"

    def _resolve_script_id(self, path: str) -> Optional[str]:
        return resolve_script_id_by_path(self.http_client, path)

    @staticmethod
    def _serialize_messages(messages: Iterable[WSMessage]) -> List[Dict]:
        serialized = []
        for message in messages:
            serialized.append({
                "timestamp": message.timestamp,
                "type": message.type.value,
                "text": message.text,
                "payload": message.payload,
            })
        return serialized


__all__ = ["WebSocketDebugService", "DebugStatus"]
