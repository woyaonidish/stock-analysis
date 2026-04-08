#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交易时间工具
"""

from datetime import datetime, time, date
from typing import Optional


def is_trading_time(dt: datetime = None) -> bool:
    """
    判断是否为交易时间
    
    Args:
        dt: 日期时间，默认当前时间
        
    Returns:
        是否为交易时间
    """
    if dt is None:
        dt = datetime.now()
    
    # 判断是否为工作日
    if dt.weekday() >= 5:
        return False
    
    current_time = dt.time()
    
    # 上午交易时间: 9:30 - 11:30
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    
    # 下午交易时间: 13:00 - 15:00
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    return (morning_start <= current_time <= morning_end) or \
           (afternoon_start <= current_time <= afternoon_end)


def get_next_trade_date(current_date: date = None) -> Optional[date]:
    """
    获取下一个交易日
    
    Args:
        current_date: 当前日期
        
    Returns:
        下一个交易日(简化版，不考虑节假日)
    """
    if current_date is None:
        current_date = date.today()
    
    next_date = current_date
    for _ in range(7):  # 最多查找7天
        next_date = date.fromordinal(next_date.toordinal() + 1)
        if next_date.weekday() < 5:  # 周一到周五
            return next_date
    
    return None


def is_trade_date(dt: date) -> bool:
    """
    判断是否为交易日(简化版，不考虑节假日)
    
    Args:
        dt: 日期
        
    Returns:
        是否为交易日
    """
    return dt.weekday() < 5
