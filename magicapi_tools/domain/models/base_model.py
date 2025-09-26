"""基础模型类。

提供所有领域模型的通用功能和基础结构。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime


@dataclass
class BaseModel:
    """基础模型类，提供通用功能。"""

    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self):
        """初始化后的处理。"""
        # 子类可以重写此方法进行额外初始化
        pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, BaseModel):
                    result[key] = value.to_dict()
                elif isinstance(value, list):
                    result[key] = [item.to_dict() if isinstance(item, BaseModel) else item for item in value]
                else:
                    result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """从字典创建模型实例。"""
        # 基本实现，子类可以重写以提供更复杂的转换逻辑
        kwargs = {}
        for key, value in data.items():
            if hasattr(cls, key):
                kwargs[key] = value
        return cls(**kwargs)

    def validate(self) -> bool:
        """验证模型数据的有效性。

        Returns:
            验证是否通过
        """
        return True  # 基本实现，子类重写

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。

        Returns:
            错误信息列表
        """
        return []  # 基本实现，子类重写
