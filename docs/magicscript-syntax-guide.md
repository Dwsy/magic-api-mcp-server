# Magic-Script `?:` 语法详解

## 🎯 `?:` 语法的作用

### **1. 在函数签名中的作用 (正确用法)**

`?:` 语法**仅在函数签名中有效**，用于标记函数参数为**可选参数**。

#### **语法格式**
```javascript
// 基础语法
functionName(paramName?: Type) -> ReturnType

// 实际示例
asInt(defaultValue?: int) -> int
page(sql: String, limit?: long, offset?: long) -> Object
```

#### **含义说明**
- **位置**: 仅出现在函数参数定义中
- **作用**: 标记该参数为可选参数，调用时可以省略
- **示例**:
  - `asInt(value?: int)` - `value` 参数可以省略
  - `page(sql, limit?, offset?)` - `limit` 和 `offset` 都可以省略

### **2. 在代码逻辑中的错误用法 (已修复)**

❌ **错误用法** (JavaScript风格，Magic-Script不支持):
```javascript
// 错误: 在代码中这样使用是错误的
var page = params.page ?: 1;
var size = params.size ?: 10;
```

✅ **正确用法** (Magic-Script三元运算符):
```javascript
// 正确: 使用标准的条件表达式
var page = params.page ? params.page : 1;
var size = params.size ? params.size : 10;
```

## 📋 语法规则对比

| 场景 | 语法 | 含义 | 状态 |
|------|------|------|------|
| **函数签名** | `param?: Type` | 参数可选 | ✅ 正确 |
| **代码逻辑** | `condition ?: value` | 空值合并 | ❌ 错误 |
| **代码逻辑** | `condition ? value1 : value2` | 三元运算 | ✅ 正确 |

## 🔍 实际修复案例

### **修复前 (错误)**
```javascript
// code_generation.py - 错误用法
var page = params.page ?: 1;
var size = params.size ?: 10;

// kb_examples.py - 错误用法
params.offset = (params.page ?: 1 - 1) * (params.size ?: 10);
```

### **修复后 (正确)**
```javascript
// code_generation.py - 正确用法
var page = params.page ? params.page : 1;
var size = params.size ? params.size : 10;

// kb_examples.py - 正确用法
params.offset = (params.page ? params.page : 1 - 1) * (params.size ? params.size : 10);
```

## ⚠️ 重要提醒

1. **函数签名中**: `?:` 表示"该参数是可选的" ✅
2. **代码逻辑中**: `?:` 语法不存在，应该使用 `? :` 三元运算符 ✅
3. **区分清楚**: 不要将函数签名语法用于实际代码逻辑

## 🎯 最佳实践

- ✅ **函数签名**: `asInt(value?: int)` - 表示 `value` 参数可选
- ✅ **代码逻辑**: `params.page ? params.page : 1` - 三元条件表达式
- ✅ **参数检查**: `if (!param) { /* 处理空值 */ }` - 显式空值检查

---

**总结**: `?:` 语法是函数参数可选性的标记符号，仅在函数签名中使用。在代码逻辑中请使用标准的 `condition ? value1 : value2` 三元运算符语法。
