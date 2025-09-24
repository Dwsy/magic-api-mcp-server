# Magic-API MCP Server 使用指南

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
    "magic-api-mcp-server": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--transport", "stdio"],
      "timeout": 600
    }
  }
}
```

#### 高级配置（需要自定义环境）：

```json
{
  "mcpServers": {
    "magic-api-mcp-server": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--transport", "stdio"],
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
    "magic-api-mcp-server-full": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "full", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-minimal": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "minimal", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-development": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "development", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-production": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "production", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-documentation-only": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "documentation_only", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-api-only": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "api_only", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-backup-only": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "backup_only", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-class-method-only": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "class_method_only", "--transport", "stdio"],
      "timeout": 600
    },
    "magic-api-mcp-server-search-only": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "search_only", "--transport", "stdio"],
      "timeout": 600
    }
  }
}
```

### 3. 本项目 MCP 工具功能

Magic-API MCP 服务器为 Magic-API 开发提供以下专业工具：

#### 3.1 系统工具 (SystemTools)
系统信息和元数据工具
- **get_assistant_metadata**: 获取Magic-API MCP Server的完整元信息，包括版本、功能列表和配置

#### 3.2 文档工具 (DocumentationTools)
文档查询和知识库工具，提供全面的Magic-API文档查询功能
- **get_script_syntax**: 获取Magic-API脚本语法说明
- **get_module_api**: 获取内置模块的API文档
- **get_function_docs**: 获取内置函数库文档
- **get_extension_docs**: 获取类型扩展功能文档
- **get_config_docs**: 获取配置选项说明
- **get_plugin_docs**: 获取插件系统文档
- **get_best_practices**: 获取最佳实践指南
- **get_pitfalls**: 获取常见问题和陷阱
- **get_workflow**: 获取工作流模板
- **list_examples**: 列出所有可用示例
- **get_examples**: 获取特定类型的示例代码
- **get_docs**: 获取官方文档索引和内容

#### 3.3 API 工具 (ApiTools)
API调用和测试工具，支持灵活的接口调用和测试
- **call_magic_api**: 调用Magic-API接口并返回请求结果，支持GET、POST、PUT、DELETE等HTTP方法

#### 3.4 资源管理工具 (ResourceManagementTools)
完整的资源管理系统，支持资源树查询、CRUD操作等
- **get_resource_tree**: 获取资源树，支持多种过滤和导出格式
- **get_resource_detail**: 获取特定资源的详细信息
- **create_resource_group**: 创建新的资源分组
- **create_api_resource**: 创建新的API资源
- **copy_resource**: 复制现有资源
- **move_resource**: 移动资源到其他分组
- **delete_resource**: 删除资源（支持软删除）
- **lock_resource**: 锁定资源防止修改
- **unlock_resource**: 解锁资源
- **list_resource_groups**: 列出所有资源分组
- **export_resource_tree**: 导出完整的资源树结构
- **get_resource_stats**: 获取资源统计信息

#### 3.5 查询工具 (QueryTools)
高效的资源查询和检索工具
- **get_api_details_by_path**: 根据API路径直接获取接口的详细信息，支持模糊匹配
- **get_api_details_by_id**: 根据接口ID获取完整的接口详细信息和配置
- **search_api_endpoints**: 搜索和过滤Magic-API接口端点，返回包含ID的完整信息列表

#### 3.6 调试工具 (DebugTools)
强大的调试功能，支持断点管理和调试会话
- **set_breakpoint**: 在指定API脚本中设置断点
- **remove_breakpoint**: 移除指定的断点
- **resume_breakpoint_execution**: 恢复断点执行，继续运行调试脚本
- **step_over_breakpoint**: 单步执行，越过当前断点继续执行
- **list_breakpoints**: 列出所有当前设置的断点
- **call_api_with_debug**: 调用指定接口并在命中断点处暂停
- **execute_debug_session**: 执行完整的调试会话
- **get_debug_status**: 获取当前调试状态
- **clear_all_breakpoints**: 清除所有断点
- **get_websocket_status**: 获取WebSocket连接状态

#### 3.7 搜索工具 (SearchTools)
内容搜索和定位工具
- **search_api_scripts**: 在所有API脚本中搜索关键词
- **search_todo_comments**: 搜索API脚本中的TODO注释

#### 3.8 备份工具 (BackupTools)
完整的备份管理功能
- **list_backups**: 查询备份列表，支持时间戳过滤和名称过滤
- **get_backup_history**: 获取备份历史记录
- **get_backup_content**: 获取指定备份的内容
- **rollback_backup**: 回滚到指定的备份版本
- **create_full_backup**: 创建完整的系统备份

#### 3.9 类方法工具 (ClassMethodTools)
Java类和方法检索工具
- **list_magic_api_classes**: 列出所有Magic-API可用的类、扩展和函数，支持翻页浏览
- **get_class_details**: 获取指定类的详细信息，包括方法、属性和继承关系
- **get_method_details**: 获取指定方法的详细信息，包括参数类型和返回值

#### 3.10 代码生成工具 (CodeGenerationTools) - 当前禁用
智能代码生成功能（需启用后使用）
- **generate_crud_api**: 生成完整的CRUD API接口代码
- **generate_database_query**: 生成数据库查询代码
- **generate_api_test**: 生成API接口测试代码
- **generate_workflow_code**: 生成工作流模板代码

#### 3.11 提示词工具 (PromptTools)
可复用的提示词模板，帮助生成专业的Magic-API开发者助手配置
- **magic_api_developer_guide**: 生成专业的 Magic-API 开发者助手提示词

### 4. 工具组合配置

本项目支持多种工具组合，可根据需要选择：

- `full`: 完整工具集 - 适用于完整开发环境 (默认)
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
# 推荐方式：使用 uvx 运行（适用于已发布到 pip 的包）
uvx magic-api-mcp-server

# 或者直接运行 Python 脚本（开发时）
python run_mcp.py

# 指定工具组合运行
uvx magic-api-mcp-server --composition development

# 使用特定配置运行
MAGIC_API_BASE_URL=http://localhost:8080 uvx magic-api-mcp-server
```

### 7. Docker 运行方式

#### 使用 Docker Compose (推荐)

```bash
# 使用 Makefile 命令 (推荐，简化操作)
make quick-start    # 快速启动开发环境
make deploy         # 生产环境部署
make logs           # 查看日志
make status         # 查看状态
make shell          # 进入容器
make test           # 运行测试

# 或直接使用 docker-compose 命令
# 1. 构建并启动服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f magic-api-mcp-server

# 3. 停止服务
docker-compose down

# 4. 重启服务
docker-compose restart magic-api-mcp-server
```

#### 使用 Docker 命令 (基于 uvx)

```bash
# 1. 构建镜像
docker build -t magic-api-mcp-server .

# 2. 运行容器 (stdio模式)
docker run --rm --entrypoint uvx magic-api-mcp-server \
  magic-api-mcp-server --composition full --transport stdio

# 3. 运行容器 (HTTP模式)
docker run -d --name magic-api-mcp-server \
  -p 8000:8000 \
  --entrypoint uvx magic-api-mcp-server \
  magic-api-mcp-server --transport http --port 8000

# 4. 查看日志
docker logs -f magic-api-mcp-server

# 5. 停止容器
docker stop magic-api-mcp-server
```

#### Docker 配置说明

**基于 uvx 的优势**:
- 自动下载并运行最新版本的包
- 无需预先安装依赖
- 镜像更小，构建更快
- 自动处理包版本管理

**生产环境配置** (`docker-compose.yml`):
- 使用桥接网络连接到Magic-API服务
- 配置资源限制和健康检查
- 支持自动重启

**开发环境配置** (`docker-compose.override.yml`):
- 挂载源代码支持热重载
- 调试日志级别
- 禁用健康检查

#### Docker 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `MAGIC_API_BASE_URL` | Magic-API 服务基础 URL | `http://host.docker.internal:10712` |
| `MAGIC_API_WS_URL` | Magic-API WebSocket URL | `ws://host.docker.internal:10712/magic/web/console` |
| `MAGIC_API_USERNAME` | 认证用户名 | 无 |
| `MAGIC_API_PASSWORD` | 认证密码 | 无 |
| `MAGIC_API_TOKEN` | 认证令牌 | 无 |
| `MAGIC_API_AUTH_ENABLED` | 是否启用认证 | `false` |
| `MAGIC_API_TIMEOUT_SECONDS` | 请求超时时间 | `30.0` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `FASTMCP_TRANSPORT` | MCP传输协议 | `stdio` |

#### 网络配置注意事项

- **Linux**: 使用 `host.docker.internal` 访问宿主机服务
- **macOS/Windows**: Docker Desktop 自动提供 `host.docker.internal`
- **自定义网络**: 可通过 `docker network` 创建专用网络

#### Docker 构建问题解决

如果遇到网络证书验证问题，请尝试以下解决方案：

**方案1: 使用国内镜像源**
```bash
# 修改Dockerfile添加国内镜像源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

**方案2: 配置Docker代理**
```bash
# 创建或修改 ~/.docker/config.json
{
  "proxies": {
    "default": {
      "httpProxy": "http://127.0.0.1:7897",
      "httpsProxy": "http://127.0.0.1:7897",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

**方案3: 跳过TLS验证 (仅用于测试)**
```bash
# 临时跳过TLS验证构建
docker build --build-arg DOCKER_TLS_VERIFY=0 -t magic-api-mcp-server:test .
```

**方案4: 使用预构建镜像**
```bash
# 如果网络问题持续，可考虑使用预构建的基础镜像
# 或者在有稳定网络的环境中构建
```

#### 故障排除

```bash
# 使用 Makefile 命令 (推荐)
make status         # 查看容器状态
make shell          # 进入容器调试
make logs-tail      # 查看详细日志
make test           # 运行健康检查
make test-connection # 测试与 Magic-API 连接
make clean-all      # 清理所有资源

# 或直接使用 docker/docker-compose 命令
# 查看容器状态
docker-compose ps

# 进入容器调试
docker-compose exec magic-api-mcp-server bash

# 查看详细日志
docker-compose logs --tail=100 magic-api-mcp-server

# 清理容器和镜像
docker-compose down --rmi all --volumes
```

### 8. 项目结构

```
magicapi_mcp/
├── magicapi_assistant.py    # 主要的 MCP 助手实现
├── tool_registry.py         # 工具注册表
├── tool_composer.py         # 工具组合器
└── settings.py              # 配置设置
magicapi_tools/
├── tools/                   # 各种 MCP 工具
│   ├── system.py            # 系统工具 (元信息查询)
│   ├── documentation.py     # 文档工具 (知识库查询)
│   ├── api.py              # API工具 (接口调用)
│   ├── resource.py         # 资源管理工具 (CRUD操作)
│   ├── query.py            # 查询工具 (资源检索)
│   ├── debug.py            # 调试工具 (断点管理)
│   ├── search.py           # 搜索工具 (内容搜索)
│   ├── backup.py           # 备份工具 (数据备份)
│   ├── class_method.py     # 类方法工具 (Java类查询)
│   ├── code_generation.py  # 代码生成工具 (当前禁用)
│   └── common.py           # 通用辅助函数
└── utils/                  # 工具助手功能
    ├── knowledge_base.py   # 知识库接口
    ├── response.py         # 标准化响应
    ├── http_client.py      # HTTP 客户端
    └── resource_manager.py # 资源管理器
```

### 9. 使用场景

#### 场景 1: 新手学习 Magic-API
使用 `documentation_only` 组合，专注于学习和文档查询：
```json
{
  "mcpServers": {
    "magic-api-docs": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "documentation_only", "--transport", "stdio"],
      "timeout": 600
    }
  }
}
```

#### 场景 2: API 开发和测试
使用 `api_only` 或 `query` 组合，进行接口开发和测试：
```json
{
  "mcpServers": {
    "magic-api-dev": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "development", "--transport", "stdio"],
      "timeout": 600
    }
  }
}
```

#### 场景 3: 生产环境运维
使用 `backup_only` 或 `resource_management` 组合，进行系统运维：
```json
{
  "mcpServers": {
    "magic-api-ops": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "production", "--transport", "stdio"],
      "timeout": 600
    }
  }
}
```

#### 场景 4: 问题排查和调试
使用 `debug` 组合，进行问题排查和调试：
```json
{
  "mcpServers": {
    "magic-api-debug": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--composition", "minimal", "--transport", "stdio"],
      "timeout": 600,
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 10. 安装方式

#### 从 PyPI 安装（推荐）

```bash
# 安装已发布的包
pip install magic-api-mcp-server

# 或使用 uv 安装
uv add magic-api-mcp-server

# 运行 MCP 服务器
uvx magic-api-mcp-server
```

#### 开发者本地安装

```bash
# 本项目已包含完整的 MCP 实现
cd magic-api-mcp-server

# 安装项目依赖（开发时）
uv sync

# 安装 fastmcp 依赖
uv add fastmcp

# 本地运行（开发时）
python run_mcp.py
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

### 11. MCP 提示词

#### 提示词概述

当使用支持 MCP 的 AI 助手（如 Claude Desktop、Cursor 等）时，请使用以下提示词让助手了解 Magic-API MCP Server 的功能和用途。

#### 核心提示词

```
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

记住：你现在具备了完整的 Magic-API 开发工具链，可以为用户提供专业、高效的开发支持！
```

#### 简短提示词 (适用于快速配置)

```
你是一个专业的 Magic-API 开发者助手，拥有以下 MCP 工具：

📚 文档查询: get_script_syntax, get_module_api, get_best_practices, get_examples
🔧 API 调用: call_magic_api
📁 资源管理: get_resource_tree, create_api_resource, delete_resource
🔍 查询工具: get_api_details_by_path, get_api_details_by_id, search_api_endpoints
🐛 调试工具: set_breakpoint, resume_breakpoint_execution, call_api_with_debug
🔎 搜索工具: search_api_scripts, search_todo_comments
💾 备份工具: list_backups, create_full_backup, rollback_backup
⚙️ 系统工具: get_assistant_metadata

优先使用文档工具了解功能，然后根据需求选择合适的工具进行操作。
```

#### 配置提示词 (Cursor/VS Code 等编辑器)

```json
{
  "mcpServers": {
    "magic-api-mcp-server": {
      "command": "uvx",
      "args": ["magic-api-mcp-server", "--transport", "stdio"],
      "timeout": 600,
      "env": {
        "MAGIC_API_BASE_URL": "http://127.0.0.1:10712",
        "MAGIC_API_WS_URL": "ws://127.0.0.1:10712/magic/web/console"
      }
    }
  }
}
```

本项目 MCP 服务器专为 Magic-API 开发者设计，提供了一套完整的工作流工具，从脚本编写、API 管理到调试和部署，全方位提升开发效率。

## 🧠 Prompts (提示词模板)

Magic-API MCP Server 提供了可复用的提示词模板，帮助您快速配置专业的 Magic-API 开发者助手。

### 可用 Prompts

#### magic_api_developer_guide
生成专业的 Magic-API 开发者助手提示词，包含：
- 完整的工具能力介绍
- 使用指南和最佳实践
- 错误处理建议
- 工具选择策略

**使用方法：**
```python
# 通过 MCP 客户端调用
prompt = await client.get_prompt("magic_api_developer_guide")
content = prompt.messages[0].content.text
```

**适用场景：**
- 配置新的 AI 助手
- 标准化开发工作流
- 培训新团队成员
- 创建一致的开发环境