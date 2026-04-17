"""
驗證器模塊 - 包含輸入驗證邏輯

使用方式：
    from bazi.validators import validate_birth_info, validate_bazi_input

    # 驗證出生信息
    validate_birth_info(gender="男", year=1995, month=11, day=24, hour=12, minute=0)

    # 驗證八字輸入（四柱反推）
    validate_bazi_input("甲", "子", "丙", "寅", "戊", "辰", "壬", "子")
"""

from typing import Optional, Tuple
from bazi.exceptions import (
    InvalidBirthTimeError,
    InvalidBirthYearError,
    InvalidBirthMonthError,
    InvalidBirthDayError,
    InvalidBirthHourError,
    InvalidGenderError,
    InvalidCalendarError,
    InvalidCityError,
)


def validate_birth_info(
    gender: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
) -> None:
    """
    驗證出生信息

    Args:
        gender: 性別（"男" 或 "女"）
        year: 年份（1900-2100）
        month: 月份（1-12）
        day: 日期（1-31）
        hour: 小時（0-23）
        minute: 分鐘（0-59）

    Raises:
        InvalidGenderError: 性別無效
        InvalidBirthYearError: 年份無效
        InvalidBirthMonthError: 月份無效
        InvalidBirthDayError: 日期無效
        InvalidBirthHourError: 小時無效
        InvalidBirthTimeError: 分鐘無效
    """
    # 驗證性別
    if gender not in ["男", "女"]:
        raise InvalidGenderError(f"無效的性別：{gender}，必須為 '男' 或 '女'", value=gender)

    # 驗證年份
    if not (1900 <= year <= 2100):
        raise InvalidBirthYearError(f"無效的年份：{year}，必須在 1900-2100 之間", value=year)

    # 驗證月份
    if not (1 <= month <= 12):
        raise InvalidBirthMonthError(f"無效的月份：{month}，必須在 1-12 之間", value=month)

    # 驗證日期
    if not (1 <= day <= 31):
        raise InvalidBirthDayError(f"無效的日期：{day}，必須在 1-31 之間", value=day)

    # 驗證小時
    if not (0 <= hour <= 23):
        raise InvalidBirthHourError(f"無效的小時：{hour}，必須在 0-23 之間", value=hour)

    # 驗證分鐘
    if not (0 <= minute <= 59):
        raise InvalidBirthTimeError(f"無效的分鐘：{minute}，必須在 0-59 之間", value=minute)


def validate_calendar(calendar: str) -> None:
    """
    驗證曆法

    Args:
        calendar: 曆法（"公曆" 或 "農曆"）

    Raises:
        InvalidCalendarError: 曆法無效
    """
    valid_calendars = ["公曆", "農曆"]
    if calendar not in valid_calendars:
        raise InvalidCalendarError(
            f"無效的曆法：{calendar}，必須為 {' 或 '.join(valid_calendars)}",
            value=calendar
        )


def validate_city(city: str, required: bool = True) -> None:
    """
    驗證城市名稱

    Args:
        city: 城市名稱
        required: 是否為必填

    Raises:
        InvalidCityError: 城市名稱無效
    """
    if not city:
        if required:
            raise InvalidCityError("出生城市不能為空", value=city)
        return

    if not isinstance(city, str):
        raise InvalidCityError(f"城市名稱必須為字符串", value=city)

    if len(city.strip()) < 2:
        raise InvalidCityError(f"城市名稱太短：'{city}'，至少需要 2 個字符", value=city)


def validate_bazi_input(
    year_gan: str,
    year_zhi: str,
    month_gan: str,
    month_zhi: str,
    day_gan: str,
    day_zhi: str,
    hour_gan: str,
    hour_zhi: str,
) -> None:
    """
    驗證八字輸入（四柱反推功能）

    Args:
        year_gan, year_zhi: 年柱天干地支
        month_gan, month_zhi: 月柱天干地支
        day_gan, day_zhi: 日柱天干地支
        hour_gan, hour_zhi: 時柱天干地支

    Raises:
        InvalidBirthTimeError: 當輸入無效時
    """
    from bazi.core.constants import Gan, Zhi

    valid_gans = set(Gan)
    valid_zhis = set(Zhi)

    for gan, name in [(year_gan, "年干"), (month_gan, "月干"), (day_gan, "日干"), (hour_gan, "時干")]:
        if gan not in valid_gans:
            raise InvalidBirthTimeError(f"無效的天干 {name}：{gan}", value=gan)

    for zhi, name in [(year_zhi, "年支"), (month_zhi, "月支"), (day_zhi, "日支"), (hour_zhi, "時支")]:
        if zhi not in valid_zhis:
            raise InvalidBirthTimeError(f"無效的地支 {name}：{zhi}", value=zhi)


def validate_name(name: str, required: bool = False, max_length: int = 50) -> Optional[str]:
    """
    驗證姓名

    Args:
        name: 姓名
        required: 是否為必填
        max_length: 最大長度

    Returns:
        修剪後的姓名，如果為空且非必填則返回 None

    Raises:
        InvalidBirthTimeError: 姓名無效
    """
    if not name:
        if required:
            raise InvalidBirthTimeError("姓名不能為空")
        return None

    if not isinstance(name, str):
        raise InvalidBirthTimeError(f"姓名必須為字符串")

    cleaned = name.strip()

    if len(cleaned) == 0:
        if required:
            raise InvalidBirthTimeError("姓名不能為空")
        return None

    if len(cleaned) > max_length:
        raise InvalidBirthTimeError(f"姓名太長：'{cleaned}'，最多 {max_length} 個字符")

    return cleaned


def validate_complete_input(
    name: str,
    gender: str,
    calendar: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    birth_city: str,
    current_city: Optional[str] = None,
) -> Tuple[str, str, str, int, int, int, int, int, str, Optional[str]]:
    """
    驗證完整的輸入信息

    Args:
        name: 姓名
        gender: 性別
        calendar: 曆法
        year: 年份
        month: 月份
        day: 日期
        hour: 小時
        minute: 分鐘
        birth_city: 出生城市
        current_city: 當前城市（可選）

    Returns:
        (cleaned_name, gender, calendar, year, month, day, hour, minute, birth_city, current_city)

    Raises:
        Various validation errors
    """
    # 驗證所有字段
    cleaned_name = validate_name(name, required=False)
    validate_gender_extended(gender)
    validate_calendar(calendar)
    validate_birth_info(gender, year, month, day, hour, minute)
    validate_city(birth_city, required=True)

    if current_city:
        validate_city(current_city, required=False)

    return (cleaned_name, gender, calendar, year, month, day, hour, minute, birth_city, current_city)


def validate_gender_extended(gender: str) -> None:
    """
    驗證性別（擴展版本，支持更多輸入格式）

    Args:
        gender: 性別

    Raises:
        InvalidGenderError: 性別無效
    """
    # 支持多種輸入格式
    gender_map = {
        "男": "男",
        "女": "女",
        "M": "男",
        "F": "女",
        "male": "男",
        "female": "女",
        "男 (乾造)": "男",
        "女 (坤造)": "女",
    }

    if gender not in gender_map:
        raise InvalidGenderError(
            f"無效的性別：{gender}，支持的格式：{', '.join(gender_map.keys())}",
            value=gender
        )
