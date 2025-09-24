# Magic-API MCP 工具系统开发指南

## 📋 概述

Magic-API MCP (Model Context Protocol) 工具系统为 AI 助手提供完整的 Magic-API 开发支持，包括文档查询、代码示例、配置管理等功能。

## 🏗️ 系统架构

```
magicapi_tools/
├── tools/
│   ├── documentation.py      # 文档和知识库工具
│   ├── api.py               # API 调用工具
│   └── __init__.py          # 工具模块初始化
├── utils/
│   ├── knowledge_base.py    # 知识库统一接口
│   ├── kb_syntax.py         # 语法知识库
│   ├── kb_modules.py        # 模块知识库
│   ├── kb_functions.py      # 函数知识库
│   ├── kb_extensions.py     # 扩展知识库
│   ├── kb_config.py         # 配置知识库
│   ├── kb_plugins.py        # 插件知识库
│   ├── kb_practices.py      # 最佳实践知识库
│   └── kb_examples.py       # 示例知识库
└── README.md               # 本文档
```

## 🔧 工具开发指南

### 工具基本结构

每个工具都遵循以下结构：

```python
@mcp_app.tool(
    name="tool_name",                    # 工具唯一标识
    description="工具功能描述",           # 简洁的功能说明
    tags={"tag1", "tag2"},              # 分类标签
    meta={"version": "x.x", "category": "category_name", "author": "author"},
    annotations={
        "title": "用户友好标题",
        "readOnlyHint": True,            # 是否只读操作
        "openWorldHint": False           # 是否与外部系统交互
    }
)
def tool_function(
    param1: Annotated[Type, Field(description="参数描述")] = default_value
) -> ReturnType:
    """工具函数文档字符串"""
    # 实现逻辑
    return result
```

### 工具配置规范

#### 1. 命名约定
- **工具名称**: 使用小写字母和下划线，如 `get_examples`
- **函数名称**: 与工具名称保持一致
- **标签**: 使用语义化标签，如 `{"syntax", "examples", "documentation"}`

#### 2. 参数类型注解
```python
# 推荐写法
param: Annotated[str, Field(description="参数描述", min_length=1)]

# 不推荐写法
param: str  # 缺少描述和验证
```

#### 3. 返回类型
- 使用明确的返回类型注解
- 对于复杂返回，使用 `Dict[str, Any]` 或具体类型
- 统一使用 `error_response()` 处理错误情况

#### 4. 错误处理
```python
if not data:
    available_options = list(OPTIONS.keys())
    return error_response("not_found", f"未找到 '{param}'。可用选项：{', '.join(available_options)}")
```

### 添加新工具

#### 步骤 1: 确定工具位置

根据工具功能选择合适的模块：

| 模块 | 适用场景 |
|------|----------|
| `documentation.py` | 文档查询、知识库访问 |
| `api.py` | API 调用、数据操作 |

#### 步骤 2: 实现工具函数

```python
@mcp_app.tool(
    name="new_tool_name",
    description="新工具的功能描述",
    tags={"category", "subcategory"},
    meta={"version": "1.0", "category": "tools", "author": "developer"},
    annotations={
        "title": "用户友好标题",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def new_tool_function(
    param1: Annotated[str, Field(description="参数1描述")] = "default",
    param2: Annotated[int, Field(description="参数2描述", ge=0)] = 0
) -> Dict[str, Any]:
    """新工具的详细说明

    这个工具用于...

    Args:
        param1: 参数1的详细说明
        param2: 参数2的详细说明

    Returns:
        返回数据的格式说明
    """
    try:
        # 实现逻辑
        result = {"data": "example"}
        return result
    except Exception as e:
        return error_response("internal_error", f"处理失败: {str(e)}")
```

#### 步骤 3: 导入依赖

在文件顶部的导入部分添加必要的依赖：

```python
from magicapi_tools.utils.knowledge_base import (
    # 添加新的辅助函数
    new_helper_function,
)
```

#### 步骤 4: 更新文档

在 `__all__` 列表中添加新函数：

```python
__all__ = [
    # 现有导出
    "existing_function",
    # 新增导出
    "new_tool_function",
]
```

#### 步骤 5: 测试工具

```bash
# 语法检查
python3 -m py_compile magicapi_tools/tools/documentation.py

# Linter 检查
python3 -m pylint magicapi_tools/tools/documentation.py

# 功能测试
python3 -c "from magicapi_tools.tools.documentation import new_tool_function; print('测试通过')"
```

### 修改现有工具

#### 兼容性原则

1. **保持接口稳定**: 尽量不修改现有参数名称和类型
2. **向后兼容**: 新版本必须兼容旧版本的使用方式
3. **渐进升级**: 使用版本号标识变更

#### 修改步骤

1. **更新工具配置**:
   ```python
   meta={"version": "2.0", "category": "existing", "author": "updater"}
   ```

2. **添加可选参数**:
   ```python
   def existing_tool(
       existing_param: str,
       new_param: Annotated[Optional[str], Field(description="新参数")] = None
   ):
       # 保持原有逻辑不变
       if new_param:
           # 新功能逻辑
           pass
   ```

3. **扩展返回格式**:
   ```python
   result = {"original_data": data}
   if new_param:
       result["new_data"] = new_data
   return result
   ```

### 删除工具

#### 安全删除流程

1. **标记为废弃** (第一阶段):
   ```python
   @mcp_app.tool(
       enabled=False,  # 禁用工具
       meta={"version": "x.x", "deprecated": True, "removal_version": "x.x+1"}
   )
   def deprecated_tool():
       """此工具已废弃，请使用 new_tool_name"""
   ```

2. **完全移除** (第二阶段):
   - 从代码中删除工具函数
   - 更新导入语句
   - 更新 `__all__` 列表
   - 更新文档

#### 删除检查清单

- [ ] 确认无其他代码依赖此工具
- [ ] 通知相关人员工具即将移除
- [ ] 提供替代方案
- [ ] 更新版本号
- [ ] 运行完整测试套件

## 📚 知识库管理

### 知识库结构

知识库分为以下模块：

| 模块 | 内容 | 更新频率 |
|------|------|----------|
| `kb_syntax.py` | 脚本语法、MyBatis语法 | 低 |
| `kb_modules.py` | 内置模块API | 中 |
| `kb_functions.py` | 内置函数库 | 中 |
| `kb_extensions.py` | 类型扩展 | 低 |
| `kb_config.py` | 配置选项 | 中 |
| `kb_plugins.py` | 插件系统 | 高 |
| `kb_practices.py` | 最佳实践 | 中 |
| `kb_examples.py` | 使用示例 | 高 |

### 添加知识内容

#### 1. 选择合适的模块

根据内容类型选择模块：
- **语法**: `kb_syntax.py`
- **API**: `kb_modules.py`
- **函数**: `kb_functions.py`
- **配置**: `kb_config.py`
- **示例**: `kb_examples.py`

#### 2. 添加内容结构

```python
# kb_examples.py
"new_category": {
    "title": "分类标题",
    "description": "分类描述",
    "examples": {
        "example_key": {
            "title": "示例标题",
            "description": "示例描述",
            "code": textwrap.dedent('''
                // 示例代码
                var result = exampleFunction();
                return result;
            ''').strip(),
            "notes": [
                "要点1",
                "要点2"
            ],
            "tags": ["tag1", "tag2"]
        }
    }
}
```

#### 3. 更新辅助函数

在 `knowledge_base.py` 中添加对应的辅助函数：

```python
def get_new_category_examples(key: str = None) -> Any:
    """获取新分类的示例"""
    from .kb_examples import EXAMPLES_KNOWLEDGE

    examples = EXAMPLES_KNOWLEDGE.get("new_category", {}).get("examples", {})
    if key:
        return examples.get(key)
    return examples
```

#### 4. 集成到统一接口

更新 `documentation.py` 中的 `get_examples` 工具：

```python
category_map = {
    # 现有映射
    "existing_category": get_existing_examples,
    # 新增映射
    "new_category": get_new_category_examples,
}
```

## 🧪 测试和验证

### 自动化测试

```bash
# 语法检查所有工具文件
find magicapi_tools -name "*.py" -exec python3 -m py_compile {} \;

# Linter 检查
find magicapi_tools -name "*.py" -exec python3 -m pylint {} \;

# 导入测试
python3 -c "import magicapi_tools; print('导入成功')"
```

### 工具功能测试

```python
# 测试工具导入
from magicapi_tools.tools.documentation import get_examples

# 测试工具调用
result = get_examples()
assert "categories" in result
assert result["total_categories"] > 0

# 测试具体功能
syntax_examples = get_examples("script_syntax")
assert len(syntax_examples) > 0
```

### 知识库测试

```python
# 测试知识库数据完整性
from magicapi_tools.utils.knowledge_base import get_available_categories

categories = get_available_categories()
for category in categories:
    topics = get_category_topics(category)
    assert len(topics) > 0, f"分类 {category} 为空"
```

## 📝 开发规范

### 代码风格

- 遵循 PEP 8 编码规范
- 使用类型注解
- 编写详细的文档字符串
- 使用有意义的变量名

### 提交规范

```bash
# 提交信息格式
<type>(<scope>): <subject>

# 示例
feat(docs): 添加新的语法示例
fix(api): 修复MyBatis查询错误
refactor(tools): 重构工具参数验证
```

### 版本管理

- **主版本**: 不兼容的API变更
- **次版本**: 新功能添加
- **补丁版本**: 错误修复

## 🔍 故障排除

### 常见问题

1. **导入错误**
   ```python
   # 检查相对导入
   from .utils.knowledge_base import function_name
   ```

2. **类型注解错误**
   ```python
   # 确保所有导入都正确
   from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Literal, Optional
   ```

3. **工具未注册**
   ```python
   # 确保在 register_tools 方法中调用
   def register_tools(self, mcp_app, context):
       # 工具定义必须在此方法内
       @mcp_app.tool(...)
       def tool_function():
           pass
   ```

### 调试技巧

1. **启用详细日志**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **测试工具隔离**:
   ```python
   # 单独测试工具函数
   result = tool_function(param="test")
   print(f"Result: {result}")
   ```

3. **验证配置**:
   ```python
   # 检查工具装饰器参数
   assert tool_function.__name__ == "expected_name"
   ```

## 📞 联系与支持

如有问题或建议，请联系开发团队或查看项目文档。

---

**最后更新**: 2025年1月
**版本**: 2.2
**维护者**: 系统开发团队