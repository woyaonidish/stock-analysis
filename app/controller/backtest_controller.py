#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
回测API接口
"""

from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.service.backtest_service import BacktestService
from app.database import get_db


router = APIRouter(prefix="/backtest", tags=["回测"])


class BacktestRequest(BaseModel):
    """回测请求"""
    strategy_type: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0


@router.post("/run", summary="运行回测")
async def run_backtest(
    request: BacktestRequest,
    db = Depends(get_db)
):
    """运行策略回测"""
    try:
        service = BacktestService(db)
        
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
        
        result = service.backtest_strategy(
            request.strategy_type,
            start_date,
            end_date,
            request.initial_capital
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-all", summary="运行所有策略回测")
async def run_all_backtest(
    start_date: str = Query(..., description="开始日期"),
    end_date: str = Query(..., description="结束日期"),
    db = Depends(get_db)
):
    """运行所有策略回测"""
    try:
        service = BacktestService(db)
        
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        results = service.backtest_all_strategies(start, end)
        
        return {
            "code": 0,
            "message": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
