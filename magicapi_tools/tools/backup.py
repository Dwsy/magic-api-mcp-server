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
            try:
                # 调用备份API
                params = {}
                if timestamp:
                    params['timestamp'] = timestamp

                ok, response = context.http_client.call_api("GET", "/magic/web/backups", params=params)

                if not ok:
                    return error_response(
                        response.get("code", "network_error"),
                        response.get("message", "查询备份列表失败"),
                        response.get("detail")
                    )

                data = response.get("body", {})
                if data.get("code") != 1:
                    return error_response(
                        data.get("code", -1),
                        data.get("message", "查询备份列表失败"),
                        data.get("data")
                    )

                backups = data.get("data", [])

                # 应用过滤
                original_count = len(backups)

                # 过滤逻辑
                if filter_text or name_filter:
                    filtered_backups = []
                    filter_lower = filter_text.lower() if filter_text else ""
                    name_filter_lower = name_filter.lower() if name_filter else ""

                    for backup in backups:
                        # 检查过滤条件
                        should_include = True

                        # 通用过滤
                        if filter_text:
                            searchable_fields = [
                                backup.get('id', ''),
                                backup.get('type', ''),
                                backup.get('name', ''),
                                backup.get('createBy', ''),
                                backup.get('tag', ''),
                            ]
                            if not any(filter_lower in str(field).lower() for field in searchable_fields if field):
                                should_include = False

                        # 名称过滤
                        if name_filter and should_include:
                            backup_name = backup.get('name', '')
                            if not (backup_name and name_filter_lower in str(backup_name).lower()):
                                should_include = False

                        if should_include:
                            filtered_backups.append(backup)

                    backups = filtered_backups

                # 应用 limit 限制
                filtered_count = len(backups)
                if limit > 0:
                    backups = backups[:limit]

                return {
                    "total_backups": original_count,
                    "filtered_backups": filtered_count,
                    "returned_backups": len(backups),
                    "limit": limit,
                    "filters_applied": {
                        "timestamp": timestamp,
                        "filter_text": filter_text,
                        "name_filter": name_filter,
                    },
                    "backups": backups,
                }

            except Exception as exc:
                return error_response("backup_list_error", f"查询备份列表失败: {exc}", str(exc))

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
            try:
                if not backup_id.strip():
                    return error_response("invalid_param", "备份ID不能为空")

                ok, response = context.http_client.call_api("GET", f"/magic/web/backup/{backup_id}")

                if not ok:
                    return error_response(
                        response.get("code", "network_error"),
                        response.get("message", "查询备份历史失败"),
                        response.get("detail")
                    )

                data = response.get("body", {})
                if data.get("code") != 1:
                    return error_response(
                        data.get("code", -1),
                        data.get("message", "查询备份历史失败"),
                        data.get("data")
                    )

                history = data.get("data", [])

                return {
                    "backup_id": backup_id,
                    "history_count": len(history),
                    "history": history,
                }

            except Exception as exc:
                return error_response("backup_history_error", f"查询备份历史失败: {exc}", str(exc))

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
            try:
                if not backup_id.strip():
                    return error_response("invalid_param", "备份ID不能为空")

                params = {
                    'id': backup_id,
                    'timestamp': timestamp
                }

                ok, response = context.http_client.call_api("GET", "/magic/web/backup", params=params)

                if not ok:
                    return error_response(
                        response.get("code", "network_error"),
                        response.get("message", "获取备份内容失败"),
                        response.get("detail")
                    )

                data = response.get("body", {})
                if data.get("code") != 1:
                    return error_response(
                        data.get("code", -1),
                        data.get("message", "获取备份内容失败"),
                        data.get("data")
                    )

                content = data.get("data")

                return {
                    "backup_id": backup_id,
                    "timestamp": timestamp,
                    "content": content,
                    "has_content": content is not None,
                }

            except Exception as exc:
                return error_response("backup_content_error", f"获取备份内容失败: {exc}", str(exc))

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
            try:
                if not backup_id.strip():
                    return error_response("invalid_param", "备份ID不能为空")

                rollback_data = {
                    'id': backup_id,
                    'timestamp': timestamp
                }

                ok, response = context.http_client.call_api("POST", "/magic/web/backup/rollback", data=rollback_data)

                if not ok:
                    return error_response(
                        response.get("code", "network_error"),
                        response.get("message", "回滚备份失败"),
                        response.get("detail")
                    )

                data = response.get("body", {})
                if data.get("code") != 1:
                    return error_response(
                        data.get("code", -1),
                        data.get("message", "回滚备份失败"),
                        data.get("data")
                    )

                success = data.get("data", False)

                return {
                    "backup_id": backup_id,
                    "timestamp": timestamp,
                    "rollback_success": success,
                    "message": "回滚成功" if success else "回滚失败",
                }

            except Exception as exc:
                return error_response("rollback_error", f"回滚备份失败: {exc}", str(exc))

        @mcp_app.tool(
            name="create_full_backup",
            description="执行手动全量备份。",
            tags={"backup", "create", "full", "manual"},
        )
        def create_full_backup_tool() -> Dict[str, Any]:
            """执行全量备份。"""
            try:
                ok, response = context.http_client.call_api("POST", "/magic/web/backup/full")

                if not ok:
                    return error_response(
                        response.get("code", "network_error"),
                        response.get("message", "创建全量备份失败"),
                        response.get("detail")
                    )

                data = response.get("body", {})
                if data.get("code") != 1:
                    return error_response(
                        data.get("code", -1),
                        data.get("message", "创建全量备份失败"),
                        data.get("data")
                    )

                success = data.get("data", False)

                return {
                    "backup_type": "full",
                    "backup_success": success,
                    "message": "全量备份成功" if success else "全量备份失败",
                }

            except Exception as exc:
                return error_response("full_backup_error", f"创建全量备份失败: {exc}", str(exc))


