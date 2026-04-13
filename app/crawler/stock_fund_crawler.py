#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
资金流向数据爬虫 - 使用 httpx 异步请求
"""

import json
import math
import time
import asyncio
import pandas as pd
from typing import Optional

from app.crawler.base_crawler import BaseCrawler


class StockFundCrawler(BaseCrawler):
    """资金流向数据爬虫"""
    
    # 指标映射
    INDIVIDUAL_INDICATOR_MAP = {
        "今日": [
            "f62",
            "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124",
        ],
        "3日": [
            "f267",
            "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124",
        ],
        "5日": [
            "f164",
            "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124",
        ],
        "10日": [
            "f174",
            "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124",
        ],
    }
    
    SECTOR_TYPE_MAP = {"行业资金流": "2", "概念资金流": "3", "地域资金流": "1"}
    
    SECTOR_INDICATOR_MAP = {
        "今日": [
            "f62",
            "1",
            "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124",
        ],
        "5日": [
            "f164",
            "5",
            "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124",
        ],
        "10日": [
            "f174",
            "10",
            "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124",
        ],
    }
    
    async def get_individual_fund_flow_rank(self, indicator: str = "5日") -> pd.DataFrame:
        """获取个股资金流向排名"""
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        page_size = 50
        
        params = {
            "fid": self.INDIVIDUAL_INDICATOR_MAP[indicator][0],
            "po": "1",
            "pz": page_size,
            "pn": 1,
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
            "fields": self.INDIVIDUAL_INDICATOR_MAP[indicator][1],
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        data = data_json["data"]["diff"]
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
        temp_df = temp_df[~temp_df["f2"].isin(["-"])]
        
        if indicator == "今日":
            temp_df = self._process_today_columns(temp_df)
        elif indicator == "3日":
            temp_df = self._process_3day_columns(temp_df)
        elif indicator == "5日":
            temp_df = self._process_5day_columns(temp_df)
        elif indicator == "10日":
            temp_df = self._process_10day_columns(temp_df)
        
        return temp_df
    
    def _process_today_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "最新价", "今日涨跌幅", "代码", "名称",
            "今日主力净流入-净额", "今日超大单净流入-净额",
            "今日超大单净流入-净占比", "今日大单净流入-净额",
            "今日大单净流入-净占比", "今日中单净流入-净额",
            "今日中单净流入-净占比", "今日小单净流入-净额",
            "今日小单净流入-净占比", "_", "今日主力净流入-净占比",
            "_", "_", "_",
        ]
        return df[[
            "代码", "名称", "最新价", "今日涨跌幅",
            "今日主力净流入-净额", "今日主力净流入-净占比",
            "今日超大单净流入-净额", "今日超大单净流入-净占比",
            "今日大单净流入-净额", "今日大单净流入-净占比",
            "今日中单净流入-净额", "今日中单净流入-净占比",
            "今日小单净流入-净额", "今日小单净流入-净占比",
        ]]
    
    def _process_3day_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "最新价", "代码", "名称", "_", "3日涨跌幅",
            "_", "_", "_", "3日主力净流入-净额", "3日主力净流入-净占比",
            "3日超大单净流入-净额", "3日超大单净流入-净占比",
            "3日大单净流入-净额", "3日大单净流入-净占比",
            "3日中单净流入-净额", "3日中单净流入-净占比",
            "3日小单净流入-净额", "3日小单净流入-净占比",
        ]
        return df[[
            "代码", "名称", "最新价", "3日涨跌幅",
            "3日主力净流入-净额", "3日主力净流入-净占比",
            "3日超大单净流入-净额", "3日超大单净流入-净占比",
            "3日大单净流入-净额", "3日大单净流入-净占比",
            "3日中单净流入-净额", "3日中单净流入-净占比",
            "3日小单净流入-净额", "3日小单净流入-净占比",
        ]]
    
    def _process_5day_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "最新价", "代码", "名称", "5日涨跌幅", "_",
            "5日主力净流入-净额", "5日主力净流入-净占比",
            "5日超大单净流入-净额", "5日超大单净流入-净占比",
            "5日大单净流入-净额", "5日大单净流入-净占比",
            "5日中单净流入-净额", "5日中单净流入-净占比",
            "5日小单净流入-净额", "5日小单净流入-净占比",
            "_", "_", "_",
        ]
        return df[[
            "代码", "名称", "最新价", "5日涨跌幅",
            "5日主力净流入-净额", "5日主力净流入-净占比",
            "5日超大单净流入-净额", "5日超大单净流入-净占比",
            "5日大单净流入-净额", "5日大单净流入-净占比",
            "5日中单净流入-净额", "5日中单净流入-净占比",
            "5日小单净流入-净额", "5日小单净流入-净占比",
        ]]
    
    def _process_10day_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "最新价", "代码", "名称", "_", "10日涨跌幅",
            "10日主力净流入-净额", "10日主力净流入-净占比",
            "10日超大单净流入-净额", "10日超大单净流入-净占比",
            "10日大单净流入-净额", "10日大单净流入-净占比",
            "10日中单净流入-净额", "10日中单净流入-净占比",
            "10日小单净流入-净额", "10日小单净流入-净占比",
            "_", "_", "_",
        ]
        return df[[
            "代码", "名称", "最新价", "10日涨跌幅",
            "10日主力净流入-净额", "10日主力净流入-净占比",
            "10日超大单净流入-净额", "10日超大单净流入-净占比",
            "10日大单净流入-净额", "10日大单净流入-净占比",
            "10日中单净流入-净额", "10日中单净流入-净占比",
            "10日小单净流入-净额", "10日小单净流入-净占比",
        ]]
    
    async def get_sector_fund_flow_rank(
        self, indicator: str = "10日", sector_type: str = "行业资金流"
    ) -> pd.DataFrame:
        """获取板块资金流向排名"""
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        page_size = 50
        
        params = {
            "pn": 1,
            "pz": page_size,
            "po": "1",
            "np": "1",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "fltt": "2",
            "invt": "2",
            "fid0": self.SECTOR_INDICATOR_MAP[indicator][0],
            "fs": f"m:90 t:{self.SECTOR_TYPE_MAP[sector_type]}",
            "stat": self.SECTOR_INDICATOR_MAP[indicator][1],
            "fields": self.SECTOR_INDICATOR_MAP[indicator][2],
            "rt": "52975239",
            "cb": "jQuery18308357908311220152_1589256588824",
            "_": int(time.time() * 1000),
        }
        
        r = await self.async_request(url, params=params)
        text_data = r.text
        data_json = json.loads(text_data[text_data.find("{"): -2])
        data = data_json["data"]["diff"]
        
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
                    text_data = response.text
                    json_data = json.loads(text_data[text_data.find("{"): -2])
                    _data = json_data["data"]["diff"]
                    data.extend(_data)
        
        temp_df = pd.DataFrame(data)
        temp_df = temp_df[~temp_df["f2"].isin(["-"])]
        
        if indicator == "今日":
            temp_df = self._process_sector_today_columns(temp_df)
        elif indicator == "5日":
            temp_df = self._process_sector_5day_columns(temp_df)
        elif indicator == "10日":
            temp_df = self._process_sector_10day_columns(temp_df)
        
        return temp_df
    
    def _process_sector_today_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "-", "今日涨跌幅", "_", "名称",
            "今日主力净流入-净额", "今日超大单净流入-净额",
            "今日超大单净流入-净占比", "今日大单净流入-净额",
            "今日大单净流入-净占比", "今日中单净流入-净额",
            "今日中单净流入-净占比", "今日小单净流入-净额",
            "今日小单净流入-净占比", "-", "今日主力净流入-净占比",
            "今日主力净流入最大股", "今日主力净流入最大股代码", "是否净流入",
        ]
        return df[[
            "名称", "今日涨跌幅",
            "今日主力净流入-净额", "今日主力净流入-净占比",
            "今日超大单净流入-净额", "今日超大单净流入-净占比",
            "今日大单净流入-净额", "今日大单净流入-净占比",
            "今日中单净流入-净额", "今日中单净流入-净占比",
            "今日小单净流入-净额", "今日小单净流入-净占比",
            "今日主力净流入最大股",
        ]]
    
    def _process_sector_5day_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "-", "_", "名称", "5日涨跌幅", "_",
            "5日主力净流入-净额", "5日主力净流入-净占比",
            "5日超大单净流入-净额", "5日超大单净流入-净占比",
            "5日大单净流入-净额", "5日大单净流入-净占比",
            "5日中单净流入-净额", "5日中单净流入-净占比",
            "5日小单净流入-净额", "5日小单净流入-净占比",
            "5日主力净流入最大股", "_", "_",
        ]
        return df[[
            "名称", "5日涨跌幅",
            "5日主力净流入-净额", "5日主力净流入-净占比",
            "5日超大单净流入-净额", "5日超大单净流入-净占比",
            "5日大单净流入-净额", "5日大单净流入-净占比",
            "5日中单净流入-净额", "5日中单净流入-净占比",
            "5日小单净流入-净额", "5日小单净流入-净占比",
            "5日主力净流入最大股",
        ]]
    
    def _process_sector_10day_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "-", "_", "名称", "_", "10日涨跌幅",
            "10日主力净流入-净额", "10日主力净流入-净占比",
            "10日超大单净流入-净额", "10日超大单净流入-净占比",
            "10日大单净流入-净额", "10日大单净流入-净占比",
            "10日中单净流入-净额", "10日中单净流入-净占比",
            "10日小单净流入-净额", "10日小单净流入-净占比",
            "10日主力净流入最大股", "_", "_",
        ]
        return df[[
            "名称", "10日涨跌幅",
            "10日主力净流入-净额", "10日主力净流入-净占比",
            "10日超大单净流入-净额", "10日超大单净流入-净占比",
            "10日大单净流入-净额", "10日大单净流入-净占比",
            "10日中单净流入-净额", "10日中单净流入-净占比",
            "10日小单净流入-净额", "10日小单净流入-净占比",
            "10日主力净流入最大股",
        ]]
    
    async def crawl(self, indicator: str = "5日", **kwargs) -> pd.DataFrame:
        """异步爬取方法"""
        return await self.get_individual_fund_flow_rank(indicator)