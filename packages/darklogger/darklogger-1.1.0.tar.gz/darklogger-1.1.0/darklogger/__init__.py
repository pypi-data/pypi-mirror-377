"""
DarkLogger - 基于loguru的增强日志记录器

一个功能强大且易于使用的Python日志库，支持多实例、ID绑定、控制台输出控制和自动日志清理。

主要特性:
- 🎯 多实例支持：每个实例独立的ID标识
- 🖥️ 控制台输出控制：可灵活控制是否在控制台显示
- 📅 自动日志轮换：每天午夜自动创建新日志文件
- 🗑️ 自动清理：自动删除30天前的日志文件
- 🔍 详细异常记录：支持完整堆栈跟踪
- 📍 调用位置追踪：自动记录日志调用的文件、函数和行号

基本用法:
    from darklogger import DarkLogger
    
    # 创建日志实例（自动保留30天）
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

__version__ = "1.1.0"
__author__ = "jiruo"  # 请改为您的真实姓名
# __email__ = "jiruo@example.com"  # 请改为您的真实邮箱

__all__ = ["DarkLogger"]
