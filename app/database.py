#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库连接和会话管理
"""

import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config.config import settings, BASE_DIR
from app.utils.logger import info, warning, error

# 创建SQLite数据库引擎
# SQLite不需要连接池配置，使用NullPool或默认配置
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    connect_args={"check_same_thread": False}  # SQLite需要此配置以支持多线程
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# 创建基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建数据库文件和所有表
    
    - 自动创建数据库目录（如果不存在）
    - 自动创建所有表（如果不存在）
    """
    # 确保数据库目录存在
    db_path = BASE_DIR / settings.DB_FILE
    db_dir = db_path.parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)
        info(f"创建数据库目录: {db_dir}")
    
    # 导入所有实体类，确保它们注册到Base.metadata
    # 此处使用局部导入以避免循环依赖（entity模块依赖database模块的Base）
    from app.entity import (
        StockSpot, StockAttention, StockIndicator, StockPattern,
        StockStrategyBase, StockStrategyEnter, StockStrategyKeepIncreasing,
        StockStrategyParkingApron, StockStrategyBacktraceMA250,
        StockStrategyBreakthroughPlatform, StockStrategyLowBacktraceIncrease,
        StockStrategyTurtleTrade, StockStrategyHighTightFlag,
        StockStrategyClimaxLimitdown, StockStrategyLowATR, STRATEGY_TABLES,
        StockSelection, StockBonus, StockLhb, StockBlocktrade,
        StockBacktestData, StockHistData
    )
    
    # 检查数据库文件是否存在
    db_exists = db_path.exists()
    
    # 创建所有表（如果不存在）
    Base.metadata.create_all(bind=engine)
    
    # 输出初始化信息
    if not db_exists:
        info(f"创建数据库文件: {db_path}")
    else:
        info(f"数据库文件存在: {db_path}")
    
    # 获取已创建的表数量
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    info(f"数据库初始化完成，共有 {len(tables)} 张表")
    
    return tables


def get_connection():
    """获取原始数据库连接（用于执行原生SQL）"""
    return engine.connect()


def get_tables() -> list:
    """获取所有表名"""
    inspector = inspect(engine)
    return inspector.get_table_names()


def table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


# SQLite外键支持
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """启用SQLite外键约束"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()