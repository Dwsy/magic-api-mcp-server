"""服务基类。

提供所有业务服务通用的基础功能和工具方法。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import (
    create_operation_error,
    handle_tool_exception,
    log_operation_start,
    log_operation_end,
)

if TYPE_CHECKING:
    from magicapi_mcp.tool_registry import ToolContext

logger = get_logger('services.base')


class BaseService:
    """服务基类，提供通用功能。"""

    def __init__(self, context: "ToolContext"):
        """初始化服务。

        Args:
            context: 工具上下文，包含HTTP客户端等依赖
        """
        self.context = context
        self.http_client = context.http_client
        self.settings = context.settings

    def execute_operation(self, operation_name: str, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """执行操作的统一模板方法。

        Args:
            operation_name: 操作名称
            operation_func: 要执行的操作函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            操作结果
        """
        log_operation_start(operation_name, kwargs)

        try:
            result = operation_func(*args, **kwargs)
            log_operation_end(operation_name, "success" in result if isinstance(result, dict) else True)
            return result
        except Exception as e:
            return handle_tool_exception(operation_name, e)

    def validate_response(self, ok: bool, payload: Any, operation: str) -> Optional[Dict[str, Any]]:
        """验证HTTP响应。

        Args:
            ok: 请求是否成功
            payload: 响应数据
            operation: 操作名称

        Returns:
            如果验证失败返回错误信息，否则返回None
        """
        if not ok:
            return create_operation_error(operation, "http_error", "HTTP请求失败", payload)

        if isinstance(payload, dict) and payload.get("code") != 1:
            error_msg = payload.get("message", "API调用失败")
            error_code = payload.get("code", "api_error")
            return create_operation_error(operation, str(error_code), error_msg, payload.get("data"))

        return None

    def extract_data_from_response(self, payload: Any, default: Any = None) -> Any:
        """从响应中提取数据。

        Args:
            payload: 响应payload
            default: 默认值

        Returns:
            提取的数据或默认值
        """
        if isinstance(payload, dict):
            return payload.get("data", default)
        return payload if payload is not None else default
