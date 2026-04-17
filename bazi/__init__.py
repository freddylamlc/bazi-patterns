"""
八字計算器包 - 中式八字（Four Pillars of Destiny）計算引擎

這是一個模塊化的八字計算系統，包含：
- 四柱計算
- 藏干、十神、十二長生
- 天干五合、地支關係
- 旺衰判斷
- 神煞計算
- 格局判斷
- 宮位分析
- 先天病源
- 大運流年判斷
"""

from bazi.core.calculator import BaZiCalculator
from bazi.models.birth_info import BirthInfo
from bazi.models.bazi_result import BaZiResult

__version__ = "2.0.0"
__all__ = ["BaZiCalculator", "BirthInfo", "BaZiResult"]
