#!/usr/bin/env python3
"""
测试断点消息解析
"""

import json

def parse_breakpoint_message(content):
    """解析BREAKPOINT消息"""
    try:
        # 解析消息格式: script_id,{json_data}
        if ',' in content:
            script_id, json_str = content.split(',', 1)
        else:
            script_id = '未知'
            json_str = content

        # 解析JSON数据
        breakpoint_data = json.loads(json_str)

        # 提取断点信息
        variables = breakpoint_data.get('variables', [])
        range_info = breakpoint_data.get('range', [])

        # 从range信息提取行号 [start_line, start_col, end_line, end_col]
        if len(range_info) >= 3:
            line_number = range_info[0]  # 开始行号
        else:
            line_number = '未知'

        result = {
            'script_id': script_id,
            'line_number': line_number,
            'variables': variables,
            'range': range_info,
            'raw_data': breakpoint_data
        }

        return result, None

    except (json.JSONDecodeError, ValueError) as e:
        return None, f"解析断点消息失败: {e}"

def test_breakpoint_parsing():
    """测试断点消息解析"""

    print("🧪 测试断点消息解析")
    print("=" * 50)

    # 模拟实际收到的断点消息 (简化版)
    test_content = """debug_test_script,{
  "variables": [
    {
      "name": "log",
      "type": "ch.qos.logback.classic.Logger",
      "value": "Logger[/test00/test0001(/test00/test0001)]"
    },
    {
      "name": "HolidayUtils",
      "type": "com.jp.med.common.util.HolidayUtils",
      "value": "{\\"holidayConfigStats\\":{\\"global\\":0,\\"hospital_zjxrmyy\\":71}}"
    },
    {
      "name": "test_mode",
      "type": "java.lang.String",
      "value": "interactive"
    },
    {
      "name": "debug",
      "type": "java.lang.String",
      "value": "true"
    }
  ],
  "range": [3, 1, 3, 13]
}"""

    result, error = parse_breakpoint_message(test_content)

    if error:
        print(f"❌ 解析失败: {error}")
        return False

    print("✅ 解析成功!")
    print(f"📜 脚本ID: {result['script_id']}")
    print(f"📍 行号: {result['line_number']}")
    print(f"📊 变量数量: {len(result['variables'])}")
    print(f"🎯 断点范围: {result['range']}")

    # 显示前几个变量
    print("\n📊 变量详情 (前3个):")
    for i, var in enumerate(result['variables'][:3]):
        name = var.get('name', '未知')
        type_name = var.get('type', '未知').split('.')[-1]  # 只显示类名
        value = var.get('value', '未知')
        if len(value) > 50:
            value = value[:47] + "..."
        print(f"   {i+1}. {name} ({type_name}) = {value}")

    # 显示断点范围详情
    if len(result['range']) >= 4:
        start_line, start_col, end_line, end_col = result['range'][:4]
        print(f"\n📍 断点位置详情:")
        print(f"   开始: 第{start_line}行第{start_col}列")
        print(f"   结束: 第{end_line}行第{end_col}列")

    print("\n✅ 断点消息解析测试通过!")
    return True

if __name__ == "__main__":
    success = test_breakpoint_parsing()
    exit(0 if success else 1)
