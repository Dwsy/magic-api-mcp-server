"""类和方法检索相关的DTO类。

定义类搜索、类详情查询等的数据传输对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..models.base_model import BaseModel


@dataclass
class ClassSearchRequest:
    """类搜索请求对象。"""

    query_type: str = "list"  # 'list', 'search', 'search_txt', 'detail'
    class_name: Optional[str] = None  # 用于详情查询
    pattern: Optional[str] = None  # 搜索模式
    search_type: str = "keyword"  # 'keyword', 'regex'
    case_sensitive: bool = False
    logic: str = "or"  # 'and', 'or'
    scope: str = "all"  # 'all', 'class', 'method', 'field'
    exact: bool = False
    exclude_pattern: Optional[str] = None
    page: int = 1
    page_size: int = 10
    limit: Optional[int] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """验证搜索请求。"""
        if self.query_type == "detail" and not self.class_name:
            return False

        if self.query_type in ["search", "search_txt"] and not self.pattern:
            return False

        valid_query_types = {"list", "search", "search_txt", "detail"}
        if self.query_type not in valid_query_types:
            return False

        valid_search_types = {"keyword", "regex"}
        if self.search_type not in valid_search_types:
            return False

        valid_scopes = {"all", "class", "method", "field"}
        if self.scope not in valid_scopes:
            return False

        valid_logics = {"and", "or"}
        if self.logic not in valid_logics:
            return False

        if self.page < 1 or self.page_size < 1 or (self.limit is not None and self.limit < 1):
            return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        if self.query_type == "detail" and not self.class_name:
            errors.append("详情查询需要提供类名")

        if self.query_type in ["search", "search_txt"] and not self.pattern:
            errors.append("搜索查询需要提供搜索模式")

        valid_query_types = {"list", "search", "search_txt", "detail"}
        if self.query_type not in valid_query_types:
            errors.append(f"不支持的查询类型: {self.query_type}")

        valid_search_types = {"keyword", "regex"}
        if self.search_type not in valid_search_types:
            errors.append(f"不支持的搜索类型: {self.search_type}")

        valid_scopes = {"all", "class", "method", "field"}
        if self.scope not in valid_scopes:
            errors.append(f"不支持的搜索范围: {self.scope}")

        valid_logics = {"and", "or"}
        if self.logic not in valid_logics:
            errors.append(f"不支持的逻辑操作: {self.logic}")

        if self.page < 1:
            errors.append("页码必须大于等于1")
        if self.page_size < 1:
            errors.append("每页大小必须大于等于1")
        if self.limit is not None and self.limit < 1:
            errors.append("限制数量必须大于等于1")

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


@dataclass
class MethodInfo:
    """方法信息对象。"""

    name: str = ""
    return_type: str = "Object"
    parameters: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "name": self.name,
            "return_type": self.return_type,
            "parameters": self.parameters
        }


@dataclass
class FieldInfo:
    """字段信息对象。"""

    name: str = ""
    type: str = "Object"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "name": self.name,
            "type": self.type
        }


@dataclass
class ClassInfo:
    """类信息对象。"""

    class_name: str = ""
    methods: List[MethodInfo] = field(default_factory=list)
    fields: List[FieldInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "class_name": self.class_name,
            "methods": [method.to_dict() for method in self.methods],
            "fields": [field.to_dict() for field in self.fields]
        }


@dataclass
class ClassSearchResponse:
    """类搜索响应对象。"""

    success: bool = False
    query_type: str = ""
    pattern: Optional[str] = None
    total_count: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    displayed_count: int = 0
    limit: Optional[int] = None
    has_more: bool = False

    # 搜索结果
    classes: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    package_matches: List[str] = field(default_factory=list)
    class_matches: List[str] = field(default_factory=list)
    detailed_matches: List[Dict[str, Any]] = field(default_factory=list)

    # 详情查询结果
    class_details: List[ClassInfo] = field(default_factory=list)

    # 摘要信息
    summary: Optional[Dict[str, Any]] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, list):
                    if key == "class_details":
                        result[key] = [item.to_dict() for item in value]
                    else:
                        result[key] = value
                else:
                    result[key] = value
        return result

    @property
    def has_error(self) -> bool:
        """检查是否有错误。"""
        return not self.success


@dataclass
class ClassDetailRequest:
    """类详情请求对象。"""

    class_name: str

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """验证详情请求。"""
        return bool(self.class_name and self.class_name.strip())

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        if not self.class_name or not self.class_name.strip():
            return ["类名不能为空"]
        return []

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
class ClassDetailResponse:
    """类详情响应对象。"""

    success: bool = False
    class_name: str = ""
    class_details: List[ClassInfo] = field(default_factory=list)
    summary: Optional[Dict[str, Any]] = None

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, list):
                    if key == "class_details":
                        result[key] = [item.to_dict() for item in value]
                    else:
                        result[key] = value
                else:
                    result[key] = value
        return result

    @property
    def has_error(self) -> bool:
        """检查是否有错误。"""
        return not self.success
