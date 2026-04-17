"""
八字卦模塊 - 實現八字起卦邏輯
"""
from typing import Dict
from ..core.constants import ZHI

# Trigram mapping (Standard Plum Blossom numbers)
# 1: 乾, 2: 兌, 3: 離, 4: 震, 5: 巽, 6: 坎, 7: 艮, 8: 坤
TRIGRAMS = ["", "乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]

def get_branch_number(branch: str) -> int:
    """子=1, 丑=2, ... 亥=12"""
    try:
        return ZHI.index(branch) + 1
    except ValueError:
        return 1

def calculate_bazi_gua(year_zhi: str, day_zhi: str) -> Dict:
    """
    八字卦起卦邏輯：年支上卦、日之下卦
    """
    upper_num = get_branch_number(year_zhi) % 8
    if upper_num == 0: upper_num = 8

    lower_num = get_branch_number(day_zhi) % 8
    if lower_num == 0: lower_num = 8

    upper_trigram = TRIGRAMS[upper_num]
    lower_trigram = TRIGRAMS[lower_num]

    # 組合卦名
    gua_name = f"{upper_trigram}{lower_trigram}"

    return {
        "upper": upper_trigram,
        "lower": lower_trigram,
        "name": gua_name,
        "description": f"此卦由年支 {year_zhi} (上卦 {upper_trigram}) 與日支 {day_zhi} (下卦 {lower_trigram}) 組成。"
    }
