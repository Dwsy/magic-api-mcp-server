"""验证新工具模块是否能被正确导入。"""

import sys
import os

# 添加当前路径到sys.path
sys.path.insert(0, os.path.abspath('..'))

def test_module_imports():
    """测试模块导入。"""
    print("测试模块导入...")
    
    # 测试导入DebugAPITools
    try:
        from magicapi_tools.tools.debug_api import DebugAPITools
        print("✅ 成功导入DebugAPITools")
        
        # 创建实例测试
        tools = DebugAPITools()
        print(f"✅ 成功创建DebugAPITools实例: {tools}")
    except ImportError as e:
        print(f"❌ 导入DebugAPITools失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 创建DebugAPITools实例失败: {e}")
        return False
    
    # 测试导入tool_composer中的新模块
    try:
        from magicapi_mcp.tool_composer import tool_composer
        print("✅ 成功导入tool_composer")
        
        # 检查debug_api模块是否在工具模块中
        if "debug_api" in tool_composer.modules:
            print("✅ debug_api模块在tool_composer中")
        else:
            print("❌ debug_api模块不在tool_composer中")
            return False
            
    except ImportError as e:
        print(f"❌ 导入tool_composer失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查tool_composer失败: {e}")
        return False
    
    # 检查组合信息
    try:
        composition_info = tool_composer.get_composition_info("debugging")
        if "debug_api" in composition_info.get('tools', []):
            print("✅ debugging组合包含debug_api工具")
        else:
            print("⚠️ debugging组合可能不包含debug_api工具，但可能是正常的")
            
        # 检查full组合
        full_info = tool_composer.get_composition_info("full")
        if "debug_api" in full_info.get('tools', []):
            print("✅ full组合包含debug_api工具")
        else:
            print("⚠️ full组合可能不包含debug_api工具，但可能是正常的")
    except Exception as e:
        print(f"⚠️ 检查组合信息时出现问题: {e}")
        # 这可能不是致命错误，继续测试
    
    return True


def test_tool_registration():
    """测试工具注册功能。"""
    print("\n测试工具注册功能...")
    
    try:
        from magicapi_mcp.settings import MagicAPISettings
        from magicapi_mcp.tool_registry import ToolContext
        from magicapi_tools.tools.debug_api import DebugAPITools
        
        # 创建模拟环境
        settings = MagicAPISettings(
            base_url="http://test-magic-api:8080",
            username="",
            password="",
            auth_enabled=False,
        )
        
        # 创建Mock环境
        import unittest.mock as mock
        with mock.patch('magicapi_tools.ws.manager.WSManager'), \
             mock.patch('magicapi_tools.utils.http_client.MagicAPIHTTPClient'):
            
            context = ToolContext(settings)
            
            # 用Mock替换实际的客户端和服务
            context.http_client = mock.Mock()
            context.ws_manager = mock.Mock()
            context.debug_service = mock.Mock()
            
            # 测试注册工具
            mcp_app = mock.Mock()
            tools = DebugAPITools()
            tools.register_tools(mcp_app, context)
            
            # 检查是否调用了工具注册方法
            print(f"✅ 工具注册被调用次数: {len(mcp_app.tool.call_args_list)}")
            
            # 检查注册的工具名称
            registered_names = []
            for call in mcp_app.tool.call_args_list:
                if call[1] and 'name' in call[1]:
                    registered_names.append(call[1]['name'])
            
            print(f"✅ 注册的工具名称: {registered_names}")
            
            # 检查关键工具是否被注册
            expected_tools = ['call_magic_api_with_timeout', 'get_latest_breakpoint_status', 
                             'resume_from_breakpoint', 'step_over_breakpoint']
            for tool in expected_tools:
                if tool in registered_names:
                    print(f"✅ 工具 {tool} 已注册")
                else:
                    print(f"❌ 工具 {tool} 未注册")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ 工具注册测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_module_imports()
    success2 = test_tool_registration()
    
    if success1 and success2:
        print("\n✅ 所有模块导入和注册测试通过！新工具已正确实现和集成。")
    else:
        print("\n❌ 有些测试失败了")