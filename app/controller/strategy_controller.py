#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
策略选股API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.service.strategy_service import StrategyService
from app.database import get_db


router = APIRouter(prefix="/strategy", tags=["策略选股"])


class StrategyRunRequest(BaseModel):
    """策略运行请求"""
    strategy_type: str
    trade_date: Optional[str] = None


@router.get("/types", summary="获取策略类型列表")
async def get_strategy_types():
    """获取支持的策略类型"""
    return {
        "code": 0,
        "message": "success",
        "data": [
            {"type": StrategyService.STRATEGY_VOLUME_UP, "name": "放量上涨"},
            {"type": StrategyService.STRATEGY_BREAKTHROUGH, "name": "突破平台"},
            {"type": StrategyService.STRATEGY_LOW_ATR, "name": "低ATR"},
            {"type": StrategyService.STRATEGY_TURTLE, "name": "海龟交易"},
            {"type": StrategyService.STRATEGY_HIGH_TIGHT_FLAG, "name": "高紧旗"},
            {"type": StrategyService.STRATEGY_PARKING_APRON, "name": "停机坪"},
            {"type": StrategyService.STRATEGY_KEEP_INCREASING, "name": "持续上涨"}
        ]
    }


@router.get("/{strategy_type}", summary="获取策略结果")
async def get_strategy_results(
    strategy_type: str,
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """获取策略选股结果"""
    try:
        service = StrategyService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        results = service.get_strategy_results(strategy_type, trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": [
                {
                    "code": r.code,
                    "date": str(r.date),
                    "strategy_type": r.strategy_type,
                    "score": r.score
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", summary="运行策略")
async def run_strategy(
    request: StrategyRunRequest,
    db = Depends(get_db)
):
    """运行策略选股"""
    try:
        service = StrategyService(db)
        
        if request.trade_date:
            trade_date = datetime.strptime(request.trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        results = service.run_strategy(request.strategy_type, trade_date)
        count = service.save_strategy_results(results)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "strategy_type": request.strategy_type,
                "trade_date": str(trade_date),
                "count": count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-all", summary="运行所有策略")
async def run_all_strategies(
    trade_date: Optional[str] = Query(None, description="交易日期"),
    db = Depends(get_db)
):
    """运行所有策略"""
    try:
        service = StrategyService(db)
        
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        results = service.run_all_strategies(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
