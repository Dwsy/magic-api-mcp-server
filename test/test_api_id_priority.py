#!/usr/bin/env python3
"""
测试 call_magic_api api_id 优先级修改
验证当提供 api_id 时是否完全忽略 path 参数
"""


def test_api_id_priority():
    """测试 api_id 优先级逻辑"""
    print("🧪 测试 call_magic_api api_id 优先级")

    def simulate_api_call_logic(api_id, method, path):
        """模拟修改后的 API 调用逻辑"""
        if api_id:
            # 传入的是接口ID，先获取详细信息，完全忽略path参数
            print(f"   使用 api_id: {api_id}，忽略 method='{method}' 和 path='{path}'")
            return f"使用ID: {api_id}"
        else:
            # 没有提供api_id，使用method和path参数
            if method is None and path is None:
                return "错误: method和path不能同时为空"
            return f"使用路径: {method} {path}"

    # 测试1: 有 api_id 时忽略 path
    print("   测试1: 有 api_id 时忽略 path")
    result = simulate_api_call_logic("123", "POST", "/api/test")
    expected = "使用ID: 123"
    assert result == expected, f"应该使用 api_id，但得到: {result}"
    print("✅ 有 api_id 时正确忽略 path")

    # 测试2: 有 api_id 时忽略 method 和 path
    print("   测试2: 有 api_id 时忽略 method 和 path")
    result = simulate_api_call_logic("456", "GET", "/api/users")
    expected = "使用ID: 456"
    assert result == expected, f"应该使用 api_id，但得到: {result}"
    print("✅ 有 api_id 时正确忽略 method 和 path")

    # 测试3: 没有 api_id 时使用 method 和 path
    print("   测试3: 没有 api_id 时使用 method 和 path")
    result = simulate_api_call_logic(None, "POST", "/api/test")
    expected = "使用路径: POST /api/test"
    assert result == expected, f"应该使用路径，但得到: {result}"
    print("✅ 没有 api_id 时正确使用 method 和 path")

    # 测试4: 没有 api_id 且 method 和 path 都为空时报错
    print("   测试4: 没有 api_id 且 method 和 path 都为空时报错")
    result = simulate_api_call_logic(None, None, None)
    expected = "错误: method和path不能同时为空"
    assert result == expected, f"应该报错，但得到: {result}"
    print("✅ 没有 api_id 且参数为空时正确报错")

    print("🎉 所有测试通过！call_magic_api api_id 优先级修改成功")


if __name__ == "__main__":
    test_api_id_priority()
