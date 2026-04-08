#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
其他股票相关实体类
"""

from datetime import date
from sqlalchemy import Column, String, Float, BigInteger, Date
from app.database import Base


class StockBonus(Base):
    """股票分红配送"""
    __tablename__ = 'cn_stock_bonus'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    name = Column(String(20), comment='名称')
    convertible_total_rate = Column(Float, comment='送转股份-送转总比例')
    convertible_rate = Column(Float, comment='送转股份-送转比例')
    convertible_transfer_rate = Column(Float, comment='送转股份-转股比例')
    bonusaward_rate = Column(Float, comment='现金分红-现金分红比例')
    bonusaward_yield = Column(Float, comment='现金分红-股息率')
    basic_eps = Column(Float, comment='每股收益')
    bvps = Column(Float, comment='每股净资产')
    per_capital_reserve = Column(Float, comment='每股公积金')
    per_unassign_profit = Column(Float, comment='每股未分配利润')
    netprofit_yoy_ratio = Column(Float, comment='净利润同比增长')
    total_shares = Column(BigInteger, comment='总股本')
    plan_date = Column(Date, comment='预案公告日')
    record_date = Column(Date, comment='股权登记日')
    ex_dividend_date = Column(Date, comment='除权除息日')
    progress = Column(String(50), comment='方案进度')
    report_date = Column(Date, comment='最新公告日期')


class StockLhb(Base):
    """股票龙虎榜"""
    __tablename__ = 'cn_stock_lhb'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    name = Column(String(20), comment='名称')
    ranking_times = Column(Date, comment='上榜日')
    interpret = Column(String(255), comment='解读')
    new_price = Column(Float, comment='收盘价')
    change_rate = Column(Float, comment='涨跌幅')
    net_amount_buy = Column(Float, comment='龙虎榜净买额')
    sum_buy = Column(Float, comment='龙虎榜买入额')
    sum_sell = Column(Float, comment='龙虎榜卖出额')
    lhb_amount = Column(Float, comment='龙虎榜成交额')
    market_amount = Column(Float, comment='市场总成交额')
    net_amount_rate = Column(Float, comment='净买额占总成交比')
    sum_rate = Column(Float, comment='成交额占总成交比')
    turnoverrate = Column(Float, comment='换手率')
    free_cap = Column(BigInteger, comment='流通市值')
    reason = Column(String(2000), comment='上榜原因')
    ranking_after_1 = Column(Float, comment='上榜后1日')
    ranking_after_2 = Column(Float, comment='上榜后2日')
    ranking_after_5 = Column(Float, comment='上榜后5日')
    ranking_after_10 = Column(Float, comment='上榜后10日')


class StockBlocktrade(Base):
    """股票大宗交易"""
    __tablename__ = 'cn_stock_blocktrade'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    name = Column(String(20), comment='名称')
    new_price = Column(Float, comment='收盘价')
    change_rate = Column(Float, comment='涨跌幅')
    average_price = Column(Float, comment='成交均价')
    overflow_rate = Column(Float, comment='折溢率')
    trade_number = Column(Float, comment='成交笔数')
    sum_volume = Column(Float, comment='成交总量')
    sum_turnover = Column(Float, comment='成交总额')
    turnover_market_rate = Column(Float, comment='成交占比流通市值')


class StockBacktestData(Base):
    """股票回测数据"""
    __tablename__ = 'cn_stock_backtest_data'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    # 100个收益率字段，使用动态方式生成
    for i in range(1, 101):
        locals()[f'rate_{i}'] = Column(Float, comment=f'{i}日收益率')


class StockHistData(Base):
    """股票历史数据（用于缓存）"""
    __tablename__ = 'cn_stock_hist'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    open = Column(Float, comment='开盘')
    close = Column(Float, comment='收盘')
    high = Column(Float, comment='最高')
    low = Column(Float, comment='最低')
    volume = Column(BigInteger, comment='成交量')
    amount = Column(BigInteger, comment='成交额')
    amplitude = Column(Float, comment='振幅')
    quote_change = Column(Float, comment='涨跌幅')
    ups_downs = Column(Float, comment='涨跌额')
    turnover = Column(Float, comment='换手率')
