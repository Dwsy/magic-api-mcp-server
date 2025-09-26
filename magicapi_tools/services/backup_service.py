"""备份业务服务。

处理所有备份相关的业务逻辑，包括备份列表、历史查询、恢复等。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import create_operation_error
from magicapi_tools.domain.dtos.backup_dtos import (
    BackupOperationRequest,
    BackupOperationResponse,
    BackupHistoryRequest
)

from .base_service import BaseService

if TYPE_CHECKING:
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('services.backup')


class BackupService(BaseService):
    """备份业务服务类。"""

    def list_backups(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """列出备份。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.backup')

        # 验证请求
        if not request.validate():
            errors = request.get_validation_errors()
            return BackupOperationResponse(
                success=False,
                operation=request.operation,
                message=f"验证失败: {'; '.join(errors)}"
            )

        log_operation_start("列出备份", {"operation": request.operation, "limit": request.limit})

        try:
            result = self._list_backups_impl(request)
            log_operation_end("列出备份", result.success)
            return result
        except Exception as e:
            logger.error(f"列出备份失败: {e}")
            return BackupOperationResponse(
                success=False,
                operation=request.operation,
                message=f"列出备份失败: {str(e)}"
            )

    # 向后兼容的方法
    def list_backups_legacy(
        self,
        timestamp: Optional[int] = None,
        filter_text: Optional[str] = None,
        name_filter: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """列出备份（向后兼容版本）。"""
        request = BackupOperationRequest(
            operation="list",
            timestamp=timestamp,
            filter_text=filter_text,
            name_filter=name_filter,
            limit=limit
        )

        response = self.list_backups(request)
        return response.to_dict()

    def _list_backups_impl(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """列出备份的实现。"""
        params = {}
        if request.timestamp:
            params['timestamp'] = request.timestamp

        ok, response = self.http_client.call_api("GET", "/magic/web/backups", params=params)
        if not ok:
            return BackupOperationResponse(
                success=False,
                operation=request.operation,
                message="查询备份列表失败",
                details={"error": response}
            )

        data = response.get("body", {})
        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(data, self.settings, "查询备份列表")
        if api_error:
            return BackupOperationResponse(
                success=False,
                operation=request.operation,
                message=api_error["error"]["message"],
                details=api_error["error"]
            )

        backups = data.get("data", [])

        # 应用过滤
        original_count = len(backups)
        filter_text = request.filter_text
        name_filter = request.name_filter

        if filter_text or name_filter:
            filtered_backups = []
            filter_lower = filter_text.lower() if filter_text else ""
            name_filter_lower = name_filter.lower() if name_filter else ""

            for backup in backups:
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

        # 应用限制
        filtered_count = len(backups)
        if request.limit > 0:
            backups = backups[:request.limit]

        return BackupOperationResponse(
            success=True,
            operation=request.operation,
            message="备份列表查询成功",
            backups=backups,
            details={
                "total_backups": original_count,
                "filtered_backups": filtered_count,
                "returned_backups": len(backups),
                "limit": request.limit,
                "filters_applied": {
                    "timestamp": request.timestamp,
                    "filter_text": request.filter_text,
                    "name_filter": request.name_filter,
                }
            }
        )

    def get_backup_history(self, request: BackupHistoryRequest) -> BackupOperationResponse:
        """获取备份历史。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.backup')

        # 验证请求
        if not request.validate():
            errors = request.get_validation_errors()
            return BackupOperationResponse(
                success=False,
                operation="get_history",
                message=f"验证失败: {'; '.join(errors)}"
            )

        log_operation_start("获取备份历史", {"backup_id": request.backup_id})

        try:
            result = self._get_backup_history_impl(request)
            log_operation_end("获取备份历史", result.success)
            return result
        except Exception as e:
            logger.error(f"获取备份历史失败: {e}")
            return BackupOperationResponse(
                success=False,
                operation="get_history",
                backup_id=request.backup_id,
                message=f"获取备份历史失败: {str(e)}"
            )

    # 向后兼容的方法
    def get_backup_history_legacy(self, backup_id: str) -> Dict[str, Any]:
        """获取备份历史（向后兼容版本）。"""
        request = BackupHistoryRequest(backup_id=backup_id)
        response = self.get_backup_history(request)
        return response.to_dict()

    def _get_backup_history_impl(self, request: BackupHistoryRequest) -> BackupOperationResponse:
        """获取备份历史的实现。"""
        ok, response = self.http_client.call_api("GET", f"/magic/web/backup/{request.backup_id}")
        if not ok:
            return BackupOperationResponse(
                success=False,
                operation="get_history",
                backup_id=request.backup_id,
                message="查询备份历史失败",
                details={"error": response}
            )

        data = response.get("body", {})
        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(data, self.settings, "查询备份历史")
        if api_error:
            return BackupOperationResponse(
                success=False,
                operation="get_history",
                backup_id=request.backup_id,
                message=api_error["error"]["message"],
                details=api_error["error"]
            )

        history = data.get("data", [])

        return BackupOperationResponse(
            success=True,
            operation="get_history",
            backup_id=request.backup_id,
            message="备份历史查询成功",
            history=history,
            details={
                "history_count": len(history)
            }
        )

    def get_backup_content(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """获取备份内容。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.backup')

        # 验证请求
        if not request.validate() or request.operation != "content":
            return BackupOperationResponse(
                success=False,
                operation="get_content",
                message="无效的备份内容请求"
            )

        if not request.backup_id or request.timestamp is None:
            return BackupOperationResponse(
                success=False,
                operation="get_content",
                message="备份ID和时间戳不能为空"
            )

        log_operation_start("获取备份内容", {"backup_id": request.backup_id, "timestamp": request.timestamp})

        try:
            result = self._get_backup_content_impl(request)
            log_operation_end("获取备份内容", result.success)
            return result
        except Exception as e:
            logger.error(f"获取备份内容失败: {e}")
            return BackupOperationResponse(
                success=False,
                operation="get_content",
                backup_id=request.backup_id,
                message=f"获取备份内容失败: {str(e)}"
            )

    # 向后兼容的方法
    def get_backup_content_legacy(self, backup_id: str, timestamp: int) -> Dict[str, Any]:
        """获取备份内容（向后兼容版本）。"""
        request = BackupOperationRequest(
            operation="content",
            backup_id=backup_id,
            timestamp=timestamp
        )
        response = self.get_backup_content(request)
        return response.to_dict()

    def _get_backup_content_impl(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """获取备份内容的实现。"""
        params = {'id': request.backup_id, 'timestamp': request.timestamp}
        ok, response = self.http_client.call_api("GET", "/magic/web/backup", params=params)
        if not ok:
            return BackupOperationResponse(
                success=False,
                operation="get_content",
                backup_id=request.backup_id,
                message="获取备份内容失败",
                details={"error": response}
            )

        data = response.get("body", {})
        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(data, self.settings, "获取备份内容")
        if api_error:
            return BackupOperationResponse(
                success=False,
                operation="get_content",
                backup_id=request.backup_id,
                message=api_error["error"]["message"],
                details=api_error["error"]
            )

        content = data.get("data")
        return BackupOperationResponse(
            success=True,
            operation="get_content",
            backup_id=request.backup_id,
            message="备份内容获取成功",
            data=content,
            details={
                "timestamp": request.timestamp,
                "has_content": content is not None
            }
        )

    def rollback_backup(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """回滚备份。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.backup')

        # 验证请求
        if not request.validate() or request.operation != "rollback":
            return BackupOperationResponse(
                success=False,
                operation="rollback",
                message="无效的回滚请求"
            )

        if not request.backup_id or request.timestamp is None:
            return BackupOperationResponse(
                success=False,
                operation="rollback",
                message="备份ID和时间戳不能为空"
            )

        log_operation_start("回滚备份", {"backup_id": request.backup_id, "timestamp": request.timestamp})

        try:
            result = self._rollback_backup_impl(request)
            log_operation_end("回滚备份", result.success)
            return result
        except Exception as e:
            logger.error(f"回滚备份失败: {e}")
            return BackupOperationResponse(
                success=False,
                operation="rollback",
                backup_id=request.backup_id,
                message=f"回滚备份失败: {str(e)}"
            )

    # 向后兼容的方法
    def rollback_backup_legacy(self, backup_id: str, timestamp: int) -> Dict[str, Any]:
        """回滚备份（向后兼容版本）。"""
        request = BackupOperationRequest(
            operation="rollback",
            backup_id=backup_id,
            timestamp=timestamp
        )
        response = self.rollback_backup(request)
        return response.to_dict()

    def _rollback_backup_impl(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """回滚备份的实现。"""
        rollback_data = {'id': request.backup_id, 'timestamp': request.timestamp}
        ok, response = self.http_client.call_api("POST", "/magic/web/backup/rollback", data=rollback_data)
        if not ok:
            return BackupOperationResponse(
                success=False,
                operation="rollback",
                backup_id=request.backup_id,
                message="回滚备份失败",
                details={"error": response}
            )

        data = response.get("body", {})
        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(data, self.settings, "回滚备份")
        if api_error:
            return BackupOperationResponse(
                success=False,
                operation="rollback",
                backup_id=request.backup_id,
                message=api_error["error"]["message"],
                details=api_error["error"]
            )

        success = data.get("data", False)
        return BackupOperationResponse(
            success=True,
            operation="rollback",
            backup_id=request.backup_id,
            message="回滚成功" if success else "回滚失败",
            data={"rollback_success": success},
            details={"timestamp": request.timestamp}
        )

    def create_full_backup(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """创建全量备份。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.backup')

        # 验证请求
        if not request.validate() or request.operation != "create_full":
            return BackupOperationResponse(
                success=False,
                operation="create_full",
                message="无效的全量备份请求"
            )

        log_operation_start("创建全量备份", {"operation": request.operation})

        try:
            result = self._create_full_backup_impl(request)
            log_operation_end("创建全量备份", result.success)
            return result
        except Exception as e:
            logger.error(f"创建全量备份失败: {e}")
            return BackupOperationResponse(
                success=False,
                operation="create_full",
                message=f"创建全量备份失败: {str(e)}"
            )

    # 向后兼容的方法
    def create_full_backup_legacy(self) -> Dict[str, Any]:
        """创建全量备份（向后兼容版本）。"""
        request = BackupOperationRequest(operation="create_full")
        response = self.create_full_backup(request)
        return response.to_dict()

    def _create_full_backup_impl(self, request: BackupOperationRequest) -> BackupOperationResponse:
        """创建全量备份的实现。"""
        ok, response = self.http_client.call_api("POST", "/magic/web/backup/full")
        if not ok:
            return BackupOperationResponse(
                success=False,
                operation="create_full",
                message="创建全量备份失败",
                details={"error": response}
            )

        data = response.get("body", {})
        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(data, self.settings, "创建全量备份")
        if api_error:
            return BackupOperationResponse(
                success=False,
                operation="create_full",
                message=api_error["error"]["message"],
                details=api_error["error"]
            )

        success = data.get("data", False)
        return BackupOperationResponse(
            success=True,
            operation="create_full",
            message="全量备份成功" if success else "全量备份失败",
            data={"backup_success": success, "backup_type": "full"}
        )
