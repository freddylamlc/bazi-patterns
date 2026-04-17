"""
四柱計算模塊 - 計算年柱、月柱、日柱、時柱
"""

import sxtwl
from bazi.core.constants import GAN, ZHI


def calculate_year_pillar(lunar_date) -> str:
    """
    計算年柱

    Args:
        lunar_date: sxtwl 農曆日期對象

    Returns:
        年柱（如 "甲子"）
    """
    year_gz = lunar_date.getYearGZ()
    return GAN[year_gz.tg] + ZHI[year_gz.dz]


def calculate_month_pillar(lunar_date) -> str:
    """
    計算月柱

    Args:
        lunar_date: sxtwl 農曆日期對象

    Returns:
        月柱（如 "丙寅"）
    """
    month_gz = lunar_date.getMonthGZ()
    return GAN[month_gz.tg] + ZHI[month_gz.dz]


def calculate_day_pillar(lunar_date) -> str:
    """
    計算日柱

    Args:
        lunar_date: sxtwl 農曆日期對象

    Returns:
        日柱（如 "己未"）
    """
    day_gz = lunar_date.getDayGZ()
    return GAN[day_gz.tg] + ZHI[day_gz.dz]


def calculate_hour_pillar(day_gan_index: int, solar_hour: int) -> str:
    """
    計算時柱

    Args:
        day_gan_index: 日天干索引（0-9）
        solar_hour: 真太陽時的小時（0-23）

    Returns:
        時柱（如 "庚午"）
    """
    hour_gz = sxtwl.getShiGz(day_gan_index, solar_hour)
    return GAN[hour_gz.tg] + ZHI[hour_gz.dz]


def calculate_pillars(lunar_date, solar_time) -> tuple[str, str, str, str]:
    """
    計算四柱

    Args:
        lunar_date: sxtwl 農曆日期對象
        solar_time: 真太陽時 datetime 對象

    Returns:
        (year_pillar, month_pillar, day_pillar, hour_pillar) 元組
    """
    year_pillar = calculate_year_pillar(lunar_date)
    month_pillar = calculate_month_pillar(lunar_date)
    day_pillar = calculate_day_pillar(lunar_date)

    # 獲取日天干索引用於計算時柱
    day_gz = lunar_date.getDayGZ()
    hour_pillar = calculate_hour_pillar(day_gz.tg, solar_time.hour)

    return year_pillar, month_pillar, day_pillar, hour_pillar


def format_ba_zi(year_pillar: str, month_pillar: str, day_pillar: str, hour_pillar: str) -> str:
    """
    格式化八字字符串

    Args:
        year_pillar: 年柱
        month_pillar: 月柱
        day_pillar: 日柱
        hour_pillar: 時柱

    Returns:
        八字字符串（如 "乙亥 丁亥 己未 庚午"）
    """
    return f"{year_pillar} {month_pillar} {day_pillar} {hour_pillar}"
