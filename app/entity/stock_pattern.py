#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票K线形态识别实体类
"""

from datetime import date
from sqlalchemy import Column, String, Date, SmallInteger
from app.database import Base


class StockPattern(Base):
    """股票K线形态识别"""
    __tablename__ = 'cn_stock_pattern'
    
    date = Column(Date, primary_key=True, comment='日期')
    code = Column(String(6), primary_key=True, comment='代码')
    
    # 61种K线形态
    tow_crows = Column(SmallInteger, comment='两只乌鸦')
    upside_gap_two_crows = Column(SmallInteger, comment='向上跳空的两只乌鸦')
    three_black_crows = Column(SmallInteger, comment='三只乌鸦')
    identical_three_crows = Column(SmallInteger, comment='三胞胎乌鸦')
    three_line_strike = Column(SmallInteger, comment='三线打击')
    dark_cloud_cover = Column(SmallInteger, comment='乌云压顶')
    evening_doji_star = Column(SmallInteger, comment='十字暮星')
    doji_star = Column(SmallInteger, comment='十字星')
    hanging_man = Column(SmallInteger, comment='上吊线')
    hikkake_pattern = Column(SmallInteger, comment='陷阱')
    modified_hikkake_pattern = Column(SmallInteger, comment='修正陷阱')
    in_neck_pattern = Column(SmallInteger, comment='颈内线')
    on_neck_pattern = Column(SmallInteger, comment='颈上线')
    thrusting_pattern = Column(SmallInteger, comment='插入')
    shooting_star = Column(SmallInteger, comment='射击之星')
    stalled_pattern = Column(SmallInteger, comment='停顿形态')
    advance_block = Column(SmallInteger, comment='大敌当前')
    high_wave_candle = Column(SmallInteger, comment='风高浪大线')
    engulfing_pattern = Column(SmallInteger, comment='吞噬模式')
    abandoned_baby = Column(SmallInteger, comment='弃婴')
    closing_marubozu = Column(SmallInteger, comment='收盘缺影线')
    doji = Column(SmallInteger, comment='十字')
    up_down_gap = Column(SmallInteger, comment='向上/下跳空并列阳线')
    long_legged_doji = Column(SmallInteger, comment='长脚十字')
    rickshaw_man = Column(SmallInteger, comment='黄包车夫')
    marubozu = Column(SmallInteger, comment='光头光脚/缺影线')
    three_inside_up_down = Column(SmallInteger, comment='三内部上涨和下跌')
    three_outside_up_down = Column(SmallInteger, comment='三外部上涨和下跌')
    three_stars_in_the_south = Column(SmallInteger, comment='南方三星')
    three_white_soldiers = Column(SmallInteger, comment='三个白兵')
    belt_hold = Column(SmallInteger, comment='捉腰带线')
    breakaway = Column(SmallInteger, comment='脱离')
    concealing_baby_swallow = Column(SmallInteger, comment='藏婴吞没')
    counterattack = Column(SmallInteger, comment='反击线')
    dragonfly_doji = Column(SmallInteger, comment='蜻蜓十字/T形十字')
    evening_star = Column(SmallInteger, comment='暮星')
    gravestone_doji = Column(SmallInteger, comment='墓碑十字/倒T十字')
    hammer = Column(SmallInteger, comment='锤头')
    harami_pattern = Column(SmallInteger, comment='母子线')
    harami_cross_pattern = Column(SmallInteger, comment='十字孕线')
    homing_pigeon = Column(SmallInteger, comment='家鸽')
    inverted_hammer = Column(SmallInteger, comment='倒锤头')
    kicking = Column(SmallInteger, comment='反冲形态')
    kicking_bull_bear = Column(SmallInteger, comment='由较长缺影线决定的反冲形态')
    ladder_bottom = Column(SmallInteger, comment='梯底')
    long_line_candle = Column(SmallInteger, comment='长蜡烛')
    matching_low = Column(SmallInteger, comment='相同低价')
    mat_hold = Column(SmallInteger, comment='铺垫')
    morning_doji_star = Column(SmallInteger, comment='十字晨星')
    morning_star = Column(SmallInteger, comment='晨星')
    piercing_pattern = Column(SmallInteger, comment='刺透形态')
    rising_falling_three = Column(SmallInteger, comment='上升/下降三法')
    separating_lines = Column(SmallInteger, comment='分离线')
    short_line_candle = Column(SmallInteger, comment='短蜡烛')
    spinning_top = Column(SmallInteger, comment='纺锤')
    stick_sandwich = Column(SmallInteger, comment='条形三明治')
    takuri = Column(SmallInteger, comment='探水竿')
    tasuki_gap = Column(SmallInteger, comment='跳空并列阴阳线')
    tristar_pattern = Column(SmallInteger, comment='三星')
    unique_3_river = Column(SmallInteger, comment='奇特三河床')
    upside_downside_gap = Column(SmallInteger, comment='上升/下降跳空三法')
