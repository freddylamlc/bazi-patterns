"""
天干五合、地支關係計算模塊
包含：六合、六沖、三合局、三會方、拱局、半合局、刑、穿、破
"""

from bazi.core.constants import (
    TIAN_GAN_WU_HE, WU_HE_HUA_QI_ZHI, TIAN_GAN_WU_HE_ZHENG_HE, TIAN_GAN_WU_HE_DU_HE,
    ZHI_LIU_HE, LIU_HE_HUA_QI_TIAN_GAN, ZHI_LIU_CHONG, ZHI_SAN_HE_JU,
    SAN_HE_JU_HUA_QI_TIAN_GAN, ZHI_SAN_HUI_FANG, ZHI_GONG_JU, ZHI_BAN_SAN_HE,
    ZHI_XING, ZHI_CHUAN, ZHI_PO, TIAN_GAN_YIN_YANG
)


def calculate_tian_gan_wu_he(ba_zi: str) -> list:
    """
    計算天干五合

    Args:
        ba_zi: 八字字符串（如 "甲子 乙丑 丙寅 丁卯"）

    Returns:
        天干五合列表
    """
    ba_zi_parts = ba_zi.split()
    results = []

    # 提取四柱的天干
    pillars = {
        "年柱": ba_zi_parts[0][0],
        "月柱": ba_zi_parts[1][0],
        "日柱": ba_zi_parts[2][0],
        "時柱": ba_zi_parts[3][0],
    }

    # 提取四柱的地支（用於判斷是否能化）
    zhi_list = [p[1] for p in ba_zi_parts]
    pillar_order = ["年柱", "月柱", "日柱", "時柱"]

    # 檢查所有天干組合
    pairs = [
        ("年柱", "月柱"), ("年柱", "日柱"), ("年柱", "時柱"),
        ("月柱", "日柱"), ("月柱", "時柱"), ("日柱", "時柱"),
    ]

    for p1, p2 in pairs:
        tg1 = pillars[p1]
        tg2 = pillars[p2]

        # 構建 key
        pair_key = tg1 + tg2
        reverse_key = tg2 + tg1

        if pair_key in TIAN_GAN_WU_HE:
            he_info = TIAN_GAN_WU_HE[pair_key]
            # 檢查是否能化
            can_hua = any(z in zhi_list for z in WU_HE_HUA_QI_ZHI.get(pair_key, []))
            status = "可化" if can_hua else "合絆"

            results.append({
                "合": he_info["合名"],
                "位置": [p1, p2],
                "天干": f"{tg1}-{tg2}",
                "化神": he_info["化氣"],
                "狀態": status,
            })
        elif reverse_key in TIAN_GAN_WU_HE:
            he_info = TIAN_GAN_WU_HE[reverse_key]
            can_hua = any(z in zhi_list for z in WU_HE_HUA_QI_ZHI.get(reverse_key, []))
            status = "可化" if can_hua else "合絆"

            results.append({
                "合": he_info["合名"],
                "位置": [p1, p2],
                "天干": f"{tg2}-{tg1}",
                "化神": he_info["化氣"],
                "狀態": status,
            })

    # 檢查爭合與妒合
    all_tian_gan = list(pillars.values())

    for r in results:
        # 獲取參與合的天干
        tg1, tg2 = r["天干"].split("-")

        # 統計這兩個天干在八字中出現的次數
        count1 = all_tian_gan.count(tg1)
        count2 = all_tian_gan.count(tg2)

        # 只要有一方出現多次，即非正常合
        if count1 > 1 or count2 > 1:
            # 判斷是誰出現了多次
            multi_tg = tg1 if count1 > 1 else tg2
            single_tg = tg2 if count1 > 1 else tg1

            # 二合一或多合一的邏輯：
            # 陽干多合一陰干 = 爭合 (Contention)
            # 陰干多合一陽干 = 妒合 (Jealousy)
            if TIAN_GAN_YIN_YANG[multi_tg] == "陽":
                r["狀態"] = f"爭合 ({count1}合{count2})" if (count1 > 1 and count2 > 1) else "爭合"
            else:
                r["狀態"] = f"妒合 ({count1}合{count2})" if (count1 > 1 and count2 > 1) else "妒合"

            # 針對常見的二合一提供具體描述
            if (count1 == 2 and count2 == 1) or (count1 == 1 and count2 == 2):
                if TIAN_GAN_YIN_YANG[multi_tg] == "陽":
                    r["狀態"] = f"爭合 ({multi_tg}{single_tg}{multi_tg})"
                else:
                    r["狀態"] = f"妒合 ({multi_tg}{single_tg}{multi_tg})"

    return results


def calculate_zhi_liu_he(zhi_list: list, tian_gan_list: list = None) -> list:
    """
    計算地支六合

    Args:
        zhi_list: 地支列表
        tian_gan_list: 天干列表（用於判斷化氣）

    Returns:
        六合列表
    """
    results = []
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    for i in range(len(zhi_list)):
        for j in range(i + 1, len(zhi_list)):
            zhi1, zhi2 = zhi_list[i], zhi_list[j]
            pair_key = zhi1 + zhi2

            if pair_key in ZHI_LIU_HE:
                he_name = ZHI_LIU_HE[pair_key]
                # 檢查是否有化氣天干
                can_hua = False
                if tian_gan_list:
                    hua_qi_gans = LIU_HE_HUA_QI_TIAN_GAN.get(pair_key, [])
                    can_hua = any(gan in tian_gan_list for gan in hua_qi_gans)

                results.append({
                    "合": he_name,
                    "位置": f"{pillar_names[i]}~{pillar_names[j]}",
                    "地支": f"{zhi1}-{zhi2}",
                    "狀態": "可化" if can_hua else "合絆",
                })

    return results


def calculate_zhi_liu_chong(zhi_list: list) -> list:
    """
    計算地支六沖

    Args:
        zhi_list: 地支列表

    Returns:
        六沖列表
    """
    results = []
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    for i in range(len(zhi_list)):
        for j in range(i + 1, len(zhi_list)):
            zhi1, zhi2 = zhi_list[i], zhi_list[j]
            for c1, c2 in ZHI_LIU_CHONG:
                if (zhi1 == c1 and zhi2 == c2) or (zhi1 == c2 and zhi2 == c1):
                    results.append({
                        "沖": f"{zhi1}{zhi2}沖",
                        "位置": f"{pillar_names[i]}~{pillar_names[j]}",
                    })

    return results


def calculate_zhi_san_he_ju(zhi_list: list, tian_gan_list: list = None) -> list:
    """
    計算地支三合局

    Args:
        zhi_list: 地支列表
        tian_gan_list: 天干列表

    Returns:
        三合局列表
    """
    results = []
    zhi_set = set(zhi_list)

    for ju_name, ju_info in ZHI_SAN_HE_JU.items():
        chang_sheng = ju_info["長生"]
        di_wang = ju_info["帝旺"]
        mu_ku = ju_info["墓庫"]

        # 檢查是否三神齊全
        if chang_sheng in zhi_set and di_wang in zhi_set and mu_ku in zhi_set:
            # 檢查是否有化氣天干
            can_hua = False
            if tian_gan_list:
                hua_qi_gans = SAN_HE_JU_HUA_QI_TIAN_GAN.get(ju_name, [])
                can_hua = any(gan in tian_gan_list for gan in hua_qi_gans)

            results.append({
                "局": ju_name,
                "組合": f"{chang_sheng}{di_wang}{mu_ku}",
                "狀態": "可化" if can_hua else "合局",
            })

    return results


def calculate_zhi_san_hui_fang(zhi_list: list) -> list:
    """
    計算地支三會方

    Args:
        zhi_list: 地支列表

    Returns:
        三會方列表
    """
    results = []
    zhi_set = set(zhi_list)

    for fang_name, fang_zhis in ZHI_SAN_HUI_FANG.items():
        if all(zhi in zhi_set for zhi in fang_zhis):
            results.append({
                "局": fang_name,
                "組合": "".join(fang_zhis),
                "狀態": "會方",
            })

    return results


def calculate_zhi_gong_ju(zhi_list: list) -> list:
    """
    計算地支拱局（又稱閘局）

    Args:
        zhi_list: 地支列表

    Returns:
        拱局列表
    """
    results = []
    zhi_set = set(zhi_list)

    for gong_name, gong_info in ZHI_GONG_JU.items():
        chang_sheng = gong_info["長生"]
        mu_ku = gong_info["墓庫"]
        zhong_shen = gong_info["中神"]

        # 拱局：有長生和墓庫，但缺乏中神
        if chang_sheng in zhi_set and mu_ku in zhi_set and zhong_shen not in zhi_set:
            results.append({
                "局": gong_name,
                "組合": f"{chang_sheng}{mu_ku}",
                "中神": zhong_shen,
                "狀態": "拱局",
            })

    return results


def calculate_zhi_zha_he(zhi_list: list) -> list:
    """
    計算地支閘局（拱局的別稱）

    Args:
        zhi_list: 地支列表

    Returns:
        閘局列表
    """
    return calculate_zhi_gong_ju(zhi_list)


def calculate_zhi_ban_san_he(zhi_list: list) -> list:
    """
    計算地支半三合局

    Args:
        zhi_list: 地支列表

    Returns:
        半三合局列表
    """
    results = []
    zhi_set = set(zhi_list)

    for ban_name, ban_info in ZHI_BAN_SAN_HE.items():
        required_zhis = set(ban_info.values())
        if all(zhi in zhi_set for zhi in required_zhis):
            results.append({
                "局": ban_name,
                "組合": "".join(ban_info.values()),
                "狀態": "半合",
            })

    return results


def calculate_zhi_xing(zhi_list: list) -> list:
    """
    計算地支三刑

    Args:
        zhi_list: 地支列表

    Returns:
        三刑列表
    """
    results = []
    zhi_set = set(zhi_list)
    zhi_count = {zhi: zhi_list.count(zhi) for zhi in zhi_set}
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    # 無禮之刑（子卯）
    if "子" in zhi_set and "卯" in zhi_set:
        # 找出子卯所在柱位
        zi_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "子"]
        mao_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "卯"]
        position = f"{','.join(zi_positions)}~{','.join(mao_positions)}"
        results.append({"刑": "子卯無禮之刑", "類": "相刑", "位置": position})

    # 恃勢之刑（丑戌未三刑）
    if "丑" in zhi_set and "戌" in zhi_set and "未" in zhi_set:
        chou_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "丑"]
        xu_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "戌"]
        wei_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "未"]
        position = f"{','.join(chou_positions)}~{','.join(xu_positions)}~{','.join(wei_positions)}"
        results.append({"刑": "丑戌未恃勢之刑", "類": "三刑", "位置": position})

    # 無恩之刑（寅巳申三刑）
    if "寅" in zhi_set and "巳" in zhi_set and "申" in zhi_set:
        yin_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "寅"]
        si_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "巳"]
        shen_positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == "申"]
        position = f"{','.join(yin_positions)}~{','.join(si_positions)}~{','.join(shen_positions)}"
        results.append({"刑": "寅巳申無恩之刑", "類": "三刑", "位置": position})

    # 自刑（辰辰、午午、酉酉、亥亥）
    for zhi, count in zhi_count.items():
        if zhi in ["辰", "午", "酉", "亥"] and count >= 2:
            # 找出該地支出現的柱位
            positions = [pillar_names[i] for i, z in enumerate(zhi_list) if z == zhi]
            position = "~".join(positions)
            results.append({"刑": f"{zhi}{zhi}自刑", "類": "自刑", "位置": position})

    return results


def calculate_zhi_chuan(zhi_list: list) -> list:
    """
    計算地支穿（害）

    Args:
        zhi_list: 地支列表

    Returns:
        穿列表
    """
    results = []
    processed = set()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    for i, zhi1 in enumerate(zhi_list):
        for j, zhi2 in enumerate(zhi_list):
            if i >= j:
                continue
            pair = tuple(sorted([zhi1, zhi2]))
            if pair in processed:
                continue

            for c1, c2 in ZHI_CHUAN:
                if (zhi1 == c1 and zhi2 == c2) or (zhi1 == c2 and zhi2 == c1):
                    processed.add(pair)
                    results.append({
                        "穿": f"{zhi1}{zhi2}穿",
                        "位置": f"{pillar_names[i]}~{pillar_names[j]}",
                    })

    return results


def calculate_zhi_po(zhi_list: list) -> list:
    """
    計算地支破

    Args:
        zhi_list: 地支列表

    Returns:
        破列表
    """
    results = []
    processed = set()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    for i, zhi1 in enumerate(zhi_list):
        for j, zhi2 in enumerate(zhi_list):
            if i >= j:
                continue
            pair = tuple(sorted([zhi1, zhi2]))
            if pair in processed:
                continue

            for c1, c2 in ZHI_PO:
                if (zhi1 == c1 and zhi2 == c2) or (zhi1 == c2 and zhi2 == c1):
                    processed.add(pair)
                    results.append({
                        "破": f"{zhi1}{zhi2}破",
                        "位置": f"{pillar_names[i]}~{pillar_names[j]}",
                    })

    return results


def calculate_relations(ba_zi: str) -> dict:
    """
    計算地支所有關係

    Args:
        ba_zi: 八字字符串

    Returns:
        地支關係字典
    """
    ba_zi_parts = ba_zi.split()
    zhi_list = [p[1] for p in ba_zi_parts]
    gan_list = [p[0] for p in ba_zi_parts]

    return {
        "六合": calculate_zhi_liu_he(zhi_list, gan_list),
        "六沖": calculate_zhi_liu_chong(zhi_list),
        "三合局": calculate_zhi_san_he_ju(zhi_list, gan_list),
        "三會方": calculate_zhi_san_hui_fang(zhi_list),
        "拱局": calculate_zhi_gong_ju(zhi_list),
        "半合局": calculate_zhi_ban_san_he(zhi_list),
        "刑": calculate_zhi_xing(zhi_list),
        "穿": calculate_zhi_chuan(zhi_list),
        "破": calculate_zhi_po(zhi_list),
    }
