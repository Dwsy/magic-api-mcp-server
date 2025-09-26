# Magic-API MCP Server

Magic-API MCP Server - A Model Context Protocol server for Magic-API development

## 项目概述

Magic-API MCP Server 是一个为 Magic-API 开发设计的 Model Context Protocol (MCP) 服务器，旨在提升 AI 助手在 Magic-API 开发任务中的效率和准确性。

## 核心目标

- **提升开发效率**：通过专业化的工具集，让 AI 助手能够更高效地进行 Magic-API 的开发工作
- **标准化开发流程**：提供一致的开发工作流，确保开发过程的规范性
- **智能辅助开发**：为 AI 助手提供直接操作 Magic-API 的能力，增强其辅助开发的能力
- **降低学习门槛**：简化 Magic-API 的复杂操作，使开发者更容易上手

## 主要功能

- **API 调用与测试**：支持对 Magic-API 接口的调用和测试
- **资源管理**：提供资源的创建、读取、更新、删除等操作
- **查询与检索**：高效的资源查询和检索功能
- **调试支持**：断点设置和调试会话管理
- **文档查询**：内置的文档和知识库查询功能
- **备份管理**：完整的备份和恢复功能
- **类方法查询**：Java 类和方法的检索功能

## 架构特性

- **模块化设计**：采用清晰的模块化架构，便于功能扩展和维护
- **MCP 协议兼容**：完全兼容 Model Context Protocol 标准
- **可配置工具组合**：支持多种工具组合，适应不同使用场景
- **服务层架构**：采用领域驱动设计（DDD），包含 domain、services、tools、utils 等模块

## 安装与使用

### 使用 uvx 运行（推荐）

```bash
uvx magic-api-mcp-server@latest
```

### 本地开发安装

```bash
# 安装项目依赖
uv sync

# 本地运行
python run_mcp.py
```

## 配置

项目支持多种环境变量配置，包括 Magic-API 服务地址、认证信息、超时设置等。

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

MIT