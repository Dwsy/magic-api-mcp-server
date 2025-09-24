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
"""

from __future__ import annotations

from typing import Any, List, Optional

from magicapi_mcp.settings import MagicAPISettings
from magicapi_mcp.tool_composer import create_app as _create_app

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

# 创建全局mcp对象供fastmcp导入
# 注意：避免在模块级别重复创建app实例，交由调用方控制

if __name__ == "__main__":  # pragma: no cover - 运行服务器专用分支
    if FastMCP is None:
        raise SystemExit("未检测到 fastmcp，请先运行 `uv add fastmcp` 安装依赖。")
    app = create_app()
    app.run()
