#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票历史数据爬虫 - 使用 httpx 异步请求
"""

import math
import asyncio
import pandas as pd
from typing import Optional, Dict

from app.crawler.base_crawler import BaseCrawler


class StockHistCrawler(BaseCrawler):
    """股票历史数据爬虫"""
    
    def __init__(self):
        super().__init__()
        self._code_id_map = None
    
    async def get_code_id_map(self) -> Dict[str, int]:
        """
        获取股票代码与市场ID映射
        
        Returns:
            股票代码到市场ID的映射字典
        """
        if self._code_id_map:
            return self._code_id_map
        
        url = "http://80.push2.eastmoney.com/api/qt/clist/get"
        page_size = 50
        
        # 上证股票
        params = {
            "pn": 1,
            "pz": page_size,
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f12",
            "fs": "m:1 t:2,m:1 t:23",
            "fields": "f12",
            "_": "1623833739532",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        code_id_dict = {}
        for item in data:
            code_id_dict[item['f12']] = 1  # 上证
        
        # 深证股票
        params["fs"] = "m:0 t:6,m:0 t:80"
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        for item in data:
            code_id_dict[item['f12']] = 0  # 深证
        
        # 北交所
        params = {
            "pn": 1,
            "pz": page_size,
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f12",
            "fs": "m:0 t:81 s:2048",
            "fields": "f12",
            "_": "1623833739532",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
        
        for item in data:
            code_id_dict[item['f12']] = 0  # 北交所
        
        self._code_id_map = code_id_dict
        return code_id_dict
    
    async def get_stock_hist(
        self, 
        symbol: str, 
        period: str = "daily",
        start_date: str = "19700101", 
        end_date: str = "20500101", 
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        获取股票历史K线数据
        
        Args:
            symbol: 股票代码
            period: 周期 daily/weekly/monthly
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型 ""/"qfq"/"hfq"
            
        Returns:
            历史K线数据DataFrame
        """
        code_id_dict = await self.get_code_id_map()
        market_id = code_id_dict.get(symbol, 0)
        
        adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
        period_dict = {"daily": "101", "weekly": "102", "monthly": "103"}
        
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "klt": period_dict[period],
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
        temp_df.columns = [
            "date", "open", "close", "high", "low", 
            "volume", "amount", "amplitude", "change_pct", 
            "change_amount", "turnover"
        ]
        
        temp_df.index = pd.to_datetime(temp_df["date"])
        temp_df.reset_index(drop=True, inplace=True)
        
        # 转换数值类型
        for col in ["open", "close", "high", "low", "volume", "amount", 
                    "amplitude", "change_pct", "change_amount", "turnover"]:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        
        return temp_df
    
    async def get_stock_hist_min(
        self,
        symbol: str,
        start_date: str = "1979-09-01 09:32:00",
        end_date: str = "2222-01-01 09:32:00",
        period: str = "5",
        adjust: str = ""
    ) -> pd.DataFrame:
        """
        获取股票分时数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期时间
            end_date: 结束日期时间
            period: 周期 1/5/15/30/60分钟
            adjust: 复权类型
            
        Returns:
            分时数据DataFrame
        """
        code_id_dict = await self.get_code_id_map()
        market_id = code_id_dict.get(symbol, 0)
        
        adjust_map = {"": "0", "qfq": "1", "hfq": "2"}
        
        if period == "1":
            url = "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
            params = {
                "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "ndays": "5",
                "iscr": "0",
                "secid": f"{market_id}.{symbol}",
                "_": "1623766962675",
            }
            
            r = await self.async_request(url, params=params)
            data_json = r.json()
            
            if not data_json.get("data") or not data_json["data"].get("trends"):
                return pd.DataFrame()
            
            temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["trends"]])
            temp_df.columns = ["time", "open", "close", "high", "low", "volume", "amount", "price"]
            
            temp_df.index = pd.to_datetime(temp_df["time"])
            temp_df = temp_df[start_date:end_date]
            temp_df.reset_index(drop=True, inplace=True)
            
            for col in ["open", "close", "high", "low", "volume", "amount", "price"]:
                temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
            
            temp_df["time"] = pd.to_datetime(temp_df["time"]).astype(str)
            return temp_df
        else:
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "klt": period,
                "fqt": adjust_map[adjust],
                "secid": f"{market_id}.{symbol}",
                "beg": "0",
                "end": "20500000",
                "_": "1630930917857",
            }
            
            r = await self.async_request(url, params=params)
            data_json = r.json()
            
            if not data_json.get("data") or not data_json["data"].get("klines"):
                return pd.DataFrame()
            
            temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
            temp_df.columns = [
                "time", "open", "close", "high", "low",
                "volume", "amount", "amplitude", "change_pct", "change_amount", "turnover"
            ]
            
            temp_df.index = pd.to_datetime(temp_df["time"])
            temp_df = temp_df[start_date:end_date]
            temp_df.reset_index(drop=True, inplace=True)
            
            for col in ["open", "close", "high", "low", "volume", "amount", 
                        "amplitude", "change_pct", "change_amount", "turnover"]:
                temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
            
            temp_df["time"] = pd.to_datetime(temp_df["time"]).astype(str)
            return temp_df[["time", "open", "close", "high", "low", "change_pct", 
                           "change_amount", "volume", "amount", "amplitude", "turnover"]]
    
    async def crawl(self, symbol: str = "000001", **kwargs) -> pd.DataFrame:
        """异步爬取方法"""
        return await self.get_stock_hist(symbol, **kwargs)