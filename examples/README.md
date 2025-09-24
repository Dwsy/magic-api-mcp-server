# Magic-API 工具使用示例

本目录包含了使用 Magic-API 工具集的示例文件。

## 🏗️ 工具组合架构

Magic-API 助手采用了模块化的工具组合架构，支持灵活配置和扩展。

### 快速开始

```python
from magicapi_mcp import create_app

# 创建完整工具集应用（推荐）
app = create_app("full")

# 创建开发环境应用
dev_app = create_app("development")

# 创建生产环境应用
prod_app = create_app("production")

# 运行应用
app.run()
```

### 可用组合

| 组合名称 | 适用场景 | 包含工具 |
|---------|---------|---------|
| `full` | 完整开发环境 | 所有工具 |
| `development` | 开发调试 | 文档+资源+查询+调试 |
| `production` | 生产运维 | 查询+资源+系统 |
| `minimal` | 基础查询 | 查询+系统 |
| `documentation_only` | 仅文档查询 | 文档+系统 |

### 架构优势

- ✅ **模块化**: 工具按功能分组，职责清晰
- ✅ **可组合**: 支持灵活的工具组合配置
- ✅ **可扩展**: 易于添加新的工具模块
- ✅ **高性能**: 共享上下文，避免资源浪费
- ✅ **易维护**: 模块独立，便于测试和更新

## 🎯 统一接口设计

### 核心特性

**内聚性设计**: 单个方法同时支持单个和批量操作，无需维护重复代码。

```python
# 单个操作
tools.create_group_tool(name="新分组")

# 批量操作
tools.create_group_tool(groups_data=[{"name": "分组1"}, {"name": "分组2"}])
```

**自动判断**: 根据提供的参数自动选择操作模式，无需额外配置。

**统一响应**: 无论单个还是批量操作，都返回统一的响应格式。

### 支持的统一接口

| 功能分类 | 统一方法 | 单个参数 | 批量参数 |
|---------|---------|---------|---------|
| 资源管理 | `create_group_tool` | `name` | `groups_data` |
| 资源管理 | `create_api_tool` | `group_id`, `name`, ... | `apis_data` |
| 资源管理 | `delete_resource_tool` | `resource_id` | `resource_ids` |
| 资源管理 | `lock_resource_tool` | `resource_id` | `resource_ids` |
| 资源管理 | `unlock_resource_tool` | `resource_id` | `resource_ids` |
| 调试工具 | `set_breakpoint_tool` | `line_number` | `line_numbers` |
| 调试工具 | `remove_breakpoint_tool` | `line_number` | `line_numbers` |

## 批量操作示例

### 1. 批量创建分组

```bash
# 使用示例文件批量创建分组
python3 magic_api_resource_manager.py --batch-create-groups examples/batch_groups_example.json
```

**示例文件内容** (`batch_groups_example.json`):
```json
[
  {
    "name": "用户管理",
    "parent_id": "0",
    "group_type": "api",
    "path": "/user"
  },
  {
    "name": "订单管理",
    "parent_id": "0",
    "group_type": "api",
    "path": "/order"
  }
]
```

### 2. 批量创建API

```bash
# 使用示例文件批量创建API接口
python3 magic_api_resource_manager.py --batch-create-apis examples/batch_apis_example.json
```

**示例文件内容** (`batch_apis_example.json`):
```json
[
  {
    "group_id": "group_id_1",
    "name": "获取用户信息",
    "method": "GET",
    "path": "/user/info",
    "script": "var userId = request.getParameter('id');\nvar sql = 'SELECT * FROM users WHERE id = ?';\nvar user = db.selectOne(sql, [userId]);\nreturn user;"
  }
]
```

### 3. 批量删除资源

```bash
# 使用示例文件批量删除资源
python3 magic_api_resource_manager.py --batch-delete examples/batch_delete_example.json
```

**示例文件内容** (`batch_delete_example.json`):
```json
[
  "resource_id_1",
  "resource_id_2",
  "group_id_old_1"
]
```

## 导出和统计功能

### 4. 导出资源树

```bash
# 导出API资源树为JSON格式
python3 magic_api_resource_manager.py --export-tree api --format json > api_tree.json

# 导出所有资源树为CSV格式
python3 magic_api_resource_manager.py --export-tree all --format csv > all_resources.csv
```

### 5. 获取统计信息

```bash
# 显示资源统计信息
python3 magic_api_resource_manager.py --stats
```

输出示例：
```
📊 获取资源统计信息:
📈 总资源数: 150
🔗 API端点数: 45
📁 其他资源数: 105
📋 按HTTP方法统计:
  GET: 25
  POST: 12
  PUT: 5
  DELETE: 3
```

## MCP工具使用

### Python代码调用

```python
from magicapi_tools import MagicAPIResourceTools, MagicAPIResourceManager

# 创建资源管理器
manager = MagicAPIResourceManager("http://127.0.0.1:10712", "username", "password")
tools = MagicAPIResourceTools(manager)

# 🎯 统一接口：单个创建分组
result = tools.create_group_tool(name="新分组", parent_id="0", group_type="api")
print(f"单个创建结果: {result}")

# 🎯 统一接口：批量创建分组
groups_data = [
    {"name": "测试分组1", "parent_id": "0", "group_type": "api"},
    {"name": "测试分组2", "parent_id": "0", "group_type": "api"}
]
result = tools.create_group_tool(groups_data=groups_data)
print(f"批量创建结果: 成功 {result['successful']} 个，失败 {result['failed']} 个")

# 🎯 统一接口：批量删除资源
tools.delete_resource_tool(resource_ids=["id1", "id2", "id3"])

# 获取统计信息
stats = tools.get_resource_stats_tool()
print(f"总资源数: {stats['stats']['total_resources']}")

# 导出资源树
export_result = tools.export_resource_tree_tool(kind="api", format="json")
```

### MCP工具调用

```python
# 🎯 统一接口：单个创建分组
await call_tool("create_group", {
    "name": "新分组",
    "parent_id": "0",
    "group_type": "api"
})

# 🎯 统一接口：批量创建分组
await call_tool("create_group", {
    "groups_data": '[{"name": "分组1"}, {"name": "分组2"}]'
})

# 获取资源统计
await call_tool("get_resource_stats", {})

# 导出资源树
await call_tool("export_resource_tree", {"kind": "api", "format": "csv"})
```

## 注意事项

1. **批量操作**: 批量操作会按顺序执行，如果某个操作失败，不会影响其他操作
2. **错误处理**: 所有批量操作都会返回详细的成功/失败统计
3. **权限验证**: 确保用户具有相应的操作权限
4. **数据备份**: 在执行批量删除操作前建议先备份数据
5. **JSON格式**: 所有输入文件必须是有效的JSON格式

## 故障排除

### 常见错误

1. **文件不存在**: 检查文件路径是否正确
2. **JSON格式错误**: 使用JSON验证工具检查文件格式
3. **权限不足**: 确认用户具有相应资源的操作权限
4. **网络连接**: 检查Magic-API服务是否正常运行

### 调试技巧

1. 使用 `--help` 查看所有可用选项
2. 查看详细的错误信息和统计结果
3. 对于批量操作，可以查看每个项目的详细结果
