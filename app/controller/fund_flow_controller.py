#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
资金流向API接口
"""

from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.service.fund_flow_service import FundFlowService
from app.database import get_db


router = APIRouter(prefix="/fund-flow", tags=["资金流向"])


@router.get("/individual", summary="获取个股资金流向")
async def get_individual_fund_flow(
    indicator: str = Query("5日", description="时间周期: 今日/3日/5日/10日"),
    db = Depends(get_db)
):
    """获取个股资金流向排名"""
    try:
        service = FundFlowService(db)
        data = await service.get_individual_fund_flow(indicator)
        
        if not data.empty:
            return {
                "code": 0,
                "message": "success",
                "data": data.to_dict(orient="records")
            }
        return {"code": 0, "message": "no data", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sector", summary="获取板块资金流向")
async def get_sector_fund_flow(
    indicator: str = Query("10日", description="时间周期: 今日/5日/10日"),
    sector_type: str = Query("行业资金流", description="板块类型: 行业资金流/概念资金流/地域资金流"),
    db = Depends(get_db)
):
    """获取板块资金流向排名"""
    try:
        service = FundFlowService(db)
        data = await service.get_sector_fund_flow(indicator, sector_type)
        
        if not data.empty:
            return {
                "code": 0,
                "message": "success",
                "data": data.to_dict(orient="records")
            }
        return {"code": 0, "message": "no data", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch", summary="抓取并保存资金流向数据")
async def fetch_fund_flow_data(
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """抓取并保存资金流向数据"""
    try:
        service = FundFlowService(db)
        
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        result = await service.fetch_and_save_daily_data(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))