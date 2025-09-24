"""Magic-API 系统信息相关 MCP 工具。

此模块提供系统级别的工具，包括：
- 获取助手元信息和配置
- 系统状态查询
- 环境信息获取
- 功能特性说明

主要工具：
- get_assistant_metadata: 获取Magic-API MCP Server的完整元信息
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from magicapi_tools.utils.knowledge_base import SYSTEM_PROMPT

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class SystemTools:
    """系统工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册系统相关工具。"""

        @mcp_app.tool(
            name="get_assistant_metadata",
            description="获取Magic-API助手元信息，包括版本、功能列表和配置。",
            tags={"meta", "info", "system"},
            meta={"version": "2.2", "category": "system"},
        )
        def meta() -> Dict[str, Any]:
            return {
                "system_prompt": SYSTEM_PROMPT,
                "version": "2.2.0",
                "features": [
                    "syntax", "examples", "docs", "best_practices", "pitfalls", "workflow",
                    "resource_tree", "path_to_id", "path_detail", "api_detail",
                    "find_api_ids_by_path(limit=10)", "find_api_details_by_path(limit=10)", "call",
                    "create_group", "create_api", "copy_resource", "move_resource",
                    "delete_resource", "lock_resource", "unlock_resource",
                    "list_resource_groups(limit=50,search)", "export_resource_tree", "get_resource_stats",
                    "list_backups(limit=10)", "get_backup_history", "get_backup_content", "rollback_backup", "create_full_backup",
                    "search_api_scripts", "search_todo_comments",
                    "set_breakpoint", "remove_breakpoint", "resume_breakpoint", "step_over",
                    "list_breakpoints", "call_api_with_debug", "execute_debug_session",
                    "get_debug_status", "clear_all_breakpoints", "websocket_status",
                ],
                "environment": {
                    "base_url": context.settings.base_url,
                    "ws_url": context.settings.ws_url,
                    "auth_enabled": context.settings.auth_enabled,
                },
                "clients": {
                    "http_client": "available",
                    "resource_manager": "available",
                    "debug_client": "available",
                },
                "architecture": {
                    "modular_design": True,
                    "tool_registry": True,
                    "composable_tools": True,
                    "parameter_metadata": True,
                },
            }

