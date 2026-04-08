#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据传输对象 - 响应类
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar('T')


class BaseResponse(BaseModel):
    """基础响应"""
    code: int = 200
    message: str = "success"


class DataResponse(BaseResponse, Generic[T]):
    """单数据响应"""
    data: Optional[T] = None


class ListResponse(BaseResponse, Generic[T]):
    """列表响应"""
    data: List[T] = []
    total: int = 0


class PageResponse(BaseResponse, Generic[T]):
    """分页响应"""
    data: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class StockResponse(BaseModel):
    """股票数据响应"""
    date: str
    code: str
    name: str
    new_price: Optional[float] = None
    change_rate: Optional[float] = None
    ups_downs: Optional[float] = None
    volume: Optional[int] = None
    deal_amount: Optional[int] = None
    amplitude: Optional[float] = None
    turnoverrate: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    pre_close_price: Optional[float] = None
    total_market_cap: Optional[int] = None
    free_cap: Optional[int] = None
    industry: Optional[str] = None


class ETFResponse(BaseModel):
    """ETF数据响应"""
    date: str
    code: str
    name: str
    new_price: Optional[float] = None
    change_rate: Optional[float] = None
    volume: Optional[int] = None
    deal_amount: Optional[int] = None
    turnoverrate: Optional[float] = None
    total_market_cap: Optional[int] = None
    free_cap: Optional[int] = None


class IndicatorResponse(BaseModel):
    """技术指标响应"""
    date: str
    code: str
    name: Optional[str] = None
    macd: Optional[float] = None
    macds: Optional[float] = None
    macdh: Optional[float] = None
    kdjk: Optional[float] = None
    kdjd: Optional[float] = None
    kdjj: Optional[float] = None
    boll_ub: Optional[float] = None
    boll: Optional[float] = None
    boll_lb: Optional[float] = None
    rsi: Optional[float] = None
    rsi_6: Optional[float] = None
    rsi_12: Optional[float] = None
    atr: Optional[float] = None
    cci: Optional[float] = None
    wr_6: Optional[float] = None
    vr: Optional[float] = None


class StrategyResponse(BaseModel):
    """策略选股响应"""
    date: str
    code: str
    name: Optional[str] = None
    strategy_type: str
    new_price: Optional[float] = None
    change_rate: Optional[float] = None


class PatternResponse(BaseModel):
    """K线形态响应"""
    date: str
    code: str
    name: Optional[str] = None
    patterns: dict = {}


class BacktestResponse(BaseModel):
    """回测响应"""
    date: str
    code: str
    name: Optional[str] = None
    rates: List[Optional[float]] = []


class FundFlowResponse(BaseModel):
    """资金流向响应"""
    date: Optional[str] = None
    code: str
    name: str
    new_price: Optional[float] = None
    change_rate: Optional[float] = None
    fund_amount: Optional[int] = None
    fund_rate: Optional[float] = None
    fund_amount_super: Optional[int] = None
    fund_rate_super: Optional[float] = None


class SelectionResponse(BaseModel):
    """综合选股响应"""
    date: str
    code: str
    name: str
    new_price: Optional[float] = None
    change_rate: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    total_market_cap: Optional[int] = None
    industry: Optional[str] = None
    concept: Optional[str] = None
