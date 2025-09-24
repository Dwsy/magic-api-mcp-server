# Magic-API 代码 AI 助手（FastMCP 实现）

基于 [FastMCP Quickstart](https://gofastmcp.com/getting-started/quickstart) 与 Magic-API 官方脚本文档（https://www.ssssssss.org/magic-api/pages/base/script/），在本仓库中落地一个面向 Magic-API 的代码 AI 助手。助手提供标准 MCP 工具，整合现有 Python 调试脚本，能够输出 Magic-Script 语法、示例、文档索引、最佳实践、常见坑点以及端到端工作流。

---

## 架构与运行

```mermaid
flowchart LR
  LLM <-->|MCP| FastMCPClient
  FastMCPClient <-->|stdio| MCPServer[magicapi_assistant]
  MCPServer --> Tools[工具: syntax / examples / docs / best_practices / pitfalls / workflow / resource_tree / path_to_id / path_detail / api_detail / call / meta]
  MCPServer --> Knowledge[知识库
  (mcp/knowledge_base.py)]
  MCPServer --> HTTPClient[HTTP 客户端
  (mcp/http_client.py)]
  HTTPClient --> MagicAPI[Magic-API 服务
  (HTTP + WebSocket)]
  HTTPClient --> LocalTools[Python 工具脚本
  extract_api_paths.py 等]
```

- **FastMCP 服务**：位于 `mcp/magicapi_assistant.py`，通过 `create_app()` 构建，默认 `stdio` 传输，可使用 `fastmcp run mcp/magicapi_assistant.py:mcp` 启动。
- **HTTP 客户端**：`mcp/http_client.py` 封装了登录、资源树、接口详情和 API 调用，继承现有工具的认证逻辑。
- **配置解析**：`mcp/config.py` 负责解析环境变量，默认匿名模式，可按需启用用户名/密码或 Token。
- **知识库**：`mcp/knowledge_base.py` 汇总 Magic-Script 语法、示例、最佳实践与踩坑项，全部数据经过官方文档核对。

## Python 模块整合

- 新增 `magicapi_tools` 包集中封装配置、HTTP 会话、资源提取及 WebSocket 调试逻辑。
- 所有 CLI 脚本复用该包，CLI 行为保持兼容，同时利于扩展与单元测试。
- MCP 服务直接依赖 `magicapi_tools`，避免重复实现认证、路径查询与调用封装。

---

## 依赖与安装

推荐使用 [uv](https://gofastmcp.com/getting-started/installation)：

```bash
# 在项目根目录
uv add fastmcp
uv pip install -r requirements.txt  # 或 uv sync
```

> FastMCP 未安装时，`create_app()` 会抛出提示性异常，提醒先执行 `uv add fastmcp`。

---

## 环境变量与认证策略

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MAGIC_API_BASE_URL` | `http://127.0.0.1:10712` | HTTP 接口根地址 |
| `MAGIC_API_WS_URL` | `ws://127.0.0.1:10712/magic/web/console` | WebSocket 控制台地址（暂保留浮动） |
| `MAGIC_API_USERNAME` / `MAGIC_API_PASSWORD` | 空 | 认证用户名与密码 |
| `MAGIC_API_TOKEN` | 空 | Header Token |
| `MAGIC_API_AUTH_ENABLED` | `false` | 是否启用认证（true/false/1/on） |
| `MAGIC_API_TIMEOUT_SECONDS` | `30` | HTTP 请求超时时间 |
| `LOG_LEVEL` | `INFO` | MCP 服务日志等级（预留） |
| `FASTMCP_TRANSPORT` | `stdio` | 可切换为 `http` 等 Transport |

- 当 `MAGIC_API_AUTH_ENABLED=true` 时，`MagicAPIHTTPClient` 会先调用 `/magic/web/login`，并在请求头中附带 Token/用户名信息。
- 所有 MCP 工具在调用外部脚本或 HTTP 接口前都会透传当前环境变量，保证与原有 CLI 行为一致。

---

## MCP 工具一览

服务注册的工具均在 `mcp/magicapi_assistant.py` 中声明：

| 工具 | 输入参数 | 返回结构 | 说明 |
| --- | --- | --- | --- |
| `syntax(topic, locale='zh-CN')` | `topic`：`keywords/operators/types/collections/db/response` | `{topic, title, summary, sections[], doc}` | 从知识库返回 Magic-Script 语法速查，覆盖可选链、事务、集合操作等重点。 |
| `examples(kind, keyword=None)` | `kind`：`basic/db/http` 等 | `{kind, examples[]}` | 返回场景化示例，支持关键字过滤。 |
| `docs(index_only=True)` | 布尔 | `{index, summary?}` | Magic-API 官方文档导航，含脚本语法与模块说明。 |
| `best_practices()` | 无 | `{items[]}` | SQL 注入防护、事务规范、响应统一等团队最佳实践。 |
| `pitfalls()` | 无 | `{items[]}` | 逻辑短路差异、`exit` 语义、时间戳转换等常见坑点。 |
| `workflow(task='create_api', with_commands=True)` | 任务类型 | `{task, description, steps[], commands?[]}` | 工作流中融入仓库 Python 脚本，默认返回命令清单。 |
| `resource_tree(kind='api', search=None, csv=False, depth=None)` | 类型、搜索词、深度、CSV 开关 | `{kind, count, nodes[], csv?}` | 调用资源树 API，返回结构化节点列表，可选 CSV 输出。 |
| `path_to_id(path, fuzzy=True)` | 接口路径 | `{path, matches[]}` 或错误 | 通过资源树查找接口 ID，支持模糊/精确匹配。 |
| `path_detail(path, fuzzy=True)` | 接口路径 | `{path, fuzzy, results[{meta, detail|error}]}` | 直接返回详情，等价于脚本 `--path-to-detail` 功能。 |
| `api_detail(file_id)` | 文件 ID | `{id, name, path, method, script, meta_raw}` | 包装 `/magic/web/resource/file/{id}`，返回完整脚本与元信息。 |
| `call(method, path, params=None, data=None, headers=None)` | HTTP 方法、路径及参数 | `{status, headers, body}` | 直接发起 Magic-API 调用，自动注入调用标识头。 |
| `meta()` | 无 | `{system_prompt, environment}` | 返回系统提示词与运行时环境信息，便于客户端调试。 |

错误统一返回 `{ "error": { code, message, detail? } }`，方便 LLM 进行容错处理。

---

## 系统提示词（System Prompt）

内置于 `mcp/knowledge_base.py` 的 `SYSTEM_PROMPT`：

```
你是 Magic-API 的代码 AI 助手。处理需求时务必：
1. 优先调用 path_detail（或 path_to_id → api_detail）获取最新脚本，避免使用过期范例；
2. SQL 参数必须使用 #{ } 占位，禁止 ${ } 字符串拼接；
3. 输出方案前同步最佳实践与潜在坑点，提醒事务、空数据、分页、时区风险；
4. 推荐配套 Python 工具命令，确保开发者可以落地执行。
```

当 FastMCP SDK 提供 `set_system_prompt` 接口时会自动写入；若没有，也可在客户端侧读取 `meta()` 手动设置。

---

## 与仓库 Python 工具的协同

MCP 工具默认输出可直接执行的命令，建议结合以下脚本完成端到端流程：

1. **资源初探**：`python3 magic_api_resource_manager.py --list-tree --depth 2`
2. **路径检索**：`python3 extract_api_paths.py --url --path-to-id '/订单/'`
3. **接口详情**：`python3 extract_api_paths.py --detail <接口ID>`
4. **调试调用**：`python3 magic_api_client.py --call 'POST /order/create' --data '{"id":1}'`
5. **断点分析**：`python3 magic_api_debug_client.py`

这些命令与 MCP `workflow()` 返回的步骤保持一致，可作为人机协作背书。

---

## 测试策略与验证命令

针对新增模块补充了轻量级单元测试：

- `test/test_magicapi_config.py`：验证环境变量解析与认证注入。
- `test/test_magicapi_utils.py`：覆盖知识库输出、节点过滤与 CSV 编码。

运行方式（避免触发旧测试的语法问题）：

```bash
python3 -m unittest discover -s test -p 'test_magicapi_*.py'
```

如需合并原有脚本测试，可逐个执行（例如 `python3 test_step_commands.py`）。

---

## 验收清单

- [x] FastMCP 服务代码：`mcp/magicapi_assistant.py`、`mcp/http_client.py`、`mcp/config.py`、`mcp/knowledge_base.py`
- [x] 依赖更新：`requirements.txt` 新增 `fastmcp`
- [x] 单元测试：`test/test_magicapi_config.py`、`test/test_magicapi_utils.py`
- [x] 文档（本文件）说明架构、配置、工具、提示词、测试与运行方式

完成上述步骤后，可使用 `fastmcp run mcp/magicapi_assistant.py:mcp` 启动服务，并在任意兼容 MCP 的客户端中体验 Magic-API 专用代码助手。
