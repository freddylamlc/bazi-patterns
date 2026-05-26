"""
十二長生計算模塊
"""

from bazi.core.constants import TIAN_GAN_ZHANG_SHENG

# 7個關鍵長生階段（文件強調只需理會這些）
CHANGSHENG_KEY_STAGES = {
    "長生": {"priority": "高", "含義": "新生、發展潛力"},
    "臨官": {"priority": "高", "含義": "得祿得位、事業有成"},
    "帝旺": {"priority": "高", "含義": "氣勢最強、精力充沛"},
    "墓": {"priority": "高", "含義": "收藏閉塞、入墓收藏"},
    "絕": {"priority": "高", "含義": "絕處逢生、轉折點"},
    "沐浴": {"priority": "中", "含義": "桃花之地、變化之象"},
    "死": {"priority": "中", "含義": "氣數已盡、轉化之象"},
}


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
    flagged_stages = []

    for i, pillar_name in enumerate(pillar_names):
        zhi = ba_zi_parts[i][1]
        chang_sheng = calculate_changsheng_for_pillar(day_gan, zhi)

        key_info = CHANGSHENG_KEY_STAGES.get(chang_sheng)
        is_flagged = key_info is not None

        if is_flagged:
            flagged_stages.append({
                "柱": pillar_name,
                "地支": zhi,
                "十二長生": chang_sheng,
                "優先級": key_info["priority"],
                "含義": key_info["含義"],
            })

        result[pillar_name] = {
            "地支": zhi,
            "十二長生": chang_sheng,
            "是否關鍵階段": is_flagged,
        }

    result["關鍵階段"] = flagged_stages
    return result
