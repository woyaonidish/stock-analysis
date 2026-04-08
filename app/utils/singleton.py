#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单例模式装饰器
"""


def singleton(cls):
    """
    单例装饰器
    
    使用方法:
        @singleton
        class MyClass:
            pass
    """
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance
