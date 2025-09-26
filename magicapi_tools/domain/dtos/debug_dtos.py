"""调试相关的DTO类。

定义调试会话、执行请求和状态响应等的数据传输对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..models.base_model import BaseModel


@dataclass
class DebugSessionRequest:
    """调试会话请求对象。"""

    script_id: str
    breakpoints: List[int] = field(default_factory=list)

    def validate(self) -> bool:
        """验证调试会话请求。"""
        return bool(self.script_id and self.script_id.strip())

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        if not self.script_id or not self.script_id.strip():
            return ["脚本ID不能为空"]
        return []


@dataclass
class DebugExecutionRequest:
    """调试执行请求对象。"""

    action: str  # 'resume', 'step_over', 'step_into', 'step_out'
    script_id: Optional[str] = None

    def validate(self) -> bool:
        """验证调试执行请求。"""
        # 操作类型必须有效
        valid_actions = {'resume', 'step_over', 'step_into', 'step_out'}
        if self.action not in valid_actions:
            return False

        # 某些操作需要script_id
        if self.action in ['step_into', 'step_out'] and not self.script_id:
            return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        valid_actions = {'resume', 'step_over', 'step_into', 'step_out'}
        if self.action not in valid_actions:
            errors.append(f"不支持的调试操作: {self.action}")

        if self.action in ['step_into', 'step_out'] and not self.script_id:
            errors.append(f"{self.action}操作需要提供脚本ID")

        return errors


@dataclass
class BreakpointInfo:
    """断点信息对象。"""

    line_number: int
    script_id: str
    enabled: bool = True
    condition: Optional[str] = None

    def validate(self) -> bool:
        """验证断点信息。"""
        return self.line_number > 0 and bool(self.script_id)


@dataclass
class DebugStatusInfo:
    """调试状态信息对象。"""

    script_id: Optional[str] = None
    status: str = "stopped"  # 'running', 'stopped', 'paused', 'error'
    breakpoints: List[BreakpointInfo] = field(default_factory=list)
    current_line: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
    call_stack: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """初始化后的处理。"""
        # 将字典转换为BreakpointInfo对象
        if self.breakpoints and isinstance(self.breakpoints[0], dict):
            self.breakpoints = [BreakpointInfo(**item) for item in self.breakpoints]

    @property
    def is_running(self) -> bool:
        """检查是否正在运行。"""
        return self.status == "running"

    @property
    def is_paused(self) -> bool:
        """检查是否已暂停。"""
        return self.status == "paused"

    @property
    def has_breakpoints(self) -> bool:
        """检查是否有断点。"""
        return len(self.breakpoints) > 0


@dataclass
class DebugStatusResponse:
    """调试状态响应对象。"""

    success: bool = False
    status_info: Optional[DebugStatusInfo] = None
    message: str = ""
    logs: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """初始化后的处理。"""
        if self.status_info and isinstance(self.status_info, dict):
            self.status_info = DebugStatusInfo(**self.status_info)

    @property
    def has_error(self) -> bool:
        """检查是否有错误。"""
        return not self.success

    @property
    def current_status(self) -> str:
        """获取当前调试状态。"""
        return self.status_info.status if self.status_info else "unknown"
