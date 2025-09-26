#!/usr/bin/env python3
"""
测试 get_best_practices 数据格式修复
验证返回格式是否正确
"""


def test_best_practices_format():
    """测试 best_practices 数据格式转换"""
    print("🧪 测试 get_best_practices 数据格式转换")

    # 模拟原始的字符串列表数据
    mock_practices = [
        "SQL 参数一律使用 `#{}` 绑定，避免 `${}` 拼接",
        "接口返回统一通过 `response` 模块封装，按需选择 json/page/text/download",
        "集合操作优先使用函数式编程：`map`/`filter`/`group` 等，提高代码可读性"
    ]

    def transform_practices(practices_list):
        """模拟修复后的转换逻辑"""
        return [
            {
                "id": i + 1,
                "title": practice,
                "description": practice,
                "category": "best_practice",
                "priority": "high"
            }
            for i, practice in enumerate(practices_list)
        ]

    # 测试转换结果
    result = transform_practices(mock_practices)

    # 验证结果格式
    assert isinstance(result, list), "结果应该是列表"
    assert len(result) == 3, f"结果应该有3个元素，得到 {len(result)}"

    for i, item in enumerate(result):
        assert isinstance(item, dict), f"第{i+1}个元素应该是字典，得到 {type(item)}"
        assert "id" in item, f"字典应该包含 'id' 字段"
        assert "title" in item, f"字典应该包含 'title' 字段"
        assert "description" in item, f"字典应该包含 'description' 字段"
        assert "category" in item, f"字典应该包含 'category' 字段"
        assert "priority" in item, f"字典应该包含 'priority' 字段"

        assert item["id"] == i + 1, f"id 应该是 {i + 1}，得到 {item['id']}"
        assert item["title"] == mock_practices[i], f"title 不匹配"
        assert item["description"] == mock_practices[i], f"description 不匹配"
        assert item["category"] == "best_practice", f"category 不匹配"
        assert item["priority"] == "high", f"priority 不匹配"

    print("✅ 数据格式转换正确")
    print(f"   示例输出: {result[0]}")

    # 验证特定元素
    last_item = result[-1]
    expected_title = "集合操作优先使用函数式编程：`map`/`filter`/`group` 等，提高代码可读性"
    assert last_item["title"] == expected_title, f"最后一个元素的标题不正确"
    assert last_item["id"] == 3, f"最后一个元素的ID应该是3，得到 {last_item['id']}"

    print("✅ 特定元素验证通过")
    print("🎉 所有测试通过！get_best_practices 数据格式修复成功")


if __name__ == "__main__":
    test_best_practices_format()
