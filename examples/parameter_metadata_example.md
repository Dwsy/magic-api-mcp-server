# FastMCP 参数元数据示例

本文档展示了为 Magic-API 助手工具添加的参数元数据示例，提升了LLM的参数理解和使用体验。

## 参数元数据特性

### 🎯 核心优势

- **智能提示**: LLM 能理解每个参数的用途和格式
- **类型验证**: 使用 Literal 和 Field 约束参数值范围
- **默认值处理**: 清晰区分必需参数和可选参数
- **中文描述**: 为中文用户提供友好的参数说明

### 🔧 实现方式

#### **简单字符串描述**
```python
from typing import Annotated

param: Annotated[str, "参数的简短描述"]
```

#### **高级元数据 (推荐)**
```python
from typing import Annotated
from pydantic import Field

param: Annotated[
    Type,
    Field(
        description="详细的参数描述",
        ge=最小值,          # 大于等于
        le=最大值,          # 小于等于
        pattern="正则表达式"  # 字符串模式
    )
] = 默认值
```

## 📋 参数元数据示例

### 1. 资源树查询 - resource_tree

```python
def resource_tree(
    kind: Annotated[
        Literal["api", "function", "task", "datasource", "all"],
        Field(description="资源类型过滤器：api（API接口）、function（函数）、task（任务）、datasource（数据源）或all（全部）")
    ] = "api",
    search: Annotated[
        Optional[str],
        Field(description="简单搜索关键词，支持部分匹配（兼容性保留参数）")
    ] = None,
    csv: Annotated[
        bool,
        Field(description="是否以CSV格式输出资源信息")
    ] = False,
    depth: Annotated[
        Optional[int],
        Field(description="限制显示的资源树深度，正整数", ge=1, le=10)
    ] = None,
    method_filter: Annotated[
        Optional[str],
        Field(description="HTTP方法过滤器，如'GET'、'POST'、'PUT'、'DELETE'")
    ] = None,
    path_filter: Annotated[
        Optional[str],
        Field(description="路径正则表达式过滤器，用于匹配API路径")
    ] = None,
    name_filter: Annotated[
        Optional[str],
        Field(description="名称正则表达式过滤器，用于匹配资源名称")
    ] = None,
    query_filter: Annotated[
        Optional[str],
        Field(description="通用查询过滤器，支持复杂的搜索条件")
    ] = None,
) -> Dict[str, Any]:
```

**LLM 理解效果**:
- 知道 `kind` 参数必须是预定义的选项之一
- 理解 `depth` 参数的取值范围 (1-10)
- 清楚每个过滤器的用途和格式

### 2. 分组创建 - create_group

```python
def create_group(
    name: Annotated[
        Optional[str],
        Field(description="分组名称（单个分组创建时必需）")
    ] = None,
    parent_id: Annotated[
        str,
        Field(description="父分组ID，根分组使用'0'")
    ] = "0",
    group_type: Annotated[
        Literal["api", "function", "task", "datasource"],
        Field(description="分组类型：api（API接口组）、function（函数组）、task（任务组）、datasource（数据源组）")
    ] = "api",
    path: Annotated[
        Optional[str],
        Field(description="分组路径，可选的URL路径前缀")
    ] = None,
    options: Annotated[
        Optional[str],
        Field(description="分组选项配置，JSON格式字符串")
    ] = None,
    groups_data: Annotated[
        Optional[str],
        Field(description="批量分组数据，JSON数组格式，每个对象包含name等字段（批量操作时使用）")
    ] = None,
) -> Dict[str, Any]:
```

**LLM 理解效果**:
- 区分单个操作和批量操作的参数
- 理解 `group_type` 的有效选项
- 知道必需参数和可选参数的区别

### 3. API接口创建 - create_api

```python
def create_api(
    group_id: Annotated[
        Optional[str],
        Field(description="分组ID（单个API创建时必需），指定API所属的分组")
    ] = None,
    name: Annotated[
        Optional[str],
        Field(description="API接口名称（单个API创建时必需）")
    ] = None,
    method: Annotated[
        Optional[Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]],
        Field(description="HTTP请求方法（单个API创建时必需）")
    ] = None,
    path: Annotated[
        Optional[str],
        Field(description="API路径，如'/api/users'（单个API创建时必需）")
    ] = None,
    script: Annotated[
        Optional[str],
        Field(description="API执行脚本，Magic-Script代码（单个API创建时必需）")
    ] = None,
    apis_data: Annotated[
        Optional[str],
        Field(description="批量API数据，JSON数组格式，每个对象包含group_id,name,method,path,script字段（批量操作时使用）")
    ] = None,
) -> Dict[str, Any]:
```

**LLM 理解效果**:
- 知道HTTP方法的有效选项
- 理解批量操作的JSON格式要求
- 清楚每个参数在不同操作模式下的要求

### 4. API调用 - call

```python
def call(
    method: Annotated[
        Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        Field(description="HTTP请求方法")
    ],
    path: Annotated[
        str,
        Field(description="API请求路径，如'/api/users'或'GET /api/users'")
    ],
    params: Annotated[
        Optional[Mapping[str, Any]],
        Field(description="URL查询参数字典")
    ] = None,
    data: Annotated[
        Optional[Any],
        Field(description="请求体数据，可以是字典、字符串或其他格式")
    ] = None,
    headers: Annotated[
        Optional[Mapping[str, str]],
        Field(description="HTTP请求头字典")
    ] = None,
) -> Dict[str, Any]:
```

**LLM 理解效果**:
- 理解HTTP方法的完整选项
- 知道各种参数的数据类型
- 清楚可选参数的用途

### 5. 断点设置 - set_breakpoint

```python
def set_breakpoint(
    line_number: Annotated[
        Optional[int],
        Field(description="单个断点行号，正整数（单个断点设置时使用）", ge=1)
    ] = None,
    line_numbers: Annotated[
        Optional[str],
        Field(description="断点行号列表，JSON数组格式如'[5,10,15]'（批量断点设置时使用）")
    ] = None,
) -> Dict[str, Any]:
```

**LLM 理解效果**:
- 知道行号必须是正整数
- 理解批量操作的JSON数组格式
- 清楚单个和批量操作的参数区别

## 🎯 验证约束示例

### **数值范围约束**
```python
depth: Annotated[
    Optional[int],
    Field(description="限制显示的资源树深度，正整数", ge=1, le=10)
] = None
```

### **字符串模式约束**
```python
path: Annotated[
    str,
    Field(description="API路径", pattern=r"^/")
] = "/api/default"
```

### **枚举值约束**
```python
method: Annotated[
    Literal["GET", "POST", "PUT", "DELETE"],
    Field(description="HTTP请求方法")
]
```

## 📈 改进效果

### **LLM 体验提升**

| 方面 | 改进前 | 改进后 |
|-----|-------|-------|
| **参数理解** | 仅函数名推断 | 详细描述 + 类型约束 |
| **错误避免** | 运行时错误 | 约束检查 + 提示 |
| **使用效率** | 试错学习 | 直接正确调用 |
| **功能发现** | 被动探索 | 主动引导 |

### **开发体验提升**

- **IDE 支持**: 类型检查和自动补全
- **文档生成**: 自动生成API文档
- **维护便利**: 参数变更时自动验证
- **团队协作**: 标准化参数说明

## 🔧 最佳实践

### **参数描述规范**
1. **清晰简洁**: 用一句话说明参数用途
2. **格式示例**: 提供具体的数据格式示例
3. **约束说明**: 明确参数的取值范围和限制
4. **使用场景**: 说明在什么情况下使用该参数

### **类型选择建议**
- **必需参数**: 使用具体类型，不设默认值
- **可选参数**: 使用 `Optional[Type]`，设置合理的默认值
- **枚举参数**: 使用 `Literal["选项1", "选项2"]`
- **复杂验证**: 使用 `Field` 的 `ge`、`le`、`pattern` 等约束

### **批量操作设计**
- **统一接口**: 单个参数和批量参数使用不同名称
- **格式明确**: 在描述中说明JSON格式要求
- **互斥逻辑**: 单个和批量参数通常不同时使用

这套参数元数据体系让 Magic-API 助手具备了企业级的工具参数定义标准，大大提升了LLM的理解能力和使用体验！🚀
