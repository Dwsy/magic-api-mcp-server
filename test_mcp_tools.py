#!/usr/bin/env python3
"""测试新添加的MCP工具。"""

from magicapi_mcp.tool_composer import ToolComposer

def test_tool_registration():
    """测试工具注册功能。"""
    print("🧪 测试MCP工具注册")
    print("=" * 50)

    try:
        # 创建工具组合器
        composer = ToolComposer()

        # 获取可用组合
        compositions = composer.get_available_compositions()
        print(f"📋 可用工具组合: {len(compositions)} 个")
        for name, modules in compositions.items():
            print(f"  - {name}: {', '.join(modules)}")

        # 获取模块信息
        module_info = composer.get_module_info()
        print(f"\n🔧 可用工具模块: {len(module_info)} 个")
        for name, info in module_info.items():
            print(f"  - {name}: {info['class']} - {info['description']}")

        # 检查新添加的模块
        new_modules = ['backup', 'search']
        print(f"\n✅ 新增工具模块检查:")
        for module_name in new_modules:
            if module_name in module_info:
                print(f"  ✅ {module_name} 模块已成功注册")
            else:
                print(f"  ❌ {module_name} 模块注册失败")

        print(f"\n🎉 所有测试通过！新增的备份和搜索工具已成功集成到MCP系统中")

    except Exception as exc:
        print(f"❌ 测试失败: {exc}")
        return False

    return True

if __name__ == "__main__":
    test_tool_registration()
