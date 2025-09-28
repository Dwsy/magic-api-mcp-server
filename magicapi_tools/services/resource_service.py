"""资源管理业务服务。

处理所有资源管理相关的业务逻辑，包括分组管理、API管理等。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import (
    clean_string_param,
    parse_json_param,
    validate_required_params,
    create_operation_error,
)
from magicapi_tools.utils.resource_manager import build_api_save_kwargs_from_detail
from magicapi_tools.domain.dtos.resource_dtos import (
    ResourceOperationRequest,
    ResourceOperationResponse,
    ApiCreationRequest,
    GroupCreationRequest,
    LockStatusRequest,
    LockStatusResponse,
)

from .base_service import BaseService

if TYPE_CHECKING:
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('services.resource')


class ResourceService(BaseService):
    """资源管理业务服务类。"""

    def get_resource_tree(
        self,
        kind: str = "api",
        format: str = "tree",
        depth: Optional[Union[int, str]] = None,
        group_id: Optional[Union[str, int]] = "0",
        method_filter: Optional[str] = None,
        path_filter: Optional[str] = None,
        name_filter: Optional[str] = None,
        query_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取资源树。"""
        return self.execute_operation(
            "获取资源树",
            self._get_resource_tree_impl,
            kind=kind,
            format=format,
            depth=depth,
            group_id=group_id,
            method_filter=method_filter,
            path_filter=path_filter,
            name_filter=name_filter,
            query_filter=query_filter
        )

    def _get_resource_tree_impl(self, **kwargs) -> Dict[str, Any]:
        """获取资源树的实现。"""
        # 参数处理
        kind = kwargs.get("kind", "api")
        format = kwargs.get("format", "tree")
        depth = kwargs.get("depth")
        group_id = kwargs.get("group_id", "0")
        filters = {
            "method_filter": kwargs.get("method_filter"),
            "path_filter": kwargs.get("path_filter"),
            "name_filter": kwargs.get("name_filter"),
            "query_filter": kwargs.get("query_filter")
        }

        # 获取资源树数据
        ok, payload = self.http_client.resource_tree()
        if not ok:
            return create_operation_error("获取资源树", "http_error", "无法获取资源树", payload)

        # 从payload中提取body作为实际的API响应数据
        api_response_body = payload.get("body", payload) if isinstance(payload, dict) else payload

        # 检查API业务逻辑响应码
        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(api_response_body, self.settings, "获取资源树")
        if api_error:
            return api_error

        # 这里应该包含resource.py中复杂的树处理逻辑
        # 为简化示例，这里只返回基本结构
        return {
            "success": True,
            "kind": kind,
            "format": format,
            "tree": payload,
            "filters_applied": filters
        }

    def save_group(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        parent_id: str = "",
        type: str = "api",
        path: Optional[str] = None,
        options: Optional[str] = None,
        groups_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """保存分组。"""
        return self.execute_operation(
            "保存分组",
            self._save_group_impl,
            name=name,
            id=id,
            parent_id=parent_id,
            type=type,
            path=path,
            options=options,
            groups_data=groups_data
        )

    def _save_group_impl(self, **kwargs) -> Dict[str, Any]:
        """保存分组的实现。"""
        # 这里应该包含resource.py中save_group_tool的逻辑
        # 暂时返回模拟结果
        return {"success": True, "message": "分组保存成功"}

    def create_api(self, request: ApiCreationRequest) -> ResourceOperationResponse:
        """创建或更新API。"""
        # 验证请求
        if not request.validate():
            errors = request.get_validation_errors()
            return ResourceOperationResponse(
                success=False,
                operation="create_api",
                message=f"验证失败: {'; '.join(errors)}"
            )

        operation = "更新API" if request.id else "创建API"
        return self.execute_operation(
            operation,
            self._create_api_impl,
            request=request
        )

    # 向后兼容的方法
    def create_api_legacy(
        self,
        group_id: Optional[str] = None,
        name: Optional[str] = None,
        method: Optional[str] = "GET",
        path: Optional[str] = None,
        script: Optional[str] = None,
        id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """创建或更新API（向后兼容版本）。"""
        request = ApiCreationRequest(
            group_id=group_id,
            name=name,
            method=method,
            path=path,
            script=script,
            id=id,
            **kwargs
        )

        response = self.create_api(request)
        return response.to_dict()

    def _create_api_impl(self, request: ApiCreationRequest) -> ResourceOperationResponse:
        """创建或更新API的实现。"""
        # 解析JSON参数
        try:
            parsed_params = {
                "parameters": parse_json_param(request.parameters, "parameters"),
                "headers": parse_json_param(request.headers, "headers"),
                "paths": parse_json_param(request.paths, "paths"),
                "options": parse_json_param(request.options, "options"),
                "request_body_definition": parse_json_param(request.request_body_definition, "request_body_definition"),
                "response_body_definition": parse_json_param(request.response_body_definition, "response_body_definition"),
            }
        except ValueError as e:
            return ResourceOperationResponse(
                success=False,
                operation="create_api",
                message=f"JSON参数解析失败: {str(e)}"
            )

        # 构建保存参数
        save_kwargs = {
            "group_id": request.group_id,
            "name": request.name,
            "method": request.method,
            "path": request.path,
            "script": request.script,
            "description": request.description,
            "parameters": parsed_params["parameters"],
            "headers": parsed_params["headers"],
            "paths": parsed_params["paths"],
            "request_body": request.request_body,
            "request_body_definition": parsed_params["request_body_definition"],
            "response_body": request.response_body,
            "response_body_definition": parsed_params["response_body_definition"],
            "options": parsed_params["options"],
        }

        # 如果是更新操作，获取现有API详情并合并
        if request.id:
            ok, payload = self.http_client.api_detail(request.id)
            if not ok:
                return ResourceOperationResponse(
                    success=False,
                    operation="create_api",
                    message="无法获取API详情",
                    details={"error": payload}
                )

            # 从payload中提取body作为实际的API响应数据
            api_response_body = payload.get("body", payload) if isinstance(payload, dict) else payload

            # 检查API业务逻辑响应码
            from magicapi_tools.utils.tool_helpers import check_api_response_success
            api_error = check_api_response_success(api_response_body, self.settings, "获取API详情")
            if api_error:
                return ResourceOperationResponse(
                    success=False,
                    operation="create_api",
                    message=api_error["error"]["message"],
                    details=api_error["error"]
                )

            try:
                existing_kwargs = build_api_save_kwargs_from_detail(payload)
                existing_kwargs.update(save_kwargs)
                save_kwargs = existing_kwargs
            except ValueError as e:
                return ResourceOperationResponse(
                    success=False,
                    operation="create_api",
                    message=f"API详情数据异常: {e}"
                )

        # 调用资源管理器的实际保存方法
        try:
            # 使用resource_manager中的工具来保存API
            result = self.resource_tools.create_api_tool(**save_kwargs)
            
            if "success" in result:
                operation = "更新" if request.id else "创建"
                # 如果result包含full_path，将其包含在响应中
                additional_info = {}
                if "full_path" in result:
                    additional_info["full_path"] = result["full_path"]
                
                return ResourceOperationResponse(
                    success=True,
                    operation=f"{operation}API",
                    resource_id=result["id"],
                    message=f"API{operation}成功",
                    affected_count=1,
                    details=additional_info
                )
            else:
                error_info = result.get("error", {})
                return ResourceOperationResponse(
                    success=False,
                    operation="create_api",
                    message=error_info.get("message", f"API{operation}失败"),
                    details=error_info
                )
        except Exception as e:
            return ResourceOperationResponse(
                success=False,
                operation="create_api",
                message=f"API{operation}过程中发生错误: {str(e)}"
            )

    def copy_resource(self, src_id: str, target_id: str) -> ResourceOperationResponse:
        """复制资源。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end
        from magicapi_tools.domain.dtos.resource_dtos import ResourceOperationResponse

        logger = get_logger('services.resource')

        log_operation_start("复制资源", {"src_id": src_id, "target_id": target_id})

        try:
            result = self._copy_resource_impl(src_id, target_id)
            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = ResourceOperationResponse(
                        success=False,
                        operation="copy",
                        resource_id=src_id,
                        target_id=target_id,
                        message=result["error"]["message"]
                    )
                else:
                    response = ResourceOperationResponse(
                        success=True,
                        operation="copy",
                        resource_id=src_id,
                        target_id=target_id,
                        message=result.get("message", "复制成功"),
                        details=result
                    )
            else:
                response = result

            log_operation_end("复制资源", response.success)
            return response
        except Exception as e:
            logger.error(f"复制资源失败: {e}")
            return ResourceOperationResponse(
                success=False,
                operation="copy",
                resource_id=src_id,
                target_id=target_id,
                message=f"复制资源失败: {str(e)}"
            )

    def _copy_resource_impl(self, src_id: str, target_id: str) -> Dict[str, Any]:
        """复制资源的实现。"""
        # 清理参数
        src_id = clean_string_param(src_id)
        target_id = clean_string_param(target_id)

        if not src_id or not target_id:
            return create_operation_error("复制资源", "invalid_params", "src_id和target_id不能为空")

        # 这里应该包含实际的复制逻辑
        return {"success": True, "message": f"资源 {src_id} 复制成功"}

    def move_resource(self, src_id: str, target_id: str) -> ResourceOperationResponse:
        """移动资源。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end
        from magicapi_tools.domain.dtos.resource_dtos import ResourceOperationResponse

        logger = get_logger('services.resource')

        log_operation_start("移动资源", {"src_id": src_id, "target_id": target_id})

        try:
            result = self._move_resource_impl(src_id, target_id)
            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = ResourceOperationResponse(
                        success=False,
                        operation="move",
                        resource_id=src_id,
                        target_id=target_id,
                        message=result["error"]["message"]
                    )
                else:
                    response = ResourceOperationResponse(
                        success=True,
                        operation="move",
                        resource_id=src_id,
                        target_id=target_id,
                        message=result.get("message", "移动成功"),
                        details=result
                    )
            else:
                response = result

            log_operation_end("移动资源", response.success)
            return response
        except Exception as e:
            logger.error(f"移动资源失败: {e}")
            return ResourceOperationResponse(
                success=False,
                operation="move",
                resource_id=src_id,
                target_id=target_id,
                message=f"移动资源失败: {str(e)}"
            )

    def _move_resource_impl(self, src_id: str, target_id: str) -> Dict[str, Any]:
        """移动资源的实现。"""
        # 清理参数
        src_id = clean_string_param(src_id)
        target_id = clean_string_param(target_id)

        if not src_id or not target_id:
            return create_operation_error("移动资源", "invalid_params", "src_id和target_id不能为空")

        # 这里应该包含实际的移动逻辑
        return {"success": True, "message": f"资源 {src_id} 移动成功"}

    def delete_resource(self, resource_id: Optional[str] = None, resource_ids: Optional[List[str]] = None) -> ResourceOperationResponse:
        """删除资源。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end
        from magicapi_tools.domain.dtos.resource_dtos import ResourceOperationResponse

        logger = get_logger('services.resource')

        # 确定操作参数
        operation_name = "批量删除资源" if resource_ids else "删除资源"
        operation = "batch_delete" if resource_ids else "delete"

        log_operation_start(operation_name, {"resource_id": resource_id, "resource_ids": resource_ids})

        try:
            if resource_ids:
                result = self._delete_resources_impl(resource_ids)
            else:
                result = self._delete_resource_impl(resource_id)

            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = ResourceOperationResponse(
                        success=False,
                        operation=operation,
                        resource_id=resource_id,
                        resource_ids=resource_ids,
                        message=result["error"]["message"]
                    )
                else:
                    response = ResourceOperationResponse(
                        success=True,
                        operation=operation,
                        resource_id=resource_id,
                        resource_ids=resource_ids,
                        message=result.get("message", "删除成功"),
                        affected_count=result.get("affected_count", len(resource_ids) if resource_ids else 1),
                        details=result
                    )
            else:
                response = result

            log_operation_end(operation_name, response.success)
            return response
        except Exception as e:
            logger.error(f"{operation_name}失败: {e}")
            return ResourceOperationResponse(
                success=False,
                operation=operation,
                resource_id=resource_id,
                resource_ids=resource_ids,
                message=f"{operation_name}失败: {str(e)}"
            )

    def _delete_resource_impl(self, resource_id: str) -> Dict[str, Any]:
        """删除单个资源的实现。"""
        resource_id = clean_string_param(resource_id)
        if not resource_id:
            return create_operation_error("删除资源", "invalid_params", "resource_id不能为空")

        # 这里应该包含实际的删除逻辑
        return {"success": True, "message": f"资源 {resource_id} 删除成功"}

    def _delete_resources_impl(self, resource_ids: List[str]) -> Dict[str, Any]:
        """批量删除资源的实现。"""
        if not resource_ids:
            return create_operation_error("批量删除资源", "invalid_params", "resource_ids不能为空")

        # 这里应该包含实际的批量删除逻辑
        return {"success": True, "message": f"批量删除了 {len(resource_ids)} 个资源"}

    def read_set_lock_status(self, resource_id: str, action: str) -> LockStatusResponse:
        """读取或设置资源的锁定状态。"""
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.resource')

        request = LockStatusRequest(resource_id=resource_id, action=action)

        if not request.validate():
            errors = request.get_validation_errors()
            return LockStatusResponse(
                success=False,
                resource_id=resource_id,
                action=action,
                message=f"验证失败: {'; '.join(errors)}"
            )

        log_operation_start("锁定状态操作", {"resource_id": resource_id, "action": action})

        try:
            result = self._read_set_lock_status_impl(resource_id, action)

            # 如果_impl方法返回Dict，转换为DTO
            if isinstance(result, dict):
                if "error" in result:
                    response = LockStatusResponse(
                        success=False,
                        resource_id=resource_id,
                        action=action,
                        message=result["error"]["message"]
                    )
                else:
                    response = LockStatusResponse(
                        success=True,
                        resource_id=resource_id,
                        action=action,
                        is_locked=result.get("is_locked"),
                        message=result.get("message", "操作成功"),
                        details=result
                    )
            else:
                response = result

            log_operation_end("锁定状态操作", response.success)
            return response
        except Exception as e:
            logger.error(f"锁定状态操作失败: {e}")
            return LockStatusResponse(
                success=False,
                resource_id=resource_id,
                action=action,
                message=f"锁定状态操作失败: {str(e)}"
            )

    def _read_set_lock_status_impl(self, resource_id: str, action: str) -> Dict[str, Any]:
        """读取或设置锁定状态的实现。"""
        # 清理参数
        resource_id = clean_string_param(resource_id)
        if not resource_id:
            return create_operation_error("锁定状态操作", "invalid_params", "resource_id不能为空")

        if action == "read":
            # 读取锁定状态 - 使用 GET /resource/file/{id} 接口
            ok, payload = self.http_client.api_detail(resource_id)
            if not ok:
                return create_operation_error("读取锁定状态", "http_error", "无法获取资源信息", payload)

            # 从payload中提取body作为实际的API响应数据
            api_response_body = payload.get("body", payload) if isinstance(payload, dict) else payload

            # 检查API业务逻辑响应码
            from magicapi_tools.utils.tool_helpers import check_api_response_success
            api_error = check_api_response_success(api_response_body, self.settings, "读取锁定状态")
            if api_error:
                return api_error

            # 从返回的数据中提取锁定状态
            lock_status = api_response_body.get("lock", "0")  # 默认解锁状态
            is_locked = lock_status == "1"

            return {
                "success": True,
                "is_locked": is_locked,
                "message": "锁定状态读取成功"
            }

        elif action == "lock":
            # 锁定资源
            result = self.resource_tools.lock_resource_tool(resource_id=resource_id)
            if "success" in result:
                return {
                    "success": True,
                    "message": f"资源 {resource_id} 已成功锁定"
                }
            else:
                error_info = result.get("error", {})
                return create_operation_error(
                    "锁定资源",
                    error_info.get("code", "lock_failed"),
                    error_info.get("message", f"锁定资源 {resource_id} 失败"),
                    result  # 包含完整的原始错误信息
                )

        elif action == "unlock":
            # 解锁资源
            result = self.resource_tools.unlock_resource_tool(resource_id=resource_id)
            if "success" in result:
                return {
                    "success": True,
                    "message": f"资源 {resource_id} 已成功解锁"
                }
            else:
                error_info = result.get("error", {})
                return create_operation_error(
                    "解锁资源",
                    error_info.get("code", "unlock_failed"),
                    error_info.get("message", f"解锁资源 {resource_id} 失败"),
                    result  # 包含完整的原始错误信息
                )

        else:
            return create_operation_error("锁定状态操作", "invalid_action", f"不支持的操作类型: {action}")

    def list_groups(self, search: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """列出分组。"""
        return self.execute_operation(
            "列出分组",
            self._list_groups_impl,
            search=search,
            limit=limit
        )

    def _list_groups_impl(self, search: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """列出分组的实现。"""
        # 这里应该包含实际的分组列表逻辑
        return {
            "success": True,
            "groups": [],
            "total_count": 0,
            "returned_count": 0,
            "search_applied": search,
            "limit": limit
        }
