#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技术指标计算器 - 使用pandas-ta实现
"""

import numpy as np
import pandas as pd
import pandas_ta as ta
from typing import Optional


class IndicatorCalculator:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_all(data: pd.DataFrame, threshold: int = 120) -> Optional[pd.DataFrame]:
        """
        计算所有技术指标
        
        Args:
            data: 股票历史数据，需包含 open, close, high, low, volume, amount, turnover 字段
            threshold: 返回最近N条数据
            
        Returns:
            计算后的DataFrame
        """
        try:
            if data is None or len(data.index) <= 1:
                return None
            
            data = data.copy()
            
            # MACD
            macd = ta.macd(data['close'], fast=12, slow=26, signal=9)
            if macd is not None:
                data['macd'] = macd['MACD_12_26_9'].fillna(0)
                data['macds'] = macd['MACDs_12_26_9'].fillna(0)
                data['macdh'] = macd['MACDh_12_26_9'].fillna(0)
            else:
                data['macd'] = 0
                data['macds'] = 0
                data['macdh'] = 0
            
            # KDJ
            stoch = ta.stoch(data['high'], data['low'], data['close'], k=9, d=5, smooth_k=5)
            if stoch is not None:
                data['kdjk'] = stoch['STOCHk_9_5_5'].fillna(0)
                data['kdjd'] = stoch['STOCHd_9_5_5'].fillna(0)
                data['kdjj'] = 3 * data['kdjk'] - 2 * data['kdjd']
            else:
                data['kdjk'] = 0
                data['kdjd'] = 0
                data['kdjj'] = 0
            
            # BOLL
            bbands = ta.bbands(data['close'], length=20, std=2)
            if bbands is not None:
                data['boll_ub'] = bbands['BBU_20_2.0'].fillna(0)
                data['boll'] = bbands['BBM_20_2.0'].fillna(0)
                data['boll_lb'] = bbands['BBL_20_2.0'].fillna(0)
            else:
                data['boll_ub'] = 0
                data['boll'] = 0
                data['boll_lb'] = 0
            
            # RSI
            data['rsi'] = ta.rsi(data['close'], length=14).fillna(0)
            data['rsi_6'] = ta.rsi(data['close'], length=6).fillna(0)
            data['rsi_12'] = ta.rsi(data['close'], length=12).fillna(0)
            data['rsi_24'] = ta.rsi(data['close'], length=24).fillna(0)
            
            # ATR
            data['atr'] = ta.atr(data['high'], data['low'], data['close'], length=14).fillna(0)
            
            # CCI
            data['cci'] = ta.cci(data['high'], data['low'], data['close'], length=14).fillna(0)
            
            # WR
            data['wr_6'] = ta.willr(data['high'], data['low'], data['close'], length=6).fillna(0)
            data['wr_10'] = ta.willr(data['high'], data['low'], data['close'], length=10).fillna(0)
            data['wr_14'] = ta.willr(data['high'], data['low'], data['close'], length=14).fillna(0)
            
            # MA
            data['ma6'] = ta.sma(data['close'], length=6).fillna(0)
            data['ma10'] = ta.sma(data['close'], length=10).fillna(0)
            data['ma20'] = ta.sma(data['close'], length=20).fillna(0)
            data['ma50'] = ta.sma(data['close'], length=50).fillna(0)
            data['ma200'] = ta.sma(data['close'], length=200).fillna(0)
            
            # VOL
            data['vol_5'] = ta.sma(data['volume'], length=5).fillna(0)
            data['vol_10'] = ta.sma(data['volume'], length=10).fillna(0)
            
            # OBV
            data['obv'] = ta.obv(data['close'], data['volume']).fillna(0)
            
            # ROC
            data['roc'] = ta.roc(data['close'], length=12).fillna(0)
            
            # MFI
            data['mfi'] = ta.mfi(data['high'], data['low'], data['close'], data['volume'], length=14).fillna(0)
            
            # TRIX (自定义实现)
            data['trix'] = IndicatorCalculator._calculate_trix(data['close'], period=12)
            
            if threshold is not None:
                data = data.tail(n=threshold).copy()
            
            return data
            
        except Exception as e:
            print(f"计算指标异常: {e}")
            return None
    
    @staticmethod
    def _calculate_trix(close: pd.Series, period: int = 12) -> pd.Series:
        """计算TRIX指标"""
        ema1 = ta.ema(close, length=period)
        ema2 = ta.ema(ema1, length=period)
        ema3 = ta.ema(ema2, length=period)
        trix = ((ema3 - ema3.shift(1)) / ema3.shift(1) * 100).fillna(0)
        return trix
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame) -> dict:
        """单独计算MACD"""
        macd = ta.macd(data['close'], fast=12, slow=26, signal=9)
        if macd is not None:
            return {
                'macd': macd['MACD_12_26_9'].iloc[-1],
                'macds': macd['MACDs_12_26_9'].iloc[-1],
                'macdh': macd['MACDh_12_26_9'].iloc[-1]
            }
        return {'macd': 0, 'macds': 0, 'macdh': 0}
    
    @staticmethod
    def calculate_kdj(data: pd.DataFrame) -> dict:
        """单独计算KDJ"""
        stoch = ta.stoch(data['high'], data['low'], data['close'], k=9, d=5, smooth_k=5)
        if stoch is not None:
            kdjk = stoch['STOCHk_9_5_5'].iloc[-1]
            kdjd = stoch['STOCHd_9_5_5'].iloc[-1]
            kdjj = 3 * kdjk - 2 * kdjd
            return {'kdjk': kdjk, 'kdjd': kdjd, 'kdjj': kdjj}
        return {'kdjk': 0, 'kdjd': 0, 'kdjj': 0}
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float:
        """单独计算RSI"""
        rsi = ta.rsi(data['close'], length=period)
        return rsi.iloc[-1] if rsi is not None and not np.isnan(rsi.iloc[-1]) else 0.0
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> float:
        """单独计算ATR"""
        atr = ta.atr(data['high'], data['low'], data['close'], length=period)
        return atr.iloc[-1] if atr is not None and not np.isnan(atr.iloc[-1]) else 0.0