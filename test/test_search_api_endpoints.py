#!/usr/bin/env python3
"""
测试API端点搜索功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from magicapi_tools import MagicAPIHTTPClient, MagicAPISettings


def test_search_api_endpoints():
    """测试API端点搜索功能"""
    print("🔍 测试API端点搜索功能")
    print("=" * 50)

    # 创建HTTP客户端
    settings = MagicAPISettings(base_url="http://127.0.0.1:10712")
    client = MagicAPIHTTPClient(settings=settings)

    try:
        # 测试1: 获取所有端点
        print("1️⃣ 测试获取所有端点")
        from magicapi_tools import load_resource_tree, extract_api_endpoints

        tree = load_resource_tree(client=client)
        all_endpoints = extract_api_endpoints(tree)
        print(f"✅ 找到 {len(all_endpoints)} 个API端点")

        # 显示前5个端点作为示例
        print("前5个端点示例:")
        for endpoint in all_endpoints[:5]:
            print(f"  {endpoint}")
        if len(all_endpoints) > 5:
            print(f"  ... 还有 {len(all_endpoints) - 5} 个端点")

        # 测试2: 按方法过滤
        print("\n2️⃣ 测试按方法过滤 (GET)")
        from magicapi_tools import filter_endpoints

        get_endpoints = filter_endpoints(all_endpoints, method_filter="GET")
        print(f"✅ 找到 {len(get_endpoints)} 个GET端点")

        # 测试3: 按路径过滤
        print("\n3️⃣ 测试按路径过滤 (包含'api')")
        api_endpoints = filter_endpoints(all_endpoints, path_filter="api")
        print(f"✅ 找到 {len(api_endpoints)} 个包含'api'的端点")

        # 测试4: 按名称过滤
        print("\n4️⃣ 测试按名称过滤 (包含'用户')")
        user_endpoints = filter_endpoints(all_endpoints, name_filter="用户")
        print(f"✅ 找到 {len(user_endpoints)} 个包含'用户'的端点")

        # 测试5: 组合过滤
        print("\n5️⃣ 测试组合过滤 (GET方法且路径包含'user')")
        filtered = filter_endpoints(all_endpoints, method_filter="GET", path_filter="user")
        print(f"✅ 找到 {len(filtered)} 个符合条件的端点")

        print("\n✅ 所有搜索功能测试通过!")

    except Exception as exc:
        print(f"❌ 测试失败: {exc}")
        return False

    return True


if __name__ == "__main__":
    success = test_search_api_endpoints()
    sys.exit(0 if success else 1)
