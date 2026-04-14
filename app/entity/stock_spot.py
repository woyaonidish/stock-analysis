#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票实时行情实体类 - 适配 MOOTDX 数据格式
"""

from datetime import date, datetime
from sqlalchemy import Column, String, Float, BigInteger, Date, DateTime
from app.database import Base


class StockSpot(Base):
    """股票实时行情 - 基于 MOOTDX 数据"""
    __tablename__ = 'cn_stock_spot'
    
    # 主键
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    
    # 基本信息
    name = Column(String(20), comment='名称')
    
    # 行情数据 (MOOTDX quotes 支持的字段)
    open_price = Column(Float, comment='开盘价')
    close_price = Column(Float, comment='收盘价(最新价)')
    high_price = Column(Float, comment='最高价')
    low_price = Column(Float, comment='最低价')
    pre_close_price = Column(Float, comment='昨收价')
    volume = Column(BigInteger, comment='成交量')
    amount = Column(BigInteger, comment='成交额')
    
    # 五档行情
    bid1 = Column(Float, comment='买一价')
    bid1_vol = Column(BigInteger, comment='买一量')
    bid2 = Column(Float, comment='买二价')
    bid2_vol = Column(BigInteger, comment='买二量')
    bid3 = Column(Float, comment='买三价')
    bid3_vol = Column(BigInteger, comment='买三量')
    bid4 = Column(Float, comment='买四价')
    bid4_vol = Column(BigInteger, comment='买四量')
    bid5 = Column(Float, comment='买五价')
    bid5_vol = Column(BigInteger, comment='买五量')
    
    ask1 = Column(Float, comment='卖一价')
    ask1_vol = Column(BigInteger, comment='卖一量')
    ask2 = Column(Float, comment='卖二价')
    ask2_vol = Column(BigInteger, comment='卖二量')
    ask3 = Column(Float, comment='卖三价')
    ask3_vol = Column(BigInteger, comment='卖三量')
    ask4 = Column(Float, comment='卖四价')
    ask4_vol = Column(BigInteger, comment='卖四量')
    ask5 = Column(Float, comment='卖五价')
    ask5_vol = Column(BigInteger, comment='卖五量')


class StockAttention(Base):
    """关注股票"""
    __tablename__ = 'cn_stock_attention'
    
    datetime = Column(DateTime, primary_key=True, comment='日期时间')
    code = Column(String(6), primary_key=True, comment='代码')
