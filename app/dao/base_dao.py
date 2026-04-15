#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAO层基类
封装通用的CRUD操作
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

T = TypeVar('T')


class BaseDAO(Generic[T]):
    """
    DAO基类
    封装通用的数据库操作方法
    """
    
    def __init__(self, model: Type[T], session: Session):
        """
        初始化DAO
        
        Args:
            model: 实体类
            session: 数据库会话
        """
        self.model = model
        self.session = session
    
    def find_by_id(self, **kwargs) -> Optional[T]:
        """
        根据主键查询单个实体
        
        Args:
            **kwargs: 主键字段和值
            
        Returns:
            实体对象或None
        """
        return self.session.query(self.model).filter_by(**kwargs).first()
    
    def find_all(self) -> List[T]:
        """
        查询所有实体
        
        Returns:
            实体列表
        """
        return self.session.query(self.model).all()
    
    def find_by_date(self, query_date: date) -> List[T]:
        """
        根据日期查询
        
        Args:
            query_date: 查询日期
            
        Returns:
            实体列表
        """
        return self.session.query(self.model).filter_by(date=query_date).all()
    
    def find_by_code(self, code: str, query_date: date = None) -> List[T]:
        """
        根据代码查询
        
        Args:
            code: 股票代码
            query_date: 查询日期（可选）
            
        Returns:
            实体列表
        """
        query = self.session.query(self.model).filter_by(code=code)
        if query_date:
            query = query.filter_by(date=query_date)
        return query.all()
    
    def find_by_condition(self, **kwargs) -> List[T]:
        """
        根据条件查询
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            实体列表
        """
        return self.session.query(self.model).filter_by(**kwargs).all()
    
    def find_latest_date(self) -> Optional[date]:
        """
        获取最新日期
        
        Returns:
            最新日期或None
        """
        result = self.session.query(self.model).order_by(self.model.date.desc()).first()
        return result.date if result else None
    
    def save(self, entity: T) -> T:
        """
        保存实体
        
        Args:
            entity: 实体对象
            
        Returns:
            保存后的实体
        """
        self.session.add(entity)
        self.session.commit()
        return entity
    
    def save_all(self, entities: List[T]) -> List[T]:
        """
        批量保存实体
        
        Args:
            entities: 实体列表
            
        Returns:
            保存后的实体列表
        """
        self.session.add_all(entities)
        self.session.commit()
        return entities
    
    def save_or_ignore(self, entities: List[T]) -> int:
        """
        批量保存实体，忽略重复数据
        
        使用 session.bulk_save_objects 并在出错时 rollback
        
        Args:
            entities: 实体列表
            
        Returns:
            成功保存的数量
        """
        try:
            self.session.bulk_save_objects(entities)
            self.session.commit()
            return len(entities)
        except Exception as e:
            self.session.rollback()
            raise e
    
    def upsert_all(self, entities: List[T], key_fields: List[str] = None) -> int:
        """
        批量插入或更新（upsert）
        
        对于已存在的数据先删除再插入
        
        Args:
            entities: 实体列表
            key_fields: 主键字段列表，默认 ['date', 'code']
            
        Returns:
            处理的记录数
        """
        if not entities:
            return 0
        
        if key_fields is None:
            key_fields = ['date', 'code']
        
        try:
            # 按主键分组收集值
            key_value_sets = {}
            for entity in entities:
                # 提取第一个主键字段的值（通常是 date）
                if len(key_fields) >= 1 and hasattr(entity, key_fields[0]):
                    first_key = key_fields[0]
                    first_val = getattr(entity, first_key)
                    if first_val not in key_value_sets:
                        key_value_sets[first_val] = []
                    key_value_sets[first_val].append(entity)
            
            # 批量删除：按第一个主键值批量删除
            for first_val in key_value_sets.keys():
                self.session.query(self.model).filter(
                    getattr(self.model, key_fields[0]) == first_val
                ).delete(synchronize_session=False)
            
            # 批量插入新数据
            self.session.bulk_save_objects(entities)
            self.session.commit()
            return len(entities)
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update(self, entity: T) -> T:
        """
        更新实体
        
        Args:
            entity: 实体对象
            
        Returns:
            更新后的实体
        """
        self.session.commit()
        return entity
    
    def delete(self, entity: T) -> None:
        """
        删除实体
        
        Args:
            entity: 实体对象
        """
        self.session.delete(entity)
        self.session.commit()
    
    def delete_by_date(self, query_date: date) -> int:
        """
        根据日期删除
        
        Args:
            query_date: 日期
            
        Returns:
            删除的记录数
        """
        count = self.session.query(self.model).filter_by(date=query_date).delete()
        self.session.commit()
        return count
    
    def delete_by_date_and_code(self, query_date: date, code: str) -> int:
        """
        根据日期和代码删除
        
        Args:
            query_date: 日期
            code: 股票代码
            
        Returns:
            删除的记录数
        """
        count = self.session.query(self.model).filter(
            and_(self.model.date == query_date, self.model.code == code)
        ).delete()
        self.session.commit()
        return count
    
    def count(self, **kwargs) -> int:
        """
        统计数量
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            记录数
        """
        return self.session.query(self.model).filter_by(**kwargs).count()
    
    def exists(self, **kwargs) -> bool:
        """
        判断是否存在
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            是否存在
        """
        return self.session.query(self.model).filter_by(**kwargs).count() > 0
    
    def bulk_insert(self, entities: List[T]) -> None:
        """
        批量插入（高效方式）
        
        Args:
            entities: 实体列表
        """
        self.session.bulk_save_objects(entities)
        self.session.commit()
    
    def execute_raw_sql(self, sql: str, params: dict = None) -> List[dict]:
        """
        执行原生SQL查询
        
        Args:
            sql: SQL语句
            params: 参数
            
        Returns:
            查询结果列表
        """
        result = self.session.execute(sql, params or {})
        return [dict(row) for row in result]
