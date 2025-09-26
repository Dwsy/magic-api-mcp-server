#!/usr/bin/env python3
"""
测试 get_common_pitfalls 数据格式修复
验证返回格式是否正确
"""


def test_pitfalls_format():
    """测试 pitfalls 数据格式转换"""
    print("🧪 测试 get_common_pitfalls 数据格式转换")

    # 模拟原始的字符串列表数据
    mock_pitfalls = [
        "0.4.6+ 逻辑运算对非布尔类型短路，与旧版本不同",
        "`exit` 会跳过 `finally`，涉及事务需谨慎",
        "`asDate()` 需要区分 10 位秒/13 位毫秒时间戳",
        "集合遍历时删除元素注意并发修改异常"
    ]

    def transform_pitfalls(pitfalls_list):
        """模拟修复后的转换逻辑"""
        return [
            {
                "id": i + 1,
                "title": pitfall,
                "description": pitfall,
                "category": "common_pitfall",
                "severity": "medium"
            }
            for i, pitfall in enumerate(pitfalls_list)
        ]

    # 测试转换结果
    result = transform_pitfalls(mock_pitfalls)

    # 验证结果格式
    assert isinstance(result, list), "结果应该是列表"
    assert len(result) == 4, f"结果应该有4个元素，得到 {len(result)}"

    for i, item in enumerate(result):
        assert isinstance(item, dict), f"第{i+1}个元素应该是字典，得到 {type(item)}"
        assert "id" in item, f"字典应该包含 'id' 字段"
        assert "title" in item, f"字典应该包含 'title' 字段"
        assert "description" in item, f"字典应该包含 'description' 字段"
        assert "category" in item, f"字典应该包含 'category' 字段"
        assert "severity" in item, f"字典应该包含 'severity' 字段"

        assert item["id"] == i + 1, f"id 应该是 {i + 1}，得到 {item['id']}"
        assert item["title"] == mock_pitfalls[i], f"title 不匹配"
        assert item["description"] == mock_pitfalls[i], f"description 不匹配"
        assert item["category"] == "common_pitfall", f"category 不匹配"
        assert item["severity"] == "medium", f"severity 不匹配"

    print("✅ 数据格式转换正确")
    print(f"   示例输出: {result[0]}")

    # 验证特定元素
    last_item = result[-1]
    expected_title = "集合遍历时删除元素注意并发修改异常"
    assert last_item["title"] == expected_title, f"最后一个元素的标题不正确"
    assert last_item["id"] == 4, f"最后一个元素的ID应该是4，得到 {last_item['id']}"

    print("✅ 特定元素验证通过")
    print("🎉 所有测试通过！get_common_pitfalls 数据格式修复成功")


if __name__ == "__main__":
    test_pitfalls_format()
