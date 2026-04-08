#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
回测服务
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.dao.stock_dao import StockDAO
from app.dao.strategy_dao import StrategyDAO
from app.service.stock_service import StockService
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BacktestService:
    """回测服务"""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.stock_dao = StockDAO(self.session)
        self.strategy_dao = StrategyDAO(self.session)
        self.stock_service = StockService(self.session)
    
    def backtest_strategy(
        self,
        strategy_type: str,
        start_date: date,
        end_date: date,
        initial_capital: float = 100000.0
    ) -> Dict:
        """
        回测策略
        
        Args:
            strategy_type: 策略类型
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            
        Returns:
            回测结果字典
        """
        result = {
            "strategy_type": strategy_type,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "final_capital": initial_capital,
            "total_return": 0.0,
            "annualized_return": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "trade_count": 0,
            "trades": []
        }
        
        try:
            # 获取策略信号日期列表
            signal_dates = self._get_trade_dates(start_date, end_date)
            
            capital = initial_capital
            position = 0  # 持仓数量
            trades = []
            max_capital = capital
            
            for signal_date in signal_dates:
                # 获取当日策略信号
                signals = self.strategy_dao.find_by_type_and_date(strategy_type, signal_date)
                
                if not signals:
                    continue
                
                for signal in signals:
                    # 获取股票历史数据
                    hist_data = self.stock_service.get_stock_hist(
                        signal.code,
                        start_date=start_date.strftime("%Y%m%d"),
                        end_date=signal_date.strftime("%Y%m%d")
                    )
                    
                    if hist_data is None or hist_data.empty:
                        continue
                    
                    latest_price = hist_data.iloc[-1]['close']
                    
                    # 买入逻辑
                    if position == 0:
                        shares = int(capital * 0.1 / latest_price)  # 每次10%仓位
                        if shares > 0:
                            position = shares
                            capital -= shares * latest_price
                            trades.append({
                                "date": signal_date,
                                "code": signal.code,
                                "type": "buy",
                                "price": latest_price,
                                "shares": shares
                            })
                    
                    # 卖出逻辑 (持有5天后卖出)
                    elif len(trades) > 0:
                        last_buy = trades[-1]
                        if (signal_date - last_buy["date"]).days >= 5:
                            capital += position * latest_price
                            trades.append({
                                "date": signal_date,
                                "code": signal.code,
                                "type": "sell",
                                "price": latest_price,
                                "shares": position
                            })
                            position = 0
                    
                    max_capital = max(max_capital, capital + position * latest_price)
            
            # 计算最终资金
            if position > 0:
                # 以最后一天价格清仓
                capital += position * latest_price
            
            result["final_capital"] = capital
            result["total_return"] = (capital - initial_capital) / initial_capital * 100
            result["trade_count"] = len(trades)
            result["trades"] = trades
            
            # 计算年化收益
            days = (end_date - start_date).days
            if days > 0:
                result["annualized_return"] = (capital / initial_capital) ** (365 / days) - 1
                result["annualized_return"] *= 100
            
            # 计算最大回撤
            result["max_drawdown"] = (max_capital - capital) / max_capital * 100
            
            # 计算胜率
            if trades:
                wins = sum(1 for t in trades[::2] if len(trades) > trades.index(t) + 1 and 
                          trades[trades.index(t) + 1]["price"] > t["price"])
                result["win_rate"] = wins / (len(trades) // 2) * 100 if len(trades) > 1 else 0
            
        except Exception as e:
            logger.error(f"回测策略{strategy_type}失败: {e}")
        
        return result
    
    def _get_trade_dates(self, start_date: date, end_date: date) -> List[date]:
        """
        获取交易日列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            交易日列表
        """
        dates = []
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # 周一到周五
                dates.append(current)
            current += timedelta(days=1)
        return dates
    
    def backtest_all_strategies(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Dict]:
        """
        回测所有策略
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            各策略回测结果
        """
        from app.service.strategy_service import StrategyService
        
        strategies = [
            StrategyService.STRATEGY_VOLUME_UP,
            StrategyService.STRATEGY_BREAKTHROUGH,
            StrategyService.STRATEGY_LOW_ATR,
            StrategyService.STRATEGY_TURTLE
        ]
        
        results = {}
        for strategy_type in strategies:
            try:
                result = self.backtest_strategy(strategy_type, start_date, end_date)
                results[strategy_type] = result
            except Exception as e:
                logger.error(f"回测策略{strategy_type}失败: {e}")
                results[strategy_type] = {"error": str(e)}
        
        return results
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
