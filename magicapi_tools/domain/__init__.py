"""领域模型层。

定义业务实体、数据传输对象(DTO)和业务规则。
提供类型安全的数据结构和业务逻辑验证。
"""

from .dtos.api_dtos import (
    ApiCallRequest,
    ApiCallResponse,
    WebSocketLogConfig,
    ApiEndpointInfo,
)
from .dtos.resource_dtos import (
    ResourceOperationRequest,
    ResourceOperationResponse,
    ApiCreationRequest,
    GroupCreationRequest,
)
from .dtos.query_dtos import (
    QueryRequest,
    QueryResponse,
    EndpointFilter,
)
from .dtos.backup_dtos import (
    BackupOperationRequest,
    BackupOperationResponse,
    BackupHistoryRequest,
)
from .dtos.debug_dtos import (
    DebugSessionRequest,
    DebugExecutionRequest,
    DebugStatusResponse,
)
from .models.base_model import BaseModel

__all__ = [
    # API DTOs
    "ApiCallRequest",
    "ApiCallResponse",
    "WebSocketLogConfig",
    "ApiEndpointInfo",

    # Resource DTOs
    "ResourceOperationRequest",
    "ResourceOperationResponse",
    "ApiCreationRequest",
    "GroupCreationRequest",

    # Query DTOs
    "QueryRequest",
    "QueryResponse",
    "EndpointFilter",

    # Backup DTOs
    "BackupOperationRequest",
    "BackupOperationResponse",
    "BackupHistoryRequest",

    # Debug DTOs
    "DebugSessionRequest",
    "DebugExecutionRequest",
    "DebugStatusResponse",

    # Base models
    "BaseModel",
]
