#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技术指标DAO
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.dao.base_dao import BaseDAO
from app.entity.stock_indicator import StockIndicator


class IndicatorDAO(BaseDAO[StockIndicator]):
    """技术指标DAO"""
    
    def __init__(self, session: Session):
        super().__init__(StockIndicator, session)
    
    def find_buy_signals(self, query_date: date) -> List[StockIndicator]:
        """
        查询买入信号股票
        KDJ超买: K>=80, D>=70, J>=100
        RSI超买: RSI_6>=80
        CCI超买: CCI>=100
        CR高位: CR>=300
        WR超买: WR_6>=-20
        VR高位: VR>=160
        
        Args:
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        return self.session.query(StockIndicator).filter(
            and_(
                StockIndicator.date == query_date,
                StockIndicator.kdjk >= 80,
                StockIndicator.kdjd >= 70,
                StockIndicator.kdjj >= 100,
                StockIndicator.rsi_6 >= 80,
                StockIndicator.cci >= 100,
                StockIndicator.cr >= 300,
                StockIndicator.wr_6 >= -20,
                StockIndicator.vr >= 160
            )
        ).all()
    
    def find_sell_signals(self, query_date: date) -> List[StockIndicator]:
        """
        查询卖出信号股票
        KDJ超卖: K<20, D<30, J<10
        RSI超卖: RSI_6<20
        CCI超卖: CCI<-100
        CR低位: CR<40
        WR超卖: WR_6<-80
        VR低位: VR<40
        
        Args:
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        return self.session.query(StockIndicator).filter(
            and_(
                StockIndicator.date == query_date,
                StockIndicator.kdjk < 20,
                StockIndicator.kdjd < 30,
                StockIndicator.kdjj < 10,
                StockIndicator.rsi_6 < 20,
                StockIndicator.cci < -100,
                StockIndicator.cr < 40,
                StockIndicator.wr_6 < -80,
                StockIndicator.vr < 40
            )
        ).all()
    
    def find_macd_golden_cross(self, query_date: date) -> List[StockIndicator]:
        """
        查询MACD金叉股票
        
        Args:
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        return self.session.query(StockIndicator).filter(
            and_(
                StockIndicator.date == query_date,
                StockIndicator.macd > 0,
                StockIndicator.macdh > 0
            )
        ).all()
    
    def find_kdj_golden_cross(self, query_date: date) -> List[StockIndicator]:
        """
        查询KDJ金叉股票
        
        Args:
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        return self.session.query(StockIndicator).filter(
            and_(
                StockIndicator.date == query_date,
                StockIndicator.kdjk > StockIndicator.kdjd,
                StockIndicator.kdjj > StockIndicator.kdjk
            )
        ).all()
    
    def find_boll_breakout(self, query_date: date) -> List[StockIndicator]:
        """
        查询布林带突破上轨股票
        
        Args:
            query_date: 查询日期
            
        Returns:
            股票列表
        """
        # 需要关联股票表获取收盘价
        from app.entity.stock_spot import StockSpot
        return self.session.query(StockIndicator).join(
            StockSpot, and_(
                StockIndicator.date == StockSpot.date,
                StockIndicator.code == StockSpot.code
            )
        ).filter(
            and_(
                StockIndicator.date == query_date,
                StockSpot.new_price > StockIndicator.boll_ub
            )
        ).all()
