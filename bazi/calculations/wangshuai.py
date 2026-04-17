"""
旺衰判斷模塊 - 計算天干旺衰狀態（根氣強度）
"""

from bazi.core.constants import (
    TIAN_GAN_WU_XING, TIAN_GAN_DE_LING, TIAN_GAN_DE_GEN,
    ZHI_CANG_GAN, WANG_SHUAI_WEIGHTS
)
from bazi.calculations.relations import calculate_zhi_gong_ju, calculate_zhi_ban_san_he


def calculate_root_strength(gan: str, zhi_list: list) -> int:
    """
    計算天干在地支的根氣強度

    根氣強度权重：
    - 月支：4（最強，月令當令）
    - 時支：3（次之，歸息之地）
    - 日支：2（再次，配偶宮）
    - 年支：1（最弱，祖上宮）

    新增虛合能量：
    - 拱局：+1（相當於年支強度）
    - 半合：+1（增加結構穩定性）

    Args:
        gan: 天干
        zhi_list: 地支列表 [年支，月支，日支，時支]

    Returns:
        根氣強度總分
    """
    if not gan:
        return 0

    # 天干五行
    gan_wuxing = TIAN_GAN_WU_XING.get(gan, "")
    if not gan_wuxing:
        return 0

    # 五行對應的地支（含藏干）
    wuxing_to_zhi = {
        "木": ["寅", "卯"],
        "火": ["巳", "午"],
        "土": ["辰", "戌", "丑", "未"],
        "金": ["申", "酉"],
        "水": ["亥", "子"],
    }

    target_zhi = wuxing_to_zhi.get(gan_wuxing, [])

    # 位置权重（月支=4, 時支=3, 日支=2, 年支=1）
    position_weights = [1, 4, 2, 3]

    total_strength = 0.0
    for i, zhi in enumerate(zhi_list):
        if zhi in target_zhi:
            weight = position_weights[i] if i < len(position_weights) else 1
            total_strength += weight

            # 檢查藏干是否有同五行
            cang_gan = ZHI_CANG_GAN.get(zhi, {})
            for qi in ["主氣", "中氣", "餘氣"]:
                cang_gan_val = cang_gan.get(qi)
                if cang_gan_val and TIAN_GAN_WU_XING.get(cang_gan_val) == gan_wuxing:
                    total_strength += weight * 0.5

    # 計算虛合能量 (拱局/半合)
    gong_jus = calculate_zhi_gong_ju(zhi_list)
    for gong in gong_jus:
        if gan_wuxing in gong["局"]:  # 如 "拱火局" 包含 "火"
            total_strength += 1.0

    ban_hes = calculate_zhi_ban_san_he(zhi_list)
    for ban in ban_hes:
        if gan_wuxing in ban["局"]:  # 如 "半合水局" 包含 "水"
            total_strength += 1.0

    return int(total_strength)


def calculate_wangshuai_for_gan(gan: str, month_zhi: str, zhi_list: list) -> dict:
    """
    計算單個天干的旺衰

    Args:
        gan: 天干
        month_zhi: 月支
        zhi_list: 地支列表

    Returns:
        旺衰字典
    """
    gan_wuxing = TIAN_GAN_WU_XING.get(gan, "")

    # 判斷是否得令
    de_ling_zhis = TIAN_GAN_DE_LING.get(gan, [])
    is_de_ling = month_zhi in de_ling_zhis

    # 判斷根氣強度
    root_strength = calculate_root_strength(gan, zhi_list)

    # 旺衰狀態判斷
    if is_de_ling:
        if root_strength >= 5:
            wang_shuai = "旺"
        else:
            wang_shuai = "相"
    else:
        if root_strength >= 5:
            wang_shuai = "相"
        elif root_strength >= 3:
            wang_shuai = "休"
        elif root_strength >= 1:
            wang_shuai = "囚"
        else:
            wang_shuai = "死"

    return {
        "天干": gan,
        "五行": gan_wuxing,
        "旺衰": wang_shuai,
        "根氣強度": root_strength,
        "得令": is_de_ling,
    }


def calculate_wangshuai(ba_zi: str) -> dict:
    """
    計算八字旺衰

    Args:
        ba_zi: 八字字符串

    Returns:
        旺衰字典，包含：
        - 年柱/月柱/日柱/時柱: 各柱旺衰信息
        - 日主旺衰: 日主根氣強度和身旺/身衰判斷
        - 地支得根: 地支得根詳情列表
        - {天干}_總根氣: 各天干的總根氣強度
        - {天干}_根氣論斷: 各天干的根氣論斷
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]
    pillar_short_names = ["年", "月", "日", "時"]

    # 提取天干和地支
    gan_list = [p[0] for p in ba_zi_parts]
    zhi_list = [p[1] for p in ba_zi_parts]
    month_zhi = zhi_list[1]  # 月支

    result = {}

    # 計算各柱旺衰
    for i, pillar_name in enumerate(pillar_names):
        gan = gan_list[i]
        result[pillar_name] = calculate_wangshuai_for_gan(gan, month_zhi, zhi_list)

    # 計算日主旺衰（用於判斷身旺/身衰）
    day_gan = gan_list[2]
    day_root_strength = calculate_root_strength(day_gan, zhi_list)
    result["日主旺衰"] = {
        "日干": day_gan,
        "根氣強度": day_root_strength,
        "身旺": day_root_strength >= 5,
        "說明": "根氣強度 ≥ 5 為身旺，< 5 為身衰",
    }

    # 計算地支得根詳情
    position_weights = [1, 4, 2, 3]  # 年、月、日、時的權重

    # 五行對應的地支（含藏干）
    wuxing_to_zhi = {
        "木": ["寅", "卯"],
        "火": ["巳", "午"],
        "土": ["辰", "戌", "丑", "未"],
        "金": ["申", "酉"],
        "水": ["亥", "子"],
    }
    day_gan_wuxing = TIAN_GAN_WU_XING.get(day_gan, "")
    target_zhi = wuxing_to_zhi.get(day_gan_wuxing, [])

    di_zhi_de_gen = []
    for i, zhi in enumerate(zhi_list):
        # 檢查日主是否在該地支得根
        is_de_gen = zhi in target_zhi
        cang_gan = ZHI_CANG_GAN.get(zhi, {})

        # 計算日主在該地支的根氣強度
        gen_qi_strength = 0
        if is_de_gen:
            gen_qi_strength = position_weights[i]

        # 檢查藏干
        cang_gan_de_gen = {}
        for qi_name, qi_gan in cang_gan.items():
            if qi_gan and TIAN_GAN_WU_XING.get(qi_gan) == day_gan_wuxing:
                cang_gan_de_gen[qi_name] = qi_gan
                gen_qi_strength += position_weights[i] * 0.5

        di_zhi_de_gen.append({
            "柱": pillar_short_names[i] + "支",
            "地支": zhi,
            "日主得根": is_de_gen or len(cang_gan_de_gen) > 0,
            "日主根氣強度": int(gen_qi_strength),
            "藏干": cang_gan_de_gen if cang_gan_de_gen else cang_gan,
        })

    result["地支得根"] = di_zhi_de_gen

    # 計算各天干的總根氣和論斷
    for i, gan in enumerate(gan_list):
        total_root = calculate_root_strength(gan, zhi_list)
        result[f"{gan}_總根氣"] = total_root

        # 根氣論斷
        if total_root >= 8:
            lun_duan = "根氣極旺"
        elif total_root >= 5:
            lun_duan = "根氣旺盛"
        elif total_root >= 3:
            lun_duan = "根氣中等"
        elif total_root >= 1:
            lun_duan = "根氣微弱"
        else:
            lun_duan = "虛浮無根"

        result[f"{gan}_根氣論斷"] = lun_duan

    return result
