"""
十神計算模塊
"""

from bazi.core.constants import TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG


def get_shi_shen(gan: str, day_gan: str) -> str:
    """
    計算單個天干相對於日干的十神

    Args:
        gan: 天干
        day_gan: 日天干

    Returns:
        十神名稱
    """
    gan_wuxing = TIAN_GAN_WU_XING.get(gan, "")
    gan_yinyang = TIAN_GAN_YIN_YANG.get(gan, "")
    day_gan_wuxing = TIAN_GAN_WU_XING.get(day_gan, "")
    day_gan_yinyang = TIAN_GAN_YIN_YANG.get(day_gan, "")

    return _calculate_shi_shen(gan, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang)


def _calculate_shi_shen(gan: str, gan_wuxing: str, gan_yinyang: str,
                        day_gan: str, day_gan_wuxing: str, day_gan_yinyang: str) -> str:
    """
    計算十神

    規則：
    - 同五行：比肩（同陰陽）/ 劫財（不同陰陽）
    - 我生：食神（同陰陽）/ 傷官（不同陰陽）
    - 我剋：偏財（同陰陽）/ 正財（不同陰陽）
    - 剋我：七殺（同陰陽）/ 正官（不同陰陽）
    - 生我：偏印（同陰陽）/ 正印（不同陰陽）
    """
    # 同五行
    if gan_wuxing == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "比肩"
        else:
            return "劫財"

    # 我生（日干生天干）
    sheng_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    if sheng_map.get(day_gan_wuxing) == gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "食神"
        else:
            return "傷官"

    # 我剋（日干剋天干）
    ke_map = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if ke_map.get(day_gan_wuxing) == gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "偏財"
        else:
            return "正財"

    # 剋我（天干剋日干）
    if ke_map.get(gan_wuxing) == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "七殺"
        else:
            return "正官"

    # 生我（天干生日干）
    if sheng_map.get(gan_wuxing) == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "偏印"
        else:
            return "正印"

    return "未知"


def calculate_shishen_for_canggan(canggan: dict, day_gan: str) -> dict:
    """
    計算藏干的十神

    Args:
        canggan: 藏干字典
        day_gan: 日天干

    Returns:
        藏干十神字典
    """
    result = {}

    for qi in ["主氣", "中氣", "餘氣"]:
        cg = canggan.get(qi)
        if cg:
            shi_shen = get_shi_shen(cg, day_gan)
            result[qi] = {
                "干": cg,
                "十神": shi_shen,
            }
        else:
            result[qi] = None

    return result


def calculate_shishen(ba_zi: str, canggan: dict) -> dict:
    """
    計算八字十神

    Args:
        ba_zi: 八字字符串
        canggan: 地支藏干字典

    Returns:
        十神字典
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    # 日天干為基準
    day_gan = ba_zi_parts[2][0]

    result = {}
    for i, pillar_name in enumerate(pillar_names):
        pillar = ba_zi_parts[i]
        gan = pillar[0]
        zhi = pillar[1]

        # 計算天干十神
        shi_shen = get_shi_shen(gan, day_gan)

        # 計算藏干十神
        pillar_canggan = canggan.get(pillar_name, {})
        canggan_shishen = calculate_shishen_for_canggan(pillar_canggan, day_gan)

        result[pillar_name] = {
            "柱": pillar,
            "天干": gan,
            "天干十神": shi_shen,
            "地支": zhi,
            "藏干十神": canggan_shishen,
        }

    return result
