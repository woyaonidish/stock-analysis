#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票策略选股实体类
"""

from datetime import date
from sqlalchemy import Column, String, Float, Date
from app.database import Base


class StockStrategyBase(Base):
    """策略选股基类 - 不映射到具体表"""
    __abstract__ = True
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')


class StockStrategyEnter(StockStrategyBase):
    """放量上涨策略"""
    __tablename__ = 'cn_stock_strategy_enter'


class StockStrategyKeepIncreasing(StockStrategyBase):
    """均线多头策略"""
    __tablename__ = 'cn_stock_strategy_keep_increasing'


class StockStrategyParkingApron(StockStrategyBase):
    """停机坪策略"""
    __tablename__ = 'cn_stock_strategy_parking_apron'


class StockStrategyBacktraceMA250(StockStrategyBase):
    """回踩年线策略"""
    __tablename__ = 'cn_stock_strategy_backtrace_ma250'


class StockStrategyBreakthroughPlatform(StockStrategyBase):
    """突破平台策略"""
    __tablename__ = 'cn_stock_strategy_breakthrough_platform'


class StockStrategyLowBacktraceIncrease(StockStrategyBase):
    """无大幅回撤策略"""
    __tablename__ = 'cn_stock_strategy_low_backtrace_increase'


class StockStrategyTurtleTrade(StockStrategyBase):
    """海龟交易策略"""
    __tablename__ = 'cn_stock_strategy_turtle_trade'


class StockStrategyHighTightFlag(StockStrategyBase):
    """高而窄的旗形策略"""
    __tablename__ = 'cn_stock_strategy_high_tight_flag'


class StockStrategyClimaxLimitdown(StockStrategyBase):
    """放量跌停策略"""
    __tablename__ = 'cn_stock_strategy_climax_limitdown'


class StockStrategyLowATR(StockStrategyBase):
    """低ATR成长策略"""
    __tablename__ = 'cn_stock_strategy_low_atr'


# 策略类型映射
STRATEGY_TABLES = {
    'enter': StockStrategyEnter,
    'keep_increasing': StockStrategyKeepIncreasing,
    'parking_apron': StockStrategyParkingApron,
    'backtrace_ma250': StockStrategyBacktraceMA250,
    'breakthrough_platform': StockStrategyBreakthroughPlatform,
    'low_backtrace_increase': StockStrategyLowBacktraceIncrease,
    'turtle_trade': StockStrategyTurtleTrade,
    'high_tight_flag': StockStrategyHighTightFlag,
    'climax_limitdown': StockStrategyClimaxLimitdown,
    'low_atr': StockStrategyLowATR,
}
