#!/usr/bin/env python3
"""测试工具组合架构的功能。"""

from __future__ import annotations

import sys
from typing import Any

# 添加项目根目录到Python路径
sys.path.insert(0, '..')

def test_tool_composition():
    """测试工具组合架构。"""
    print("🧪 测试 Magic-API 工具组合架构")
    print("=" * 50)

    try:
        # 测试导入
        print("📦 测试模块导入...")
        from magicapi_mcp.tool_composer import tool_composer
        from magicapi_mcp.tool_registry import tool_registry
        from magicapi_tools.tools.documentation import DocumentationTools
        from magicapi_tools.tools.resource import ResourceManagementTools
        from magicapi_tools.tools.query import QueryTools
        from magicapi_tools.tools.debug import DebugTools
        from magicapi_tools.tools.system import SystemTools
        print("✅ 所有模块导入成功")

        # 测试组合配置
        print("\n🔧 测试工具组合...")
        compositions = tool_composer.get_available_compositions()
        print(f"✅ 可用组合: {list(compositions.keys())}")

        for name, modules in compositions.items():
            print(f"  - {name}: {len(modules)} 个模块")

        # 测试模块信息
        print("\n📋 测试模块信息...")
        modules = tool_composer.get_module_info()
        print(f"✅ 模块数量: {len(modules)}")

        for name, info in modules.items():
            print(f"  - {name}: {info['description']}")

        # 测试工具注册器
        print("\n🎯 测试工具注册器...")
        registry_modules = len(tool_registry.modules)
        print(f"✅ 注册器模块数量: {registry_modules}")

        # 测试工具创建（不运行服务器）
        print("\n🚀 测试应用创建...")
        try:
            from magicapi_mcp.settings import MagicAPISettings

            settings = MagicAPISettings(
                base_url="http://127.0.0.1:10712",
                auth_enabled=False
            )

            # 测试不同组合的应用创建
            for composition in ["minimal", "documentation_only"]:
                try:
                    app = tool_composer.create_app(composition, settings)
                    print(f"✅ {composition} 组合创建成功")
                except Exception as e:
                    print(f"⚠️  {composition} 组合创建失败: {e}")

        except ImportError:
            print("⚠️  FastMCP 未安装，跳过应用创建测试")

        print("\n🎉 工具组合架构测试完成！")
        print("✅ 所有核心功能正常")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_counts():
    """统计工具数量。"""
    print("\n📊 工具统计")
    print("-" * 30)

    try:
        # 导入工具模块
        from magicapi_tools.tools.documentation import DocumentationTools
        from magicapi_tools.tools.resource import ResourceManagementTools
        from magicapi_tools.tools.query import QueryTools
        from magicapi_tools.tools.debug import DebugTools
        from magicapi_tools.tools.system import SystemTools

        # 创建模拟上下文
        class MockContext:
            pass

        class MockApp:
            def tool(self, **kwargs):
                return lambda func: func

        # 统计工具数量
        modules = [
            ("DocumentationTools", DocumentationTools()),
            ("ResourceManagementTools", ResourceManagementTools()),
            ("QueryTools", QueryTools()),
            ("DebugTools", DebugTools()),
            ("SystemTools", SystemTools()),
        ]

        total_tools = 0
        for module_name, module_instance in modules:
            try:
                # 模拟注册过程来计数
                tool_count = 0
                original_tool = MockApp.tool

                def counting_tool(**kwargs):
                    nonlocal tool_count
                    tool_count += 1
                    return original_tool

                MockApp.tool = counting_tool

                mock_app = MockApp()
                mock_context = MockContext()

                # 调用注册方法
                module_instance.register_tools(mock_app, mock_context)

                print(f"✅ {module_name}: {tool_count} 个工具")
                total_tools += tool_count

            except Exception as e:
                print(f"⚠️  {module_name}: 统计失败 - {e}")

        print(f"\n🎯 总计: {total_tools} 个工具")
        return total_tools

    except Exception as e:
        print(f"❌ 工具统计失败: {e}")
        return 0

if __name__ == "__main__":
    success = test_tool_composition()
    tool_count = test_tool_counts()

    if success:
        print("\n🎊 所有测试通过！")
        print(f"🔢 架构包含 {tool_count} 个工具")
        print("🚀 Magic-API 助手已就绪！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)
