#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETF数据API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd

from app.service.etf_service import ETFService
from app.database import get_db


router = APIRouter(prefix="/etf", tags=["ETF数据"])


@router.get("/list", summary="获取ETF列表")
async def get_etf_list(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取ETF列表"""
    try:
        service = ETFService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = await service.get_etf_list(trade_date)
        
        if isinstance(data, pd.DataFrame):
            return {
                "code": 0,
                "message": "success",
                "data": data.to_dict(orient="records")
            }
        return {"code": 0, "message": "success", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}", summary="获取ETF详情")
async def get_etf_detail(
    code: str,
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """获取ETF详情"""
    try:
        service = ETFService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        etf = service.get_etf_spot(code, trade_date)
        
        if etf:
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "code": etf.code,
                    "name": etf.name,
                    "date": str(etf.date),
                    "new_price": etf.new_price,
                    "change_rate": etf.change_rate,
                    "change_amount": etf.change_amount,
                    "volume": etf.volume,
                    "amount": etf.amount
                }
            }
        return {"code": 404, "message": "ETF not found", "data": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/hist", summary="获取ETF历史数据")
async def get_etf_hist(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期(YYYYMMDD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYYMMDD)"),
    period: str = Query("daily", description="周期: daily/weekly/monthly"),
    adjust: str = Query("", description="复权: ''/'qfq'/'hfq'"),
    db = Depends(get_db)
):
    """获取ETF历史K线数据"""
    try:
        service = ETFService(db)
        data = await service.get_etf_hist(code, start_date, end_date, period, adjust)
        
        if isinstance(data, pd.DataFrame) and not data.empty:
            return {
                "code": 0,
                "message": "success",
                "data": data.to_dict(orient="records")
            }
        return {"code": 0, "message": "no data", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch", summary="抓取并保存每日数据")
async def fetch_daily_data(
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """抓取并保存每日ETF数据"""
    try:
        service = ETFService(db)
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