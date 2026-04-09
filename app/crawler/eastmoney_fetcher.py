#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据获取器 - 使用 akshare 数据源
"""

import asyncio
import time
import random
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import akshare as ak

from app.crawler.base_crawler import BaseCrawler
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EastMoneyFetcher(BaseCrawler):
    """股票数据获取器 - 基于 akshare"""
    
    def __init__(self):
        super().__init__()
        self._code_id_map = None
    
    def _get_market_code(self, code: str) -> str:
        """根据股票代码获取市场代码"""
        code = str(code).zfill(6)
        if code.startswith('6'):
            return "sh"
        else:
            return "sz"
    
    # ==================== 同步方法 ====================
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取A股股票列表
        
        使用 akshare 获取股票基本信息列表，
        然后通过历史数据接口获取最新行情
        
        Returns:
            股票数据DataFrame
        """
        try:
            logger.info("开始获取A股股票列表(akshare)...")
            
            # 方案1: 获取股票代码名称列表（稳定接口）
            df = ak.stock_info_a_code_name()
            
            if df is None or df.empty:
                logger.warning("获取股票列表为空")
                return pd.DataFrame()
            
            # 重命名列
            df = df.rename(columns={
                'code': 'code',
                'name': 'name',
            })
            
            # 添加默认值列
            default_cols = {
                'new_price': 0.0,
                'change_rate': 0.0,
                'ups_downs': 0.0,
                'volume': 0,
                'deal_amount': 0.0,
                'amplitude': 0.0,
                'turnoverrate': 0.0,
                'volume_ratio': 0.0,
                'high_price': 0.0,
                'low_price': 0.0,
                'open_price': 0.0,
                'pre_close_price': 0.0,
                'pe9': 0.0,
                'pbnewmrq': 0.0,
                'total_market_cap': 0.0,
                'free_cap': 0.0,
                'industry': '',
            }
            
            for col, default_val in default_cols.items():
                if col not in df.columns:
                    df[col] = default_val
            
            # 只保留A股（过滤掉指数、基金等）
            df = df[df['code'].str.match(r'^[0-9]{6}$')]
            df = df.reset_index(drop=True)
            
            logger.info(f"获取A股股票列表成功，共 {len(df)} 条数据")
            return df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_stock_list_with_realtime(self, retry_count: int = 3) -> pd.DataFrame:
        """
        获取A股实时行情全量数据
        
        直接使用 stock_zh_a_spot_em() 获取全量数据
        失败时自动重试，间隔为 1分钟、3分钟、5分钟
        
        Args:
            retry_count: 重试次数，默认3次
            
        Returns:
            完整股票数据DataFrame
        """
        # 重试间隔（秒）：1分钟、3分钟、5分钟
        retry_intervals = [60, 180, 300]
        
        for attempt in range(retry_count + 1):
            try:
                if attempt == 0:
                    logger.info("开始获取A股实时行情全量数据...")
                else:
                    interval = retry_intervals[min(attempt - 1, len(retry_intervals) - 1)]
                    logger.info(f"第 {attempt} 次重试，等待 {interval // 60} 分钟后重试...")
                    time.sleep(interval)
                
                # 直接获取全量实时行情
                df = ak.stock_zh_a_spot_em()
                
                if df is None or df.empty:
                    logger.warning(f"获取数据为空，尝试: {attempt + 1}/{retry_count + 1}")
                    continue
                
                # 重命名列
                df = self._rename_realtime_columns(df)
                
                logger.info(f"获取A股实时行情成功，共 {len(df)} 条数据")
                return df
                
            except Exception as e:
                logger.warning(f"获取A股实时行情失败(尝试 {attempt + 1}/{retry_count + 1}): {e}")
                
                if attempt == retry_count:
                    logger.error(f"获取A股实时行情失败，已重试 {retry_count} 次，全部失败")
                    return pd.DataFrame()
        
        return pd.DataFrame()
    
    def _rename_realtime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """重命名实时行情数据列名"""
        column_mapping = {
            '代码': 'code',
            '名称': 'name',
            '最新价': 'new_price',
            '涨跌幅': 'change_rate',
            '涨跌额': 'ups_downs',
            '成交量': 'volume',
            '成交额': 'deal_amount',
            '振幅': 'amplitude',
            '最高': 'high_price',
            '最低': 'low_price',
            '今开': 'open_price',
            '昨收': 'pre_close_price',
            '换手率': 'turnoverrate',
            '量比': 'volume_ratio',
            '市盈率-动态': 'pe9',
            '市净率': 'pbnewmrq',
            '总市值': 'total_market_cap',
            '流通市值': 'free_cap',
        }
        
        df = df.rename(columns=column_mapping)
        
        # 添加行业字段（如果不存在）
        if 'industry' not in df.columns:
            df['industry'] = ''
        
        # 只保留需要的列
        keep_cols = ['code', 'name', 'new_price', 'change_rate', 'ups_downs', 
                     'volume', 'deal_amount', 'amplitude', 'high_price', 'low_price',
                     'open_price', 'pre_close_price', 'turnoverrate', 'volume_ratio',
                     'pe9', 'pbnewmrq', 'total_market_cap', 'free_cap', 'industry']
        
        df = df[[col for col in keep_cols if col in df.columns]]
        
        return df
    
    def get_stock_realtime(self, symbol: str) -> Dict:
        """
        获取单只股票实时行情
        
        通过获取最新历史数据模拟实时行情
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票行情字典
        """
        try:
            # 添加随机延迟避免被封IP（1-3秒）
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            # 获取最近几天的历史数据
            today = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start,
                end_date=today,
                adjust=""
            )
            
            if df is None or df.empty:
                return {}
            
            # 取最后一条数据作为"实时"数据
            latest = df.iloc[-1]
            
            return {
                'code': symbol,
                'date': latest['日期'],
                'open': float(latest.get('开盘', 0) or 0),
                'close': float(latest.get('收盘', 0) or 0),
                'high': float(latest.get('最高', 0) or 0),
                'low': float(latest.get('最低', 0) or 0),
                'volume': float(latest.get('成交量', 0) or 0),
                'amount': float(latest.get('成交额', 0) or 0),
                'change_rate': float(latest.get('涨跌幅', 0) or 0),
                'ups_downs': float(latest.get('涨跌额', 0) or 0),
                'amplitude': float(latest.get('振幅', 0) or 0),
                'turnover': float(latest.get('换手率', 0) or 0),
            }
            
        except Exception as e:
            logger.warning(f"获取股票 {symbol} 实时数据失败: {e}")
            return {}
    
    def get_stock_hist(self, symbol: str, start_date: str = "19700101", 
                       end_date: str = "20500101", adjust: str = "") -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码（如 "000001"）
            start_date: 开始日期（格式 YYYYMMDD 或 YYYY-MM-DD）
            end_date: 结束日期（格式 YYYYMMDD 或 YYYY-MM-DD）
            adjust: 复权类型 "" (不复权) / "qfq" (前复权) / "hfq" (后复权)
            
        Returns:
            历史数据DataFrame
        """
        try:
            logger.info(f"开始获取股票 {symbol} 历史数据(akshare)...")
            
            # 格式化日期 YYYYMMDD -> YYYY-MM-DD
            if len(start_date) == 8:
                start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            if len(end_date) == 8:
                end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
            
            # akshare 东方财富历史K线接口
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df is None or df.empty:
                logger.warning(f"股票 {symbol} 历史数据为空")
                return pd.DataFrame()
            
            # 重命名列
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_rate',
                '涨跌额': 'ups_downs',
                '换手率': 'turnover',
            }
            
            df = df.rename(columns=column_mapping)
            
            # 只保留需要的列
            keep_cols = ['date', 'open', 'close', 'high', 'low', 'volume', 
                         'amount', 'amplitude', 'change_rate', 'ups_downs', 'turnover']
            df = df[[col for col in keep_cols if col in df.columns]]
            
            # 设置日期索引
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.reset_index(drop=True, inplace=True)
            
            logger.info(f"获取股票 {symbol} 历史数据成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_hist_min(self, symbol: str, period: str = "5", 
                           start_date: str = None, end_date: str = None, 
                           adjust: str = "") -> pd.DataFrame:
        """
        获取股票分时数据
        
        Args:
            symbol: 股票代码
            period: 周期 1/5/15/30/60 分钟
            start_date: 开始日期时间
            end_date: 结束日期时间
            adjust: 复权类型
            
        Returns:
            分时数据DataFrame
        """
        try:
            logger.info(f"开始获取股票 {symbol} {period}分钟分时数据(akshare)...")
            
            # akshare 东方财富分时数据接口
            df = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period=period,
                adjust=adjust
            )
            
            if df is None or df.empty:
                logger.warning(f"股票 {symbol} 分时数据为空")
                return pd.DataFrame()
            
            # 重命名列
            column_mapping = {
                '时间': 'time',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
            }
            
            df = df.rename(columns=column_mapping)
            
            logger.info(f"获取股票 {symbol} 分时数据成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 分时数据失败: {e}")
            return pd.DataFrame()
    
    def get_etf_list(self) -> pd.DataFrame:
        """获取ETF实时行情"""
        try:
            logger.info("开始获取ETF实时行情(akshare)...")
            
            df = ak.fund_etf_spot_em()
            
            if df is None or df.empty:
                logger.warning("获取ETF行情数据为空")
                return pd.DataFrame()
            
            # 重命名列
            column_mapping = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'new_price',
                '涨跌幅': 'change_rate',
                '涨跌额': 'change_amount',
                '成交量': 'volume',
                '成交额': 'amount',
                '开盘价': 'open_price',
                '最高价': 'high_price',
                '最低价': 'low_price',
                '昨收价': 'pre_close_price',
            }
            
            df = df.rename(columns=column_mapping)
            
            # 只保留需要的列
            keep_cols = ['code', 'name', 'new_price', 'change_rate', 'change_amount',
                         'volume', 'amount', 'open_price', 'high_price', 'low_price', 'pre_close_price']
            df = df[[col for col in keep_cols if col in df.columns]]
            
            logger.info(f"获取ETF行情成功，共 {len(df)} 条数据")
            return df
            
        except Exception as e:
            logger.error(f"获取ETF行情失败: {e}")
            return pd.DataFrame()
    
    def get_fund_flow_individual(self, indicator: str = "今日") -> pd.DataFrame:
        """
        获取个股资金流向
        
        Args:
            indicator: 时间周期 今日/3日/5日/10日
            
        Returns:
            资金流向DataFrame
        """
        try:
            logger.info(f"开始获取个股资金流向({indicator})(akshare)...")
            
            df = ak.stock_individual_fund_flow_rank(indicator=indicator)
            
            if df is None or df.empty:
                logger.warning("个股资金流向数据为空")
                return pd.DataFrame()
            
            logger.info(f"获取个股资金流向成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取个股资金流向失败: {e}")
            return pd.DataFrame()
    
    def get_fund_flow_sector(self, indicator: str = "今日", sector_type: str = "行业") -> pd.DataFrame:
        """
        获取板块资金流向
        
        Args:
            indicator: 时间周期 今日/3日/5日/10日
            sector_type: 板块类型 行业/概念/地域
            
        Returns:
            板块资金流向DataFrame
        """
        try:
            logger.info(f"开始获取板块资金流向({sector_type})(akshare)...")
            
            df = ak.stock_sector_fund_flow_rank(indicator=indicator, sector_type=sector_type)
            
            if df is None or df.empty:
                logger.warning("板块资金流向数据为空")
                return pd.DataFrame()
            
            logger.info(f"获取板块资金流向成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取板块资金流向失败: {e}")
            return pd.DataFrame()
    
    def get_trade_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            交易日历DataFrame
        """
        try:
            logger.info(f"获取交易日历 {start_date} - {end_date}(akshare)...")
            
            df = ak.tool_trade_date_hist_sina()
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            # 筛选日期范围
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            df = df[(df['trade_date'] >= start_dt) & (df['trade_date'] <= end_dt)]
            
            return df
            
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return pd.DataFrame()
    
    def get_code_id_map(self) -> Dict[str, int]:
        """获取股票代码与市场ID映射（上证=1，深证=0）"""
        if self._code_id_map:
            return self._code_id_map
        
        try:
            df = self.get_stock_list()
            
            if df.empty:
                return {}
            
            code_id_dict = {}
            for code in df['code']:
                code = str(code).zfill(6)
                if code.startswith('6'):
                    code_id_dict[code] = 1  # 上证
                else:
                    code_id_dict[code] = 0  # 深证
            
            self._code_id_map = code_id_dict
            return code_id_dict
            
        except Exception as e:
            logger.error(f"获取股票市场映射失败: {e}")
            return {}
    
    # ==================== 异步方法 ====================
    
    async def async_get_stock_list(self) -> pd.DataFrame:
        """异步获取A股股票列表"""
        return await asyncio.to_thread(self.get_stock_list)
    
    async def async_get_stock_list_with_realtime(self, retry_count: int = 3) -> pd.DataFrame:
        """异步获取A股实时行情全量数据"""
        return await asyncio.to_thread(self.get_stock_list_with_realtime, retry_count)
    
    async def async_get_stock_realtime(self, symbol: str) -> Dict:
        """异步获取单只股票实时行情"""
        return await asyncio.to_thread(self.get_stock_realtime, symbol)
    
    async def async_get_stock_hist(self, symbol: str, start_date: str = "19700101", 
                                    end_date: str = "20500101", adjust: str = "") -> pd.DataFrame:
        """异步获取股票历史数据"""
        return await asyncio.to_thread(
            self.get_stock_hist, symbol, start_date, end_date, adjust
        )
    
    async def async_get_stock_hist_min(self, symbol: str, period: str = "5", 
                                        start_date: str = None, end_date: str = None, 
                                        adjust: str = "") -> pd.DataFrame:
        """异步获取股票分时数据"""
        return await asyncio.to_thread(
            self.get_stock_hist_min, symbol, period, start_date, end_date, adjust
        )
    
    async def async_get_etf_list(self) -> pd.DataFrame:
        """异步获取ETF实时行情"""
        return await asyncio.to_thread(self.get_etf_list)
    
    async def async_get_fund_flow_individual(self, indicator: str = "今日") -> pd.DataFrame:
        """异步获取个股资金流向"""
        return await asyncio.to_thread(self.get_fund_flow_individual, indicator)
    
    async def async_get_fund_flow_sector(self, indicator: str = "今日", 
                                          sector_type: str = "行业") -> pd.DataFrame:
        """异步获取板块资金流向"""
        return await asyncio.to_thread(self.get_fund_flow_sector, indicator, sector_type)
    
    async def async_get_trade_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """异步获取交易日历"""
        return await asyncio.to_thread(self.get_trade_calendar, start_date, end_date)
    
    # ==================== 爬虫接口方法 ====================
    
    def crawl(self, *args, **kwargs):
        """实现爬取方法"""
        return self.get_stock_list()
    
    async def async_crawl(self, *args, **kwargs):
        """异步爬取方法"""
        return await self.async_get_stock_list()