#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
历史数据缓存API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.service.hist_service import HistService
from app.database import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/hist", tags=["历史数据缓存"])


@router.get("/cache/{code}", summary="获取缓存历史数据")
async def get_cached_hist(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """从缓存获取历史数据"""
    try:
        service = HistService(db)
        
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = date.today() - __import__('datetime').timedelta(days=365)
        
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = date.today()
        
        data = service.get_cached_hist(code, start_date, end_date)
        
        if data.empty:
            return {"code": -1, "message": "缓存中无数据", "data": []}
        
        result = data.to_dict(orient="records")
        return {"code": 0, "message": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{code}", summary="获取缓存状态")
async def get_cache_status(
    code: str,
    db = Depends(get_db)
):
    """获取指定股票的缓存状态"""
    try:
        service = HistService(db)
        status = service.get_cache_status(code)
        
        return {"code": 0, "message": "success", "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch/{code}", summary="获取并缓存历史数据")
async def fetch_and_cache(
    code: str,
    days: int = Query(365, description="获取天数"),
    db = Depends(get_db)
):
    """从数据源获取历史数据并保存到缓存"""
    try:
        service = HistService(db)
        count = await service.fetch_and_cache(code, days)
        
        return {
            "code": 0,
            "message": "success",
            "data": {"code": code, "count": count}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-batch", summary="批量获取并缓存历史数据")
async def fetch_batch_cache(
    days: int = Query(365, description="获取天数"),
    codes: Optional[str] = Query(None, description="股票代码列表(逗号分隔)"),
    db = Depends(get_db)
):
    """批量获取并缓存历史数据"""
    try:
        from app.service.stock_service import StockService
        from app.crawler.tdx_fetcher import TdxFetcher
        
        hist_service = HistService(db)
        
        # 获取股票代码列表
        if codes:
            code_list = codes.split(',')
        else:
            fetcher = TdxFetcher()
            stock_list = await fetcher.get_stock_list()
            if stock_list.empty:
                return {"code": -1, "message": "获取股票列表失败", "data": None}
            code_list = stock_list['code'].tolist()
        
        total_count = 0
        success_count = 0
        
        for code in code_list[:50]:  # 限制批量数量，避免请求过多
            try:
                count = await hist_service.fetch_and_cache(code, days)
                if count > 0:
                    success_count += 1
                total_count += count
            except Exception as e:
                logger.warning(f"获取 {code} 历史数据失败: {e}")
                continue
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total_count": total_count,
                "success_count": success_count,
                "processed": len(code_list[:50])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/{code}", summary="清除缓存")
async def clear_cache(
    code: str,
    db = Depends(get_db)
):
    """清除指定股票的历史数据缓存"""
    try:
        service = HistService(db)
        count = service.clear_cache(code)
        
        return {"code": 0, "message": "success", "data": {"code": code, "count": count}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))