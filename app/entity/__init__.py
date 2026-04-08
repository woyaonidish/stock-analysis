#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实体类模块
"""

from app.entity.stock_spot import StockSpot, StockAttention
from app.entity.etf_spot import ETFSpot
from app.entity.stock_indicator import StockIndicator
from app.entity.stock_pattern import StockPattern
from app.entity.stock_strategy import (
    StockStrategyBase, StockStrategyEnter, StockStrategyKeepIncreasing,
    StockStrategyParkingApron, StockStrategyBacktraceMA250,
    StockStrategyBreakthroughPlatform, StockStrategyLowBacktraceIncrease,
    StockStrategyTurtleTrade, StockStrategyHighTightFlag,
    StockStrategyClimaxLimitdown, StockStrategyLowATR,
    STRATEGY_TABLES
)
from app.entity.fund_flow import StockFundFlow, StockFundFlowIndustry, StockFundFlowConcept
from app.entity.stock_selection import StockSelection
from app.entity.stock_other import (
    StockBonus, StockLhb, StockBlocktrade, StockBacktestData, StockHistData
)

__all__ = [
    'StockSpot', 'StockAttention',
    'ETFSpot',
    'StockIndicator',
    'StockPattern',
    'StockStrategyBase', 'StockStrategyEnter', 'StockStrategyKeepIncreasing',
    'StockStrategyParkingApron', 'StockStrategyBacktraceMA250',
    'StockStrategyBreakthroughPlatform', 'StockStrategyLowBacktraceIncrease',
    'StockStrategyTurtleTrade', 'StockStrategyHighTightFlag',
    'StockStrategyClimaxLimitdown', 'StockStrategyLowATR', 'STRATEGY_TABLES',
    'StockFundFlow', 'StockFundFlowIndustry', 'StockFundFlowConcept',
    'StockSelection',
    'StockBonus', 'StockLhb', 'StockBlocktrade', 'StockBacktestData', 'StockHistData'
]
