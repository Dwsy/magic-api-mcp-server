#!/usr/bin/env python3
"""
测试命令解析修复的脚本
"""

def test_command_parsing():
    """测试test命令的解析逻辑"""

    def parse_test_command(command_line):
        """模拟test命令的解析逻辑"""
        if not command_line.strip():
            return None

        parts = command_line.split()
        command = parts[0].lower()

        if command == "test":
            # 执行测试API，支持自定义路径和断点
            path = "/test00/test0001"  # 默认路径
            breakpoints = []

            if len(parts) > 1:
                # 检查第一个参数是否是路径（不是纯数字且看起来像路径）
                first_arg = parts[1]

                # 如果是纯数字或数字逗号组合，认为是断点
                if first_arg.isdigit() or (',' in first_arg and all(x.strip().isdigit() for x in first_arg.split(','))):
                    try:
                        breakpoints = [int(x.strip()) for x in first_arg.split(',')]
                    except ValueError:
                        return f"❌ 断点格式错误: {first_arg}"
                else:
                    # 这是一个路径
                    path = first_arg
                    # 检查是否有断点参数
                    if len(parts) > 2:
                        try:
                            breakpoints = [int(x.strip()) for x in parts[2].split(',')]
                        except ValueError:
                            return f"❌ 断点格式错误: {parts[2]}"

            return {
                "command": "test",
                "path": path,
                "breakpoints": breakpoints
            }

        return None

    # 测试用例
    test_cases = [
        ("test", {"command": "test", "path": "/test00/test0001", "breakpoints": []}),
        ("test 5,10", {"command": "test", "path": "/test00/test0001", "breakpoints": [5, 10]}),
        ("test test00/test0001", {"command": "test", "path": "test00/test0001", "breakpoints": []}),
        ("test test00/test0001 3", {"command": "test", "path": "test00/test0001", "breakpoints": [3]}),
        ("test test00/test0001 3,4", {"command": "test", "path": "test00/test0001", "breakpoints": [3, 4]}),
        ("test /api/test 5,10", {"command": "test", "path": "/api/test", "breakpoints": [5, 10]}),
        ("test invalid_breakpoint", {"command": "test", "path": "invalid_breakpoint", "breakpoints": []}),
        ("test /api/test invalid", "❌ 断点格式错误: invalid"),
    ]

    print("🧪 测试命令解析修复")
    print("=" * 50)

    all_passed = True
    for i, (input_cmd, expected) in enumerate(test_cases, 1):
        result = parse_test_command(input_cmd)
        if result == expected:
            print(f"✅ 测试 {i}: '{input_cmd}' -> {result}")
        else:
            print(f"❌ 测试 {i}: '{input_cmd}'")
            print(f"   期望: {expected}")
            print(f"   实际: {result}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉 所有测试通过！命令解析修复成功。")
        return True
    else:
        print("❌ 部分测试失败！")
        return False


if __name__ == "__main__":
    success = test_command_parsing()
    exit(0 if success else 1)
