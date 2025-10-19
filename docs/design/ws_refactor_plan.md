# WebSocket 子系统重构设计稿

> 目标：为 MCP 与 CLI 提供统一的 WebSocket 能力，支撑环境感知、日志捕获、调试联动与进度反馈。

## 背景动因
- 现有 `magicapi_tools/utils/ws.py` 与 `magic_api_debug_client.py` 逻辑重复、状态分散，难以扩展。
- 新需求要求：
  - 以登录 IP 聚合 `client_id`，构建 IDE 环境视图。
  - 追踪 `SET_FILE_ID` 消息，关联已加载的资源树信息，提供上下文。
  - 在 MCP 工具中输出 Server Logging / Progress，并允许手动查询实时日志。
  - `call_magic_api` 默认附带调用前后 0.1 秒的 WebSocket 日志。
- 需要逐步替换旧实现，保持兼容现有工具与测试。

## 模块结构（新建 `magicapi_tools/ws/`）
```
magicapi_tools/ws/
├── __init__.py
├── client.py      # 底层 WebSocket 客户端：连接、心跳、发送
├── messages.py    # 消息枚举 + 数据结构 + 解析/构建工具
├── state.py       # IDE 环境、资源上下文、日志缓冲
├── manager.py     # 对外统一接口，协调 client / state / observer
├── observers.py   # Observer 抽象与 MCP、CLI 实现
└── utils.py       # 公共工具（时间、重试、节流等）
```

## 核心组件设计
### 1. 消息模型 (`messages.py`)
- 定义 `MessageType` 枚举覆盖：`LOG`、`LOGS`、`LOGIN_RESPONSE`、`USER_LOGIN`、`USER_LOGOUT`、`PING`、`SET_FILE_ID`、`INTO_FILE_ID`、`BREAKPOINT`、`EXCEPTION` 等。
- `WSMessage` 数据类：包含 `type`、`raw`、`payload`、`timestamp`。
- `parse_raw(message: str) -> WSMessage`：
  - 自动识别 JSON 载荷。
  - 对 `LOGS`、`BREAKPOINT` 等特殊格式进行结构化解析。
  - 捕获解析异常并保留原始文本。

### 2. WebSocket 客户端 (`client.py`)
- 负责：
  - 建立连接、自动重连、发送 `login` / `ping` / 命令。
  - 暴露 `async def message_stream()` 生成器供 `manager` 消费。
  - `client_id` 生成策略沿用 16 位小写十六进制（兼容现有测试）。
- 支持外部注入 HTTP Session / 认证头，便于在断点命令时共享配置。

### 3. 环境状态 (`state.py`)
- `IDEEnvironment`：
  - `ide_key`（默认使用 `login_ip`，若缺失降级为 `client_id`）。
  - `client_ids`：同一 IP 对应的所有 `client_id`，标记是否由本 MCP 创建。
  - `latest_user`：记录登录用户信息（昵称、IP、角色等）。
  - `opened_files: Dict[str, OpenFileContext]`。
  - `last_active_at`：最近消息时间。
- `OpenFileContext`：包含 `file_id`、`method`、`path`、`name`、`group_chain`、`detail`（延迟加载）。
- `EnvironmentState` 职责：
  - 处理 `LOGIN_RESPONSE`/`USER_LOGIN`/`USER_LOGOUT` 更新。
  - 处理 `SET_FILE_ID`/`INTO_FILE_ID`，调用 `ResourceResolver` 获取资源基础信息。
  - 将 `LogBuffer` 与环境绑定，保留最近 N 条消息（默认 500）。
  - 提供查询接口 `list_environments()`、`get_environment(ide_key)`。

### 4. 资源解析 (`state.py` or `utils.py`)
- `ResourceResolver`：
  - 首次调用批量加载资源树 `MagicAPIResourceManager.get_resource_tree()`，缓存并定时刷新。
  - 提供 `resolve_file(file_id)` 返回基础信息；若资源树缺失则回退到 `get_file_detail()`。
  - 支持结合 `method/path` 生成完整显示路径。

### 5. 日志缓冲 (`state.py`)
- `LogBuffer`：使用 `collections.deque`，保存 `(timestamp, WSMessage)`。
- `slice_window(center, pre=0.1, post=0.1)` 获取时间窗数据，供 `call_magic_api` 或工具查询。
- 支持按条数或时间范围截取。

### 6. 管理器 (`manager.py`)
- 对外暴露：
  - `async start()` / `async stop()`。
  - `async ensure_running()`：按需启动后台监听任务。
  - `get_environments()`、`get_recent_logs(window)`、`capture_logs_around(ts, pre, post)`。
  - 调试命令封装（resume/step/set_breakpoint）。
- 内部流程：
  1. 从 `WSClient.message_stream()` 接收消息。
  2. 写入 `LogBuffer`。
  3. 调用 `EnvironmentState.handle_message()` 更新状态。
  4. 广播给注册的 Observer（例如 CLI 输出、MCP 进度）。

### 7. 观察者 (`observers.py`)
- `BaseObserver`: 定义 `on_message`, `on_environment_update`, `on_error` 等钩子。
- `MCPObserver`：注入 `fastmcp.Context`，使用 `ctx.debug/info/error` 发送结构化日志；长操作时调用 `ctx.report_progress`。
- `CLIObserver`：复用现有打印逻辑，支持可选彩色输出；确保原 CLI 行为兼容。

## 工具层改造
- `magicapi_mcp/tool_registry.ToolContext` 持有单例 `WSManager` 与 `ResourceResolver`。
- `DebugTools` 调整：复用 `WSManager` 执行断点命令，读取状态。
- 新增 MCP 工具：
  1. `list_ws_environments`：返回聚合后的 IDE 环境（含当前文件、最后活动时间等）。
  2. `get_ws_recent_logs`：按时间窗口/数量返回日志记录。
  3. `get_ws_environment_detail`：详细展示指定 IDE 环境及打开文件上下文。
- `call_magic_api` 增加参数 `include_ws_logs: bool = True`，调用成功后附带 `ws_logs` 字段；若日志为空返回空数组。

## MCP 日志与进度策略
- 关键事件：
  - 首次启动 WebSocket -> `ctx.info("🔌 正在建立 WebSocket 连接")`。
  - 资源树加载 -> `ctx.report_progress(progress=20, total=100)`。
  - 收到 `BREAKPOINT` -> `ctx.warning(..., extra={"ide_key": ..., "file": ...})`。
  - 异常消息 -> `ctx.error(..., extra={"message_type": "EXCEPTION"})`。
- 工具执行期间，如需等待 WebSocket 返回结果，使用进度条标记等待状态。

## 配置扩展
- `MagicAPISettings` 新增字段（并提供默认值）：
  - `ws_auto_start: bool = True`
  - `ws_log_history_size: int = 500`
  - `ws_log_capture_window: float = 0.1`
  - `ws_reconnect_interval: float = 5.0`
- 在 `.env` / 环境变量中提供同名配置。

## 迁移步骤
1. **阶段1（当前阶段）**：搭建目录与骨架，迁移消息解析与基础客户端，不改动功能。完成后运行现有相关测试（例如 `uv run python test/test_client_id_generation.py` 使用 mock websockets）。
2. **阶段2**：实现 `EnvironmentState` + 资源解析 + 新工具 `list_ws_environments`，并补充对应单测。
3. **阶段3**：日志缓冲与 `call_magic_api` 集成，新增工具 `get_ws_recent_logs`，完善单测。
4. **阶段4**：MCP 观察者、文档更新、回归测试（含现有 `test/test_websocket_performance.py`、`test/test_async_http_fix.py` 等）。

## 测试计划
- 新增 `tests/ws/`：
  - `test_messages.py`：覆盖消息解析成功与兜底逻辑。
  - `test_environment_state.py`：模拟登录/文件切换流程。
  - `test_log_buffer.py`：验证时间窗口截取。
- 调整现有测试以调用新接口：
  - `test/test_client_id_generation.py`、`test/test_websocket_performance.py` 等。
- 每阶段结束使用 `uv run` 执行对应测试套件，确保增量变更可验证。

## 风险与缓解
- **连接管理复杂度**：通过 `WSManager` 统一管理单例连接；在 ToolContext 中延迟初始化。
- **资源树尺寸大**：引入缓存与按需明细查询，避免频繁全量加载。
- **兼容性**：阶段性迁移，保留旧接口直到新模块完全稳定；提供适配层。
- **测试依赖网络**：必要时通过 mock 或离线样本替代，确保 CI 无需真实服务。

---
该设计稿将在实现过程中同步修订，确保重构过程具备可追踪的愿景与落地步骤。
