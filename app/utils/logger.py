#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全局日志工具 - 基于 loguru 实现，支持颜色输出和文件跳转
"""

import sys
from loguru import logger


def setup_logger():
    """
    配置 loguru 日志记录器
    
    日志格式: 时间 级别 模块 文件:行号 - 消息
    """
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器，带颜色和文件跳转支持
    # 格式说明: 时间 级别 模块 文件路径:行号 - 消息
    # 使用 {file.path}:{line} 提供完整路径，支持 IDE 点击跳转
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
               "<level>{level: <8}</level> "
               "<cyan>{name}</cyan> "
               "<yellow>{file.path}:{line}</yellow> "
               "- <level>{message}</level>",
        level="DEBUG",
        colorize=True,
    )
    
    return logger


# 初始化 logger
setup_logger()


def get_logger(name: str = "instock"):
    """
    获取日志记录器
    
    Args:
        name: 模块名称
        
    Returns:
        配置好的 logger 实例
    """
    return logger.bind(name=name)


def debug(msg: str, *args, **kwargs):
    """输出 DEBUG 级别日志"""
    logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """输出 INFO 级别日志（绿色）"""
    logger.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """输出 WARNING 级别日志（黄色）"""
    logger.warning(msg, *args, **kwargs)


# 别名
warn = warning


def error(msg: str, *args, **kwargs):
    """输出 ERROR 级别日志（红色）"""
    logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """输出 CRITICAL 级别日志（红底白字）"""
    logger.critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    """输出异常日志（包含堆栈信息）"""
    logger.exception(msg, *args, **kwargs)