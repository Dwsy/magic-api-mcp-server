"""测试断点调试API工具的功能。"""

import asyncio
import time
import unittest
from unittest.mock import Mock, patch, MagicMock

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
        
        # 检查特定工具是否被注册
        tool_names = [call[1]['name'] for call in self.mcp_app.tool.call_args_list]
        self.assertIn('call_magic_api_with_timeout', tool_names)
        self.assertIn('get_latest_breakpoint_status', tool_names)
        self.assertIn('resume_from_breakpoint', tool_names)
        self.assertIn('step_over_breakpoint', tool_names)
        self.assertIn('step_into_breakpoint', tool_names)
        self.assertIn('step_out_breakpoint', tool_names)
        self.assertIn('set_breakpoint', tool_names)
        self.assertIn('remove_breakpoint', tool_names)
        self.assertIn('list_breakpoints', tool_names)

    @patch('magicapi_tools.tools.debug_api.ThreadPoolExecutor')
    def test_call_with_timeout_immediate_response(self, mock_executor):
        """测试带超时的API调用（立即响应）。"""
        # Mock executor和future
        mock_future = Mock()
        mock_future.result.return_value = {"success": True, "response": {"data": "test"}}
        mock_executor_instance = Mock()
        mock_executor_instance.submit.return_value = mock_future
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 获取注册的函数
        registered_func = [
            call[0][1] for call in self.mcp_app.tool.call_args_list
            if call[1]['name'] == 'call_magic_api_with_timeout'
        ][0]
        
        # 调用注册的函数
        result = registered_func(
            method="GET",
            path="/test/api",
            timeout=2.0
        )
        
        # 验证结果
        self.assertEqual(result["success"], True)
        self.assertEqual(result["response"]["data"], "test")

    @patch('magicapi_tools.tools.debug_api.ThreadPoolExecutor')
    def test_call_with_timeout_timeout_response(self, mock_executor):
        """测试带超时的API调用（超时响应）。"""
        # Mock executor和future，模拟TimeoutError
        mock_future = Mock()
        mock_future.result.side_effect = TimeoutError()
        mock_executor_instance = Mock()
        mock_executor_instance.submit.return_value = mock_future
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 获取注册的函数
        registered_func = [
            call[0][1] for call in self.mcp_app.tool.call_args_list
            if call[1]['name'] == 'call_magic_api_with_timeout'
        ][0]
        
        # 调用注册的函数
        result = registered_func(
            method="GET",
            path="/test/api",
            timeout=0.1
        )
        
        # 验证结果是超时响应
        self.assertIn("message", result)
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["expected_next_action"], "get_latest_breakpoint_status")

    def test_get_breakpoint_status(self):
        """测试获取断点状态。"""
        # Mock调试服务
        mock_debug_service = Mock()
        mock_debug_service.get_debug_status_tool.return_value = {
            "success": True,
            "status": {"breakpoints": [1, 2, 3]}
        }
        self.context.debug_service = mock_debug_service
        
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 获取注册的函数
        registered_func = [
            call[0][1] for call in self.mcp_app.tool.call_args_list
            if call[1]['name'] == 'get_latest_breakpoint_status'
        ][0]
        
        # 调用注册的函数
        result = registered_func()
        
        # 验证结果
        self.assertEqual(result["success"], True)
        self.assertEqual(result["status"]["breakpoints"], [1, 2, 3])
        self.assertTrue(result["is_breakpoint_status"])

    def test_resume_from_breakpoint(self):
        """测试恢复断点执行。"""
        # Mock调试服务
        mock_debug_service = Mock()
        mock_debug_service.resume_breakpoint_tool = AsyncMock(return_value={"success": True, "script_id": "test-script", "step": 0})
        self.context.debug_service = mock_debug_service
        
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 获取注册的函数
        registered_func = [
            call[0][1] for call in self.mcp_app.tool.call_args_list
            if call[1]['name'] == 'resume_from_breakpoint'
        ][0]
        
        # 调用注册的函数
        result = asyncio.run(registered_func())
        
        # 验证结果
        self.assertEqual(result["success"], True)
        self.assertEqual(result["script_id"], "test-script")

    def test_step_over_breakpoint(self):
        """测试单步跳过断点。"""
        # Mock调试服务
        mock_debug_service = Mock()
        mock_debug_service.step_over_tool = AsyncMock(return_value={"success": True, "script_id": "test-script", "step": 1})
        self.context.debug_service = mock_debug_service
        
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 获取注册的函数
        registered_func = [
            call[0][1] for call in self.mcp_app.tool.call_args_list
            if call[1]['name'] == 'step_over_breakpoint'
        ][0]
        
        # 调用注册的函数
        result = asyncio.run(registered_func())
        
        # 验证结果
        self.assertEqual(result["success"], True)
        self.assertEqual(result["script_id"], "test-script")

    def test_set_breakpoint(self):
        """测试设置断点。"""
        # Mock调试服务
        mock_debug_service = Mock()
        mock_debug_service.set_breakpoint_tool.return_value = {"success": True, "breakpoints": [10]}
        self.context.debug_service = mock_debug_service
        
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 获取注册的函数
        registered_func = [
            call[0][1] for call in self.mcp_app.tool.call_args_list
            if call[1]['name'] == 'set_breakpoint'
        ][0]
        
        # 调用注册的函数
        result = registered_func(line_number=10)
        
        # 验证结果
        self.assertEqual(result["success"], True)
        self.assertEqual(result["breakpoints"], [10])

    def test_remove_breakpoint(self):
        """测试移除断点。"""
        # Mock调试服务
        mock_debug_service = Mock()
        mock_debug_service.remove_breakpoint_tool.return_value = {"success": True, "breakpoints": []}
        self.context.debug_service = mock_debug_service
        
        self.debug_api_tools.register_tools(self.mcp_app, self.context)
        
        # 获取注册的函数
        registered_func = [
            call[0][1] for call in self.mcp_app.tool.call_args_list
            if call[1]['name'] == 'remove_breakpoint'
        ][0]
        
        # 调用注册的函数
        result = registered_func(line_number=10)
        
        # 验证结果
        self.assertEqual(result["success"], True)
        self.assertEqual(result["breakpoints"], [])


# 为异步方法创建Mock
class AsyncMock(Mock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


if __name__ == '__main__':
    unittest.main()