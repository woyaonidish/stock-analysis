#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
K线形态识别API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.service.pattern_service import PatternService
from app.database import get_db


router = APIRouter(prefix="/patterns", tags=["K线形态"])


# 响应模型
class PatternResponse(BaseModel):
    """形态识别响应"""
    code: str
    date: str
    patterns: dict
    
    class Config:
        from_attributes = True


@router.get("/{code}", summary="获取股票形态")
async def get_patterns(
    code: str,
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取单只股票的K线形态"""
    try:
        service = PatternService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = service.get_patterns(code, trade_date)
        
        if data is None:
            return {"code": -1, "message": "形态数据不存在", "data": None}
        
        # 提取非零形态字段
        patterns = {}
        for attr in ['doji', 'hammer', 'inverted_hammer', 'engulfing_pattern',
                     'morning_star', 'evening_star', 'three_white_soldiers',
                     'three_black_crows', 'dark_cloud_cover', 'piercing_pattern',
                     'hanging_man', 'shooting_star', 'abandoned_baby', 'dragonfly_doji',
                     'gravestone_doji', 'harami_pattern', 'harami_cross_pattern']:
            value = getattr(data, attr, 0)
            if value != 0:
                patterns[attr] = value
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "code": data.code,
                "date": str(data.date),
                "patterns": patterns
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", summary="获取形态列表")
async def get_pattern_list(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取指定日期的所有股票形态"""
    try:
        service = PatternService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = service.get_all_patterns(trade_date)
        
        result = []
        for item in data:
            # 提取非零形态字段
            patterns = {}
            for attr in ['doji', 'hammer', 'inverted_hammer', 'engulfing_pattern',
                         'morning_star', 'evening_star', 'three_white_soldiers',
                         'three_black_crows', 'dark_cloud_cover', 'piercing_pattern',
                         'hanging_man', 'shooting_star']:
                value = getattr(item, attr, 0)
                if value != 0:
                    patterns[attr] = value
            
            if patterns:  # 只返回有形态的股票
                result.append({
                    "code": item.code,
                    "date": str(item.date),
                    "patterns": patterns
                })
        
        return {"code": 0, "message": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/buy", summary="获取买入信号")
async def get_buy_signals(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取看涨形态（买入信号）"""
    try:
        service = PatternService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        signals = service.get_buy_signals(trade_date)
        
        return {"code": 0, "message": "success", "data": signals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/sell", summary="获取卖出信号")
async def get_sell_signals(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取看跌形态（卖出信号）"""
    try:
        service = PatternService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        signals = service.get_sell_signals(trade_date)
        
        return {"code": 0, "message": "success", "data": signals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate/{code}", summary="计算并保存形态")
async def calculate_and_save(
    code: str,
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """识别单只股票K线形态并保存"""
    try:
        service = PatternService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = service.recognize_and_save(code, trade_date)
        
        if data is None:
            return {"code": -1, "message": "未识别到形态", "data": None}
        
        return {
            "code": 0,
            "message": "success",
            "data": {"code": code}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-all", summary="批量计算并保存形态")
async def calculate_all(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """批量识别所有股票K线形态并保存"""
    try:
        service = PatternService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        count = service.recognize_and_save_all(trade_date)
        
        return {
            "code": 0,
            "message": "success",
            "data": {"count": count}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))