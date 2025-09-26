"""API相关的DTO类。

定义API调用、响应和配置的数据传输对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..models.base_model import BaseModel


@dataclass
class WebSocketLogConfig:
    """WebSocket日志配置。"""

    pre_wait: float = 0.1  # 调用前等待时间（秒）
    post_wait: float = 1.5  # 调用后等待时间（秒）
    enabled: bool = True  # 是否启用日志捕获

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketLogConfig':
        """从字典创建配置对象。"""
        if isinstance(data, str):
            # 如果是字符串，尝试解析为JSON
            import json
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return cls()  # 返回默认配置

        if not isinstance(data, dict):
            return cls()  # 返回默认配置

        return cls(
            pre_wait=data.get("pre", 0.1),
            post_wait=data.get("post", 1.5),
            enabled=data.get("enabled", True)
        )


@dataclass
class ApiCallRequest:
    """API调用请求对象。"""

    method: str
    path: Optional[str] = None
    api_id: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    headers: Optional[Dict[str, str]] = None
    ws_log_config: Optional[WebSocketLogConfig] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self):
        """初始化后的处理。"""
        if self.ws_log_config is None:
            self.ws_log_config = WebSocketLogConfig()
        elif isinstance(self.ws_log_config, dict):
            self.ws_log_config = WebSocketLogConfig.from_dict(self.ws_log_config)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApiCallRequest':
        """从字典创建请求对象。"""
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        # 处理ws_log_config
        ws_config = data.get("ws_log_config")
        if isinstance(ws_config, dict):
            ws_config = WebSocketLogConfig.from_dict(ws_config)

        return cls(
            method=data.get("method", "GET"),
            path=data.get("path"),
            api_id=data.get("api_id"),
            params=data.get("params"),
            data=data.get("data"),
            headers=data.get("headers"),
            ws_log_config=ws_config
        )

    def validate(self) -> bool:
        """验证请求参数的有效性。"""
        # 必须提供method
        if not self.method or not self.method.strip():
            return False

        # 必须提供path或api_id之一
        if not self.path and not self.api_id:
            return False

        # method必须是有效的HTTP方法
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if self.method.upper() not in valid_methods:
            return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []
        if not self.method or not self.method.strip():
            errors.append("HTTP方法不能为空")

        if not self.path and not self.api_id:
            errors.append("必须提供API路径(path)或接口ID(api_id)")

        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if self.method and self.method.upper() not in valid_methods:
            errors.append(f"不支持的HTTP方法: {self.method}")

        return errors


@dataclass
class ApiEndpointInfo:
    """API端点信息。"""

    id: Optional[str] = None
    method: str = ""
    path: str = ""
    name: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    script: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    headers: Optional[List[Dict[str, Any]]] = None
    paths: Optional[List[Dict[str, Any]]] = None
    request_body: Optional[str] = None
    request_body_definition: Optional[Dict[str, Any]] = None
    response_body: Optional[str] = None
    response_body_definition: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, Any]]] = None

    @property
    def full_path(self) -> str:
        """获取完整的API路径。"""
        return f"{self.method} {self.path}" if self.method and self.path else self.path or ""


@dataclass
class ApiCallResponse:
    """API调用响应对象。"""

    success: bool = False
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None
    ws_logs: Optional[List[Dict[str, Any]]] = None
    endpoint_info: Optional[ApiEndpointInfo] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self):
        """初始化后的处理。"""
        if self.endpoint_info and isinstance(self.endpoint_info, dict):
            self.endpoint_info = ApiEndpointInfo(**self.endpoint_info)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result

    @property
    def has_error(self) -> bool:
        """检查是否有错误。"""
        return not self.success or self.error is not None

    @property
    def error_message(self) -> Optional[str]:
        """获取错误消息。"""
        if self.error and isinstance(self.error, dict):
            return self.error.get("message")
        elif isinstance(self.error, str):
            return self.error
        return None

    @property
    def status_code(self) -> Optional[int]:
        """获取HTTP状态码。"""
        if self.error and isinstance(self.error, dict):
            return self.error.get("code")
        return None
