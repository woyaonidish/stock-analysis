#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史数据缓存服务
"""

from datetime import date, datetime, timedelta
from typing import List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.dao.other_dao import HistDAO
from app.entity.stock_other import StockHistData
from app.crawler.tdx_fetcher import TdxFetcher
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HistService:
    """历史数据缓存服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.hist_dao = HistDAO(self.session)
        self.fetcher = TdxFetcher()
    
    def get_cached_hist(self, code: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        从缓存获取历史数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            历史数据DataFrame
        """
        entities = self.hist_dao.find_by_code_range(code, start_date, end_date)
        
        if not entities:
            return pd.DataFrame()
        
        data = []
        for entity in entities:
            data.append({
                'date': entity.date,
                'open': entity.open,
                'close': entity.close,
                'high': entity.high,
                'low': entity.low,
                'volume': entity.volume,
                'amount': entity.amount,
                'amplitude': entity.amplitude,
                'quote_change': entity.quote_change,
                'ups_downs': entity.ups_downs,
                'turnover': entity.turnover
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        return df
    
    def save_hist_data(self, code: str, hist_data: pd.DataFrame) -> int:
        """
        保存历史数据到缓存
        
        Args:
            code: 股票代码
            hist_data: 历史数据DataFrame
            
        Returns:
            保存记录数
        """
        if hist_data is None or hist_data.empty:
            return 0
        
        entities = []
        for _, row in hist_data.iterrows():
            date_val = row.get('date')
            if isinstance(date_val, str):
                date_val = datetime.strptime(date_val.split()[0], '%Y-%m-%d').date()
            elif isinstance(date_val, pd.Timestamp):
                date_val = date_val.date()
            elif isinstance(date_val, datetime):
                date_val = date_val.date()
            
            # 检查是否已存在
            existing = self.hist_dao.find_by_id(date=date_val, code=code)
            if existing:
                continue  # 已存在则跳过
            
            entity = StockHistData(
                date=date_val,
                code=code,
                open=float(row.get('open', 0) or 0),
                close=float(row.get('close', 0) or 0),
                high=float(row.get('high', 0) or 0),
                low=float(row.get('low', 0) or 0),
                volume=int(row.get('volume', 0) or 0),
                amount=int(row.get('amount', 0) or 0),
                amplitude=self._calc_amplitude(row),
                quote_change=self._calc_quote_change(row),
                ups_downs=self._calc_ups_downs(row),
                turnover=float(row.get('turnover', 0) or 0)
            )
            entities.append(entity)
        
        if entities:
            self.hist_dao.save_all(entities)
            logger.info(f"保存历史数据缓存成功: {code}, 共 {len(entities)} 条")
        
        return len(entities)
    
    def _calc_amplitude(self, row) -> float:
        """计算振幅"""
        high = row.get('high', 0)
        low = row.get('low', 0)
        pre_close = row.get('pre_close', 0) or row.get('close', 0)
        if pre_close > 0:
            return round((high - low) / pre_close * 100, 2)
        return 0.0
    
    def _calc_quote_change(self, row) -> float:
        """计算涨跌幅"""
        close = row.get('close', 0)
        pre_close = row.get('pre_close', 0) or row.get('close', 0)
        if pre_close > 0:
            return round((close - pre_close) / pre_close * 100, 2)
        return 0.0
    
    def _calc_ups_downs(self, row) -> float:
        """计算涨跌额"""
        close = row.get('close', 0)
        pre_close = row.get('pre_close', 0) or row.get('close', 0)
        return round(close - pre_close, 2)
    
    async def fetch_and_cache(self, code: str, days: int = 365) -> int:
        """
        获取并缓存历史数据
        
        Args:
            code: 股票代码
            days: 获取天数
            
        Returns:
            保存记录数
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # 获取历史数据
            hist_data = await self.fetcher.get_stock_hist(
                symbol=code,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                period="daily"
            )
            
            if hist_data is None or hist_data.empty:
                logger.warning(f"获取 {code} 历史数据为空")
                return 0
            
            # 保存到缓存
            count = self.save_hist_data(code, hist_data)
            return count
            
        except Exception as e:
            logger.error(f"获取并缓存 {code} 历史数据失败: {e}")
            return 0
    
    def get_cache_status(self, code: str) -> dict:
        """
        获取缓存状态
        
        Args:
            code: 股票代码
            
        Returns:
            缓存状态信息
        """
        count = self.hist_dao.count_by_code(code)
        latest_date = self.hist_dao.find_latest_date(code)
        
        return {
            'code': code,
            'cache_count': count,
            'latest_date': str(latest_date) if latest_date else None
        }
    
    def clear_cache(self, code: str) -> int:
        """
        清除指定股票的缓存
        
        Args:
            code: 股票代码
            
        Returns:
            清除记录数
        """
        entities = self.hist_dao.find_by_code(code)
        count = 0
        for entity in entities:
            self.hist_dao.delete(entity)
            count += 1
        logger.info(f"清除 {code} 历史数据缓存，共 {count} 条")
        return count
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()