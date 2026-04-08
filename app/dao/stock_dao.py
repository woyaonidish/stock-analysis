#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据DAO
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.dao.base_dao import BaseDAO
from app.entity.stock_spot import StockSpot, StockAttention


class StockDAO(BaseDAO[StockSpot]):
    """股票数据DAO"""
    
    def __init__(self, session: Session):
        super().__init__(StockSpot, session)
    
    def find_by_codes(self, codes: List[str], query_date: date = None) -> List[StockSpot]:
        """
        根据代码列表查询
        
        Args:
            codes: 代码列表
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        query = self.session.query(StockSpot).filter(StockSpot.code.in_(codes))
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        return query.all()
    
    def find_by_industry(self, industry: str, query_date: date = None) -> List[StockSpot]:
        """
        根据行业查询
        
        Args:
            industry: 行业名称
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        query = self.session.query(StockSpot).filter(StockSpot.industry == industry)
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        return query.all()
    
    def find_by_change_rate(self, min_rate: float = None, max_rate: float = None, 
                           query_date: date = None) -> List[StockSpot]:
        """
        根据涨跌幅范围查询
        
        Args:
            min_rate: 最小涨跌幅
            max_rate: 最大涨跌幅
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        query = self.session.query(StockSpot)
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        if min_rate is not None:
            query = query.filter(StockSpot.change_rate >= min_rate)
        if max_rate is not None:
            query = query.filter(StockSpot.change_rate <= max_rate)
        return query.all()
    
    def find_limit_up(self, query_date: date = None) -> List[StockSpot]:
        """
        查询涨停股票
        
        Args:
            query_date: 查询日期
            
        Returns:
            涨停股票列表
        """
        query = self.session.query(StockSpot).filter(StockSpot.change_rate >= 9.9)
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        return query.all()
    
    def find_limit_down(self, query_date: date = None) -> List[StockSpot]:
        """
        查询跌停股票
        
        Args:
            query_date: 查询日期
            
        Returns:
            跌停股票列表
        """
        query = self.session.query(StockSpot).filter(StockSpot.change_rate <= -9.9)
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        return query.all()
    
    def find_top_volume(self, limit: int = 100, query_date: date = None) -> List[StockSpot]:
        """
        查询成交量最大的股票
        
        Args:
            limit: 返回数量
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        query = self.session.query(StockSpot)
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        return query.order_by(StockSpot.volume.desc()).limit(limit).all()
    
    def find_top_amount(self, limit: int = 100, query_date: date = None) -> List[StockSpot]:
        """
        查询成交额最大的股票
        
        Args:
            limit: 返回数量
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        query = self.session.query(StockSpot)
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        return query.order_by(StockSpot.deal_amount.desc()).limit(limit).all()
    
    def find_st_stocks(self, query_date: date = None) -> List[StockSpot]:
        """
        查询ST股票
        
        Args:
            query_date: 查询日期
            
        Returns:
            ST股票列表
        """
        query = self.session.query(StockSpot).filter(
            or_(StockSpot.name.like('ST%'), StockSpot.name.like('*ST%'))
        )
        if query_date:
            query = query.filter(StockSpot.date == query_date)
        return query.all()


class StockAttentionDAO(BaseDAO[StockAttention]):
    """关注股票DAO"""
    
    def __init__(self, session: Session):
        super().__init__(StockAttention, session)
    
    def find_all_codes(self) -> List[str]:
        """
        获取所有关注的股票代码
        
        Returns:
            股票代码列表
        """
        results = self.session.query(StockAttention.code).distinct().all()
        return [r[0] for r in results]
    
    def is_attention(self, code: str) -> bool:
        """
        判断股票是否被关注
        
        Args:
            code: 股票代码
            
        Returns:
            是否被关注
        """
        return self.session.query(StockAttention).filter(
            StockAttention.code == code
        ).count() > 0
    
    def add_attention(self, code: str) -> StockAttention:
        """
        添加关注
        
        Args:
            code: 股票代码
            
        Returns:
            关注记录
        """
        from datetime import datetime
        attention = StockAttention(datetime=datetime.now(), code=code)
        return self.save(attention)
    
    def remove_attention(self, code: str) -> bool:
        """
        取消关注
        
        Args:
            code: 股票代码
            
        Returns:
            是否成功
        """
        count = self.session.query(StockAttention).filter(
            StockAttention.code == code
        ).delete()
        self.session.commit()
        return count > 0
