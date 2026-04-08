#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
策略选股DAO
"""

from datetime import date
from typing import List, Type, Dict, Any
from sqlalchemy.orm import Session

from app.dao.base_dao import BaseDAO
from app.entity.stock_strategy import (
    StockStrategyBase, StockStrategyEnter, StockStrategyKeepIncreasing,
    StockStrategyParkingApron, StockStrategyBacktraceMA250,
    StockStrategyBreakthroughPlatform, StockStrategyLowBacktraceIncrease,
    StockStrategyTurtleTrade, StockStrategyHighTightFlag,
    StockStrategyClimaxLimitdown, StockStrategyLowATR,
    STRATEGY_TABLES
)


class StrategyDAO:
    """策略选股DAO工厂"""
    
    def __init__(self, session: Session):
        self.session = session
        self._dao_cache: Dict[str, BaseDAO] = {}
    
    def get_dao(self, strategy_type: str) -> BaseDAO:
        """
        获取指定策略类型的DAO
        
        Args:
            strategy_type: 策略类型
            
        Returns:
            DAO实例
        """
        if strategy_type not in self._dao_cache:
            model = STRATEGY_TABLES.get(strategy_type)
            if model is None:
                raise ValueError(f"未知的策略类型: {strategy_type}")
            self._dao_cache[strategy_type] = BaseDAO(model, self.session)
        return self._dao_cache[strategy_type]
    
    def find_by_strategy_type(self, strategy_type: str, query_date: date = None) -> List[Any]:
        """
        根据策略类型查询选股结果
        
        Args:
            strategy_type: 策略类型
            query_date: 查询日期
            
        Returns:
            选股结果列表
        """
        dao = self.get_dao(strategy_type)
        if query_date:
            return dao.find_by_date(query_date)
        return dao.find_all()
    
    def find_codes_by_strategy(self, strategy_type: str, query_date: date) -> List[str]:
        """
        根据策略类型查询股票代码列表
        
        Args:
            strategy_type: 策略类型
            query_date: 查询日期
            
        Returns:
            股票代码列表
        """
        dao = self.get_dao(strategy_type)
        model = STRATEGY_TABLES[strategy_type]
        results = self.session.query(model.code).filter(
            model.date == query_date
        ).all()
        return [r[0] for r in results]
    
    def delete_by_date(self, strategy_type: str, query_date: date) -> int:
        """
        根据日期删除策略数据
        
        Args:
            strategy_type: 策略类型
            query_date: 日期
            
        Returns:
            删除的记录数
        """
        dao = self.get_dao(strategy_type)
        return dao.delete_by_date(query_date)
    
    def count_by_strategy(self, strategy_type: str, query_date: date = None) -> int:
        """
        统计策略选股数量
        
        Args:
            strategy_type: 策略类型
            query_date: 查询日期
            
        Returns:
            记录数
        """
        dao = self.get_dao(strategy_type)
        if query_date:
            return dao.count(date=query_date)
        return dao.count()


# 各策略专用DAO类
class StrategyEnterDAO(BaseDAO[StockStrategyEnter]):
    """放量上涨策略DAO"""
    def __init__(self, session: Session):
        super().__init__(StockStrategyEnter, session)


class StrategyKeepIncreasingDAO(BaseDAO[StockStrategyKeepIncreasing]):
    """均线多头策略DAO"""
    def __init__(self, session: Session):
        super().__init__(StockStrategyKeepIncreasing, session)


class StrategyBreakthroughDAO(BaseDAO[StockStrategyBreakthroughPlatform]):
    """突破平台策略DAO"""
    def __init__(self, session: Session):
        super().__init__(StockStrategyBreakthroughPlatform, session)


class StrategyTurtleDAO(BaseDAO[StockStrategyTurtleTrade]):
    """海龟交易策略DAO"""
    def __init__(self, session: Session):
        super().__init__(StockStrategyTurtleTrade, session)
