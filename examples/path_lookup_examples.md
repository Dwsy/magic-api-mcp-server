# Magic-API 路径查找功能示例

本文档展示了新添加的根据路径查找API ID和详情的功能示例。

## 🎯 新增功能概述

参考 `extract_api_paths.py` 的实现，为 Magic-API 助手添加了两个新的路径查找工具：

1. **`find_api_ids_by_path`** - 根据路径查找API ID列表
2. **`find_api_details_by_path`** - 根据路径查找API详情列表

## 📋 功能特性

### 支持的路径格式
- **完整路径**: `/api/users`
- **方法+路径**: `GET /api/users`
- **部分匹配**: 支持模糊搜索

### 返回数据结构
- **ID查找**: 返回匹配的API节点信息列表
- **详情查找**: 返回包含元数据和详细信息的完整结果

## 🔍 使用示例

### 1. 根据路径查找API ID列表

```python
# 查找所有匹配 '/api/users' 路径的API ID
result = find_api_ids_by_path("/api/users")
print(f"找到 {result['count']} 个匹配的API")
for match in result['matches']:
    print(f"ID: {match['id']}, 路径: {match['path']}, 方法: {match['method']}")
```

**预期输出**:
```json
{
  "path": "/api/users",
  "count": 3,
  "matches": [
    {
      "id": "api_001",
      "path": "/api/users",
      "method": "GET",
      "name": "获取用户列表"
    },
    {
      "id": "api_002",
      "path": "/api/users",
      "method": "POST",
      "name": "创建用户"
    },
    {
      "id": "api_003",
      "path": "/api/users/{id}",
      "method": "GET",
      "name": "获取单个用户"
    }
  ]
}
```

### 2. 根据路径查找API详情列表

```python
# 查找所有匹配 '/api/users' 路径的API详细信息
result = find_api_details_by_path("/api/users", fuzzy=True)
print(f"找到 {result['count']} 个API详情")
for item in result['results']:
    meta = item['meta']
    detail = item.get('detail')
    if detail:
        print(f"=== {meta['method']} {meta['path']} (ID: {meta['id']}) ===")
        print(f"名称: {detail.get('name')}")
        print(f"描述: {detail.get('comment')}")
        print(f"脚本: {detail.get('script')[:100]}...")
    else:
        print(f"错误: {item.get('error')}")
```

**预期输出**:
```json
{
  "path": "/api/users",
  "fuzzy": true,
  "count": 3,
  "results": [
    {
      "meta": {
        "id": "api_001",
        "path": "/api/users",
        "method": "GET",
        "name": "获取用户列表"
      },
      "detail": {
        "id": "api_001",
        "name": "获取用户列表",
        "path": "/api/users",
        "method": "GET",
        "script": "return db.select('users');",
        "comment": "获取所有用户信息的接口",
        "groupId": "group_001",
        "options": {},
        "createTime": "2024-01-01T00:00:00Z",
        "updateTime": "2024-01-01T00:00:00Z"
      }
    }
  ]
}
```

### 3. MCP 工具调用示例

#### 查找API ID列表
```python
await call_tool("find_api_ids_by_path", {
    "path": "/api/users"
})
```

#### 查找API详情列表
```python
await call_tool("find_api_details_by_path", {
    "path": "/api/users",
    "fuzzy": true
})
```

## 🔄 与现有功能的区别

| 功能 | `path_to_id` | `find_api_ids_by_path` | 区别 |
|-----|-------------|----------------------|-----|
| **返回类型** | 单个匹配 | 所有匹配列表 | 批量vs单个 |
| **匹配模式** | 简单字符串 | 高级路径匹配 | 匹配算法 |
| **使用场景** | 单个API查找 | 批量API查找 | 适用范围 |

## 🚀 实际应用场景

### 场景1: 批量API管理
```python
# 查找所有用户相关的API
user_apis = find_api_ids_by_path("/api/users")

# 对找到的API执行批量操作
for api in user_apis['matches']:
    delete_resource(api['id'])
```

### 场景2: API文档生成
```python
# 获取所有API的详细信息
all_apis = find_api_details_by_path("/", fuzzy=True)

# 生成API文档
for item in all_apis['results']:
    if 'detail' in item:
        generate_api_doc(item['detail'])
```

### 场景3: API变更影响分析
```python
# 查找受影响的API
affected_apis = find_api_ids_by_path("/api/users/profile")

# 检查依赖关系
for api in affected_apis['matches']:
    check_dependencies(api['id'])
```

## ⚡ 性能优化

### 智能缓存
- 资源树数据会被缓存，避免重复请求
- 支持增量更新，提高查询效率

### 高效匹配
- 使用优化的字符串匹配算法
- 支持正则表达式和模糊匹配
- 快速过滤大量API端点

## 🛠️ 错误处理

### 常见错误情况
- **路径不存在**: 返回 `"not_found"` 错误
- **网络错误**: 返回 `"extraction_error"` 错误
- **权限不足**: 返回相应的HTTP错误码

### 错误响应格式
```json
{
  "error": {
    "code": "not_found",
    "message": "未找到路径为 '/api/missing' 的 API 端点"
  }
}
```

## 📚 相关工具对比

| 工具名称 | 功能描述 | 输入 | 输出 | 适用场景 |
|---------|---------|-----|-----|---------|
| `path_to_id` | 路径转ID（单个） | 路径字符串 | 单个API信息 | 精确查找 |
| `find_api_ids_by_path` | 路径查找ID列表 | 路径字符串 | API信息列表 | 批量查找 |
| `find_api_details_by_path` | 路径查找详情列表 | 路径+模糊选项 | 完整详情列表 | 详细信息获取 |
| `api_detail` | ID获取详情 | API ID | 单个API详情 | 已知ID查询 |

这套路径查找功能大大增强了 Magic-API 助手的查询能力，让开发者能够更高效地管理和操作API资源！🎉
