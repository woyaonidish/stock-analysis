#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指数实时行情实体类 - 基于 MOOTDX 数据
"""

from datetime import date
from sqlalchemy import Column, String, Float, BigInteger, Date
from app.database import Base


class StockIndexSpot(Base):
    """指数实时行情 - 基于 MOOTDX index 数据"""
    __tablename__ = 'cn_stock_index_spot'
    
    # 主键
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='指数代码')
    
    # 基本信息
    name = Column(String(20), comment='指数名称')
    
    # 行情数据
    open_price = Column(Float, comment='开盘价')
    close_price = Column(Float, comment='收盘价(最新价)')
    high_price = Column(Float, comment='最高价')
    low_price = Column(Float, comment='最低价')
    volume = Column(BigInteger, comment='成交量')
    amount = Column(BigInteger, comment='成交额')
    
    # 涨跌数据（计算得出）
    pre_close = Column(Float, comment='昨收价')
    change_rate = Column(Float, comment='涨跌幅(%)')