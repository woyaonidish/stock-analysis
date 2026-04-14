#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指数数据DAO
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app.dao.base_dao import BaseDAO
from app.entity.stock_index_spot import StockIndexSpot


class IndexDAO(BaseDAO[StockIndexSpot]):
    """指数数据DAO"""
    
    def __init__(self, session: Session):
        super().__init__(StockIndexSpot, session)
    
    def find_by_code(self, code: str, query_date: date = None) -> Optional[StockIndexSpot]:
        """
        根据指数代码查询
        
        Args:
            code: 指数代码
            query_date: 查询日期
            
        Returns:
            指数行情实体
        """
        query = self.session.query(StockIndexSpot).filter(StockIndexSpot.code == code)
        if query_date:
            query = query.filter(StockIndexSpot.date == query_date)
        return query.first()
    
    def find_by_date(self, query_date: date) -> List[StockIndexSpot]:
        """
        根据日期查询所有指数
        
        Args:
            query_date: 查询日期
            
        Returns:
            指数列表
        """
        return self.session.query(StockIndexSpot).filter(
            StockIndexSpot.date == query_date
        ).all()
    
    def delete_by_date(self, query_date: date) -> int:
        """
        删除指定日期的指数数据
        
        Args:
            query_date: 日期
            
        Returns:
            删除数量
        """
        count = self.session.query(StockIndexSpot).filter(
            StockIndexSpot.date == query_date
        ).delete()
        self.session.commit()
        return count