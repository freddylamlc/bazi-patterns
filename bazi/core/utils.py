"""
工具函數模塊 - 包含農曆轉換、節氣計算等通用工具函數
"""

import datetime
from typing import Any
import sxtwl
from bazi.core.constants import (
    GAN, ZHI, JIE_QI_NAMES, YUE_ORDER, RI_ORDER,
    TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG, LIU_SHI_JIA_ZI
)


def calculate_solar_time(year: int, month: int, day: int, hour: int, minute: int, birth_longitude: float) -> datetime.datetime:
    """
    計算真太陽時

    真太陽時 = 出生時間 + (出生城市經度 - 120) × 4 分鐘

    Args:
        year: 年份
        month: 月份
        day: 日期
        hour: 小時
        minute: 分鐘
        birth_longitude: 出生城市經度

    Returns:
        真太陽時 datetime 對象
    """
    # 計算時間差（分鐘）
    time_diff = (birth_longitude - 120) * 4

    # 建立出生時間
    birth_time = datetime.datetime(year, month, day, hour, minute)

    # 計算真太陽時
    solar_time = birth_time + datetime.timedelta(minutes=time_diff)

    return solar_time


def convert_to_lunar(solar_time: datetime.datetime, calendar: str) -> Any:
    """
    將公曆日期轉換為農曆

    Args:
        solar_time: 真太陽時 datetime 對象
        calendar: 曆法（"公曆" 或 "農曆"）

    Returns:
        農曆日期對象
    """
    # 支持简体和繁体的"公曆"以及"陽曆"
    if calendar in ["公曆", "阳历", "陽曆"]:
        # 使用真太陽時轉換
        year = solar_time.year
        month = solar_time.month
        day = solar_time.day
        day_obj = sxtwl.fromSolar(year, month, day)
    else:  # 農曆
        # 直接使用輸入的農曆日期
        year = solar_time.year
        month = solar_time.month
        day = solar_time.day
        # 需要判斷是否為閏月
        day_obj = sxtwl.fromLunar(year, month, day)

    return day_obj


def calculate_jie_qi(solar_time: datetime.datetime, month_zhi: str) -> dict:
    """
    計算節氣信息

    Args:
        solar_time: 真太陽時
        month_zhi: 月支

    Returns:
        節氣信息字典，包含：
        - 當前節氣
        - 下一節氣
        - 距前一節氣的天數
        - 距下一節氣的天數
    """
    # 節氣與地支的對應關係
    zhi_to_jieqi = {
        "子": "大雪", "丑": "小寒", "寅": "立春", "卯": "驚蟄",
        "辰": "清明", "巳": "立夏", "午": "芒種", "未": "小暑",
        "申": "立秋", "酉": "白露", "戌": "寒露", "亥": "立冬",
    }

    # 獲取當前月支對應的節氣
    current_jieqi_name = zhi_to_jieqi.get(month_zhi, "")

    # 計算節氣時間
    year = solar_time.year
    jieqi_times = {}
    for jq_name in JIE_QI_NAMES:
        try:
            jq = sxtwl.getJieQi(year, jq_name)
            jieqi_times[jq_name] = jq
        except Exception:
            pass

    # 找到當前節氣和下一節氣
    current_jieqi = None
    next_jieqi = None
    prev_jieqi = None

    jq_names_cycle = JIE_QI_NAMES + JIE_QI_NAMES  # 循環處理跨年

    for i, jq_name in enumerate(jq_names_cycle):
        if jq_name in jieqi_times:
            jq_time = jieqi_times[jq_name]
            jq_datetime = datetime.datetime(
                jq_time.year, jq_time.month, jq_time.day,
                jq_time.hour, jq_time.minute
            )

            if jq_datetime <= solar_time:
                prev_jieqi = (jq_name, jq_datetime)
            elif jq_datetime > solar_time and next_jieqi is None:
                next_jieqi = (jq_name, jq_datetime)
                break

    # 計算距離
    days_to_prev = (solar_time - prev_jieqi[1]).days if prev_jieqi else 0
    days_to_next = (next_jieqi[1] - solar_time).days if next_jieqi else 0

    return {
        "當前節氣": current_jieqi_name,
        "前一節氣": prev_jieqi[0] if prev_jieqi else "",
        "下一節氣": next_jieqi[0] if next_jieqi else "",
        "距前一節氣": f"{days_to_prev}天",
        "距下一節氣": f"{days_to_next}天",
    }


def get_wu_xing_sheng(wu_xing: str) -> str:
    """
    獲取某五行所生的五行

    Args:
        wu_xing: 五行（木、火、土、金、水）

    Returns:
        所生的五行
    """
    sheng_map = {
        "木": "火", "火": "土", "土": "金",
        "金": "水", "水": "木",
    }
    return sheng_map.get(wu_xing, "")


def get_wu_xing_ke(wu_xing: str) -> str:
    """
    獲取某五行所剋的五行

    Args:
        wu_xing: 五行（木、火、土、金、水）

    Returns:
        所剋的五行
    """
    ke_map = {
        "木": "土", "土": "水", "水": "火",
        "火": "金", "金": "木",
    }
    return ke_map.get(wu_xing, "")


def get_gan_index(gan: str) -> int:
    """獲取天干索引"""
    return GAN.index(gan) if gan in GAN else -1


def get_zhi_index(zhi: str) -> int:
    """獲取地支索引"""
    return ZHI.index(zhi) if zhi in ZHI else -1


def get_jia_zi_index(gan: str, zhi: str) -> int:
    """
    獲取干支在六十甲子中的索引

    Args:
        gan: 天干
        zhi: 地支

    Returns:
        索引（0-59），-1 表示無效
    """
    gan_idx = get_gan_index(gan)
    zhi_idx = get_zhi_index(zhi)

    if gan_idx == -1 or zhi_idx == -1:
        return -1

    # 檢查陰陽是否匹配（陽干配陽支，陰干配陰支）
    if gan_idx % 2 != zhi_idx % 2:
        return -1

    # 計算索引
    for i, jia_zi in enumerate(LIU_SHI_JIA_ZI):
        if jia_zi[0] == gan and jia_zi[1] == zhi:
            return i

    return -1


def lunar_to_solar(lunar_year: int, lunar_month: int, lunar_day: int, is_leap: bool = False) -> tuple:
    """
    農曆轉公曆

    Args:
        lunar_year: 農历年份
        lunar_month: 農曆月份
        lunar_day: 農曆日期
        is_leap: 是否閏月

    Returns:
        (year, month, day) 元組
    """
    try:
        day_obj = sxtwl.fromLunar(lunar_year, lunar_month, lunar_day, is_leap)
        return (day_obj.getSolarYear(), day_obj.getSolarMonth(), day_obj.getSolarDay())
    except Exception:
        return (lunar_year, lunar_month, lunar_day)
