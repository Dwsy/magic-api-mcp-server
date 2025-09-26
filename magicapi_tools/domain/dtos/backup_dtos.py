"""备份相关的DTO类。

定义备份操作、历史查询等的数据传输对象。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..models.base_model import BaseModel


@dataclass
class BackupOperationRequest:
    """备份操作请求对象。"""

    operation: str  # 'list', 'history', 'content', 'rollback', 'create_full'
    backup_id: Optional[str] = None
    timestamp: Optional[int] = None
    filter_text: Optional[str] = None
    name_filter: Optional[str] = None
    limit: int = 10

    def validate(self) -> bool:
        """验证备份操作请求。"""
        # 操作类型必须有效
        valid_operations = {'list', 'history', 'content', 'rollback', 'create_full'}
        if self.operation not in valid_operations:
            return False

        # 不同操作的必需参数
        if self.operation in ['history', 'content', 'rollback']:
            if not self.backup_id:
                return False
        if self.operation == 'content':
            if self.timestamp is None:
                return False
        if self.operation == 'rollback':
            if self.timestamp is None:
                return False

        return True

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        errors = []

        valid_operations = {'list', 'history', 'content', 'rollback', 'create_full'}
        if self.operation not in valid_operations:
            errors.append(f"不支持的备份操作: {self.operation}")

        if self.operation in ['history', 'content', 'rollback']:
            if not self.backup_id:
                errors.append("备份ID不能为空")

        if self.operation == 'content':
            if self.timestamp is None:
                errors.append("时间戳不能为空")

        if self.operation == 'rollback':
            if self.timestamp is None:
                errors.append("时间戳不能为空")

        return errors


@dataclass
class BackupHistoryRequest:
    """备份历史查询请求对象。"""

    backup_id: str
    limit: int = 50

    def validate(self) -> bool:
        """验证历史查询请求。"""
        return bool(self.backup_id and self.backup_id.strip())

    def get_validation_errors(self) -> list[str]:
        """获取验证错误信息。"""
        if not self.backup_id or not self.backup_id.strip():
            return ["备份ID不能为空"]
        return []


@dataclass
class BackupInfo:
    """备份信息对象。"""

    id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    tag: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        """从字典创建备份信息对象。"""
        if not isinstance(data, dict):
            return cls()

        # 处理时间字段
        create_time = None
        if data.get('create_time'):
            try:
                create_time = datetime.fromisoformat(str(data['create_time']).replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass

        return cls(
            id=data.get('id'),
            type=data.get('type'),
            name=data.get('name'),
            create_by=data.get('createBy'),
            create_time=create_time,
            tag=data.get('tag')
        )


@dataclass
class BackupOperationResponse:
    """备份操作响应对象。"""

    success: bool = False
    operation: str = ""
    backup_id: Optional[str] = None
    timestamp: Optional[int] = None
    message: str = ""
    data: Optional[Any] = None
    backups: List[BackupInfo] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """初始化后的处理。"""
        # 将字典转换为BackupInfo对象
        if self.backups and len(self.backups) > 0 and isinstance(self.backups[0], dict):
            self.backups = [BackupInfo.from_dict(item) for item in self.backups]

    @property
    def has_error(self) -> bool:
        """检查是否有错误。"""
        return not self.success

    @property
    def backup_count(self) -> int:
        """获取备份数量。"""
        return len(self.backups)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif key == "backups":
                    result[key] = [backup.to_dict() if hasattr(backup, 'to_dict') else backup for backup in value]
                else:
                    result[key] = value
        return result
