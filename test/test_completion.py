#!/usr/bin/env python3
"""
测试readline补全行为
"""

try:
    import readline
except ImportError:
    # Windows 系统使用 pyreadline3
    try:
        import pyreadline3 as readline
    except ImportError:
        # 如果都没有 readline 功能，创建一个兼容层
        class MockReadline:
            def get_line_buffer(self): return ""
            def redisplay(self): pass
            def set_completer(self, completer): pass
            def set_completer_delims(self, delims): pass
            def parse_and_bind(self, binding): pass
            def read_history_file(self, filename): pass
            def write_history_file(self, filename): pass
        readline = MockReadline()

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
