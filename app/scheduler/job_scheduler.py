#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定时任务调度器
"""

from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.utils.logger import get_logger, info, warning, error

logger = get_logger(__name__)

scheduler = None


def start_scheduler():
    """启动定时任务调度器"""
    global scheduler
    
    if scheduler is not None:
        return
    
    scheduler = BackgroundScheduler()
    
    # 添加每日数据抓取任务 (每个交易日 15:30)
    scheduler.add_job(
        daily_data_job,
        CronTrigger(hour=15, minute=30, day_of_week='mon-fri'),
        id='daily_data_job',
        name='每日数据抓取',
        replace_existing=True
    )
    
    # 添加指标计算任务 (每个交易日 16:00)
    scheduler.add_job(
        indicator_calc_job,
        CronTrigger(hour=16, minute=0, day_of_week='mon-fri'),
        id='indicator_calc_job',
        name='指标计算',
        replace_existing=True
    )
    
    # 添加策略选股任务 (每个交易日 16:30)
    scheduler.add_job(
        strategy_job,
        CronTrigger(hour=16, minute=30, day_of_week='mon-fri'),
        id='strategy_job',
        name='策略选股',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("定时任务调度器已停止")


def daily_data_job():
    """每日数据抓取任务"""
    import asyncio
    
    try:
        logger.info("开始执行每日数据抓取任务")
        
        from app.service.stock_service import StockService
        from app.service.etf_service import ETFService
        
        trade_date = date.today()
        
        # 创建新的事件循环来运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 抓取股票数据
            stock_service = StockService()
            stock_count = loop.run_until_complete(stock_service.fetch_and_save_daily_data(trade_date))
            stock_service.close()
            
            # 抓取ETF数据
            etf_service = ETFService()
            etf_count = loop.run_until_complete(etf_service.fetch_and_save_daily_data(trade_date))
            etf_service.close()
        finally:
            loop.close()
        
        logger.info(f"每日数据抓取完成: 股票{stock_count}条, ETF{etf_count}条")
        
    except Exception as e:
        logger.error(f"每日数据抓取任务执行失败: {e}")


def indicator_calc_job():
    """指标计算任务"""
    try:
        logger.info("开始执行指标计算任务")
        
        from app.service.indicator_service import IndicatorService
        from app.service.stock_service import StockService
        
        trade_date = date.today()
        
        # 获取股票代码列表
        stock_service = StockService()
        codes = stock_service.get_stock_codes(trade_date)
        stock_service.close()
        
        # 批量计算指标
        indicator_service = IndicatorService()
        count = indicator_service.batch_calculate_and_save(codes, trade_date)
        indicator_service.close()
        
        logger.info(f"指标计算完成: {count}/{len(codes)}只股票")
        
    except Exception as e:
        logger.error(f"指标计算任务执行失败: {e}")


def strategy_job():
    """策略选股任务"""
    try:
        logger.info("开始执行策略选股任务")
        
        from app.service.strategy_service import StrategyService
        
        trade_date = date.today()
        
        # 运行所有策略
        strategy_service = StrategyService()
        results = strategy_service.run_all_strategies(trade_date)
        strategy_service.close()
        
        logger.info(f"策略选股完成: {results}")
        
    except Exception as e:
        logger.error(f"策略选股任务执行失败: {e}")


if __name__ == "__main__":
    # 手动测试
    start_scheduler()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        stop_scheduler()
