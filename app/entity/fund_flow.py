#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票资金流向实体类
"""

from datetime import date
from sqlalchemy import Column, String, Float, BigInteger, Date
from app.database import Base


class StockFundFlow(Base):
    """股票资金流向"""
    __tablename__ = 'cn_stock_fund_flow'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    name = Column(String(20), comment='名称')
    new_price = Column(Float, comment='最新价')
    change_rate = Column(Float, comment='今日涨跌幅')
    fund_amount = Column(BigInteger, comment='今日主力净流入-净额')
    fund_rate = Column(Float, comment='今日主力净流入-净占比')
    fund_amount_super = Column(BigInteger, comment='今日超大单净流入-净额')
    fund_rate_super = Column(Float, comment='今日超大单净流入-净占比')
    fund_amount_large = Column(BigInteger, comment='今日大单净流入-净额')
    fund_rate_large = Column(Float, comment='今日大单净流入-净占比')
    fund_amount_medium = Column(BigInteger, comment='今日中单净流入-净额')
    fund_rate_medium = Column(Float, comment='今日中单净流入-净占比')
    fund_amount_small = Column(BigInteger, comment='今日小单净流入-净额')
    fund_rate_small = Column(Float, comment='今日小单净流入-净占比')
    # 3日数据
    change_rate_3 = Column(Float, comment='3日涨跌幅')
    fund_amount_3 = Column(BigInteger, comment='3日主力净流入-净额')
    fund_rate_3 = Column(Float, comment='3日主力净流入-净占比')
    # 5日数据
    change_rate_5 = Column(Float, comment='5日涨跌幅')
    fund_amount_5 = Column(BigInteger, comment='5日主力净流入-净额')
    fund_rate_5 = Column(Float, comment='5日主力净流入-净占比')
    # 10日数据
    change_rate_10 = Column(Float, comment='10日涨跌幅')
    fund_amount_10 = Column(BigInteger, comment='10日主力净流入-净额')
    fund_rate_10 = Column(Float, comment='10日主力净流入-净占比')


class StockFundFlowIndustry(Base):
    """行业资金流向"""
    __tablename__ = 'cn_stock_fund_flow_industry'
    
    date = Column(Date, primary_key=True, comment='日期')
    name = Column(String(30), primary_key=True, comment='名称')
    change_rate = Column(Float, comment='今日涨跌幅')
    fund_amount = Column(BigInteger, comment='今日主力净流入-净额')
    fund_rate = Column(Float, comment='今日主力净流入-净占比')
    fund_amount_super = Column(BigInteger, comment='今日超大单净流入-净额')
    fund_rate_super = Column(Float, comment='今日超大单净流入-净占比')
    stock_name = Column(String(20), comment='今日主力净流入最大股')


class StockFundFlowConcept(Base):
    """概念资金流向"""
    __tablename__ = 'cn_stock_fund_flow_concept'
    
    date = Column(Date, primary_key=True, comment='日期')
    name = Column(String(30), primary_key=True, comment='名称')
    change_rate = Column(Float, comment='今日涨跌幅')
    fund_amount = Column(BigInteger, comment='今日主力净流入-净额')
    fund_rate = Column(Float, comment='今日主力净流入-净占比')
    fund_amount_super = Column(BigInteger, comment='今日超大单净流入-净额')
    fund_rate_super = Column(Float, comment='今日超大单净流入-净占比')
    stock_name = Column(String(20), comment='今日主力净流入最大股')
