#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票技术指标实体类
"""

from datetime import date
from sqlalchemy import Column, String, Float, Date, SmallInteger
from app.database import Base


class StockIndicator(Base):
    """股票技术指标"""
    __tablename__ = 'cn_stock_indicators'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    
    # MACD
    macd = Column(Float, comment='dif')
    macds = Column(Float, comment='macd')
    macdh = Column(Float, comment='histogram')
    
    # KDJ
    kdjk = Column(Float, comment='kdjk')
    kdjd = Column(Float, comment='kdjd')
    kdjj = Column(Float, comment='kdjj')
    
    # BOLL
    boll_ub = Column(Float, comment='boll上轨')
    boll = Column(Float, comment='boll')
    boll_lb = Column(Float, comment='boll下轨')
    
    # TRIX
    trix = Column(Float, comment='trix')
    trix_20_sma = Column(Float, comment='trma')
    
    # CR
    cr = Column(Float, comment='cr')
    cr_ma1 = Column('cr-ma1', Float, comment='cr-ma1')
    cr_ma2 = Column('cr-ma2', Float, comment='cr-ma2')
    cr_ma3 = Column('cr-ma3', Float, comment='cr-ma3')
    
    # RSI
    rsi_6 = Column(Float, comment='rsi_6')
    rsi_12 = Column(Float, comment='rsi_12')
    rsi = Column(Float, comment='rsi')
    rsi_24 = Column(Float, comment='rsi_24')
    
    # VR
    vr = Column(Float, comment='vr')
    vr_6_sma = Column(Float, comment='mavr')
    
    # ATR
    tr = Column(Float, comment='tr')
    atr = Column(Float, comment='atr')
    
    # DMI
    pdi = Column(Float, comment='pdi')
    mdi = Column(Float, comment='mdi')
    dx = Column(Float, comment='dx')
    adx = Column(Float, comment='adx')
    adxr = Column(Float, comment='adxr')
    
    # WR
    wr_6 = Column(Float, comment='wr_6')
    wr_10 = Column(Float, comment='wr_10')
    wr_14 = Column(Float, comment='wr_14')
    
    # CCI
    cci = Column(Float, comment='cci')
    cci_84 = Column(Float, comment='cci_84')
    
    # DMA
    dma = Column(Float, comment='dma')
    dma_10_sma = Column(Float, comment='ama')
    
    # OBV
    obv = Column(Float, comment='obv')
    
    # SAR
    sar = Column(Float, comment='sar')
    
    # PSY
    psy = Column(Float, comment='psy')
    psyma = Column(Float, comment='psyma')
    
    # BRAR
    br = Column(Float, comment='br')
    ar = Column(Float, comment='ar')
    
    # EMV
    emv = Column(Float, comment='emv')
    emva = Column(Float, comment='emva')
    
    # BIAS
    bias = Column(Float, comment='bias')
    bias_12 = Column(Float, comment='bias_12')
    bias_24 = Column(Float, comment='bias_24')
    
    # MFI
    mfi = Column(Float, comment='mfi')
    mfisma = Column(Float, comment='mfisma')
    
    # VWMA
    vwma = Column(Float, comment='vwma')
    mvwma = Column(Float, comment='mvwma')
    
    # PPO
    ppo = Column(Float, comment='ppo')
    ppos = Column(Float, comment='ppos')
    ppoh = Column(Float, comment='ppoh')
    
    # STOCHRSI
    stochrsi_k = Column(Float, comment='stochrsi_k')
    stochrsi_d = Column(Float, comment='stochrsi_d')
    
    # WT
    wt1 = Column(Float, comment='wt1')
    wt2 = Column(Float, comment='wt2')
    
    # Supertrend
    supertrend_ub = Column(Float, comment='supertrend_ub')
    supertrend = Column(Float, comment='supertrend')
    supertrend_lb = Column(Float, comment='supertrend_lb')
    
    # ROC
    roc = Column(Float, comment='roc')
    rocma = Column(Float, comment='rocma')
    rocema = Column(Float, comment='rocema')
    
    # DPO
    dpo = Column(Float, comment='dpo')
    madpo = Column(Float, comment='madpo')
    
    # VHF
    vhf = Column(Float, comment='vhf')
    
    # RVI
    rvi = Column(Float, comment='rvi')
    rvis = Column(Float, comment='rvis')
    
    # FI
    fi = Column(Float, comment='fi')
    force_2 = Column(Float, comment='force_2')
    force_13 = Column(Float, comment='force_13')
    
    # ENE
    ene_ue = Column(Float, comment='ene上轨')
    ene = Column(Float, comment='ene')
    ene_le = Column(Float, comment='ene下轨')
    
    # TEMA
    tema = Column(Float, comment='tema')
    
    # VOL
    vol_5 = Column(Float, comment='vol_5')
    vol_10 = Column(Float, comment='vol_10')
    
    # MA
    ma6 = Column(Float, comment='ma6')
    ma10 = Column(Float, comment='ma10')
    ma12 = Column(Float, comment='ma12')
    ma20 = Column(Float, comment='ma20')
    ma24 = Column(Float, comment='ma24')
    ma50 = Column(Float, comment='ma50')
    ma200 = Column(Float, comment='ma200')
