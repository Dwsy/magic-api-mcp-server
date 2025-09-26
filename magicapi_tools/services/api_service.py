"""API业务服务。

处理所有API相关的业务逻辑，包括接口调用、数据处理等。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import (
    clean_string_param,
    log_api_call_details,
    create_operation_error,
)
from magicapi_tools.ws import normalize_breakpoints, resolve_script_id_by_path
from magicapi_tools.domain.dtos.api_dtos import ApiCallRequest, ApiCallResponse

from .base_service import BaseService

if TYPE_CHECKING:
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('services.api')


class ApiService(BaseService):
    """API业务服务类。"""

    def call_api_with_details(self, request: ApiCallRequest) -> ApiCallResponse:
        """调用API接口并返回详细信息。

        Args:
            request: API调用请求对象

        Returns:
            API调用响应对象
        """
        from magicapi_tools.logging_config import get_logger
        from magicapi_tools.utils.tool_helpers import log_operation_start, log_operation_end

        logger = get_logger('services.api')

        # 验证请求
        if not request.validate():
            errors = request.get_validation_errors()
            return ApiCallResponse(
                success=False,
                error={"code": "validation_error", "message": "; ".join(errors)}
            )

        log_operation_start("调用API接口", {"method": request.method, "path": request.path})

        try:
            result = self._call_api_with_details_impl(request)
            log_operation_end("调用API接口", result.success)
            return result
        except Exception as e:
            logger.error(f"调用API接口失败: {e}")
            return ApiCallResponse(
                success=False,
                error={"code": "api_call_error", "message": f"调用API接口失败: {str(e)}"}
            )

    # 保留向后兼容的方法
    def call_api_with_details_legacy(
        self,
        method: str,
        path: Optional[str] = None,
        api_id: Optional[str] = None,
        params: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Any] = None,
        include_ws_logs: Optional[Union[Dict[str, float], str]] = None
    ) -> Dict[str, Any]:
        """调用API接口并返回详细信息（向后兼容版本）。

        Args:
            method: HTTP方法
            path: API路径
            api_id: 接口ID
            params: 查询参数
            data: 请求体数据
            headers: 请求头
            include_ws_logs: WebSocket日志配置

        Returns:
            API调用结果字典
        """
        request = ApiCallRequest(
            method=method,
            path=path,
            api_id=api_id,
            params=params,
            data=data,
            headers=headers,
            ws_log_config=include_ws_logs
        )

        response = self.call_api_with_details(request)
        return response.to_dict()

    def _call_api_with_details_impl(self, request: ApiCallRequest) -> ApiCallResponse:
        """调用API的具体实现。"""

        # 处理api_id优先逻辑
        if request.api_id:
            api_info = self._resolve_api_by_id(request.api_id)
            if "error" in api_info:
                return ApiCallResponse(
                    success=False,
                    error=api_info
                )
            actual_method = api_info["method"]
            actual_path = api_info["path"]
            log_api_call_details("调用API接口", request.api_id, api_info.get("name"), actual_path, actual_method)
        else:
            actual_method = request.method
            actual_path = request.path
            log_api_call_details("调用API接口", None, None, actual_path, actual_method)

        # 准备WebSocket环境
        self.context.ws_manager.ensure_running_sync()

        # 处理请求头和断点
        request_headers, script_id = self._prepare_request_headers(request.headers, request.api_id, actual_path)

        # 配置WebSocket日志捕获
        ws_config = request.ws_log_config
        if not ws_config.enabled:
            pre_wait = 0.0
            post_wait = 0.0
        else:
            pre_wait = ws_config.pre_wait
            post_wait = ws_config.post_wait

        # 执行API调用
        import time
        start_ts = time.time()
        ok, payload = self.http_client.call_api(
            actual_method,
            actual_path,
            params=request.params,
            data=request.data,
            headers=request_headers,
        )

        execution_end = time.time()

        # 等待WebSocket日志
        if post_wait > 0:
            time.sleep(post_wait)

        # 获取WebSocket日志
        ws_logs = []
        if ws_config.enabled:
            logs = self.context.ws_manager.capture_logs_between(
                start_ts, execution_end, pre=pre_wait, post=post_wait
            )
            ws_logs = [{
                "timestamp": msg.timestamp,
                "type": msg.type.value,
                "payload": msg.payload,
            } for msg in logs]

        duration = execution_end - start_ts

        # 处理响应
        if not ok:
            # HTTP调用失败，返回包含详细错误信息的响应体
            if payload is None:
                error_info = {
                    "code": "http_error",
                    "message": "HTTP请求失败：无响应数据",
                    "detail": None,
                    "http_status": "connection_error"
                }
            elif isinstance(payload, str):
                error_info = {
                    "code": "http_error",
                    "message": f"HTTP请求失败：{payload}",
                    "detail": payload,
                    "http_status": "error"
                }
            elif isinstance(payload, dict):
                # 保留原始错误信息，但标准化格式
                error_info = {
                    "code": payload.get("code", "http_error"),
                    "message": payload.get("message", "HTTP请求失败"),
                    "detail": payload.get("detail", payload.get("data")),
                    "http_status": payload.get("status", "http_error")
                }
            else:
                error_info = {
                    "code": "http_error",
                    "message": "HTTP请求失败：未知错误",
                    "detail": str(payload),
                    "http_status": "unknown_error"
                }

            return ApiCallResponse(
                success=False,
                error=error_info,
                duration=duration,
                ws_logs=ws_logs if ws_config.enabled else None
            )

        # HTTP调用成功，但需要检查API业务逻辑响应码
        # 从payload中提取body作为实际的API响应数据
        api_response_body = payload.get("body", payload) if isinstance(payload, dict) else payload

        from magicapi_tools.utils.tool_helpers import check_api_response_success
        api_error = check_api_response_success(api_response_body, self.settings, "调用API接口")
        if api_error:
            return ApiCallResponse(
                success=False,
                error=api_error["error"],
                duration=duration,
                ws_logs=ws_logs if ws_config.enabled else None
            )

        # 真正成功的情况
        if isinstance(api_response_body, dict):
            # 如果body中有data字段，使用data字段的值，否则使用整个body
            data = api_response_body.get("data", api_response_body)
        else:
            data = api_response_body

        return ApiCallResponse(
            success=True,
            data=data,
            duration=duration,
            ws_logs=ws_logs if ws_config.enabled else None
        )

    def _resolve_api_by_id(self, api_id: str) -> Dict[str, Any]:
        """通过ID解析API信息。"""
        ok, payload = self.http_client.api_detail(api_id)
        if not ok:
            return create_operation_error("解析API信息", "api_detail_failed", f"无法获取接口详情: {api_id}")

        if not payload:
            return create_operation_error("解析API信息", "api_not_found", f"接口不存在: {api_id}")

        # 获取基础信息
        method = payload.get("method", "").upper()
        path = payload.get("path", "")
        name = payload.get("name", "")

        if not method or not path:
            return create_operation_error("解析API信息", "invalid_api_data", f"接口数据不完整: {api_id}")

        # 获取完整的路径
        from magicapi_tools.tools.query import _get_full_path_by_api_details
        full_path = _get_full_path_by_api_details(self.http_client, api_id, method, path, name)

        return {
            "method": method,
            "path": full_path,
            "name": name,
            "original_path": path
        }

    def _prepare_request_headers(self, user_headers: Optional[Any], api_id: Optional[str], path: str) -> tuple[Dict[str, str], Optional[str]]:
        """准备请求头。"""
        script_id = (user_headers.get("Magic-Request-Script-Id") if user_headers else None) or api_id
        if not script_id:
            script_id = resolve_script_id_by_path(self.http_client, path)

        if not script_id:
            raise ValueError("无法根据路径定位接口脚本，请提供 api_id")

        breakpoint_header = user_headers.get("Magic-Request-Breakpoints") if user_headers else None
        normalized_breakpoints = normalize_breakpoints(breakpoint_header) if breakpoint_header else ""

        base_headers = {
            "Magic-Request-Script-Id": script_id,
            "Magic-Request-Breakpoints": normalized_breakpoints,
        }

        request_headers = self.context.ws_manager.build_request_headers(base_headers)
        if isinstance(user_headers, dict):
            request_headers.update({k: v for k, v in user_headers.items() if v is not None})

        return request_headers, script_id
