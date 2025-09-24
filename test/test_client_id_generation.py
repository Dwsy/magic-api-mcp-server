#!/usr/bin/env python3
"""
测试client_id生成功能
"""

import sys
import os
import re

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from magic_api_debug_client import MagicAPIDebugClient


def test_client_id_generation():
    """测试client_id生成功能"""

    print("🧪 测试client_id生成功能")
    print("=" * 50)

    # 创建多个客户端实例，验证ID的唯一性和格式
    clients = []
    client_ids = []

    for i in range(5):
        client = MagicAPIDebugClient(
            ws_url="ws://127.0.0.1:10712/magic/web/console",
            api_base_url="http://127.0.0.1:10712"
        )
        clients.append(client)
        client_ids.append(client.client_id)
        print(f"客户端 {i+1}: {client.client_id}")

    print("\n🔍 验证生成结果:")

    # 验证格式（16字符十六进制）
    hex_pattern = re.compile(r'^[0-9a-f]{16}$')

    all_valid = True
    for i, client_id in enumerate(client_ids):
        if len(client_id) != 16:
            print(f"❌ 客户端 {i+1}: 长度错误 ({len(client_id)} != 16)")
            all_valid = False
        elif not hex_pattern.match(client_id):
            print(f"❌ 客户端 {i+1}: 格式错误 (不是有效的16进制)")
            all_valid = False
        else:
            print(f"✅ 客户端 {i+1}: 格式正确 (16字符十六进制)")

    # 验证唯一性
    if len(set(client_ids)) == len(client_ids):
        print("✅ 所有client_id都是唯一的")
    else:
        print("❌ 发现重复的client_id")
        all_valid = False

    # 验证与示例格式相似
    example_id = "e14351b1da793922"
    print("\n📋 与示例对比:")
    print(f"示例ID: {example_id} (长度: {len(example_id)})")
    print(f"生成ID: {client_ids[0]} (长度: {len(client_ids[0])})")
    print(f"格式匹配: {'✅' if hex_pattern.match(example_id) else '❌'}")

    print("\n" + "=" * 50)
    if all_valid:
        print("✅ client_id生成测试通过!")
        print("🎯 生成的ID符合以下要求:")
        print("   - 长度: 16字符")
        print("   - 格式: 小写十六进制")
        print("   - 唯一性: 每次生成都不相同")
        return True
    else:
        print("❌ client_id生成测试失败!")
        return False


if __name__ == "__main__":
    success = test_client_id_generation()
    exit(0 if success else 1)
