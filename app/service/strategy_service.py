#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
策略选股服务 - 使用pandas-ta实现
"""

import logging
from datetime import date, datetime
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.dao.strategy_dao import StrategyDAO
from app.dao.stock_dao import StockDAO
from app.entity.stock_strategy import StockStrategy
from app.service.stock_service import StockService
from app.database import SessionLocal
import pandas_ta as ta
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StrategyService:
    """策略选股服务"""
    
    # 策略类型枚举
    STRATEGY_VOLUME_UP = "volume_up"
    STRATEGY_BREAKTHROUGH = "breakthrough"
    STRATEGY_LOW_ATR = "low_atr"
    STRATEGY_TURTLE = "turtle"
    STRATEGY_HIGH_TIGHT_FLAG = "high_tight_flag"
    STRATEGY_PARKING_APRON = "parking_apron"
    STRATEGY_KEEP_INCREASING = "keep_increasing"
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.strategy_dao = StrategyDAO(self.session)
        self.stock_dao = StockDAO(self.session)
        self.stock_service = StockService(self.session)
    
    def run_strategy(
        self, 
        strategy_type: str, 
        trade_date: date,
        codes: List[str] = None
    ) -> List[StockStrategy]:
        """运行策略选股"""
        if codes is None:
            codes = self.stock_service.get_stock_codes(trade_date)
        
        results = []
        
        for code in codes:
            try:
                hist_data = self.stock_service.get_stock_hist(code)
                if hist_data is None or hist_data.empty:
                    continue
                
                if self._check_strategy(strategy_type, hist_data):
                    entity = StockStrategy(
                        date=trade_date,
                        code=code,
                        strategy_type=strategy_type,
                        score=1.0
                    )
                    results.append(entity)
                    
            except Exception as e:
                logger.error(f"运行策略{strategy_type}筛选股票{code}失败: {e}")
        
        return results
    
    def _check_strategy(self, strategy_type: str, data: pd.DataFrame) -> bool:
        """检查是否满足策略条件"""
        if data.empty or len(data) < 20:
            return False
        
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        if strategy_type == self.STRATEGY_VOLUME_UP:
            # 放量上涨
            avg_volume = data['volume'].tail(20).mean()
            return (
                latest['volume'] > avg_volume * 1.5 and
                latest['close'] > prev['close']
            )
        
        elif strategy_type == self.STRATEGY_BREAKTHROUGH:
            # 突破平台
            high_20 = data['high'].tail(20).max()
            return latest['close'] >= high_20 * 0.98
        
        elif strategy_type == self.STRATEGY_LOW_ATR:
            # 低ATR (使用pandas-ta)
            atr = ta.atr(data['high'], data['low'], data['close'], length=14)
            if atr is not None and len(atr) > 0:
                atr_value = atr.iloc[-1]
                if not np.isnan(atr_value) and atr_value > 0:
                    atr_ratio = atr_value / latest['close']
                    return atr_ratio < 0.02
            return False
        
        elif strategy_type == self.STRATEGY_TURTLE:
            # 海龟交易
            high_20 = data['high'].tail(20).max()
            return latest['close'] >= high_20
        
        elif strategy_type == self.STRATEGY_HIGH_TIGHT_FLAG:
            # 高紧旗
            high_10 = data['high'].tail(10).max()
            low_10 = data['low'].tail(10).min()
            return (
                latest['close'] > data['close'].tail(60).mean() and
                (high_10 - low_10) / low_10 < 0.1
            )
        
        elif strategy_type == self.STRATEGY_PARKING_APRON:
            # 停机坪
            ma_20 = data['close'].tail(20).mean()
            return abs(latest['close'] - ma_20) / ma_20 < 0.03
        
        elif strategy_type == self.STRATEGY_KEEP_INCREASING:
            # 持续上涨
            recent = data['close'].tail(5)
            return all(recent.iloc[i] > recent.iloc[i-1] for i in range(1, len(recent)))
        
        return False
    
    def save_strategy_results(self, results: List[StockStrategy]) -> int:
        """保存策略结果"""
        if not results:
            return 0
        self.strategy_dao.batch_save(results)
        return len(results)
    
    def get_strategy_results(
        self, 
        strategy_type: str, 
        trade_date: date
    ) -> List[StockStrategy]:
        """获取策略结果"""
        return self.strategy_dao.find_by_type_and_date(strategy_type, trade_date)
    
    def run_all_strategies(self, trade_date: date) -> Dict[str, int]:
        """运行所有策略"""
        strategies = [
            self.STRATEGY_VOLUME_UP,
            self.STRATEGY_BREAKTHROUGH,
            self.STRATEGY_LOW_ATR,
            self.STRATEGY_TURTLE,
            self.STRATEGY_HIGH_TIGHT_FLAG,
            self.STRATEGY_PARKING_APRON,
            self.STRATEGY_KEEP_INCREASING
        ]
        
        result = {}
        for strategy_type in strategies:
            try:
                self.strategy_dao.delete_by_type_and_date(strategy_type, trade_date)
                results = self.run_strategy(strategy_type, trade_date)
                count = self.save_strategy_results(results)
                result[strategy_type] = count
            except Exception as e:
                logger.error(f"运行策略{strategy_type}失败: {e}")
                result[strategy_type] = 0
        
        return result
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()