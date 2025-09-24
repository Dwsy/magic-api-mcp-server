"""Magic-API MCP 工具注册模块集合。

此包包含所有Magic-API MCP Server提供的工具模块：

核心工具模块：
├── SystemTools - 系统信息和元数据工具
├── DocumentationTools - 文档查询和知识库工具
├── ApiTools - API调用和测试工具
├── ResourceManagementTools - 资源管理和操作工具
├── QueryTools - 资源查询和检索工具
├── DebugTools - 调试和断点管理工具
├── SearchTools - 内容搜索和定位工具
├── BackupTools - 备份管理和恢复工具
├── ClassMethodTools - Java类和方法检索工具
└── CodeGenerationTools - 代码生成工具（当前禁用）

辅助模块：
└── common - 共享的工具辅助函数

每个工具模块都实现register_tools方法，向MCP应用注册相应的工具函数。
所有工具都遵循统一的错误处理和响应格式规范。
"""

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

