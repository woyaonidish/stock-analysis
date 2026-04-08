#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票实时行情实体类
"""

from datetime import date, datetime
from sqlalchemy import Column, String, Float, BigInteger, Date, DateTime
from app.database import Base


class StockSpot(Base):
    """股票实时行情"""
    __tablename__ = 'cn_stock_spot'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    name = Column(String(20), comment='名称')
    new_price = Column(Float, comment='最新价')
    change_rate = Column(Float, comment='涨跌幅')
    ups_downs = Column(Float, comment='涨跌额')
    volume = Column(BigInteger, comment='成交量')
    deal_amount = Column(BigInteger, comment='成交额')
    amplitude = Column(Float, comment='振幅')
    turnoverrate = Column(Float, comment='换手率')
    volume_ratio = Column(Float, comment='量比')
    open_price = Column(Float, comment='今开')
    high_price = Column(Float, comment='最高')
    low_price = Column(Float, comment='最低')
    pre_close_price = Column(Float, comment='昨收')
    speed_increase = Column(Float, comment='涨速')
    speed_increase_5 = Column(Float, comment='5分钟涨跌')
    speed_increase_60 = Column(Float, comment='60日涨跌幅')
    speed_increase_all = Column(Float, comment='年初至今涨跌幅')
    dtsyl = Column(Float, comment='市盈率动')
    pe9 = Column(Float, comment='市盈率TTM')
    pe = Column(Float, comment='市盈率静')
    pbnewmrq = Column(Float, comment='市净率')
    basic_eps = Column(Float, comment='每股收益')
    bvps = Column(Float, comment='每股净资产')
    per_capital_reserve = Column(Float, comment='每股公积金')
    per_unassign_profit = Column(Float, comment='每股未分配利润')
    roe_weight = Column(Float, comment='加权净资产收益率')
    sale_gpr = Column(Float, comment='毛利率')
    debt_asset_ratio = Column(Float, comment='资产负债率')
    total_operate_income = Column(BigInteger, comment='营业收入')
    toi_yoy_ratio = Column(Float, comment='营业收入同比增长')
    parent_netprofit = Column(BigInteger, comment='归属净利润')
    netprofit_yoy_ratio = Column(Float, comment='归属净利润同比增长')
    report_date = Column(Date, comment='报告期')
    total_shares = Column(BigInteger, comment='总股本')
    free_shares = Column(BigInteger, comment='已流通股份')
    total_market_cap = Column(BigInteger, comment='总市值')
    free_cap = Column(BigInteger, comment='流通市值')
    industry = Column(String(20), comment='所处行业')
    listing_date = Column(Date, comment='上市时间')


class StockAttention(Base):
    """关注股票"""
    __tablename__ = 'cn_stock_attention'
    
    datetime = Column(DateTime, primary_key=True, comment='日期时间')
    code = Column(String(6), primary_key=True, comment='代码')
