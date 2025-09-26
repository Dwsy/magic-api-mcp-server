"""资源管理相关的DTO类。

定义资源操作、API创建、组管理等的数据传输对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from datetime import datetime

if TYPE_CHECKING:
    from .api_dtos import ApiEndpointInfo


@dataclass
class ResourceOperationRequest:
    """资源操作请求对象。"""

    operation: str  # 操作类型: 'copy', 'move', 'delete'
    resource_id: Optional[str] = None
    resource_ids: Optional[List[str]] = None  # 批量操作时使用
    target_id: Optional[str] = None  # copy/move操作的目标ID
    group_id: Optional[str] = None  # 分组ID，用于过滤

    def validate(self) -> bool:
        """验证请求参数。"""
        # 必须指定操作类型
        if not self.operation:
            return False

        # 不同操作的必需参数
        if self.operation in ['copy', 'move']:
            if not self.resource_id or not self.target_id:
                return False
        elif self.operation == 'delete':
            if not self.resource_id and not self.resource_ids:
                return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        if not self.operation:
            errors.append("操作类型不能为空")

        if self.operation in ['copy', 'move']:
            if not self.resource_id:
                errors.append("资源ID不能为空")
            if not self.target_id:
                errors.append("目标ID不能为空")
        elif self.operation == 'delete':
            if not self.resource_id and not self.resource_ids:
                errors.append("必须提供资源ID或资源ID列表")

        return errors


@dataclass
class ApiCreationRequest:
    """API创建/更新请求对象。"""

    group_id: Optional[str] = None
    name: Optional[str] = None
    method: str = "GET"
    path: Optional[str] = None
    script: Optional[str] = None
    id: Optional[str] = None  # 更新时使用
    description: Optional[str] = None
    parameters: Optional[str] = None  # JSON字符串
    headers: Optional[str] = None  # JSON字符串
    paths: Optional[str] = None  # JSON字符串
    request_body: Optional[str] = None
    request_body_definition: Optional[str] = None  # JSON字符串
    response_body: Optional[str] = None
    response_body_definition: Optional[str] = None  # JSON字符串
    options: Optional[str] = None  # JSON字符串

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """验证API创建请求。"""
        # 创建操作必需字段
        if not self.id:  # 创建操作
            required_fields = [self.group_id, self.name, self.path, self.script]
            if not all(required_fields):
                return False

        # method必须有效
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if self.method.upper() not in valid_methods:
            return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        if not self.id:  # 创建操作
            if not self.group_id:
                errors.append("分组ID不能为空")
            if not self.name:
                errors.append("API名称不能为空")
            if not self.path:
                errors.append("API路径不能为空")
            if not self.script:
                errors.append("脚本内容不能为空")

        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if self.method.upper() not in valid_methods:
            errors.append(f"不支持的HTTP方法: {self.method}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result

    def to_api_endpoint_info(self) -> 'ApiEndpointInfo':
        """转换为API端点信息对象。"""
        # 动态导入以避免循环依赖
        from . import api_dtos
        ApiEndpointInfo = api_dtos.ApiEndpointInfo

        return ApiEndpointInfo(
            id=self.id,
            method=self.method,
            path=self.path,
            name=self.name,
            group_id=self.group_id,
            description=self.description,
            script=self.script,
            request_body=self.request_body,
            response_body=self.response_body,
            # JSON字段会在服务层解析
        )


@dataclass
class GroupCreationRequest:
    """分组创建/更新请求对象。"""

    name: Optional[str] = None
    id: Optional[str] = None  # 更新时使用
    parent_id: str = "0"
    type: str = "api"  # 'api', 'function', 'task', 'datasource'
    path: Optional[str] = None
    options: Optional[str] = None  # JSON字符串

    def validate(self) -> bool:
        """验证分组创建请求。"""
        # 创建操作必需名称
        if not self.id and not self.name:
            return False

        # 类型必须有效
        valid_types = {"api", "function", "task", "datasource"}
        if self.type not in valid_types:
            return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        if not self.id and not self.name:
            errors.append("分组名称不能为空")

        valid_types = {"api", "function", "task", "datasource"}
        if self.type not in valid_types:
            errors.append(f"不支持的分组类型: {self.type}")

        return errors


@dataclass
class LockStatusRequest:
    """锁定状态操作请求对象。"""

    resource_id: str
    action: str  # 'read', 'lock', 'unlock'

    def validate(self) -> bool:
        """验证锁定状态请求。"""
        if not self.resource_id:
            return False

        if self.action not in ['read', 'lock', 'unlock']:
            return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        if not self.resource_id:
            errors.append("资源ID不能为空")

        if self.action not in ['read', 'lock', 'unlock']:
            errors.append(f"不支持的操作类型: {self.action}")

        return errors


@dataclass
class LockStatusResponse:
    """锁定状态操作响应对象。"""

    success: bool = False
    resource_id: str = ""
    action: str = ""
    is_locked: Optional[bool] = None  # 只有read操作时才返回
    message: str = ""
    details: Optional[Dict[str, Any]] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result


@dataclass
class ResourceOperationResponse:
    """资源操作响应对象。"""

    success: bool = False
    operation: str = ""
    resource_id: Optional[str] = None
    target_id: Optional[str] = None
    message: str = ""
    affected_count: int = 0
    details: Optional[Dict[str, Any]] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result

    @property
    def has_error(self) -> bool:
        """检查是否有错误。"""
        return not self.success
