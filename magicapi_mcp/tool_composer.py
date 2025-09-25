"""Magic-API 工具组合器 - 组合和编排工具模块。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from magicapi_mcp.settings import DEFAULT_SETTINGS, MagicAPISettings
from magicapi_mcp.tool_registry import tool_registry
from magicapi_tools.tools import ApiTools
from magicapi_tools.tools import BackupTools
from magicapi_tools.tools import ClassMethodTools
# from magicapi_tools.tools import CodeGenerationTools
from magicapi_tools.tools import DebugTools
from magicapi_tools.tools import DocumentationTools
from magicapi_tools.tools import QueryTools
from magicapi_tools.tools import ResourceManagementTools
from magicapi_tools.tools import SearchTools
from magicapi_tools.tools import SystemTools

try:
    from fastmcp import FastMCP
    from fastmcp.prompts.prompt import PromptMessage, TextContent
except ImportError:
    FastMCP = None
    PromptMessage = None
    TextContent = None


class ToolComposer:
    """工具组合器，负责组合和编排不同的工具模块。

    提供智能的工具组合推荐，根据使用场景自动选择合适的工具组合。
    """

    def __init__(self):
        # 基础工具组合配置
        self.compositions: Dict[str, List[str]] = {
            "full": [  # 完整工具集 - 适用于完整开发环境
                "documentation",
                "resource_management",
                "query",
                "api",
                "backup",
                "class_method",
                "search",
                "debug",
                "code_generation",
                "system"
            ],
            "minimal": [  # 最小工具集 - 适用于资源受限环境
                "query",
                "api",
                "backup",
                "class_method",
                "search",
                "system"
            ],
            "development": [  # 开发工具集 - 专注于开发调试
                "documentation",
                "resource_management",
                "query",
                "api",
                "backup",
                "class_method",
                "search",
                "debug",
                "code_generation"
            ],
            "production": [  # 生产工具集 - 生产环境稳定运行
                "query",
                "resource_management",
                "api",
                "backup",
                "class_method",
                "search",
                "system"
            ],
            "documentation_only": [  # 仅文档工具 - 文档查询和学习
                "documentation",
                "system"
            ],
            "api_only": [  # 仅API工具 - 接口测试和调用
                "api",
                "system"
            ],
            "backup_only": [  # 仅备份工具 - 数据备份和管理
                "backup",
                "system"
            ],
            "class_method_only": [  # 仅类方法工具 - Java类和方法查询
                "class_method",
                "system"
            ],
            "search_only": [  # 仅搜索工具 - 快速搜索定位
                "search",
                "system"
            ],
        }

        # 智能推荐配置
        self.smart_recommendations = {
            "beginner": {
                "description": "新手友好配置，包含基础功能和详细文档",
                "composition": ["documentation", "query", "api", "system"],
                "reasoning": "适合初学者，提供全面的文档支持和基础API功能"
            },
            "expert": {
                "description": "专家配置，专注核心功能，性能优化",
                "composition": ["query", "api", "resource_management", "debug"],
                "reasoning": "适合有经验的开发者，提供高效的核心功能"
            },
            "learning": {
                "description": "学习模式，重点提供教育资源和示例",
                "composition": ["documentation", "search", "code_generation", "system"],
                "reasoning": "专注于学习和知识获取，并提供代码生成辅助，适合学习Magic-API"
            },
            "maintenance": {
                "description": "运维配置，侧重系统监控和管理",
                "composition": ["resource_management", "backup", "system"],
                "reasoning": "适合系统运维和管理，提供资源和备份功能"
            },
            "integration": {
                "description": "集成配置，用于与其他系统集成",
                "composition": ["api", "query", "class_method", "system"],
                "reasoning": "适合系统集成场景，提供API调用和类方法查询"
            },
            "debugging": {
                "description": "调试配置，专注问题排查和调试",
                "composition": ["debug", "query", "api", "documentation"],
                "reasoning": "提供强大的调试和故障排查功能"
            }
        }

        # 工具依赖关系
        self.tool_dependencies = {
            "documentation": [],  # 文档工具独立
            "resource_management": ["system"],  # 资源管理依赖系统工具
            "query": ["system"],  # 查询工具依赖系统工具
            "api": ["system"],  # API工具依赖系统工具
            "backup": ["resource_management"],  # 备份工具依赖资源管理
            "class_method": ["system"],  # 类方法工具依赖系统工具
            "search": ["system"],  # 搜索工具依赖系统工具
            "debug": ["query", "api"],  # 调试工具依赖查询和API
            "code_generation": ["documentation"],  # 代码生成依赖文档工具
            "system": []  # 系统工具独立
        }

        # 工具优先级（用于自动排序）
        self.tool_priority = {
            "system": 1,  # 系统工具优先级最高
            "documentation": 2,  # 文档工具其次
            "api": 3,  # API工具重要
            "query": 4,  # 查询工具重要
            "resource_management": 5,  # 资源管理中等
            "debug": 6,  # 调试工具中等
            "code_generation": 7,  # 代码生成工具一般
            "search": 8,  # 搜索工具一般
            "backup": 9,  # 备份工具一般
            "class_method": 10  # 类方法工具最低
        }

        self.modules = {
            "documentation": DocumentationTools(),
            "resource_management": ResourceManagementTools(),
            "query": QueryTools(),
            "api": ApiTools(),
            "backup": BackupTools(),
            "class_method": ClassMethodTools(),
            "search": SearchTools(),
            "debug": DebugTools(),
            # "code_generation": CodeGenerationTools(),
            "system": SystemTools(),
        }

    def create_app(
        self,
        composition: str = "full",
        settings: Optional[MagicAPISettings] = None,
        custom_modules: Optional[List[Any]] = None
    ) -> "FastMCP":
        """创建FastMCP应用。

        Args:
            composition: 工具组合名称 ("full", "minimal", "development", "production",
                          "documentation_only", "api_only", "backup_only", "class_method_only", "search_only")
            settings: 应用设置
            custom_modules: 自定义工具模块列表

        Returns:
            配置好的FastMCP应用实例
        """
        if FastMCP is None:
            raise RuntimeError("请先通过 `uv add fastmcp` 安装 fastmcp 依赖后再运行服务器。")

        app_settings = settings or DEFAULT_SETTINGS

        # 初始化工具注册器
        tool_registry.initialize_context(app_settings)

        # 获取指定的工具组合
        module_names = self.compositions.get(composition, self.compositions["full"])

        # 添加标准模块
        for module_name in module_names:
            if module_name in self.modules:
                tool_registry.add_module(self.modules[module_name])

        # 添加自定义模块
        if custom_modules:
            for custom_module in custom_modules:
                tool_registry.add_module(custom_module)

        # 创建MCP应用
        mcp_app = FastMCP("Magic-API MCP Server")

        # 注册所有工具
        tool_registry.register_all_tools(mcp_app)

        # 注册 prompts
        self._register_prompts(mcp_app)

        return mcp_app

    def _register_prompts(self, mcp_app: "FastMCP") -> None:
        """注册 prompts 到 MCP 应用。"""
        if PromptMessage is None or TextContent is None:
            return

        @mcp_app.prompt(
            name="magic_api_developer_guide",
            description="生成专业的 Magic-API 开发者助手提示词，帮助用户高效使用 Magic-API MCP 工具",
        )
        def magic_api_developer_guide() -> str:
            """生成 Magic-API 开发者助手的核心提示词。"""
            return """# Magic-API 开发者助手提示词

你是一名专业的 Magic-API 开发者助手，完全依托 MCP (Model Context Protocol) 工具完成所有推理与操作。

## 🚦 工作守则
- 仅依据 MCP 工具返回的信息给出结论；缺少工具证据时必须明确说明限制。
- 分析任务前优先调用 `system.get_assistant_metadata` 了解上下文，必要时使用 `get_development_workflow` 获取官方流程。
- 若信息不足，优先通过文档、查询、搜索类工具补全事实，再继续推理或向用户确认。
- 在回答中引用已使用的工具及其关键输出，确保结论可追踪、可复现。

## 🔁 MCP 工具工作流
1. 准备阶段 → 调用 `system.get_assistant_metadata` 掌握环境、鉴权与可用工具，需要流程时调用 `get_development_workflow`。
2. 需求拆解 → 借助 `get_magic_api_docs`、`get_best_practices`、`get_common_pitfalls` 明确目标和约束，形成行动计划。
3. 信息采集 → 使用 `search_api_scripts`、`get_api_details_by_path`、`get_resource_tree`、`search_api_endpoints` 等工具获取最新状态。
4. 行动执行 → 按计划调用 `call_magic_api`、`save_api_endpoint`、`copy_resource`、`move_resource`、`set_breakpoint`、`call_api_with_debug` 等工具落实方案（API脚本开发时需遵循get_development_workflow指南）。
5. 结果校验 → 重复调用 `call_magic_api`、`get_practices_guide(guide_type='debugging')`、`list_backups` 等工具验证效果与风险。
6. 输出总结 → 基于工具输出撰写回答，标注关键证据和未确认事项。

## 🧠 输出要求
- 描述使用过的工具及核心发现，必要时给出下一步可执行的工具调用建议。
- 对无法通过工具验证的假设要注明“待确认”或提示用户补充信息。
- 回答保持结构化、可执行，符合项目的中文沟通习惯。

## 🛠️ 工具速览

### DocumentationTools
- `get_magic_script_syntax`：查询 Magic-Script 语法规则
- `get_magic_api_docs`：获取官方文档索引或详情
- `get_best_practices` / `get_common_pitfalls`：读取最佳实践与常见问题
- `get_development_workflow`：获取标准化开发流程
- `get_practices_guide`：查看性能、安全、调试等专项指南
- `list_examples` / `get_examples`：检索示例代码

### ApiTools
- `call_magic_api`：调试或验证任意 HTTP 方法的 Magic-API 接口

### ResourceManagementTools
- `get_resource_tree`：查看或导出资源树
- `save_api_endpoint` / `copy_resource` / `move_resource`：管理接口资源
- `save_group` / `delete_resource` 等：维护分组与资源

### QueryTools
- `get_api_details_by_path` / `get_api_details_by_id`：获取接口详情
- `search_api_endpoints`：按条件搜索接口端点

### DebugTools
- `set_breakpoint`、`step_over_breakpoint`、`resume_breakpoint_execution`：控制断点调试流程
- `call_api_with_debug`：在调试模式下重放接口
- `list_breakpoints`：查看当前断点

### SearchTools
- `search_api_scripts`：在脚本中搜索关键词
- `search_todo_comments`：检索 TODO 注释（按需启用）

### BackupTools
- `list_backups` / `create_full_backup` / `rollback_backup`：管理备份与回滚

### ClassMethodTools
- 查询 Java 类和方法签名，辅助排查引用关系

### SystemTools
- `get_assistant_metadata`：获取助手元信息、版本与可用功能

遵循上述工作流，以 MCP 工具为唯一事实来源，为用户提供专业、高效且可验证的 Magic-API 支持。"""

    def get_available_compositions(self) -> Dict[str, List[str]]:
        """获取可用的工具组合。"""
        return self.compositions.copy()

    def get_module_info(self) -> Dict[str, Dict[str, Any]]:
        """获取模块信息。"""
        return {
            name: {
                "class": module.__class__.__name__,
                "description": getattr(module, "__doc__", "").strip() or "No description",
            }
            for name, module in self.modules.items()
        }

    def recommend_composition(self, scenario: str = None, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """智能推荐工具组合。

        Args:
            scenario: 使用场景，可选值: beginner, expert, learning, maintenance, integration, debugging
            preferences: 用户偏好设置

        Returns:
            推荐的工具组合信息
        """
        if scenario and scenario in self.smart_recommendations:
            recommendation = self.smart_recommendations[scenario].copy()
            recommendation["scenario"] = scenario
            return recommendation

        # 如果没有指定场景，根据偏好进行推荐
        if preferences:
            return self._recommend_based_on_preferences(preferences)

        # 默认推荐新手配置
        recommendation = self.smart_recommendations["beginner"].copy()
        recommendation["scenario"] = "beginner"
        return recommendation

    def _recommend_based_on_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """基于用户偏好推荐工具组合。"""
        # 分析偏好并推荐合适的组合
        composition = []
        reasoning_parts = []

        # 检查是否需要文档支持
        if preferences.get("needs_documentation", True):
            composition.extend(["documentation"])
            reasoning_parts.append("包含文档工具以提供学习支持")

        # 检查是否需要调试功能
        if preferences.get("needs_debugging", False):
            composition.extend(["debug", "query", "api"])
            reasoning_parts.append("包含调试和API工具以支持开发调试")

        # 检查是否需要管理功能
        if preferences.get("needs_management", False):
            composition.extend(["resource_management", "backup"])
            reasoning_parts.append("包含资源管理和备份工具以支持系统运维")

        # 检查是否需要代码生成功能
        if preferences.get("needs_code_generation", False):
            composition.extend(["code_generation"])
            reasoning_parts.append("包含代码生成工具以提高开发效率")

        # 始终包含系统工具
        if "system" not in composition:
            composition.append("system")

        # 确保组合有效性
        composition = self._validate_and_sort_composition(composition)

        return {
            "description": "基于您的偏好定制的工具组合",
            "composition": composition,
            "reasoning": "，".join(reasoning_parts)
        }

    def validate_composition(self, composition: List[str]) -> Dict[str, Any]:
        """验证工具组合的有效性。

        Args:
            composition: 待验证的工具组合

        Returns:
            验证结果
        """
        missing_deps = []
        invalid_tools = []

        # 检查工具是否存在
        for tool in composition:
            if tool not in self.modules:
                invalid_tools.append(tool)

        # 检查依赖关系
        for tool in composition:
            if tool in invalid_tools:
                continue
            deps = self.tool_dependencies.get(tool, [])
            for dep in deps:
                if dep not in composition:
                    missing_deps.append(f"{tool} -> {dep}")

        # 按优先级排序
        valid_composition = [tool for tool in composition if tool not in invalid_tools]
        sorted_composition = self._validate_and_sort_composition(valid_composition)

        return {
            "valid": len(invalid_tools) == 0 and len(missing_deps) == 0,
            "original_composition": composition,
            "sorted_composition": sorted_composition,
            "invalid_tools": invalid_tools,
            "missing_dependencies": missing_deps,
            "warnings": []
        }

    def _validate_and_sort_composition(self, composition: List[str]) -> List[str]:
        """验证并排序工具组合。"""
        # 移除重复项
        unique_composition = list(set(composition))

        # 按优先级排序
        sorted_composition = sorted(unique_composition,
                                  key=lambda x: self.tool_priority.get(x, 999))

        return sorted_composition

    def get_composition_info(self, composition_name: str = None) -> Dict[str, Any]:
        """获取工具组合的详细信息。

        Args:
            composition_name: 组合名称，如果为None则返回所有组合信息

        Returns:
            组合详细信息
        """
        if composition_name:
            if composition_name in self.compositions:
                composition = self.compositions[composition_name]
                validation = self.validate_composition(composition)
                return {
                    "name": composition_name,
                    "tools": composition,
                    "tool_count": len(composition),
                    "validation": validation,
                    "description": self._get_composition_description(composition_name)
                }
            else:
                return {"error": f"组合 '{composition_name}' 不存在"}
        else:
            # 返回所有组合的概览
            overview = {}
            for name, tools in self.compositions.items():
                validation = self.validate_composition(tools)
                overview[name] = {
                    "tools": tools,
                    "tool_count": len(tools),
                    "is_valid": validation["valid"],
                    "description": self._get_composition_description(name)
                }
            return overview

    def _get_composition_description(self, composition_name: str) -> str:
        """获取组合的描述信息。"""
        descriptions = {
            "full": "完整工具集，适用于完整开发环境，包含所有功能",
            "minimal": "最小工具集，适用于资源受限环境，仅核心功能",
            "development": "开发工具集，专注于开发调试，包含代码生成",
            "production": "生产工具集，生产环境稳定运行",
            "documentation_only": "仅文档工具，文档查询和学习",
            "api_only": "仅API工具，接口测试和调用",
            "backup_only": "仅备份工具，数据备份和管理",
            "class_method_only": "仅类方法工具，Java类和方法查询",
            "search_only": "仅搜索工具，快速搜索定位"
        }
        return descriptions.get(composition_name, f"{composition_name} 工具组合")

    def create_custom_composition(self, tools: List[str], name: str = None) -> Dict[str, Any]:
        """创建自定义工具组合。

        Args:
            tools: 工具列表
            name: 组合名称（可选）

        Returns:
            创建的组合信息
        """
        validation = self.validate_composition(tools)
        sorted_tools = validation["sorted_composition"]

        composition_info = {
            "name": name or f"custom_{len(sorted_tools)}_tools",
            "tools": sorted_tools,
            "tool_count": len(sorted_tools),
            "validation": validation,
            "created": True
        }

        # 如果提供了名称，可以选择保存到预定义组合中
        if name and validation["valid"]:
            self.compositions[name] = sorted_tools

        return composition_info

    def analyze_tool_usage(self) -> Dict[str, Any]:
        """分析工具使用情况和依赖关系。"""
        analysis = {
            "total_tools": len(self.modules),
            "available_tools": list(self.modules.keys()),
            "compositions_count": len(self.compositions),
            "dependency_graph": self.tool_dependencies,
            "priority_ranking": sorted(self.tool_priority.items(), key=lambda x: x[1]),
            "most_used_composition": self._find_most_used_composition()
        }

        return analysis

    def _find_most_used_composition(self) -> str:
        """找出最常用的工具组合（基于工具数量和覆盖面）。"""
        # 简单算法：选择工具数量最多且包含核心工具的组合
        best_composition = None
        best_score = 0

        for name, tools in self.compositions.items():
            score = len(tools)
            # 奖励包含核心工具的组合
            core_tools = {"system", "api", "query"}
            if core_tools.issubset(set(tools)):
                score += 10

            if score > best_score:
                best_score = score
                best_composition = name

        return best_composition or "full"


# 全局工具组合器实例
tool_composer = ToolComposer()


def create_app(
    composition: str = "full",
    settings: Optional[MagicAPISettings] = None,
    custom_modules: Optional[List[Any]] = None
) -> "FastMCP":
    """便捷函数：创建FastMCP应用。

    Args:
        composition: 工具组合名称，可选值: full, minimal, development, production 等
        settings: 应用设置
        custom_modules: 自定义工具模块

    Returns:
        FastMCP应用实例
    """
    return tool_composer.create_app(composition, settings, custom_modules)

def recommend_composition(scenario: str = None, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
    """智能推荐工具组合。

    Args:
        scenario: 使用场景，可选值: beginner, expert, learning, maintenance, integration, debugging
        preferences: 用户偏好设置，如 {"needs_documentation": True, "needs_debugging": False}

    Returns:
        推荐的工具组合信息
    """
    return tool_composer.recommend_composition(scenario, preferences)

def validate_composition(composition: List[str]) -> Dict[str, Any]:
    """验证工具组合的有效性。

    Args:
        composition: 待验证的工具组合列表

    Returns:
        验证结果
    """
    return tool_composer.validate_composition(composition)

def get_composition_info(composition_name: str = None) -> Dict[str, Any]:
    """获取工具组合的详细信息。

    Args:
        composition_name: 组合名称，如果为None则返回所有组合信息

    Returns:
        组合详细信息
    """
    return tool_composer.get_composition_info(composition_name)

def create_custom_composition(tools: List[str], name: str = None) -> Dict[str, Any]:
    """创建自定义工具组合。

    Args:
        tools: 工具列表
        name: 组合名称（可选）

    Returns:
        创建的组合信息
    """
    return tool_composer.create_custom_composition(tools, name)

def analyze_tool_usage() -> Dict[str, Any]:
    """分析工具使用情况和依赖关系。

    Returns:
        工具使用分析结果
    """
    return tool_composer.analyze_tool_usage()
