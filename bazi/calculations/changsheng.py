"""
十二長生計算模塊
"""

from bazi.core.constants import TIAN_GAN_ZHANG_SHENG


def calculate_changsheng_for_pillar(day_gan: str, zhi: str) -> str:
    """
    計算單個地支的十二長生

    Args:
        day_gan: 日天干
        zhi: 地支

    Returns:
        十二長生狀態
    """
    return TIAN_GAN_ZHANG_SHENG.get(day_gan, {}).get(zhi, "")


def calculate_changsheng(ba_zi: str) -> dict:
    """
    計算八字十二長生

    Args:
        ba_zi: 八字字符串

    Returns:
        十二長生字典
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    # 日天干為基準
    day_gan = ba_zi_parts[2][0]

    result = {}
    for i, pillar_name in enumerate(pillar_names):
        zhi = ba_zi_parts[i][1]
        chang_sheng = calculate_changsheng_for_pillar(day_gan, zhi)
        result[pillar_name] = {
            "地支": zhi,
            "十二長生": chang_sheng,
        }

    return result
