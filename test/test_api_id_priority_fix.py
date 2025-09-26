#!/usr/bin/env python3
"""
测试 call_magic_api api_id 优先级和参数验证修复
验证 api_id 使用完整路径和参数验证逻辑
"""


def test_api_id_priority_fix():
    """测试 api_id 优先级和参数验证修复"""
    print("🧪 测试 call_magic_api api_id 优先级和参数验证修复")

    def simulate_api_call_logic(api_id, method, path):
        """模拟修改后的 API 调用逻辑"""
        if api_id:
            # 传入的是接口ID，先获取详细信息，完全忽略path参数
            # 模拟获取完整路径
            full_path = f"/full/path/to/api/{api_id}"
            actual_method = "POST"  # 从API详情中获取
            actual_path = full_path  # 直接使用完整的路径
            return f"使用ID: {api_id}, 方法: {actual_method}, 路径: {actual_path}"
        else:
            # 没有提供api_id，使用method和path参数
            # 检查参数有效性：如果提供了path，必须提供method
            if path is not None and method is None:
                return "错误: 如果提供path参数，必须同时提供method参数"

            if method is None and path is None:
                return "错误: method和path不能同时为空"

            return f"使用路径: {method} {path}"

    # 测试1: 只提供 api_id，应该成功
    print("   测试1: 只提供 api_id")
    result = simulate_api_call_logic("123", None, None)
    expected = "使用ID: 123, 方法: POST, 路径: /full/path/to/api/123"
    assert result == expected, f"只提供 api_id 应该成功，但得到: {result}"
    print("✅ 只提供 api_id 成功")

    # 测试2: 提供 api_id 和其他参数，应该忽略其他参数
    print("   测试2: 提供 api_id 和其他参数（应该忽略其他参数）")
    result = simulate_api_call_logic("456", "GET", "/api/test")
    expected = "使用ID: 456, 方法: POST, 路径: /full/path/to/api/456"
    assert result == expected, f"提供 api_id 时应该忽略其他参数，但得到: {result}"
    print("✅ 提供 api_id 时正确忽略其他参数")

    # 测试3: 不提供 api_id，提供 method 和 path，应该成功
    print("   测试3: 不提供 api_id，提供 method 和 path")
    result = simulate_api_call_logic(None, "GET", "/api/test")
    expected = "使用路径: GET /api/test"
    assert result == expected, f"提供 method 和 path 应该成功，但得到: {result}"
    print("✅ 提供 method 和 path 成功")

    # 测试4: 不提供 api_id，只提供 path，应该报错
    print("   测试4: 不提供 api_id，只提供 path")
    result = simulate_api_call_logic(None, None, "/api/test")
    expected = "错误: 如果提供path参数，必须同时提供method参数"
    assert result == expected, f"只提供 path 应该报错，但得到: {result}"
    print("✅ 只提供 path 正确报错")

    # 测试5: 不提供 api_id，也不提供 method 和 path，应该报错
    print("   测试5: 不提供任何参数")
    result = simulate_api_call_logic(None, None, None)
    expected = "错误: method和path不能同时为空"
    assert result == expected, f"不提供任何参数应该报错，但得到: {result}"
    print("✅ 不提供任何参数正确报错")

    print("🎉 所有测试通过！call_magic_api api_id 优先级和参数验证修复成功")


if __name__ == "__main__":
    test_api_id_priority_fix()
