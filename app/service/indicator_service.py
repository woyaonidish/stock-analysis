#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指标计算服务 - 使用pandas-ta实现
"""

from datetime import date, datetime
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
import concurrent.futures
from sqlalchemy.orm import Session

from app.dao.indicator_dao import IndicatorDAO
from app.dao.stock_dao import StockDAO
from app.entity.stock_indicator import StockIndicator
from app.service.stock_service import StockService
from app.database import SessionLocal
import pandas_ta as ta
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IndicatorService:
    """指标计算服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.indicator_dao = IndicatorDAO(self.session)
        self.stock_dao = StockDAO(self.session)
        self.stock_service = StockService(self.session)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: 股票历史数据DataFrame
            
        Returns:
            包含技术指标的DataFrame
        """
        if data is None or data.empty:
            return pd.DataFrame()
        
        result = data.copy()
        
        # MACD
        macd = ta.macd(result['close'], fast=12, slow=26, signal=9)
        if macd is not None:
            result['macd'] = macd['MACD_12_26_9'].fillna(0)
            result['macds'] = macd['MACDs_12_26_9'].fillna(0)
            result['macdh'] = macd['MACDh_12_26_9'].fillna(0)
        else:
            result['macd'] = 0
            result['macds'] = 0
            result['macdh'] = 0
        
        # KDJ
        stoch = ta.stoch(result['high'], result['low'], result['close'], k=9, d=5, smooth_k=5)
        if stoch is not None:
            result['kdjk'] = stoch['STOCHk_9_5_5'].fillna(0)
            result['kdjd'] = stoch['STOCHd_9_5_5'].fillna(0)
            result['kdjj'] = 3 * result['kdjk'] - 2 * result['kdjd']
        else:
            result['kdjk'] = 0
            result['kdjd'] = 0
            result['kdjj'] = 0
        
        # BOLL
        bbands = ta.bbands(result['close'], length=20, std=2)
        if bbands is not None:
            result['boll_ub'] = bbands['BBU_20_2.0'].fillna(0)
            result['boll'] = bbands['BBM_20_2.0'].fillna(0)
            result['boll_lb'] = bbands['BBL_20_2.0'].fillna(0)
        else:
            result['boll_ub'] = 0
            result['boll'] = 0
            result['boll_lb'] = 0
        
        # RSI
        result['rsi'] = ta.rsi(result['close'], length=14).fillna(0)
        result['rsi_6'] = ta.rsi(result['close'], length=6).fillna(0)
        result['rsi_12'] = ta.rsi(result['close'], length=12).fillna(0)
        result['rsi_24'] = ta.rsi(result['close'], length=24).fillna(0)
        
        # ATR
        result['atr'] = ta.atr(result['high'], result['low'], result['close'], length=14).fillna(0)
        
        # CCI
        result['cci'] = ta.cci(result['high'], result['low'], result['close'], length=14).fillna(0)
        
        # WR
        result['wr_6'] = ta.willr(result['high'], result['low'], result['close'], length=6).fillna(0)
        result['wr_10'] = ta.willr(result['high'], result['low'], result['close'], length=10).fillna(0)
        
        # MA
        result['ma5'] = ta.sma(result['close'], length=5).fillna(0)
        result['ma10'] = ta.sma(result['close'], length=10).fillna(0)
        result['ma20'] = ta.sma(result['close'], length=20).fillna(0)
        result['ma60'] = ta.sma(result['close'], length=60).fillna(0)
        
        # TRIX
        result['trix'] = self._calculate_trix(result['close'], period=12)
        
        # MFI
        result['mfi'] = ta.mfi(result['high'], result['low'], result['close'], result['volume'], length=14).fillna(0)
        
        return result
    
    def _calculate_trix(self, close: pd.Series, period: int = 12) -> pd.Series:
        """计算TRIX指标"""
        ema1 = ta.ema(close, length=period)
        ema2 = ta.ema(ema1, length=period)
        ema3 = ta.ema(ema2, length=period)
        trix = ((ema3 - ema3.shift(1)) / ema3.shift(1) * 100).fillna(0)
        return trix
    
    def calculate_and_save(self, code: str, trade_date: date) -> Optional[StockIndicator]:
        """计算并保存单只股票的指标"""
        try:
            hist_data = self.stock_service.get_stock_hist(code)
            if hist_data is None or hist_data.empty:
                return None
            
            indicator_data = self.calculate_indicators(hist_data)
            if indicator_data.empty:
                return None
            
            latest = indicator_data.iloc[-1]
            
            entity = StockIndicator(
                date=trade_date,
                code=code,
                macd=float(latest.get('macd', 0)),
                macds=float(latest.get('macds', 0)),
                macdh=float(latest.get('macdh', 0)),
                kdjk=float(latest.get('kdjk', 0)),
                kdjd=float(latest.get('kdjd', 0)),
                kdjj=float(latest.get('kdjj', 0)),
                rsi=float(latest.get('rsi', 0)),
                rsi_6=float(latest.get('rsi_6', 0)),
                rsi_12=float(latest.get('rsi_12', 0)),
                rsi_24=float(latest.get('rsi_24', 0)),
                atr=float(latest.get('atr', 0)),
                cci=float(latest.get('cci', 0)),
                wr_6=float(latest.get('wr_6', 0)),
                wr_10=float(latest.get('wr_10', 0)),
                boll_ub=float(latest.get('boll_ub', 0)),
                boll=float(latest.get('boll', 0)),
                boll_lb=float(latest.get('boll_lb', 0)),
                ma5=float(latest.get('ma5', 0)),
                ma10=float(latest.get('ma10', 0)),
                ma20=float(latest.get('ma20', 0)),
                ma60=float(latest.get('ma60', 0)),
                trix=float(latest.get('trix', 0)),
                mfi=float(latest.get('mfi', 0))
            )
            
            self.indicator_dao.save(entity)
            return entity
            
        except Exception as e:
            logger.error(f"计算股票{code}指标失败: {e}")
            return None
    
    def batch_calculate_and_save(self, codes: List[str], trade_date: date, workers: int = 10) -> int:
        """批量计算并保存指标"""
        success_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_code = {
                executor.submit(self.calculate_and_save, code, trade_date): code
                for code in codes
            }
            
            for future in concurrent.futures.as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                except Exception as e:
                    logger.error(f"批量计算股票{code}指标异常: {e}")
        
        logger.info(f"批量计算指标完成: {trade_date}, 成功{success_count}/{len(codes)}")
        return success_count
    
    def get_indicators(self, code: str, trade_date: date) -> Optional[StockIndicator]:
        """获取股票指标"""
        return self.indicator_dao.find_by_code_and_date(code, trade_date)
    
    def get_indicators_by_date(self, trade_date: date) -> List[StockIndicator]:
        """获取指定日期的所有股票指标"""
        return self.indicator_dao.find_by_date(trade_date)
    
    def guess_buy(self, trade_date: date) -> List[StockIndicator]:
        """筛选买入信号股票"""
        return self.indicator_dao.find_buy_signals(trade_date)
    
    def guess_sell(self, trade_date: date) -> List[StockIndicator]:
        """筛选卖出信号股票"""
        return self.indicator_dao.find_sell_signals(trade_date)
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()