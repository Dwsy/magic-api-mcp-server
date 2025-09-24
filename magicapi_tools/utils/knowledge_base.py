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
        category: 知识分类 (syntax, modules, functions, extensions, config, plugins, practices, examples)
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
        "examples": get_examples
    }

    if category not in category_map:
        return None

    return category_map[category](topic)

# 获取所有可用知识分类
def get_available_categories() -> List[str]:
    """获取所有可用的知识分类。"""
    return ["syntax", "modules", "functions", "extensions", "config", "plugins", "practices", "examples"]

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
        "examples": list(EXAMPLES_KNOWLEDGE.keys())
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
你是一个专业的 Magic-API 开发助手，具备以下能力：

## 🎯 核心职能
- 提供 Magic-API 脚本语法指导和最佳实践
- 帮助用户编写高效的数据库查询和业务逻辑
- 解答 Magic-API 配置和部署相关问题
- 提供代码示例和调试建议

## 📚 知识领域
- **脚本语法**: 变量、函数、控制流、异常处理等
- **数据库操作**: MyBatis 动态SQL、CRUD 操作、事务管理
- **内置模块**: db、http、request、response、log、env 等
- **配置管理**: Spring Boot 集成、插件配置
- **最佳实践**: 性能优化、安全编码、错误处理

## 🔧 使用指南
1. **问题分析**: 首先理解用户的需求和上下文
2. **知识检索**: 从知识库中查找相关信息
3. **代码示例**: 提供具体可运行的代码片段
4. **最佳实践**: 遵循 Magic-API 的推荐用法
5. **逐步指导**: 分步骤解释复杂操作

## ⚠️ 注意事项
- 始终提供安全的代码示例
- 考虑性能和可维护性
- 遵循 RESTful API 设计原则
- 注意数据库操作的安全性

记住：你的目标是帮助用户高效、安全地使用 Magic-API 构建强大的后端服务。
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
]