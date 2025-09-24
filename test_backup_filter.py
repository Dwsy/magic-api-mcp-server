#!/usr/bin/env python3
"""测试备份过滤功能。"""

from backup_manager import filter_backups

# 测试数据
test_backups = [
    {
        "id": "api-demo",
        "type": "api",
        "name": "演示API",
        "createBy": "admin",
        "tag": "demo",
        "createDate": 1700000000000
    },
    {
        "id": "user-mgmt",
        "type": "api",
        "name": "用户管理",
        "createBy": "developer",
        "tag": "user",
        "createDate": 1700000001000
    },
    {
        "id": "config-system",
        "type": "config",
        "name": "系统配置",
        "createBy": "admin",
        "tag": "system",
        "createDate": 1700000002000
    },
    {
        "id": "report-api",
        "type": "api",
        "name": "报表API",
        "createBy": "analyst",
        "tag": "report",
        "createDate": 1700000003000
    }
]

def test_filter():
    """测试过滤功能。"""
    print("🧪 测试备份过滤功能")
    print("=" * 50)

    # 测试用例
    test_cases = [
        ("", "无过滤条件"),
        ("api", "按类型过滤 'api'"),
        ("admin", "按创建者过滤 'admin'"),
        ("管理", "按名称过滤 '管理'"),
        ("user", "按标签过滤 'user'"),
        ("不存在的关键词", "不存在的关键词"),
    ]

    for filter_text, description in test_cases:
        print(f"\n🔍 {description}")
        print(f"过滤关键词: '{filter_text}'")

        filtered = filter_backups(test_backups, filter_text)
        print(f"匹配结果: {len(filtered)} 条记录")

        for backup in filtered:
            print(f"  - ID: {backup['id']}, 类型: {backup['type']}, 名称: {backup['name']}, 创建者: {backup['createBy']}")

if __name__ == "__main__":
    test_filter()
