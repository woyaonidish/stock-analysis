#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETF实时行情实体类
"""

from datetime import date
from sqlalchemy import Column, String, Float, BigInteger, Date
from app.database import Base


class ETFSpot(Base):
    """ETF实时行情"""
    __tablename__ = 'cn_etf_spot'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    name = Column(String(20), comment='名称')
    new_price = Column(Float, comment='最新价')
    change_rate = Column(Float, comment='涨跌幅')
    ups_downs = Column(Float, comment='涨跌额')
    volume = Column(BigInteger, comment='成交量')
    deal_amount = Column(BigInteger, comment='成交额')
    open_price = Column(Float, comment='开盘价')
    high_price = Column(Float, comment='最高价')
    low_price = Column(Float, comment='最低价')
    pre_close_price = Column(Float, comment='昨收')
    turnoverrate = Column(Float, comment='换手率')
    total_market_cap = Column(BigInteger, comment='总市值')
    free_cap = Column(BigInteger, comment='流通市值')
