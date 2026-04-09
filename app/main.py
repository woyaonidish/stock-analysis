#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
InStock FastAPI 应用入口
"""

import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import date

from app.config.config import settings
from app.database import init_db
from app.controller import stock_controller, etf_controller, fund_flow_controller
from app.controller import indicator_controller, strategy_controller, backtest_controller
from app.utils.trade_time import is_trade_date
from app.utils.logger import get_logger, info, warning, error

logger = get_logger(__name__)


async def async_fetch_daily_data_task():
    """
    异步获取当日股票数据的任务
    
    使用异步方式执行，不阻塞主服务启动
    """
    from app.database import SessionLocal
    from app.service.stock_service import StockService
    from app.dao.stock_dao import StockDAO
    
    today = date.today()
    
    # 检查是否为交易日
    if not is_trade_date(today):
        info(f"[后台任务] 今天 {today} 不是交易日，跳过数据获取")
        return
    
    try:
        session = SessionLocal()
        stock_dao = StockDAO(session)
        
        # 检查数据库中是否已有当日数据
        existing_stocks = stock_dao.find_by_date(today)
        
        if existing_stocks and len(existing_stocks) > 0:
            info(f"[后台任务] 数据库已有 {today} 的股票数据，共 {len(existing_stocks)} 条记录")
            session.close()
            return
        
        # 没有当日数据，开始异步获取
        info(f"[后台任务] 开始异步获取 {today} 的股票数据...")
        stock_service = StockService(session)
        count = await stock_service.async_fetch_and_save_daily_data(today)
        
        if count > 0:
            info(f"[后台任务] 成功获取并保存 {count} 条股票数据")
        else:
            warning(f"[后台任务] 获取股票数据失败或数据为空")
        
        session.close()
        
    except Exception as e:
        error(f"[后台任务] 自动获取股票数据异常: {e}")


def start_background_fetch():
    """启动后台异步数据获取任务"""
    import threading
    
    def run_async_task():
        """在新线程中运行异步任务"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_fetch_daily_data_task())
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_async_task, daemon=True)
    thread.start()
    info("已启动后台异步数据获取任务")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    
    # 启动后台异步数据获取（不阻塞主服务）
    start_background_fetch()
    
    # 启动定时任务
    if settings.SCHEDULER_ENABLED:
        from app.scheduler.job_scheduler import start_scheduler
        start_scheduler()
    
    yield
    
    # 关闭时清理
    info("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="InStock股票分析系统 - 三层架构实现",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stock_controller.router, prefix="/api")
app.include_router(etf_controller.router, prefix="/api")
app.include_router(fund_flow_controller.router, prefix="/api")
app.include_router(indicator_controller.router, prefix="/api")
app.include_router(strategy_controller.router, prefix="/api")
app.include_router(backtest_controller.router, prefix="/api")


@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )