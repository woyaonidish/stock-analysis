#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票综合选股实体类
"""

from datetime import date
from sqlalchemy import Column, String, Float, BigInteger, Date
from app.database import Base


class StockSelection(Base):
    """综合选股"""
    __tablename__ = 'cn_stock_selection'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    name = Column(String(20), comment='名称')
    new_price = Column(Float, comment='最新价')
    change_rate = Column(Float, comment='涨跌幅')
    volume_ratio = Column(Float, comment='量比')
    high_price = Column(Float, comment='最高价')
    low_price = Column(Float, comment='最低价')
    pre_close_price = Column(Float, comment='昨收价')
    volume = Column(BigInteger, comment='成交量')
    deal_amount = Column(BigInteger, comment='成交额')
    turnoverrate = Column(Float, comment='换手率')
    listing_date = Column(Date, comment='上市时间')
    industry = Column(String(50), comment='行业')
    area = Column(String(50), comment='地区')
    concept = Column(String(800), comment='概念')
    style = Column(String(255), comment='板块')
    is_hs300 = Column(String(2), comment='沪300')
    is_sz50 = Column(String(2), comment='上证50')
    is_zz500 = Column(String(2), comment='中证500')
    is_zz1000 = Column(String(2), comment='中证1000')
    is_cy50 = Column(String(2), comment='创业板50')
    pe9 = Column(Float, comment='市盈率TTM')
    pbnewmrq = Column(Float, comment='市净率MRQ')
    pettmdeducted = Column(Float, comment='市盈率TTM扣非')
    ps9 = Column(Float, comment='市销率TTM')
    pcfjyxjl9 = Column(Float, comment='市现率TTM')
    predict_pe_syear = Column(Float, comment='预测市盈率今年')
    predict_pe_nyear = Column(Float, comment='预测市盈率明年')
    total_market_cap = Column(BigInteger, comment='总市值')
    free_cap = Column(BigInteger, comment='流通市值')
    dtsyl = Column(Float, comment='动态市盈率')
    ycpeg = Column(Float, comment='预测PEG')
    enterprise_value_multiple = Column(Float, comment='企业价值倍数')
    basic_eps = Column(Float, comment='每股收益')
    bvps = Column(Float, comment='每股净资产')
    per_netcash_operate = Column(Float, comment='每股经营现金流')
    per_fcfe = Column(Float, comment='每股自由现金流')
