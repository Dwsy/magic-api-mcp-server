#!/usr/bin/env python3
\"\"\"优雅的MCP服务器启动器 - 确保正确的资源清理\"\"\"

import signal
import sys
import atexit
from magicapi_mcp.magicapi_assistant import create_app, _cleanup_resources, setup_signal_handlers, cleanup_on_exit

def main():
    # 设置信号处理器
    setup_signal_handlers()
    
    # 注册退出时的清理函数
    atexit.register(cleanup_on_exit)
    
    # 创建应用
    mcp = create_app()
    
    try:
        # 使用stdio传输（FastMCP默认）
        mcp.run(transport=\"stdio\")
    except KeyboardInterrupt:
        print('\\n正在关闭服务器...')
        _cleanup_resources()
        print(\"服务器已关闭\")
        sys.exit(0)
    except Exception as e:
        print(f\"服务器运行出错: {e}\")
        _cleanup_resources()
        sys.exit(1)

if __name__ == \"__main__\":
    main()