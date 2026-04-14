#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指数行情API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.service.index_service import IndexService
from app.database import get_db


router = APIRouter(prefix="/index", tags=["指数行情"])


# 响应模型
class IndexSpotResponse(BaseModel):
    """指数实时行情响应"""
    code: str
    name: str
    date: str
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    pre_close: float
    change_rate: float
    volume: int
    amount: int
    
    class Config:
        from_attributes = True


@router.get("/list", summary="获取指数列表")
async def get_index_list(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取指数列表"""
    try:
        service = IndexService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = service.get_index_list(trade_date)
        
        result = [
            {
                "code": item.code,
                "name": item.name,
                "date": str(item.date),
                "open_price": item.open_price,
                "close_price": item.close_price,
                "high_price": item.high_price,
                "low_price": item.low_price,
                "pre_close": item.pre_close,
                "change_rate": item.change_rate,
                "volume": item.volume,
                "amount": item.amount,
            }
            for item in data
        ]
        
        return {"code": 0, "message": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}", summary="获取指数详情")
async def get_index_detail(
    code: str,
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取单只指数详情"""
    try:
        service = IndexService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = service.get_index(code, trade_date)
        
        if data is None:
            return {"code": -1, "message": "指数不存在", "data": None}
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "code": data.code,
                "name": data.name,
                "date": str(data.date),
                "open_price": data.open_price,
                "close_price": data.close_price,
                "high_price": data.high_price,
                "low_price": data.low_price,
                "pre_close": data.pre_close,
                "change_rate": data.change_rate,
                "volume": data.volume,
                "amount": data.amount,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch", summary="抓取并保存指数数据")
async def fetch_and_save_index(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """抓取并保存指数实时行情"""
    try:
        service = IndexService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        count = await service.fetch_and_save_index_data(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": {"count": count}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))