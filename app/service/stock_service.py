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
from app.crawler.tdx_fetcher import TdxFetcher
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StockService:
    """股票数据服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.stock_dao = StockDAO(self.session)
        self.fetcher = TdxFetcher()
    
    async def get_stock_list(self, trade_date: date = None) -> pd.DataFrame:
        """
        异步获取股票列表
        
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
        return await self.fetcher.get_stock_list()
    
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
    
    async def get_stock_hist(
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
        return await self.fetcher.get_stock_hist(
            symbol=code,
            period=period,
            start_date=start_date or "19700101",
            end_date=end_date or "20500101",
            adjust=adjust
        )
    
    async def get_stock_hist_min(
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
        return await self.fetcher.get_stock_hist_min(
            symbol=code,
            period=period,
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
                open_price=float(row.get('open_price', 0) or 0),
                close_price=float(row.get('close_price', 0) or 0),
                high_price=float(row.get('high_price', 0) or 0),
                low_price=float(row.get('low_price', 0) or 0),
                pre_close_price=float(row.get('pre_close_price', 0) or 0),
                volume=int(row.get('volume', 0) or 0),
                amount=int(row.get('amount', 0) or 0),
                bid1=float(row.get('bid1', 0) or 0),
                bid1_vol=int(row.get('bid1_vol', 0) or 0),
                bid2=float(row.get('bid2', 0) or 0),
                bid2_vol=int(row.get('bid2_vol', 0) or 0),
                bid3=float(row.get('bid3', 0) or 0),
                bid3_vol=int(row.get('bid3_vol', 0) or 0),
                ask1=float(row.get('ask1', 0) or 0),
                ask1_vol=int(row.get('ask1_vol', 0) or 0),
                ask2=float(row.get('ask2', 0) or 0),
                ask2_vol=int(row.get('ask2_vol', 0) or 0),
                ask3=float(row.get('ask3', 0) or 0),
                ask3_vol=int(row.get('ask3_vol', 0) or 0),
            )
            entities.append(entity)
        
        # 批量保存
        self.stock_dao.save_all(entities)
        return len(entities)
    
    def _save_batch_data(self, data: pd.DataFrame, trade_date: date) -> int:
        """
        保存单批次股票行情数据
        
        Args:
            data: 单批次股票数据DataFrame
            trade_date: 交易日期
            
        Returns:
            保存的记录数
        """
        if data is None or data.empty:
            return 0
        
        try:
            # 转换为实体列表
            entities = []
            for _, row in data.iterrows():
                entity = StockSpot(
                    date=trade_date,
                    code=str(row.get('code', '')),
                    name=str(row.get('name', '')),
                    open_price=float(row.get('open_price', 0) or 0),
                    close_price=float(row.get('close_price', 0) or 0),
                    high_price=float(row.get('high_price', 0) or 0),
                    low_price=float(row.get('low_price', 0) or 0),
                    pre_close_price=float(row.get('pre_close_price', 0) or 0),
                    volume=int(row.get('volume', 0) or 0),
                    amount=int(row.get('amount', 0) or 0),
                    bid1=float(row.get('bid1', 0) or 0),
                    bid1_vol=int(row.get('bid1_vol', 0) or 0),
                    bid2=float(row.get('bid2', 0) or 0),
                    bid2_vol=int(row.get('bid2_vol', 0) or 0),
                    bid3=float(row.get('bid3', 0) or 0),
                    bid3_vol=int(row.get('bid3_vol', 0) or 0),
                    ask1=float(row.get('ask1', 0) or 0),
                    ask1_vol=int(row.get('ask1_vol', 0) or 0),
                    ask2=float(row.get('ask2', 0) or 0),
                    ask2_vol=int(row.get('ask2_vol', 0) or 0),
                    ask3=float(row.get('ask3', 0) or 0),
                    ask3_vol=int(row.get('ask3_vol', 0) or 0),
                )
                entities.append(entity)
            
            # 使用 upsert_all 处理已存在数据（先删除后插入）
            count = self.stock_dao.upsert_all(entities, key_fields=['date', 'code'])
            logger.debug(f"批次保存 {count} 条数据")
            return count
            
        except Exception as e:
            # 发生异常时 rollback
            self.session.rollback()
            logger.error(f"批次保存失败: {e}")
            raise e
    
    async def fetch_and_save_daily_data(self, trade_date: date = None) -> int:
        """
        异步抓取并保存每日股票数据
        
        批量获取全部A股实时行情，每批次获取后立即保存
        
        Args:
            trade_date: 交易日期
            
        Returns:
            保存的总记录数
        """
        if trade_date is None:
            trade_date = date.today()
        
        try:
            # 先删除旧数据
            self.stock_dao.delete_by_date(trade_date)
            logger.info(f"已删除 {trade_date} 的旧数据")
            
            # 定义批次保存回调函数
            def batch_save_callback(batch_df: pd.DataFrame, batch_idx: int):
                count = self._save_batch_data(batch_df, trade_date)
                logger.debug(f"批次 {batch_idx + 1} 保存 {count} 条数据到数据库")
            
            # 批量获取全部A股实时行情，每批次立即保存
            total_count = await self.fetcher.get_all_stocks_realtime(
                on_batch_save=batch_save_callback
            )
            
            logger.info(f"抓取并保存股票数据完成: {trade_date}, 共 {total_count} 条")
            return total_count
            
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
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
