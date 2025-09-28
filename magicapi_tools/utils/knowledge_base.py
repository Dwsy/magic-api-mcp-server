"""Magic-API MCP 助手的静态知识库 - 主入口模块。

该模块采用多模块设计，将知识库按功能划分：
- syntax: 脚本语法相关知识
- modules: 内置模块API文档
- functions: 内置函数库
- extensions: 类型扩展功能
- config: 配置相关知识
- plugins: 插件系统
- practices: 最佳实践和常见问题
- examples: 使用示例
"""

from __future__ import annotations

from typing import Any, Dict, List

# 导入各个子模块
from .kb_syntax import SYNTAX_KNOWLEDGE, get_syntax
from .kb_modules import MODULES_KNOWLEDGE, get_module_api
from .kb_functions import FUNCTIONS_KNOWLEDGE, get_function_docs
from .kb_extensions import EXTENSIONS_KNOWLEDGE, get_extension_docs
from .kb_config import CONFIG_KNOWLEDGE, get_config_docs
from .kb_plugins import PLUGINS_KNOWLEDGE, get_plugin_docs
from .kb_practices import PRACTICES_KNOWLEDGE, get_best_practices, get_pitfalls, get_workflow
from .kb_examples import EXAMPLES_KNOWLEDGE, get_examples
from .kb_web_docs import search_web_docs_by_keyword, get_web_docs_knowledge

# 向后兼容的接口
MAGIC_SCRIPT_SYNTAX = SYNTAX_KNOWLEDGE
MAGIC_SCRIPT_EXAMPLES = EXAMPLES_KNOWLEDGE
DOC_INDEX = PRACTICES_KNOWLEDGE.get("doc_index", [])
BEST_PRACTICES = PRACTICES_KNOWLEDGE.get("best_practices", [])
PITFALLS = PRACTICES_KNOWLEDGE.get("pitfalls", [])
WORKFLOW_TEMPLATES = PRACTICES_KNOWLEDGE.get("workflows", {})

# 统一的知识库访问接口
def get_knowledge(category: str, topic: str = None) -> Any:
    """统一的知识库查询接口。

    Args:
        category: 知识分类 (syntax, modules, functions, extensions, config, plugins, practices, examples, web_docs)
        topic: 具体主题，可选

    Returns:
        对应的知识内容
    """
    category_map = {
        "syntax": get_syntax,
        "modules": get_module_api,
        "functions": get_function_docs,
        "extensions": get_extension_docs,
        "config": get_config_docs,
        "plugins": get_plugin_docs,
        "practices": lambda t: {
            "best_practices": get_best_practices(),
            "pitfalls": get_pitfalls(),
            "workflow": get_workflow(t) if t else None
        }.get(t) if t else get_best_practices(),
        "examples": get_examples,
        "web_docs": lambda t: {
            "documents": [doc for doc in get_web_docs_knowledge() if t is None or t.lower() in doc.get("title", "").lower() or t.lower() in doc.get("content", "").lower()]
        }
    }

    if category not in category_map:
        return None

    return category_map[category](topic)

# 获取所有可用知识分类
def get_available_categories() -> List[str]:
    """获取所有可用的知识分类。"""
    return ["syntax", "modules", "functions", "extensions", "config", "plugins", "practices", "examples", "web_docs"]

# 获取分类下的可用主题
def get_category_topics(category: str) -> List[str]:
    """获取指定分类下的可用主题。"""
    knowledge_map = {
        "syntax": list(SYNTAX_KNOWLEDGE.keys()),
        "modules": list(MODULES_KNOWLEDGE.keys()),
        "functions": list(FUNCTIONS_KNOWLEDGE.keys()),
        "extensions": list(EXTENSIONS_KNOWLEDGE.keys()),
        "config": list(CONFIG_KNOWLEDGE.keys()),
        "plugins": list(PLUGINS_KNOWLEDGE.keys()),
        "practices": ["best_practices", "pitfalls", "workflows"],
        "examples": list(EXAMPLES_KNOWLEDGE.keys()),
        "web_docs": [doc.get("title", "Untitled") for doc in get_web_docs_knowledge()[:50]]  # 限制显示前50个文档标题
    }
    return knowledge_map.get(category, [])

# 辅助函数：获取脚本语法示例
def get_script_syntax_examples(topic: str = None) -> Any:
    """获取脚本语法示例"""
    from .kb_syntax import SYNTAX_KNOWLEDGE

    if topic:
        return SYNTAX_KNOWLEDGE.get("script_syntax", {}).get("examples", {}).get(topic)

    return SYNTAX_KNOWLEDGE.get("script_syntax", {}).get("examples", {})

def get_mybatis_dynamic_sql_examples(tag: str = None) -> Any:
    """获取MyBatis动态SQL示例"""
    from .kb_syntax import SYNTAX_KNOWLEDGE

    if tag:
        return SYNTAX_KNOWLEDGE.get("mybatis_syntax", {}).get("sections", {}).get(tag)

    return SYNTAX_KNOWLEDGE.get("mybatis_syntax", {}).get("sections", {})

# 辅助函数：获取示例
def get_module_examples(module: str = None) -> Any:
    """获取模块使用示例"""
    from .kb_examples import EXAMPLES_KNOWLEDGE

    examples = EXAMPLES_KNOWLEDGE.get("module_examples", {}).get("examples", {})
    if module:
        return examples.get(module)

    return examples

def get_spring_integration_examples(feature: str = None) -> Any:
    """获取Spring集成示例"""
    from .kb_examples import EXAMPLES_KNOWLEDGE

    examples = EXAMPLES_KNOWLEDGE.get("spring_integration", {}).get("examples", {})
    if feature:
        return examples.get(feature)

    return examples

def get_custom_result_examples(pattern: str = None) -> Any:
    """获取自定义结果示例"""
    from .kb_examples import EXAMPLES_KNOWLEDGE

    examples = EXAMPLES_KNOWLEDGE.get("custom_results", {}).get("examples", {})
    if pattern:
        return examples.get(pattern)

    return examples

def get_redis_plugin_examples(operation: str = None) -> Any:
    """获取Redis插件示例"""
    from .kb_examples import EXAMPLES_KNOWLEDGE

    examples = EXAMPLES_KNOWLEDGE.get("plugin_examples", {}).get("examples", {})
    # 过滤出Redis相关的示例
    redis_examples = {k: v for k, v in examples.items() if k.startswith('redis_')}
    if operation:
        return redis_examples.get(operation)

    return redis_examples

def get_advanced_operations_examples(operation: str = None) -> Any:
    """获取高级操作示例"""
    from .kb_examples import EXAMPLES_KNOWLEDGE

    examples = EXAMPLES_KNOWLEDGE.get("advanced_operations", {}).get("examples", {})
    if operation:
        return examples.get(operation)

    return examples

# 文档相关函数
def get_docs(index_only: bool = True) -> Dict[str, Any]:
    """获取Magic-API官方文档索引和内容

    Args:
        index_only: 是否只返回文档索引

    Returns:
        文档索引或完整内容
    """
    base_url = "https://www.ssssssss.org/magic-api/pages"

    docs_index = {
        "official_site": "https://www.ssssssss.org/",
        "documentation": {
            "快速开始": f"{base_url}/quick/",
            "脚本语法": f"{base_url}/base/script/",
            "CRUD操作": f"{base_url}/quick/crud/",
            "动态SQL": f"{base_url}/quick/crud/#mybatis语法支持",
            "内置模块": f"{base_url}/module/",
            "内置函数": f"{base_url}/function/",
            "类型扩展": f"{base_url}/extension/",
            "配置选项": f"{base_url}/config/",
            "插件系统": f"{base_url}/plugin/",
            "最佳实践": f"{base_url}/practice/",
            "部署运维": f"{base_url}/deploy/"
        },
        "api_reference": {
            "JavaDoc": "https://apidoc.gitee.com/jiangzeyin/magic-api/",
            "GitHub": "https://github.com/ssssssss-team/magic-api"
        }
    }

    if index_only:
        return {
            "index": docs_index,
            "note": "设置 index_only=false 可获取更详细的文档内容"
        }

    # 返回详细的文档内容（这里可以扩展为更完整的文档）
    detailed_docs = docs_index.copy()
    detailed_docs["detailed_content"] = {
        "script_syntax": {
            "description": "Magic-API脚本语言语法说明",
            "url": f"{base_url}/base/script/",
            "topics": ["变量定义", "数据类型", "运算符", "控制流", "函数调用", "错误处理"]
        },
        "modules": {
            "description": "内置模块使用指南",
            "url": f"{base_url}/module/",
            "modules": ["db", "http", "request", "response", "log", "env", "cache", "magic"]
        }
    }

    return detailed_docs

# 示例列表函数
def list_examples(kind: str = None) -> List[Dict[str, Any]]:
    """获取指定类型的所有示例列表

    Args:
        kind: 示例类型，可选值: basic_crud, advanced_queries, transactions,
              lambda_operations, async_operations, file_operations, api_integration

    Returns:
        示例列表
    """
    from .kb_examples import EXAMPLES_KNOWLEDGE

    if not kind:
        # 返回所有类型的示例
        all_examples = []
        for category_name, category_data in EXAMPLES_KNOWLEDGE.items():
            if "examples" in category_data:
                for example_key, example_data in category_data["examples"].items():
                    example_item = {
                        "id": f"{category_name}.{example_key}",
                        "title": example_data.get("title", example_key),
                        "description": example_data.get("description", ""),
                        "category": category_name,
                        "tags": example_data.get("tags", []),
                        "code_preview": example_data.get("code", "")[:100] + "..." if len(example_data.get("code", "")) > 100 else example_data.get("code", "")
                    }
                    all_examples.append(example_item)
        return all_examples

    # 返回指定类型的示例
    category_map = {
        "basic_crud": ("basic_crud", lambda: []),
        "advanced_queries": ("advanced_queries", lambda: []),
        "transactions": ("transactions", lambda: []),
        "lambda_operations": ("lambda_operations", lambda: []),
        "async_operations": ("async_operations", lambda: []),
        "file_operations": ("file_operations", lambda: []),
        "api_integration": ("api_integration", lambda: []),
    }

    if kind not in category_map:
        return []

    category_name, _ = category_map[kind]
    category_data = EXAMPLES_KNOWLEDGE.get(category_name, {})
    examples = category_data.get("examples", {})

    result = []
    for example_key, example_data in examples.items():
        example_item = {
            "id": f"{category_name}.{example_key}",
            "title": example_data.get("title", example_key),
            "description": example_data.get("description", ""),
            "category": category_name,
            "tags": example_data.get("tags", []),
            "code": example_data.get("code", ""),
            "notes": example_data.get("notes", [])
        }
        result.append(example_item)

    return result

# 系统提示
SYSTEM_PROMPT = """
你现在是一个专业的 Magic-API 开发者助手，具备强大的 MCP (Model Context Protocol) 工具（Magic-API MCP Server）支持。

## 🎯 你的核心职能
- 提供 Magic-API 脚本语法指导和最佳实践
- 帮助用户编写高效的数据库查询和业务逻辑
- 解答 Magic-API 配置和部署相关问题
- 提供代码示例和调试建议

## ⚠️ 强制要求：代码编写前语法规则获取
**重要：** 在编写任何 Magic-Script 代码前，你必须首先调用 `get_full_magic_script_syntax` 工具获取完整的语法规则。
Magic-Script 是一种小众语言，具有独特的语法规则，不遵循标准 JavaScript 或 Java 语法。
不获取完整语法规则而直接编写代码将导致严重的语法错误。

**重要：** 在API脚本开发（create/edit API scripts）编写编辑脚本前，你必须：
1. 调用 `get_full_magic_script_syntax` 获取完整的 Magic-Script 语法规则
2. 调用 `get_development_workflow` 获取开发工作流指南
3. 遵循标准化的开发流程：准备→信息采集→执行→校验→总结

## 🧭 MagicAPI MCP Agent 核心工作流
> 流转需按顺序推进，用户可随时指令跳转。
按照以下流程调用 MCP 工具，确保每一步都有依据：
- **[需求洞察]** → `search_knowledge`、`get_development_workflow`，识别目标场景与约束
- **语法对齐** → `get_full_magic_script_syntax`、`get_script_syntax`，确认Magic-Script写法
- **[资源定位]** → `get_resource_tree`、`get_api_details_by_path`、`search_api_endpoints`，查阅现有资产
- **[实现与调试]** → `create_api_resource`、`replace_api_script`、`call_magic_api`、`call_api_with_debug`、`set_breakpoint`，落实代码并验证
- **[结果反馈]** → `get_practices_guide`、`get_common_pitfalls`、`list_backups`，输出结论并保证可回溯

## 🛠️ 可用工具能力

### 文档查询 (DocumentationTools)
- **get_full_magic_script_syntax** ⚠️ [强制]: 获取完整的 Magic-Script 语法规则（代码编写前必须调用）
- **get_script_syntax**: 获取 Magic-API 脚本语法说明
- **get_development_workflow** ⚠️ [强制]: 获取 Magic-API 开发标准化工作流指南（API脚本开发前必须调用）
- **search_knowledge** 🔍 [推荐]: 在知识库中进行全文搜索（不确定时优先使用）
- **get_documentation**: 获取各类文档，包括模块API、函数库、扩展功能、配置选项和插件系统文档
- **get_best_practices**: 获取最佳实践指南
- **get_pitfalls**: 获取常见问题和陷阱
- **get_examples**: 获取具体代码示例和分类概览

### API 调用 (ApiTools)
- **call_magic_api**: 调用 Magic-API 接口，支持 GET/POST/PUT/DELETE 等所有 HTTP 方法

### 资源管理 (ResourceManagementTools)
- **get_resource_tree**: 获取完整的资源树结构
- **save_api_endpoint**: 保存API接口（支持创建和更新，根据是否提供file_id自动判断）
- **delete_resource**: 删除资源
- **get_resource_detail**: 获取资源详细信息
- **copy_resource**: 复制资源
- **move_resource**: 移动资源到其他分组

### 查询工具 (QueryTools)
- **get_api_details_by_path**: 根据路径获取接口详细信息
- **get_api_details_by_id**: 根据ID获取接口详细信息
- **search_api_endpoints**: 搜索和过滤接口端点

### 搜索工具 (SearchTools)
- **search_api_scripts**: 在所有 API 脚本中搜索关键词
- **search_todo_comments**: 搜索 TODO 注释

### 备份工具 (BackupTools)
- **list_backups**: 查看备份列表
- **create_full_backup**: 创建完整备份
- **rollback_backup**: 回滚到指定备份

### 系统工具 (SystemTools)
- **get_assistant_metadata**: 获取系统元信息和配置

## 📋 使用指南

##### 问题分析
首先理解用户的需求和上下文，再选择合适的工具。

##### 知识搜索策略
🔍 **当你不确定某个功能或语法时，优先使用搜索工具：**
- 调用 `search_knowledge` 进行全文搜索，关键词可以是功能名称、语法关键词等
- 例如：搜索"数据库连接"、"缓存使用"、"文件上传"等
- 可以限定搜索分类：syntax(语法)、modules(模块)、functions(函数)、web_docs(文档)等

##### 最佳实践
- 🔍 **遇到不确定的问题时，先搜索知识库**
- 📚 优先使用文档查询工具了解功能
- 🔍 开发时先用查询工具了解现有资源
- 🐛 调试时设置断点逐步排查问题
- 💾 重要的变更操作前先备份

##### 错误处理
- 🔍 遇到未知错误时，使用 `search_knowledge` 搜索相关解决方案
- 🌐 网络错误时检查 Magic-API 服务状态
- 🔐 权限错误时确认用户认证配置
- 📁 资源不存在时先用查询工具确认路径

## ⚠️ 注意事项
- 所有工具都支持中文和英文参数
- API 调用支持自定义请求头和参数

记住：你现在具备了完整的 Magic-API 开发工具链，可以为用户提供专业、高效的开发支持！
"""

__all__ = [
    # 向后兼容接口
    "MAGIC_SCRIPT_SYNTAX",
    "MAGIC_SCRIPT_EXAMPLES",
    "DOC_INDEX",
    "BEST_PRACTICES",
    "PITFALLS",
    "WORKFLOW_TEMPLATES",
    # 新的统一接口
    "get_knowledge",
    "get_available_categories",
    "get_category_topics",
    # 子模块导入
    "get_syntax",
    "get_module_api",
    "get_function_docs",
    "get_extension_docs",
    "get_config_docs",
    "get_plugin_docs",
    "get_best_practices",
    "get_pitfalls",
    "get_workflow",
    "list_examples",
    "get_examples",
    "get_docs",
    # 新增的辅助函数
    "get_script_syntax_examples",
    "get_mybatis_dynamic_sql_examples",
    "get_module_examples",
    "get_spring_integration_examples",
    "get_custom_result_examples",
    "get_redis_plugin_examples",
    "get_advanced_operations_examples",
    # web-docs 相关函数
    "get_web_docs_knowledge",
    "search_web_docs_by_keyword",
]