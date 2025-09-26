"""Magic-API 备份管理相关 MCP 工具。

此模块提供完整的备份管理功能，包括：
- 备份记录查询和过滤
- 备份历史查看
- 备份内容获取
- 备份恢复操作
- 自动备份创建

主要工具：
- list_backups: 查询备份列表，支持时间戳过滤和名称过滤
- get_backup_history: 获取备份历史记录
- get_backup_content: 获取指定备份的内容
- rollback_backup: 回滚到指定的备份版本
- create_full_backup: 创建完整的系统备份
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

from pydantic import Field

from magicapi_tools.tools.common import error_response

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class BackupTools:
    """备份管理工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册备份管理相关工具。"""

        @mcp_app.tool(
            name="list_backups",
            description="查询备份列表，支持时间戳过滤和名称过滤。",
            tags={"backup", "list", "filter", "timestamp"},
        )
        def list_backups_tool(
            timestamp: Annotated[
                Optional[int],
                Field(description="查询指定时间戳之前的备份记录")
            ] = None,
            filter_text: Annotated[
                Optional[str],
                Field(description="通用模糊过滤备份记录（支持ID、类型、名称、创建者等字段）")
            ] = None,
            name_filter: Annotated[
                Optional[str],
                Field(description="按名称精确过滤备份记录")
            ] = None,
            limit: Annotated[
                int,
                Field(description="返回结果的最大数量，默认10条")
            ] = 10,
        ) -> Dict[str, Any]:
            """查询备份列表。"""
            # 使用服务层处理备份列表查询
            from magicapi_tools.domain.dtos.backup_dtos import BackupOperationRequest

            request = BackupOperationRequest(
                operation="list",
                timestamp=timestamp,
                filter_text=filter_text,
                name_filter=name_filter,
                limit=limit
            )

            response = context.backup_service.list_backups(request)
            return response.to_dict()

        @mcp_app.tool(
            name="get_backup_history",
            description="根据ID查询特定对象的备份历史记录。",
            tags={"backup", "history", "id", "timeline"},
        )
        def get_backup_history_tool(
            backup_id: Annotated[
                str,
                Field(description="备份对象ID")
            ],
        ) -> Dict[str, Any]:
            """查询备份历史。"""
            # 使用服务层处理备份历史查询
            from magicapi_tools.domain.dtos.backup_dtos import BackupHistoryRequest

            request = BackupHistoryRequest(backup_id=backup_id)
            response = context.backup_service.get_backup_history(request)
            return response.to_dict()

        @mcp_app.tool(
            name="get_backup_content",
            description="获取指定备份版本的脚本内容。",
            tags={"backup", "content", "script", "restore"},
        )
        def get_backup_content_tool(
            backup_id: Annotated[
                str,
                Field(description="备份对象ID")
            ],
            timestamp: Annotated[
                int,
                Field(description="备份时间戳")
            ],
        ) -> Dict[str, Any]:
            """获取备份内容。"""
            # 使用服务层处理备份内容查询
            from magicapi_tools.domain.dtos.backup_dtos import BackupOperationRequest

            request = BackupOperationRequest(
                operation="content",
                backup_id=backup_id,
                timestamp=timestamp
            )
            response = context.backup_service.get_backup_content(request)
            return response.to_dict()

        @mcp_app.tool(
            name="rollback_backup",
            description="回滚到指定的备份版本。",
            tags={"backup", "rollback", "restore", "dangerous"},
        )
        def rollback_backup_tool(
            backup_id: Annotated[
                str,
                Field(description="备份对象ID")
            ],
            timestamp: Annotated[
                int,
                Field(description="备份时间戳")
            ],
        ) -> Dict[str, Any]:
            """执行回滚操作。"""
            # 使用服务层处理备份回滚
            from magicapi_tools.domain.dtos.backup_dtos import BackupOperationRequest

            request = BackupOperationRequest(
                operation="rollback",
                backup_id=backup_id,
                timestamp=timestamp
            )
            response = context.backup_service.rollback_backup(request)
            return response.to_dict()

        @mcp_app.tool(
            name="create_full_backup",
            description="执行手动全量备份。",
            tags={"backup", "create", "full", "manual"},
        )
        def create_full_backup_tool() -> Dict[str, Any]:
            """执行全量备份。"""
            # 使用服务层处理全量备份创建
            from magicapi_tools.domain.dtos.backup_dtos import BackupOperationRequest

            request = BackupOperationRequest(operation="create_full")
            response = context.backup_service.create_full_backup(request)
            return response.to_dict()


