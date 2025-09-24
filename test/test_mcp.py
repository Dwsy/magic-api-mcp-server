#!/usr/bin/env python3
"""测试MCP模块导入"""

try:
    from magicapi_mcp.magicapi_assistant import mcp
    print("✅ 成功导入MCP对象")
    print(f"✅ MCP对象类型: {type(mcp)}")
    print("✅ 测试完成")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()