# FastMCP 工具装饰器示例

本文档展示了为 Magic-API 助手工具添加的丰富装饰器参数示例。

## 装饰器参数说明

FastMCP 支持为 `@mcp.tool` 装饰器添加以下参数：

- `name`: 自定义工具名称（供LLM识别）
- `description`: 详细的工具描述
- `tags`: 标签集合，用于分类和过滤
- `meta`: 元数据字典，包含版本、作者等信息

## 示例装饰器

### 1. 语法查询工具
```python
@mcp.tool(
    name="get_magic_script_syntax",
    description="查询 Magic-Script 编程语言的语法规则和使用示例，支持中文和英文。",
    tags={"syntax", "documentation", "scripting"},
    meta={"version": "1.0", "category": "documentation"}
)
def syntax(topic: str, locale: str = "zh-CN") -> Dict[str, Any]:
    """返回指定主题的 Magic-Script 语法速查。"""
```

### 2. 资源管理工具
```python
@mcp.tool(
    name="create_resource_group",
    description="创建资源分组，支持单个分组创建或批量分组创建。",
    tags={"resource", "group", "create", "management"},
    meta={"version": "2.0", "category": "resource-management"}
)
def create_group(name=None, groups_data=None) -> Dict[str, Any]:
    """创建分组（支持单个和批量操作）。"""
```

### 3. 调试工具
```python
@mcp.tool(
    name="set_breakpoint",
    description="设置调试断点，支持单个断点设置或批量断点设置。",
    tags={"debug", "breakpoint", "development"},
    meta={"version": "2.0", "category": "debugging"}
)
def set_breakpoint(line_number=None, line_numbers=None) -> Dict[str, Any]:
    """设置断点（支持单个和批量操作）。"""
```

### 4. API调用工具
```python
@mcp.tool(
    name="call_magic_api",
    description="调用 Magic-API 接口并返回请求结果，支持各种HTTP方法和参数。",
    tags={"api", "call", "http", "request"},
    meta={"version": "1.0", "category": "api-execution"}
)
def call(method: str, path: str, params=None, data=None, headers=None) -> Dict[str, Any]:
    """调用 Magic-API 接口并返回请求结果。"""
```

## 标签分类体系

### 功能分类标签
- `syntax`: 语法相关
- `documentation`: 文档相关
- `examples`: 示例相关
- `best-practices`: 最佳实践
- `pitfalls`: 常见问题
- `workflow`: 工作流
- `resource`: 资源管理
- `api`: API相关
- `debug`: 调试相关
- `websocket`: WebSocket相关
- `meta`: 元信息

### 操作类型标签
- `create`: 创建操作
- `delete`: 删除操作
- `update`: 更新操作
- `list`: 列表查询
- `export`: 导出功能
- `statistics`: 统计功能
- `lookup`: 查找功能
- `management`: 管理功能

### 状态标签
- `deprecated`: 已废弃的功能

## 元数据结构

```python
meta = {
    "version": "2.0",        # 工具版本
    "category": "resource-management",  # 功能分类
    "author": "system",     # 作者信息（可选）
    "priority": "high"      # 优先级（可选）
}
```

## 工具命名约定

### 统一接口工具
- `create_resource_group`: 创建资源分组
- `create_api_endpoint`: 创建API端点
- `delete_resource`: 删除资源
- `set_breakpoint`: 设置断点

### 专用功能工具
- `get_magic_script_syntax`: 获取语法信息
- `get_resource_tree`: 获取资源树
- `call_magic_api`: 调用API
- `get_assistant_metadata`: 获取助手元信息

## 使用效果

添加了丰富装饰器参数后，LLM 可以：

1. **更准确地识别工具**: 通过自定义名称理解工具功能
2. **更好地过滤工具**: 使用标签进行分类筛选
3. **理解工具版本**: 通过元数据了解工具状态
4. **获得详细描述**: 通过详细描述了解工具用途和参数

这大大提升了 Magic-API 助手与 LLM 的交互质量和用户体验！
