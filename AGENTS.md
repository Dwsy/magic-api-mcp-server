# Repository Guidelines

## 项目结构与模块组织
- `extract_api_paths.py`：从 Magic-API 数据源抽取端点并导出 CSV，支持关键词与方法过滤。
- `magic_api_client.py` 与 `magic_api_debug_client.py`：WebSocket 调试核心，负责日志监听、断点控制和命令执行。
- `magic_api_resource_manager.py`：封装资源同步逻辑，供代理脚本复用。
- `mcp/`：多代理实验脚本与配置，保持独立命名空间便于扩展。
- `magicapi_mcp/tools/api_tools.py`：API执行工具模块，包含 `call_magic_api` 工具用于调用接口。
- `magicapi_mcp/tools/query_tools.py`：查询工具模块，包含搜索和过滤API端点的功能。
- `test/` 目录及根目录 `test_*.py`：脚本化回归用例，覆盖消息过滤、断点、异步网络修复、API搜索等场景。

## 构建、测试与开发命令
- 安装依赖：`pip install -r requirements.txt`，确保 requests 与 websockets 版本一致。
- 提取接口：`python3 extract_api_paths.py --url http://127.0.0.1:10712/magic/web/resource --query 关键词`。
- 调试调用：`python3 magic_api_client.py --call 'GET /demo' --params 'k=v' --listen-only`。
- API搜索测试：`python3 test/test_search_api_endpoints.py`，验证API端点搜索和过滤功能。
- 异步回归：`python3 test_async_http_fix.py`，验证 HTTP 调用不阻塞 WebSocket。
- 批量检查：`find test -name 'test_*.py' -exec python3 {} +`，快速执行脚本式测试矩阵。

## 编码风格与命名约定
- Python 保持 4 空格缩进与模块级 docstring，函数名、变量名统一 snake_case。
- 文件命名体现职责，例如 `magic_api_*` 前缀标识客户端相关逻辑。
- CLI 提示与日志沿用现有 emoji+中文文案，突出执行阶段与异常类型。
- 新增第三方依赖需同步更新 `requirements.txt` 并写明用途注释。

## 测试准则
- 每项修复至少补充一个可复现脚本，命名为 `test_描述.py` 并放在 `test/`。
- 异步流程需覆盖事件循环内外两种调用，可参考 `test_async_http_fix.py` 的结构。
- 涉及远程 HTTP 的用例请提供 Mock、替代 URL 或说明本地模拟步骤，避免 CI 网络依赖。
- 调试客户端改动要验证断点、消息过滤、认证登录三类关键路径。

## 提交与合并请求指南
- 建议提交信息采用 `type(scope): summary`，常见 type 包括 `feat`、`fix`、`refactor`、`test`。
- 推送前运行相关测试脚本并清理临时日志，保持工作树干净。
- PR 描述需说明背景、实现要点与验证方式，并附命令输出或截图证明关键行为。
- 若改动影响接口或配置，列出回滚策略与默认值，协助评审快速评估风险。
