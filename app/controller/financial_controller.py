#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
财务数据API接口
"""

from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel

from app.service.financial_service import FinancialService
from app.database import get_db


router = APIRouter(prefix="/financial", tags=["财务数据"])


# 响应模型
class FinancialResponse(BaseModel):
    """财务数据响应"""
    code: str
    report_date: str
    eps: Optional[float] = None
    eps_deducted: Optional[float] = None
    bvps: Optional[float] = None
    cfps: Optional[float] = None
    roe: Optional[float] = None
    roe_weighted: Optional[float] = None
    net_profit_margin: Optional[float] = None
    gross_profit_margin: Optional[float] = None
    revenue_growth: Optional[float] = None
    net_profit_growth: Optional[float] = None
    debt_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    revenue: Optional[int] = None
    net_profit: Optional[int] = None
    net_profit_parent: Optional[int] = None
    net_profit_deducted: Optional[int] = None
    total_assets: Optional[int] = None
    net_assets: Optional[int] = None
    operating_cf: Optional[int] = None
    investing_cf: Optional[int] = None
    financing_cf: Optional[int] = None
    total_shares: Optional[int] = None
    float_shares_a: Optional[int] = None
    
    class Config:
        from_attributes = True


@router.get("/{code}", summary="获取股票财务数据")
async def get_financial(
    code: str,
    report_date: Optional[str] = Query(None, description="报告期(YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """获取单只股票财务数据（默认返回最新报告期）"""
    try:
        service = FinancialService(db)
        if report_date:
            report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        
        data = service.get_financial(code, report_date)
        
        if data is None:
            return {"code": -1, "message": "财务数据不存在", "data": None}
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "code": data.code,
                "report_date": str(data.report_date),
                "eps": data.eps,
                "eps_deducted": data.eps_deducted,
                "bvps": data.bvps,
                "cfps": data.cfps,
                "roe": data.roe,
                "roe_weighted": data.roe_weighted,
                "net_profit_margin": data.net_profit_margin,
                "gross_profit_margin": data.gross_profit_margin,
                "revenue_growth": data.revenue_growth,
                "net_profit_growth": data.net_profit_growth,
                "debt_ratio": data.debt_ratio,
                "current_ratio": data.current_ratio,
                "quick_ratio": data.quick_ratio,
                "revenue": data.revenue,
                "net_profit": data.net_profit,
                "net_profit_parent": data.net_profit_parent,
                "net_profit_deducted": data.net_profit_deducted,
                "total_assets": data.total_assets,
                "net_assets": data.net_assets,
                "operating_cf": data.operating_cf,
                "investing_cf": data.investing_cf,
                "financing_cf": data.financing_cf,
                "total_shares": data.total_shares,
                "float_shares_a": data.float_shares_a,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/history", summary="获取股票历史财务数据")
async def get_financial_history(
    code: str,
    limit: int = Query(8, description="返回数量，默认8个报告期"),
    db = Depends(get_db)
):
    """获取股票历史财务数据（最近N个报告期）"""
    try:
        service = FinancialService(db)
        data = service.get_financial_history(code, limit)
        
        if not data:
            return {"code": -1, "message": "财务数据不存在", "data": []}
        
        result = [
            {
                "code": item.code,
                "report_date": str(item.report_date),
                "eps": item.eps,
                "eps_deducted": item.eps_deducted,
                "bvps": item.bvps,
                "roe": item.roe,
                "roe_weighted": item.roe_weighted,
                "revenue_growth": item.revenue_growth,
                "net_profit_growth": item.net_profit_growth,
                "revenue": item.revenue,
                "net_profit": item.net_profit,
                "net_profit_parent": item.net_profit_parent,
            }
            for item in data
        ]
        
        return {"code": 0, "message": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest-report-date", summary="获取最新报告期")
async def get_latest_report_date(db = Depends(get_db)):
    """获取数据库中最新的财务报告期"""
    try:
        service = FinancialService(db)
        report_date = service.get_latest_report_date()
        
        if report_date is None:
            return {"code": -1, "message": "无财务数据", "data": None}
        
        return {
            "code": 0,
            "message": "success",
            "data": {"report_date": str(report_date)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse", summary="解析财务数据文件")
async def parse_financial_file(
    filepath: str = Query(..., description="财务数据文件路径(gpcw*.zip)"),
    db = Depends(get_db)
):
    """解析财务数据文件并保存到数据库
    
    需要先通过 mootdx 下载财务数据文件：
    ```
    python -c "from mootdx.affair import Affair; Affair.fetch(downdir='./data', filename='gpcw20231231.zip')"
    ```
    """
    try:
        service = FinancialService(db)
        count = await service.fetch_and_save_financial_data(filepath)
        
        return {
            "code": 0,
            "message": "success",
            "data": {"count": count}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))