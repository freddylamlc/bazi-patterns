"""
干支生剋計算模塊 - 計算天干生剋和同柱干支關係
"""

from bazi.core.constants import (
    TIAN_GAN_WU_XING,
    TIAN_GAN_YIN_YANG,
    ZHI_WU_XING,
    ZHI_YIN_YANG,
    WU_XING_SHENG,
    WU_XING_KE,
)


def calculate_ganzhi_shengke(ba_zi: str) -> dict:
    """
    計算干支生剋

    Args:
        ba_zi: 八字字符串 "甲子 乙丑 丙寅 丁卯"

    Returns:
        {
            "天干生剋": [...],  # 天干之間的生剋
            "同柱干支": [...],  # 同柱干支關係 (蓋頭、截腳、洩氣、得支支持)
        }
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    results = {
        "天干生剋": [],
        "同柱干支": [],
    }

    # 提取天干和地支
    tian_gan_list = [p[0] for p in ba_zi_parts]
    zhi_list = [p[1] for p in ba_zi_parts]

    # 1. 檢查天干之間的生剋 (年-月, 年-日, 年-時, 月-日, 月-時, 日-時)
    pairs = [
        ("年柱", "月柱", tian_gan_list[0], tian_gan_list[1]),
        ("年柱", "日柱", tian_gan_list[0], tian_gan_list[2]),
        ("年柱", "時柱", tian_gan_list[0], tian_gan_list[3]),
        ("月柱", "日柱", tian_gan_list[1], tian_gan_list[2]),
        ("月柱", "時柱", tian_gan_list[1], tian_gan_list[3]),
        ("日柱", "時柱", tian_gan_list[2], tian_gan_list[3]),
    ]

    for p1, p2, tg1, tg2 in pairs:
        wuxing1 = TIAN_GAN_WU_XING[tg1]
        wuxing2 = TIAN_GAN_WU_XING[tg2]
        yinyang1 = TIAN_GAN_YIN_YANG[tg1]
        yinyang2 = TIAN_GAN_YIN_YANG[tg2]

        # 判斷生剋關係
        # 異性相生、同性相剋
        if yinyang1 != yinyang2:  # 異性
            # 檢查是否相生
            if WU_XING_SHENG.get(wuxing1) == wuxing2:
                # tg1 生 tg2
                results["天干生剋"].append({
                    "關係": f"{tg1}生{tg2}",
                    "位置": f"{p1}與{p2}",
                    "五行": f"{wuxing1}生{wuxing2}",
                    "備註": "異性相生（盡生）"
                })
            elif WU_XING_KE.get(wuxing1) == wuxing2:
                # tg1 剋 tg2
                results["天干生剋"].append({
                    "關係": f"{tg1}剋{tg2}",
                    "位置": f"{p1}與{p2}",
                    "五行": f"{wuxing1}剋{wuxing2}",
                    "備註": "異性相剋（不盡剋）"
                })
        else:  # 同性
            # 同性相剋必盡剋
            if WU_XING_KE.get(wuxing1) == wuxing2:
                results["天干生剋"].append({
                    "關係": f"{tg1}剋{tg2}",
                    "位置": f"{p1}與{p2}",
                    "五行": f"{wuxing1}剋{wuxing2}",
                    "備註": "同性相剋（盡剋）"
                })
            elif WU_XING_SHENG.get(wuxing1) == wuxing2:
                # 同性相生不盡生
                results["天干生剋"].append({
                    "關係": f"{tg1}生{tg2}",
                    "位置": f"{p1}與{p2}",
                    "五行": f"{wuxing1}生{wuxing2}",
                    "備註": "同性相生（不盡生）"
                })

    # 2. 檢查同柱干支關係 (蓋頭、截腳、洩氣、得支支持)
    for i, (pillar, zhi) in enumerate(zip(ba_zi_parts, zhi_list)):
        tg = pillar[0]  # 天干
        zhi = pillar[1]  # 地支

        tg_wuxing = TIAN_GAN_WU_XING[tg]
        zhi_wuxing = ZHI_WU_XING[zhi]
        tg_yinyang = TIAN_GAN_YIN_YANG[tg]
        zhi_yinyang = ZHI_YIN_YANG[zhi]

        # 支被干剋 = 蓋頭 (天干剋地支)
        if WU_XING_KE.get(tg_wuxing) == zhi_wuxing:
            if tg_yinyang == zhi_yinyang:
                # 蓋頭 - 陰陽相同，盡剋
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"蓋頭（{tg}剋{zhi}）",
                    "五行": f"{tg_wuxing}剋{zhi_wuxing}",
                    "備註": "同性相剋（盡剋）"
                })
            else:
                # 蓋頭 - 陰陽不同，不盡剋
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"蓋頭（{tg}剋{zhi}）",
                    "五行": f"{tg_wuxing}剋{zhi_wuxing}",
                    "備註": "異性相剋（不盡剋）"
                })

        # 干被支剋 = 截腳 (地支剋天干)
        elif WU_XING_KE.get(zhi_wuxing) == tg_wuxing:
            if tg_yinyang == zhi_yinyang:
                # 截腳 - 陰陽相同，盡剋
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"截腳（{zhi}剋{tg}）",
                    "五行": f"{zhi_wuxing}剋{tg_wuxing}",
                    "備註": "同性相剋（盡剋）"
                })
            else:
                # 截腳 - 陰陽不同，不盡剋
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"截腳（{zhi}剋{tg}）",
                    "五行": f"{zhi_wuxing}剋{tg_wuxing}",
                    "備註": "異性相剋（不盡剋）"
                })

        # 干生支 = 洩氣
        elif WU_XING_SHENG.get(tg_wuxing) == zhi_wuxing:
            if tg_yinyang == zhi_yinyang:
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"干洩氣於支（{tg}生{zhi}）",
                    "五行": f"{tg_wuxing}生{zhi_wuxing}",
                    "備註": "同性相生（不盡生）"
                })
            else:
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"干洩氣於支（{tg}生{zhi}）",
                    "五行": f"{tg_wuxing}生{zhi_wuxing}",
                    "備註": "異性相生（盡生）"
                })

        # 支生干 = 得支支持
        elif WU_XING_SHENG.get(zhi_wuxing) == tg_wuxing:
            if tg_yinyang == zhi_yinyang:
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"支生干（{zhi}生{tg}）",
                    "五行": f"{zhi_wuxing}生{tg_wuxing}",
                    "備註": "同性相生（不盡生）"
                })
            else:
                results["同柱干支"].append({
                    "柱": pillar_names[i],
                    "干支": pillar,
                    "關係": f"支生干（{zhi}生{tg}）",
                    "五行": f"{zhi_wuxing}生{tg_wuxing}",
                    "備註": "異性相生（盡生）"
                })

    return results


def calculate_fan_sheng_ke(ba_zi: str) -> dict:
    """
    計算反生為剋和反剋為生

    規則：
    - 反生為剋：A生B，但B太旺（得根得令），A的生成為負擔
      如：水生木，但木太旺，水反被木吸乾
    - 反剋為生：A剋B，但B太弱，A的剋制反而幫助B
      如：金剋木，但木太弱，適度修剪反而有利

    Args:
        ba_zi: 八字字符串

    Returns:
        反生為剋/反剋為生的分析結果
    """
    from bazi.core.constants import TIAN_GAN_DE_GEN, TIAN_GAN_DE_LING

    ba_zi_parts = ba_zi.split()
    tian_gan_list = [p[0] for p in ba_zi_parts]
    zhi_list = [p[1] for p in ba_zi_parts]
    month_zhi = zhi_list[1]

    results = {"反生為剋": [], "反剋為生": []}

    def count_gen(gan: str) -> int:
        roots = TIAN_GAN_DE_GEN.get(gan, [])
        return sum(1 for z in zhi_list if z in roots)

    def is_de_ling(gan: str) -> bool:
        ling_zhis = TIAN_GAN_DE_LING.get(gan, [])
        return month_zhi in ling_zhis

    pairs = [
        ("年柱", "月柱", 0, 1), ("年柱", "日柱", 0, 2), ("年柱", "時柱", 0, 3),
        ("月柱", "日柱", 1, 2), ("月柱", "時柱", 1, 3), ("日柱", "時柱", 2, 3),
    ]

    for p1_name, p2_name, i, j in pairs:
        g1, g2 = tian_gan_list[i], tian_gan_list[j]
        w1, w2 = TIAN_GAN_WU_XING[g1], TIAN_GAN_WU_XING[g2]

        # g1 生 g2（標準相生）
        if WU_XING_SHENG.get(w1) == w2:
            g2_gen = count_gen(g2)
            g2_ling = is_de_ling(g2)
            if g2_gen >= 3 or (g2_gen >= 2 and g2_ling):
                results["反生為剋"].append({
                    "天干": f"{g1}→{g2}",
                    "位置": f"{p1_name}~{p2_name}",
                    "說明": f"{g1}({w1})生{g2}({w2})，但{g2}太旺，{w1}反被吸乾",
                    "類型": "反生為剋"
                })

        # g2 生 g1（反向檢查）
        if WU_XING_SHENG.get(w2) == w1:
            g1_gen = count_gen(g1)
            g1_ling = is_de_ling(g1)
            if g1_gen >= 3 or (g1_gen >= 2 and g1_ling):
                results["反生為剋"].append({
                    "天干": f"{g2}→{g1}",
                    "位置": f"{p2_name}~{p1_name}",
                    "說明": f"{g2}({w2})生{g1}({w1})，但{g1}太旺，{w2}反被吸乾",
                    "類型": "反生為剋"
                })

        # g1 剋 g2（標準相剋）
        if WU_XING_KE.get(w1) == w2:
            g2_gen = count_gen(g2)
            g2_ling = is_de_ling(g2)
            if g2_gen == 0 and not g2_ling:
                results["反剋為生"].append({
                    "天干": f"{g1}→{g2}",
                    "位置": f"{p1_name}~{p2_name}",
                    "說明": f"{g1}({w1})剋{g2}({w2})，但{g2}太弱無根，適度剋制反有利",
                    "類型": "反剋為生"
                })

        # g2 剋 g1（反向檢查）
        if WU_XING_KE.get(w2) == w1:
            g1_gen = count_gen(g1)
            g1_ling = is_de_ling(g1)
            if g1_gen == 0 and not g1_ling:
                results["反剋為生"].append({
                    "天干": f"{g2}→{g1}",
                    "位置": f"{p2_name}~{p1_name}",
                    "說明": f"{g2}({w2})剋{g1}({w1})，但{g1}太弱無根，適度剋制反有利",
                    "類型": "反剋為生"
                })

    return results