"""查询相关的DTO类。

定义查询请求、响应和过滤条件的数据传输对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..models.base_model import BaseModel


@dataclass
class EndpointFilter:
    """端点过滤条件。"""

    method_filter: Optional[str] = None
    path_filter: Optional[str] = None
    name_filter: Optional[str] = None
    query_filter: Optional[str] = None
    group_id: Optional[str] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，只包含非空值。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None and not key.startswith('_') and key not in ['created_at', 'updated_at']:
                result[key] = value
        return result

    def is_empty(self) -> bool:
        """检查是否没有设置任何过滤条件。"""
        return not any([
            self.method_filter,
            self.path_filter,
            self.name_filter,
            self.query_filter,
            self.group_id
        ])

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，只包含非空值。"""
        result = {}
        if self.method_filter:
            result["method_filter"] = self.method_filter
        if self.path_filter:
            result["path_filter"] = self.path_filter
        if self.name_filter:
            result["name_filter"] = self.name_filter
        if self.query_filter:
            result["query_filter"] = self.query_filter
        if self.group_id:
            result["group_id"] = self.group_id
        return result


@dataclass
class QueryRequest:
    """查询请求对象。"""

    query_type: str  # 'api_details', 'endpoints', 'resource_tree', 'groups'
    filters: Optional[EndpointFilter] = None
    limit: int = 50
    page: int = 1
    search: Optional[str] = None

    def __post_init__(self):
        """初始化后的处理。"""
        if self.filters is None:
            self.filters = EndpointFilter()

    def validate(self) -> bool:
        """验证查询请求。"""
        # 查询类型必须有效
        valid_types = {'api_details', 'endpoints', 'resource_tree', 'groups'}
        if self.query_type not in valid_types:
            return False

        # 分页参数必须合理
        if self.limit < 1 or self.limit > 1000:
            return False
        if self.page < 1:
            return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        valid_types = {'api_details', 'endpoints', 'resource_tree', 'groups'}
        if self.query_type not in valid_types:
            errors.append(f"不支持的查询类型: {self.query_type}")

        if self.limit < 1 or self.limit > 1000:
            errors.append("限制数量必须在1-1000之间")

        if self.page < 1:
            errors.append("页码必须大于等于1")

        return errors


@dataclass
class ApiEndpointSummary:
    """API端点摘要信息。"""

    id: Optional[str] = None
    method: str = ""
    path: str = ""
    name: Optional[str] = None
    display: str = ""
    group_id: Optional[str] = None

    @property
    def full_path(self) -> str:
        """获取完整路径。"""
        return f"{self.method} {self.path}" if self.method and self.path else self.path or ""


@dataclass
class QueryResponse:
    """查询响应对象。"""

    success: bool = False
    query_type: str = ""
    total_count: int = 0
    filtered_count: int = 0
    returned_count: int = 0
    page: int = 1
    limit: int = 50
    has_more: bool = False
    filters_applied: Optional[EndpointFilter] = None
    results: List[Any] = field(default_factory=list)
    summary: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """初始化后的处理。"""
        if self.filters_applied is None:
            self.filters_applied = EndpointFilter()

    @property
    def is_paginated(self) -> bool:
        """检查是否为分页结果。"""
        return self.page > 1 or self.has_more

    @property
    def current_page_size(self) -> int:
        """获取当前页大小。"""
        return len(self.results)

    @property
    def has_error(self) -> bool:
        """检查是否有错误。"""
        return not self.success

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
