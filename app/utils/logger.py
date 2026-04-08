#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全局日志工具 - 支持颜色输出的日志系统
"""

import logging
import sys
from typing import Optional


# ANSI 颜色代码
class LogColors:
    """日志颜色配置"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 背景色
    BG_RED = "\033[41m"
    BG_YELLOW = "\033[43m"


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # 日志级别对应的颜色
    LEVEL_COLORS = {
        logging.DEBUG: LogColors.CYAN,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.BG_RED + LogColors.WHITE,
    }
    
    # 日志级别对应的名称
    LEVEL_NAMES = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARN",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 获取级别对应的颜色
        color = self.LEVEL_COLORS.get(record.levelno, LogColors.WHITE)
        level_name = self.LEVEL_NAMES.get(record.levelno, record.levelname)
        
        # 构建带颜色的级别标识
        colored_level = f"{color}{LogColors.BOLD}[{level_name}]{LogColors.RESET}"
        
        # 构建时间戳
        timestamp = self.formatTime(record, self.datefmt)
        
        # 构建模块名
        module = f"{LogColors.BLUE}{record.name}{LogColors.RESET}"
        
        # 构建文件位置（文件名:行号）
        location = f"{LogColors.MAGENTA}{record.filename}:{record.lineno}{LogColors.RESET}"
        
        # 构建消息
        message = record.getMessage()
        
        # 组合格式: 时间 级别 模块 文件:行号 - 消息
        formatted = f"{timestamp} {colored_level} {module} {location} - {message}"
        
        # 添加异常信息
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
        
        return formatted


# 全局 logger 实例
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "instock") -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    global _logger
    
    if _logger is not None:
        # 返回带有指定名称的子 logger
        if name != "instock":
            return _logger.getChild(name)
        return _logger
    
    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 移除已有的处理器
    logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 设置带颜色的格式化器
    colored_formatter = ColoredFormatter(
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(colored_formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    # 防止日志传播到根 logger
    logger.propagate = False
    
    _logger = logger
    return logger


def init_logger(level: int = logging.DEBUG) -> logging.Logger:
    """
    初始化全局日志记录器
    
    Args:
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    global _logger
    _logger = None  # 重置以便重新初始化
    
    logger = get_logger()
    logger.setLevel(level)
    
    return logger


# 便捷方法
def debug(msg: str, *args, **kwargs):
    """输出 DEBUG 级别日志"""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """输出 INFO 级别日志（绿色）"""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """输出 WARNING 级别日志（黄色）"""
    get_logger().warning(msg, *args, **kwargs)


# 别名
warn = warning


def error(msg: str, *args, **kwargs):
    """输出 ERROR 级别日志（红色）"""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """输出 CRITICAL 级别日志（红底白字）"""
    get_logger().critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    """输出异常日志"""
    get_logger().exception(msg, *args, **kwargs)


# 初始化默认 logger
init_logger()