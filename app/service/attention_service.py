#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关注股票服务
"""

from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.dao.stock_dao import StockAttentionDAO, StockDAO
from app.entity.stock_spot import StockAttention, StockSpot
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AttentionService:
    """关注股票服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.attention_dao = StockAttentionDAO(self.session)
        self.stock_dao = StockDAO(self.session)
    
    def get_attention_list(self) -> List[str]:
        """
        获取关注股票代码列表
        
        Returns:
            股票代码列表
        """
        return self.attention_dao.find_all_codes()
    
    def get_attention_stocks(self, query_date: date = None) -> List[dict]:
        """
        获取关注股票的行情信息
        
        Args:
            query_date: 查询日期
            
        Returns:
            关注股票行情列表
        """
        if query_date is None:
            query_date = date.today()
        
        codes = self.attention_dao.find_all_codes()
        if not codes:
            return []
        
        result = []
        for code in codes:
            stock = self.stock_dao.find_by_id(date=query_date, code=code)
            if stock:
                result.append({
                    'code': stock.code,
                    'name': stock.name,
                    'date': str(stock.date),
                    'close_price': stock.close_price,
                    'change_rate': self._calc_change_rate(stock),
                    'volume': stock.volume,
                    'amount': stock.amount
                })
        
        return result
    
    def _calc_change_rate(self, stock: StockSpot) -> float:
        """计算涨跌幅"""
        if stock.pre_close_price and stock.pre_close_price > 0:
            return round((stock.close_price - stock.pre_close_price) / stock.pre_close_price * 100, 2)
        return 0.0
    
    def is_attention(self, code: str) -> bool:
        """
        判断股票是否被关注
        
        Args:
            code: 股票代码
            
        Returns:
            是否被关注
        """
        return self.attention_dao.is_attention(code)
    
    def add_attention(self, code: str) -> bool:
        """
        添加关注
        
        Args:
            code: 股票代码
            
        Returns:
            是否成功
        """
        try:
            # 检查是否已关注
            if self.attention_dao.is_attention(code):
                logger.warning(f"股票 {code} 已被关注")
                return False
            
            self.attention_dao.add_attention(code)
            logger.info(f"添加关注股票 {code} 成功")
            return True
        except Exception as e:
            logger.error(f"添加关注股票 {code} 失败: {e}")
            return False
    
    def remove_attention(self, code: str) -> bool:
        """
        取消关注
        
        Args:
            code: 股票代码
            
        Returns:
            是否成功
        """
        try:
            result = self.attention_dao.remove_attention(code)
            if result:
                logger.info(f"取消关注股票 {code} 成功")
            else:
                logger.warning(f"股票 {code} 未被关注")
            return result
        except Exception as e:
            logger.error(f"取消关注股票 {code} 失败: {e}")
            return False
    
    def clear_all_attentions(self) -> int:
        """
        清空所有关注
        
        Returns:
            清空的记录数
        """
        codes = self.attention_dao.find_all_codes()
        count = 0
        for code in codes:
            if self.attention_dao.remove_attention(code):
                count += 1
        logger.info(f"清空所有关注，共 {count} 条")
        return count
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()