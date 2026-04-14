#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
财务数据DAO
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app.dao.base_dao import BaseDAO
from app.entity.stock_financial import StockFinancial


class FinancialDAO(BaseDAO[StockFinancial]):
    """财务数据DAO"""
    
    def __init__(self, session: Session):
        super().__init__(StockFinancial, session)
    
    def find_by_code(self, code: str, report_date: date = None) -> Optional[StockFinancial]:
        """
        根据股票代码查询
        
        Args:
            code: 股票代码
            report_date: 报告期
            
        Returns:
            财务数据实体
        """
        query = self.session.query(StockFinancial).filter(StockFinancial.code == code)
        if report_date:
            query = query.filter(StockFinancial.report_date == report_date)
        return query.order_by(StockFinancial.report_date.desc()).first()
    
    def find_by_code_history(self, code: str, limit: int = 8) -> List[StockFinancial]:
        """
        查询股票历史财务数据
        
        Args:
            code: 股票代码
            limit: 返回数量
            
        Returns:
            财务数据列表
        """
        return self.session.query(StockFinancial).filter(
            StockFinancial.code == code
        ).order_by(StockFinancial.report_date.desc()).limit(limit).all()
    
    def find_by_report_date(self, report_date: date) -> List[StockFinancial]:
        """
        根据报告期查询所有股票财务数据
        
        Args:
            report_date: 报告期
            
        Returns:
            财务数据列表
        """
        return self.session.query(StockFinancial).filter(
            StockFinancial.report_date == report_date
        ).all()
    
    def delete_by_report_date(self, report_date: date) -> int:
        """
        删除指定报告期的财务数据
        
        Args:
            report_date: 报告期
            
        Returns:
            删除数量
        """
        count = self.session.query(StockFinancial).filter(
            StockFinancial.report_date == report_date
        ).delete()
        self.session.commit()
        return count
    
    def find_latest_report_date(self) -> Optional[date]:
        """
        获取最新报告期
        
        Returns:
            最新报告期日期
        """
        result = self.session.query(StockFinancial.report_date).order_by(
            StockFinancial.report_date.desc()
        ).first()
        return result[0] if result else None