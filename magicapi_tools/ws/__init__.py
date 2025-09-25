"""Magic-API WebSocket 子系统。

该命名空间统一封装 WebSocket 客户端、消息模型、环境状态管理与观察者。
"""

from .messages import MessageType, WSMessage, parse_ws_message  # noqa: F401
from .client import WSClient  # noqa: F401
from .state import EnvironmentState, IDEEnvironment, OpenFileContext, LogBuffer  # noqa: F401
from .debug_service import WebSocketDebugService  # noqa: F401
from .manager import WSManager  # noqa: F401
from .utils import normalize_breakpoints, resolve_script_id_by_path  # noqa: F401

__all__ = [
    "MessageType",
    "WSMessage",
    "parse_ws_message",
    "WSClient",
    "EnvironmentState",
    "IDEEnvironment",
    "OpenFileContext",
    "LogBuffer",
    "WSManager",
    "WebSocketDebugService",
    "normalize_breakpoints",
    "resolve_script_id_by_path",
]
