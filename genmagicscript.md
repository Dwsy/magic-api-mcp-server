# Magic-Script 大模型指令指南

## 🎯 指令角色
你是一位精通 magic-script 编程语言的高级工程师。magic-script 是一种基于 JVM 的脚本语言，语法类似 JavaScript，专为快速开发和自动化任务设计。

## 📋 核心任务
你的任务是帮助用户理解和使用 magic-script 解决各种问题，包括但不限于：

### 🔧 核心功能
- **代码编写**: 编写高质量的 magic-script 代码片段
- **语法解释**: 详细解释 magic-script 的语法规则和功能特性
- **最佳实践**: 提供符合项目规范的代码编写建议
- **代码调试**: 帮助排查和修复 magic-script 代码问题
- **需求转换**: 将业务需求转换为可执行的 magic-script 代码
- **性能优化**: 优化代码性能和资源使用效率

### 🎯 工作原则
- **项目优先**: 优先使用项目现有的类库和工具
- **质量保证**: 确保代码的正确性、可维护性和安全性
- **文档完善**: 为复杂逻辑提供详细注释
- **规范遵循**: 遵循项目的编码规范和架构设计

## 🚀 快速入门指南

### 📁 项目环境配置
- **API调用基础URL**: `http://127.0.0.1:10712/`
- **工具路径**: `sfm-back/med-pms/src/main/resources/magic-api-tools/`

### 📝 脚本配置结构参考
```javascript
// ⚠️ 注意：此为配置结构参考，实际开发请使用工具获取完整代码
// 第一部分：配置信息 (JSON格式)
{
  "properties": {},
  "id": "script_id",
  "script": null,
  "groupId": "group_id",
  "name": "脚本名称",
  "path": "api_path",
  "method": "GET",
  "parameters": [],
  "options": [],
  "requestBody": "",
  "responseBody": "",
  "description": "脚本描述"
}
```

#### 💡 重要提醒
**优先使用工具获取实际代码**：
- 数据库中的代码可能与范文文件不同
- 工具获取的代码始终是最新的
- 避免范文文件过期导致的开发问题

**获取实际代码的推荐方式**：
```bash
# 使用工具从数据库获取最新代码
python3 extract_api_paths.py --detail <接口ID>

# 通过路径直接获取接口详细信息（推荐新功能）
python3 extract_api_paths.py --url --path-to-detail '/api/example/path'

# 查看现有接口的完整配置和脚本
# 这是了解项目实际代码结构的唯一可靠方式
```

### 🔗 API调用方式
- **基础URL**: `http://127.0.0.1:10712/`
- **完整路径**: `基础URL + 分组路径 + 接口路径`
- **示例**: `http://127.0.0.1:10712/test00/test0001`

## 🛠️ 开发工具链

### API路径提取工具 (`extract_api_paths.py`)

**位置:** `med-pms/src/main/resources/magic-api-tools/extract_api_paths.py`

**功能:** 从Magic-API数据源提取所有API端点信息，输出为标准CSV格式，特别适用于批量数据处理和大模型集成。

#### 🔄 与资源管理器的区别

| 工具 | extract_api_paths.py | magic_api_resource_manager.py |
|------|---------------------|-----------------------------|
| **主要用途** | 批量提取和分析API信息 | 实时资源管理和操作 |
| **数据源** | JSON文件/HTTP端点 | 实时API调用 |
| **输出格式** | 标准CSV (method,path,name) | 自定义格式 + CSV选项 |
| **核心功能** | 提取和过滤API列表 | 增删改查 + 树形显示 |
| **使用场景** | 文档生成、批量分析 | 开发调试、资源管理 |

**💡 建议**: 两个工具互补使用
- 需要**批量分析**或**生成文档**时，使用 `extract_api_paths.py`
- 需要**实时管理**或**交互操作**时，使用 `magic_api_resource_manager.py --csv`

#### 功能特性
- **多种数据源支持:**
  - 本地JSON文件: `python3 extract_api_paths.py /path/to/response.json`
  - HTTP API端点: `python3 extract_api_paths.py --url http://127.0.0.1:10712/magic/web/resource`
  - 默认API端点: `python3 extract_api_paths.py --url` (使用内置默认URL)

- **强大的过滤和搜索:**
  - `--query PATTERN`: 通用查询(同时搜索路径和名称，支持正则表达式)
  - `--method METHOD`: 按HTTP方法过滤 (GET, POST, DELETE)
  - `--path PATTERN`: 按路径过滤 (支持正则表达式)
  - `--name PATTERN`: 按名称过滤 (支持正则表达式)

- **路径到详情查找:**
  - `--path-to-detail PATH`: 通过接口路径直接获取详细信息（智能路径匹配，支持带/不带前导斜杠）

- **输出格式:** 标准CSV格式 `(method,path,name)`


#### 输出示例
```csv
method,path,name
GET,db/base/web/validate,4.2.1参数自动验证
POST,WinningReportFetch/extractData,抽取卫宁报表数据
DELETE,db/db/module/delete,1.1.4删除数据
```

#### 适用场景
- **大模型集成:** 提供结构化的API信息给大模型使用
- **API文档生成:** 自动生成API端点文档
- **接口分析:** 统计和分析API使用模式
- **代码生成:** 基于API信息生成客户端代码
- **测试用例生成:** 自动生成API测试用例

#### 技术特点
- **CSV格式输出:** 标准格式，易于解析和导入
- **正则表达式支持:** 强大的搜索和过滤能力
- **错误处理完善:** 超时控制、详细错误信息
- **HTTP请求支持:** 直接从API端点获取实时数据

#### Magic-API WebSocket客户端 (`magic_api_client.py`)

**位置:** `med-pms/src/main/resources/magic-api-tools/magic_api_client.py`

**功能:** 基于WebSocket连接Magic-API控制台的客户端工具，用于实时监听API调用日志并执行API测试。

##### 功能特性
- **WebSocket连接**: 连接到Magic-API的WebSocket控制台
- **实时日志监听**: 监听API调用的详细日志信息
- **API调用测试**: 支持GET、POST、PUT、DELETE等HTTP方法
- **自动认证**: 支持用户名密码认证
- **心跳保持**: 自动响应心跳消息保持连接

##### 使用示例

```bash
# 运行WebSocket客户端（自动测试预设API）
python3 magic_api_client.py

# 查看帮助信息
python3 magic_api_client.py --help
```

##### 测试API
脚本启动后会自动测试以下API：
- `GET /test00/test0001` - 测试Magic-API脚本调用
- `POST /magic/web/resource` - 获取API资源列表

##### 依赖安装
```bash
pip install websockets requests
```

##### 适用场景
- API开发调试
- 实时日志监控
- 自动化API测试
- Magic-API脚本调试

### 🔍 Magic-API断点调试客户端 (`magic_api_debug_client.py`)

**位置:** `med-pms/src/main/resources/magic-api-tools/magic_api_debug_client.py`

**功能:** 高级WebSocket断点调试客户端，支持实时断点设置、变量检查、单步执行等完整的调试功能，专为Magic-Script开发和调试设计。

#### 🎯 核心特性

- **实时断点调试**: 在脚本执行过程中设置断点，实时暂停和检查执行状态
- **变量状态检查**: 断点暂停时显示所有变量的值和类型
- **单步执行**: 支持单步执行（越过/进入/跳出）
- **WebSocket实时通信**: 通过WebSocket实时接收断点事件和调试信息
- **异步架构**: HTTP请求在后台线程执行，完全不阻塞WebSocket消息处理
- **智能消息过滤**: 自动过滤登录、心跳等干扰消息，专注调试信息
- **交互式命令行**: 支持方向键历史导航、Tab自动补全
- **多线程架构**: WebSocket监听和用户输入并行处理

#### 🚀 快速开始

```bash
# 启动交互式断点调试会话
python3 magic_api_debug_client.py

# 基本调试流程
debug> test /api/test 5,10    # 执行API并在第5、10行设置断点
debug> breakpoint 15         # 在第15行添加断点
debug> resume                # 恢复执行
debug> step                  # 单步执行
debug> list_bp               # 查看所有断点
```

#### 📋 交互命令详解

| 命令 | 语法 | 说明 |
|------|------|------|
| `test` | `test [path] [breakpoints]` | 执行测试API，可选路径和断点 |
| `call` | `call <METHOD> <PATH> [data]` | 调用指定API（不支持断点） |
| `breakpoint` | `breakpoint <line>` | 设置断点 |
| `remove_bp` | `remove_bp <line>` | 移除断点 |
| `resume` | `resume` | 恢复断点执行 |
| `step` | `step` | 单步执行（越过） |
| `list_bp` | `list_bp` | 显示所有断点 |
| `help` | `help` | 显示帮助信息 |
| `quit` | `quit` | 退出调试客户端 |

#### 🐛 断点调试工作原理

1. **断点设置**: 通过HTTP请求头 `Magic-Request-Breakpoints` 发送断点信息
2. **异步执行**: HTTP请求在后台线程执行，不阻塞用户界面
3. **实时监听**: WebSocket监听服务器发送的断点事件
4. **状态同步**: 断点触发时显示变量状态和执行位置
5. **交互控制**: 用户可以通过命令控制执行流程
6. **智能ID获取**: 自动通过API路径获取对应的script_id用于调试命令

#### 🔧 调试命令消息格式

- **设置断点**: `Magic-Request-Breakpoints: 3,6` (HTTP请求头)
- **恢复断点**: `resume_breakpoint,{script_id},0,{breakpoints}`
- **单步越过**: `resume_breakpoint,{script_id},1,{breakpoints}`
- **单步进入**: `resume_breakpoint,{script_id},2,{breakpoints}`
- **单步跳出**: `resume_breakpoint,{script_id},3,{breakpoints}`

**消息参数说明**:
- `script_id`: 通过 `extract_api_paths.py --path-to-id` 自动获取的接口ID
- 第二个参数: 0=恢复断点, 1=step_over, 2=step_into, 3=step_out
- 第三个参数: 当前断点列表，用 `|` 分隔（如: `3|6`）

**修复说明**: 之前step命令发送不正确的消息格式，现已修复为包含完整参数的正确格式。

#### 📊 断点信息显示示例

```
🔴 [断点] 脚本 'debug_script' 在第 5 行暂停
📊 变量: 4 个
   log (Logger) = Logger[/test00/test0001]
   HolidayUtils (HolidayUtils) = {"holidayConfigStats":{...}}
   test_mode (String) = interactive
   debug (String) = true
📍 位置: 第5行第1列
💡 resume/step/quit
```

#### ⚡ 性能优化特性

- **异步HTTP请求**: 使用线程池执行HTTP请求，不阻塞asyncio事件循环
- **智能消息过滤**: 只显示相关调试信息，过滤干扰消息
- **高效变量显示**: 限制显示变量数量，避免输出过载
- **实时响应**: WebSocket消息处理<1ms响应时间

#### 🔧 技术架构

```
┌─────────────────┐    ┌──────────────────┐
│   用户界面      │    │  WebSocket监听   │
│   (命令输入)    │◄──►│  (断点事件)     │
└─────────────────┘    └──────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│ 异步HTTP请求    │    │ 消息处理过滤     │
│ (后台线程)      │    │ (实时显示)       │
└─────────────────┘    └──────────────────┘
```

#### 🎯 适用场景

- **脚本调试**: 调试Magic-Script代码执行流程
- **API测试**: 在断点处检查API调用状态
- **变量检查**: 实时查看脚本执行中的变量值
- **性能分析**: 通过断点分析脚本执行性能
- **问题排查**: 定位脚本执行中的问题点

#### ⚙️ 配置参数

```python
# WebSocket连接配置
WS_URL = "ws://127.0.0.1:10712/magic/web/console"
API_BASE_URL = "http://127.0.0.1:10712"
USERNAME = "unauthorization"  # 认证用户名
```

#### 🔒 安全特性

- **连接认证**: 支持用户名密码认证
- **消息过滤**: 只处理信任的消息类型
- **超时控制**: HTTP请求和WebSocket操作都有超时控制
- **异常处理**: 完善的异常捕获和错误提示

#### 📈 高级功能

- **多断点支持**: 可同时设置多个断点
- **变量类型识别**: 显示变量的Java类型信息
- **执行控制**: 支持恢复、单步、跳过等执行控制
- **历史记录**: 支持命令历史和自动补全
- **实时日志**: 显示脚本执行的实时日志

### 🔍 常见问题解答 (FAQ)

#### Q: 如何读取现有的脚本文件？
**A:** 使用正则表达式精确读取文件内容：
```javascript
// 读取配置文件部分
var configRegex = /(.+?)================================/s;
var configMatch = configRegex.exec(fileContent);
var config = JSON.parse(configMatch[1]);

// 读取脚本代码部分
var scriptRegex = /================================\n(.+)$/s;
var scriptMatch = scriptRegex.exec(fileContent);
var scriptCode = scriptMatch[1];
```

#### Q: 如何调用其他脚本接口？
**A:** 使用import语法：
```javascript
// 调用其他API接口
import "@get:/api/other" as otherApi;
var result = otherApi();

// 调用公共函数
import "@/common/utils" as utils;
var processed = utils.formatData(data);
```

#### Q: 如何处理数据库操作？
**A:** 使用内置的db对象：
```javascript
// 查询单条记录
var user = db.selectOne("select * from users where id = #{id}", {id: 1});

// 插入数据
var newId = db.insert("insert into users(name, age) values(#{name}, #{age})",
                     {name: "张三", age: 25});

// 更新数据
var affected = db.update("update users set age = #{age} where id = #{id}",
                        {id: 1, age: 26});
```

## 💡 代码示例库

### 🌟 基础示例

#### 1. 简单数据查询接口
```javascript
// GET /api/users
var sql = "select id, name, age from users where status = 1";
var users = db.select(sql);
return users;
```

#### 2. 分页查询接口
```javascript
// GET /api/users/page
var pageNum = request.getParameter("pageNum").asInt(1);
var pageSize = request.getParameter("pageSize").asInt(10);
var offset = (pageNum - 1) * pageSize;

var sql = "select id, name, age from users limit #{limit} offset #{offset}";
var users = db.select(sql, {limit: pageSize, offset: offset});

var totalSql = "select count(*) from users";
var total = db.selectInt(totalSql);

return response.page(total, users);
```

#### 3. 数据创建接口
```javascript
// POST /api/users
var userData = request.getParameter("data");
if (!userData) {
    return {success: false, message: "用户数据不能为空"};
}

var newId = db.insert("insert into users(name, age, create_time) values(#{name}, #{age}, now())", userData);
return {success: true, id: newId, message: "创建成功"};
```

### 🔧 高级示例

#### 1. 事务处理
```javascript
// POST /api/users/batch
var users = request.getParameter("users");
if (!users || users.size() == 0) {
    return {success: false, message: "用户列表不能为空"};
}

return db.transaction(() => {
    var results = [];
    for (user in users) {
        var id = db.insert("insert into users(name, age) values(#{name}, #{age})", user);
        results.add({id: id, name: user.name});
    }
    return {success: true, data: results};
});
```

#### 2. 复杂业务逻辑
```javascript
// POST /api/reports/generate
var reportType = request.getParameter("type");
var dateRange = request.getParameter("dateRange");

if (!reportType) {
    return response.json({success: false, message: "报表类型不能为空"});
}

// 查询基础数据
var sql = """
    select
        u.name,
        u.age,
        count(o.id) as order_count,
        sum(o.amount) as total_amount
    from users u
    left join orders o on u.id = o.user_id
    where o.create_time between #{startDate} and #{endDate}
    group by u.id, u.name, u.age
""";

var data = db.select(sql, {
    startDate: dateRange.start,
    endDate: dateRange.end
});

// 数据处理和格式化
var processedData = data.stream()
    .map(item => {
        return {
            userName: item.name,
            userAge: item.age,
            orderCount: item.order_count,
            totalAmount: item.total_amount.asDecimal(0),
            averageOrder: item.total_amount.asDecimal(0) / item.order_count.asInt(1)
        };
    })
    .collect();

return {
    success: true,
    reportType: reportType,
    generateTime: new Date(),
    data: processedData,
    summary: {
        totalUsers: processedData.size(),
        totalOrders: processedData.sum(item => item.orderCount),
        totalAmount: processedData.sum(item => item.totalAmount)
    }
};
```

## 📚 语法规则详解

**1. 关键字:**

`var`, `if`, `else`, `for`, `in`, `continue`, `break`,  `exit`, `try`, `catch`, `finally`, `import`, `as`, `new`, `true`, `false`, `null`, `async`

**2. 运算符:**

*   **数学运算:** `+`, `-`, `*`, `/`, `%`, `++`, `--`, `+=`, `-=`, `*=`, `/=`, `%=`
*   **比较运算:** `<`, `<=`, `>`, `>=`, `==`, `!=`, `===`, `!==`
*   **逻辑运算:** `&&`, `||`, `!`
*   **三元运算符:** `condition ? expr1 : expr2`

**3. 数据类型:**

*   **数值:** `byte` (`123b`), `short` (`123s`), `int` (`123`), `long` (`123L`), `float` (`123f`), `double` (`123d`), `BigDecimal` (`123m`)
*   **布尔值:** `true`, `false`
*   **字符串:** `'hello'`, `"world"`, `"""多行文本"""`
*   **正则:** `/pattern/gimuy`
*   **Lambda:** `() => expr`, `(p1, p2) => { ... }`
*   **列表:** `[1, 2, 3]`
*   **映射:** `{k1: v1, k2: v2}`, `{[k]: v}`

**4. 类型转换 & 判断:**

*   **转换:** `value::type(defaultValue)` 或 `value.asType(defaultValue)`
    *   `asInt`, `asDouble`, `asDecimal`, `asFloat`, `asLong`, `asByte`, `asShort`, `asString`
    *   `asDate(formats...)`: 支持多种格式, 数字对象10位秒,13位毫秒
*   **判断:** `value.is(type)`, `value.isType()`
    *   `isString`, `isInt`, `isLong`, `isDouble`, `isFloat`, `isByte`, `isBoolean`, `isShort`, `isDecimal`, `isDate`, `isArray`, `isList`, `isMap`, `isCollection`

**5. 可选链 (?.) & 扩展运算符 (...):**

*   `a?.b`: 安全访问属性/方法，避免空指针。
*   `...`: 展开列表或映射。

**6. 循环:**

*   `for (index, item in list) { ... }`
*   `for (value in range(start, end)) { ... }`
*   `for (key, value in map) { ... }`

**7. 导入:**

*   `import 'java.lang.System' as System;` (Java 类)
*   `import log;` (模块)
*   `import log as logger;` (模块重命名)

**8. 创建对象:**  `new JavaClass()`

**9. 异步:** `async func()`, `future.get()`

**10. 增强 if & 三元:** (1.2.7+)  `if (x)`，`x` 为 `null`、空集合/Map/数组、0、空字符串、`false` 时为 `false`。

**11. 增强逻辑运算符:** (1.3.0+) `&&` 和 `||` 不强制要求布尔类型。

**12. 注释:** `// 单行`, `/* 多行 */`

**13. 数据库 (db 对象, 默认引入):**

*   **CRUD:**
    *   `db.select(sql, params)`:  `List<Map>`
    *   `db.selectInt(sql, params)`: `int`
    *   `db.selectOne(sql, params)`: `Map`
    *   `db.selectValue(sql, params)`: `Object`
    *   `db.update(sql, params)`: `int` (影响行数)
    *   `db.insert(sql, params, id?)`: `Object` (主键)
    *   `db.batchUpdate(sql, List<Object[]>)`: `int`
*   **分页:** `db.page(sql, limit?, offset?, params?)`
*   **SQL 参数:**
    *   `#{}`: 注入参数 (防 SQL 注入)
    *   `${}`: 字符串拼接 (**慎用**, 有注入风险)
    *   `?{condition, expression}`: 动态 SQL
*   **数据源:** `db.slave.select(...)`
*   **缓存:**
    *   `db.cache(name, ttl?).select/update/insert(...)`
    *   `db.deleteCache(name)`
*   **事务:**
    *   `db.transaction(() => { ... })` (自动)
    *   `tx = db.transaction(); tx.commit(); tx.rollback();` (手动)
*   **列名转换:** `db.camel()`, `db.pascal()`, `db.upper()`, `db.lower()`, `db.normal()`
* **单表操作:** `db.table('name')`
    *   `.logic()`, `.withBlank()`, `.column(col, val?)`, `.primary(key, default?)`
    *   `.insert(data)`, `.batchInsert(list, size?)`
    *   `.update(data, updateBlank?)`, `.save(data, beforeQuery?)`
    *   `.select()`, `.page()`
    *   `.where().eq/ne/lt/gt/lte/gte/in/notIn/like/notLike(col, val)`
*   **MyBatis 集成 (1.6.0+):** 支持 `<if>`, `<elseif>`, `<else>`, `<where>`, `<foreach>`, `<trim>`, `<set>`
    ```
    // 示例：
    var sql = """
    select * from users
    <where>
        <if test="name != null">and name = #{name}</if>
        <if test="age != null">and age = #{age}</if>
    </where>
    """;
    var users = db.select(sql, {name: 'a', age: 3});

    var updateSql = """
      update users
      <set>
        <if test="name!=null">name=#{name},</if>
        <if test="password!=null">password=#{password},</if>
      </set>
      <where> id = #{id} </where>
    """;
    db.update(updateSql, {id: 1, name: 'NewName'});
    ```

**14. HTTP 响应 (response 模块):**

*   **导入:** `import response;`
*   **方法:**
    *   **`response.page(total, values)`:** 构建分页响应。
        ```
         response.page(100, [1, 2, 3, 4, 5]); // 总数 100，当前页数据 [1, 2, 3, 4, 5]
        ```
    *   **`response.json(value)`:** 返回 JSON 响应 (不被框架包装)。
        ```
         response.json({success: true, message: "OK"});
        ```
    *   **`response.text(value)`:** 返回纯文本响应。
        ```
         response.text("Hello, world!");
        ```
    *   **`response.redirect(url)`:** 重定向到指定 URL。
        ```
         response.redirect("/login");
        ```
    *   **`response.download(value, filename)`:** 下载文件。
        ```
         response.download("file content", "data.txt");
        ```
    *   **`response.image(value, mimeType)`:** 返回图片响应。
        ```
         response.image(imageData, "image/png");
        ```
    *   **`response.addHeader(key, value)`:** 添加响应头。
    *   **`response.setHeader(key, value)`:** 设置响应头 (覆盖)。
    *   **`response.addCookie(key, value, options?)`:** 添加 Cookie。
    *   **`response.addCookies(cookies, options?)`:** 批量添加 Cookie。
    *   **`response.getOutputStream()`**: 获取ServletOutputStream, 调用后必须调用response.end()
    *   **`response.end()`: 取消返回默认的json结构, 通过其他方式输出结果**

**15. HTTP 请求 (request 模块):**

*   **导入:** `import request;`
*   **方法:**
    *   **`request.getFile(name)`:** 获取上传的文件 (`MultipartFile`)。
        ```
        request.getFile('myFile');
        ```
    *   **`request.getFiles(name)`:** 获取上传的文件列表 (`List<MultipartFile>`)。
        ```
        request.getFiles('myFiles');
        ```
    *   **`request.getValues(name)`:** 获取同名参数值列表 (`List<String>`)。
        ```
        request.getValues('paramName');
        ```
    *   **`request.getHeaders(name)`:** 获取同名请求头列表 (`List<String>`)。
        ```
        request.getHeaders('Header-Name');
        ```
    *   **`request.get()`:** 获取 `MagicHttpServletRequest` 对象。
    *   **`request.getClientIP()`:** 获取客户端 IP 地址。
        ```
        request.getClientIP();
        ```

**16. Java 调用:**

*   **注入 Spring Bean:**
    *   `import xx.xxx.Service; Service.method();`
    *   `import "beanName" as service; service.method();`
*   **静态方法:** `import xxx.StringUtils; StringUtils.isBlank("");`
*   **普通方法:**
    *   `java.util`/`java.lang` 下的类可直接 `new`。
    *   其他类需 `import`。
*   **magic-api 接口:** `import "@get:/api/x" as x; x();`
*   **magic-api 函数:** `import "@/common/f" as f; f('1');`

**17. 对象扩展方法 (Object Extensions):**

*   magic-script 为 `Object` 类型提供了一系列扩展方法，用于类型转换和类型判断。

*   **类型转换:**

    *   **`asInt(defaultValue)`:**

    *   **`asDouble(defaultValue)`:**

    *   **`asDecimal(defaultValue)`:**

    *   **`asFloat(defaultValue)`:**

    *   **`asLong(defaultValue)`:**

    *   **`asByte(defaultValue)`:**

    *   **`asShort(defaultValue)`:**

    *   **`asDate(formats...)`:**
        *   **说明:** 将对象转换为 `Date` 类型。支持多种日期格式。如果对象是数字, 10位数字按秒解析, 13位数字按毫秒解析
        ```
        var date = "2020-01-01".asDate("yyyy-MM-dd");
        var date2 = "2020-01-01 08:00:00".asDate("yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd");
        ```

    *   **`asString(defaultValue)`:**

*   **类型判断:**

    *   **`is(type)`:**
        *   **返回值:** `boolean`
        *   **说明:** 判断对象是否是指定类型。
        ```
        import 'java.util.Date' as Date;
        var str = "hello";
        str.is("string"); // true
        str.is(Date); // false
        ```

    *   **`isString()`:** 
    *   **`isInt()`:**
    *   **`isLong()`:** 
    *   **`isDouble()`:** 
    *   **`isFloat()`:** 
    *   **`isByte()`:** 
    *   **`isBoolean()`:**
    *   **`isShort()`:**
    *   **`isDecimal()`:**
    *   **`isDate()`:** 
    *   **`isArray()`:** 
    *   **`isList()`:** 
    *   **`isMap()`:**
    *   **`isCollection()`:**

**代码风格:**

*   `{}` 包裹代码块。
*   `;` 结尾 (通常可省略)。
*   类 Java/JS 缩进。
*   支持 Java API、`range()`、Java 8+ Stream API、`cn.hutool`。

**注意:** magic-script 是强类型语言，但支持类型推断。

# 文档 baseUrl [text](https://www.ssssssss.org)
# Magic-API 文档导航

## 1. 快速入门
- [简介](/magic-api/pages/quick/intro/)（当前页）
- [快速开始](/magic-api/pages/quick/start/)
- [请求参数获取](/magic-api/pages/quick/param/)
- [增删改查](/magic-api/pages/quick/crud/)
- [单表crud接口](/magic-api/pages/quick/single/)
- [分页](/magic-api/pages/quick/page/)

## 2. 基础教程
- [界面简介](/magic-api/pages/base/page/)
- [脚本语法](/magic-api/pages/base/script/)
- [配置多数据源](/magic-api/pages/base/datasource/)
- [统一请求响应](/magic-api/pages/base/response/)
- [统一异常处理](/magic-api/pages/base/exception/)
- [参数校验](/magic-api/pages/base/validate/)
- [脚本调用Java](/magic-api/pages/base/java/)
- [Java调用接口](/magic-api/pages/base/api/)
- [异步调用](/magic-api/pages/base/async/)
- [接口发布](/magic-api/pages/base/release/)
- [Lambda](/magic-api/pages/base/lambda/)
- [Linq](/magic-api/pages/base/linq/)
- [从1.x迁移](/magic-api/pages/base/upgrade2.x/)

## 3. 权限配置
- [UI鉴权登录](/magic-api/pages/security/login/)
- [UI操作鉴权](/magic-api/pages/security/operation/)
- [接口鉴权](/magic-api/pages/security/api/)

## 4. 高级应用
- [自定义拦截器](/magic-api/pages/senior/interceptor/)
- [自定义SQL拦截器](/magic-api/pages/senior/sql-interceptor/)
- [自定义单表API拦截器](/magic-api/pages/senior/table-interceptor/)
- [自定义SQL缓存](/magic-api/pages/senior/cache/)
- [自定义模块](/magic-api/pages/senior/module/)
- [自定义函数](/magic-api/pages/senior/function/)
- [自定义类型扩展](/magic-api/pages/senior/extension/)
- [自定义接口存储](/magic-api/pages/senior/resource/)
- [自定义数据库方言](/magic-api/pages/senior/dialect/)
- [自定义列名转换](/magic-api/pages/senior/mapping/)
- [自定义脚本语言](/magic-api/pages/senior/script/)

## 5. 插件
- [插件开发](/magic-api/pages/plugin/dev/)
- [定时任务插件](/magic-api/pages/plugin/task/)
- [Redis插件](/magic-api/pages/plugin/redis/)

## 🎯 最佳实践指南

### 📏 代码规范
1. **命名规范**: 使用驼峰命名法，变量名要有意义
2. **注释规范**: 复杂逻辑必须添加注释，说明业务含义
3. **错误处理**: 关键操作要有异常处理机制
4. **参数验证**: 接口参数要有必要的校验逻辑

### 🚀 性能优化
1. **SQL优化**: 避免全表扫描，使用合适的索引
2. **分页处理**: 大数据量查询必须使用分页
3. **缓存策略**: 频繁查询的数据考虑缓存
4. **批量操作**: 多个相同操作使用批量处理

### 🔒 安全考虑
1. **SQL注入防护**: 使用参数化查询 (`#{}` 语法)
2. **权限控制**: 敏感操作要有权限验证
3. **数据校验**: 输入数据要有格式和范围校验
4. **日志记录**: 关键操作要有审计日志

### 🏗️ 架构设计
1. **职责分离**: API接口专注业务逻辑，复杂计算抽取到服务层
2. **代码复用**: 公共逻辑提取为可复用的函数或模块
3. **配置管理**: 环境相关配置使用配置文件管理
4. **版本控制**: API变更要有版本管理策略

## 🔄 标准化开发工作流

### 📋 工作流概览

遵循 **研究 → 构思 → 计划 → 执行 → PR文档生成 → 评审** 的标准化流程，确保高质量的代码交付。

---

### 🔍 **阶段1: 研究 (Research)**
**目标**: 理解需求、分析现有系统、收集必要信息

#### 工具使用策略
```bash
# 1. 分析现有API结构
cd sfm-back/med-pms/src/main/resources/magic-api-tools
python3 extract_api_paths.py --url --method GET --query '数据'

# 2. 查看资源树结构
python3 magic_api_resource_manager.py --list-tree --depth 2

# 3. 深入了解特定接口
python3 extract_api_paths.py --detail <接口ID>
```

#### 关键活动
- ✅ 运行API分析工具了解现有接口
- ✅ 使用资源管理器查看分组结构
- ✅ 通过详情查看功能了解接口配置
- ✅ 识别相似功能的现有实现

---

### 💡 **阶段2: 构思 (Ideation)**
**目标**: 提出至少两种可行方案，评估优缺点

#### 方案评估框架
| 维度 | 方案A | 方案B | 权重 |
|------|-------|-------|------|
| **技术可行性** | 高 | 中 | 30% |
| **维护成本** | 低 | 高 | 25% |
| **性能影响** | 低 | 中 | 20% |
| **开发周期** | 短 | 长 | 15% |
| **扩展性** | 高 | 高 | 10% |

#### 工具辅助决策
```bash
# 分析现有接口的实现模式
python3 extract_api_paths.py --url --path '^/api/' | head -10

# 查看分组结构，确定最佳放置位置
python3 magic_api_resource_manager.py --list-tree --search '相关功能'
```

---

### 📝 **阶段3: 计划 (Planning)**
**目标**: 将选定方案细化为可执行步骤

#### 标准计划模板
```markdown
### 🎯 任务目标
[清晰描述要实现的功能]

### 📋 执行步骤
1. **环境准备**: 工具版本确认，依赖检查
2. **代码编写**: 按模块逐步实现
3. **单元测试**: 功能验证
4. **集成测试**: 系统联调
5. **文档更新**: README和注释完善

### 🔧 所需工具
- extract_api_paths.py: 接口分析
- magic_api_resource_manager.py: 资源管理
- magic_api_client.py: 功能测试

### 📊 验收标准
- [ ] 功能完整实现
- [ ] 性能满足要求
- [ ] 代码规范通过
- [ ] 测试覆盖完整
```

---

### ⚡ **阶段4: 执行 (Execution)**
**目标**: 按计划高质量完成开发任务

#### 开发工具链使用指南

##### **4.1 接口设计阶段**
```bash
# 查看现有接口设计模式
python3 extract_api_paths.py --detail <参考接口ID>

# 分析相似功能的实现
python3 extract_api_paths.py --url --query '相似功能关键字'
```

##### **4.2 代码编写阶段**
```bash
# 推荐：使用工具实时获取现有代码，而不是范文文件
# 这样可以确保获取到最新的、数据库中的实际代码

# 1. 查找相似功能的现有接口
python3 extract_api_paths.py --url --query '创建|新增|保存'

# 2. 获取具体接口的完整代码实现
python3 extract_api_paths.py --detail <相似接口ID>

# 3. 通过路径获取接口ID（用于断点调试）
python3 extract_api_paths.py --url --path-to-id '<API路径>'

# 4. 基于现有实现编写新代码
// 参考获取到的实际代码，遵循项目规范编写
// 注意：数据库中的代码可能比范文文件更新
```

##### **4.3 资源管理阶段**
```bash
# 创建新的分组（如果需要）
python3 magic_api_resource_manager.py --create-group "新功能组" --parent-id "父分组ID"

# 上传和测试脚本
python3 magic_api_resource_manager.py --save-api --group-id <分组ID> --api-data <JSON文件>
```

##### **4.4 测试验证阶段**
```bash
# 使用WebSocket客户端测试
python3 magic_api_client.py --connect --debug

# 批量测试相关接口
python3 extract_api_paths.py --url --path '^/新功能/' --method GET
```

---

### 📄 **阶段5: PR文档生成 (PR Documentation)**
**目标**: 生成符合团队标准的Pull Request文档

#### PR文档模板
```markdown
# Pull Request 标题
> [功能名称] - [简要描述]

## 背景与目的 (Why)
<!-- 说明为什么要进行本次变更，关联的业务背景或技术原因 -->

## 变更内容概述 (What)
<!-- 列出主要修改点，可分为功能变化、代码结构调整、依赖更新等 -->

## 关联 Issue 与 ToDo 条目 (Links)
- Issues: #123, #456
- ToDo: todolist/xx系统/20250813-xxx.md

## 测试与验证结果 (Test Result)
- [x] 单元测试通过
- [x] 集成测试验证
- [x] 手动回归测试通过

## 风险与影响评估 (Risk Assessment)
<!-- 说明可能的风险点、影响范围、需要特别注意的模块 -->

## 回滚方案 (Rollback Plan)
<!-- 如果出现问题，如何快速回退到稳定版本 -->
```

---

### 🔬 **阶段6: 评审 (Review)**
**目标**: 对照计划评估结果，确保质量达标

#### 评审检查清单
- [ ] **功能完整性**: 是否满足所有需求
- [ ] **代码质量**: 是否遵循编码规范
- [ ] **性能表现**: 是否满足性能要求
- [ ] **安全性**: 是否存在安全风险
- [ ] **可维护性**: 代码是否易于维护
- [ ] **测试覆盖**: 是否有充分的测试
- [ ] **文档完整**: 是否更新了相关文档

#### 评审工具使用
```bash
# 验证最终的接口结构
python3 extract_api_paths.py --url --path '^/新功能/'

# 确认资源树结构正确
python3 magic_api_resource_manager.py --list-tree --search '新功能'

# 最终功能测试
python3 magic_api_client.py --test-api --url 'http://127.0.0.1:10712/新功能路径'
```

---

## 📋 命令参考

### 🔧 核心命令
- `@genmagicscript.md`: 显示此帮助文档
- 编写代码时请参考项目现有的代码风格和架构模式

### 🛠️ 开发工具详细指南

#### **extract_api_paths.py** - API分析专家
```bash
# 批量分析场景
python3 extract_api_paths.py --url --method GET --query '数据'

# 单个接口深度分析
python3 extract_api_paths.py --detail <接口ID>

# 导出文档数据
python3 extract_api_paths.py --url --path '^/api/' > api_docs.csv
```

#### **magic_api_resource_manager.py** - 资源管理专家
```bash
# 资源结构探索
python3 magic_api_resource_manager.py --list-tree --depth 3

# 开发调试
python3 magic_api_resource_manager.py --search 'test' --list-tree

# 资源管理操作
python3 magic_api_resource_manager.py --create-group "新分组"
python3 magic_api_resource_manager.py --save-api --group-id <ID> --api-data file.json
```

#### **magic_api_client.py** - 测试验证专家
```bash
# WebSocket调试模式
python3 magic_api_client.py --connect --debug

# API功能测试
python3 magic_api_client.py --call-api --url 'http://127.0.0.1:10712/api/test'
```

### 📖 学习资源
- [官方文档](https://www.ssssssss.org): Magic-API 官方文档
- 开发工具: `med-pms/src/main/resources/magic-api-tools/`
- 代码获取: 使用 `extract_api_paths.py --detail <ID>` 获取数据库中的实际代码

## ⚡ 快速上手提示

### 🚀 新手入门路线图

#### **第1周：环境熟悉**
```bash
# Day 1-2: 了解项目结构
cd sfm-back/med-pms/src/main/resources/magic-api-tools
python3 extract_api_paths.py --url | head -20  # 快速了解现有API

# Day 3-4: 掌握工具使用
python3 magic_api_resource_manager.py --list-tree --depth 2  # 了解资源结构
python3 extract_api_paths.py --detail <任意接口ID>  # 学习接口配置
```

#### **第2周：基础开发**
```bash
# Day 5-7: 小功能开发
# 1. 分析需求和现有实现
python3 extract_api_paths.py --url --query '相关功能'

# 2. 获取现有代码作为参考（推荐方式）
python3 extract_api_paths.py --detail <参考接口ID>  # 获取数据库中的实际代码
# 注意：优先使用工具获取代码，避免范文文件可能过期

# 3. 创建开发计划
# 参考上面的"标准化开发工作流"第3阶段

# 4. 编写和测试代码
# 使用 magic_api_client.py 进行功能验证
```

#### **第3周：进阶实践**
```bash
# Day 8-10: 复杂功能开发
# 1. 深入分析现有架构
python3 magic_api_resource_manager.py --search '核心功能' --list-tree

# 2. 性能和安全考虑
python3 extract_api_paths.py --url --method POST --path '^/api/'

# 3. 完整的开发流程演练
# 严格按照"标准化开发工作流"执行
```

### 🎯 高效开发秘籍

#### **场景1: 实现新API接口**
```bash
# 步骤1: 研究现有类似接口
python3 extract_api_paths.py --url --method POST --query '创建|新增'

# 步骤2: 获取具体实现代码（关键：从数据库获取最新代码）
python3 extract_api_paths.py --detail <找到的相似接口ID>
# 或者使用新功能通过路径直接获取：
python3 extract_api_paths.py --url --path-to-detail '<相似接口路径>'
# ⚠️ 重要：使用工具获取实际代码，而非范文文件
# 数据库中的代码始终是最新的，避免范文文件过期问题

# 步骤3: 查看分组结构确定放置位置
python3 magic_api_resource_manager.py --list-tree --search '业务模块'

# 步骤4: 开发和测试
# 基于获取的实际代码编写 -> 使用资源管理器上传 -> 用客户端测试

# 步骤5: 生成PR文档
# 按照模板填写完整信息
```

#### **场景2: 修改现有接口**
```bash
# 步骤1: 详细了解当前实现
python3 extract_api_paths.py --detail <接口ID>

# 步骤2: 分析影响范围
python3 extract_api_paths.py --url --path '^/相关路径/'

# 步骤3: 修改和回归测试
# 修改代码 -> 重新上传 -> 批量测试相关接口
```

#### **场景3: 系统重构优化**
```bash
# 步骤1: 全量分析系统接口
python3 extract_api_paths.py --url > full_api_analysis.csv

# 步骤2: 识别优化机会
python3 extract_api_paths.py --url --method GET --query '重复|冗余'

# 步骤3: 制定重构计划
# 使用评审检查清单评估影响
```

### 💡 效率提升技巧

1. **工具组合使用**: `extract_api_paths.py` 用于分析，`magic_api_resource_manager.py` 用于管理
2. **命令别名设置**: 为常用命令创建别名，提高操作效率
3. **批量操作**: 使用工具的过滤功能批量处理相似任务
4. **文档同步**: 开发过程中同步更新相关文档
5. **测试先行**: 使用 `magic_api_client.py` 进行充分测试后再提交

### ⚠️ 常见陷阱避免

- ❌ **不要跳过研究阶段**: 未经分析就盲目开发
- ❌ **不要忽略现有代码**: 重复造轮子造成维护负担
- ❌ **不要缺少测试**: 未经验证的功能容易出问题
- ❌ **不要忘记文档**: 缺少文档的代码难以维护
- ❌ **不要违反规范**: 不符合规范的代码难以集成

## 🎉 总结

这是一份**企业级的 Magic-Script 开发指南**，不仅涵盖技术内容，更重要的是建立了标准化的开发流程和质量保障体系。

### 🏆 核心价值

#### **技术能力提升**
- ✅ **语言精通**: 从语法到高级特性，全面掌握 Magic-Script
- ✅ **架构理解**: 深入理解项目的技术架构和设计模式
- ✅ **工具运用**: 熟练使用专业的开发工具链
- ✅ **质量保障**: 编写安全、可维护、高性能的代码

#### **工程化能力提升**
- ✅ **流程标准化**: 遵循研究→构思→计划→执行→评审的标准化流程
- ✅ **文档规范化**: 使用标准化的PR文档和代码注释
- ✅ **测试完备性**: 建立完整的测试验证体系
- ✅ **协作高效性**: 团队协作的规范和最佳实践

#### **效率倍增**
- ✅ **工具赋能**: 通过 `extract_api_paths.py`、`magic_api_resource_manager.py`、`magic_api_client.py` 三驾马车
- ✅ **实时代码获取**: 优先使用工具从数据库获取最新代码，避免范文文件过期问题
- ✅ **流程优化**: 标准化的工作流减少决策时间
- ✅ **问题预防**: 通过评审检查清单提前发现风险
- ✅ **知识传承**: 完善的文档体系便于知识传递

### 🛠️ 智能工具链生态

| 工具角色 | 核心功能 | 使用场景 | 效率提升 |
|---------|---------|---------|---------|
| **extract_api_paths.py**<br/>📊 API分析专家 | 批量提取、过滤、详情查看、路径转ID | 需求分析、文档生成、接口研究 | 10x 分析效率 |
| **magic_api_resource_manager.py**<br/>🎯 资源管理专家 | 增删改查、树形显示、搜索过滤 | 开发调试、资源管理、结构探索 | 5x 管理效率 |
| **magic_api_client.py**<br/>🔧 测试验证专家 | WebSocket调试、API调用、日志监听 | 功能测试、性能验证、问题排查 | 3x 测试效率 |
| **magic_api_debug_client.py**<br/>🐛 断点调试专家 | 断点设置、单步执行、变量检查、异步调试 | 脚本调试、断点分析、变量状态检查 | 5x 调试效率 |

### 📈 成长路径图

```
新手入门 (1-2周)
    ↓
基础开发 (3-4周) → 高效开发秘籍 → 标准化工作流
    ↓
进阶实践 (5-8周) → 复杂功能开发 → 架构设计能力
    ↓
专家水平 (2-3个月) → 系统重构优化 → 技术领导力
```

### 🎯 成功指标

- **代码质量**: 通过所有评审检查点
- **交付效率**: 遵循标准化流程，减少返工
- **团队协作**: PR文档完善，知识共享充分
- **系统稳定性**: 充分测试，风险控制到位
- **技术成长**: 能够独立完成复杂功能开发

### 🚀 立即开始行动

1. **现在就开始**: 按照"第1周：环境熟悉"开始你的学习之旅
2. **使用工具获取代码**: 优先使用 `python3 extract_api_paths.py --detail <ID>` 获取数据库中的最新代码
3. **断点调试**: 使用 `python3 magic_api_debug_client.py` 进行实时断点调试和变量检查
4. **严格执行**: 使用"标准化开发工作流"指导你的每一个开发任务
5. **工具为王**: 熟练掌握四大工具，成为开发效率的倍增器
6. **质量第一**: 记住"常见陷阱避免"，防患于未然
7. **持续改进**: 每个项目结束后都回顾总结，提升自我

**你已经站在了专业开发的起点上。现在，迈出第一步，开始你的 Magic-Script 专家之旅吧！** 🚀

---

*这份指南不仅是一份技术文档，更是团队工程能力和开发文化的体现。通过标准化流程和专业工具链，我们正在构建一个高效、可靠、可持续发展的技术团队。*
