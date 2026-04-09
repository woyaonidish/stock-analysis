#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据获取器 - 使用 akshare 替代东方财富接口
"""

import asyncio
import pandas as pd
from typing import Optional, Dict
import akshare

from app.crawler.base_crawler import BaseCrawler
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EastMoneyFetcher(BaseCrawler):
    """股票数据获取器 - 基于 akshare"""
    
    def __init__(self):
        super().__init__()
        self._code_id_map = None
    
    # ==================== 同步方法 ====================
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取A股实时行情列表
        
        Returns:
            股票数据DataFrame，列: code, name, new_price, change_rate, ups_downs, volume, deal_amount...
        """
        
        try:
            logger.info("开始获取A股实时行情...")
            df = akshare.stock_zh_a_spot_em()
            
            if df.empty:
                logger.warning("获取A股行情数据为空")
                return pd.DataFrame()
            
            # 重命名列，保持与原接口兼容
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
            
            # 只保留需要的列
            keep_cols = ['code', 'name', 'new_price', 'change_rate', 'ups_downs', 
                         'volume', 'deal_amount', 'amplitude', 'high_price', 'low_price',
                         'open_price', 'pre_close_price', 'turnoverrate', 'volume_ratio',
                         'pe9', 'pbnewmrq', 'total_market_cap', 'free_cap']
            
            df = df[[col for col in keep_cols if col in df.columns]]
            
            logger.info(f"获取A股行情成功，共 {len(df)} 条数据")
            return df
            
        except Exception as e:
            logger.error(f"获取A股行情失败: {e}")
            return pd.DataFrame()
    
    def get_code_id_map(self) -> Dict[str, int]:
        """获取股票代码与市场ID映射（上证=1，深证=0）"""
        if self._code_id_map:
            return self._code_id_map
        
        try:
            # 获取所有股票列表
            df = akshare.stock_zh_a_spot_em()
            
            code_id_dict = {}
            for code in df['代码']:
                # 上证股票代码以 6 开头
                if str(code).startswith('6'):
                    code_id_dict[str(code)] = 1  # 上证
                else:
                    code_id_dict[str(code)] = 0  # 深证
            
            self._code_id_map = code_id_dict
            return code_id_dict
            
        except Exception as e:
            logger.error(f"获取股票市场映射失败: {e}")
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
            历史数据DataFrame，列: date, open, close, high, low, volume, amount...
        """
        
        try:
            logger.info(f"开始获取股票 {symbol} 历史数据...")
            
            # 转换日期格式 YYYYMMDD -> YYYY-MM-DD
            if len(start_date) == 8:
                start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            if len(end_date) == 8:
                end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
            
            # akshare 的 adjust 参数: "" -> 不复权, "qfq" -> 前复权, "hfq" -> 后复权
            df = akshare.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df.empty:
                logger.warning(f"股票 {symbol} 历史数据为空")
                return pd.DataFrame()
            
            # 重命名列，保持与原接口兼容
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'quote_change',
                '涨跌额': 'ups_downs',
                '换手率': 'turnover',
            }
            
            df = df.rename(columns=column_mapping)
            
            # 只保留需要的列
            keep_cols = ['date', 'open', 'close', 'high', 'low', 'volume', 
                         'amount', 'amplitude', 'quote_change', 'ups_downs', 'turnover']
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
            logger.info(f"开始获取股票 {symbol} {period}分钟分时数据...")
            
            # akshare 分时数据接口
            df = akshare.stock_zh_a_hist_min_em(
                symbol=symbol,
                period=period,
                adjust=adjust
            )
            
            if df.empty:
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
            logger.info("开始获取ETF实时行情...")
            df = akshare.fund_etf_spot_em()
            
            if df.empty:
                logger.warning("获取ETF行情数据为空")
                return pd.DataFrame()
            
            # 重命名列，保持与原接口兼容
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
            logger.info(f"开始获取个股资金流向({indicator})...")
            
            # akshare 个股资金流接口
            df = akshare.stock_individual_fund_flow_rank(indicator=indicator)
            
            if df.empty:
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
            logger.info(f"开始获取板块资金流向({sector_type})...")
            
            # akshare 板块资金流接口
            df = akshare.stock_sector_fund_flow_rank(indicator=indicator, sector_type=sector_type)
            
            if df.empty:
                logger.warning("板块资金流向数据为空")
                return pd.DataFrame()
            
            logger.info(f"获取板块资金流向成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取板块资金流向失败: {e}")
            return pd.DataFrame()
    
    # ==================== 异步方法 ====================
    
    async def async_get_stock_list(self) -> pd.DataFrame:
        """异步获取A股实时行情列表"""
        # akshare 是同步库，使用 asyncio 包装
        return await asyncio.to_thread(self.get_stock_list)
    
    async def async_get_code_id_map(self) -> Dict[str, int]:
        """异步获取股票代码与市场ID映射"""
        return await asyncio.to_thread(self.get_code_id_map)
    
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
    
    # ==================== 爬虫接口方法 ====================
    
    def crawl(self, *args, **kwargs):
        """实现爬取方法"""
        return self.get_stock_list()
    
    async def async_crawl(self, *args, **kwargs):
        """异步爬取方法"""
        return await self.async_get_stock_list()