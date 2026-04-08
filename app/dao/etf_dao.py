#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETF数据DAO
"""

from datetime import date
from typing import List
from sqlalchemy.orm import Session

from app.dao.base_dao import BaseDAO
from app.entity.etf_spot import ETFSpot


class ETFDAO(BaseDAO[ETFSpot]):
    """ETF数据DAO"""
    
    def __init__(self, session: Session):
        super().__init__(ETFSpot, session)
    
    def find_by_codes(self, codes: List[str], query_date: date = None) -> List[ETFSpot]:
        """
        根据代码列表查询
        
        Args:
            codes: 代码列表
            query_date: 查询日期
            
        Returns:
            ETF列表
        """
        query = self.session.query(ETFSpot).filter(ETFSpot.code.in_(codes))
        if query_date:
            query = query.filter(ETFSpot.date == query_date)
        return query.all()
    
    def find_by_change_rate(self, min_rate: float = None, max_rate: float = None,
                           query_date: date = None) -> List[ETFSpot]:
        """
        根据涨跌幅范围查询
        
        Args:
            min_rate: 最小涨跌幅
            max_rate: 最大涨跌幅
            query_date: 查询日期
            
        Returns:
            ETF列表
        """
        query = self.session.query(ETFSpot)
        if query_date:
            query = query.filter(ETFSpot.date == query_date)
        if min_rate is not None:
            query = query.filter(ETFSpot.change_rate >= min_rate)
        if max_rate is not None:
            query = query.filter(ETFSpot.change_rate <= max_rate)
        return query.all()
    
    def find_top_volume(self, limit: int = 50, query_date: date = None) -> List[ETFSpot]:
        """
        查询成交量最大的ETF
        
        Args:
            limit: 返回数量
            query_date: 查询日期
            
        Returns:
            ETF列表
        """
        query = self.session.query(ETFSpot)
        if query_date:
            query = query.filter(ETFSpot.date == query_date)
        return query.order_by(ETFSpot.volume.desc()).limit(limit).all()
