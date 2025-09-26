"""MCP 工具辅助函数库。

此模块提供所有工具模块共享的可复用功能函数，
遵循DRY原则，减少代码重复，提高可维护性。

主要功能：
- 参数清理和验证
- 错误响应格式化
- API调用结果处理
- JSON参数解析
- 搜索过滤逻辑
- 日志记录辅助
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Union

from magicapi_tools.logging_config import get_logger
from magicapi_tools.utils import error_response

logger = get_logger('utils.tool_helpers')


# === 参数处理工具 ===

def clean_string_param(value: Optional[Any], default: Optional[str] = None) -> Optional[str]:
    """清理字符串参数，处理空值和空白字符。

    Args:
        value: 输入值
        default: 默认值

    Returns:
        清理后的字符串或默认值
    """
    if value is None:
        return default
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else default
    return str(value).strip() or default


def parse_json_param(value: Optional[str], param_name: str = "parameter") -> Optional[Any]:
    """安全解析JSON参数。

    Args:
        value: JSON字符串
        param_name: 参数名称，用于错误信息

    Returns:
        解析后的对象

    Raises:
        ValueError: JSON格式错误时抛出
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None

    if not isinstance(value, str):
        return value

    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"{param_name} 格式错误: {e}")


def validate_required_params(params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
    """验证必需参数。

    Args:
        params: 参数字典
        required: 必需参数列表

    Returns:
        如果验证失败返回错误信息，否则返回None
    """
    missing = [key for key in required if key not in params or params[key] is None]
    if missing:
        return error_response("invalid_params", f"缺少必需参数: {', '.join(missing)}")
    return None


# === API调用工具 ===

def process_api_response(response: Dict[str, Any], operation: str = "operation") -> Dict[str, Any]:
    """统一处理API响应。

    Args:
        response: HTTP客户端响应
        operation: 操作名称，用于日志

    Returns:
        处理后的结果字典
    """
    if not response.get("status"):
        # HTTP请求失败
        error_info = response.get("body", {})
        logger.error(f"{operation} HTTP请求失败: {error_info.get('message', '未知错误')}")
        return error_response(
            error_info.get("code", "http_error"),
            f"{operation} HTTP请求失败",
            error_info.get("detail")
        )

    data = response.get("body", {})
    if data.get("code") != 1:
        logger.error(f"{operation} API调用失败: {data.get('message', '未知错误')}")
        return error_response(
            data.get("code", -1),
            f"{operation} API调用失败",
            data.get("data")
        )

    return {"success": True, "data": data.get("data")}


def extract_api_detail_data(payload: Optional[Dict[str, Any]], operation: str = "获取详情") -> Optional[Dict[str, Any]]:
    """从API详情响应中提取数据。

    Args:
        payload: API响应payload
        operation: 操作名称

    Returns:
        提取的数据或None
    """
    if payload is None:
        logger.warning(f"{operation}: 响应数据为空")
        return None

    if not isinstance(payload, dict):
        logger.warning(f"{operation}: 响应数据格式异常: {type(payload)}")
        return None

    return payload


# === 错误处理工具 ===

def create_operation_error(operation: str, error_code: str, message: str, detail: Any = None) -> Dict[str, Any]:
    """创建操作错误响应。

    Args:
        operation: 操作名称
        error_code: 错误代码
        message: 错误消息
        detail: 详细信息

    Returns:
        错误响应字典
    """
    logger.error(f"{operation}失败: {message}")
    return error_response(error_code, message, detail)


def handle_tool_exception(operation: str, exc: Exception) -> Dict[str, Any]:
    """处理工具执行异常。

    Args:
        operation: 操作名称
        exc: 异常对象

    Returns:
        错误响应字典
    """
    error_msg = f"{operation}时发生异常: {str(exc)}"
    logger.error(error_msg, exc_info=True)
    return error_response("unexpected_error", error_msg, str(exc))


# === 验证工具 ===

def validate_path_format(path: str, allow_empty: bool = False) -> Optional[str]:
    """验证路径格式。

    Args:
        path: 路径字符串
        allow_empty: 是否允许空路径

    Returns:
        验证后的路径或None（如果验证失败）
    """
    if not path and not allow_empty:
        return None

    if not path:
        return ""

    # 确保路径以/开头
    if not path.startswith("/"):
        path = f"/{path}"

    return path


def validate_breakpoints(breakpoints: Any) -> Optional[List[int]]:
    """验证断点格式。

    Args:
        breakpoints: 断点数据

    Returns:
        验证后的断点列表或None
    """
    if breakpoints is None or breakpoints == "":
        return []

    if isinstance(breakpoints, str):
        try:
            # 尝试解析JSON字符串
            parsed = json.loads(breakpoints)
            if isinstance(parsed, list):
                return [int(bp) for bp in parsed if isinstance(bp, (int, str)) and str(bp).isdigit()]
        except (json.JSONDecodeError, ValueError):
            pass
    elif isinstance(breakpoints, list):
        return [int(bp) for bp in breakpoints if isinstance(bp, (int, str)) and str(bp).isdigit()]

    return []


# === 搜索和过滤工具 ===

def match_keyword(text: str, keyword: str, case_sensitive: bool = False,
                 exact: bool = False, is_regex: bool = False) -> bool:
    """检查文本是否匹配关键词。

    Args:
        text: 待检查文本
        keyword: 关键词
        case_sensitive: 是否区分大小写
        exact: 是否精确匹配
        is_regex: 是否为正则表达式

    Returns:
        是否匹配
    """
    if not text or not keyword:
        return False

    if is_regex:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            return bool(re.search(keyword, text, flags))
        except re.error:
            return False

    if exact:
        if case_sensitive:
            return keyword == text
        else:
            return keyword.lower() == text.lower()

    # 包含匹配
    if case_sensitive:
        return keyword in text
    else:
        return keyword.lower() in text.lower()


def apply_limit_and_filter(items: List[Any], limit: int = 10,
                          filters: Optional[List[callable]] = None) -> List[Any]:
    """应用限制和过滤到项目列表。

    Args:
        items: 项目列表
        limit: 最大数量限制
        filters: 过滤函数列表

    Returns:
        过滤和限制后的列表
    """
    if not items:
        return []

    # 应用过滤器
    if filters:
        for filter_func in filters:
            items = [item for item in items if filter_func(item)]

    # 应用数量限制
    if limit > 0:
        items = items[:limit]

    return items


# === 日志工具 ===

def log_operation_start(operation: str, params: Optional[Dict[str, Any]] = None) -> None:
    """记录操作开始日志。

    Args:
        operation: 操作名称
        params: 操作参数
    """
    logger.info(f"开始执行: {operation}")
    if params:
        # 只记录关键参数，避免敏感信息泄露
        safe_params = {k: v for k, v in params.items()
                      if not any(sensitive in k.lower()
                               for sensitive in ['password', 'token', 'secret', 'key'])}
        logger.debug(f"操作参数: {safe_params}")


def log_operation_end(operation: str, success: bool, result_count: Optional[int] = None) -> None:
    """记录操作结束日志。

    Args:
        operation: 操作名称
        success: 是否成功
        result_count: 结果数量
    """
    status = "成功" if success else "失败"
    if result_count is not None:
        logger.info(f"{operation} {status}, 返回 {result_count} 条结果")
    else:
        logger.info(f"{operation} {status}")


def log_api_call_details(operation: str, api_id: Optional[str] = None,
                        api_name: Optional[str] = None, api_path: Optional[str] = None,
                        method: Optional[str] = None, group_id: Optional[str] = None) -> None:
    """记录API调用详情日志。

    Args:
        operation: 操作类型
        api_id: API ID
        api_name: API名称
        api_path: API路径
        method: HTTP方法
        group_id: 分组ID
    """
    logger.info(f"MCP工具调用: {operation}")
    if api_id:
        logger.info(f"  API ID: {api_id}")
    if api_name:
        logger.info(f"  API名称: {api_name}")
    if api_path:
        logger.info(f"  API路径: {api_path}")
    if method:
        logger.info(f"  HTTP方法: {method}")
    if group_id:
        logger.info(f"  分组ID: {group_id}")


# === 通用工具 ===

def safe_get_nested_value(data: Dict[str, Any], keys: List[str],
                         default: Any = None) -> Any:
    """安全获取嵌套字典的值。

    Args:
        data: 数据字典
        keys: 键路径列表
        default: 默认值

    Returns:
        获取的值或默认值
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def format_api_display(method: Optional[str], path: Optional[str],
                      name: Optional[str] = None) -> str:
    """格式化API显示字符串。

    Args:
        method: HTTP方法
        path: 路径
        name: 名称

    Returns:
        格式化的显示字符串
    """
    display = ""
    if method and path:
        display = f"{method} {path}"
    elif method:
        display = method
    elif path:
        display = path
    else:
        display = "未知API"

    if name and name != path:
        display += f" [{name}]"

    return display


def calculate_pagination(total: int, page: int, page_size: int) -> Dict[str, Any]:
    """计算分页信息。

    Args:
        total: 总数量
        page: 当前页码
        page_size: 每页大小

    Returns:
        分页信息字典
    """
    total_pages = (total + page_size - 1) // page_size
    start_index = (page - 1) * page_size
    end_index = min(start_index + page_size, total)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "start_index": start_index,
        "end_index": end_index,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def is_api_response_success(payload: Any, settings) -> bool:
    """检查API响应是否表示成功。

    支持多种响应格式和可配置的状态码/消息。
    优先级：message="success" > code检查 > status检查 > 错误字段检查 > 默认成功

    Args:
        payload: API响应数据
        settings: MagicAPI配置，包含成功状态码和消息配置

    Returns:
        bool: 是否成功
    """
    if not isinstance(payload, dict):
        return False

    # 🚀 优先级1：检查message字段是否等于"success"（最高优先级）
    message = payload.get("message")
    print(f"优先级1：检查message字段是否等于 message: {message}")
    if message is not None and isinstance(message, str):
        # 直接匹配"success"字符串（不区分大小写）
        print(f"优先级1：检查message字段是否等于 message: {message}")
        if message.strip().lower() == "success":
            print(f"优先级1：检查message字段是否等于 message: {message}")
            return True
        # 如果message不匹配success且包含错误关键字，则失败
        error_keywords = ["error", "fail", "exception", "invalid", "wrong", "failed", "not found", "timeout", "denied", "forbidden"]
        if any(error_keyword in message.lower() for error_keyword in error_keywords):
            print(f"优先级1：检查message字段是否等于 message: {message}")
            return False

    # 🚀 优先级2：检查code字段（可配置的状态码）
    code = payload.get("code")
    if code is not None:
        # 如果code等于配置的成功码，则成功
        if code == settings.api_success_code:
            return True
        # 如果code不等于成功码，则失败
        print(f"优先级2：检查code字段是否等于 code: {code}")
        return False

    # 🚀 优先级3：检查status字段（某些自定义格式）
    status = payload.get("status")
    if status is not None:
        if status == settings.api_success_code:
            return True
        print(f"优先级3：检查status字段是否等于 status = {settings.api_success_code} : {status}")
        return False

    # 🚀 优先级4：检查是否有任何错误相关的字段
    error_fields = ["error", "exception", "failure"]
    for field in error_fields:
        if field in payload:
            print(f"优先级4：检查是否有任何错误相关的字段 field: {field}")
            return False

    # 🚀 优先级5：默认认为是成功的（兼容模式）
    # 这样可以兼容一些没有标准格式的API
    return True


def check_api_response_success(payload: Any, settings, operation: str) -> Optional[Dict[str, Any]]:
    """检查API响应是否成功，如果失败则返回错误响应。

    使用 is_api_response_success 进行检查，如果失败则生成错误响应。

    Args:
        payload: API响应数据
        settings: MagicAPI配置
        operation: 操作名称（用于错误日志）

    Returns:
        Optional[Dict[str, Any]]: 如果失败返回错误响应，否则返回None
    """
    if not isinstance(payload, dict):
        return create_operation_error(operation, "invalid_response", "API返回格式无效", payload)

    # 使用 is_api_response_success 检查是否成功
    if not is_api_response_success(payload, settings):
        # 确定错误原因和消息
        code = payload.get("code")
        message = payload.get("message", "")
        status = payload.get("status")

        if code is not None and code != settings.api_success_code:
            error_message = message or f"API调用失败，响应码: {code}"
            return create_operation_error(operation, str(code), error_message, payload)
        elif message and isinstance(message, str):
            # message 包含错误关键字
            return create_operation_error(operation, "api_error", message, payload)
        elif status is not None and status != settings.api_success_code:
            error_message = message or f"API调用失败，状态码: {status}"
            return create_operation_error(operation, str(status), error_message, payload)
        else:
            # 其他错误情况
            return create_operation_error(operation, "api_error", "API调用失败", payload)

    # 如果都没有问题，返回None表示成功
    return None
