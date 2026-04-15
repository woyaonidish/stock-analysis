#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller层模块
"""

from app.controller.stock_controller import router as stock_router
from app.controller.index_controller import router as index_router
from app.controller.financial_controller import router as financial_router
from app.controller.indicator_controller import router as indicator_router
from app.controller.pattern_controller import router as pattern_router
from app.controller.strategy_controller import router as strategy_router
from app.controller.backtest_controller import router as backtest_router
from app.controller.attention_controller import router as attention_router
from app.controller.hist_controller import router as hist_router

__all__ = [
    'stock_router',
    'index_router',
    'financial_router',
    'indicator_router',
    'pattern_router',
    'strategy_router',
    'backtest_router',
    'attention_router',
    'hist_router'
]
