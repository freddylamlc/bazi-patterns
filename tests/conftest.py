"""
pytest 配置
"""

import pytest
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def test_birth_data():
    """測試用出生數據"""
    return {
        "name": "測試",
        "gender": "男",
        "calendar": "公曆",
        "year": 1995,
        "month": 11,
        "day": 24,
        "hour": 12,
        "minute": 0,
        "birth_city": "香港",
    }


@pytest.fixture(scope="session")
def female_birth_data():
    """測試用女性出生數據"""
    return {
        "name": "測試",
        "gender": "女",
        "calendar": "公曆",
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 8,
        "minute": 30,
        "birth_city": "台北",
    }


@pytest.fixture(scope="session")
def bazi_input_data():
    """測試用八字輸入數據（四柱反推）"""
    return {
        "year_gan": "乙",
        "year_zhi": "亥",
        "month_gan": "丁",
        "month_zhi": "亥",
        "day_gan": "己",
        "day_zhi": "未",
        "hour_gan": "庚",
        "hour_zhi": "午",
    }


@pytest.fixture
def sample_gan_zhi():
    """測試用天干地支樣本"""
    return {
        "gans": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
        "zhis": ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"],
    }
