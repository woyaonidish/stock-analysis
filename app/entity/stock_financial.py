#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票财务数据实体类 - 精简核心字段
"""

from datetime import date
from sqlalchemy import Column, String, Float, BigInteger, Date, Integer
from app.database import Base


class StockFinancial(Base):
    """股票财务数据 - 精简核心指标"""
    __tablename__ = 'cn_stock_financial'
    
    # 主键
    report_date = Column(Date, primary_key=True, comment='报告期')
    code = Column(String(6), primary_key=True, comment='股票代码')
    
    # 每股指标
    eps = Column(Float, comment='基本每股收益')
    eps_deducted = Column(Float, comment='扣非每股收益')
    bvps = Column(Float, comment='每股净资产')
    cfps = Column(Float, comment='每股经营现金流')
    
    # 盈利能力
    roe = Column(Float, comment='净资产收益率(%)')
    roe_weighted = Column(Float, comment='加权净资产收益率(%)')
    net_profit_margin = Column(Float, comment='销售净利率(%)')
    gross_profit_margin = Column(Float, comment='销售毛利率(%)')
    
    # 成长能力
    revenue_growth = Column(Float, comment='营业收入增长率(%)')
    net_profit_growth = Column(Float, comment='净利润增长率(%)')
    
    # 资产负债
    debt_ratio = Column(Float, comment='资产负债率(%)')
    current_ratio = Column(Float, comment='流动比率')
    quick_ratio = Column(Float, comment='速动比率')
    
    # 核心财务数据（万元）
    revenue = Column(BigInteger, comment='营业收入(万元)')
    operating_profit = Column(BigInteger, comment='营业利润(万元)')
    net_profit = Column(BigInteger, comment='净利润(万元)')
    net_profit_parent = Column(BigInteger, comment='归母净利润(万元)')
    net_profit_deducted = Column(BigInteger, comment='扣非净利润(万元)')
    total_assets = Column(BigInteger, comment='资产总计(万元)')
    total_liability = Column(BigInteger, comment='负债合计(万元)')
    net_assets = Column(BigInteger, comment='净资产(万元)')
    
    # 现金流（万元）
    operating_cf = Column(BigInteger, comment='经营活动现金流净额(万元)')
    investing_cf = Column(BigInteger, comment='投资活动现金流净额(万元)')
    financing_cf = Column(BigInteger, comment='筹资活动现金流净额(万元)')
    
    # 估值指标
    pe_ratio = Column(Float, comment='市盈率(动态)')
    pb_ratio = Column(Float, comment='市净率')
    
    # 股本数据
    total_shares = Column(BigInteger, comment='总股本(股)')
    float_shares_a = Column(BigInteger, comment='流通A股(股)')