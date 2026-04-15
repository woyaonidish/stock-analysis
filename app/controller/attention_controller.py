#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关注股票API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.service.attention_service import AttentionService
from app.database import get_db


router = APIRouter(prefix="/attention", tags=["关注股票"])


@router.get("/list", summary="获取关注股票列表")
async def get_attention_list(
    trade_date: Optional[str] = Query(None, description="交易日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取关注股票列表（含行情信息）"""
    try:
        service = AttentionService(db)
        if trade_date:
            trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
        else:
            trade_date = date.today()
        
        data = service.get_attention_stocks(trade_date)
        
        return {"code": 0, "message": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/codes", summary="获取关注股票代码")
async def get_attention_codes(db = Depends(get_db)):
    """获取关注股票代码列表"""
    try:
        service = AttentionService(db)
        codes = service.get_attention_list()
        
        return {"code": 0, "message": "success", "data": codes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{code}", summary="检查是否关注")
async def check_attention(
    code: str,
    db = Depends(get_db)
):
    """检查股票是否被关注"""
    try:
        service = AttentionService(db)
        is_att = service.is_attention(code)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "code": code,
                "is_attention": is_att
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add/{code}", summary="添加关注")
async def add_attention(
    code: str,
    db = Depends(get_db)
):
    """添加股票到关注列表"""
    try:
        service = AttentionService(db)
        result = service.add_attention(code)
        
        if result:
            return {"code": 0, "message": "success", "data": {"code": code}}
        else:
            return {"code": -1, "message": "股票已被关注或添加失败", "data": {"code": code}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remove/{code}", summary="取消关注")
async def remove_attention(
    code: str,
    db = Depends(get_db)
):
    """从关注列表移除股票"""
    try:
        service = AttentionService(db)
        result = service.remove_attention(code)
        
        if result:
            return {"code": 0, "message": "success", "data": {"code": code}}
        else:
            return {"code": -1, "message": "股票未被关注", "data": {"code": code}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear", summary="清空关注列表")
async def clear_attention(db = Depends(get_db)):
    """清空所有关注股票"""
    try:
        service = AttentionService(db)
        count = service.clear_all_attentions()
        
        return {"code": 0, "message": "success", "data": {"count": count}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))