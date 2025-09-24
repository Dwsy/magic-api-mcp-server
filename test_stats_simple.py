#!/usr/bin/env python3
"""使用 requests 直接测试统计功能"""

import requests
import json

def test_stats_simple():
    """使用 requests 直接测试统计功能"""
    print("🔧 使用 requests 直接测试统计功能...")

    try:
        # 直接调用资源树 API
        response = requests.post(
            'http://127.0.0.1:10712/magic/web/resource',
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code != 200:
            print(f"❌ HTTP 响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

        result = response.json()
        if result.get('code') != 1:
            print(f"❌ API 返回错误: {result}")
            return False

        tree_data = result.get('data', {})
        print(f"✅ 获取资源树成功，数据类型: {type(tree_data)}")
        print(f"📊 资源树包含类型: {list(tree_data.keys()) if isinstance(tree_data, dict) else 'N/A'}")

        # 手动实现统计逻辑
        total_resources = 0
        api_endpoints = 0
        by_method = {}
        by_type = {}

        # 遍历所有资源类型
        for resource_type, type_data in tree_data.items():
            if not isinstance(type_data, dict) or "children" not in type_data:
                continue

            print(f"🔍 处理资源类型: {resource_type}")

            # 递归统计节点
            def count_nodes(nodes, current_type):
                nonlocal total_resources, api_endpoints, by_method, by_type
                for node in nodes:
                    node_info = node.get("node", {})
                    total_resources += 1

                    # 统计资源类型
                    node_resource_type = node_info.get("type", current_type)
                    by_type[node_resource_type] = by_type.get(node_resource_type, 0) + 1

                    # 如果是API接口，统计方法
                    method = node_info.get("method")
                    if method:
                        api_endpoints += 1
                        by_method[method.upper()] = by_method.get(method.upper(), 0) + 1

                    # 递归处理子节点
                    children = node.get("children", [])
                    if children:
                        count_nodes(children, current_type)

            count_nodes(type_data["children"], resource_type)

        stats = {
            "total_resources": total_resources,
            "api_endpoints": api_endpoints,
            "other_resources": total_resources - api_endpoints,
            "by_method": by_method,
            "by_type": by_type,
            "resource_types": list(tree_data.keys()) if isinstance(tree_data, dict) else []
        }

        print("✅ 统计完成!")
        print("📈 统计结果:")
        print(f"   总资源数: {stats['total_resources']}")
        print(f"   API端点数: {stats['api_endpoints']}")
        print(f"   其他资源数: {stats['other_resources']}")
        print(f"   按方法统计: {stats['by_method']}")
        print(f"   按类型统计: {stats['by_type']}")
        print(f"   资源类型: {stats['resource_types']}")

        return True

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stats_simple()
    print(f"\n🎯 测试结果: {'通过' if success else '失败'}")
    exit(0 if success else 1)
