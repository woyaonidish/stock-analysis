#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据服务
"""

from datetime import date, datetime
from typing import Optional, List, Dict
import pandas as pd
from sqlalchemy.orm import Session

from app.dao.stock_dao import StockDAO
from app.entity.stock_spot import StockSpot
from app.crawler.eastmoney_fetcher import EastMoneyFetcher
from app.crawler.stock_hist_crawler import StockHistCrawler
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StockService:
    """股票数据服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.stock_dao = StockDAO(self.session)
        self.fetcher = EastMoneyFetcher()
        self.hist_crawler = StockHistCrawler()
    
    def get_stock_list(self, trade_date: date = None) -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            trade_date: 交易日期
            
        Returns:
            股票列表DataFrame
        """
        if trade_date is None:
            trade_date = date.today()
        
        # 先从数据库查询
        stocks = self.stock_dao.find_by_date(trade_date)
        if stocks:
            return pd.DataFrame([s.__dict__ for s in stocks])
        
        # 数据库没有则从网络获取
        return self.fetcher.get_stock_list()
    
    def get_stock_spot(self, code: str, trade_date: date = None) -> Optional[StockSpot]:
        """
        获取单只股票实时行情
        
        Args:
            code: 股票代码
            trade_date: 交易日期
            
        Returns:
            股票行情实体
        """
        if trade_date is None:
            trade_date = date.today()
        
        return self.stock_dao.find_by_code_and_date(code, trade_date)
    
    def get_stock_hist(
        self, 
        code: str, 
        start_date: str = None, 
        end_date: str = None,
        period: str = "daily",
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期 daily/weekly/monthly
            adjust: 复权类型
            
        Returns:
            历史数据DataFrame
        """
        return self.hist_crawler.get_stock_hist(
            symbol=code,
            period=period,
            start_date=start_date or "19700101",
            end_date=end_date or "20500101",
            adjust=adjust
        )
    
    def get_stock_hist_min(
        self,
        code: str,
        period: str = "5",
        start_date: str = None,
        end_date: str = None,
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        获取股票分时数据
        
        Args:
            code: 股票代码
            period: 周期 1/5/15/30/60分钟
            start_date: 开始日期时间
            end_date: 结束日期时间
            adjust: 复权类型
            
        Returns:
            分时数据DataFrame
        """
        return self.hist_crawler.get_stock_hist_min(
            symbol=code,
            period=period,
            start_date=start_date or "1979-09-01 09:32:00",
            end_date=end_date or "2222-01-01 09:32:00",
            adjust=adjust
        )
    
    def save_stock_spot_data(self, data: pd.DataFrame, trade_date: date) -> int:
        """
        保存股票实时行情数据
        
        Args:
            data: 股票数据DataFrame
            trade_date: 交易日期
            
        Returns:
            保存的记录数
        """
        if data is None or data.empty:
            return 0
        
        # 删除旧数据
        self.stock_dao.delete_by_date(trade_date)
        
        # 转换为实体列表
        entities = []
        for _, row in data.iterrows():
            entity = StockSpot(
                date=trade_date,
                code=str(row.get('code', '')),
                name=str(row.get('name', '')),
                new_price=float(row.get('new_price', 0) or 0),
                change_rate=float(row.get('change_rate', 0) or 0),
                ups_downs=float(row.get('ups_downs', 0) or 0),
                volume=float(row.get('volume', 0) or 0),
                deal_amount=float(row.get('deal_amount', 0) or 0),
                amplitude=float(row.get('amplitude', 0) or 0),
                turnoverrate=float(row.get('turnoverrate', 0) or 0),
                volume_ratio=float(row.get('volume_ratio', 0) or 0),
                open_price=float(row.get('open_price', 0) or 0),
                high_price=float(row.get('high_price', 0) or 0),
                low_price=float(row.get('low_price', 0) or 0),
                pre_close_price=float(row.get('pre_close_price', 0) or 0),
                total_market_cap=float(row.get('total_market_cap', 0) or 0),
                free_cap=float(row.get('free_cap', 0) or 0),
                pe=float(row.get('pe9', 0) or 0),
                pb=float(row.get('pbnewmrq', 0) or 0),
                industry=str(row.get('industry', ''))
            )
            entities.append(entity)
        
        # 批量保存
        self.stock_dao.batch_save(entities)
        return len(entities)
    
    def fetch_and_save_daily_data(self, trade_date: date = None) -> int:
        """
        同步抓取并保存每日股票数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            保存的记录数
        """
        if trade_date is None:
            trade_date = date.today()
        
        try:
            # 获取股票列表
            data = self.fetcher.get_stock_list()
            if data is None or data.empty:
                logger.warning(f"获取股票数据为空: {trade_date}")
                return 0
            
            # 保存数据
            count = self.save_stock_spot_data(data, trade_date)
            logger.info(f"保存股票数据成功: {trade_date}, 共{count}条")
            return count
            
        except Exception as e:
            logger.error(f"抓取并保存股票数据失败: {e}")
            return 0
    
    async def async_fetch_and_save_daily_data(self, trade_date: date = None) -> int:
        """
        异步抓取并保存每日股票数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            保存的记录数
        """
        if trade_date is None:
            trade_date = date.today()
        
        try:
            # 异步获取股票列表
            data = await self.fetcher.async_get_stock_list()
            if data is None or data.empty:
                logger.warning(f"获取股票数据为空: {trade_date}")
                return 0
            
            # 保存数据
            count = self.save_stock_spot_data(data, trade_date)
            logger.info(f"保存股票数据成功: {trade_date}, 共{count}条")
            return count
            
        except Exception as e:
            logger.error(f"异步抓取并保存股票数据失败: {e}")
            return 0
    
    def search_stocks(
        self, 
        keyword: str = None,
        industry: str = None,
        min_price: float = None,
        max_price: float = None,
        trade_date: date = None
    ) -> List[StockSpot]:
        """
        搜索股票
        
        Args:
            keyword: 关键词(代码或名称)
            industry: 行业
            min_price: 最低价格
            max_price: 最高价格
            trade_date: 交易日期
            
        Returns:
            股票列表
        """
        if trade_date is None:
            trade_date = date.today()
        
        return self.stock_dao.search(
            keyword=keyword,
            industry=industry,
            min_price=min_price,
            max_price=max_price,
            trade_date=trade_date
        )
    
    def get_stock_codes(self, trade_date: date = None) -> List[str]:
        """
        获取股票代码列表
        
        Args:
            trade_date: 交易日期
            
        Returns:
            股票代码列表
        """
        if trade_date is None:
            trade_date = date.today()
        
        stocks = self.stock_dao.find_by_date(trade_date)
        return [s.code for s in stocks] if stocks else []
    
    def get_code_id_map(self) -> Dict[str, int]:
        """
        获取股票代码与市场ID映射
        
        Returns:
            代码到市场ID的映射字典
        """
        return self.fetcher.get_code_id_map()
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
