#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
财务数据服务
"""

from datetime import date
from typing import List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.dao.financial_dao import FinancialDAO
from app.entity.stock_financial import StockFinancial
from app.crawler.tdx_fetcher import TdxFetcher
from app.database import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FinancialService:
    """财务数据服务"""
    
    # MOOTDX 财务数据字段映射（中文 -> 实体字段）
    FIELD_MAPPING = {
        '基本每股收益': 'eps',
        '扣除非经常性损益每股收益': 'eps_deducted',
        '每股净资产': 'bvps',
        '每股经营性现金流(元)': 'cfps',
        '净资产收益率': 'roe',
        '加权净资产收益率(每股指标)': 'roe_weighted',
        '销售净利率(%)': 'net_profit_margin',
        '销售毛利率(%)(非金融类指标)': 'gross_profit_margin',
        '营业收入增长率(%)': 'revenue_growth',
        '净利润增长率(%)': 'net_profit_growth',
        '资产负债率(%)': 'debt_ratio',
        '流动比率(非金融类指标)': 'current_ratio',
        '速动比率(非金融类指标)': 'quick_ratio',
        '营业收入': 'revenue',
        '营业利润': 'operating_profit',
        '净利润': 'net_profit',
        '归属于母公司所有者的净利润': 'net_profit_parent',
        '扣除非经常性损益后的净利润': 'net_profit_deducted',
        '资产总计': 'total_assets',
        '负债合计': 'total_liability',
        '所有者权益（或股东权益）合计': 'net_assets',
        '经营活动产生的现金流量净额': 'operating_cf',
        '投资活动产生的现金流量净额': 'investing_cf',
        '筹资活动产生的现金流量净额': 'financing_cf',
        '总股本': 'total_shares',
        '已上市流通A股': 'float_shares_a',
    }
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.financial_dao = FinancialDAO(self.session)
        self.fetcher = TdxFetcher()
    
    def get_financial(self, code: str, report_date: date = None) -> Optional[StockFinancial]:
        """
        获取股票财务数据
        
        Args:
            code: 股票代码
            report_date: 报告期
            
        Returns:
            财务数据实体
        """
        return self.financial_dao.find_by_code(code, report_date)
    
    def get_financial_history(self, code: str, limit: int = 8) -> List[StockFinancial]:
        """
        获取股票历史财务数据
        
        Args:
            code: 股票代码
            limit: 返回数量
            
        Returns:
            财务数据列表
        """
        return self.financial_dao.find_by_code_history(code, limit)
    
    def save_financial_data(self, data: pd.DataFrame) -> int:
        """
        保存财务数据
        
        Args:
            data: 财务数据DataFrame
            
        Returns:
            保存记录数
        """
        if data is None or data.empty:
            return 0
        
        # 转换为实体列表
        entities = []
        for idx, row in data.iterrows():
            # idx 是股票代码（code）
            code = str(idx).zfill(6)
            report_date_str = str(row.get('report_date', ''))
            
            # 解析报告期日期
            try:
                report_date_val = date(
                    int(report_date_str[:4]),
                    int(report_date_str[4:6]),
                    int(report_date_str[6:8])
                )
            except:
                logger.warning(f"无法解析报告期: {report_date_str}")
                continue
            
            # 创建实体
            entity = StockFinancial(
                report_date=report_date_val,
                code=code,
            )
            
            # 映射字段
            for cn_field, en_field in self.FIELD_MAPPING.items():
                if cn_field in row:
                    value = row.get(cn_field)
                    if value is not None and pd.notna(value):
                        setattr(entity, en_field, float(value) if isinstance(value, (int, float)) else value)
            
            entities.append(entity)
        
        # 批量保存
        if entities:
            self.financial_dao.save_all(entities)
            logger.info(f"保存财务数据成功，共 {len(entities)} 条")
        
        return len(entities)
    
    async def fetch_and_save_financial_data(self, filepath: str) -> int:
        """
        异步解析并保存财务数据
        
        Args:
            filepath: 财务数据文件路径
            
        Returns:
            保存记录数
        """
        try:
            # 解析财务数据文件
            data = await self.fetcher.get_financial_data(filepath)
            if data is None or data.empty:
                logger.warning(f"解析财务数据为空: {filepath}")
                return 0
            
            # 保存数据
            count = self.save_financial_data(data)
            logger.info(f"保存财务数据成功，共 {count} 条")
            return count
            
        except Exception as e:
            logger.error(f"解析并保存财务数据失败: {e}")
            return 0
    
    def get_latest_report_date(self) -> Optional[date]:
        """
        获取最新报告期
        
        Returns:
            最新报告期日期
        """
        return self.financial_dao.find_latest_report_date()
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()