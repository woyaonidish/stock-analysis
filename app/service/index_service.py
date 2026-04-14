#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指数数据服务
"""

from datetime import date
from typing import List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.dao.index_dao import IndexDAO
from app.entity.stock_index_spot import StockIndexSpot
from app.crawler.tdx_fetcher import TdxFetcher
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IndexService:
    """指数数据服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.index_dao = IndexDAO(self.session)
        self.fetcher = TdxFetcher()
    
    def get_index_list(self, query_date: date = None) -> List[StockIndexSpot]:
        """
        获取指数列表
        
        Args:
            query_date: 查询日期
            
        Returns:
            指数列表
        """
        if query_date is None:
            query_date = date.today()
        
        return self.index_dao.find_by_date(query_date)
    
    def get_index(self, code: str, query_date: date = None) -> Optional[StockIndexSpot]:
        """
        获取单只指数行情
        
        Args:
            code: 指数代码
            query_date: 查询日期
            
        Returns:
            指数行情实体
        """
        if query_date is None:
            query_date = date.today()
        
        return self.index_dao.find_by_code(code, query_date)
    
    def save_index_data(self, data: pd.DataFrame, query_date: date) -> int:
        """
        保存指数数据
        
        Args:
            data: 指数数据DataFrame
            query_date: 查询日期
            
        Returns:
            保存记录数
        """
        if data is None or data.empty:
            return 0
        
        # 删除旧数据
        self.index_dao.delete_by_date(query_date)
        
        # 转换为实体列表
        entities = []
        for _, row in data.iterrows():
            entity = StockIndexSpot(
                date=query_date,
                code=str(row.get('code', '')),
                name=str(row.get('name', '')),
                open_price=float(row.get('open_price', 0) or 0),
                close_price=float(row.get('close_price', 0) or 0),
                high_price=float(row.get('high_price', 0) or 0),
                low_price=float(row.get('low_price', 0) or 0),
                pre_close=float(row.get('pre_close', 0) or 0),
                change_rate=float(row.get('change_rate', 0) or 0),
                volume=int(row.get('volume', 0) or 0),
                amount=int(row.get('amount', 0) or 0),
            )
            entities.append(entity)
        
        # 批量保存
        self.index_dao.save_all(entities)
        return len(entities)
    
    async def fetch_and_save_index_data(self, query_date: date = None) -> int:
        """
        异步抓取并保存指数数据
        
        Args:
            query_date: 查询日期
            
        Returns:
            保存记录数
        """
        if query_date is None:
            query_date = date.today()
        
        try:
            # 获取指数实时行情
            data = await self.fetcher.get_index_realtime()
            if data is None or data.empty:
                logger.warning(f"获取指数数据为空: {query_date}")
                return 0
            
            # 保存数据
            count = self.save_index_data(data, query_date)
            logger.info(f"保存指数数据成功: {query_date}, 共 {count} 条")
            return count
            
        except Exception as e:
            logger.error(f"抓取并保存指数数据失败: {e}")
            return 0
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()