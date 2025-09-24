# Magic-API MCP 服务器使用指南

## 🚀 快速开始

本项目集成了 Model Context Protocol (MCP) 功能，为 Magic-API 开发提供高级交互能力。

### 1. 安装与测试

```bash
# 如果尚未安装 uv (推荐方式)
pip install uv

# 安装项目依赖
uv sync
# 或者安装 fastmcp
uv add fastmcp
```

### 2. MCP 配置

#### 基础配置（适用于大多数用户）：

```json
{
  "mcpServers": {
    "magic-api-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "run_mcp.py:mcp", "--transport", "stdio"],
      "timeout": 600
    }
  }
}
```

#### 高级配置（需要自定义环境）：

```json
{
  "mcpServers": {
    "magic-api-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "run_mcp.py:mcp", "--transport", "stdio"],
      "timeout": 600,
      "env": {
        "MAGIC_API_BASE_URL": "http://127.0.0.1:10712",
        "MAGIC_API_WS_URL": "ws://127.0.0.1:10712/magic/web/console",
        "MAGIC_API_TIMEOUT_SECONDS": "30.0",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 使用不同工具组合的配置：

```json
{
  "mcpServers": {
    "magic-api-mcp-full": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "run_mcp.py:mcp", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-minimal": {
      "command": "python",
      "args": ["-c", "from magicapi_mcp.magicapi_assistant import create_app; create_app('minimal').run(transport='stdio')"],
      "timeout": 600
    },
    "magic-api-mcp-documentation-only": {
      "command": "python",
      "args": ["-c", "from magicapi_mcp.magicapi_assistant import create_app; create_app('documentation_only').run(transport='stdio')"],
      "timeout": 600
    }
  }
}
```

### 3. 本项目 MCP 工具功能

Magic-API MCP 服务器为 Magic-API 开发提供以下专业工具：

#### 3.1 文档工具 (DocumentationTools)
- 获取 Magic-API 脚本语法示例
- 获取内置模块文档
- 获取内置函数文档
- 获取类型扩展信息
- 获取配置选项说明
- 获取插件系统信息
- 获取最佳实践指南

#### 3.2 API 工具 (ApiTools)
- 执行 Magic-API HTTP 请求
- 调用 Magic-API 端点
- 测试 API 接口功能
- 获取 API 响应数据

#### 3.3 查询工具 (QueryTools)
- 查询 API 资源信息
- 搜索和过滤 API 端点
- 获取接口详细信息
- 参数分析和验证

#### 3.4 资源管理工具 (ResourceManagementTools)
- 管理 Magic-API 资源
- 创建、更新、删除 API 接口
- 分组管理
- 资源导入导出

#### 3.5 搜索工具 (SearchTools)
- 搜索 API 端点
- 按名称、路径、方法等条件搜索
- 高级搜索和过滤功能

#### 3.6 调试工具 (DebugTools)
- 断点调试功能
- 变量检查
- 执行流程控制

#### 3.7 备份工具 (BackupTools)
- 配置备份与恢复
- 资源备份管理

#### 3.8 类方法工具 (ClassMethodTools)
- 查询 Java 类和方法
- 获取类方法详细信息
- 参数和返回值分析

#### 3.9 系统工具 (SystemTools)
- 系统信息查询
- 工具状态检查
- 配置验证

### 4. 工具组合配置

本项目支持多种工具组合，可根据需要选择：

- `full`: 完整工具集 - 适用于完整开发环境
- `minimal`: 最小工具集 - 适用于资源受限环境
- `development`: 开发工具集 - 专注于开发调试
- `production`: 生产工具集 - 生产环境稳定运行
- `documentation_only`: 仅文档工具 - 文档查询和学习
- `api_only`: 仅API工具 - 接口测试和调用
- `backup_only`: 仅备份工具 - 数据备份和管理
- `class_method_only`: 仅类方法工具 - Java类和方法查询
- `search_only`: 仅搜索工具 - 快速搜索定位

### 5. 环境变量

| 变量 | 用途 | 值 | 默认值 |
|------|------|----|--------|
| MAGIC_API_BASE_URL | Magic-API 服务基础 URL | URL 地址 | http://127.0.0.1:10712 |
| MAGIC_API_WS_URL | Magic-API WebSocket URL | WebSocket 地址 | ws://127.0.0.1:10712/magic/web/console |
| MAGIC_API_USERNAME | Magic-API 认证用户名 | 字符串 | 无 |
| MAGIC_API_PASSWORD | Magic-API 认证密码 | 字符串 | 无 |
| MAGIC_API_TOKEN | Magic-API 认证令牌 | 字符串 | 无 |
| MAGIC_API_AUTH_ENABLED | 是否启用认证 | true/false | false |
| MAGIC_API_TIMEOUT_SECONDS | 请求超时时间（秒） | 数字 | 30.0 |
| LOG_LEVEL | 日志级别 | DEBUG/INFO/WARNING/ERROR | INFO |
| FASTMCP_TRANSPORT | FastMCP 传输协议 | stdio/http | stdio |

### 6. 本地运行方式

```bash
# 推荐方式：使用 uv 运行
uv run fastmcp run run_mcp.py:mcp

# 或者直接运行 Python 脚本
python run_mcp.py

# 指定工具组合运行
python -c "from magicapi_mcp.magicapi_assistant import create_app; create_app('development').run(transport='stdio')"

# 使用特定配置运行
MAGIC_API_BASE_URL=http://localhost:8080 uv run fastmcp run run_mcp.py:mcp
```

### 7. 开发者安装

```bash
# 本项目已包含完整的 MCP 实现
cd magic-api-tools
pip install -r requirements.txt

# 或使用 uv (推荐)
uv sync

# 安装 fastmcp 依赖
uv add fastmcp
```

## 🛠️ 项目结构

```
magicapi_mcp/
├── magicapi_assistant.py    # 主要的 MCP 助手实现
├── tool_registry.py         # 工具注册表
├── tool_composer.py         # 工具组合器
└── settings.py              # 配置设置
magicapi_tools/
├── tools/                   # 各种 MCP 工具
│   ├── documentation.py     # 文档相关工具
│   ├── api.py              # API 相关工具
│   ├── code_generation.py   # 代码生成工具 (当前已禁用)
│   ├── query.py            # 查询工具
│   ├── backup.py           # 备份工具
│   ├── class_method.py     # 类方法工具
│   ├── debug.py            # 调试工具
│   ├── resource.py         # 资源管理工具
│   ├── search.py           # 搜索工具
│   └── system.py           # 系统工具
└── utils/                  # 工具助手功能
    ├── knowledge_base.py    # 知识库接口
    ├── response.py          # 标准化响应
    ├── http_client.py       # HTTP 客户端
    └── resource_manager.py  # 资源管理器
```

## 🎯 使用场景

### 场景 1: 获取 API 详细信息
使用 `get_examples` 工具获取 Magic-API 脚本语法示例和最佳实践。

### 场景 2: API 测试
使用 `call_api` 工具测试 Magic-API 接口。

### 场景 3: 资源管理
使用 `manage_resource` 工具查询和管理 Magic-API 资源。

### 场景 4: 调试和搜索
使用 `search_api_endpoints` 和 `debug_endpoint` 工具进行 API 调试和搜索。

### 场景 5: 文档查询
使用 `get_documentation` 工具获取 Magic-API 相关文档。

本项目 MCP 服务器专为 Magic-API 开发者设计，提供了一套完整的工作流工具，从脚本编写、API 管理到调试和部署，全方位提升开发效率。