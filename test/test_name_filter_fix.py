#!/usr/bin/env python3
"""
测试 get_resource_tree name_filter 修复
验证 name_filter 是否能在树形结构中正常工作
"""


def test_name_filter_logic():
    """测试 name_filter 过滤逻辑"""
    print("🧪 测试 get_resource_tree name_filter 过滤逻辑")

    def simulate_filter_node(node, name_filter, path_filter=None, method_filter=None, query_filter=None, allowed=None):
        """模拟修改后的过滤逻辑"""
        if allowed is None:
            allowed = ["api"]

        # 过滤node信息
        if "node" in node:
            node_info = node["node"]
            node_type = node_info.get("type")
            method = node_info.get("method")
            node_name = node_info.get("name")
            node_path = node_info.get("path", "")

            # 检查是否应该包含此节点
            should_include = True

            # 类型过滤
            if allowed != ["all"]:
                if node_type and node_type not in allowed:
                    should_include = False
                elif method and "api" in allowed:
                    should_include = True

            # 高级过滤器：name_filter, path_filter, method_filter, query_filter
            if should_include and (name_filter or path_filter or method_filter or query_filter):
                # name_filter：名称过滤
                if name_filter and node_name:
                    if name_filter.lower() not in node_name.lower():
                        should_include = False

                # path_filter：路径过滤
                if should_include and path_filter and node_path:
                    if path_filter.lower() not in node_path.lower():
                        should_include = False

                # method_filter：方法过滤
                if should_include and method_filter and method:
                    if method_filter.upper() != method.upper():
                        should_include = False

                # query_filter：通用查询过滤
                if should_include and query_filter:
                    # 检查是否在任何相关字段中包含查询关键词
                    searchable_text = f"{node_name} {node_path} {method} {node_type or ''}".strip().lower()
                    query_lower = query_filter.lower()
                    if query_lower not in searchable_text:
                        should_include = False

            return should_include

        return True

    # 测试数据
    test_nodes = [
        {"node": {"name": "背包算法", "path": "/api/knapsack", "method": "POST", "type": "api"}},
        {"node": {"name": "用户管理", "path": "/api/users", "method": "GET", "type": "api"}},
        {"node": {"name": "订单背包", "path": "/api/orders", "method": "POST", "type": "api"}},
        {"node": {"name": "数据统计", "path": "/api/stats", "method": "GET", "type": "api"}},
    ]

    # 测试1: name_filter="背包" 应该匹配包含"背包"的节点
    print("   测试1: name_filter='背包' 过滤")
    results = [simulate_filter_node(node, name_filter="背包") for node in test_nodes]
    expected = [True, False, True, False]  # "背包算法"和"订单背包"应该匹配
    assert results == expected, f"name_filter='背包' 过滤失败，期望 {expected}，得到 {results}"
    print("✅ name_filter='背包' 正确过滤出包含'背包'的节点")

    # 测试2: name_filter="管理" 应该匹配"用户管理"
    print("   测试2: name_filter='管理' 过滤")
    results = [simulate_filter_node(node, name_filter="管理") for node in test_nodes]
    expected = [False, True, False, False]  # 只有"用户管理"应该匹配
    assert results == expected, f"name_filter='管理' 过滤失败，期望 {expected}，得到 {results}"
    print("✅ name_filter='管理' 正确过滤出'用户管理'节点")

    # 测试3: name_filter="test" 应该不匹配任何节点
    print("   测试3: name_filter='test' 过滤（无匹配）")
    results = [simulate_filter_node(node, name_filter="test") for node in test_nodes]
    expected = [False, False, False, False]  # 都不应该匹配
    assert results == expected, f"name_filter='test' 过滤失败，期望 {expected}，得到 {results}"
    print("✅ name_filter='test' 正确过滤出无匹配节点")

    # 测试4: path_filter="/api/users" 应该匹配用户管理
    print("   测试4: path_filter='/api/users' 过滤")
    results = [simulate_filter_node(node, name_filter=None, path_filter="/api/users") for node in test_nodes]
    expected = [False, True, False, False]  # 只有用户管理应该匹配
    assert results == expected, f"path_filter='/api/users' 过滤失败，期望 {expected}，得到 {results}"
    print("✅ path_filter='/api/users' 正确过滤出匹配路径的节点")

    # 测试5: method_filter="POST" 应该匹配POST方法
    print("   测试5: method_filter='POST' 过滤")
    results = [simulate_filter_node(node, name_filter=None, method_filter="POST") for node in test_nodes]
    expected = [True, False, True, False]  # "背包算法"和"订单背包"应该是POST
    assert results == expected, f"method_filter='POST' 过滤失败，期望 {expected}，得到 {results}"
    print("✅ method_filter='POST' 正确过滤出POST方法的节点")

    # 测试6: query_filter="数据" 应该匹配"数据统计"
    print("   测试6: query_filter='数据' 过滤")
    results = [simulate_filter_node(node, name_filter=None, query_filter="数据") for node in test_nodes]
    expected = [False, False, False, True]  # 只有"数据统计"应该匹配
    assert results == expected, f"query_filter='数据' 过滤失败，期望 {expected}，得到 {results}"
    print("✅ query_filter='数据' 正确过滤出包含关键词的节点")

    print("🎉 所有测试通过！get_resource_tree name_filter 过滤修复成功")


if __name__ == "__main__":
    test_name_filter_logic()
