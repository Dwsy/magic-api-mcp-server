#!/usr/bin/env python3
"""Magic-API 资源管理 CLI。"""

from __future__ import annotations

import sys

from magicapi_tools import MagicAPIResourceManager, MagicAPISettings


def print_usage():
    """打印使用说明"""
    print("Magic-API 资源管理器")
    print("=" * 50)
    print("功能: 基于 MagicResourceController 实现目录分组管理")
    print("依赖: pip install requests")
    print("")
    print("基本使用:")
    print("  python3 magic_api_resource_manager.py [选项]")
    print("")
    print("选项:")
    print("  --create-group NAME         创建分组")
    print("  --parent-id ID              指定父分组ID (默认: 0)")
    print("  --group-type TYPE           分组类型 (默认: api)")
    print("  --path PATH                 分组路径")
    print("  --options JSON              选项配置 (JSON格式)")
    print("  --copy SRC_ID TARGET_ID     复制分组")
    print("  --move SRC_ID TARGET_ID     移动资源")
    print("  --delete ID                 删除资源")
    print("  --lock ID                   锁定资源")
    print("  --unlock ID                 解锁资源")
    print("  --list-tree [TYPE]          显示资源树 (默认: api，可选: all, api, function, task, datasource)")
    print("  --csv                       以CSV格式输出资源信息")
    print("  --search PATTERN            搜索过滤资源 (支持正则表达式)")
    print("  --depth N                   限制显示深度 (N为正整数)")
    print("  --list-groups               显示所有分组")
    print("  --create-api GID NAME METH PATH SCRIPT  创建API接口")
    print("  --base-url URL              API基础URL (默认: http://127.0.0.1:10712)")
    print("  --username USER             用户名")
    print("  --password PASS             密码")
    print("  --help, -h                  显示此帮助信息")
    print("")
    print("示例:")
    print("  python3 magic_api_resource_manager.py --list-tree              # 默认显示API类型")
    print("  python3 magic_api_resource_manager.py --list-tree api          # 显示API类型")
    print("  python3 magic_api_resource_manager.py --list-tree all          # 显示所有类型")
    print("  python3 magic_api_resource_manager.py --list-tree function     # 只显示函数类型")
    print("  python3 magic_api_resource_manager.py --list-tree task         # 只显示任务类型")
    print("  python3 magic_api_resource_manager.py --csv --list-tree        # CSV格式输出")
    print("  python3 magic_api_resource_manager.py --search 'python' --list-tree  # 搜索包含'python'的资源")
    print("  python3 magic_api_resource_manager.py --search '.*create.*' --list-tree  # 正则表达式搜索")
    print("  python3 magic_api_resource_manager.py --depth 2 --list-tree   # 只显示2层深度的资源")
    print("  python3 magic_api_resource_manager.py --depth 1 --csv --list-tree  # CSV格式显示1层深度")
    print("  python3 magic_api_resource_manager.py --list-groups            # 显示所有分组")
    print("  python3 magic_api_resource_manager.py --create-group '测试分组'")
    print("  python3 magic_api_resource_manager.py --create-api 'group_id' 'api_name' 'GET' '/api/path' 'return \"Hello\";'")
    print("  python3 magic_api_resource_manager.py --delete 'resource_id'")
    print("")
    print("批量操作:")
    print("  python3 magic_api_resource_manager.py --batch-create-groups 'groups.json'")
    print("  python3 magic_api_resource_manager.py --batch-create-apis 'apis.json'")
    print("  python3 magic_api_resource_manager.py --batch-delete 'resource_ids.json'")
    print("  python3 magic_api_resource_manager.py --export-tree api --format csv > export.csv")
    print("  python3 magic_api_resource_manager.py --stats")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print_usage()
        sys.exit(0)

    # 默认配置
    settings = MagicAPISettings.from_env()
    base_url = settings.base_url
    username = settings.username if settings.auth_enabled else None
    password = settings.password if settings.auth_enabled else None

    # 解析命令行参数
    actions = {
        'create_group': None,
        'copy_group': None,
        'move_resource': None,
        'delete_resource': None,
        'lock_resource': None,
        'unlock_resource': None,
        'list_tree': {'enabled': False, 'type': 'api', 'csv': False, 'search': None, 'depth': None},
        'list_groups': False,
        'create_api': None,
        'batch_create_groups': None,
        'batch_create_apis': None,
        'batch_delete_resources': None,
        'export_tree': {'enabled': False, 'type': 'api', 'format': 'json'},
        'get_stats': False
    }

    params = {
        'parent_id': '0',
        'group_type': 'api',
        'path': None,
        'options': None
    }

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == '--create-group' and i + 1 < len(sys.argv):
            actions['create_group'] = sys.argv[i + 1]
            i += 2
        elif arg == '--copy' and i + 2 < len(sys.argv):
            actions['copy_group'] = (sys.argv[i + 1], sys.argv[i + 2])
            i += 3
        elif arg == '--move' and i + 2 < len(sys.argv):
            actions['move_resource'] = (sys.argv[i + 1], sys.argv[i + 2])
            i += 3
        elif arg == '--delete' and i + 1 < len(sys.argv):
            actions['delete_resource'] = sys.argv[i + 1]
            i += 2
        elif arg == '--lock' and i + 1 < len(sys.argv):
            actions['lock_resource'] = sys.argv[i + 1]
            i += 2
        elif arg == '--unlock' and i + 1 < len(sys.argv):
            actions['unlock_resource'] = sys.argv[i + 1]
            i += 2
        elif arg == '--parent-id' and i + 1 < len(sys.argv):
            params['parent_id'] = sys.argv[i + 1]
            i += 2
        elif arg == '--group-type' and i + 1 < len(sys.argv):
            params['group_type'] = sys.argv[i + 1]
            i += 2
        elif arg == '--path' and i + 1 < len(sys.argv):
            params['path'] = sys.argv[i + 1]
            i += 2
        elif arg == '--options' and i + 1 < len(sys.argv):
            params['options'] = sys.argv[i + 1]
            i += 2
        elif arg == '--base-url' and i + 1 < len(sys.argv):
            base_url = sys.argv[i + 1]
            i += 2
        elif arg == '--username' and i + 1 < len(sys.argv):
            username = sys.argv[i + 1]
            i += 2
        elif arg == '--password' and i + 1 < len(sys.argv):
            password = sys.argv[i + 1]
            i += 2
        elif arg == '--list-tree':
            actions['list_tree']['enabled'] = True
            # 检查是否有类型参数
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                tree_type = sys.argv[i + 1].lower()
                if tree_type in ['all', 'api', 'function', 'task', 'datasource']:
                    actions['list_tree']['type'] = tree_type
                    i += 2
                else:
                    print(f"⚠️ 无效的类型参数: {tree_type}，使用默认类型 'api'")
                    i += 1
            else:
                i += 1
        elif arg == '--csv':
            actions['list_tree']['csv'] = True
            i += 1
        elif arg == '--search' and i + 1 < len(sys.argv):
            actions['list_tree']['search'] = sys.argv[i + 1]
            i += 2
        elif arg == '--depth' and i + 1 < len(sys.argv):
            try:
                depth = int(sys.argv[i + 1])
                if depth > 0:
                    actions['list_tree']['depth'] = depth
                    i += 2
                else:
                    print(f"⚠️ 深度参数必须是正整数: {sys.argv[i + 1]}")
                    i += 2
            except ValueError:
                print(f"⚠️ 无效的深度参数: {sys.argv[i + 1]}，使用默认深度")
                i += 2
        elif arg == '--list-groups':
            actions['list_groups'] = True
            i += 1
        elif arg == '--create-api' and i + 5 < len(sys.argv):
            actions['create_api'] = {
                'group_id': sys.argv[i + 1],
                'name': sys.argv[i + 2],
                'method': sys.argv[i + 3],
                'path': sys.argv[i + 4],
                'script': sys.argv[i + 5]
            }
            i += 6
        elif arg == '--batch-create-groups' and i + 1 < len(sys.argv):
            actions['batch_create_groups'] = sys.argv[i + 1]
            i += 2
        elif arg == '--batch-create-apis' and i + 1 < len(sys.argv):
            actions['batch_create_apis'] = sys.argv[i + 1]
            i += 2
        elif arg == '--batch-delete' and i + 1 < len(sys.argv):
            actions['batch_delete_resources'] = sys.argv[i + 1]
            i += 2
        elif arg == '--export-tree':
            actions['export_tree']['enabled'] = True
            # 检查是否有类型参数
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                export_type = sys.argv[i + 1].lower()
                if export_type in ['all', 'api', 'function', 'task', 'datasource']:
                    actions['export_tree']['type'] = export_type
                    i += 2
                else:
                    print(f"⚠️ 无效的导出类型参数: {export_type}，使用默认类型 'api'")
                    i += 1
            else:
                i += 1
        elif arg == '--format' and i + 1 < len(sys.argv):
            format_type = sys.argv[i + 1].lower()
            if format_type in ['json', 'csv']:
                actions['export_tree']['format'] = format_type
                i += 2
            else:
                print(f"⚠️ 无效的格式参数: {format_type}，使用默认格式 'json'")
                i += 2
        elif arg == '--stats':
            actions['get_stats'] = True
            i += 1
        else:
            print(f"❌ 未知参数: {arg}")
            print_usage()
            sys.exit(1)

    # 创建资源管理器
    print(f"📡 连接到: {base_url}")
    manager = MagicAPIResourceManager(base_url, username, password)

    print("\n" + "=" * 50)
    print("Magic API 资源管理器")
    print("=" * 50)

    # 执行操作
    try:
        # 1. 显示资源树
        if actions['list_tree']['enabled']:
            tree_type = actions['list_tree']['type']
            csv_mode = actions['list_tree']['csv']
            search_pattern = actions['list_tree']['search']
            depth = actions['list_tree']['depth']

            # 构建信息字符串
            info_parts = []
            if tree_type != 'api':
                info_parts.append(f"过滤类型: {tree_type}")
            if csv_mode:
                info_parts.append("CSV格式")
            if search_pattern:
                info_parts.append(f"搜索: {search_pattern}")
            if depth is not None:
                info_parts.append(f"最大深度: {depth}")

            filter_info = f" ({', '.join(info_parts)})" if info_parts else " (默认显示API类型)"
            print(f"\n📋 获取资源树结构{filter_info}:")

            tree_data = manager.get_resource_tree()
            if tree_data:
                manager.print_resource_tree(tree_data, filter_type=tree_type, csv_format=csv_mode, search_pattern=search_pattern, max_depth=depth)
            else:
                print("❌ 获取资源树失败")
            return

        # 2. 显示分组列表
        elif actions['list_groups']:
            print("\n📋 获取分组列表:")
            groups = manager.list_groups()
            if groups:
                print(f"📊 共找到 {len(groups)} 个分组:")
                for group in groups:
                    if group.get('method'):
                        # API接口
                        print(f"  📄 {group['name']} [{group['method']}] (ID: {group['id']})")
                    else:
                        # 分组目录
                        print(f"  📁 {group['name']} ({group['type']}) (ID: {group['id']})")
            else:
                print("❌ 获取分组列表失败")
            return

        # 3. 创建API接口
        elif actions['create_api']:
            api_info = actions['create_api']
            print(f"\n📝 创建API接口: {api_info['name']}")
            file_id = manager.create_api_file(
                group_id=api_info['group_id'],
                name=api_info['name'],
                method=api_info['method'],
                path=api_info['path'],
                script=api_info['script']
            )
            if file_id:
                print(f"✅ API接口创建成功: {api_info['name']} (ID: {file_id})")
            return

        # 4. 创建分组
        if actions['create_group']:
            print(f"\n📁 创建分组: {actions['create_group']}")

            # 解析选项
            options = {}
            if params['options']:
                try:
                    options = json.loads(params['options'])
                except json.JSONDecodeError:
                    print("⚠️ 选项格式错误，使用默认值")

            group_id = manager.create_group(
                name=actions['create_group'],
                parent_id=params['parent_id'],
                group_type=params['group_type'],
                path=params['path'],
                options=options
            )

            if group_id:
                print(f"✅ 分组ID: {group_id}")

        # 5. 复制分组
        elif actions['copy_group']:
            src_id, target_id = actions['copy_group']
            print(f"\n📋 复制分组: {src_id} -> {target_id}")
            new_group_id = manager.copy_group(src_id, target_id)
            if new_group_id:
                print(f"✅ 新分组ID: {new_group_id}")

        # 6. 移动资源
        elif actions['move_resource']:
            src_id, target_id = actions['move_resource']
            print(f"\n📋 移动资源: {src_id} -> {target_id}")
            success = manager.move_resource(src_id, target_id)
            if success:
                print("✅ 移动成功")

        # 7. 删除资源
        elif actions['delete_resource']:
            resource_id = actions['delete_resource']
            print(f"\n🗑️  删除资源: {resource_id}")
            success = manager.delete_resource(resource_id)
            if success:
                print("✅ 删除成功")

        # 8. 锁定资源
        elif actions['lock_resource']:
            resource_id = actions['lock_resource']
            print(f"\n🔒 锁定资源: {resource_id}")
            success = manager.lock_resource(resource_id)
            if success:
                print("✅ 锁定成功")

        # 9. 解锁资源
        elif actions['unlock_resource']:
            resource_id = actions['unlock_resource']
            print(f"\n🔓 解锁资源: {resource_id}")
            success = manager.unlock_resource(resource_id)
            if success:
                print("✅ 解锁成功")

        # 批量创建分组
        elif actions['batch_create_groups']:
            file_path = actions['batch_create_groups']
            print(f"\n📁 批量创建分组 (从文件: {file_path})")
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    groups_data = json.load(f)

                from magicapi_tools import MagicAPIResourceTools
                tools = MagicAPIResourceTools(manager)
                result = tools.batch_create_groups_tool(groups_data)

                if result['successful'] > 0:
                    print(f"✅ 批量创建分组完成: {result['successful']} 个成功")
                    if result['failed'] > 0:
                        print(f"⚠️  {result['failed']} 个失败")
                        for item in result['results']:
                            if 'error' in item['result']:
                                print(f"  ❌ {item['name']}: {item['result']['error']['message']}")
                else:
                    print("❌ 批量创建分组失败")

            except FileNotFoundError:
                print(f"❌ 文件不存在: {file_path}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON格式错误: {e}")
            except Exception as e:
                print(f"❌ 批量创建分组异常: {e}")

        # 批量创建API
        elif actions['batch_create_apis']:
            file_path = actions['batch_create_apis']
            print(f"\n📝 批量创建API (从文件: {file_path})")
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    apis_data = json.load(f)

                from magicapi_tools import MagicAPIResourceTools
                tools = MagicAPIResourceTools(manager)
                result = tools.batch_create_apis_tool(apis_data)

                if result['successful'] > 0:
                    print(f"✅ 批量创建API完成: {result['successful']} 个成功")
                    if result['failed'] > 0:
                        print(f"⚠️  {result['failed']} 个失败")
                        for item in result['results']:
                            if 'error' in item['result']:
                                print(f"  ❌ {item['name']}: {item['result']['error']['message']}")
                else:
                    print("❌ 批量创建API失败")

            except FileNotFoundError:
                print(f"❌ 文件不存在: {file_path}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON格式错误: {e}")
            except Exception as e:
                print(f"❌ 批量创建API异常: {e}")

        # 批量删除资源
        elif actions['batch_delete_resources']:
            file_path = actions['batch_delete_resources']
            print(f"\n🗑️  批量删除资源 (从文件: {file_path})")
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    resource_ids = json.load(f)

                from magicapi_tools import MagicAPIResourceTools
                tools = MagicAPIResourceTools(manager)
                result = tools.batch_delete_resources_tool(resource_ids)

                if result['successful'] > 0:
                    print(f"✅ 批量删除资源完成: {result['successful']} 个成功")
                    if result['failed'] > 0:
                        print(f"⚠️  {result['failed']} 个失败")
                        for item in result['results']:
                            if 'error' in item['result']:
                                print(f"  ❌ {item['resource_id']}: {item['result']['error']['message']}")
                else:
                    print("❌ 批量删除资源失败")

            except FileNotFoundError:
                print(f"❌ 文件不存在: {file_path}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON格式错误: {e}")
            except Exception as e:
                print(f"❌ 批量删除资源异常: {e}")

        # 导出资源树
        elif actions['export_tree']['enabled']:
            export_type = actions['export_tree']['type']
            export_format = actions['export_tree']['format']

            print(f"\n📤 导出资源树 (类型: {export_type}, 格式: {export_format})")

            try:
                from magicapi_tools import MagicAPIResourceTools
                tools = MagicAPIResourceTools(manager)
                result = tools.export_resource_tree_tool(kind=export_type, format=export_format)

                if 'success' in result:
                    if export_format == 'csv':
                        print(result['data'])
                    else:
                        print(json.dumps(result['data'], indent=2, ensure_ascii=False))
                else:
                    print("❌ 导出资源树失败")

            except Exception as e:
                print(f"❌ 导出资源树异常: {e}")

        # 获取统计信息
        elif actions['get_stats']:
            print("\n📊 获取资源统计信息:")

            try:
                from magicapi_tools import MagicAPIResourceTools
                tools = MagicAPIResourceTools(manager)
                result = tools.get_resource_stats_tool()

                if 'success' in result:
                    stats = result['stats']
                    print(f"📈 总资源数: {stats['total_resources']}")
                    print(f"🔗 API端点数: {stats['api_endpoints']}")
                    print(f"📁 其他资源数: {stats['other_resources']}")
                    print("📋 按HTTP方法统计:")
                    for method, count in stats['by_method'].items():
                        print(f"  {method}: {count}")
                else:
                    print("❌ 获取统计信息失败")

            except Exception as e:
                print(f"❌ 获取统计信息异常: {e}")

        else:
            # 默认显示资源树
            print("\n📋 资源树结构:")
            tree_data = manager.get_resource_tree()
            if tree_data:
                manager.print_resource_tree(tree_data)
            else:
                print("❌ 获取资源树失败")

    except KeyboardInterrupt:
        print("\n⏹️ 操作被用户中断")
    except Exception as e:
        print(f"❌ 执行异常: {e}")


if __name__ == "__main__":
    main()
