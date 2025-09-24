"""Magic-API 工具注册器 - 管理工具的注册和组合。"""

from __future__ import annotations

from typing import Any, List, Optional, Protocol

from magicapi_mcp.settings import MagicAPISettings
from magicapi_tools.utils.http_client import MagicAPIHTTPClient
from magicapi_tools.utils.resource_manager import MagicAPIResourceManager, MagicAPIResourceTools
from magicapi_tools.utils.ws import MagicAPIDebugClient, MagicAPIDebugTools


class ToolContext:
    """工具上下文，包含所有必要的客户端和服务。"""

    def __init__(self, settings: MagicAPISettings):
        self.settings = settings
        self.http_client = MagicAPIHTTPClient(settings)
        self.resource_manager = MagicAPIResourceManager(
            settings.base_url,
            settings.username if settings.auth_enabled else None,
            settings.password if settings.auth_enabled else None,
            http_client=self.http_client,
        )
        self.resource_tools = MagicAPIResourceTools(self.resource_manager)
        self.debug_client = MagicAPIDebugClient(
            settings.ws_url,
            settings.base_url,
            settings.username if settings.auth_enabled else None,
            settings.password if settings.auth_enabled else None,
        )
        self.debug_tools = MagicAPIDebugTools(self.debug_client)


class ToolModule(Protocol):
    """工具模块协议。"""

    def register_tools(self, mcp_app: Any, context: ToolContext) -> None:
        """注册工具到MCP应用。

        Args:
            mcp_app: FastMCP应用实例
            context: 工具上下文
        """
        ...


class ToolRegistry:
    """工具注册器，管理所有工具模块的注册。"""

    def __init__(self):
        self.modules: List[ToolModule] = []
        self.context: Optional[ToolContext] = None

    def add_module(self, module: ToolModule) -> None:
        """添加工具模块。"""
        self.modules.append(module)

    def initialize_context(self, settings: MagicAPISettings) -> None:
        """初始化工具上下文。"""
        self.context = ToolContext(settings)

    def register_all_tools(self, mcp_app: Any) -> None:
        """注册所有工具模块到MCP应用。"""
        if not self.context:
            raise RuntimeError("工具上下文未初始化，请先调用 initialize_context()")

        for module in self.modules:
            module.register_tools(mcp_app, self.context)


# 全局工具注册器实例
tool_registry = ToolRegistry()
