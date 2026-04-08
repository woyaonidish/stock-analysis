#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指标数据API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd

from app.service.indicator_service import IndicatorService
from app.database import get_db


router = APIRouter(prefix="/indicators", tags=["指标数据"])


@router.get("/{code}", summary="获取股票指标")
async def get_indicator(
    code: str,
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """获取股票技术指标"""
    try:
        service = IndicatorService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        indicator = service.get_indicators(code, trade_date)
        
        if indicator:
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "code": indicator.code,
                    "date": str(indicator.date),
                    "macd": indicator.macd,
                    "macds": indicator.macds,
                    "macdh": indicator.macdh,
                    "kdjk": indicator.kdjk,
                    "kdjd": indicator.kdjd,
                    "kdjj": indicator.kdjj,
                    "rsi": indicator.rsi,
                    "rsi_6": indicator.rsi_6,
                    "rsi_12": indicator.rsi_12,
                    "rsi_24": indicator.rsi_24,
                    "atr": indicator.atr,
                    "cci": indicator.cci,
                    "wr_6": indicator.wr_6,
                    "wr_10": indicator.wr_10
                }
            }
        return {"code": 404, "message": "indicator not found", "data": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", summary="获取所有股票指标")
async def get_indicator_list(
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """获取指定日期的所有股票指标"""
    try:
        service = IndicatorService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        indicators = service.get_indicators_by_date(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": [
                {
                    "code": i.code,
                    "date": str(i.date),
                    "macd": i.macd,
                    "kdjk": i.kdjk,
                    "rsi": i.rsi,
                    "cci": i.cci
                }
                for i in indicators
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/buy", summary="获取买入信号")
async def get_buy_signals(
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """获取买入信号股票"""
    try:
        service = IndicatorService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        signals = service.guess_buy(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": [
                {"code": s.code, "date": str(s.date)}
                for s in signals
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/sell", summary="获取卖出信号")
async def get_sell_signals(
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """获取卖出信号股票"""
    try:
        service = IndicatorService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        signals = service.guess_sell(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": [
                {"code": s.code, "date": str(s.date)}
                for s in signals
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate/{code}", summary="计算并保存指标")
async def calculate_indicator(
    code: str,
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """计算并保存单只股票的指标"""
    try:
        service = IndicatorService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        indicator = service.calculate_and_save(code, trade_date)
        
        if indicator:
            return {
                "code": 0,
                "message": "success",
                "data": {"code": indicator.code}
            }
        return {"code": 500, "message": "calculate failed", "data": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
