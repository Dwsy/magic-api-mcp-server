#!/usr/bin/env python3
"""
调试补全问题的脚本
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

class DebugCompleter:
    def __init__(self):
        self.commands = ['test', 'call', 'breakpoint', 'list_bp', 'help', 'quit']

    def complete(self, text, state):
        print(f"\nDEBUG: complete called with text='{text}', state={state}")

        if state == 0:
            # 第一次调用，生成补全列表
            line = readline.get_line_buffer()
            print(f"DEBUG: line_buffer='{line}'")
            self.matches = self._get_matches(line, text)
            print(f"DEBUG: matches={self.matches}")

        try:
            result = self.matches[state]
            print(f"DEBUG: returning '{result}' for state {state}")
            return result
        except IndexError:
            print(f"DEBUG: no more matches for state {state}")
            return None

    def _get_matches(self, line, text):
        """获取匹配的补全项"""
        matches = []

        # 如果是空行或只输入了部分命令
        if not line.strip() or ' ' not in line:
            # 补全命令
            matches.extend([cmd for cmd in self.commands if cmd.startswith(text)])
            print(f"DEBUG: command completion for '{text}': {matches}")
        else:
            print(f"DEBUG: parameter completion not implemented")

        return matches

def test_completion():
    """测试补全问题"""
    completer = DebugCompleter()
    readline.set_completer(completer.complete)
    readline.set_completer_delims('\t\n')  # 只用tab和换行符作为分隔符
    readline.parse_and_bind('tab: complete')

    print("测试补全问题:")
    print("输入单个字符如 'l' 然后按 Tab，应该看到补全调试信息")
    print("如果看到 'llist_bp' 这样的问题，就是我们要修复的bug")
    print("按 Ctrl+C 退出")

    try:
        while True:
            try:
                line = input("debug> ")
                print(f"最终输入: '{line}'")
                print(f"  长度: {len(line)}")
                print(f"  字符: {[c for c in line]}")
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\n退出测试")

if __name__ == "__main__":
    test_completion()
