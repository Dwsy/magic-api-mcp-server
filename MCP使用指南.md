# Magic-API MCP 服务器使用指南

## 🚀 快速开始

本项目集成了 Model Context Protocol (MCP) 功能，为 Magic-API 开发提供高级交互能力。

### 1. 安装与测试

```bash
# 如果尚未安装 uv
pip install uv
```

### 2. MCP 配置

#### 基础配置（适用于大多数用户）：

```json
{
  "mcpServers": {
    "magic-api-mcp": {
      "command": "python",
      "args": ["-m", "uv", "run", "fastmcp", "run", "magicapi_mcp/magicapi_assistant.py:tools", "--transport", "stdio"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

#### 高级配置（需要自定义环境）：

```json
{
  "mcpServers": {
    "magic-api-mcp": {
      "command": "python",
      "args": ["-m", "uv", "run", "fastmcp", "run", "magicapi_mcp/magicapi_assistant.py:tools", "--transport", "stdio"],
      "timeout": 600,
      "env": {
        "MCP_DEBUG": "false",
        "MCP_WEB_HOST": "127.0.0.1",
        "MCP_WEB_PORT": "8765",
        "MCP_LANGUAGE": "zh-CN"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

#### 桌面应用程序配置（v2.5.0 新功能 - 使用原生桌面应用程序）：

```json
{
  "mcpServers": {
    "magic-api-mcp": {
      "command": "python",
      "args": ["-m", "uv", "run", "fastmcp", "run", "magicapi_mcp/magicapi_assistant.py:tools", "--transport", "stdio"],
      "timeout": 600,
      "env": {
        "MCP_DESKTOP_MODE": "true",
        "MCP_WEB_HOST": "127.0.0.1",
        "MCP_WEB_PORT": "8765",
        "MCP_DEBUG": "false"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

### 3. 本项目 MCP 工具功能

Magic-API MCP 服务器为 Magic-API 开发提供以下专业工具：

#### 3.1 文档工具
- 获取 Magic-API 脚本语法示例
- 获取内置模块文档
- 获取内置函数文档
- 获取类型扩展信息
- 获取配置选项说明
- 获取插件系统信息
- 获取最佳实践指南

#### 3.2 代码生成工具
- 生成 Magic-API 脚本代码
- 生成 MyBatis SQL 语句
- 生成 Java 代码片段
- 生成 API 端点示例

#### 3.3 API 管理工具
- 查询 API 端点信息
- 管理 Magic-API 资源
- 调试 API 接口
- 搜索 API 端点

#### 3.4 系统工具
- 备份与恢复功能
- 系统状态查询
- 资源管理器
- 搜索与过滤功能

### 4. Prompt Engineering 设置

为获得最佳结果，请在 AI 助手中添加以下规则：

```
# Magic-API MCP 交互反馈规则

1. 遵循 magic-api-mcp 指令
2. 使用项目中的工具获取最新、最准确的信息
3. 优先使用 extract_api_paths.py 从数据库获取实际代码
4. 参考项目架构和现有实现模式
5. 遵循项目编码规范和最佳实践
```

### 5. 环境变量

| 变量 | 用途 | 值 | 默认值 |
|------|------|----|--------|
| MCP_DEBUG | 调试模式 | true/false | false |
| MCP_WEB_HOST | Web UI 主机绑定 | IP 地址或主机名 | 127.0.0.1 |
| MCP_WEB_PORT | Web UI 端口 | 1024-65535 | 8765 |
| MCP_DESKTOP_MODE | 桌面应用程序模式 | true/false | false |
| MCP_LANGUAGE | 强制 UI 语言 | zh-TW/zh-CN/en | 自动检测 |

#### MCP_WEB_HOST 说明：
- `127.0.0.1`（默认）：仅本地访问，更高安全性
- `0.0.0.0`：允许远程访问，适用于 SSH 远程开发环境

#### MCP_LANGUAGE 说明：
用于强制界面语言，覆盖自动系统检测。
支持的语言代码：
- `zh-TW`：繁体中文
- `zh-CN`：简体中文
- `en`：英语

语言检测优先级：
1. 界面中用户保存的语言设置（最高优先级）
2. MCP_LANGUAGE 环境变量
3. 系统环境变量（LANG, LC_ALL 等）
4. 系统默认语言
5. 回退到默认语言（简体中文）

### 6. 测试选项

```bash
# 版本检查
python -m uv run fastmcp run magicapi_mcp/magicapi_assistant.py:tools --help

# 启动 MCP 服务
python -m uv run fastmcp run magicapi_mcp/magicapi_assistant.py:tools --transport stdio

# 调试模式
MCP_DEBUG=true python -m uv run fastmcp run magicapi_mcp/magicapi_assistant.py:tools --transport stdio

# 指定语言测试
MCP_LANGUAGE=en python -m uv run fastmcp run magicapi_mcp/magicapi_assistant.py:tools --transport stdio  # 强制英文界面
MCP_LANGUAGE=zh-CN python -m uv run fastmcp run magicapi_mcp/magicapi_assistant.py:tools --transport stdio  # 强制简体中文
```

### 7. 开发者安装

```bash
# 本项目已包含完整的 MCP 实现
cd /path/to/magic-api-tools
pip install -r requirements.txt
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
│   ├── code_generation.py   # 代码生成工具
│   ├── query.py            # 查询工具
│   └── ...                 # 其他功能模块
└── utils/                  # 工具助手功能
    ├── knowledge_base.py    # 知识库接口
    ├── response.py          # 标准化响应
    └── ...                 # 其他辅助功能
```

## 🎯 使用场景

### 场景 1: 获取 API 详细信息
使用 `get_examples` 工具获取 Magic-API 脚本语法示例和最佳实践。

### 场景 2: 代码生成
使用 `generate_code` 工具根据需求生成 Magic-API 脚本代码。

### 场景 3: 资源管理
使用 `query_api_resources` 工具查询和管理 Magic-API 资源。

### 场景 4: 调试和搜索
使用 `search_api_endpoints` 和 `debug_script` 工具进行 API 调试和搜索。

本项目 MCP 服务器专为 Magic-API 开发者设计，提供了一套完整的工作流工具，从脚本编写、API 管理到调试和部署，全方位提升开发效率。