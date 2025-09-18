# DarkLogger

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DarkLogger 是一个基于 [loguru](https://github.com/Delgan/loguru) 的增强日志记录器，提供了多实例支持、ID绑定、灵活的控制台输出控制和自动日志清理功能。

## 主要特性

- ✨ **多实例支持**: 可以创建多个独立的日志实例，每个实例都有自己的ID标识
- 🎯 **ID绑定**: 每条日志都会包含实例ID，便于追踪和调试
- 🖥️ **控制台输出控制**: 可以灵活控制是否在控制台显示日志
- 📁 **自动文件管理**: 按日期自动轮换日志文件
- 🗑️ **自动日志清理**: 自动删除30天前的日志文件（新功能 v1.1.0+）
- 🔍 **详细异常信息**: 支持记录完整的异常堆栈信息
- 📍 **调用位置追踪**: 自动记录日志调用的文件、函数和行号

## 安装

使用 pip 安装：

```bash
pip install darklogger
```

## 快速开始

### 基本使用

```python
from darklogger import DarkLogger

# 创建日志实例（自动保留30天的日志）
logger = DarkLogger("user123")

# 记录不同级别的日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志") 
logger.error("这是一条错误日志")
logger.critical("这是一条严重错误日志")
```

### 多实例使用

```python
from darklogger import DarkLogger

# 创建两个不同ID的日志实例
user_logger = DarkLogger("user123")
admin_logger = DarkLogger("admin456")

# 每个实例的日志都会包含对应的ID
user_logger.info("用户登录成功")
admin_logger.warning("管理员权限变更")
```

### 控制台输出控制

```python
from darklogger import DarkLogger

logger = DarkLogger("app")

# 默认情况下会在控制台显示日志
logger.info("这条消息会显示在控制台")

# 关闭控制台输出
logger.set_console_output(False)
logger.info("这条消息只会保存到文件中")

# 重新开启控制台输出
logger.set_console_output(True)
logger.info("这条消息又会显示在控制台了")

# 临时控制单条日志的控制台输出
logger.info("只保存到文件", show_console=False)
logger.error("只在控制台显示", show_console=True)
```

### 异常处理

```python
from darklogger import DarkLogger

logger = DarkLogger("exception_test")

try:
    result = 10 / 0
except Exception as e:
    # 记录异常（包含完整堆栈信息）
    logger.exception(f"计算错误: {str(e)}")
    
    # 或者使用自定义异常记录
    logger.log_exception(message=f"自定义异常记录: {str(e)}")
    
    # 不在控制台显示异常详情
    logger.exception(f"静默异常: {str(e)}", show_console=False)
```

## 日志输出格式

日志会自动记录以下信息：

- ⏰ **时间戳**: 精确到毫秒
- 📊 **日志级别**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- 📂 **调用位置**: 文件名:函数名:行号
- 🆔 **实例ID**: 日志实例的唯一标识
- 📝 **日志内容**: 具体的日志消息

示例输出：
```
2025-09-18 10:30:45.123 | INFO     | main.py:login:25 | ID: user123 - 用户登录成功
2025-09-18 10:30:46.456 | WARNING  | admin.py:update_permissions:67 | ID: admin456 - 管理员权限变更
```

## 文件管理

- 日志文件保存在 `log_/` 目录下
- 按日期命名：`YYYY-MM-DD.log`
- 每天午夜自动轮换到新文件
- 自动创建目录（如果不存在）

## API 参考

### DarkLogger(id_value)

创建一个新的日志实例。

**参数:**
- `id_value` (str): 日志实例的唯一标识符

**日志保留策略:**
- 自动保留30天的日志文件
- 超过30天的日志文件会被自动删除

### 日志方法

- `logger.debug(message, show_console=None)`: 调试日志
- `logger.info(message, show_console=None)`: 信息日志  
- `logger.warning(message, show_console=None)`: 警告日志
- `logger.error(message, show_console=None)`: 错误日志
- `logger.critical(message, show_console=None)`: 严重错误日志
- `logger.exception(message, exc_info=True, show_console=None)`: 异常日志
- `logger.log_exception(message, show_console=None, ...)`: 自定义异常日志

### 控制方法

- `logger.set_console_output(enabled)`: 控制控制台输出开关

**参数:**
- `show_console` (bool, optional): 控制单条日志是否在控制台显示
- `enabled` (bool): True 启用控制台输出，False 禁用

## 系统要求

- Python 3.7+
- loguru >= 0.6.0

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issues 和 Pull Requests！

## 更新日志

### v1.1.0
- 🆕 新增自动日志清理功能
- 🆕 自动删除30天前的日志文件
- 📚 更新文档和使用示例
- 🐛 优化日志文件管理

### v1.0.0
- 初始版本发布
- 支持多实例日志记录
- 支持ID绑定和控制台输出控制
- 支持异常详细记录
- 支持调用位置自动追踪
