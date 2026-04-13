#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据获取器 - 使用 akshare 数据源（异步版本）
"""

import asyncio
import time
import pandas as pd
from typing import Dict
from datetime import datetime, timedelta

import akshare as ak

from app.crawler.base_crawler import BaseCrawler
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EastMoneyFetcher(BaseCrawler):
    """股票数据获取器 - 基于 akshare（仅异步方法）"""
    
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
    
    # ==================== 异步方法 ====================
    
    async def get_stock_list(self) -> pd.DataFrame:
        """
        异步获取A股股票列表
        
        Returns:
            股票数据DataFrame
        """
        def _fetch():
            logger.info("开始获取A股股票列表(akshare)...")
            df = ak.stock_info_a_code_name()
            
            if df is None or df.empty:
                logger.warning("获取股票列表为空")
                return pd.DataFrame()
            
            # 重命名列
            df = df.rename(columns={'code': 'code', 'name': 'name'})
            
            # 添加默认值列
            default_cols = {
                'new_price': 0.0, 'change_rate': 0.0, 'ups_downs': 0.0,
                'volume': 0, 'deal_amount': 0.0, 'amplitude': 0.0,
                'turnoverrate': 0.0, 'volume_ratio': 0.0, 'high_price': 0.0,
                'low_price': 0.0, 'open_price': 0.0, 'pre_close_price': 0.0,
                'pe9': 0.0, 'pbnewmrq': 0.0, 'total_market_cap': 0.0,
                'free_cap': 0.0, 'industry': '',
            }
            
            for col, default_val in default_cols.items():
                if col not in df.columns:
                    df[col] = default_val
            
            # 只保留A股
            df = df[df['code'].str.match(r'^[0-9]{6}$')]
            df = df.reset_index(drop=True)
            
            logger.info(f"获取A股股票列表成功，共 {len(df)} 条数据")
            return df
        
        try:
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    async def get_stock_list_with_realtime(self, retry_count: int = 3) -> pd.DataFrame:
        """
        异步获取A股实时行情全量数据
        
        直接使用 stock_zh_a_spot_em() 获取全量数据
        失败时自动重试，间隔为 1分钟、3分钟、5分钟
        
        Args:
            retry_count: 重试次数，默认3次
            
        Returns:
            完整股票数据DataFrame
        """
        retry_intervals = [60, 180, 300]  # 1分钟、3分钟、5分钟
        
        def _fetch():
            return ak.stock_zh_a_spot_em()
        
        for attempt in range(retry_count + 1):
            try:
                if attempt == 0:
                    logger.info("开始获取A股实时行情全量数据...")
                else:
                    interval = retry_intervals[min(attempt - 1, len(retry_intervals) - 1)]
                    logger.info(f"第 {attempt} 次重试，等待 {interval // 60} 分钟后重试...")
                    await asyncio.sleep(interval)
                
                # 异步获取全量实时行情
                df = await asyncio.to_thread(_fetch)
                
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
    
    async def get_stock_realtime(self, symbol: str) -> Dict:
        """
        异步获取单只股票实时行情
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票行情字典
        """
        def _fetch():
            today = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            return ak.stock_zh_a_hist(
                symbol=symbol, period="daily",
                start_date=start, end_date=today, adjust=""
            )
        
        try:
            df = await asyncio.to_thread(_fetch)
            
            if df is None or df.empty:
                return {}
            
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
    
    async def get_stock_hist(self, symbol: str, start_date: str = "19700101", 
                             end_date: str = "20500101", adjust: str = "") -> pd.DataFrame:
        """
        异步获取股票历史数据
        
        Args:
            symbol: 股票代码（如 "000001"）
            start_date: 开始日期（格式 YYYYMMDD 或 YYYY-MM-DD）
            end_date: 结束日期（格式 YYYYMMDD 或 YYYY-MM-DD）
            adjust: 复权类型 "" / "qfq" / "hfq"
            
        Returns:
            历史数据DataFrame
        """
        def _fetch():
            # 格式化日期
            s = start_date if len(start_date) == 10 else f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            e = end_date if len(end_date) == 10 else f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
            return ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=s, end_date=e, adjust=adjust)
        
        try:
            logger.info(f"开始获取股票 {symbol} 历史数据(akshare)...")
            df = await asyncio.to_thread(_fetch)
            
            if df is None or df.empty:
                logger.warning(f"股票 {symbol} 历史数据为空")
                return pd.DataFrame()
            
            # 重命名列
            column_mapping = {
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume',
                '成交额': 'amount', '振幅': 'amplitude',
                '涨跌幅': 'change_rate', '涨跌额': 'ups_downs', '换手率': 'turnover',
            }
            df = df.rename(columns=column_mapping)
            
            keep_cols = ['date', 'open', 'close', 'high', 'low', 'volume', 
                         'amount', 'amplitude', 'change_rate', 'ups_downs', 'turnover']
            df = df[[col for col in keep_cols if col in df.columns]]
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.reset_index(drop=True, inplace=True)
            
            logger.info(f"获取股票 {symbol} 历史数据成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 历史数据失败: {e}")
            return pd.DataFrame()
    
    async def get_stock_hist_min(self, symbol: str, period: str = "5", 
                                  adjust: str = "") -> pd.DataFrame:
        """
        异步获取股票分时数据
        
        Args:
            symbol: 股票代码
            period: 周期 1/5/15/30/60 分钟
            adjust: 复权类型
            
        Returns:
            分时数据DataFrame
        """
        def _fetch():
            return ak.stock_zh_a_hist_min_em(symbol=symbol, period=period, adjust=adjust)
        
        try:
            logger.info(f"开始获取股票 {symbol} {period}分钟分时数据(akshare)...")
            df = await asyncio.to_thread(_fetch)
            
            if df is None or df.empty:
                logger.warning(f"股票 {symbol} 分时数据为空")
                return pd.DataFrame()
            
            column_mapping = {
                '时间': 'time', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume', '成交额': 'amount',
            }
            df = df.rename(columns=column_mapping)
            
            logger.info(f"获取股票 {symbol} 分时数据成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 分时数据失败: {e}")
            return pd.DataFrame()
    
    async def get_etf_list(self) -> pd.DataFrame:
        """异步获取ETF实时行情"""
        def _fetch():
            return ak.fund_etf_spot_em()
        
        try:
            logger.info("开始获取ETF实时行情(akshare)...")
            df = await asyncio.to_thread(_fetch)
            
            if df is None or df.empty:
                logger.warning("获取ETF行情数据为空")
                return pd.DataFrame()
            
            column_mapping = {
                '代码': 'code', '名称': 'name', '最新价': 'new_price',
                '涨跌幅': 'change_rate', '涨跌额': 'change_amount',
                '成交量': 'volume', '成交额': 'amount',
                '开盘价': 'open_price', '最高价': 'high_price',
                '最低价': 'low_price', '昨收价': 'pre_close_price',
            }
            df = df.rename(columns=column_mapping)
            
            keep_cols = ['code', 'name', 'new_price', 'change_rate', 'change_amount',
                         'volume', 'amount', 'open_price', 'high_price', 'low_price', 'pre_close_price']
            df = df[[col for col in keep_cols if col in df.columns]]
            
            logger.info(f"获取ETF行情成功，共 {len(df)} 条数据")
            return df
            
        except Exception as e:
            logger.error(f"获取ETF行情失败: {e}")
            return pd.DataFrame()
    
    async def get_fund_flow_individual(self, indicator: str = "今日") -> pd.DataFrame:
        """异步获取个股资金流向"""
        try:
            logger.info(f"开始获取个股资金流向({indicator})(akshare)...")
            df = await asyncio.to_thread(ak.stock_individual_fund_flow_rank, indicator=indicator)
            
            if df is None or df.empty:
                logger.warning("个股资金流向数据为空")
                return pd.DataFrame()
            
            logger.info(f"获取个股资金流向成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取个股资金流向失败: {e}")
            return pd.DataFrame()
    
    async def get_fund_flow_sector(self, indicator: str = "今日", sector_type: str = "行业") -> pd.DataFrame:
        """异步获取板块资金流向"""
        try:
            logger.info(f"开始获取板块资金流向({sector_type})(akshare)...")
            df = await asyncio.to_thread(ak.stock_sector_fund_flow_rank, indicator=indicator, sector_type=sector_type)
            
            if df is None or df.empty:
                logger.warning("板块资金流向数据为空")
                return pd.DataFrame()
            
            logger.info(f"获取板块资金流向成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取板块资金流向失败: {e}")
            return pd.DataFrame()
    
    async def get_trade_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """异步获取交易日历"""
        try:
            logger.info(f"获取交易日历 {start_date} - {end_date}(akshare)...")
            df = await asyncio.to_thread(ak.tool_trade_date_hist_sina)
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            df = df[(df['trade_date'] >= start_dt) & (df['trade_date'] <= end_dt)]
            return df
            
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return pd.DataFrame()
    
    async def get_code_id_map(self) -> Dict[str, int]:
        """异步获取股票代码与市场ID映射（上证=1，深证=0）"""
        if self._code_id_map:
            return self._code_id_map
        
        try:
            df = await self.get_stock_list()
            
            if df.empty:
                return {}
            
            code_id_dict = {}
            for code in df['code']:
                code = str(code).zfill(6)
                code_id_dict[code] = 1 if code.startswith('6') else 0
            
            self._code_id_map = code_id_dict
            return code_id_dict
            
        except Exception as e:
            logger.error(f"获取股票市场映射失败: {e}")
            return {}
    
    # ==================== 爬虫接口方法 ====================
    
    async def crawl(self, *args, **kwargs):
        """异步爬取方法"""
        return await self.get_stock_list()