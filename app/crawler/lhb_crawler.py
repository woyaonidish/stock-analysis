#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
龙虎榜数据爬虫 - 使用 httpx 支持同步和异步请求
"""

import asyncio
import pandas as pd
from typing import Optional

from app.crawler.base_crawler import BaseCrawler


class LhbCrawler(BaseCrawler):
    """龙虎榜数据爬虫"""
    
    SYMBOL_MAP = {
        "近一月": "01",
        "近三月": "02",
        "近六月": "03",
        "近一年": "04",
    }
    
    # ==================== 同步方法 ====================
    
    def get_lhb_detail(
        self, start_date: str = "20230403", end_date: str = "20230417"
    ) -> pd.DataFrame:
        """获取龙虎榜详情"""
        start_date_fmt = "-".join([start_date[:4], start_date[4:6], start_date[6:]])
        end_date_fmt = "-".join([end_date[:4], end_date[4:6], end_date[6:]])
        
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "SECURITY_CODE,TRADE_DATE",
            "sortTypes": "1,-1",
            "pageSize": "5000",
            "pageNumber": "1",
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECUCODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLAIN,CLOSE_PRICE,CHANGE_RATE,BILLBOARD_NET_AMT,BILLBOARD_BUY_AMT,BILLBOARD_SELL_AMT,BILLBOARD_DEAL_AMT,ACCUM_AMOUNT,DEAL_NET_RATIO,DEAL_AMOUNT_RATIO,TURNOVERRATE,FREE_MARKET_CAP,EXPLANATION,D1_CLOSE_ADJCHRATE,D2_CLOSE_ADJCHRATE,D5_CLOSE_ADJCHRATE,D10_CLOSE_ADJCHRATE,SECURITY_TYPE_CODE",
            "source": "WEB",
            "client": "WEB",
            "filter": f"(TRADE_DATE<='{end_date_fmt}')(TRADE_DATE>='{start_date_fmt}')",
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        total_page_num = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        
        for page in range(1, total_page_num + 1):
            import time
            import random
            time.sleep(random.uniform(1, 1.5))
            params["pageNumber"] = page
            r = self.request(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = pd.concat([big_df, temp_df], ignore_index=True)
        
        if big_df.empty:
            return pd.DataFrame()
        
        big_df.reset_index(inplace=True)
        big_df["index"] = big_df.index + 1
        big_df.rename(
            columns={
                "index": "序号",
                "SECURITY_CODE": "代码",
                "SECUCODE": "-",
                "SECURITY_NAME_ABBR": "名称",
                "TRADE_DATE": "上榜日",
                "EXPLAIN": "解读",
                "CLOSE_PRICE": "收盘价",
                "CHANGE_RATE": "涨跌幅",
                "BILLBOARD_NET_AMT": "龙虎榜净买额",
                "BILLBOARD_BUY_AMT": "龙虎榜买入额",
                "BILLBOARD_SELL_AMT": "龙虎榜卖出额",
                "BILLBOARD_DEAL_AMT": "龙虎榜成交额",
                "ACCUM_AMOUNT": "市场总成交额",
                "DEAL_NET_RATIO": "净买额占总成交比",
                "DEAL_AMOUNT_RATIO": "成交额占总成交比",
                "TURNOVERRATE": "换手率",
                "FREE_MARKET_CAP": "流通市值",
                "EXPLANATION": "上榜原因",
                "D1_CLOSE_ADJCHRATE": "上榜后1日",
                "D2_CLOSE_ADJCHRATE": "上榜后2日",
                "D5_CLOSE_ADJCHRATE": "上榜后5日",
                "D10_CLOSE_ADJCHRATE": "上榜后10日",
            },
            inplace=True,
        )
        
        big_df = big_df[[
            "代码", "名称", "上榜日", "解读", "收盘价", "涨跌幅",
            "龙虎榜净买额", "龙虎榜买入额", "龙虎榜卖出额", "龙虎榜成交额",
            "市场总成交额", "净买额占总成交比", "成交额占总成交比",
            "换手率", "流通市值", "上榜原因",
            "上榜后1日", "上榜后2日", "上榜后5日", "上榜后10日",
        ]]
        
        big_df["上榜日"] = pd.to_datetime(big_df["上榜日"]).dt.date
        
        numeric_cols = [
            "收盘价", "涨跌幅", "龙虎榜净买额", "龙虎榜买入额", "龙虎榜卖出额",
            "龙虎榜成交额", "市场总成交额", "净买额占总成交比", "成交额占总成交比",
            "换手率", "流通市值", "上榜后1日", "上榜后2日", "上榜后5日", "上榜后10日"
        ]
        for col in numeric_cols:
            big_df[col] = pd.to_numeric(big_df[col], errors="coerce")
        
        return big_df
    
    def get_stock_statistic(self, symbol: str = "近一月") -> pd.DataFrame:
        """获取个股上榜统计"""
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "BILLBOARD_TIMES,LATEST_TDATE,SECURITY_CODE",
            "sortTypes": "-1,-1,1",
            "pageSize": "500",
            "pageNumber": "1",
            "reportName": "RPT_BILLBOARD_TRADEALL",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "filter": f'(STATISTICS_CYCLE="{self.SYMBOL_MAP[symbol]}")',
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["result"]["data"])
        
        if temp_df.empty:
            return pd.DataFrame()
        
        temp_df.reset_index(inplace=True)
        temp_df["index"] = temp_df.index + 1
        temp_df.columns = [
            "序号", "-", "代码", "最近上榜日", "名称",
            "近1个月涨跌幅", "近3个月涨跌幅", "近6个月涨跌幅", "近1年涨跌幅",
            "涨跌幅", "收盘价", "-", "龙虎榜总成交额", "龙虎榜净买额",
            "-", "-", "机构买入净额", "上榜次数", "龙虎榜买入额",
            "龙虎榜卖出额", "机构买入总额", "机构卖出总额",
            "买方机构次数", "卖方机构次数", "-",
        ]
        
        temp_df = temp_df[[
            "序号", "代码", "名称", "最近上榜日", "收盘价", "涨跌幅",
            "上榜次数", "龙虎榜净买额", "龙虎榜买入额", "龙虎榜卖出额",
            "龙虎榜总成交额", "买方机构次数", "卖方机构次数",
            "机构买入净额", "机构买入总额", "机构卖出总额",
            "近1个月涨跌幅", "近3个月涨跌幅", "近6个月涨跌幅", "近1年涨跌幅",
        ]]
        
        temp_df["最近上榜日"] = pd.to_datetime(temp_df["最近上榜日"]).dt.date
        return temp_df
    
    def get_institution_statistic(
        self, start_date: str = "20220906", end_date: str = "20220906"
    ) -> pd.DataFrame:
        """获取机构买卖每日统计"""
        start_date_fmt = "-".join([start_date[:4], start_date[4:6], start_date[6:]])
        end_date_fmt = "-".join([end_date[:4], end_date[4:6], end_date[6:]])
        
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "NET_BUY_AMT,TRADE_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1,1",
            "pageSize": "5000",
            "pageNumber": "1",
            "reportName": "RPT_ORGANIZATION_TRADE_DETAILS",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "filter": f"(TRADE_DATE>='{start_date_fmt}')(TRADE_DATE<='{end_date_fmt}')",
        }
        
        r = self.request(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["result"]["data"])
        
        if temp_df.empty:
            return pd.DataFrame()
        
        temp_df.reset_index(inplace=True)
        temp_df["index"] = temp_df.index + 1
        temp_df.columns = [
            "序号", "-", "名称", "代码", "上榜日期", "收盘价", "涨跌幅",
            "买方机构数", "卖方机构数", "机构买入总额", "机构卖出总额",
            "机构买入净额", "市场总成交额", "机构净买额占总成交额比",
            "换手率", "流通市值", "上榜原因", "-", "-", "-", "-", "-", "-", "-", "-", "-",
        ]
        
        temp_df = temp_df[[
            "序号", "代码", "名称", "收盘价", "涨跌幅", "买方机构数",
            "卖方机构数", "机构买入总额", "机构卖出总额", "机构买入净额",
            "市场总成交额", "机构净买额占总成交额比", "换手率", "流通市值", "上榜原因",
        ]]
        
        numeric_cols = [
            "收盘价", "涨跌幅", "买方机构数", "卖方机构数", "机构买入总额",
            "机构卖出总额", "机构买入净额", "市场总成交额",
            "机构净买额占总成交额比", "换手率", "流通市值"
        ]
        for col in numeric_cols:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        
        return temp_df
    
    # ==================== 异步方法 ====================
    
    async def async_get_lhb_detail(
        self, start_date: str = "20230403", end_date: str = "20230417"
    ) -> pd.DataFrame:
        """异步获取龙虎榜详情"""
        start_date_fmt = "-".join([start_date[:4], start_date[4:6], start_date[6:]])
        end_date_fmt = "-".join([end_date[:4], end_date[4:6], end_date[6:]])
        
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "SECURITY_CODE,TRADE_DATE",
            "sortTypes": "1,-1",
            "pageSize": "5000",
            "pageNumber": "1",
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECUCODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLAIN,CLOSE_PRICE,CHANGE_RATE,BILLBOARD_NET_AMT,BILLBOARD_BUY_AMT,BILLBOARD_SELL_AMT,BILLBOARD_DEAL_AMT,ACCUM_AMOUNT,DEAL_NET_RATIO,DEAL_AMOUNT_RATIO,TURNOVERRATE,FREE_MARKET_CAP,EXPLANATION,D1_CLOSE_ADJCHRATE,D2_CLOSE_ADJCHRATE,D5_CLOSE_ADJCHRATE,D10_CLOSE_ADJCHRATE,SECURITY_TYPE_CODE",
            "source": "WEB",
            "client": "WEB",
            "filter": f"(TRADE_DATE<='{end_date_fmt}')(TRADE_DATE>='{start_date_fmt}')",
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        total_page_num = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        
        # 异步请求剩余页面
        if total_page_num > 1:
            urls = []
            params_list = []
            for page in range(1, total_page_num + 1):
                page_params = params.copy()
                page_params["pageNumber"] = page
                urls.append(url)
                params_list.append(page_params)
            
            responses = await self.async_batch_request(urls, params_list, delay=0.3)
            
            for response in responses:
                if response:
                    temp_df = pd.DataFrame(response.json()["result"]["data"])
                    big_df = pd.concat([big_df, temp_df], ignore_index=True)
        else:
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = temp_df
        
        if big_df.empty:
            return pd.DataFrame()
        
        big_df.reset_index(inplace=True)
        big_df["index"] = big_df.index + 1
        big_df.rename(
            columns={
                "index": "序号",
                "SECURITY_CODE": "代码",
                "SECUCODE": "-",
                "SECURITY_NAME_ABBR": "名称",
                "TRADE_DATE": "上榜日",
                "EXPLAIN": "解读",
                "CLOSE_PRICE": "收盘价",
                "CHANGE_RATE": "涨跌幅",
                "BILLBOARD_NET_AMT": "龙虎榜净买额",
                "BILLBOARD_BUY_AMT": "龙虎榜买入额",
                "BILLBOARD_SELL_AMT": "龙虎榜卖出额",
                "BILLBOARD_DEAL_AMT": "龙虎榜成交额",
                "ACCUM_AMOUNT": "市场总成交额",
                "DEAL_NET_RATIO": "净买额占总成交比",
                "DEAL_AMOUNT_RATIO": "成交额占总成交比",
                "TURNOVERRATE": "换手率",
                "FREE_MARKET_CAP": "流通市值",
                "EXPLANATION": "上榜原因",
                "D1_CLOSE_ADJCHRATE": "上榜后1日",
                "D2_CLOSE_ADJCHRATE": "上榜后2日",
                "D5_CLOSE_ADJCHRATE": "上榜后5日",
                "D10_CLOSE_ADJCHRATE": "上榜后10日",
            },
            inplace=True,
        )
        
        big_df = big_df[[
            "代码", "名称", "上榜日", "解读", "收盘价", "涨跌幅",
            "龙虎榜净买额", "龙虎榜买入额", "龙虎榜卖出额", "龙虎榜成交额",
            "市场总成交额", "净买额占总成交比", "成交额占总成交比",
            "换手率", "流通市值", "上榜原因",
            "上榜后1日", "上榜后2日", "上榜后5日", "上榜后10日",
        ]]
        
        big_df["上榜日"] = pd.to_datetime(big_df["上榜日"]).dt.date
        
        numeric_cols = [
            "收盘价", "涨跌幅", "龙虎榜净买额", "龙虎榜买入额", "龙虎榜卖出额",
            "龙虎榜成交额", "市场总成交额", "净买额占总成交比", "成交额占总成交比",
            "换手率", "流通市值", "上榜后1日", "上榜后2日", "上榜后5日", "上榜后10日"
        ]
        for col in numeric_cols:
            big_df[col] = pd.to_numeric(big_df[col], errors="coerce")
        
        return big_df
    
    async def async_get_stock_statistic(self, symbol: str = "近一月") -> pd.DataFrame:
        """异步获取个股上榜统计"""
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "BILLBOARD_TIMES,LATEST_TDATE,SECURITY_CODE",
            "sortTypes": "-1,-1,1",
            "pageSize": "500",
            "pageNumber": "1",
            "reportName": "RPT_BILLBOARD_TRADEALL",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "filter": f'(STATISTICS_CYCLE="{self.SYMBOL_MAP[symbol]}")',
        }
        
        r = await self.async_request(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["result"]["data"])
        
        if temp_df.empty:
            return pd.DataFrame()
        
        temp_df.reset_index(inplace=True)
        temp_df["index"] = temp_df.index + 1
        temp_df.columns = [
            "序号", "-", "代码", "最近上榜日", "名称",
            "近1个月涨跌幅", "近3个月涨跌幅", "近6个月涨跌幅", "近1年涨跌幅",
            "涨跌幅", "收盘价", "-", "龙虎榜总成交额", "龙虎榜净买额",
            "-", "-", "机构买入净额", "上榜次数", "龙虎榜买入额",
            "龙虎榜卖出额", "机构买入总额", "机构卖出总额",
            "买方机构次数", "卖方机构次数", "-",
        ]
        
        temp_df = temp_df[[
            "序号", "代码", "名称", "最近上榜日", "收盘价", "涨跌幅",
            "上榜次数", "龙虎榜净买额", "龙虎榜买入额", "龙虎榜卖出额",
            "龙虎榜总成交额", "买方机构次数", "卖方机构次数",
            "机构买入净额", "机构买入总额", "机构卖出总额",
            "近1个月涨跌幅", "近3个月涨跌幅", "近6个月涨跌幅", "近1年涨跌幅",
        ]]
        
        temp_df["最近上榜日"] = pd.to_datetime(temp_df["最近上榜日"]).dt.date
        return temp_df
    
    def crawl(self, start_date: str = None, end_date: str = None, **kwargs) -> pd.DataFrame:
        """实现爬取方法"""
        if start_date and end_date:
            return self.get_lhb_detail(start_date, end_date)
        return self.get_stock_statistic()
    
    async def async_crawl(self, start_date: str = None, end_date: str = None, **kwargs) -> pd.DataFrame:
        """异步爬取方法"""
        if start_date and end_date:
            return await self.async_get_lhb_detail(start_date, end_date)
        return await self.async_get_stock_statistic()