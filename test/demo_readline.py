#!/usr/bin/env python3
"""
演示readline功能和路径自动补全的脚本
用于测试方向键导航、Tab补全和路径自动补全功能
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
import rlcompleter
import sys


class DemoCompleter:
    """演示用补全器"""

    def __init__(self):
        self.commands = ['test', 'call', 'breakpoint', 'help', 'quit']
        self.http_methods = ['GET', 'POST', 'PUT', 'DELETE']
        self.paths = ['/api/test', '/api/user', '/api/data', '/debug/test']

    def complete(self, text, state):
        if state == 0:
            line = readline.get_line_buffer()
            self.matches = self._get_matches(line, text)
        try:
            return self.matches[state]
        except IndexError:
            return None

    def _get_matches(self, line, text):
        matches = []
        if not line.strip() or ' ' not in line:
            matches.extend([cmd for cmd in self.commands if cmd.startswith(text)])
        else:
            parts = line.split()
            command = parts[0].lower()

            if command == 'test' and len(parts) == 2:
                matches.extend([path for path in self.paths if path.startswith(text)])
            elif command == 'call' and len(parts) >= 2:
                current_part_index = len(parts) - 1
                if current_part_index == 1:
                    matches.extend([method for method in self.http_methods if method.startswith(text.upper())])
                elif current_part_index == 2:
                    matches.extend([path for path in self.paths if path.startswith(text)])

        return matches


def preprocess_command(command_line):
    """预处理命令行，自动为test命令的路径添加前缀'/'"""
    if not command_line.strip():
        return command_line

    parts = command_line.split()
    if len(parts) >= 2 and parts[0].lower() == 'test':
        path_arg = parts[1]
        if not path_arg.isdigit() and ',' not in path_arg and not path_arg.startswith('/'):
            parts[1] = '/' + path_arg
            return ' '.join(parts)

    return command_line


def setup_readline():
    """设置readline"""
    completer = DemoCompleter()
    readline.set_completer(completer.complete)
    readline.set_completer_delims(' \t\n')
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set enable-keypad on')


def main():
    print("🔧 Readline功能演示")
    print("=" * 30)
    print("功能演示:")
    print("• ↑↓方向键: 浏览命令历史")
    print("• ←→方向键: 编辑当前命令")
    print("• Tab键: 自动补全")
    print("• test命令路径自动添加'/'前缀")
    print("\n尝试以下命令:")
    print("  test api/test")
    print("  call GET api")
    print("  help")
    print("  quit")
    print("\n输入 'quit' 退出演示")
    print("-" * 30)

    setup_readline()
    history = []

    while True:
        try:
            command = input("demo> ").strip()
            if not command:
                continue

            # 预处理命令
            original_command = command
            command = preprocess_command(command)

            if original_command != command:
                print(f"📝 自动补全: {original_command} -> {command}")

            history.append(command)

            if command.lower() == 'quit':
                print("👋 演示结束")
                break
            elif command.lower() == 'help':
                print("可用命令:")
                print("  test <path>     - 测试路径自动补全")
                print("  call <method> <path> - 测试方法和路径补全")
                print("  history         - 显示命令历史")
                print("  quit            - 退出演示")
            elif command.lower() == 'history':
                print("命令历史:")
                for i, cmd in enumerate(history[-10:], 1):  # 显示最近10条
                    print(f"  {i}: {cmd}")
            else:
                print(f"执行命令: {command}")

        except KeyboardInterrupt:
            print("\n👋 演示被中断")
            break
        except EOFError:
            print("\n👋 演示结束")
            break


if __name__ == "__main__":
    main()
