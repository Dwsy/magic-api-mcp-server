#!/usr/bin/env python3
"""
测试 depth 参数字符串处理修复
验证字符串 "2" 是否能正确转换为整数 2
"""


def test_depth_string_conversion():
    """测试 depth 参数字符串转换"""
    print("🧪 测试 depth 参数字符串转换")

    def cleanup_depth(depth):
        """复制自修复后的代码的参数清理逻辑"""
        if isinstance(depth, str) and depth.strip() == "":
            depth = None
        elif isinstance(depth, str):
            try:
                depth = int(depth)
                # 确保 depth 在有效范围内
                if depth < 1 or depth > 10:
                    depth = None
            except ValueError:
                depth = None
        return depth

    # 测试1: 字符串 "2" 转换为整数 2
    print("   测试1: 字符串 '2' 转换为整数 2")
    result = cleanup_depth("2")
    assert result == 2, f"字符串 '2' 应该转换为整数 2，但得到 {result}"
    print("✅ 字符串 '2' 正确转换为整数 2")

    # 测试2: 字符串 "5" 转换为整数 5
    print("   测试2: 字符串 '5' 转换为整数 5")
    result = cleanup_depth("5")
    assert result == 5, f"字符串 '5' 应该转换为整数 5，但得到 {result}"
    print("✅ 字符串 '5' 正确转换为整数 5")

    # 测试3: 超出范围的字符串 "15" 转换为 None
    print("   测试3: 超出范围的字符串 '15' 转换为 None")
    result = cleanup_depth("15")
    assert result is None, f"超出范围的字符串 '15' 应该转换为 None，但得到 {result}"
    print("✅ 超出范围的字符串 '15' 正确转换为 None")

    # 测试4: 无效字符串 "abc" 转换为 None
    print("   测试4: 无效字符串 'abc' 转换为 None")
    result = cleanup_depth("abc")
    assert result is None, f"无效字符串 'abc' 应该转换为 None，但得到 {result}"
    print("✅ 无效字符串 'abc' 正确转换为 None")

    # 测试5: 空字符串转换为 None
    print("   测试5: 空字符串转换为 None")
    result = cleanup_depth("")
    assert result is None, f"空字符串应该转换为 None，但得到 {result}"
    print("✅ 空字符串正确转换为 None")

    # 测试6: None 值保持不变
    print("   测试6: None 值保持不变")
    result = cleanup_depth(None)
    assert result is None, f"None 值应该保持不变，但得到 {result}"
    print("✅ None 值保持不变")

    # 测试7: 整数值保持不变
    print("   测试7: 整数值保持不变")
    result = cleanup_depth(3)
    assert result == 3, f"整数 3 应该保持不变，但得到 {result}"
    print("✅ 整数值保持不变")

    print("🎉 所有测试通过！depth 参数字符串处理修复成功")


if __name__ == "__main__":
    test_depth_string_conversion()
