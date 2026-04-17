"""
六十甲子體象論模塊 - 計算旬判斷和六親類化
"""

from bazi.core.constants import (
    TIAN_GAN_WU_XING,
    TIAN_GAN_YIN_YANG,
    TIAN_GAN_YANG,
    TIAN_GAN_YIN,
    WU_XING_SHENG,
    WU_XING_KE,
    LIU_SHI_JIA_ZI,
)


# 六十甲子順序
LIU_SHI_JIA_ZI_ORDER = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]


def get_xun(day_pillar: str) -> tuple:
    """
    取得日柱所屬的旬

    Args:
        day_pillar: 日柱干支

    Returns:
        (旬名, 旬成員列表)
    """
    idx = LIU_SHI_JIA_ZI_ORDER.index(day_pillar)
    xun_start = (idx // 10) * 10
    xun_names = ["甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅"]
    xun_name = xun_names[xun_start // 10]
    return xun_name, LIU_SHI_JIA_ZI_ORDER[xun_start:xun_start + 10]


def get_liu_qin_xian_tian(member_gan: str, day_gan: str, is_male: bool) -> str:
    """
    根據六十甲子體象論計算六親（以先天為準）

    男命：不論日干陰陽，一律以陽天干為先天
    女命：不論日干陰陽，一律以陰天干為先天

    Args:
        member_gan: 旬成員的天干
        day_gan: 日主天干
        is_male: 是否為男命

    Returns:
        六親名稱，如 "妻子"、"母親" 等，無則返回 None
    """
    member_wuxing = TIAN_GAN_WU_XING[member_gan]
    member_yinyang = TIAN_GAN_YIN_YANG[member_gan]

    # 先天天干：男命用陽，女命用陰
    xian_tian_gan = TIAN_GAN_YANG[day_gan] if is_male else TIAN_GAN_YIN[day_gan]
    xian_tian_wuxing = TIAN_GAN_WU_XING[xian_tian_gan]
    xian_tian_yinyang = TIAN_GAN_YIN_YANG[xian_tian_gan]

    if is_male:
        # 男命（以陽為先天）
        # 妻：先天我剋且不同陰陽（陰陽相配）
        if WU_XING_KE.get(xian_tian_wuxing) == member_wuxing and member_yinyang != xian_tian_yinyang:
            return "妻子"
        # 母：生先天我且為陰
        if WU_XING_SHENG.get(member_wuxing) == xian_tian_wuxing and member_yinyang == "陰":
            return "母親"
        # 父：陽且剋母
        # 母是生我者（印），父是剋母者（財）
        ke_mu_wuxing = WU_XING_KE.get(xian_tian_wuxing)  # 剋我者
        if ke_mu_wuxing:
            for tg, wx in TIAN_GAN_WU_XING.items():
                if wx == ke_mu_wuxing and TIAN_GAN_YIN_YANG[tg] == "陽":
                    if tg == member_gan:
                        return "父親"
        # 子：剋先天我且為陽（七殺）
        if WU_XING_KE.get(member_wuxing) == xian_tian_wuxing and member_yinyang == "陽":
            return "兒子"
        # 女：剋先天我且為陰（正官）
        if WU_XING_KE.get(member_wuxing) == xian_tian_wuxing and member_yinyang == "陰":
            return "女兒"
        # 兄弟：同五行且為陽（先天五行）
        if member_wuxing == xian_tian_wuxing and member_yinyang == "陽" and member_gan != xian_tian_gan:
            return "兄弟"
        # 姐妹：同五行且為陰（先天五行）
        if member_wuxing == xian_tian_wuxing and member_yinyang == "陰" and member_gan != xian_tian_gan:
            return "姐妹"
        # 女婿：女兒的丈夫 = 我生且為陽（食神）
        if WU_XING_SHENG.get(xian_tian_wuxing) == member_wuxing and member_yinyang == "陽":
            return "女婿"
        # 兒媳：兒子的妻子 = 我生且為陰（傷官）
        if WU_XING_SHENG.get(xian_tian_wuxing) == member_wuxing and member_yinyang == "陰":
            return "兒媳"
    else:
        # 女命（以陰為先天）
        # 夫：剋先天我且不同陰陽（陰陽相配）
        if WU_XING_KE.get(member_wuxing) == xian_tian_wuxing and member_yinyang != xian_tian_yinyang:
            return "丈夫"
        # 母：生先天我且為陰
        if WU_XING_SHENG.get(member_wuxing) == xian_tian_wuxing and member_yinyang == "陰":
            return "母親"
        # 父：陽且剋母（與男命相同）
        ke_mu_wuxing = WU_XING_KE.get(xian_tian_wuxing)  # 剋我者
        if ke_mu_wuxing:
            for tg, wx in TIAN_GAN_WU_XING.items():
                if wx == ke_mu_wuxing and TIAN_GAN_YIN_YANG[tg] == "陽":
                    if tg == member_gan:
                        return "父親"
        # 女婿：生先天我且為陽（印）
        if WU_XING_SHENG.get(member_wuxing) == xian_tian_wuxing and member_yinyang == "陽":
            return "女婿"
        # 兒媳：剋先天我且為陰（官）
        if WU_XING_KE.get(member_wuxing) == xian_tian_wuxing and member_yinyang == "陰":
            return "兒媳"
        # 兄弟：同五行且為陽（先天五行）
        if member_wuxing == xian_tian_wuxing and member_yinyang == "陽" and member_gan != xian_tian_gan:
            return "兄弟"
        # 姐妹：同五行且為陰（先天五行）
        if member_wuxing == xian_tian_wuxing and member_yinyang == "陰" and member_gan != xian_tian_gan:
            return "姐妹"
        # 兒子：生先天我且為陽（食神）
        if WU_XING_SHENG.get(xian_tian_wuxing) == member_wuxing and member_yinyang == "陽":
            return "兒子"
        # 女兒：生先天我且為陰（傷官）
        if WU_XING_SHENG.get(xian_tian_wuxing) == member_wuxing and member_yinyang == "陰":
            return "女兒"

    return None


def calculate_liu_shi_jia_zi(ba_zi: str, gender: str) -> dict:
    """
    計算六十甲子體象論

    男命：不分陰陽都以陽來運行
    女命：不分陰陽都以陰來運行

    Args:
        ba_zi: 八字字符串
        gender: 性別（"男" 或 "女"）

    Returns:
        {
            "日柱": 日柱干支,
            "性別": 性別,
            "先天": 先天天干,
            "所屬旬": 旬名,
            "旬成員": 旬成員列表,
            "四柱同旬": 四柱同旬信息,
            "六親類化": 六親類化列表,
        }
    """
    ba_zi_parts = ba_zi.split()
    day_pillar = ba_zi_parts[2]  # 日柱
    day_gan = day_pillar[0]
    is_male = gender == "男"

    # 取得日柱所屬旬
    xun_name, xun_members = get_xun(day_pillar)

    # 找出四柱中同旬的柱
    same_xun = []
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]
    for i, pillar in enumerate(ba_zi_parts):
        in_xun = pillar in xun_members
        same_xun.append({
            "柱": pillar_names[i],
            "干支": pillar,
            "同旬": in_xun
        })

    # 計算六親類化（根據六十甲子體象論）
    # 先天天干（男命用陽天干，女命用陰天干）
    xian_tian_gan = TIAN_GAN_YANG[day_gan] if is_male else day_gan
    liu_qin = []
    for member in xun_members:
        member_gan = member[0]
        lq = get_liu_qin_xian_tian(member_gan, day_gan, is_male)
        if lq:
            liu_qin.append({
                "干支": member,
                "六親": lq,
                "天干": member_gan,
                "五行": TIAN_GAN_WU_XING[member_gan],
                "陰陽": TIAN_GAN_YIN_YANG[member_gan]
            })

    return {
        "日柱": day_pillar,
        "性別": gender,
        "先天": xian_tian_gan + "（" + ("男" if is_male else "女") + "）",
        "所屬旬": xun_name + "旬",
        "旬成員": xun_members,
        "四柱同旬": same_xun,
        "六親類化": liu_qin,
    }