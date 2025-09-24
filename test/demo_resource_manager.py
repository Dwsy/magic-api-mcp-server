#!/usr/bin/env python3
"""
Magic-API 资源管理器演示脚本
演示如何使用 MagicAPIResourceManager 进行目录分组管理
"""

from magic_api_resource_manager import MagicAPIResourceManager


def demo_resource_manager():
    """演示资源管理器的基本功能"""

    # 配置连接信息
    BASE_URL = "http://127.0.0.1:10712"
    USERNAME = "admin"
    PASSWORD = "123456"

    print("🚀 Magic-API 资源管理器演示")
    print("=" * 50)

    # 创建资源管理器
    print(f"📡 连接到: {BASE_URL}")
    manager = MagicAPIResourceManager(BASE_URL, USERNAME, PASSWORD)

    print("\n" + "=" * 50)
    print("演示步骤:")
    print("=" * 50)

    try:
        # 1. 获取并显示资源树
        print("\n1️⃣ 获取资源树结构:")
        tree_data = manager.get_resource_tree()
        if tree_data:
            manager.print_resource_tree(tree_data)
        else:
            print("❌ 获取资源树失败")
            return
        print()

        # 2. 创建新分组
        print("2️⃣ 创建新分组:")
        group_id = manager.create_group(
            name="演示分组",
            parent_id="0",
            group_type="api",
            path="/demo",
            options={"description": "这是演示用的分组", "author": "demo_script"}
        )
        print()

        # 3. 创建子分组
        if group_id:
            print("3️⃣ 创建子分组:")
            sub_group_id = manager.create_group(
                name="子分组",
                parent_id=group_id,
                group_type="api",
                path="/sub"
            )
            print()

            # 4. 复制分组
            print("4️⃣ 复制分组:")
            copied_group_id = manager.copy_group(group_id, "0")
            print()

            # 5. 锁定和解锁资源
            print("5️⃣ 资源锁定操作:")
            if sub_group_id:
                manager.lock_resource(sub_group_id)
                print("   锁定子分组成功")

                manager.unlock_resource(sub_group_id)
                print("   解锁子分组成功")
            print()

            # 6. 删除测试资源
            print("6️⃣ 清理测试资源:")
            if copied_group_id:
                manager.delete_resource(copied_group_id)
                print("   删除复制的分组成功")

            if sub_group_id:
                manager.delete_resource(sub_group_id)
                print("   删除子分组成功")

            manager.delete_resource(group_id)
            print("   删除演示分组成功")
            print()

        # 7. 再次获取资源树查看变化
        print("7️⃣ 最终资源树结构:")
        tree_data = manager.get_resource_tree()
        if tree_data:
            manager.print_resource_tree(tree_data)
        else:
            print("❌ 获取资源树失败")
        print()

        print("✅ 演示完成！")
        print("📚 更多功能请参考 README.md")

    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"❌ 演示异常: {e}")


def demo_api_operations():
    """演示API操作功能"""

    print("\n" + "=" * 50)
    print("API 操作演示:")
    print("=" * 50)

    # 配置连接信息
    BASE_URL = "http://127.0.0.1:10712"
    USERNAME = "admin"
    PASSWORD = "123456"

    # 创建资源管理器
    manager = MagicAPIResourceManager(BASE_URL, USERNAME, PASSWORD)

    try:
        # 获取文件详情示例
        print("\n📋 获取文件详情:")
        # 注意：这里需要实际的文件ID，实际使用时请替换为真实的ID
        # file_detail = manager.get_file_detail("actual_file_id")
        # if file_detail:
        #     print(f"📄 文件信息: {file_detail}")
        print("   提示：需要提供实际的文件ID才能查看详情")
        print()

        # 保存API文件示例
        print("📦 保存API文件:")
        # 注意：实际使用时请提供真实的API数据
        # api_data = {
        #     "name": "demo_api",
        #     "method": "GET",
        #     "path": "/demo/api",
        #     "script": "return 'Hello from demo API';"
        # }
        # file_id = manager.save_api_file("api", api_data, auto_save=True)
        # if file_id:
        #     print(f"✅ API文件保存成功，文件ID: {file_id}")
        print("   提示：需要提供真实的API数据才能保存")
        print()

        print("✅ API操作演示完成！")

    except Exception as e:
        print(f"❌ API操作异常: {e}")


if __name__ == "__main__":
    print("🎯 Magic-API 资源管理器功能演示")
    print("   本演示将展示资源管理器的基本功能")

    # 询问用户是否继续
    try:
        input("\n按 Enter 键开始演示，或 Ctrl+C 取消...")
    except KeyboardInterrupt:
        print("\n👋 演示已取消")
        exit(0)

    demo_resource_manager()
    demo_api_operations()

    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("=" * 50)
    print("📖 如需了解更多用法，请查看 README.md")
    print("💻 命令行使用示例：")
    print("   python3 magic_api_resource_manager.py --help")
    print("   python3 magic_api_resource_manager.py --list-tree")
    print("   python3 magic_api_resource_manager.py --create-group '测试分组'")
