"""Magic-API 文档和知识库相关 MCP 工具。

此模块提供全面的Magic-API文档查询和知识获取功能，包括：
- 脚本语法文档和示例
- 内置模块API文档
- 函数库使用说明
- 类型扩展功能介绍
- 配置选项说明
- 插件系统文档
- 最佳实践和常见问题解答
- 使用示例和代码片段

主要工具：
- get_script_syntax: 获取Magic-API脚本语法说明
- get_module_api: 获取内置模块的API文档
- get_function_docs: 获取内置函数库文档
- get_extension_docs: 获取类型扩展功能文档
- get_config_docs: 获取配置选项说明
- get_plugin_docs: 获取插件系统文档
- get_best_practices: 获取最佳实践指南
- get_pitfalls: 获取常见问题和陷阱
- get_workflow: 获取工作流模板
- list_examples: 列出所有可用示例
- get_examples: 获取特定类型的示例代码
- get_docs: 获取官方文档索引和内容
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import Field

from magicapi_tools.utils.knowledge_base import (
    # 向后兼容接口
    MAGIC_SCRIPT_SYNTAX,
    get_best_practices,
    get_docs,
    get_pitfalls,
    get_syntax,
    get_workflow,
    list_examples,
    # 新的统一接口
    get_knowledge,
    get_available_categories,
    get_category_topics,
    # 子模块接口
    get_module_api,
    get_function_docs,
    get_extension_docs,
    get_config_docs,
    get_plugin_docs,
    get_examples,
    # 新增的辅助函数
    get_script_syntax_examples,
    get_mybatis_dynamic_sql_examples,
    get_module_examples,
    get_spring_integration_examples,
    get_custom_result_examples,
    get_redis_plugin_examples,
    get_advanced_operations_examples,
)
from magicapi_tools.utils.kb_syntax import get_full_syntax_rules as get_full_syntax_from_kb

def get_full_syntax_rules(locale: str = "zh-CN") -> Dict[str, Any]:
    """获取完整的Magic-Script语法规则。

    从kb_syntax.py中获取配置化的语法规则，
    这是专门为大模型编写代码前强制获取的完整语法规则。

    Args:
        locale: 语言设置，默认为zh-CN

    Returns:
        包含完整语法规则的字典
    """
    return get_full_syntax_from_kb(locale)

from magicapi_tools.utils.kb_modules import MODULES_KNOWLEDGE
from magicapi_tools.utils import error_response

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from magicapi_mcp.tool_registry import ToolContext


class DocumentationTools:
    """文档相关工具模块。"""

    def register_tools(self, mcp_app: "FastMCP", context: "ToolContext") -> None:  # pragma: no cover - 装饰器环境
        """注册文档相关工具。"""

        @mcp_app.tool(
            name="get_magic_script_syntax",
            description="查询 Magic-Script 编程语言的语法规则和使用示例",
            tags={"syntax", "documentation", "scripting", "language"},
            meta={"version": "2.1", "category": "syntax", "author": "system"},
            annotations={
                "title": "脚本语法查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def syntax(
            topic: Annotated[
                str,
                Field(description="要查询的语法主题，如'variables'、'loops'、'functions'等；使用'full'获取完整语法规则", min_length=1)
            ],
            locale: Annotated[
                str,
                Field(description="文档语言选择", default="zh-CN")
            ] = "zh-CN"
        ) -> Dict[str, Any]:
            # 强制返回全量语法规则的特殊处理
            if topic.lower() == "full":
                return get_full_syntax_rules(locale)

            data = get_syntax(topic)
            if not data:
                available_topics = ", ".join(MAGIC_SCRIPT_SYNTAX.keys())
                return error_response("not_found", f"未找到主题 '{topic}' 的语法信息。可用主题：{available_topics}, full(完整语法)")
            result = {"topic": topic, "locale": locale}
            result.update(data)
            return result

        @mcp_app.tool(
            name="get_full_magic_script_syntax",
            description="强制获取完整的Magic-Script语法规则 - 大模型编写代码前必须调用此工具以确保语法准确性",
            tags={"syntax", "documentation", "scripting", "language", "mandatory", "full-rules"},
            meta={"version": "2.1", "category": "syntax", "author": "system", "mandatory": True},
            annotations={
                "title": "强制完整语法规则获取",
                "readOnlyHint": True,
                "openWorldHint": False,
                "mandatory": True,
                "description": "大模型编写任何Magic-Script代码前必须先调用此工具获取完整语法规则"
            }
        )
        def get_full_syntax(locale: Annotated[
            str,
            Field(description="文档语言选择", default="zh-CN")
        ] = "zh-CN") -> Dict[str, Any]:
            """强制获取完整的Magic-Script语法规则。

            ⚠️ 重要：大模型在编写任何Magic-Script代码前必须调用此工具获取完整语法规则。
            Magic-Script是一种小众语言，语法规则独特，必须确保准确理解后再编写代码。

            Args:
                locale: 语言设置，默认为zh-CN

            Returns:
                包含完整语法规则的字典
            """
            return get_full_syntax_rules(locale)

        @mcp_app.tool(
            name="get_magic_script_examples",
            description="获取 Magic-Script 的场景示例代码，支持按类型和关键词过滤",
            tags={"examples", "documentation", "scripting", "tutorials"},
            meta={"version": "2.1", "category": "examples", "author": "system"},
            annotations={
                "title": "脚本示例查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def examples(
            kind: Annotated[
                str,
                Field(description="示例分类，如'api'、'database'、'workflow'等", min_length=1)
            ],
            keyword: Annotated[
                Optional[str],
                Field(description="关键词过滤，用于在示例中搜索特定内容", min_length=1)
            ] = None
        ) -> Dict[str, Any]:
            sample_list = list_examples(kind)
            if keyword:
                keyword_lower = keyword.lower()
                sample_list = [
                    sample
                    for sample in sample_list
                    if keyword_lower in sample.get("title", "").lower()
                    or keyword_lower in sample.get("notes", "").lower()
                    or keyword_lower in sample.get("code", "").lower()
                ]
            if not sample_list:
                return error_response("not_found", f"未找到 {kind} 分类的示例")
            return {"kind": kind, "examples": sample_list}

        @mcp_app.tool(
            name="get_magic_api_docs",
            description="获取 Magic-API 官方文档索引和详细内容",
            tags={"documentation", "api", "reference", "official"},
            meta={"version": "2.1", "category": "docs", "author": "system"},
            annotations={
                "title": "官方文档查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def docs(
            index_only: Annotated[
                bool,
                Field(description="是否只返回文档索引，true时只返回目录，false时返回完整内容", default=True)
            ] = True
        ) -> Dict[str, Any]:
            return get_docs(index_only)

        @mcp_app.tool(
            name="get_best_practices",
            description="获取 Magic-API 开发的最佳实践指南",
            tags={"best-practices", "guidelines", "development", "tips"},
            meta={"version": "2.1", "category": "guidance", "author": "system"},
            annotations={
                "title": "最佳实践指南",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def best_practices() -> List[Dict[str, Any]]:
            """获取最佳实践列表"""
            return get_best_practices()

        @mcp_app.tool(
            name="get_common_pitfalls",
            description="获取 Magic-API 开发中常见的坑点和注意事项",
            tags={"pitfalls", "warnings", "troubleshooting", "errors"},
            meta={"version": "2.1", "category": "guidance", "author": "system"},
            annotations={
                "title": "常见问题指南",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def pitfalls() -> List[Dict[str, Any]]:
            """获取常见坑点列表"""
            return get_pitfalls()

        @mcp_app.tool(
            name="get_development_workflow",
            description="获取 Magic-API 开发的标准化工作流程和命令示例",
            tags={"workflow", "development", "process", "guide"},
            meta={"version": "2.1", "category": "guidance", "author": "system"},
            annotations={
                "title": "开发工作流指南",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def workflow(
            task: Annotated[
                str,
                Field(description="工作流任务类型，如'api_script_development'、'setup_database'、'deploy_app'等", min_length=1)
            ] = "api_script_development",
            with_commands: Annotated[
                bool,
                Field(description="是否包含具体的命令示例，true时返回可执行的命令，false时只返回步骤描述", default=True)
            ] = True
        ) -> Dict[str, Any]:
            flow = get_workflow(task)
            response: Dict[str, Any] = {
                "task": task,
                "description": flow.get("description"),
                "steps": flow.get("steps", []),
                "core_workflow_overview": {
                    "summary": "MagicAPI MCP Agent 核心工作流：需求洞察 → 语法对齐 → 资源定位 → 实现调试 → 结果反馈",
                    "stages": [
                        {
                            "stage": "需求洞察",
                            "recommended_tools": [
                                "documentation.search_knowledge",
                                "documentation.get_development_workflow",
                                "documentation.get_best_practices"
                            ],
                            "goal": "明确业务目标、限制条件，以及适用的标准流程"
                        },
                        {
                            "stage": "语法对齐",
                            "recommended_tools": [
                                "documentation.get_full_magic_script_syntax",
                                "documentation.get_script_syntax"
                            ],
                            "goal": "确保Magic-Script语法与特性被准确掌握，避免JS思维误差"
                        },
                        {
                            "stage": "资源定位",
                            "recommended_tools": [
                                "resource_management.get_resource_tree",
                                "query.get_api_details_by_path",
                                "query.search_api_endpoints"
                            ],
                            "goal": "查找现有接口与脚本，确认依赖与影响范围"
                        },
                        {
                            "stage": "实现与调试",
                            "recommended_tools": [
                                 "resource_management.save_api_endpoint",
                                "api.call_magic_api",
                                "debug.call_api_with_debug",
                                "debug.set_breakpoint"
                            ],
                            "goal": "完成脚本编写/修改，并通过断点、调试调用确保行为正确"
                        },
                        {
                            "stage": "结果反馈",
                            "recommended_tools": [
                                "documentation.get_practices_guide",
                                "documentation.get_common_pitfalls",
                                "backup.list_backups"
                            ],
                            "goal": "输出可溯源的结论，总结风险与回滚保障"
                        }
                    ]
                }
            }
            if with_commands:
                response["commands"] = [
                    "python3 extract_api_paths.py --url --query '关键词'",
                    "python3 extract_api_paths.py --detail <接口ID>",
                    "python3 magic_api_resource_manager.py --list-tree --depth 2",
                    "python3 magic_api_client.py --call 'GET /path' --params 'k=v'",
                    "python3 magic_api_debug_client.py",
                ]
            return response

        @mcp_app.tool(
            name="get_module_api_docs",
            description="获取指定Magic-API内置模块的API文档",
            tags={"modules", "api", "reference", "built-in"},
            meta={"version": "2.1", "category": "modules", "author": "system"},
            annotations={
                "title": "模块API文档查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def module_api(
            module_name: Annotated[
                str,
                Field(description="模块名称，如'db'、'http'、'response'、'request'、'log'、'env'、'magic'", min_length=1)
            ]
        ) -> Dict[str, Any]:
            module_info = get_module_api(module_name)
            if not module_info:
                available_modules = list(MODULES_KNOWLEDGE.keys())
                return error_response("not_found", f"未找到模块 '{module_name}' 的API文档。可用模块：{', '.join(available_modules)}")
            return module_info

        @mcp_app.tool(
            name="list_available_modules",
            description="获取所有可用的Magic-API内置模块列表",
            tags={"modules", "list", "overview", "built-in"},
            meta={"version": "2.1", "category": "modules", "author": "system"},
            annotations={
                "title": "模块列表查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def list_modules() -> Dict[str, Any]:
            """获取所有可用模块的详细信息"""
            from magicapi_tools.utils.kb_modules import list_available_modules, get_auto_import_modules
            return {
                "all_modules": list_available_modules(),
                "auto_import_modules": get_auto_import_modules(),
                "module_count": len(list_available_modules())
            }

        @mcp_app.tool(
            name="get_function_docs",
            description="获取Magic-API内置函数库文档",
            tags={"functions", "api", "reference", "built-in"},
            meta={"version": "2.1", "category": "functions", "author": "system"},
            annotations={
                "title": "函数库文档查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def function_docs(
            category: Annotated[
                Optional[str],
                Field(description="函数分类，可选值: aggregation, date, string, array, math, other, range")
            ] = None
        ) -> Dict[str, Any]:
            return get_function_docs(category)

        @mcp_app.tool(
            name="get_extension_docs",
            description="获取Magic-API类型扩展功能文档",
            tags={"extensions", "types", "api", "enhancements"},
            meta={"version": "2.1", "category": "extensions", "author": "system"},
            enabled=False,
            annotations={
                "title": "类型扩展文档查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def extension_docs(
            type_name: Annotated[
                Optional[str],
                Field(description="类型名称，可选值: object, number, collection, string, date")
            ] = None
        ) -> Dict[str, Any]:
            return get_extension_docs(type_name)

        @mcp_app.tool(
            name="get_config_docs",
            description="获取Magic-API配置相关文档",
            tags={"config", "settings", "reference", "configuration"},
            meta={"version": "2.1", "category": "config", "author": "system"},
            enabled=False,
            annotations={
                "title": "配置文档查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def config_docs(
            category: Annotated[
                Optional[str],
                Field(description="配置分类，可选值: spring_boot, editor_config, database, cache, cluster, cors, debug, backup")
            ] = None
        ) -> Dict[str, Any]:
            return get_config_docs(category)

        @mcp_app.tool(
            name="get_plugin_docs",
            description="获取Magic-API插件系统文档",
            tags={"plugins", "extensions", "reference", "add-ons"},
            meta={"version": "2.1", "category": "plugins", "author": "system"},
            enabled=False,
            annotations={
                "title": "插件文档查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def plugin_docs(
            plugin_name: Annotated[
                Optional[str],
                Field(description="插件名称，可选值: cluster, task, redis, mongodb, elasticsearch, swagger, springdoc, git, nebula")
            ] = None
        ) -> Dict[str, Any]:
            return get_plugin_docs(plugin_name)

        @mcp_app.tool(
            name="get_examples",
            description="获取Magic-API所有类型的使用示例",
            tags={"examples", "tutorials", "best-practices", "code-samples", "syntax", "modules", "integration"},
            meta={"version": "2.2", "category": "examples", "author": "system"},
            annotations={
                "title": "统一示例查询",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def examples(
            category: Annotated[
                Optional[str],
                Field(description="示例分类，可选值: script_syntax(脚本语法), module_usage(模块使用), spring_integration(Spring集成), mybatis_dynamic_sql(MyBatis动态SQL), custom_results(自定义结果), redis_plugin(Redis插件), advanced_operations(高级操作), basic_crud(基础CRUD), advanced_queries(高级查询), transactions(事务), lambda_operations(Lambda操作), async_operations(异步操作), file_operations(文件操作), api_integration(API集成)")
            ] = None,
            topic: Annotated[
                Optional[str],
                Field(description="具体主题，当指定category时可进一步筛选具体示例")
            ] = None
        ) -> Dict[str, Any]:
            """获取各种类型的Magic-API使用示例"""
            if not category:
                # 返回所有示例的概览
                return {
                    "categories": {
                        "script_syntax": {"description": "脚本语法示例", "count": len(get_script_syntax_examples())},
                        "module_usage": {"description": "模块使用示例", "count": len(get_module_examples())},
                        "spring_integration": {"description": "Spring集成示例", "count": len(get_spring_integration_examples())},
                        "mybatis_dynamic_sql": {"description": "MyBatis动态SQL示例", "count": len(get_mybatis_dynamic_sql_examples())},
                        "custom_results": {"description": "自定义结果示例", "count": len(get_custom_result_examples())},
                        "redis_plugin": {"description": "Redis插件示例", "count": len(get_redis_plugin_examples())},
                        "advanced_operations": {"description": "高级操作示例", "count": len(get_advanced_operations_examples())},
                        "basic_crud": {"description": "基础CRUD操作", "count": len(get_examples("basic_crud") or [])},
                        "advanced_queries": {"description": "高级查询", "count": len(get_examples("advanced_queries") or [])},
                        "transactions": {"description": "事务操作", "count": len(get_examples("transactions") or [])},
                        "lambda_operations": {"description": "Lambda操作", "count": len(get_examples("lambda_operations") or [])},
                        "async_operations": {"description": "异步操作", "count": len(get_examples("async_operations") or [])},
                        "file_operations": {"description": "文件操作", "count": len(get_examples("file_operations") or [])},
                        "api_integration": {"description": "API集成", "count": len(get_examples("api_integration") or [])}
                    },
                    "total_categories": 14
                }

            # 根据分类返回具体示例
            category_map = {
                "script_syntax": get_script_syntax_examples,
                "module_usage": get_module_examples,
                "spring_integration": get_spring_integration_examples,
                "mybatis_dynamic_sql": get_mybatis_dynamic_sql_examples,
                "custom_results": get_custom_result_examples,
                "redis_plugin": get_redis_plugin_examples,
                "advanced_operations": get_advanced_operations_examples,
                "basic_crud": lambda: get_examples("basic_crud"),
                "advanced_queries": lambda: get_examples("advanced_queries"),
                "transactions": lambda: get_examples("transactions"),
                "lambda_operations": lambda: get_examples("lambda_operations"),
                "async_operations": lambda: get_examples("async_operations"),
                "file_operations": lambda: get_examples("file_operations"),
                "api_integration": lambda: get_examples("api_integration")
            }

            if category not in category_map:
                available_categories = list(category_map.keys())
                return error_response("not_found", f"未找到示例分类 '{category}'。可用分类：{', '.join(available_categories)}")

            examples_data = category_map[category]()
            if not examples_data:
                return error_response("not_found", f"分类 '{category}' 下暂无示例")

            # 如果指定了具体主题，进一步筛选
            if topic:
                if isinstance(examples_data, dict):
                    if topic in examples_data:
                        return {"category": category, "topic": topic, "example": examples_data[topic]}
                    else:
                        available_topics = list(examples_data.keys())
                        return error_response("not_found", f"未找到主题 '{topic}'。可用主题：{', '.join(available_topics)}")
                else:
                    # 对于列表类型的数据，尝试按title或name匹配
                    filtered = [ex for ex in examples_data if ex.get("title") == topic or ex.get("name") == topic]
                    if filtered:
                        return {"category": category, "topic": topic, "example": filtered[0]}
                    else:
                        return error_response("not_found", f"在 '{category}' 分类中未找到主题 '{topic}'")

            return {"category": category, "examples": examples_data}

        @mcp_app.tool(
            name="search_knowledge",
            description="在Magic-API知识库中进行全文搜索",
            tags={"search", "knowledge", "query", "full-text"},
            meta={"version": "2.1", "category": "search", "author": "system"},
            annotations={
                "title": "知识库全文搜索",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def search_knowledge(
            keyword: Annotated[
                str,
                Field(description="搜索关键词", min_length=1)
            ],
            category: Annotated[
                Optional[str],
                Field(description="限定搜索分类，可选值: syntax, modules, functions, extensions, config, plugins, practices, examples")
            ] = None
        ) -> Dict[str, Any]:
            results = []

            # 搜索语法
            if not category or category == "syntax":
                for topic, data in MAGIC_SCRIPT_SYNTAX.items():
                    if keyword.lower() in topic.lower() or keyword.lower() in data.get("summary", "").lower():
                        results.append({
                            "category": "syntax",
                            "topic": topic,
                            "title": data.get("title"),
                            "summary": data.get("summary"),
                            "type": "语法"
                        })

            # 搜索模块
            if not category or category == "modules":
                from magicapi_tools.utils.kb_modules import MODULES_KNOWLEDGE
                for module_name, module_data in MODULES_KNOWLEDGE.items():
                    if keyword.lower() in module_name.lower() or keyword.lower() in module_data.get("description", "").lower():
                        results.append({
                            "category": "modules",
                            "topic": module_name,
                            "title": module_data.get("title"),
                            "description": module_data.get("description"),
                            "type": "模块"
                        })

            # 搜索函数
            if not category or category == "functions":
                from magicapi_tools.utils.kb_functions import search_functions
                func_results = search_functions(keyword)
                for result in func_results:
                    results.append({
                        "category": "functions",
                        "topic": result.get("category"),
                        "title": result.get("name"),
                        "description": result.get("description"),
                        "type": "函数"
                    })

            # 搜索扩展
            if not category or category == "extensions":
                from magicapi_tools.utils.kb_extensions import search_extensions
                ext_results = search_extensions(keyword)
                for result in ext_results:
                    results.append({
                        "category": "extensions",
                        "topic": result.get("type"),
                        "title": result.get("method"),
                        "description": result.get("description"),
                        "type": "扩展"
                    })

            # 搜索实践
            if not category or category == "practices":
                from magicapi_tools.utils.kb_practices import search_practices
                practice_results = search_practices(keyword)
                for result in practice_results:
                    results.append({
                        "category": "practices",
                        "topic": result.get("category"),
                        "content": result.get("content"),
                        "type": "实践"
                    })

            return {
                "keyword": keyword,
                "category": category,
                "results": results,
                "total": len(results)
            }

        @mcp_app.tool(
            name="get_knowledge_overview",
            description="获取Magic-API知识库概览信息",
            tags={"overview", "summary", "guide", "catalog"},
            meta={"version": "2.1", "category": "overview", "author": "system"},
            annotations={
                "title": "知识库概览",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def knowledge_overview() -> Dict[str, Any]:
            """获取知识库概览"""
            categories = get_available_categories()

            overview = {
                "total_categories": len(categories),
                "categories": {}
            }

            for category in categories:
                topics = get_category_topics(category)
                overview["categories"][category] = {
                    "topic_count": len(topics),
                    "topics": topics[:10],  # 只显示前10个主题
                    "has_more": len(topics) > 10
                }

            return overview

        @mcp_app.tool(
            name="get_practices_guide",
            description="获取Magic-API开发实践指南，包括性能优化、安全实践和调试指南",
            tags={"practices", "performance", "security", "debugging", "optimization", "best-practices"},
            meta={"version": "2.1", "category": "practices", "author": "system"},
            annotations={
                "title": "开发实践指南",
                "readOnlyHint": True,
                "openWorldHint": False
            }
        )
        def practices_guide(
            guide_type: Annotated[
                str,
                Field(description="指南类型: performance(性能优化), security(安全实践), debugging(调试指南)", default="performance")
            ] = "performance",
            category: Annotated[
                Optional[str],
                Field(description="具体分类，根据guide_type而定: performance时可选database/cache/async/memory, security时可选input_validation/authentication/authorization/data_protection, debugging时可选common_issues/debug_tools")
            ] = None
        ) -> Dict[str, Any]:
            """获取各种开发实践指南"""
            from magicapi_tools.utils.kb_practices import get_performance_tips, get_security_practices, get_debugging_guide

            if guide_type == "performance":
                return {"guide_type": "performance", "performance_tips": get_performance_tips(category)}
            elif guide_type == "security":
                return {"guide_type": "security", "security_practices": get_security_practices(category)}
            elif guide_type == "debugging":
                return {"guide_type": "debugging", "debugging_guide": get_debugging_guide(category)}
            else:
                return error_response("invalid_type", f"无效的指南类型 '{guide_type}'。支持的类型: performance, security, debugging")
