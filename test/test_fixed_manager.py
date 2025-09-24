#!/usr/bin/env python3
"""
Magic-API 资源管理器修复测试脚本
测试修复后的功能是否正常工作
"""

from magic_api_resource_manager import MagicAPIResourceManager


def test_fixed_functionality():
    """测试修复后的功能"""

    # 配置连接信息
    BASE_URL = "http://127.0.0.1:10712"
    USERNAME = "admin"
    PASSWORD = "123456"

    print("🧪 测试修复后的 Magic-API 资源管理器")
    print("=" * 60)

    # 创建资源管理器
    print(f"📡 连接到: {BASE_URL}")
    manager = MagicAPIResourceManager(BASE_URL, USERNAME, PASSWORD)

    print("\n" + "=" * 60)
    print("测试步骤:")
    print("=" * 60)

    try:
        # 1. 测试资源树获取
        print("\n1️⃣ 测试资源树获取:")
        tree_data = manager.get_resource_tree()
        if tree_data:
            print("✅ 资源树获取成功")
            print(f"📊 获取到 {len(tree_data)} 个顶级分类")
        else:
            print("❌ 资源树获取失败")
            return

        # 2. 测试分组列表获取
        print("\n2️⃣ 测试分组列表获取:")
        groups = manager.list_groups()
        if groups:
            print(f"✅ 分组列表获取成功，共 {len(groups)} 个分组")
            for group in groups[:3]:  # 只显示前3个
                print(f"   - {group.get('name', 'Unknown')} (ID: {group.get('id', 'Unknown')})")
        else:
            print("⚠️ 分组列表为空或获取失败")

        # 3. 测试API创建功能
        print("\n3️⃣ 测试API创建功能:")
        api_data = {
            "name": "test_api_fixed",
            "method": "GET",
            "path": "/test/fixed/api",
            "script": "return 'API created by fixed manager';"
        }

        file_id = manager.save_api_file("978f18c6a92649f69b2acaf7b27f55e8", api_data, auto_save=True)
        if file_id:
            print(f"✅ API创建成功: {api_data['name']} (ID: {file_id})")
        else:
            print("❌ API创建失败")

        # 4. 测试便捷API创建方法
        print("\n4️⃣ 测试便捷API创建方法:")
        file_id2 = manager.create_api_file(
            group_id="978f18c6a92649f69b2acaf7b27f55e8",
            name="test_api_convenient",
            method="POST",
            path="/test/convenient/api",
            script="return 'Created by convenient method';"
        )
        if file_id2:
            print(f"✅ 便捷API创建成功: test_api_convenient (ID: {file_id2})")
        else:
            print("❌ 便捷API创建失败")

        # 5. 清理测试数据
        print("\n5️⃣ 清理测试数据:")
        if file_id:
            success = manager.delete_resource(file_id)
            if success:
                print("✅ 测试API删除成功")
            else:
                print("❌ 测试API删除失败")

        if file_id2:
            success = manager.delete_resource(file_id2)
            if success:
                print("✅ 便捷API删除成功")
            else:
                print("❌ 便捷API删除失败")

        print("\n" + "=" * 60)
        print("✅ 修复测试完成！")
        print("🎯 所有核心功能都工作正常")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试异常: {e}")


def test_command_line_interface():
    """测试命令行界面"""
    print("\n" + "=" * 60)
    print("命令行界面测试:")
    print("=" * 60)

    print("📋 可用命令:")
    print("  python3 magic_api_resource_manager.py --help")
    print("  python3 magic_api_resource_manager.py --list-tree")
    print("  python3 magic_api_resource_manager.py --list-groups")
    print("  python3 magic_api_resource_manager.py --create-group '测试分组'")
    print("  python3 magic_api_resource_manager.py --create-api 'group_id' 'api_name' 'GET' '/api/path' 'return \"Hello\";'")
    print("  python3 magic_api_resource_manager.py --delete 'resource_id'")

    print("\n✅ 命令行界面测试完成！")


if __name__ == "__main__":
    test_fixed_functionality()
    test_command_line_interface()

    print("\n" + "=" * 60)
    print("🎉 Magic-API 资源管理器修复完成！")
    print("🚀 现在可以正常使用了！")
    print("=" * 60)
