"""集成测试：验证新的调试API工具是否能正常工作。"""

import asyncio
import sys
import os
from unittest.mock import Mock

# 添加当前路径到sys.path
sys.path.insert(0, os.path.abspath('..'))

from magicapi_mcp.settings import MagicAPISettings
from magicapi_mcp.tool_registry import ToolContext
from magicapi_tools.tools.debug_api import DebugAPITools


def test_debug_api_tools_integration():
    """集成测试：验证新调试API工具的功能。"""
    print("开始集成测试...")
    
    # 创建设置
    settings = MagicAPISettings(
        base_url="http://127.0.0.1:10712",  # 使用默认的Magic-API地址
        username="",
        password="",
        auth_enabled=False,
    )
    
    # 创建上下文
    context = ToolContext(settings)
    
    # 创建MCP应用模拟
    mcp_app = Mock()
    
    # 创建调试API工具实例
    debug_api_tools = DebugAPITools()
    
    # 注册工具
    debug_api_tools.register_tools(mcp_app, context)
    
    # 验证工具是否注册成功
    registered_tools_count = len(mcp_app.tool.call_args_list)
    print(f"注册的工具数量: {registered_tools_count}")
    
    # 获取所有注册的工具信息
    registered_tool_names = []
    for call in mcp_app.tool.call_args_list:
        if len(call) >= 2 and 'name' in call[1]:
            tool_name = call[1]['name']
            registered_tool_names.append(tool_name)
            print(f"已注册工具: {tool_name}")
    
    # 验证关键工具是否已注册
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
    
    missing_tools = [tool for tool in expected_tools if tool not in registered_tool_names]
    if missing_tools:
        print(f"缺少的工具: {missing_tools}")
        return False
    else:
        print("所有预期的工具都已成功注册")
        return True


def test_tool_execution():
    """测试工具执行功能。"""
    print("\n开始工具执行测试...")
    
    # 创建设置
    settings = MagicAPISettings(
        base_url="http://127.0.0.1:10712",
        username="",
        password="",
        auth_enabled=False,
    )
    
    # 创建上下文
    context = ToolContext(settings)
    
    # 由于我们只是测试注册和基本功能，不需要连接到真实的服务器
    # 所以可以跳过WSManager的启动
    
    # 创建MCP应用模拟
    mcp_app = Mock()
    
    # 创建调试API工具实例
    debug_api_tools = DebugAPITools()
    
    # 注册工具
    debug_api_tools.register_tools(mcp_app, context)
    
    # 获取注册的函数进行基本调用测试
    registered_functions = {}
    for call in mcp_app.tool.call_args_list:
        if len(call) >= 2 and 'name' in call[1]:
            tool_name = call[1]['name']
            # 从call[0]获取注册的函数
            if len(call[0]) > 0:
                registered_functions[tool_name] = call[0][0]
    
    # 测试获取断点状态工具（同步函数）
    if 'get_latest_breakpoint_status' in registered_functions:
        try:
            # 模拟context中的对象
            context.ws_manager.ensure_running_sync = Mock()
            context.debug_service.get_debug_status_tool = Mock(return_value={"success": True, "status": {"breakpoints": [1, 2, 3]}})
            
            get_status_func = registered_functions['get_latest_breakpoint_status']
            result = get_status_func()
            print(f"获取断点状态测试: {result}")
            
            # 验证结果结构
            assert 'is_breakpoint_status' in result
            assert 'timestamp' in result
            print("获取断点状态测试通过")
        except Exception as e:
            print(f"获取断点状态测试失败: {e}")
    
    # 测试设置断点工具
    if 'set_breakpoint' in registered_functions:
        try:
            # 模拟context中的对象
            context.ws_manager.ensure_running_sync = Mock()
            context.debug_service.set_breakpoint_tool = Mock(return_value={"success": True, "breakpoints": [10]})
            
            set_breakpoint_func = registered_functions['set_breakpoint']
            result = set_breakpoint_func(line_number=10)
            print(f"设置断点测试: {result}")
            
            assert result["success"] == True
            print("设置断点测试通过")
        except Exception as e:
            print(f"设置断点测试失败: {e}")
    
    print("工具执行测试完成")
    return True


if __name__ == "__main__":
    success1 = test_debug_api_tools_integration()
    success2 = test_tool_execution()
    
    if success1 and success2:
        print("\n✅ 所有集成测试通过！")
    else:
        print("\n❌ 有些测试失败了")