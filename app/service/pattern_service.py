#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
形态识别服务 - 使用纯Python实现
"""

from datetime import date, datetime
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.dao.stock_dao import StockDAO
from app.entity.stock_pattern import StockPattern
from app.service.stock_service import StockService
from app.database import SessionLocal
from app.calculator.pattern_recognizer import PatternRecognizer
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PatternService:
    """形态识别服务"""
    
    # K线形态枚举
    PATTERN_DOJI = "doji"
    PATTERN_HAMMER = "hammer"
    PATTERN_INVERTED_HAMMER = "inverted_hammer"
    PATTERN_BULLISH_ENGULFING = "engulfing_pattern"
    PATTERN_BEARISH_ENGULFING = "engulfing_pattern"
    PATTERN_MORNING_STAR = "morning_star"
    PATTERN_EVENING_STAR = "evening_star"
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.stock_dao = StockDAO(self.session)
        self.stock_service = StockService(self.session)
    
    def recognize_patterns(self, data: pd.DataFrame) -> Dict[str, int]:
        """
        识别K线形态
        
        Args:
            data: 股票历史数据DataFrame
            
        Returns:
            识别到的形态字典 (正值=看涨，负值=看跌)
        """
        if data is None or data.empty:
            return {}
        
        # 使用纯Python形态识别器
        result_df = PatternRecognizer.recognize_all(data)
        if result_df is None or result_df.empty:
            return {}
        
        # 取最新一条数据
        latest = result_df.iloc[-1]
        
        patterns = {}
        pattern_names = PatternRecognizer.get_pattern_names()
        
        for pattern_name in pattern_names:
            if pattern_name in latest.index:
                value = int(latest[pattern_name])
                if value != 0:
                    patterns[pattern_name] = value
        
        return patterns
    
    def recognize_and_save(self, code: str, trade_date: date) -> Optional[StockPattern]:
        """识别并保存股票形态"""
        try:
            hist_data = self.stock_service.get_stock_hist(code)
            if hist_data is None or hist_data.empty:
                return None
            
            patterns = self.recognize_patterns(hist_data)
            if not patterns:
                return None
            
            entity = StockPattern(
                date=trade_date,
                code=code,
                patterns=patterns,
                pattern_count=len(patterns)
            )
            
            return entity
            
        except Exception as e:
            logger.error(f"识别股票{code}形态失败: {e}")
            return None
    
    def get_patterns(self, code: str, trade_date: date) -> Optional[StockPattern]:
        """获取股票形态"""
        return None
    
    def get_all_patterns(self, trade_date: date) -> List[StockPattern]:
        """获取指定日期的所有股票形态"""
        return []
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()