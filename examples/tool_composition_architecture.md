# Magic-API 工具组合架构

本文档介绍了重新设计的工具组合架构，该架构提供了高度模块化和可组合的工具系统。

## 🏗️ 架构概述

### 核心组件

```
Magic-API 助手
├── tool_composer.py      # 工具组合器（入口）
├── tool_registry.py      # 工具注册器
├── magicapi_assistant.py # 兼容性入口
└── tools/                # 工具模块目录
    ├── documentation_tools.py   # 文档工具
    ├── resource_tools.py        # 资源管理工具
    ├── query_tools.py           # 查询工具
    ├── debug_tools.py           # 调试工具
    └── system_tools.py          # 系统工具
```

### 设计原则

1. **模块化**: 每个工具模块职责单一，独立开发
2. **可组合**: 支持灵活的工具组合配置
3. **可扩展**: 易于添加新的工具模块
4. **向后兼容**: 保持现有API的兼容性

## 🔧 核心组件详解

### 1. 工具注册器 (Tool Registry)

```python
class ToolRegistry:
    """工具注册器，管理所有工具模块的注册。"""

    def add_module(self, module: ToolModule) -> None:
        """添加工具模块。"""

    def initialize_context(self, settings) -> None:
        """初始化工具上下文。"""

    def register_all_tools(self, mcp_app) -> None:
        """注册所有工具到MCP应用。"""
```

**职责**:
- 管理工具模块的注册
- 提供统一的上下文环境
- 协调工具间的依赖关系

### 2. 工具组合器 (Tool Composer)

```python
class ToolComposer:
    """工具组合器，负责组合和编排工具模块。"""

    def create_app(self, composition: str, settings, custom_modules) -> FastMCP:
        """创建FastMCP应用。"""
```

**职责**:
- 定义预设的工具组合
- 组合不同的工具模块
- 提供统一的创建接口

### 3. 工具上下文 (Tool Context)

```python
class ToolContext:
    """工具上下文，包含所有必要的客户端和服务。"""

    def __init__(self, settings):
        self.http_client = MagicAPIHTTPClient(settings)
        self.resource_tools = MagicAPIResourceTools(...)
        self.debug_tools = MagicAPIDebugTools(...)
        # ...
```

**职责**:
- 提供统一的客户端和服务实例
- 管理工具间的共享状态
- 确保资源的高效利用

### 4. 工具模块协议 (Tool Module Protocol)

```python
class ToolModule(Protocol):
    """工具模块协议。"""

    def register_tools(self, mcp_app, context: ToolContext) -> None:
        """注册工具到MCP应用。"""
```

**职责**:
- 定义工具模块的统一接口
- 确保模块间的标准化交互

## 🎯 工具组合配置

### 预定义组合

| 组合名称 | 包含模块 | 适用场景 |
|---------|---------|---------|
| `full` | 全部模块 | 完整的开发环境 |
| `minimal` | query + system | 基本的查询功能 |
| `development` | documentation + resource + query + debug | 开发调试环境 |
| `production` | query + resource + system | 生产运维环境 |
| `documentation_only` | documentation + system | 仅文档查询 |

### 自定义组合

```python
from magicapi_mcp import create_app
from my_custom_tools import MyCustomTool

# 使用预定义组合
app = create_app("development")

# 添加自定义工具模块
custom_modules = [MyCustomTool()]
app = create_app("minimal", custom_modules=custom_modules)
```

## 📦 工具模块详解

### 文档工具模块 (DocumentationTools)

**包含工具**:
- `get_magic_script_syntax` - 语法查询
- `get_magic_script_examples` - 示例查询
- `get_magic_api_docs` - 官方文档
- `get_best_practices` - 最佳实践
- `get_common_pitfalls` - 常见问题
- `get_development_workflow` - 开发流程

### 资源管理工具模块 (ResourceManagementTools)

**包含工具**:
- `get_resource_tree` - 资源树查询
- `create_resource_group` - 创建分组
- `create_api_endpoint` - 创建API
- `copy/move/delete/lock/unlock_resource` - 资源操作
- `export_resource_tree` - 导出资源树
- `get_resource_statistics` - 资源统计

### 查询工具模块 (QueryTools)

**包含工具**:
- `find_resource_id_by_path` - 路径查找ID
- `get_api_details_by_path` - 路径获取详情
- `get_api_details_by_id` - ID获取详情
- `find_api_ids_by_path` - 批量查找ID
- `find_api_details_by_path` - 批量查找详情
- `call_magic_api` - API调用

### 调试工具模块 (DebugTools)

**包含工具**:
- `set_breakpoint/remove_breakpoint` - 断点管理
- `resume_breakpoint/step_over` - 执行控制
- `list_breakpoints` - 断点列表
- `call_api_with_debugging` - 调试API调用
- `execute_debug_session` - 调试会话
- `get_debug_status` - 调试状态
- `clear_all_breakpoints` - 清除断点
- `get_websocket_status` - WebSocket状态

### 系统工具模块 (SystemTools)

**包含工具**:
- `get_assistant_metadata` - 助手元信息

## 🔄 组合操作的优势

### 1. 灵活配置

```python
# 不同场景使用不同组合
dev_app = create_app("development")      # 开发环境
prod_app = create_app("production")      # 生产环境
doc_app = create_app("documentation_only") # 文档环境
```

### 2. 模块独立

```python
# 每个模块可以独立开发和测试
from magicapi_tools import DocumentationTools

docs_module = DocumentationTools()
# 可以单独测试或使用
```

### 3. 易于扩展

```python
# 添加自定义工具模块
class MyCustomTools(ToolModule):
    def register_tools(self, mcp_app, context):
        # 注册自定义工具
        pass

app = create_app("minimal", custom_modules=[MyCustomTools()])
```

### 4. 资源优化

```python
# 上下文共享，避免重复创建客户端
context = ToolContext(settings)
# 所有工具共享同一个 http_client 和其他服务实例
```

## 🚀 使用示例

### 基本使用

```python
from magicapi_mcp import create_app

# 创建完整工具集应用
app = create_app()

# 创建开发环境应用
dev_app = create_app("development")

# 运行应用
app.run()
```

### 高级配置

```python
from magicapi_mcp import create_app
from magicapi_mcp.settings import MagicAPISettings

# 自定义设置
settings = MagicAPISettings(
    base_url="https://api.example.com",
    auth_enabled=True,
    username="user",
    password="pass"
)

# 创建自定义配置的应用
app = create_app("full", settings=settings)
```

### 模块化开发

```python
# 单独开发和测试工具模块
from magicapi_tools import ResourceManagementTools
from magicapi_mcp.tool_registry import ToolContext

# 创建测试上下文
context = ToolContext(settings)

# 测试单个模块
resource_tools = ResourceManagementTools()
# 可以进行单元测试或单独功能测试
```

## 📈 架构优势

### 相比原有架构的改进

| 方面 | 原架构 | 新架构 | 优势 |
|-----|-------|-------|-----|
| **代码组织** | 单文件900+行 | 模块化设计 | 易维护、易理解 |
| **功能组合** | 固定工具集 | 可配置组合 | 灵活适配不同场景 |
| **扩展性** | 难以扩展 | 插件化架构 | 易于添加新功能 |
| **测试性** | 整体测试 | 模块化测试 | 提高测试覆盖率 |
| **资源管理** | 重复创建 | 上下文共享 | 提高性能和资源利用 |

### 性能优化

- **延迟加载**: 工具按需注册
- **资源复用**: 共享客户端实例
- **组合优化**: 只加载需要的工具模块

### 维护便利

- **关注点分离**: 每个模块职责单一
- **接口标准化**: 统一的注册协议
- **配置集中**: 组合配置集中管理

## 🎯 最佳实践

### 1. 组合选择

```python
# 根据使用场景选择合适的组合
environments = {
    "development": "full",           # 开发时需要所有功能
    "staging": "development",        # 预发布使用开发组合
    "production": "production",      # 生产环境精简功能
    "documentation": "documentation_only"  # 文档站点
}
```

### 2. 自定义模块

```python
# 为特定项目创建自定义工具
class ProjectSpecificTools(ToolModule):
    def register_tools(self, mcp_app, context):
        # 注册项目特定的工具
        pass

# 组合使用
app = create_app("minimal", custom_modules=[ProjectSpecificTools()])
```

### 3. 配置管理

```python
# 使用环境变量或配置文件管理设置
import os
settings = MagicAPISettings(
    base_url=os.getenv("MAGIC_API_URL", "http://localhost:10712"),
    auth_enabled=os.getenv("MAGIC_API_AUTH", "false").lower() == "true",
    username=os.getenv("MAGIC_API_USER"),
    password=os.getenv("MAGIC_API_PASS")
)
```

## 🔮 未来扩展

### 支持的功能扩展

1. **动态组合**: 运行时动态调整工具组合
2. **条件注册**: 基于配置条件注册工具
3. **工具版本**: 支持工具的版本管理和兼容性
4. **监控统计**: 工具使用情况的监控和统计

### 生态系统扩展

1. **第三方工具**: 支持第三方开发的工具模块
2. **工具市场**: 提供工具模块的发现和安装机制
3. **标准化协议**: 定义工具模块的标准协议

这套组合架构为 Magic-API 助手提供了强大的扩展能力和灵活的配置选项，使其能够适应各种使用场景和需求！🎉
