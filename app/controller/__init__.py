#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller层模块
"""

from app.controller.stock_controller import router as stock_router
from app.controller.indicator_controller import router as indicator_router
from app.controller.strategy_controller import router as strategy_router
from app.controller.backtest_controller import router as backtest_router

__all__ = [
    'stock_router',
    'indicator_router',
    'strategy_router',
    'backtest_router'
]
