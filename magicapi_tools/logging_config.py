"""MagicAPI 工具日志配置模块。"""

import logging

# 配置日志系统
def _setup_logging():
    """设置日志配置"""
    # 创建根logger
    root_logger = logging.getLogger('magicapi_tools')
    root_logger.setLevel(logging.DEBUG)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # 避免重复添加处理器
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    return root_logger

# 初始化日志系统
_root_logger = _setup_logging()

def get_logger(module_name: str) -> logging.Logger:
    """获取指定模块的logger"""
    return _root_logger.getChild(module_name)
