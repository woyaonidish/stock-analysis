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
from mootdx.consts import (
    KLINE_DAILY, KLINE_WEEKLY, KLINE_MONTHLY,
    KLINE_1MIN, KLINE_5MIN, KLINE_15MIN, KLINE_30MIN, KLINE_1HOUR
)

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
            
            # 过滤只保留沪深A股
            # 沪市A股: 60xxxx, 科创板: 68xxxx
            # 深市A股: 00xxxx, 创业板: 30xxxx
            # 排除北交所(8xxxxx, 4xxxxx)和其他特殊品种
            def is_valid_a_stock(code):
                code = str(code).zfill(6)
                # 沪市A股和科创板
                if code.startswith('60') or code.startswith('68'):
                    return True
                # 深市A股和创业板
                if code.startswith('00') or code.startswith('30'):
                    return True
                return False
            
            df = df[df['code'].apply(is_valid_a_stock)]
            df = df.reset_index(drop=True)
            
            logger.info(f"获取A股股票列表成功，共 {len(df)} 条数据（已过滤北交所等特殊品种）")
            return df
        
        try:
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    async def get_stock_realtime(self, symbol: str, name: str = '') -> Dict:
        """
        异步获取单只股票实时行情
        
        Args:
            symbol: 股票代码
            name: 股票名称（可选，MOOTDX quotes 不返回 name）
            
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
                'name': name,  # name 需要外部传入
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
        batch_size: int = 50,
        on_batch_save: callable = None,
        code_name_map: Dict[str, str] = None
    ) -> int:
        """
        异步批量获取股票实时行情
        
        分批请求，每批次获取后可立即保存（通过回调函数）
        
        Args:
            symbols: 股票代码列表
            batch_size: 每批次数量
            on_batch_save: 批次保存回调函数，接收 DataFrame 和批次索引
            code_name_map: 股票代码到名称的映射字典
            
        Returns:
            总获取条数
        """
        if not symbols:
            return 0
        
        # 过滤无效股票代码，避免 NotImplementedError
        def is_valid_code(code):
            code = str(code).zfill(6)
            return code.startswith('60') or code.startswith('68') or \
                   code.startswith('00') or code.startswith('30')
        
        valid_symbols = [s for s in symbols if is_valid_code(s)]
        if len(valid_symbols) < len(symbols):
            logger.warning(f"过滤掉 {len(symbols) - len(valid_symbols)} 个无效股票代码")
        
        if not valid_symbols:
            return 0
        
        logger.info(f"开始批量获取 {len(valid_symbols)} 只股票实时行情...")
        
        total_saved = 0
        total_batches = (len(valid_symbols) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(valid_symbols))
            batch_symbols = valid_symbols[start_idx:end_idx]
            
            def _fetch_batch(symbols_batch):
                client = self._get_client()
                batch_data = []
                for sym in symbols_batch:
                    try:
                        market = self._get_market(sym)
                        df = client.quotes(symbol=sym, market=market)
                        if df is not None and not df.empty:
                            row = df.iloc[0]
                            # name 从映射字典获取，quotes 接口不返回 name
                            stock_name = code_name_map.get(sym, '') if code_name_map else ''
                            batch_data.append({
                                'code': sym,
                                'name': stock_name,
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
                    except Exception as err:
                        logger.warning(f"获取股票 {sym} 数据失败: {err}")
                return batch_data
            
            try:
                batch_data = await asyncio.to_thread(_fetch_batch, batch_symbols)
                
                if batch_data:
                    batch_df = pd.DataFrame(batch_data)
                    saved_count = len(batch_data)
                    
                    # 调用保存回调
                    if on_batch_save:
                        try:
                            on_batch_save(batch_df, batch_idx)
                        except Exception as save_err:
                            logger.error(f"批次 {batch_idx + 1} 保存失败: {save_err}")
                            # 关键修复：异常后需要恢复 Session 状态才能继续
                            # 回调函数内部应该已经 rollback，这里记录错误并继续
                            # 但后续批次可能使用损坏的 Session，需要在外层处理
                    
                    total_saved += saved_count
                    logger.info(f"批次 {batch_idx + 1}/{total_batches} 完成，获取 {saved_count} 条，累计 {total_saved} 条")
                
                # 批次间延迟
                if batch_idx < total_batches - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"批次 {batch_idx + 1} 失败: {e}")
        
        logger.info(f"批量获取实时行情完成，共获取 {total_saved} 条数据")
        return total_saved
    
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
                'daily': KLINE_DAILY,
                'weekly': KLINE_WEEKLY,
                'monthly': KLINE_MONTHLY,
            }
            kline_type = kline_map.get(period, KLINE_DAILY)
            
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
                '1': KLINE_1MIN,
                '5': KLINE_5MIN,
                '15': KLINE_15MIN,
                '30': KLINE_30MIN,
                '60': KLINE_1HOUR,
            }
            kline_type = min_map.get(period, KLINE_5MIN)
            
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
    
    async def get_all_stocks_realtime(self, on_batch_save: callable = None) -> int:
        """
        异步获取全部A股实时行情
        
        先获取股票列表建立 code→name 映射，再批量获取行情
        
        Args:
            on_batch_save: 批次保存回调函数
            
        Returns:
            总获取条数
        """
        # 获取股票列表（包含 code 和 name）
        stock_list = await self.get_stock_list()
        if stock_list.empty:
            return 0
        
        symbols = stock_list['code'].tolist()
        
        # 建立 code → name 映射字典
        # 注意：MOOTDX quotes 接口不返回 name，需要从 stocks 接口获取
        code_name_map = dict(zip(stock_list['code'], stock_list['name']))
        logger.info(f"建立股票代码-名称映射，共 {len(code_name_map)} 条")
        
        # 批量获取行情（每批次保存），传入映射字典填充 name
        return await self.get_stock_realtime_batch(
            symbols, 
            on_batch_save=on_batch_save,
            code_name_map=code_name_map
        )
    
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
    
    # ==================== 指数数据获取 ====================
    
    # 主要指数代码映射
    INDEX_CODE_MAP = {
        # 沪市指数
        '000001': ('上证指数', 1),
        '000016': ('上证50', 1),
        '000300': ('沪深300', 1),
        '000905': ('中证500', 1),
        '000852': ('中证1000', 1),
        # 深市指数
        '399001': ('深证成指', 0),
        '399006': ('创业板指', 0),
        '399300': ('沪深300', 0),  # 深市版本
        '399005': ('中小板指', 0),
    }
    
    async def get_index_realtime(self) -> pd.DataFrame:
        """
        异步获取主要指数实时行情
        
        Returns:
            指数行情 DataFrame
        """
        def _fetch():
            client = self._get_client()
            logger.info("开始获取指数实时行情(MOOTDX)...")
            
            results = []
            for code, (name, market) in self.INDEX_CODE_MAP.items():
                try:
                    df = client.index(market=market)
                    if df is not None and not df.empty:
                        # index 返回所有指数数据，筛选目标指数
                        # 注意：MOOTDX index() 返回的是市场所有指数，不是单只
                        # 需要通过其他方式获取单只指数行情
                        pass
                except Exception as e:
                    logger.warning(f"获取指数 {code} 数据失败: {e}")
            
            # 实际上 MOOTDX 的 index() 返回市场指数列表
            # 我们使用 quotes 获取指数实时数据
            for code, (name, market) in self.INDEX_CODE_MAP.items():
                try:
                    df = client.quotes(symbol=code, market=market)
                    if df is not None and not df.empty:
                        row = df.iloc[0]
                        results.append({
                            'code': code,
                            'name': name,
                            'open_price': float(row.get('open', 0) or 0),
                            'close_price': float(row.get('price', 0) or 0),
                            'high_price': float(row.get('high', 0) or 0),
                            'low_price': float(row.get('low', 0) or 0),
                            'pre_close': float(row.get('last_close', 0) or 0),
                            'volume': int(row.get('volume', 0) or 0),
                            'amount': int(row.get('amount', 0) or 0),
                        })
                except Exception as e:
                    logger.warning(f"获取指数 {code} 数据失败: {e}")
            
            if results:
                df = pd.DataFrame(results)
                # 计算涨跌幅
                if 'pre_close' in df.columns and 'close_price' in df.columns:
                    df['change_rate'] = ((df['close_price'] - df['pre_close']) / df['pre_close'] * 100).round(2)
                logger.info(f"获取指数行情成功，共 {len(df)} 条")
                return df
            return pd.DataFrame()
        
        try:
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            logger.error(f"获取指数行情失败: {e}")
            return pd.DataFrame()
    
    # ==================== 财务数据获取 ====================
    
    async def get_financial_data(self, filepath: str) -> pd.DataFrame:
        """
        异步解析财务数据文件
        
        MOOTDX 财务数据需要先下载 gpcw*.zip 文件，再解析
        可通过 mootdx.affair.Affair.fetch() 下载
        
        Args:
            filepath: 财务数据文件路径 (gpcw20231231.zip 或 .dat)
            
        Returns:
            财务数据 DataFrame（完整字段）
        """
        def _parse():
            from mootdx.financial.financial import FinancialReader
            
            logger.info(f"开始解析财务数据文件: {filepath}")
            
            try:
                df = FinancialReader.to_data(filepath, header='zh')
                logger.info(f"解析财务数据成功，共 {len(df)} 条，{len(df.columns)} 列")
                return df
            except Exception as e:
                logger.error(f"解析财务数据失败: {e}")
                return pd.DataFrame()
        
        try:
            return await asyncio.to_thread(_parse)
        except Exception as e:
            logger.error(f"解析财务数据失败: {e}")
            return pd.DataFrame()
    
    async def download_financial_files(self, downdir: str) -> List[str]:
        """
        异步下载财务数据文件列表
        
        Args:
            downdir: 下载目录
            
        Returns:
            下载的文件列表
        """
        def _download():
            from mootdx.affair import Affair
            from mootdx.financial.financial import FinancialList
            
            logger.info(f"开始获取财务数据文件列表...")
            
            # 获取文件列表
            flist = FinancialList()
            flist_file = flist.content(downdir=downdir + '/gpcw.txt')
            
            if flist_file is None:
                logger.warning("获取财务文件列表失败")
                return []
            
            # 解析文件列表
            files = flist.parse(flist_file)
            logger.info(f"获取到 {len(files)} 个财务数据文件")
            
            return files
        
        try:
            return await asyncio.to_thread(_download)
        except Exception as e:
            logger.error(f"获取财务文件列表失败: {e}")
            return []