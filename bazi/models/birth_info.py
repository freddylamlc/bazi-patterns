"""
出生信息數據類 - 用於封裝出生時間、地點等信息
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BirthInfo:
    """出生信息數據類"""

    name: str
    """姓名"""

    gender: str
    """性別（"男" 或 "女"）"""

    calendar: str
    """曆法（"公曆" 或 "農曆"）"""

    year: int
    """年份"""

    month: int
    """月份"""

    day: int
    """日期"""

    hour: int
    """小時"""

    minute: int
    """分鐘"""

    birth_city: str
    """出生城市"""

    current_city: Optional[str] = None
    """現居城市（可選）"""

    birth_longitude: Optional[float] = None
    """出生城市經度（可選）"""

    def validate(self) -> tuple[bool, str]:
        """
        驗證出生信息是否有效

        Returns:
            (is_valid, error_message) 元組
        """
        # 驗證性別
        if self.gender not in ["男", "女"]:
            return False, f"無效的性別：{self.gender}，必須為 '男' 或 '女'"

        # 驗證年份
        if not (1900 <= self.year <= 2100):
            return False, f"無效的年份：{self.year}，必須在 1900-2100 之間"

        # 驗證月份
        if not (1 <= self.month <= 12):
            return False, f"無效的月份：{self.month}，必須在 1-12 之間"

        # 驗證日期
        if not (1 <= self.day <= 31):
            return False, f"無效的日期：{self.day}，必須在 1-31 之間"

        # 驗證小時
        if not (0 <= self.hour <= 23):
            return False, f"無效的小時：{self.hour}，必須在 0-23 之間"

        # 驗證分鐘
        if not (0 <= self.minute <= 59):
            return False, f"無效的分鐘：{self.minute}，必須在 0-59 之間"

        return True, ""

    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "name": self.name,
            "gender": self.gender,
            "calendar": self.calendar,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "birth_city": self.birth_city,
            "current_city": self.current_city,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BirthInfo":
        """從字典創建"""
        return cls(
            name=data.get("name", ""),
            gender=data.get("gender", "男"),
            calendar=data.get("calendar", "公曆"),
            year=int(data.get("year", 1995)),
            month=int(data.get("month", 1)),
            day=int(data.get("day", 1)),
            hour=int(data.get("hour", 12)),
            minute=int(data.get("minute", 0)),
            birth_city=data.get("birth_city", "香港"),
            current_city=data.get("current_city"),
        )
