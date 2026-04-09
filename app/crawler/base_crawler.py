#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫基类 - 使用 httpx 支持同步和异步请求
"""

import time
import random
import asyncio
from abc import ABC, abstractmethod
import httpx
from typing import Optional, Dict, List
import os

from app.config.config import settings
from app.utils.logger import warning, error


class BaseCrawler(ABC):
    """爬虫基类 - 支持同步和异步请求"""
    
    def __init__(self):
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
        self.proxies = self._get_proxies()
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
    
    def _get_sync_client(self) -> httpx.Client:
        """获取同步客户端"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                headers=self._headers,
                timeout=httpx.Timeout(30.0, connect=10.0),
                follow_redirects=True,
            )
        return self._sync_client
    
    def _get_async_client(self) -> httpx.AsyncClient:
        """获取异步客户端"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                headers=self._headers,
                timeout=httpx.Timeout(30.0, connect=10.0),
                follow_redirects=True,
            )
        return self._async_client
    
    def _get_proxies(self) -> Optional[Dict]:
        """获取代理配置"""
        if not settings.PROXY_ENABLED:
            return None
        
        proxy_file = settings.PROXY_FILE
        if not os.path.exists(proxy_file):
            return None
        
        with open(proxy_file, 'r') as f:
            lines = f.readlines()
            if not lines:
                return None
            # 随机选择一个代理
            proxy = random.choice(lines).strip()
            return {
                'http://': f'http://{proxy}',
                'https://': f'http://{proxy}'
            }
    
    def close(self):
        """关闭同步客户端"""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
    
    async def async_close(self):
        """关闭异步客户端"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
    
    # ==================== 同步请求方法 ====================
    
    def request(self, url: str, params: dict = None, retry: int = 3, timeout: int = 10) -> Optional[httpx.Response]:
        """
        发送同步HTTP请求
        
        Args:
            url: 请求URL
            params: 请求参数
            retry: 重试次数
            timeout: 超时时间
            
        Returns:
            响应对象
        """
        client = self._get_sync_client()
        
        for i in range(retry):
            try:
                response = client.get(
                    url,
                    params=params,
                    timeout=timeout
                )
                response.raise_for_status()
                return response
            except httpx.HTTPError as e:
                warning(f"请求错误: {e}, 第 {i + 1}/{retry} 次重试")
                if i < retry - 1:
                    time.sleep(random.uniform(1, 3))
                else:
                    raise
        return None
    
    def request_with_delay(self, url: str, params: dict = None, delay: float = 1.0) -> Optional[httpx.Response]:
        """
        带延迟的同步请求
        
        Args:
            url: 请求URL
            params: 请求参数
            delay: 延迟时间
            
        Returns:
            响应对象
        """
        time.sleep(random.uniform(delay * 0.8, delay * 1.2))
        return self.request(url, params)
    
    # ==================== 异步请求方法 ====================
    
    async def async_request(self, url: str, params: dict = None, retry: int = 3, timeout: int = 10) -> Optional[httpx.Response]:
        """
        发送异步HTTP请求
        
        Args:
            url: 请求URL
            params: 请求参数
            retry: 重试次数
            timeout: 超时时间
            
        Returns:
            响应对象
        """
        client = self._get_async_client()
        
        for i in range(retry):
            try:
                response = await client.get(
                    url,
                    params=params,
                    timeout=timeout
                )
                response.raise_for_status()
                return response
            except httpx.HTTPError as e:
                warning(f"请求错误: {e}, 第 {i + 1}/{retry} 次重试")
                if i < retry - 1:
                    await asyncio.sleep(random.uniform(1, 3))
                else:
                    raise
        return None
    
    async def async_request_with_delay(self, url: str, params: dict = None, delay: float = 1.0) -> Optional[httpx.Response]:
        """
        带延迟的异步请求
        
        Args:
            url: 请求URL
            params: 请求参数
            delay: 延迟时间
            
        Returns:
            响应对象
        """
        await asyncio.sleep(random.uniform(delay * 0.8, delay * 1.2))
        return await self.async_request(url, params)
    
    # ==================== 批量异步请求 ====================
    
    async def async_batch_request(
        self, 
        urls: List[str], 
        params_list: List[dict] = None,
        delay: float = 0.5
    ) -> List[httpx.Response]:
        """
        批量异步请求
        
        Args:
            urls: URL列表
            params_list: 参数列表
            delay: 每个请求之间的延迟
            
        Returns:
            响应列表
        """
        if params_list is None:
            params_list = [None] * len(urls)
        
        responses = []
        for url, params in zip(urls, params_list):
            await asyncio.sleep(delay)
            try:
                response = await self.async_request(url, params)
                responses.append(response)
            except Exception as e:
                error(f"批量请求失败: {url}, {e}")
                responses.append(None)
        
        return responses
    
    @abstractmethod
    def crawl(self, *args, **kwargs):
        """同步爬取数据（子类实现）"""
        pass
    
    async def async_crawl(self, *args, **kwargs):
        """异步爬取数据（子类可选实现）"""
        # 默认调用同步方法，子类可覆盖
        return self.crawl(*args, **kwargs)