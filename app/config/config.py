#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用配置文件
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "InStock API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 9988
    
    # SQLite数据库配置
    DB_FILE: str = "data/instock.db"
    DB_ECHO: bool = False  # 是否打印SQL语句
    
    # 东方财富Cookie
    EAST_MONEY_COOKIE: Optional[str] = None
    
    # 代理配置
    PROXY_ENABLED: bool = False
    PROXY_FILE: str = "config/proxy.txt"
    
    # 交易配置
    TRADE_ENABLED: bool = False
    TRADE_CONFIG_FILE: str = "config/trade_client.json"
    
    # 定时任务配置
    SCHEDULER_ENABLED: bool = True
    
    @property
    def DATABASE_URL(self) -> str:
        """获取数据库连接URL"""
        db_path = BASE_DIR / self.DB_FILE
        # 确保数据目录存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 便捷访问
settings = get_settings()
