"""
名人命盤匹配模塊
從 celebrities.json 載入名人資料，提供按出生日期匹配的功能。
"""

import json
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).resolve().parent
_CelebrityDB: Optional[list[dict]] = None


def _load_database() -> list[dict]:
    """載入名人資料庫（惰性載入，僅讀取一次）。"""
    global _CelebrityDB
    if _CelebrityDB is not None:
        return _CelebrityDB

    db_path = _DATA_DIR / "celebrities.json"
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            _CelebrityDB = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _CelebrityDB = []

    return _CelebrityDB


def _parse_year(raw_year) -> Optional[int]:
    """將年份轉為整數，處理西元前字串格式。"""
    if raw_year is None:
        return None
    if isinstance(raw_year, int):
        return raw_year
    if isinstance(raw_year, str):
        # 處理 "西元前259" → -259
        if raw_year.startswith("西元前"):
            try:
                return -int(raw_year.replace("西元前", "").strip())
            except ValueError:
                return None
        try:
            return int(raw_year)
        except ValueError:
            return None
    return None


def find_matching_celebrities(year: int, month: int, day: int) -> dict:
    """
    根據出生日期查找匹配的名人。

    參數:
        year: 公曆出生年份
        month: 公曆出生月份
        day: 公曆出生日

    回傳:
        {
            "同月同日": [...],   # 同月同日（任何年份，排除近似日期）
            "同年": [...],       # 同年出生
            "同月": [...]        # 同月出生（最多 10 筆，按年份接近排序）
        }
    """
    db = _load_database()

    same_month_day: list[dict] = []
    same_year: list[dict] = []
    same_month: list[dict] = []

    for c in db:
        entry = _format_entry(c)
        if entry is None:
            continue

        c_month = c.get("month")
        c_day = c.get("day")
        c_year = _parse_year(c.get("year"))
        is_approx = c.get("date_approximate", False)

        # 同月同日：排除近似日期（如古代人物用 1/1 佔位）
        if c_month == month and c_day == day and not is_approx:
            same_month_day.append(entry)

        # 同年：處理西元前年份
        if c_year is not None and c_year == year:
            same_year.append(entry)

        # 同月：排除同月同日（已在上面分類）及近似日期
        if c_month == month and not (c_month == month and c_day == day) and not is_approx:
            same_month.append(entry)

    # 同月按年份接近排序（越接近查詢年份越靠前）
    same_month.sort(key=lambda e: abs((e.get("year") or 9999) - year))
    same_month = same_month[:10]

    return {
        "同月同日": same_month_day,
        "同年": same_year,
        "同月": same_month,
    }


def _format_entry(c: dict) -> Optional[dict]:
    """將名人記錄格式化為標準輸出格式。"""
    name = c.get("name")
    if not name:
        return None
    return {
        "name": name,
        "name_en": c.get("name_en", ""),
        "year": _parse_year(c.get("year")),
        "month": c.get("month"),
        "day": c.get("day"),
        "field": c.get("field", ""),
        "country": c.get("country", ""),
        "description": c.get("description", ""),
    }
