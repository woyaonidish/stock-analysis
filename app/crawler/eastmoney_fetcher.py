#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
东方财富网爬虫 - 使用 httpx 支持同步和异步请求
"""

import math
import asyncio
import pandas as pd
from typing import Optional, Dict
from pathlib import Path

from app.crawler.base_crawler import BaseCrawler
from app.config import settings


class EastMoneyFetcher(BaseCrawler):
    """东方财富网数据获取器"""
    
    def __init__(self):
        super().__init__()
        self._cookie = None
        self._code_id_map = None
    
    def _get_cookie(self) -> str:
        """获取Cookie"""
        if self._cookie:
            return self._cookie
        
        # 1. 从环境变量获取
        cookie = settings.EAST_MONEY_COOKIE
        if cookie:
            return cookie
        
        # 2. 从文件获取
        cookie_file = Path(settings.PROXY_FILE).parent / 'eastmoney_cookie.txt'
        if cookie_file.exists():
            with open(cookie_file, 'r') as f:
                cookie = f.read().strip()
            if cookie:
                return cookie
        
        # 3. 默认Cookie
        return 'st_si=78948464251292; st_psi=20260205091253851-119144370567-1089607836'
    
    def _update_headers_cookie(self):
        """更新请求头Cookie"""
        cookie = self._get_cookie()
        self._headers['Cookie'] = cookie
    
    # ==================== 同步方法 ====================
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取A股实时行情列表
        
        Returns:
            股票数据DataFrame
        """
        self._update_headers_cookie()
        
        url = "http://82.push2.eastmoney.com/api/qt/clist/get"
        page_size = 50
        page_current = 1
        params = {
            "pn": page_current,
            "pz": page_size,
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f12",
            "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
            "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f37,f38,f39,f40,f41,f45,f46,f48,f49,f57,f61,f100,f112,f113,f114,f115,f221",
            "_": "1623833739532",
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        if not data:
            return pd.DataFrame()
        
        data_count = data_json["data"]["total"]
        page_count = math.ceil(data_count / page_size)
        
        while page_count > 1:
            import time
            import random
            time.sleep(random.uniform(1, 1.5))
            page_current += 1
            params["pn"] = page_current
            r = self.request(url, params=params)
            data_json = r.json()
            _data = data_json["data"]["diff"]
            data.extend(_data)
            page_count -= 1
        
        temp_df = pd.DataFrame(data)
        # 重命名列
        column_mapping = {
            'f12': 'code', 'f14': 'name', 'f2': 'new_price', 'f3': 'change_rate',
            'f4': 'ups_downs', 'f5': 'volume', 'f6': 'deal_amount', 'f7': 'amplitude',
            'f8': 'turnoverrate', 'f10': 'volume_ratio', 'f17': 'open_price',
            'f15': 'high_price', 'f16': 'low_price', 'f18': 'pre_close_price',
            'f20': 'total_market_cap', 'f21': 'free_cap', 'f46': 'pe9',
            'f45': 'pbnewmrq', 'f116': 'industry'
        }
        temp_df = temp_df.rename(columns=column_mapping)
        
        return temp_df
    
    def get_code_id_map(self) -> Dict[str, int]:
        """获取股票代码与市场ID映射"""
        if self._code_id_map:
            return self._code_id_map
        
        url = "http://80.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1, "pz": 50, "po": "1", "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2", "invt": "2", "fid": "f12",
            "fs": "m:1 t:2,m:1 t:23",
            "fields": "f12", "_": "1623833739532",
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        code_id_dict = {}
        for item in data:
            code_id_dict[item['f12']] = 1  # 上证
        
        # 深证
        params["fs"] = "m:0 t:6,m:0 t:80"
        r = self.request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        for item in data:
            code_id_dict[item['f12']] = 0  # 深证
        
        self._code_id_map = code_id_dict
        return code_id_dict
    
    def get_stock_hist(self, symbol: str, start_date: str = "19700101", 
                       end_date: str = "20500101", adjust: str = "") -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型 "" "qfq" "hfq"
            
        Returns:
            历史数据DataFrame
        """
        code_id_dict = self.get_code_id_map()
        market_id = code_id_dict.get(symbol, 0)
        
        adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
        
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "klt": "101",  # 日线
            "fqt": adjust_dict[adjust],
            "secid": f"{market_id}.{symbol}",
            "beg": start_date,
            "end": end_date,
            "_": "1623766962675",
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        
        if not (data_json["data"] and data_json["data"]["klines"]):
            return pd.DataFrame()
        
        temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
        temp_df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 
                          'amplitude', 'quote_change', 'ups_downs', 'turnover']
        
        temp_df.index = pd.to_datetime(temp_df["date"])
        temp_df.reset_index(drop=True, inplace=True)
        
        # 转换数值类型
        for col in ['open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'quote_change', 'ups_downs', 'turnover']:
            temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')
        
        return temp_df
    
    def get_etf_list(self) -> pd.DataFrame:
        """获取ETF实时行情"""
        url = "http://82.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1, "pz": 500, "po": "1", "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2", "invt": "2", "fid": "f12",
            "fs": "b:MK0404",
            "fields": "f12,f14,f2,f3,f4,f5,f6,f17,f15,f16,f18,f10,f20,f21",
            "_": "1623833739532",
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        temp_df = pd.DataFrame(data)
        column_mapping = {
            'f12': 'code', 'f14': 'name', 'f2': 'new_price', 'f3': 'change_rate',
            'f4': 'ups_downs', 'f5': 'volume', 'f6': 'deal_amount',
            'f17': 'open_price', 'f15': 'high_price', 'f16': 'low_price',
            'f18': 'pre_close_price', 'f10': 'turnoverrate',
            'f20': 'total_market_cap', 'f21': 'free_cap'
        }
        temp_df = temp_df.rename(columns=column_mapping)
        
        return temp_df
    
    # ==================== 异步方法 ====================
    
    async def async_get_stock_list(self) -> pd.DataFrame:
        """
        异步获取A股实时行情列表
        
        Returns:
            股票数据DataFrame
        """
        self._update_headers_cookie()
        
        url = "http://82.push2.eastmoney.com/api/qt/clist/get"
        page_size = 50
        params = {
            "pn": 1,
            "pz": page_size,
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f12",
            "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
            "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f37,f38,f39,f40,f41,f45,f46,f48,f49,f57,f61,f100,f112,f113,f114,f115,f221",
            "_": "1623833739532",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        if not data:
            return pd.DataFrame()
        
        data_count = data_json["data"]["total"]
        page_count = math.ceil(data_count / page_size)
        
        # 异步请求剩余页面
        if page_count > 1:
            urls = []
            params_list = []
            for page in range(2, page_count + 1):
                page_params = params.copy()
                page_params["pn"] = page
                urls.append(url)
                params_list.append(page_params)
            
            # 并发请求，带延迟避免被封
            responses = await self.async_batch_request(urls, params_list, delay=0.3)
            
            for response in responses:
                if response:
                    _data = response.json()["data"]["diff"]
                    data.extend(_data)
        
        temp_df = pd.DataFrame(data)
        column_mapping = {
            'f12': 'code', 'f14': 'name', 'f2': 'new_price', 'f3': 'change_rate',
            'f4': 'ups_downs', 'f5': 'volume', 'f6': 'deal_amount', 'f7': 'amplitude',
            'f8': 'turnoverrate', 'f10': 'volume_ratio', 'f17': 'open_price',
            'f15': 'high_price', 'f16': 'low_price', 'f18': 'pre_close_price',
            'f20': 'total_market_cap', 'f21': 'free_cap', 'f46': 'pe9',
            'f45': 'pbnewmrq', 'f116': 'industry'
        }
        temp_df = temp_df.rename(columns=column_mapping)
        
        return temp_df
    
    async def async_get_code_id_map(self) -> Dict[str, int]:
        """异步获取股票代码与市场ID映射"""
        if self._code_id_map:
            return self._code_id_map
        
        url = "http://80.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1, "pz": 50, "po": "1", "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2", "invt": "2", "fid": "f12",
            "fs": "m:1 t:2,m:1 t:23",
            "fields": "f12", "_": "1623833739532",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        code_id_dict = {}
        for item in data:
            code_id_dict[item['f12']] = 1  # 上证
        
        # 深证
        params["fs"] = "m:0 t:6,m:0 t:80"
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        for item in data:
            code_id_dict[item['f12']] = 0  # 深证
        
        self._code_id_map = code_id_dict
        return code_id_dict
    
    async def async_get_stock_hist(self, symbol: str, start_date: str = "19700101", 
                                    end_date: str = "20500101", adjust: str = "") -> pd.DataFrame:
        """
        异步获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型 "" "qfq" "hfq"
            
        Returns:
            历史数据DataFrame
        """
        code_id_dict = await self.async_get_code_id_map()
        market_id = code_id_dict.get(symbol, 0)
        
        adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
        
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "klt": "101",  # 日线
            "fqt": adjust_dict[adjust],
            "secid": f"{market_id}.{symbol}",
            "beg": start_date,
            "end": end_date,
            "_": "1623766962675",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        
        if not (data_json["data"] and data_json["data"]["klines"]):
            return pd.DataFrame()
        
        temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
        temp_df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 
                          'amplitude', 'quote_change', 'ups_downs', 'turnover']
        
        temp_df.index = pd.to_datetime(temp_df["date"])
        temp_df.reset_index(drop=True, inplace=True)
        
        for col in ['open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'quote_change', 'ups_downs', 'turnover']:
            temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')
        
        return temp_df
    
    async def async_get_etf_list(self) -> pd.DataFrame:
        """异步获取ETF实时行情"""
        url = "http://82.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1, "pz": 500, "po": "1", "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2", "invt": "2", "fid": "f12",
            "fs": "b:MK0404",
            "fields": "f12,f14,f2,f3,f4,f5,f6,f17,f15,f16,f18,f10,f20,f21",
            "_": "1623833739532",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        temp_df = pd.DataFrame(data)
        column_mapping = {
            'f12': 'code', 'f14': 'name', 'f2': 'new_price', 'f3': 'change_rate',
            'f4': 'ups_downs', 'f5': 'volume', 'f6': 'deal_amount',
            'f17': 'open_price', 'f15': 'high_price', 'f16': 'low_price',
            'f18': 'pre_close_price', 'f10': 'turnoverrate',
            'f20': 'total_market_cap', 'f21': 'free_cap'
        }
        temp_df = temp_df.rename(columns=column_mapping)
        
        return temp_df
    
    def crawl(self, *args, **kwargs):
        """实现爬取方法"""
        return self.get_stock_list()
    
    async def async_crawl(self, *args, **kwargs):
        """异步爬取方法"""
        return await self.async_get_stock_list()