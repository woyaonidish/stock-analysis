#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETF数据爬虫 - 使用 httpx 支持同步和异步请求
"""

import math
import asyncio
import pandas as pd
from typing import Dict, Optional

from app.crawler.base_crawler import BaseCrawler


class ETFCrawler(BaseCrawler):
    """ETF数据爬虫"""
    
    def __init__(self):
        super().__init__()
        self._code_id_map = None
    
    # ==================== 同步方法 ====================
    
    def get_code_id_map(self) -> Dict[str, int]:
        """获取ETF代码与市场ID映射"""
        if self._code_id_map:
            return self._code_id_map
        
        url = "http://88.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1",
            "pz": "5000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "wbp2u": "|0|0|0|web",
            "fid": "f3",
            "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
            "fields": "f12,f13",
            "_": "1672806290972",
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        self._code_id_map = dict(zip(temp_df["f12"], temp_df["f13"]))
        
        return self._code_id_map
    
    def get_etf_spot(self) -> pd.DataFrame:
        """获取ETF实时行情"""
        url = "http://88.push2.eastmoney.com/api/qt/clist/get"
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
            "wbp2u": "|0|0|0|web",
            "fid": "f12",
            "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
            "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
            "_": "1672806290972",
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
        temp_df.rename(
            columns={
                "f12": "code",
                "f14": "name",
                "f2": "new_price",
                "f3": "change_rate",
                "f4": "change_amount",
                "f5": "volume",
                "f6": "amount",
                "f17": "open_price",
                "f15": "high_price",
                "f16": "low_price",
                "f18": "pre_close",
                "f8": "turnover_rate",
                "f21": "circulation_cap",
                "f20": "total_cap",
            },
            inplace=True,
        )
        
        temp_df = temp_df[[
            "code", "name", "new_price", "change_rate", "change_amount",
            "volume", "amount", "open_price", "high_price", "low_price",
            "pre_close", "turnover_rate", "circulation_cap", "total_cap"
        ]]
        
        # 转换数值类型
        for col in ["new_price", "change_rate", "change_amount", "volume", "amount",
                    "open_price", "high_price", "low_price", "pre_close", 
                    "turnover_rate", "circulation_cap", "total_cap"]:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        
        return temp_df
    
    def get_etf_hist(
        self,
        symbol: str = "159707",
        period: str = "daily",
        start_date: str = "19700101",
        end_date: str = "20500101",
        adjust: str = ""
    ) -> pd.DataFrame:
        """获取ETF历史数据"""
        code_id_dict = self.get_code_id_map()
        market_id = code_id_dict.get(symbol, 1)
        
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
        
        r = self.request(url, params=params)
        data_json = r.json()
        
        if not (data_json["data"] and data_json["data"]["klines"]):
            return pd.DataFrame()
        
        temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
        temp_df.columns = [
            "date", "open", "close", "high", "low",
            "volume", "amount", "amplitude", "change_pct", "change_amount", "turnover"
        ]
        
        temp_df.index = pd.to_datetime(temp_df["date"])
        temp_df.reset_index(drop=True, inplace=True)
        
        for col in ["open", "close", "high", "low", "volume", "amount",
                    "amplitude", "change_pct", "change_amount", "turnover"]:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        
        return temp_df
    
    def get_etf_hist_min(
        self,
        symbol: str = "159707",
        start_date: str = "1979-09-01 09:32:00",
        end_date: str = "2222-01-01 09:32:00",
        period: str = "5",
        adjust: str = ""
    ) -> pd.DataFrame:
        """获取ETF分时数据"""
        code_id_dict = self.get_code_id_map()
        market_id = code_id_dict.get(symbol, 1)
        
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
            
            r = self.request(url, params=params)
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
            
            r = self.request(url, params=params)
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
    
    # ==================== 异步方法 ====================
    
    async def async_get_code_id_map(self) -> Dict[str, int]:
        """异步获取ETF代码与市场ID映射"""
        if self._code_id_map:
            return self._code_id_map
        
        url = "http://88.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1",
            "pz": "5000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "wbp2u": "|0|0|0|web",
            "fid": "f3",
            "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
            "fields": "f12,f13",
            "_": "1672806290972",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        self._code_id_map = dict(zip(temp_df["f12"], temp_df["f13"]))
        
        return self._code_id_map
    
    async def async_get_etf_spot(self) -> pd.DataFrame:
        """异步获取ETF实时行情"""
        url = "http://88.push2.eastmoney.com/api/qt/clist/get"
        page_size = 50
        
        params = {
            "pn": 1,
            "pz": page_size,
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "wbp2u": "|0|0|0|web",
            "fid": "f12",
            "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
            "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
            "_": "1672806290972",
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
            
            responses = await self.async_batch_request(urls, params_list, delay=0.3)
            
            for response in responses:
                if response:
                    _data = response.json()["data"]["diff"]
                    data.extend(_data)
        
        temp_df = pd.DataFrame(data)
        temp_df.rename(
            columns={
                "f12": "code",
                "f14": "name",
                "f2": "new_price",
                "f3": "change_rate",
                "f4": "change_amount",
                "f5": "volume",
                "f6": "amount",
                "f17": "open_price",
                "f15": "high_price",
                "f16": "low_price",
                "f18": "pre_close",
                "f8": "turnover_rate",
                "f21": "circulation_cap",
                "f20": "total_cap",
            },
            inplace=True,
        )
        
        temp_df = temp_df[[
            "code", "name", "new_price", "change_rate", "change_amount",
            "volume", "amount", "open_price", "high_price", "low_price",
            "pre_close", "turnover_rate", "circulation_cap", "total_cap"
        ]]
        
        for col in ["new_price", "change_rate", "change_amount", "volume", "amount",
                    "open_price", "high_price", "low_price", "pre_close", 
                    "turnover_rate", "circulation_cap", "total_cap"]:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        
        return temp_df
    
    async def async_get_etf_hist(
        self,
        symbol: str = "159707",
        period: str = "daily",
        start_date: str = "19700101",
        end_date: str = "20500101",
        adjust: str = ""
    ) -> pd.DataFrame:
        """异步获取ETF历史数据"""
        code_id_dict = await self.async_get_code_id_map()
        market_id = code_id_dict.get(symbol, 1)
        
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
        temp_df.columns = ["date", "open", "close", "high", "low",
                          "volume", "amount", "amplitude", "change_pct", "change_amount", "turnover"]
        
        temp_df.index = pd.to_datetime(temp_df["date"])
        temp_df.reset_index(drop=True, inplace=True)
        
        for col in ["open", "close", "high", "low", "volume", "amount",
                    "amplitude", "change_pct", "change_amount", "turnover"]:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        
        return temp_df
    
    def crawl(self, **kwargs) -> pd.DataFrame:
        """实现爬取方法"""
        return self.get_etf_spot()
    
    async def async_crawl(self, **kwargs) -> pd.DataFrame:
        """异步爬取方法"""
        return await self.async_get_etf_spot()