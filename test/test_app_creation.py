"""验证FastMCP应用能否成功启动并包含新的调试API工具。"""

import sys
import os

# 添加当前路径到sys.path
sys.path.insert(0, os.path.abspath('..'))

from magicapi_mcp.tool_composer import create_app, get_composition_info


def test_app_creation_with_debug_api():
    """测试创建包含debug_api工具的FastMCP应用。"""
    print("测试创建包含debug_api工具的FastMCP应用...")
    
    # 测试创建完整工具集的应用
    try:
        app = create_app(composition="full")
        print("✅ 成功创建完整工具集的FastMCP应用")
    except Exception as e:
        print(f"❌ 创建完整工具集的FastMCP应用失败: {e}")
        return False
    
    # 测试创建调试专用工具集的应用
    try:
        app = create_app(composition="debugging")
        print("✅ 成功创建调试专用工具集的FastMCP应用")
    except Exception as e:
        print(f"❌ 创建调试专用工具集的FastMCP应用失败: {e}")
        return False
    
    # 验证组合信息中包含debug_api
    composition_info = get_composition_info("debugging")
    if "debug_api" in composition_info.get("tools", []):
        print("✅ 调试组合中包含debug_api工具")
    else:
        print("❌ 调试组合中未包含debug_api工具")
        return False
    
    # 验证完整组合中也包含debug_api
    full_composition_info = get_composition_info("full")
    if "debug_api" in full_composition_info.get("tools", []):
        print("✅ 完整组合中包含debug_api工具")
    else:
        print("❌ 完整组合中未包含debug_api工具")
        return False
    
    return True


if __name__ == "__main__":
    success = test_app_creation_with_debug_api()
    
    if success:
        print("\n✅ FastMCP应用创建测试通过！新工具已成功集成。")
    else:
        print("\n❌ FastMCP应用创建测试失败。")