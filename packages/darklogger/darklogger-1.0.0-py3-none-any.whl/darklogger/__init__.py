"""
DarkLogger - 基于loguru的增强日志记录器

一个功能强大且易于使用的Python日志库，支持多实例、ID绑定和控制台输出控制。

基本用法:
    from darklogger import DarkLogger
    
    # 创建日志实例
    logger = DarkLogger("user123")
    
    # 记录日志
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    # 控制控制台输出
    logger.set_console_output(False)  # 关闭控制台输出
    logger.info("这条消息只会保存到文件中")
"""

from .darklogger import DarkLogger

__version__ = "1.0.0"
__author__ = "jiruo"  # 请改为您的真实姓名
__email__ = "jiruo@example.com"  # 请改为您的真实邮箱

__all__ = ["DarkLogger"]
