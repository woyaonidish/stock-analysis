#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
K线形态识别器 - 纯Python实现
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List


class PatternRecognizer:
    """K线形态识别器 - 纯Python实现"""
    
    # 形态名称列表
    PATTERN_NAMES = [
        'doji',                    # 十字星
        'dragonfly_doji',          # 蜻蜓十字星
        'gravestone_doji',         # 墓碑十字星
        'hammer',                  # 锤子线
        'inverted_hammer',         # 倒锤子线
        'hanging_man',             # 上吊线
        'shooting_star',           # 流星线
        'engulfing_pattern',       # 吞没形态
        'harami_pattern',          # 孕线形态
        'morning_star',            # 启明星
        'evening_star',            # 黄昏星
        'three_white_soldiers',    # 三白兵
        'three_black_crows',       # 三只乌鸦
        'dark_cloud_cover',        # 乌云盖顶
        'piercing_pattern',        # 刺透形态
        'spinning_top',            # 纺锤线
        'marubozu',                # 光头光脚
    ]
    
    @classmethod
    def recognize_all(cls, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        识别所有K线形态
        
        Args:
            data: 股票历史数据
            
        Returns:
            识别结果DataFrame，包含各形态的识别结果(正值=看涨，负值=看跌，0=无形态)
        """
        try:
            if data is None or len(data.index) <= 1:
                return None
            
            data = data.copy()
            
            # 逐个识别形态
            data['doji'] = cls._recognize_doji(data)
            data['dragonfly_doji'] = cls._recognize_dragonfly_doji(data)
            data['gravestone_doji'] = cls._recognize_gravestone_doji(data)
            data['hammer'] = cls._recognize_hammer(data)
            data['inverted_hammer'] = cls._recognize_inverted_hammer(data)
            data['hanging_man'] = cls._recognize_hanging_man(data)
            data['shooting_star'] = cls._recognize_shooting_star(data)
            data['engulfing_pattern'] = cls._recognize_engulfing(data)
            data['harami_pattern'] = cls._recognize_harami(data)
            data['morning_star'] = cls._recognize_morning_star(data)
            data['evening_star'] = cls._recognize_evening_star(data)
            data['three_white_soldiers'] = cls._recognize_three_white_soldiers(data)
            data['three_black_crows'] = cls._recognize_three_black_crows(data)
            data['dark_cloud_cover'] = cls._recognize_dark_cloud_cover(data)
            data['piercing_pattern'] = cls._recognize_piercing(data)
            data['spinning_top'] = cls._recognize_spinning_top(data)
            data['marubozu'] = cls._recognize_marubozu(data)
            
            return data
            
        except Exception as e:
            print(f"形态识别异常: {e}")
            return None
    
    @classmethod
    def get_pattern_names(cls) -> list:
        """获取所有形态名称"""
        return cls.PATTERN_NAMES
    
    # ==================== 基础计算函数 ====================
    
    @staticmethod
    def _body_size(open_price: np.ndarray, close_price: np.ndarray) -> np.ndarray:
        """计算实体大小"""
        return np.abs(close_price - open_price)
    
    @staticmethod
    def _upper_shadow(high_price: np.ndarray, open_price: np.ndarray, close_price: np.ndarray) -> np.ndarray:
        """计算上影线"""
        body_top = np.maximum(open_price, close_price)
        return high_price - body_top
    
    @staticmethod
    def _lower_shadow(low_price: np.ndarray, open_price: np.ndarray, close_price: np.ndarray) -> np.ndarray:
        """计算下影线"""
        body_bottom = np.minimum(open_price, close_price)
        return body_bottom - low_price
    
    @staticmethod
    def _total_range(high_price: np.ndarray, low_price: np.ndarray) -> np.ndarray:
        """计算总振幅"""
        return high_price - low_price
    
    # ==================== 形态识别函数 ====================
    
    @classmethod
    def _recognize_doji(cls, data: pd.DataFrame) -> np.ndarray:
        """十字星识别"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        body = cls._body_size(open_price, close_price)
        range_total = cls._total_range(high_price, low_price)
        
        doji = np.where((body / (range_total + 1e-10)) < 0.05, 100, 0)
        doji = np.where(range_total == 0, 0, doji)
        return doji
    
    @classmethod
    def _recognize_dragonfly_doji(cls, data: pd.DataFrame) -> np.ndarray:
        """蜻蜓十字星"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        body = cls._body_size(open_price, close_price)
        range_total = cls._total_range(high_price, low_price)
        
        pattern = np.where(
            (upper_shadow < body + 1e-10) & 
            (lower_shadow > body * 3) & 
            (body < range_total * 0.1),
            100, 0
        )
        return pattern
    
    @classmethod
    def _recognize_gravestone_doji(cls, data: pd.DataFrame) -> np.ndarray:
        """墓碑十字星"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        body = cls._body_size(open_price, close_price)
        range_total = cls._total_range(high_price, low_price)
        
        pattern = np.where(
            (lower_shadow < body + 1e-10) & 
            (upper_shadow > body * 3) & 
            (body < range_total * 0.1),
            -100, 0
        )
        return pattern
    
    @classmethod
    def _recognize_hammer(cls, data: pd.DataFrame) -> np.ndarray:
        """锤子线"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        body = cls._body_size(open_price, close_price)
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        
        pattern = np.where(
            (lower_shadow >= body * 2) & 
            (upper_shadow <= body * 0.5) &
            (body > 0),
            100, 0
        )
        return pattern
    
    @classmethod
    def _recognize_inverted_hammer(cls, data: pd.DataFrame) -> np.ndarray:
        """倒锤子线"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        body = cls._body_size(open_price, close_price)
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        
        pattern = np.where(
            (upper_shadow >= body * 2) & 
            (lower_shadow <= body * 0.5) &
            (body > 0),
            100, 0
        )
        return pattern
    
    @classmethod
    def _recognize_hanging_man(cls, data: pd.DataFrame) -> np.ndarray:
        """上吊线"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        body = cls._body_size(open_price, close_price)
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        
        pattern = np.where(
            (lower_shadow >= body * 2) & 
            (upper_shadow <= body * 0.5) &
            (body > 0),
            -100, 0
        )
        return pattern
    
    @classmethod
    def _recognize_shooting_star(cls, data: pd.DataFrame) -> np.ndarray:
        """流星线"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        body = cls._body_size(open_price, close_price)
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        
        pattern = np.where(
            (upper_shadow >= body * 2) & 
            (lower_shadow <= body * 0.5) &
            (body > 0),
            -100, 0
        )
        return pattern
    
    @classmethod
    def _recognize_engulfing(cls, data: pd.DataFrame) -> np.ndarray:
        """吞没形态"""
        open_price = data['open'].values
        close_price = data['close'].values
        
        result = np.zeros(len(data))
        
        for i in range(1, len(data)):
            prev_open = open_price[i-1]
            prev_close = close_price[i-1]
            prev_body = abs(prev_close - prev_open)
            
            curr_open = open_price[i]
            curr_close = close_price[i]
            curr_body = abs(curr_close - curr_open)
            
            if curr_body > prev_body and prev_body > 0:
                # 看涨吞没
                if prev_close < prev_open and curr_close > curr_open:
                    if curr_open <= prev_close and curr_close >= prev_open:
                        result[i] = 100
                # 看跌吞没
                elif prev_close > prev_open and curr_close < curr_open:
                    if curr_open >= prev_close and curr_close <= prev_open:
                        result[i] = -100
        
        return result
    
    @classmethod
    def _recognize_harami(cls, data: pd.DataFrame) -> np.ndarray:
        """孕线形态"""
        open_price = data['open'].values
        close_price = data['close'].values
        
        result = np.zeros(len(data))
        
        for i in range(1, len(data)):
            prev_body_top = max(open_price[i-1], close_price[i-1])
            prev_body_bottom = min(open_price[i-1], close_price[i-1])
            
            curr_body_top = max(open_price[i], close_price[i])
            curr_body_bottom = min(open_price[i], close_price[i])
            
            if curr_body_top <= prev_body_top and curr_body_bottom >= prev_body_bottom:
                if close_price[i-1] < open_price[i-1] and close_price[i] > open_price[i]:
                    result[i] = 100
                elif close_price[i-1] > open_price[i-1] and close_price[i] < open_price[i]:
                    result[i] = -100
        
        return result
    
    @classmethod
    def _recognize_morning_star(cls, data: pd.DataFrame) -> np.ndarray:
        """启明星"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        result = np.zeros(len(data))
        
        for i in range(2, len(data)):
            first_bearish = close_price[i-2] < open_price[i-2]
            first_body = abs(close_price[i-2] - open_price[i-2])
            first_range = high_price[i-2] - low_price[i-2]
            
            second_body = abs(close_price[i-1] - open_price[i-1])
            
            third_bullish = close_price[i] > open_price[i]
            third_body = abs(close_price[i] - open_price[i])
            
            if (first_bearish and first_body > first_range * 0.6 and 
                second_body < first_body * 0.3 and 
                third_bullish and third_body > first_body * 0.6):
                result[i] = 100
        
        return result
    
    @classmethod
    def _recognize_evening_star(cls, data: pd.DataFrame) -> np.ndarray:
        """黄昏星"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        result = np.zeros(len(data))
        
        for i in range(2, len(data)):
            first_bullish = close_price[i-2] > open_price[i-2]
            first_body = abs(close_price[i-2] - open_price[i-2])
            first_range = high_price[i-2] - low_price[i-2]
            
            second_body = abs(close_price[i-1] - open_price[i-1])
            
            third_bearish = close_price[i] < open_price[i]
            third_body = abs(close_price[i] - open_price[i])
            
            if (first_bullish and first_body > first_range * 0.6 and 
                second_body < first_body * 0.3 and 
                third_bearish and third_body > first_body * 0.6):
                result[i] = -100
        
        return result
    
    @classmethod
    def _recognize_three_white_soldiers(cls, data: pd.DataFrame) -> np.ndarray:
        """三白兵"""
        open_price = data['open'].values
        close_price = data['close'].values
        
        result = np.zeros(len(data))
        
        for i in range(2, len(data)):
            all_bullish = (
                close_price[i] > open_price[i] and
                close_price[i-1] > open_price[i-1] and
                close_price[i-2] > open_price[i-2]
            )
            
            closing_advancing = (
                close_price[i] > close_price[i-1] and
                close_price[i-1] > close_price[i-2]
            )
            
            opening_in_range = (
                open_price[i] > open_price[i-1] and
                open_price[i] < close_price[i-1]
            )
            
            if all_bullish and closing_advancing and opening_in_range:
                result[i] = 100
        
        return result
    
    @classmethod
    def _recognize_three_black_crows(cls, data: pd.DataFrame) -> np.ndarray:
        """三只乌鸦"""
        open_price = data['open'].values
        close_price = data['close'].values
        
        result = np.zeros(len(data))
        
        for i in range(2, len(data)):
            all_bearish = (
                close_price[i] < open_price[i] and
                close_price[i-1] < open_price[i-1] and
                close_price[i-2] < open_price[i-2]
            )
            
            closing_declining = (
                close_price[i] < close_price[i-1] and
                close_price[i-1] < close_price[i-2]
            )
            
            opening_in_range = (
                open_price[i] < open_price[i-1] and
                open_price[i] > close_price[i-1]
            )
            
            if all_bearish and closing_declining and opening_in_range:
                result[i] = -100
        
        return result
    
    @classmethod
    def _recognize_dark_cloud_cover(cls, data: pd.DataFrame) -> np.ndarray:
        """乌云盖顶"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        
        result = np.zeros(len(data))
        
        for i in range(1, len(data)):
            first_bullish = close_price[i-1] > open_price[i-1]
            first_midpoint = (open_price[i-1] + close_price[i-1]) / 2
            
            second_bearish = close_price[i] < open_price[i]
            
            opens_above_high = open_price[i] > high_price[i-1]
            closes_deep = close_price[i] < first_midpoint
            closes_above_first_open = close_price[i] > open_price[i-1]
            
            if first_bullish and second_bearish and opens_above_high and closes_deep and closes_above_first_open:
                result[i] = -100
        
        return result
    
    @classmethod
    def _recognize_piercing(cls, data: pd.DataFrame) -> np.ndarray:
        """刺透形态"""
        open_price = data['open'].values
        close_price = data['close'].values
        low_price = data['low'].values
        
        result = np.zeros(len(data))
        
        for i in range(1, len(data)):
            first_bearish = close_price[i-1] < open_price[i-1]
            first_midpoint = (open_price[i-1] + close_price[i-1]) / 2
            
            second_bullish = close_price[i] > open_price[i]
            
            opens_below_low = open_price[i] < low_price[i-1]
            closes_deep = close_price[i] > first_midpoint
            closes_below_first_open = close_price[i] < open_price[i-1]
            
            if first_bearish and second_bullish and opens_below_low and closes_deep and closes_below_first_open:
                result[i] = 100
        
        return result
    
    @classmethod
    def _recognize_spinning_top(cls, data: pd.DataFrame) -> np.ndarray:
        """纺锤线"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        body = cls._body_size(open_price, close_price)
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        range_total = cls._total_range(high_price, low_price)
        
        pattern = np.where(
            (body < range_total * 0.3) &
            (upper_shadow > body) &
            (lower_shadow > body) &
            (range_total > 0),
            50, 0
        )
        return pattern
    
    @classmethod
    def _recognize_marubozu(cls, data: pd.DataFrame) -> np.ndarray:
        """光头光脚"""
        open_price = data['open'].values
        close_price = data['close'].values
        high_price = data['high'].values
        low_price = data['low'].values
        
        body = cls._body_size(open_price, close_price)
        upper_shadow = cls._upper_shadow(high_price, open_price, close_price)
        lower_shadow = cls._lower_shadow(low_price, open_price, close_price)
        range_total = cls._total_range(high_price, low_price)
        
        almost_no_shadow = (upper_shadow < range_total * 0.05) & (lower_shadow < range_total * 0.05)
        
        result = np.zeros(len(data))
        bullish = close_price > open_price
        bearish = close_price < open_price
        
        result = np.where(bullish & almost_no_shadow & (body > 0), 100, result)
        result = np.where(bearish & almost_no_shadow & (body > 0), -100, result)
        
        return result
    
    @classmethod
    def recognize_pattern(cls, data: pd.DataFrame, pattern_name: str) -> pd.DataFrame:
        """识别单个形态"""
        if pattern_name not in cls.PATTERN_NAMES:
            raise ValueError(f"未知的形态: {pattern_name}")
        
        data = data.copy()
        
        pattern_func_map = {
            'doji': cls._recognize_doji,
            'dragonfly_doji': cls._recognize_dragonfly_doji,
            'gravestone_doji': cls._recognize_gravestone_doji,
            'hammer': cls._recognize_hammer,
            'inverted_hammer': cls._recognize_inverted_hammer,
            'hanging_man': cls._recognize_hanging_man,
            'shooting_star': cls._recognize_shooting_star,
            'engulfing_pattern': cls._recognize_engulfing,
            'harami_pattern': cls._recognize_harami,
            'morning_star': cls._recognize_morning_star,
            'evening_star': cls._recognize_evening_star,
            'three_white_soldiers': cls._recognize_three_white_soldiers,
            'three_black_crows': cls._recognize_three_black_crows,
            'dark_cloud_cover': cls._recognize_dark_cloud_cover,
            'piercing_pattern': cls._recognize_piercing,
            'spinning_top': cls._recognize_spinning_top,
            'marubozu': cls._recognize_marubozu,
        }
        
        pattern_func = pattern_func_map.get(pattern_name)
        if pattern_func:
            data[pattern_name] = pattern_func(data)
        
        return data