#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
资金流向服务
"""

from datetime import date, datetime
from typing import Optional, List, Dict
import pandas as pd
from sqlalchemy.orm import Session

from app.dao.stock_dao import StockDAO
from app.entity.fund_flow import StockFundFlow
from app.crawler.stock_fund_crawler import StockFundCrawler
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FundFlowService:
    """资金流向服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.stock_dao = StockDAO(self.session)
        self.fund_crawler = StockFundCrawler()
    
    async def get_individual_fund_flow(self, indicator: str = "5日") -> pd.DataFrame:
        """
        获取个股资金流向
        
        Args:
            indicator: 时间周期 今日/3日/5日/10日
            
        Returns:
            资金流向DataFrame
        """
        return await self.fund_crawler.get_individual_fund_flow_rank(indicator)
    
    async def get_sector_fund_flow(
        self, 
        indicator: str = "10日", 
        sector_type: str = "行业资金流"
    ) -> pd.DataFrame:
        """
        获取板块资金流向
        
        Args:
            indicator: 时间周期 今日/5日/10日
            sector_type: 板块类型 行业资金流/概念资金流/地域资金流
            
        Returns:
            板块资金流向DataFrame
        """
        return await self.fund_crawler.get_sector_fund_flow_rank(indicator, sector_type)
    
    def save_fund_flow_data(
        self, 
        data: pd.DataFrame, 
        trade_date: date,
        indicator: str = "今日"
    ) -> int:
        """
        保存资金流向数据
        
        Args:
            data: 资金流向DataFrame
            trade_date: 交易日期
            indicator: 时间周期
            
        Returns:
            保存的记录数
        """
        if data is None or data.empty:
            return 0
        
        # 转换为实体列表
        entities = []
        for _, row in data.iterrows():
            entity = StockFundFlow(
                date=trade_date,
                code=str(row.get('代码', '')),
                name=str(row.get('名称', '')),
                indicator=indicator,
                main_net_inflow=float(row.get(f'{indicator}主力净流入-净额', 0) or 0),
                main_net_inflow_ratio=float(row.get(f'{indicator}主力净流入-净占比', 0) or 0),
                super_large_net_inflow=float(row.get(f'{indicator}超大单净流入-净额', 0) or 0),
                super_large_net_inflow_ratio=float(row.get(f'{indicator}超大单净流入-净占比', 0) or 0),
                large_net_inflow=float(row.get(f'{indicator}大单净流入-净额', 0) or 0),
                large_net_inflow_ratio=float(row.get(f'{indicator}大单净流入-净占比', 0) or 0),
                medium_net_inflow=float(row.get(f'{indicator}中单净流入-净额', 0) or 0),
                medium_net_inflow_ratio=float(row.get(f'{indicator}中单净流入-净占比', 0) or 0),
                small_net_inflow=float(row.get(f'{indicator}小单净流入-净额', 0) or 0),
                small_net_inflow_ratio=float(row.get(f'{indicator}小单净流入-净占比', 0) or 0)
            )
            entities.append(entity)
        
        return len(entities)
    
    async def fetch_and_save_daily_data(self, trade_date: date = None) -> Dict[str, int]:
        """
        抓取并保存每日资金流向数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            各指标保存的记录数
        """
        if trade_date is None:
            trade_date = date.today()
        
        result = {}
        indicators = ["今日", "3日", "5日", "10日"]
        
        for indicator in indicators:
            try:
                data = await self.get_individual_fund_flow(indicator)
                count = self.save_fund_flow_data(data, trade_date, indicator)
                result[indicator] = count
                logger.info(f"保存资金流向数据成功: {trade_date} {indicator}, 共{count}条")
            except Exception as e:
                logger.error(f"抓取并保存资金流向数据失败: {indicator}, {e}")
                result[indicator] = 0
        
        return result
    
    def get_top_inflow(self, trade_date: date, limit: int = 50) -> List[StockFundFlow]:
        """
        获取资金净流入前N名
        
        Args:
            trade_date: 交易日期
            limit: 数量限制
            
        Returns:
            资金流向列表
        """
        # 需要实现fund_flow_dao
        return []
    
    def get_top_outflow(self, trade_date: date, limit: int = 50) -> List[StockFundFlow]:
        """
        获取资金净流出前N名
        
        Args:
            trade_date: 交易日期
            limit: 数量限制
            
        Returns:
            资金流向列表
        """
        return []
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()