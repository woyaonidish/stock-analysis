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
from app.dao.other_dao import PatternDAO
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
        self.pattern_dao = PatternDAO(self.session)
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
        """
        识别并保存股票形态
        
        Args:
            code: 股票代码
            trade_date: 交易日期
            
        Returns:
            保存的形态实体
        """
        try:
            hist_data = self.stock_service.get_stock_hist(code)
            if hist_data is None or hist_data.empty:
                return None
            
            patterns = self.recognize_patterns(hist_data)
            if not patterns:
                return None
            
            # 创建实体，映射形态字段
            entity = StockPattern(
                date=trade_date,
                code=code,
            )
            
            # 设置各个形态字段
            for pattern_name, value in patterns.items():
                if hasattr(StockPattern, pattern_name):
                    setattr(entity, pattern_name, value)
            
            # 保存到数据库
            self.pattern_dao.save(entity)
            logger.info(f"保存股票 {code} 形态数据成功")
            
            return entity
            
        except Exception as e:
            logger.error(f"识别股票{code}形态失败: {e}")
            return None
    
    def recognize_and_save_all(self, trade_date: date) -> int:
        """
        批量识别并保存所有股票形态
        
        Args:
            trade_date: 交易日期
            
        Returns:
            保存记录数
        """
        try:
            # 获取当日股票列表
            stocks = self.stock_dao.find_by_date(trade_date)
            if not stocks:
                logger.warning(f"未找到 {trade_date} 的股票数据")
                return 0
            
            entities = []
            for stock in stocks:
                try:
                    hist_data = self.stock_service.get_stock_hist(stock.code)
                    if hist_data is None or hist_data.empty:
                        continue
                    
                    patterns = self.recognize_patterns(hist_data)
                    if not patterns:
                        continue
                    
                    entity = StockPattern(
                        date=trade_date,
                        code=stock.code,
                    )
                    
                    for pattern_name, value in patterns.items():
                        if hasattr(StockPattern, pattern_name):
                            setattr(entity, pattern_name, value)
                    
                    entities.append(entity)
                    
                except Exception as e:
                    logger.warning(f"识别股票 {stock.code} 形态失败: {e}")
                    continue
            
            # 批量保存
            if entities:
                # 先删除旧数据
                self.pattern_dao.delete_by_date(trade_date)
                self.pattern_dao.save_all(entities)
                logger.info(f"批量保存形态数据成功，共 {len(entities)} 条")
            
            return len(entities)
            
        except Exception as e:
            logger.error(f"批量识别形态失败: {e}")
            return 0
    
    def get_patterns(self, code: str, trade_date: date) -> Optional[StockPattern]:
        """
        获取股票形态
        
        Args:
            code: 股票代码
            trade_date: 交易日期
            
        Returns:
            形态实体
        """
        results = self.pattern_dao.find_by_code(code, trade_date)
        return results[0] if results else None
    
    def get_all_patterns(self, trade_date: date) -> List[StockPattern]:
        """
        获取指定日期的所有股票形态
        
        Args:
            trade_date: 交易日期
            
        Returns:
            形态列表
        """
        return self.pattern_dao.find_by_date(trade_date)
    
    def get_patterns_by_type(self, pattern_name: str, trade_date: date) -> List[StockPattern]:
        """
        根据形态类型查询
        
        Args:
            pattern_name: 形态名称
            trade_date: 交易日期
            
        Returns:
            出现该形态的股票列表
        """
        return self.pattern_dao.find_by_pattern(pattern_name, trade_date)
    
    def get_buy_signals(self, trade_date: date) -> List[Dict]:
        """
        获取买入信号（看涨形态）
        
        Args:
            trade_date: 交易日期
            
        Returns:
            买入信号列表
        """
        patterns = self.get_all_patterns(trade_date)
        buy_signals = []
        
        # 看涨形态名称列表
        bullish_patterns = [
            'hammer', 'inverted_hammer', 'engulfing_pattern', 
            'morning_star', 'morning_doji_star', 'piercing_pattern',
            'three_white_soldiers', ' abandoned_baby', 'dragonfly_doji'
        ]
        
        for pattern in patterns:
            for bp in bullish_patterns:
                value = getattr(pattern, bp, 0)
                if value > 0:  # 正值表示看涨
                    buy_signals.append({
                        'code': pattern.code,
                        'date': str(pattern.date),
                        'pattern': bp,
                        'signal': 'buy'
                    })
                    break  # 只记录第一个看涨形态
        
        return buy_signals
    
    def get_sell_signals(self, trade_date: date) -> List[Dict]:
        """
        获取卖出信号（看跌形态）
        
        Args:
            trade_date: 交易日期
            
        Returns:
            卖出信号列表
        """
        patterns = self.get_all_patterns(trade_date)
        sell_signals = []
        
        # 看跌形态名称列表
        bearish_patterns = [
            'hanging_man', 'shooting_star', 'dark_cloud_cover',
            'evening_star', 'evening_doji_star', 'three_black_crows',
            'gravestone_doji', 'tow_crows'
        ]
        
        for pattern in patterns:
            for bp in bearish_patterns:
                value = getattr(pattern, bp, 0)
                if value < 0:  # 负值表示看跌
                    sell_signals.append({
                        'code': pattern.code,
                        'date': str(pattern.date),
                        'pattern': bp,
                        'signal': 'sell'
                    })
                    break
        
        return sell_signals
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()