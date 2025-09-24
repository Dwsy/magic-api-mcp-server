#!/usr/bin/env python3
"""
测试readline刷新功能
"""

import sys
import time

def test_readline_refresh():
    """测试readline刷新功能"""

    print("🧪 测试readline刷新功能")
    print("=" * 50)

    # 测试刷新逻辑
    print("1️⃣ 测试基础刷新功能")

    # 模拟输出消息
    messages = [
        "📝 [日志] 用户登录消息",
        "🔴 [断点] 脚本在第5行暂停",
        "📊 变量: name = test",
        "💡 resume/step/quit"
    ]

    for i, msg in enumerate(messages, 1):
        print(f"消息 {i}: {msg}")

        # 测试刷新逻辑
        try:
            # 刷新stdout缓冲区
            sys.stdout.flush()

            # 强制重绘readline输入行
            import readline
            readline.redisplay()
            print("   ✅ readline.redisplay() 成功")
        except Exception as e:
            print(f"   ❌ readline.redisplay() 失败: {e}")
            # readline不可用时至少刷新stdout
            try:
                sys.stdout.flush()
                print("   ✅ sys.stdout.flush() 成功")
            except:
                print("   ❌ 刷新失败")

        time.sleep(0.2)  # 短暂延迟

    print("\n2️⃣ 测试性能")
    # 测试刷新性能
    start_time = time.time()
    for _ in range(100):
        sys.stdout.flush()
        try:
            import readline
            readline.redisplay()
        except:
            pass
    end_time = time.time()

    print(f"执行时间: {end_time - start_time:.4f}秒")
    print(f"平均每次刷新: {(end_time - start_time) / iterations:.6f}秒")
    print("✅ readline刷新测试完成")

if __name__ == "__main__":
    test_readline_refresh()
