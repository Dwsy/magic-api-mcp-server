#!/usr/bin/env python3
"""测试按名称过滤功能。"""

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
        "name": "用户管理API",
        "createBy": "developer",
        "tag": "user",
        "createDate": 1700000001000
    },
    {
        "id": "user-auth",
        "type": "api",
        "name": "用户认证API",
        "createBy": "developer",
        "tag": "auth",
        "createDate": 1700000002000
    },
    {
        "id": "config-system",
        "type": "config",
        "name": "系统配置",
        "createBy": "admin",
        "tag": "system",
        "createDate": 1700000003000
    },
    {
        "id": "report-api",
        "type": "api",
        "name": "用户报表API",
        "createBy": "analyst",
        "tag": "report",
        "createDate": 1700000004000
    }
]

def test_name_filter():
    """测试按名称过滤功能。"""
    print("🧪 测试按名称过滤功能")
    print("=" * 50)

    # 测试用例
    test_cases = [
        ("", "", "无过滤条件"),
        ("用户", "", "按名称过滤 '用户'（通用过滤）"),
        ("", "API", "按名称过滤 'API'（名称过滤）"),
        ("", "用户", "按名称过滤 '用户'（名称过滤）"),
        ("", "系统", "按名称过滤 '系统'（名称过滤）"),
        ("api", "用户", "组合过滤：通用'api' + 名称'用户'"),
        ("", "不存在的名称", "不存在的名称过滤"),
    ]

    for filter_text, name_filter, description in test_cases:
        print(f"\n🔍 {description}")
        print(f"通用过滤: '{filter_text}', 名称过滤: '{name_filter}'")

        filtered = filter_backups(test_backups, filter_text, name_filter)
        print(f"匹配结果: {len(filtered)} 条记录")

        for backup in filtered:
            print(f"  - ID: {backup['id']}, 名称: {backup['name']}, 类型: {backup['type']}")

if __name__ == "__main__":
    test_name_filter()
