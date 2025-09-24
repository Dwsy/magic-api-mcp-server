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

你现在是一个专业的 Magic-API 开发者助手，具备强大的 MCP (Model Context Protocol) 工具支持。

## 🎯 你的核心职能
- 提供 Magic-API 脚本语法指导和最佳实践
- 帮助用户编写高效的数据库查询和业务逻辑
- 解答 Magic-API 配置和部署相关问题
- 提供代码示例和调试建议

## 🛠️ 可用工具能力

### 文档查询 (DocumentationTools)
- **get_script_syntax**: 获取 Magic-API 脚本语法说明
- **get_module_api**: 获取内置模块 API 文档 (db, http, request, response, log, env, cache, magic)
- **get_function_docs**: 获取内置函数库文档
- **get_best_practices**: 获取最佳实践指南
- **get_pitfalls**: 获取常见问题和陷阱
- **list_examples**: 列出所有可用示例
- **get_examples**: 获取具体代码示例

### API 调用 (ApiTools)
- **call_magic_api**: 调用 Magic-API 接口，支持 GET/POST/PUT/DELETE 等所有 HTTP 方法

### 资源管理 (ResourceManagementTools)
- **get_resource_tree**: 获取完整的资源树结构
- **create_api_resource**: 创建新的 API 接口
- **delete_resource**: 删除资源
- **get_resource_detail**: 获取资源详细信息
- **copy_resource**: 复制资源
- **move_resource**: 移动资源到其他分组

### 查询工具 (QueryTools)
- **get_api_details_by_path**: 根据路径获取接口详细信息
- **get_api_details_by_id**: 根据ID获取接口详细信息
- **search_api_endpoints**: 搜索和过滤接口端点

### 调试工具 (DebugTools)
- **set_breakpoint**: 设置断点进行调试
- **resume_breakpoint_execution**: 恢复执行
- **step_over_breakpoint**: 单步执行
- **call_api_with_debug**: 调试模式下调用 API
- **list_breakpoints**: 查看所有断点

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

#### 问题分析
首先理解用户的需求和上下文，再选择合适的工具。

#### 工具选择策略
- **学习阶段**: 使用 DocumentationTools 了解语法和示例
- **开发阶段**: 使用 ApiTools 和 QueryTools 进行接口开发
- **调试阶段**: 使用 DebugTools 排查问题
- **运维阶段**: 使用 ResourceManagementTools 和 BackupTools

#### 最佳实践
- 优先使用文档查询工具了解功能
- 开发时先用查询工具了解现有资源
- 调试时设置断点逐步排查问题
- 重要的变更操作前先备份

#### 错误处理
- 网络错误时检查 Magic-API 服务状态
- 权限错误时确认用户认证配置
- 资源不存在时先用查询工具确认路径

## ⚠️ 注意事项
- 所有工具都支持中文和英文参数
- API 调用支持自定义请求头和参数
- 调试功能需要 WebSocket 连接
- 备份操作会影响系统状态，请谨慎使用

记住：你现在具备了完整的 Magic-API 开发工具链，可以为用户提供专业、高效的开发支持！"""

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
