"""FastMCP 版 Magic-API 代码助手。

此模块现在使用工具组合器架构，提供模块化和可组合的工具系统。

支持多种工具组合:
- full: 完整工具集 (默认)
- minimal: 最小工具集
- development: 开发工具集
- production: 生产工具集
- documentation_only: 仅文档工具

使用示例:
    from magicapi_mcp import create_app

    # 创建完整工具集应用
    app = create_app("full")

    # 创建仅文档工具应用
    doc_app = create_app("documentation_only")

    # 运行应用
    app.run()

命令行使用示例:
    # 运行完整工具集
    uvx magic-api-mcp

    # 运行特定工具组合
    uvx magic-api-mcp --composition development

    # 指定传输协议
    uvx magic-api-mcp --transport http --port 8000
"""

from __future__ import annotations

import argparse
import sys
import signal
import atexit
from typing import Any, List, Optional

from magicapi_mcp.settings import MagicAPISettings
from magicapi_mcp.tool_composer import create_app as _create_app
from magicapi_mcp.tool_registry import tool_registry

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

def create_app(
    composition: str = "full",
    settings: Optional[MagicAPISettings] = None,
    custom_modules: Optional[List[Any]] = None
) -> "FastMCP":
    """创建并配置 FastMCP 应用。

    Args:
        composition: 工具组合名称 ("full", "minimal", "development", "production", "documentation_only")
        settings: 应用设置
        custom_modules: 自定义工具模块列表

    Returns:
        配置好的FastMCP应用实例

    Raises:
        RuntimeError: 当FastMCP依赖未安装时抛出
    """
    return _create_app(composition, settings, custom_modules)

def _cleanup_resources():
    """清理资源，特别是 WebSocket 管理器"""
    # 获取工具注册器中的上下文
    if tool_registry.context:
        # 获取并关闭 WebSocket 管理器
        try:
            ws_manager = tool_registry.context.ws_manager
            if ws_manager and hasattr(ws_manager, 'stop_sync'):
                ws_manager.stop_sync()
                print("WebSocket 管理器已关闭")
        except Exception as e:
            print(f"关闭 WebSocket 管理器时出错: {e}")
        
        # 清理资源管理器
        try:
            resource_manager = tool_registry.context.resource_manager
            if resource_manager and hasattr(resource_manager, 'close'):
                resource_manager.close()
        except Exception as e:
            print(f"关闭资源管理器时出错: {e}")

def signal_handler(sig, frame):
    """处理 Ctrl+C 信号，确保优雅关闭"""
    print('\\n正在关闭服务器...')
    _cleanup_resources()
    print("服务器已关闭")
    sys.exit(0)

def setup_signal_handlers():
    """设置信号处理器以确保优雅关闭"""
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination

# 注册退出时的清理函数
def cleanup_on_exit():
    """程序退出时的清理函数"""
    _cleanup_resources()

def main() -> None:
    """命令行入口点函数，用于pip安装后的命令行调用。"""
    if FastMCP is None:
        raise SystemExit("未检测到 fastmcp，请先运行 `uv add fastmcp` 安装依赖。")

    # 设置信号处理器
    setup_signal_handlers()
    
    # 注册退出时的清理函数
    atexit.register(cleanup_on_exit)

    parser = argparse.ArgumentParser(
        description="Magic-API MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  uvx magic-api-mcp-server                           # 运行完整工具集
  uvx magic-api-mcp-server --composition development  # 运行开发工具集
  uvx magic-api-mcp-server --transport http --port 8000  # HTTP模式运行
        """
    )

    parser.add_argument(
        "--composition",
        choices=["full", "minimal", "development", "production", "documentation_only", "api_only", "backup_only", "class_method_only", "search_only"],
        default="full",
        help="选择工具组合 (默认: full)"
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="传输协议 (默认: stdio)"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP服务器主机地址 (默认: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP服务器端口 (默认: 8000)"
    )

    args = parser.parse_args()

    app = create_app(args.composition)

    try:
        if args.transport == "http":
            app.run(transport="http", host=args.host, port=args.port)
        else:
            app.run(transport="stdio")
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"服务器运行出错: {e}")
        _cleanup_resources()
        sys.exit(1)


# 创建全局mcp对象供fastmcp导入
# 注意：避免在模块级别重复创建app实例，交由调用方控制

if __name__ == "__main__":  # pragma: no cover - 运行服务器专用分支
    main()
