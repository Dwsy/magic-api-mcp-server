#!/usr/bin/env python3
"""
测试readline补全行为
"""

import readline

class TestCompleter:
    def __init__(self):
        self.commands = ['test', 'call', 'breakpoint', 'help', 'quit']

    def complete(self, text, state):
        if state == 0:
            line = readline.get_line_buffer()
            print(f"DEBUG: line='{line}', text='{text}'")
            self.matches = [cmd for cmd in self.commands if cmd.startswith(text)]
            print(f"DEBUG: matches={self.matches}")
        try:
            result = self.matches[state]
            print(f"DEBUG: returning '{result}' for state {state}")
            return result
        except IndexError:
            return None

def test_completion():
    """测试补全行为"""
    completer = TestCompleter()
    readline.set_completer(completer.complete)
    readline.set_completer_delims('\t\n')  # 只用tab和换行作为分隔符
    readline.parse_and_bind('tab: complete')

    print("测试补全功能:")
    print("输入 't' 然后按 Tab，应该补全为 'test'")
    print("输入 'c' 然后按 Tab，应该补全为 'call'")
    print("输入 'q' 然后按 Tab，应该补全为 'quit'")
    print("按 Ctrl+C 退出测试")

    try:
        while True:
            try:
                line = input("test> ")
                print(f"你输入了: '{line}'")
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\n测试结束")

if __name__ == "__main__":
    test_completion()
