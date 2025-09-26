"""测试断点调试API工具的功能。"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import sys
import os

# 添加当前路径到sys.path
sys.path.insert(0, os.path.abspath('..'))

from magicapi_mcp.settings import MagicAPISettings
from magicapi_mcp.tool_registry import ToolContext
from magicapi_tools.tools.debug_api import DebugAPITools


class TestDebugAPITools(unittest.TestCase):
    """测试断点调试API工具。"""

    def setUp(self):
        """设置测试环境。"""
        self.settings = MagicAPISettings(
            base_url="http://test-magic-api:8080",
            username="test_user",
            password="test_password",
            auth_enabled=True,
        )
        
        # 创建Mock对象来模拟FastMCP和ToolContext
        self.mcp_app = Mock()
        self.context = ToolContext(self.settings)
        
        # 替换真实的HTTP客户端和WS管理器为Mock对象
        self.context.http_client = Mock()
        self.context.ws_manager = Mock()
        self.context.debug_service = Mock()
        
        self.debug_api_tools = DebugAPITools()
        
    def test_register_tools(self):
        """测试工具注册。"""
        # 这个测试检查工具是否被正确注册
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 检查是否调用了mcp_app.tool方法来注册预期的工具
        self.assertTrue(len(self.mcp_app.tool.call_args_list) >= 8)  # 至少有8个工具被注册
        
        # 获取所有已注册的工具名称
        registered_tools = []
        for call in self.mcp_app.tool.call_args_list:
            if len(call[1]) > 0 and 'name' in call[1]:
                registered_tools.append(call[1]['name'])
        
        # 检查特定工具是否被注册
        expected_tools = [
            'call_magic_api_with_timeout',
            'get_latest_breakpoint_status',
            'resume_from_breakpoint',
            'step_over_breakpoint',
            'step_into_breakpoint',
            'step_out_breakpoint',
            'set_breakpoint',
            'remove_breakpoint',
            'list_breakpoints'
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, registered_tools, f"工具 {tool} 未被注册")


class AsyncMock(Mock):
    """异步Mock类。"""
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


if __name__ == '__main__':
    unittest.main()