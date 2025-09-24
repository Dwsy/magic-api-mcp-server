"""Magic-API MCP 工具注册模块集合。"""

from .api import ApiTools
from .backup import BackupTools
from .class_method import ClassMethodTools
# from .code_generation import CodeGenerationTools
from .debug import DebugTools
from .documentation import DocumentationTools
from .query import QueryTools
from .resource import ResourceManagementTools
from .search import SearchTools
from .system import SystemTools

__all__ = [
    "ApiTools",
    "BackupTools",
    "ClassMethodTools",
    # "CodeGenerationTools",
    "DebugTools",
    "DocumentationTools",
    "QueryTools",
    "MagicAPIResourceTools",
    "ResourceManagementTools",
    "SearchTools",
    "SystemTools",
]

from ..utils.resource_manager import MagicAPIResourceTools

