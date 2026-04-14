#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
其他DAO模块
"""

from datetime import date
from typing import List
from sqlalchemy.orm import Session

from app.dao.base_dao import BaseDAO
from app.entity.stock_pattern import StockPattern
from app.entity.stock_selection import StockSelection
from app.entity.stock_other import StockBonus, StockLhb, StockBlocktrade, StockBacktestData


class PatternDAO(BaseDAO[StockPattern]):
    """K线形态DAO"""
    def __init__(self, session: Session):
        super().__init__(StockPattern, session)
    
    def find_by_pattern(self, pattern_name: str, query_date: date) -> List[StockPattern]:
        """根据形态名称查询"""
        if not hasattr(StockPattern, pattern_name):
            raise ValueError(f"未知的形态: {pattern_name}")
        
        pattern_col = getattr(StockPattern, pattern_name)
        # 买入信号 (正数) 或 卖出信号 (负数)
        return self.session.query(StockPattern).filter(
            StockPattern.date == query_date,
            pattern_col != 0
        ).all()
    
    def find_buy_patterns(self, query_date: date) -> List[StockPattern]:
        """查询出现买入形态的股票"""
        # 这里简化处理，实际需要遍历所有形态字段
        return self.session.query(StockPattern).filter(
            StockPattern.date == query_date
        ).all()


class SelectionDAO(BaseDAO[StockSelection]):
    """综合选股DAO"""
    def __init__(self, session: Session):
        super().__init__(StockSelection, session)
    
    def find_by_industry(self, industry: str, query_date: date = None) -> List[StockSelection]:
        """根据行业查询"""
        query = self.session.query(StockSelection).filter(
            StockSelection.industry == industry
        )
        if query_date:
            query = query.filter(StockSelection.date == query_date)
        return query.all()
    
    def find_by_concept(self, concept: str, query_date: date = None) -> List[StockSelection]:
        """根据概念查询"""
        query = self.session.query(StockSelection).filter(
            StockSelection.concept.like(f'%{concept}%')
        )
        if query_date:
            query = query.filter(StockSelection.date == query_date)
        return query.all()


class BacktestDAO(BaseDAO[StockBacktestData]):
    """回测数据DAO"""
    def __init__(self, session: Session):
        super().__init__(StockBacktestData, session)


class LhbDAO(BaseDAO[StockLhb]):
    """龙虎榜DAO"""
    def __init__(self, session: Session):
        super().__init__(StockLhb, session)


class BlocktradeDAO(BaseDAO[StockBlocktrade]):
    """大宗交易DAO"""
    def __init__(self, session: Session):
        super().__init__(StockBlocktrade, session)


class BonusDAO(BaseDAO[StockBonus]):
    """分红配送DAO"""
    def __init__(self, session: Session):
        super().__init__(StockBonus, session)
