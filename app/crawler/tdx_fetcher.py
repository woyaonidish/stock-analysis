#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票数据获取器 - 使用 MOOTDX（通达信数据接口）
"""

import asyncio
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, date
from mootdx.quotes import Quotes
from mootdx.consts import KLINE_TYPE

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TdxFetcher:
    """股票数据获取器 - 基于 MOOTDX"""
    
    def __init__(self):
        self._client = None
        self._stock_list = None
    
    def _get_client(self):
        """获取 MOOTDX 客户端（延迟初始化）"""
        if self._client is None:
            self._client = Quotes.factory(
                market='std',
                bestip=True,  # 自动选择最快服务器
                timeout=15
            )
            logger.info("MOOTDX 客户端初始化成功")
        return self._client
    
    def _get_market(self, code: str) -> int:
        """根据股票代码获取市场代码
        
        Args:
            code: 股票代码
            
        Returns:
            市场代码 (0=深市, 1=沪市)
        """
        code = str(code).zfill(6)
        if code.startswith('6'):
            return 1  # 沪市
        else:
            return 0  # 深市
    
    async def get_stock_list(self) -> pd.DataFrame:
        """
        异步获取A股股票列表
        
        Returns:
            股票列表 DataFrame (code, name)
        """
        def _fetch():
            client = self._get_client()
            logger.info("开始获取A股股票列表(MOOTDX)...")
            
            # 获取沪市股票
            sh_df = client.stocks(market=1)
            # 获取深市股票
            sz_df = client.stocks(market=0)
            
            # 合并
            df = pd.concat([sh_df, sz_df], ignore_index=True)
            
            if df is None or df.empty:
                logger.warning("获取股票列表为空")
                return pd.DataFrame()
            
            # 重命名列
            df = df.rename(columns={'code': 'code', 'name': 'name'})
            
            # 过滤只保留A股（6位数字代码）
            df = df[df['code'].str.match(r'^[0-9]{6}$')]
            df = df.reset_index(drop=True)
            
            logger.info(f"获取A股股票列表成功，共 {len(df)} 条数据")
            return df
        
        try:
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
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
            client = self._get_client()
            market = self._get_market(symbol)
            return client.quotes(symbol=symbol, market=market)
        
        try:
            df = await asyncio.to_thread(_fetch)
            
            if df is None or df.empty:
                return {}
            
            # MOOTDX quotes 返回 DataFrame
            row = df.iloc[0] if len(df) > 0 else None
            if row is None:
                return {}
            
            return {
                'code': symbol,
                'name': str(row.get('name', '')),
                'open_price': float(row.get('open', 0) or 0),
                'close_price': float(row.get('price', 0) or 0),
                'high_price': float(row.get('high', 0) or 0),
                'low_price': float(row.get('low', 0) or 0),
                'pre_close_price': float(row.get('last_close', 0) or 0),
                'volume': int(row.get('volume', 0) or 0),
                'amount': int(row.get('amount', 0) or 0),
                'bid1': float(row.get('bid1', 0) or 0),
                'bid1_vol': int(row.get('bid_vol1', 0) or 0),
                'ask1': float(row.get('ask1', 0) or 0),
                'ask1_vol': int(row.get('ask_vol1', 0) or 0),
            }
            
        except Exception as e:
            logger.warning(f"获取股票 {symbol} 实时数据失败: {e}")
            return {}
    
    async def get_stock_realtime_batch(
        self, 
        symbols: List[str], 
        batch_size: int = 50
    ) -> pd.DataFrame:
        """
        异步批量获取股票实时行情
        
        分批并发请求，避免服务器拒绝
        
        Args:
            symbols: 股票代码列表
            batch_size: 每批次数量
            
        Returns:
            股票行情 DataFrame
        """
        if not symbols:
            return pd.DataFrame()
        
        logger.info(f"开始批量获取 {len(symbols)} 只股票实时行情...")
        
        results = []
        total_batches = (len(symbols) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(symbols))
            batch_symbols = symbols[start_idx:end_idx]
            
            def _fetch_batch(symbols_batch):
                client = self._get_client()
                batch_data = []
                for sym in symbols_batch:
                    try:
                        market = self._get_market(sym)
                        df = client.quotes(symbol=sym, market=market)
                        if df is not None and not df.empty:
                            row = df.iloc[0]
                            batch_data.append({
                                'code': sym,
                                'name': str(row.get('name', '')),
                                'open_price': float(row.get('open', 0) or 0),
                                'close_price': float(row.get('price', 0) or 0),
                                'high_price': float(row.get('high', 0) or 0),
                                'low_price': float(row.get('low', 0) or 0),
                                'pre_close_price': float(row.get('last_close', 0) or 0),
                                'volume': int(row.get('volume', 0) or 0),
                                'amount': int(row.get('amount', 0) or 0),
                                'bid1': float(row.get('bid1', 0) or 0),
                                'bid1_vol': int(row.get('bid_vol1', 0) or 0),
                                'bid2': float(row.get('bid2', 0) or 0),
                                'bid2_vol': int(row.get('bid_vol2', 0) or 0),
                                'bid3': float(row.get('bid3', 0) or 0),
                                'bid3_vol': int(row.get('bid_vol3', 0) or 0),
                                'ask1': float(row.get('ask1', 0) or 0),
                                'ask1_vol': int(row.get('ask_vol1', 0) or 0),
                                'ask2': float(row.get('ask2', 0) or 0),
                                'ask2_vol': int(row.get('ask_vol2', 0) or 0),
                                'ask3': float(row.get('ask3', 0) or 0),
                                'ask3_vol': int(row.get('ask_vol3', 0) or 0),
                            })
                    except Exception as e:
                        logger.warning(f"获取股票 {sym} 数据失败: {e}")
                return batch_data
            
            try:
                batch_data = await asyncio.to_thread(_fetch_batch, batch_symbols)
                results.extend(batch_data)
                logger.info(f"批次 {batch_idx + 1}/{total_batches} 完成，获取 {len(batch_data)} 条")
                
                # 批次间延迟
                if batch_idx < total_batches - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"批次 {batch_idx + 1} 失败: {e}")
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        logger.info(f"批量获取实时行情成功，共 {len(df)} 条数据")
        return df
    
    async def get_stock_hist(
        self, 
        symbol: str,
        start_date: str = "19700101",
        end_date: str = "20500101",
        period: str = "daily",
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        异步获取股票历史K线数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            period: 周期 daily/weekly/monthly
            adjust: 复权类型 (MOOTDX暂不支持复权参数)
            
        Returns:
            历史K线 DataFrame
        """
        def _fetch():
            client = self._get_client()
            market = self._get_market(symbol)
            
            # K线类型映射
            kline_map = {
                'daily': KLINE_TYPE.DAY,
                'weekly': KLINE_TYPE.WEEK,
                'monthly': KLINE_TYPE.MONTH,
            }
            kline_type = kline_map.get(period, KLINE_TYPE.DAY)
            
            return client.bars(
                symbol=symbol,
                market=market,
                frequency=kline_type,
                start=0,  # MOOTDX 使用 offset 获取数据
                count=800  # 每次最多800条
            )
        
        try:
            logger.info(f"开始获取股票 {symbol} 历史数据(MOOTDX)...")
            df = await asyncio.to_thread(_fetch)
            
            if df is None or df.empty:
                logger.warning(f"股票 {symbol} 历史数据为空")
                return pd.DataFrame()
            
            # MOOTDX bars 返回的列名
            column_mapping = {
                'date': 'date',
                'open': 'open',
                'close': 'close',
                'high': 'high',
                'low': 'low',
                'vol': 'volume',
                'amount': 'amount',
            }
            df = df.rename(columns=column_mapping)
            
            # 确保需要的列存在
            keep_cols = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']
            df = df[[col for col in keep_cols if col in df.columns]]
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.reset_index(drop=True, inplace=True)
            
            logger.info(f"获取股票 {symbol} 历史数据成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 历史数据失败: {e}")
            return pd.DataFrame()
    
    async def get_stock_hist_min(
        self,
        symbol: str,
        period: str = "5",
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        异步获取股票分时数据
        
        Args:
            symbol: 股票代码
            period: 周期 1/5/15/30/60 分钟
            adjust: 复权类型
            
        Returns:
            分时数据 DataFrame
        """
        def _fetch():
            client = self._get_client()
            market = self._get_market(symbol)
            
            # 分钟K线类型映射
            min_map = {
                '1': KLINE_TYPE.MIN1,
                '5': KLINE_TYPE.MIN5,
                '15': KLINE_TYPE.MIN15,
                '30': KLINE_TYPE.MIN30,
                '60': KLINE_TYPE.MIN60,
            }
            kline_type = min_map.get(period, KLINE_TYPE.MIN5)
            
            return client.bars(
                symbol=symbol,
                market=market,
                frequency=kline_type,
                start=0,
                count=800
            )
        
        try:
            logger.info(f"开始获取股票 {symbol} {period}分钟分时数据(MOOTDX)...")
            df = await asyncio.to_thread(_fetch)
            
            if df is None or df.empty:
                logger.warning(f"股票 {symbol} 分时数据为空")
                return pd.DataFrame()
            
            # 重命名列
            column_mapping = {
                'date': 'time',
                'open': 'open',
                'close': 'close',
                'high': 'high',
                'low': 'low',
                'vol': 'volume',
                'amount': 'amount',
            }
            df = df.rename(columns=column_mapping)
            
            logger.info(f"获取股票 {symbol} 分时数据成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 分时数据失败: {e}")
            return pd.DataFrame()
    
    async def get_all_stocks_realtime(self) -> pd.DataFrame:
        """
        异步获取全部A股实时行情
        
        先获取股票列表，再批量获取行情
        
        Returns:
            全量股票行情 DataFrame
        """
        # 获取股票列表
        stock_list = await self.get_stock_list()
        if stock_list.empty:
            return pd.DataFrame()
        
        symbols = stock_list['code'].tolist()
        
        # 批量获取行情
        return await self.get_stock_realtime_batch(symbols)
    
    def close(self):
        """关闭客户端连接"""
        if self._client:
            try:
                self._client.close()
            except:
                pass
            self._client = None
            logger.info("MOOTDX 客户端已关闭")
    
    async def crawl(self, *args, **kwargs):
        """异步爬取方法"""
        return await self.get_stock_list()