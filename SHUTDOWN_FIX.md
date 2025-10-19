# MCP 服务器优雅关闭修复说明

## 问题描述

原始的 `run_mcp.py` 脚本在使用 `Ctrl+C` (SIGINT) 终止时存在问题，会出现以下错误：

```
Fatal Python error: _enter_buffered_busy: could not acquire lock for <_io.BufferedReader name='<stdin>'> at interpreter shutdown, possibly due to daemon threads
```

## 问题原因

该问题发生是因为：

1. FastMCP 服务器创建了 WebSocket 客户端连接，使用了后台线程来处理 WebSocket 通信
2. 当用户按下 `Ctrl+C` 时，Python 解释器尝试关闭，但后台线程仍然在运行
3. 这些后台线程（特别是 WebSocket 管理器的事件循环线程）没有被正确清理
4. 导致在程序退出时出现资源竞争和锁获取失败

## 解决方案

修复方案包括以下改进：

### 1. 信号处理

在 `run_mcp.py` 中添加了信号处理函数，用于捕获 `SIGINT` 和 `SIGTERM` 信号：

```python
def signal_handler(sig, frame):
    """处理 Ctrl+C 信号，确保优雅关闭"""
    print('\n正在关闭服务器...')
    _cleanup_resources()
    print('服务器已关闭')
    sys.exit(0)

def setup_signal_handlers():
    """设置信号处理器以确保优雅关闭"""
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination
```

### 2. 资源清理

添加了专门的清理函数来关闭 WebSocket 管理器和相关资源：

```python
def _cleanup_resources():
    """清理资源，特别是 WebSocket 管理器"""
    from magicapi_mcp.tool_registry import tool_registry
    
    if tool_registry.context:
        # 获取并关闭 WebSocket 管理器
        try:
            ws_manager = tool_registry.context.ws_manager
            if ws_manager and hasattr(ws_manager, 'stop_sync'):
                ws_manager.stop_sync()
                print('WebSocket 管理器已关闭')
        except Exception as e:
            print(f'关闭 WebSocket 管理器时出错: {e}')
        
        # 清理资源管理器
        try:
            resource_manager = tool_registry.context.resource_manager
            if resource_manager and hasattr(resource_manager, 'close'):
                resource_manager.close()
        except Exception as e:
            print(f'关闭资源管理器时出错: {e}')
```

### 3. 退出钩子

使用 `atexit` 模块注册退出时的清理函数：

```python
import atexit

if __name__ == '__main__':
    # 设置信号处理器
    setup_signal_handlers()
    
    # 注册退出时的清理函数
    atexit.register(cleanup_on_exit)
```

## 使用方法

现在可以正常使用以下命令启动服务器：

```bash
uv run fastmcp run run_mcp.py:mcp
```

要关闭服务器时，使用 `Ctrl+C`，服务器将：

1. 接收信号
2. 执行清理程序
3. 关闭 WebSocket 连接
4. 正常退出

## 注意事项

- 修复后的代码同时添加到了 `magicapi_mcp/magicapi_assistant.py` 文件中，这样无论是通过 `uv run fastmcp run run_mcp.py:mcp` 还是直接运行 `python run_mcp.py` 都能正确处理退出
- 所有的资源清理操作都使用了 try-catch 包装，以防止清理过程中出现异常影响正常退出
- WebSocket 管理器的 `stop_sync()` 方法会同步地停止后台任务，确保所有线程安全关闭