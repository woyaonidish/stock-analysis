#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import pandas as pd

from app.service.stock_service import StockService
from app.database import get_db


router = APIRouter(prefix="/stocks", tags=["股票数据"])


# 响应模型
class StockSpotResponse(BaseModel):
    """股票实时行情响应"""
    code: str
    name: str
    date: str
    new_price: float
    change_rate: float
    change_amount: float
    volume: float
    amount: float
    open_price: float
    high_price: float
    low_price: float
    pre_close_price: float
    
    class Config:
        from_attributes = True


class StockHistRequest(BaseModel):
    """股票历史数据请求"""
    code: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: str = "daily"
    adjust: str = ""


class PageResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    data: List[dict]


@router.get("/list", summary="获取股票列表")
async def get_stock_list(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取股票列表"""
    try:
        service = StockService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = await service.get_stock_list(trade_date)
        
        if isinstance(data, pd.DataFrame):
            return {
                "code": 0,
                "message": "success",
                "data": data.to_dict(orient="records")
            }
        return {"code": 0, "message": "success", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}", summary="获取股票详情")
async def get_stock_detail(
    code: str,
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """获取股票详情"""
    try:
        service = StockService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        stock = service.get_stock_spot(code, trade_date)
        
        if stock:
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "code": stock.code,
                    "name": stock.name,
                    "date": str(stock.date),
                    "new_price": stock.new_price,
                    "change_rate": stock.change_rate,
                    "change_amount": stock.ups_downs,
                    "volume": stock.volume,
                    "amount": stock.deal_amount,
                    "open_price": stock.open_price,
                    "high_price": stock.high_price,
                    "low_price": stock.low_price,
                    "pre_close_price": stock.pre_close_price
                }
            }
        return {"code": 404, "message": "stock not found", "data": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/hist", summary="获取股票历史数据")
async def get_stock_hist(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期(YYYYMMDD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYYMMDD)"),
    period: str = Query("daily", description="周期: daily/weekly/monthly"),
    adjust: str = Query("", description="复权: ''/'qfq'/'hfq'"),
    db = Depends(get_db)
):
    """获取股票历史K线数据"""
    try:
        service = StockService(db)
        data = await service.get_stock_hist(code, start_date, end_date, period, adjust)
        
        if isinstance(data, pd.DataFrame) and not data.empty:
            return {
                "code": 0,
                "message": "success",
                "data": data.to_dict(orient="records")
            }
        return {"code": 0, "message": "no data", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/min", summary="获取股票分时数据")
async def get_stock_hist_min(
    code: str,
    period: str = Query("5", description="周期: 1/5/15/30/60分钟"),
    start_date: Optional[str] = Query(None, description="开始日期时间"),
    end_date: Optional[str] = Query(None, description="结束日期时间"),
    adjust: str = Query("", description="复权类型"),
    db = Depends(get_db)
):
    """获取股票分时数据"""
    try:
        service = StockService(db)
        data = await service.get_stock_hist_min(code, period, start_date, end_date, adjust)
        
        if isinstance(data, pd.DataFrame) and not data.empty:
            return {
                "code": 0,
                "message": "success",
                "data": data.to_dict(orient="records")
            }
        return {"code": 0, "message": "no data", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{keyword}", summary="搜索股票")
async def search_stocks(
    keyword: str,
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """搜索股票(按代码或名称)"""
    try:
        service = StockService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        stocks = service.search_stocks(keyword=keyword, trade_date=trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": [
                {
                    "code": s.code,
                    "name": s.name,
                    "new_price": s.new_price,
                    "change_rate": s.change_rate
                }
                for s in stocks
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch", summary="抓取并保存每日数据")
async def fetch_daily_data(
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """抓取并保存每日股票数据"""
    try:
        service = StockService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        count = await service.fetch_and_save_daily_data(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": {"count": count}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
