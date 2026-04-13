#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETF数据服务
"""

from datetime import date, datetime
from typing import Optional, List
import pandas as pd
from sqlalchemy.orm import Session

from app.dao.etf_dao import ETFDAO
from app.entity.etf_spot import ETFSpot
from app.crawler.etf_crawler import ETFCrawler
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ETFService:
    """ETF数据服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.etf_dao = ETFDAO(self.session)
        self.etf_crawler = ETFCrawler()
    
    async def get_etf_list(self, trade_date: date = None) -> pd.DataFrame:
        """
        获取ETF列表
        
        Args:
            trade_date: 交易日期
            
        Returns:
            ETF列表DataFrame
        """
        if trade_date is None:
            trade_date = date.today()
        
        # 先从数据库查询
        etfs = self.etf_dao.find_by_date(trade_date)
        if etfs:
            return pd.DataFrame([e.__dict__ for e in etfs])
        
        # 数据库没有则从网络获取
        return await self.etf_crawler.get_etf_spot()
    
    def get_etf_spot(self, code: str, trade_date: date = None) -> Optional[ETFSpot]:
        """
        获取单只ETF实时行情
        
        Args:
            code: ETF代码
            trade_date: 交易日期
            
        Returns:
            ETF行情实体
        """
        if trade_date is None:
            trade_date = date.today()
        
        return self.etf_dao.find_by_code_and_date(code, trade_date)
    
    async def get_etf_hist(
        self,
        code: str,
        start_date: str = None,
        end_date: str = None,
        period: str = "daily",
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        获取ETF历史数据
        
        Args:
            code: ETF代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期 daily/weekly/monthly
            adjust: 复权类型
            
        Returns:
            历史数据DataFrame
        """
        return await self.etf_crawler.get_etf_hist(
            symbol=code,
            period=period,
            start_date=start_date or "19700101",
            end_date=end_date or "20500101",
            adjust=adjust
        )
    
    async def get_etf_hist_min(
        self,
        code: str,
        period: str = "5",
        start_date: str = None,
        end_date: str = None,
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        获取ETF分时数据
        
        Args:
            code: ETF代码
            period: 周期 1/5/15/30/60分钟
            start_date: 开始日期时间
            end_date: 结束日期时间
            adjust: 复权类型
            
        Returns:
            分时数据DataFrame
        """
        return await self.etf_crawler.get_etf_hist_min(
            symbol=code,
            period=period,
            start_date=start_date or "1979-09-01 09:32:00",
            end_date=end_date or "2222-01-01 09:32:00",
            adjust=adjust
        )
    
    def save_etf_spot_data(self, data: pd.DataFrame, trade_date: date) -> int:
        """
        保存ETF实时行情数据
        
        Args:
            data: ETF数据DataFrame
            trade_date: 交易日期
            
        Returns:
            保存的记录数
        """
        if data is None or data.empty:
            return 0
        
        # 删除旧数据
        self.etf_dao.delete_by_date(trade_date)
        
        # 转换为实体列表
        entities = []
        for _, row in data.iterrows():
            entity = ETFSpot(
                date=trade_date,
                code=str(row.get('code', '')),
                name=str(row.get('name', '')),
                new_price=float(row.get('new_price', 0) or 0),
                change_rate=float(row.get('change_rate', 0) or 0),
                change_amount=float(row.get('change_amount', 0) or 0),
                volume=float(row.get('volume', 0) or 0),
                amount=float(row.get('amount', 0) or 0),
                open_price=float(row.get('open_price', 0) or 0),
                high_price=float(row.get('high_price', 0) or 0),
                low_price=float(row.get('low_price', 0) or 0),
                pre_close=float(row.get('pre_close', 0) or 0),
                turnover_rate=float(row.get('turnover_rate', 0) or 0),
                circulation_cap=float(row.get('circulation_cap', 0) or 0),
                total_cap=float(row.get('total_cap', 0) or 0)
            )
            entities.append(entity)
        
        # 批量保存
        self.etf_dao.save_all(entities)
        return len(entities)
    
    async def fetch_and_save_daily_data(self, trade_date: date = None) -> int:
        """
        抓取并保存每日ETF数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            保存的记录数
        """
        if trade_date is None:
            trade_date = date.today()
        
        try:
            # 获取ETF列表
            data = await self.etf_crawler.get_etf_spot()
            if data is None or data.empty:
                logger.warning(f"获取ETF数据为空: {trade_date}")
                return 0
            
            # 保存数据
            count = self.save_etf_spot_data(data, trade_date)
            logger.info(f"保存ETF数据成功: {trade_date}, 共{count}条")
            return count
            
        except Exception as e:
            logger.error(f"抓取并保存ETF数据失败: {e}")
            return 0
    
    def search_etfs(
        self,
        keyword: str = None,
        min_price: float = None,
        max_price: float = None,
        trade_date: date = None
    ) -> List[ETFSpot]:
        """
        搜索ETF
        
        Args:
            keyword: 关键词(代码或名称)
            min_price: 最低价格
            max_price: 最高价格
            trade_date: 交易日期
            
        Returns:
            ETF列表
        """
        if trade_date is None:
            trade_date = date.today()
        
        return self.etf_dao.search(
            keyword=keyword,
            min_price=min_price,
            max_price=max_price,
            trade_date=trade_date
        )
    
    def get_etf_codes(self, trade_date: date = None) -> List[str]:
        """
        获取ETF代码列表
        
        Args:
            trade_date: 交易日期
            
        Returns:
            ETF代码列表
        """
        if trade_date is None:
            trade_date = date.today()
        
        etfs = self.etf_dao.find_by_date(trade_date)
        return [e.code for e in etfs] if etfs else []
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()