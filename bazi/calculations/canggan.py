"""
地支藏干計算模塊
"""

from bazi.core.constants import ZHI_CANG_GAN


def calculate_canggan_for_zhi(zhi: str) -> dict:
    """
    計算單個地支的藏干

    Args:
        zhi: 地支

    Returns:
        藏干字典
    """
    cang_gan = ZHI_CANG_GAN.get(zhi, {"主氣": None, "中氣": None, "餘氣": None})

    # 格式化藏干字符串
    cg_list = []
    if cang_gan.get("主氣"):
        cg_list.append(cang_gan["主氣"])
    if cang_gan.get("中氣"):
        cg_list.append(cang_gan["中氣"])
    if cang_gan.get("餘氣"):
        cg_list.append(cang_gan["餘氣"])

    return {
        "地支": zhi,
        "藏干": "".join(cg_list) if cg_list else "",
        "主氣": cang_gan.get("主氣"),
        "中氣": cang_gan.get("中氣"),
        "餘氣": cang_gan.get("餘氣"),
    }


def calculate_canggan(ba_zi: str) -> dict:
    """
    計算八字的地支藏干

    Args:
        ba_zi: 八字字符串（如 "甲子 乙丑 丙寅 丁卯"）

    Returns:
        四柱藏干字典
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    result = {}
    for i, pillar in enumerate(ba_zi_parts):
        zhi = pillar[1]  # 獲取地支
        canggan_info = calculate_canggan_for_zhi(zhi)

        result[pillar_names[i]] = {
            "柱": pillar,
            **canggan_info,
        }

    return result
