"""
大運流年分析模塊

根據《歲運真機》邏輯實現：
- 大運判斷（干支陰陽、生剋、蓋頭截腳、空亡、十神取向）
- 流年判斷（字碰字、天干碰天干、地支碰地支）
- 用神/忌神分析
"""

from bazi.core.constants import (
    TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG, ZHI_WU_XING, ZHI_YIN_YANG,
    WU_XING_KE, WU_XING_SHENG, ZHI_LIU_CHONG, ZHI_XING, ZHI_CHUAN, ZHI_PO,
    ZHI_CANG_GAN, TIAN_GAN_ZHANG_SHENG, GAN_ZHI_KONG_WANG, TIAN_GAN_WU_HE,
)
from bazi.calculations.shishen import _calculate_shi_shen as get_shi_shen

# 別名（兼容舊代碼）
TianGanWuXing = TIAN_GAN_WU_XING
TianGanYinYang = TIAN_GAN_YIN_YANG
ZhiWuXing = ZHI_WU_XING
ZhiYinYang = ZHI_YIN_YANG
WuXingKe = WU_XING_KE
WuXingSheng = WU_XING_SHENG
ZhiLiuChong = ZHI_LIU_CHONG
ZhiXing = ZHI_XING
ZhiChuan = ZHI_CHUAN
ZhiPo = ZHI_PO
ZhiCangGan = ZHI_CANG_GAN
TianGanZhangSheng = TIAN_GAN_ZHANG_SHENG
GanZhiKongWang = GAN_ZHI_KONG_WANG
TianGanWuHe = TIAN_GAN_WU_HE

# 歲運格局新增導入
from bazi.core.constants import WU_XING_KE, WU_XING_SHENG, ZHI_LIU_CHONG


def check_sui_yun_damaged(target_zhi: str, sui_yun_zhi_list: list) -> list:
    """檢查命局地支是否被歲運地支沖、刑、穿、破"""
    damaged_by = []
    for other_zhi in sui_yun_zhi_list:
        if other_zhi == target_zhi:
            continue
        for c1, c2 in ZhiLiuChong:
            if (target_zhi == c1 and other_zhi == c2) or (target_zhi == c2 and other_zhi == c1):
                damaged_by.append(f"{other_zhi}沖")
                break
        if target_zhi + other_zhi in ZhiXing or other_zhi + target_zhi in ZhiXing:
            damaged_by.append(f"{other_zhi}刑")
        for c1, c2 in ZhiChuan:
            if (target_zhi == c1 and other_zhi == c2) or (target_zhi == c2 and other_zhi == c1):
                damaged_by.append(f"{other_zhi}穿")
                break
        for c1, c2 in ZhiPo:
            if (target_zhi == c1 and other_zhi == c2) or (target_zhi == c2 and other_zhi == c1):
                damaged_by.append(f"{other_zhi}破")
                break
    return damaged_by


def check_special_gan_condition(day_gan: str, target_gan: str) -> tuple:
    """
    檢查特殊天干條件
    陽日干見正財天干，陰日干見正官天干，不論生剋
    """
    yang_day_zhengcai = {"甲": "己", "丙": "辛", "戊": "癸", "庚": "乙", "壬": "丁"}
    yin_day_zhengguan = {"乙": "庚", "丁": "壬", "己": "甲", "辛": "丙", "癸": "戊"}

    day_gan_yinyang = TianGanYinYang.get(day_gan, "")

    if day_gan_yinyang == "陽":
        zhengcai = yang_day_zhengcai.get(day_gan, "")
        if target_gan == zhengcai:
            return True, f"陽日干見正財（{day_gan}見{zhengcai}）"

    if day_gan_yinyang == "陰":
        zhengguan = yin_day_zhengguan.get(day_gan, "")
        if target_gan == zhengguan:
            return True, f"陰日干見正官（{day_gan}見{zhengguan}）"

    return False, ""


def calculate_dayun_pan_duan(ba_zi: str, ge_ju: dict, detailed_dayun: dict,
                             gender: str) -> dict:
    """
    計算大運判斷

    Args:
        ba_zi: 八字字符串
        ge_ju: 格局判斷字典
        detailed_dayun: 詳細大運信息
        gender: 性別

    Returns:
        大運判斷字典
    """
    ba_zi_parts = ba_zi.split()
    day_gan = ba_zi_parts[2][0]
    day_zhi = ba_zi_parts[2][1]
    day_gan_yinyang = TianGanYinYang[day_gan]
    day_zhi_yinyang = ZhiYinYang[day_zhi]
    day_gan_wuxing = TianGanWuXing[day_gan]
    day_zhi_wuxing = ZhiWuXing[day_zhi]

    # 獲取格局信息
    yong_shen = ge_ju.get("用神", "")
    xiang_shen = ge_ju.get("相神", [])
    yong_shen_wuxing = TianGanWuXing.get(yong_shen, "") if yong_shen else ""

    # 檢查原局是否有兩種相神並存（凶神逆用）
    ge_name = ge_ju.get("格局", "").replace("格", "")
    ji_shens = ["正官", "正印", "偏印", "正財", "偏財", "食神"]
    xiong_shens = ["七殺", "傷官", "比肩", "劫財"]
    is_auspicious = ge_name in ji_shens
    is_xiong_shen_ge = ge_name in xiong_shens
    has_two_xiang_shen = len(xiang_shen) >= 2 and is_xiong_shen_ge

    # 從 ge_ju 提取喜神忌神
    xishen_gans = ge_ju.get("喜神", [])
    xishen_wuxing_list = ge_ju.get("喜神五行", [])
    jishen_gans = ge_ju.get("忌神", [])
    jishen_wuxing = ge_ju.get("忌神五行", [])

    # 獲取十個大運
    dayuns = detailed_dayun.get("十個大運", [])

    dayun_analysis = []
    for dayun in dayuns:
        dy_gan = dayun["大運干"]
        dy_zhi = dayun["大運支"]
        dy_gan_yinyang = TianGanYinYang[dy_gan]
        dy_zhi_yinyang = ZhiYinYang[dy_zhi]
        dy_gan_wuxing = TianGanWuXing[dy_gan]
        dy_zhi_wuxing = ZhiWuXing[dy_zhi]

        # 1. 干支陰陽分判斷
        gan_yinyang_tong = "同陰陽" if dy_gan_yinyang == day_gan_yinyang else "不同陰陽"
        zhi_yinyang_tong = "同陰陽" if dy_zhi_yinyang == day_zhi_yinyang else "不同陰陽"

        # 2. 干支生剋判斷
        is_special, special_note = check_special_gan_condition(day_gan, dy_gan)

        dy_gan_sheng_ke_day = ""
        if is_special:
            dy_gan_sheng_ke_day = f"特殊條件（{special_note}，不論生剋）"
        elif WU_XING_SHENG.get(dy_gan_wuxing) == day_gan_wuxing:
            dy_gan_sheng_ke_day = "相生"
        elif WU_XING_SHENG.get(day_gan_wuxing) == dy_gan_wuxing:
            dy_gan_sheng_ke_day = "被生"
        elif WU_XING_KE.get(dy_gan_wuxing) == day_gan_wuxing:
            dy_gan_sheng_ke_day = "相剋"
        elif WU_XING_KE.get(day_gan_wuxing) == dy_gan_wuxing:
            dy_gan_sheng_ke_day = "被剋"

        dy_zhi_sheng_ke_day = ""
        if WU_XING_SHENG.get(dy_zhi_wuxing) == day_zhi_wuxing:
            dy_zhi_sheng_ke_day = "相生"
        elif WU_XING_SHENG.get(day_zhi_wuxing) == dy_zhi_wuxing:
            dy_zhi_sheng_ke_day = "被生"
        elif WU_XING_KE.get(dy_zhi_wuxing) == day_zhi_wuxing:
            dy_zhi_sheng_ke_day = "相剋"
        elif WU_XING_KE.get(day_zhi_wuxing) == dy_zhi_wuxing:
            dy_zhi_sheng_ke_day = "被剋"

        # 3. 蓋頭截腳判斷
        gai_tou = False
        jie_jiao = False
        if not is_special and dy_gan_wuxing == WU_XING_KE.get(day_gan_wuxing):
            gai_tou = True
        if dy_zhi_wuxing == WU_XING_KE.get(day_zhi_wuxing):
            jie_jiao = True

        # 4. 空亡判斷
        dy_kong_wang = GanZhiKongWang.get(dy_gan + dy_zhi, (None, None))
        dy_gan_luo_kong = "落空亡" if day_gan in dy_kong_wang else ""
        dy_zhi_luo_kong = "落空亡" if day_zhi in dy_kong_wang else ""

        # 5. 十神取向
        dy_gan_shishen = get_shi_shen(dy_gan, dy_gan_wuxing, dy_gan_yinyang,
                                       day_gan, day_gan_wuxing, day_gan_yinyang)
        dy_zhi_benqi = ZhiCangGan.get(dy_zhi, {}).get("主氣", dy_zhi)
        dy_zhi_benqi_wuxing = TianGanWuXing.get(dy_zhi_benqi, "")
        dy_zhi_benqi_yinyang = TianGanYinYang.get(dy_zhi_benqi, "陽")
        dy_zhi_shishen = get_shi_shen(dy_zhi_benqi, dy_zhi_benqi_wuxing, dy_zhi_benqi_yinyang,
                                       day_gan, day_gan_wuxing, day_gan_yinyang)

        # 6. 用神/喜神/忌神分析
        yong_shen_dao_wei = ""
        xishen_dao_wei = ""
        ji_shen_dao_wei = ""
        ge_ju_ying_xiang = "平穩"

        if is_auspicious and yong_shen:
            if dy_gan_wuxing == yong_shen_wuxing:
                yong_shen_dao_wei = f"用神{yong_shen}到位（天干）"
                ge_ju_ying_xiang = "用神到位 - 格局增強"
            if dy_zhi_wuxing == yong_shen_wuxing:
                yong_shen_dao_wei += f"、" if yong_shen_dao_wei else f"用神{yong_shen}到位（地支）"
                if not ge_ju_ying_xiang.startswith("用神"):
                    ge_ju_ying_xiang = "用神到位 - 格局增強"

        if dy_gan in xishen_gans:
            xishen_dao_wei = f"喜神{dy_gan}到位（天干）"
            if not ge_ju_ying_xiang.startswith("用神"):
                ge_ju_ying_xiang = "喜神到位 - 吉運"
        if dy_zhi in xishen_gans:
            xishen_dao_wei += f"、" if xishen_dao_wei else f"喜神{dy_zhi}到位（地支）"
            if not ge_ju_ying_xiang.startswith("用神"):
                ge_ju_ying_xiang = "喜神到位 - 吉運"

        if dy_gan in jishen_gans:
            ji_shen_dao_wei = f"忌神{dy_gan}到位（天干）"
            ge_ju_ying_xiang = "忌神到位 - 格局受損"
        if dy_zhi_wuxing in jishen_wuxing:
            ji_shen_dao_wei += f"、" if ji_shen_dao_wei else f"忌神{dy_zhi}到位（地支）"
            if not ge_ju_ying_xiang.startswith("忌神"):
                ge_ju_ying_xiang = "忌神到位 - 格局受損"

        # 7. 吉凶總結
        if ge_ju_ying_xiang.startswith("用神"):
            jixing = "大吉"
        elif ge_ju_ying_xiang.startswith("喜神"):
            jixing = "吉"
        elif ge_ju_ying_xiang.startswith("忌神"):
            jixing = "凶"
        else:
            jixing = "平"

        # 8. 歲運對相神/忌神的影響
        xiang_shen_ke_zhi = []
        ji_shen_ke_zhi = []
        genqi_damaged = []

        mingju_zhi_list = [p[1] for p in ba_zi_parts]
        for mzhi in mingju_zhi_list:
            damaged = check_sui_yun_damaged(mzhi, [dy_zhi])
            if damaged:
                genqi_damaged.append(f"{mzhi}被{','.join(damaged)}")

        if genqi_damaged:
            ge_ju_ying_xiang += f"，根氣受損：{','.join(genqi_damaged)}"

        # 綜合判斷
        sui_yun_ying_xiang = []
        if xiang_shen_ke_zhi:
            sui_yun_ying_xiang.append(f"相神受剋：{','.join(xiang_shen_ke_zhi)}")
        if ji_shen_ke_zhi:
            sui_yun_ying_xiang.append(f"忌神受制：{','.join(ji_shen_ke_zhi)}")
        if genqi_damaged:
            sui_yun_ying_xiang.append(f"根氣受損：{','.join(genqi_damaged)}")

        if xiang_shen_ke_zhi and jixing in ["大吉", "吉"]:
            jixing = "吉中帶凶" if jixing == "大吉" else "平"
            ge_ju_ying_xiang += "，相神受剋，吉中帶凶"
        if ji_shen_ke_zhi and jixing == "凶":
            jixing = "凶中有救"
            ge_ju_ying_xiang += "，忌神受制，凶中有救"

        # 原局有兩種相神並存時的調整
        if has_two_xiang_shen:
            ge_chengbai = ge_ju.get("成敗", "")
            is_po_ge = "破格" in ge_chengbai or ge_ju.get("凶神破格", False)

            if is_po_ge:
                jixing = "凶"
                ge_ju_ying_xiang += "，原局破格，大運無救應"
            elif jixing in ["大吉", "吉"]:
                jixing = "吉中帶凶"
                ge_ju_ying_xiang += "，原局兩種相神並存，待流年判斷"
            elif jixing == "平":
                jixing = "凶"
                ge_ju_ying_xiang += "，原局兩種相神並存，無救應"

        # 評分
        score_map = {"大吉": 90, "吉": 70, "凶": 30, "大凶": 10, "平": 50, "吉中帶凶": 60, "凶中有救": 40}
        score = score_map.get(jixing, 50)

        # 計算大運地支藏干和十二長生
        dy_zhi_cang_gan = ZhiCangGan.get(dy_zhi, {})
        dy_zhi_benqi = dy_zhi_cang_gan.get("主氣", dy_zhi)
        dy_zhi_zhongqi = dy_zhi_cang_gan.get("中氣")
        dy_zhi_yuqi = dy_zhi_cang_gan.get("餘氣")

        dy_benqi_wuxing = TianGanWuXing.get(dy_zhi_benqi, "")
        dy_benqi_yinyang = TianGanYinYang.get(dy_zhi_benqi, "陽")
        dy_benqi_shishen = get_shi_shen(dy_zhi_benqi, dy_benqi_wuxing, dy_benqi_yinyang,
                                         day_gan, day_gan_wuxing, day_gan_yinyang)

        dy_zhongqi_shishen = ""
        if dy_zhi_zhongqi:
            dy_zhongqi_wuxing = TianGanWuXing.get(dy_zhi_zhongqi, "")
            dy_zhongqi_yinyang = TianGanYinYang.get(dy_zhi_zhongqi, "陽")
            dy_zhongqi_shishen = get_shi_shen(dy_zhi_zhongqi, dy_zhongqi_wuxing, dy_zhongqi_yinyang,
                                               day_gan, day_gan_wuxing, day_gan_yinyang)

        dy_yuqi_shishen = ""
        if dy_zhi_yuqi:
            dy_yuqi_wuxing = TianGanWuXing.get(dy_zhi_yuqi, "")
            dy_yuqi_yinyang = TianGanYinYang.get(dy_zhi_yuqi, "陽")
            dy_yuqi_shishen = get_shi_shen(dy_zhi_yuqi, dy_yuqi_wuxing, dy_yuqi_yinyang,
                                            day_gan, day_gan_wuxing, day_gan_yinyang)

        # 十二長生
        dy_chang_sheng = TianGanZhangSheng.get(day_gan, {}).get(dy_zhi, "")

        dayun_analysis.append({
            "大運": dayun["大運"],
            "起運年齡": dayun["起運年齡"],
            "十神": dayun["十神"],
            "天干": {
                "干": dy_gan,
                "陰陽": dy_gan_yinyang,
                "五行": dy_gan_wuxing,
                "與日干關係": dy_gan_sheng_ke_day,
                "十神": dy_gan_shishen,
            },
            "地支": {
                "支": dy_zhi,
                "陰陽": dy_zhi_yinyang,
                "五行": dy_zhi_wuxing,
                "與日支關係": dy_zhi_sheng_ke_day,
                "十神": dy_zhi_shishen,
                "十二長生": dy_chang_sheng,
                "藏干": {
                    "主氣": {"干": dy_zhi_benqi, "十神": dy_benqi_shishen},
                    "中氣": {"干": dy_zhi_zhongqi, "十神": dy_zhongqi_shishen} if dy_zhi_zhongqi else None,
                    "餘氣": {"干": dy_zhi_yuqi, "十神": dy_yuqi_shishen} if dy_zhi_yuqi else None,
                },
            },
            "陰陽分": {"干": gan_yinyang_tong, "支": zhi_yinyang_tong},
            "用神忌神": {
                "用神到位": yong_shen_dao_wei,
                "喜神到位": xishen_dao_wei,
                "忌神到位": ji_shen_dao_wei,
            },
            "格局影響": ge_ju_ying_xiang,
            "歲運影響": sui_yun_ying_xiang,
            "評分": score,
            "吉凶": jixing,
        })

    return {
        "用神": yong_shen,
        "用神五行": yong_shen_wuxing,
        "相神": xiang_shen,
        "喜神": xishen_gans,
        "忌神": jishen_gans,
        "忌神五行": jishen_wuxing,
        "十個大運分析": dayun_analysis,
    }


def calculate_liunian_pan_duan(ba_zi: str, ge_ju: dict, dayun_pan_duan: dict,
                               detailed_dayun: dict) -> dict:
    """
    計算流年判斷

    Args:
        ba_zi: 八字字符串
        ge_ju: 格局判斷字典
        dayun_pan_duan: 大運判斷字典
        detailed_dayun: 詳細大運信息

    Returns:
        流年判斷字典
    """
    ba_zi_parts = ba_zi.split()
    year_gan = ba_zi_parts[0][0]
    year_zhi = ba_zi_parts[0][1]
    day_gan = ba_zi_parts[2][0]
    day_zhi = ba_zi_parts[2][1]
    day_gan_yinyang = TianGanYinYang[day_gan]
    day_zhi_yinyang = ZhiYinYang[day_zhi]
    day_gan_wuxing = TianGanWuXing[day_gan]
    day_zhi_wuxing = ZhiWuXing[day_zhi]

    # 獲取格局信息
    yong_shen = ge_ju.get("用神", "")
    xiang_shen = ge_ju.get("相神", [])
    yong_shen_wuxing = TianGanWuXing.get(yong_shen, "") if yong_shen else ""

    ge_name = ge_ju.get("格局", "").replace("格", "")
    ji_shens = ["正官", "正印", "偏印", "正財", "偏財", "食神"]
    xiong_shens = ["七殺", "傷官", "比肩", "劫財"]
    is_auspicious = ge_name in ji_shens
    is_xiong_shen_ge = ge_name in xiong_shens
    has_two_xiang_shen = len(xiang_shen) >= 2 and is_xiong_shen_ge
    is_po_ge = "破格" in ge_ju.get("成敗", "") or ge_ju.get("凶神破格", False)

    # 從 ge_ju 提取喜神忌神
    xishen_gans = ge_ju.get("喜神", [])
    xishen_wuxing_list = ge_ju.get("喜神五行", [])
    jishen_gans = ge_ju.get("忌神", [])
    jishen_wuxing = ge_ju.get("忌神五行", [])

    # 獲取大運
    dayuns = detailed_dayun.get("十個大運", [])

    liunian_analysis = []

    for dayun_idx, dayun in enumerate(dayuns):
        dy_gan = dayun["大運干"]
        dy_zhi = dayun["大運支"]
        start_age = dayun["起運年齡"]

        # 計算該大運的 10 個流年
        for liunian_idx in range(10):
            liunian_age = start_age + liunian_idx

            # 計算流年干支（以年柱為基礎，從起運年齡開始順行）
            # 流年是連續的，從出生年份 + 年齡 開始計算
            gan_order = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
            zhi_order = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

            year_gan_idx = gan_order.index(year_gan)
            year_zhi_idx = zhi_order.index(year_zhi)

            # 流年偏移量 = 年齡（從出生年到該年的年數）
            # 例如：4 歲 = 出生後第 4 年，偏移量 = 4
            ln_gan_idx = (year_gan_idx + liunian_age) % 10
            ln_zhi_idx = (year_zhi_idx + liunian_age) % 12

            ln_gan = gan_order[ln_gan_idx]
            ln_zhi = zhi_order[ln_zhi_idx]
            ln_gan_wuxing = TianGanWuXing[ln_gan]
            ln_zhi_wuxing = ZhiWuXing[ln_zhi]

            # 字碰字分析
            # 天干碰天干
            is_special, special_note = check_special_gan_condition(day_gan, ln_gan)

            ln_gan_sheng_ke_day = ""
            if is_special:
                ln_gan_sheng_ke_day = f"特殊條件（{special_note}，不論生剋）"
            elif WU_XING_SHENG.get(ln_gan_wuxing) == day_gan_wuxing:
                ln_gan_sheng_ke_day = "相生"
            elif WU_XING_SHENG.get(day_gan_wuxing) == ln_gan_wuxing:
                ln_gan_sheng_ke_day = "被生"
            elif WU_XING_KE.get(ln_gan_wuxing) == day_gan_wuxing:
                ln_gan_sheng_ke_day = "相剋"
            elif WU_XING_KE.get(day_gan_wuxing) == ln_gan_wuxing:
                ln_gan_sheng_ke_day = "被剋"

            # 地支碰地支
            ln_zhi_sheng_ke_day = ""
            if WU_XING_SHENG.get(ln_zhi_wuxing) == day_zhi_wuxing:
                ln_zhi_sheng_ke_day = "相生"
            elif WU_XING_SHENG.get(day_zhi_wuxing) == ln_zhi_wuxing:
                ln_zhi_sheng_ke_day = "被生"
            elif WU_XING_KE.get(ln_zhi_wuxing) == day_zhi_wuxing:
                ln_zhi_sheng_ke_day = "相剋"
            elif WU_XING_KE.get(day_zhi_wuxing) == ln_zhi_wuxing:
                ln_zhi_sheng_ke_day = "被剋"

            # 檢查地支沖剋
            ln_zhi_chong = check_sui_yun_damaged(day_zhi, [ln_zhi])

            # 用神/忌神分析
            yong_shen_dao_wei = ""
            xishen_dao_wei = ""
            ji_shen_dao_wei = ""
            ge_ju_ying_xiang = "平穩"

            if is_auspicious and yong_shen:
                if ln_gan_wuxing == yong_shen_wuxing:
                    yong_shen_dao_wei = f"用神{yong_shen}到位（天干）"
                    ge_ju_ying_xiang = "用神到位 - 格局增強"
                if ln_zhi_wuxing == yong_shen_wuxing:
                    yong_shen_dao_wei += f"、" if yong_shen_dao_wei else f"用神{yong_shen}到位（地支）"
                    if not ge_ju_ying_xiang.startswith("用神"):
                        ge_ju_ying_xiang = "用神到位 - 格局增強"

            if ln_gan in xishen_gans:
                xishen_dao_wei = f"喜神{ln_gan}到位（天干）"
                if not ge_ju_ying_xiang.startswith("用神"):
                    ge_ju_ying_xiang = "喜神到位 - 吉運"
            if ln_zhi in xishen_gans:
                xishen_dao_wei += f"、" if xishen_dao_wei else f"喜神{ln_zhi}到位（地支）"
                if not ge_ju_ying_xiang.startswith("用神"):
                    ge_ju_ying_xiang = "喜神到位 - 吉運"

            # 檢查流年天干/地支五行是否在喜神五行列表中
            if ln_gan_wuxing in xishen_wuxing_list:
                if not xishen_dao_wei:
                    xishen_dao_wei = f"喜神{ln_gan_wuxing}到位（天干五行）"
                    if not ge_ju_ying_xiang.startswith("用神"):
                        ge_ju_ying_xiang = "喜神到位 - 吉運"
            if ln_zhi_wuxing in xishen_wuxing_list:
                if not xishen_dao_wei:
                    xishen_dao_wei = f"喜神{ln_zhi_wuxing}到位（地支五行）"
                    if not ge_ju_ying_xiang.startswith("用神"):
                        ge_ju_ying_xiang = "喜神到位 - 吉運"

            if ln_gan in jishen_gans:
                ji_shen_dao_wei = f"忌神{ln_gan}到位（天干）"
                ge_ju_ying_xiang = "忌神到位 - 格局受損"
            if ln_zhi_wuxing in jishen_wuxing:
                ji_shen_dao_wei += f"、" if ji_shen_dao_wei else f"忌神{ln_zhi}到位（地支）"
                if not ge_ju_ying_xiang.startswith("忌神"):
                    ge_ju_ying_xiang = "忌神到位 - 格局受損"

            # 吉凶判斷
            if ge_ju_ying_xiang.startswith("用神"):
                jixing = "大吉"
            elif ge_ju_ying_xiang.startswith("喜神"):
                jixing = "吉"
            elif ge_ju_ying_xiang.startswith("忌神"):
                jixing = "凶"
            else:
                jixing = "平"

            # 歲運影響
            sui_yun_ying_xiang = []
            if ln_zhi_chong:
                sui_yun_ying_xiang.append(f"日支被{','.join(ln_zhi_chong)}")
                if jixing in ["大吉", "吉"]:
                    jixing = "吉中帶凶"
                    ge_ju_ying_xiang += "，日支受沖，吉中帶凶"
                elif jixing == "凶":
                    ge_ju_ying_xiang += "，日支受沖，凶上加凶"

            # 原局破格時的判斷
            if is_po_ge and jixing not in ["大吉", "吉"]:
                jixing = "凶"
                ge_ju_ying_xiang += "，原局破格，流年無救應"

            # 評分
            score_map = {"大吉": 90, "吉": 70, "凶": 30, "大凶": 10, "平": 50, "吉中帶凶": 60, "凶中有救": 40}
            score = score_map.get(jixing, 50)

            # 流年十神
            ln_gan_yinyang = TianGanYinYang[ln_gan]
            ln_gan_shishen = get_shi_shen(ln_gan, ln_gan_wuxing, ln_gan_yinyang,
                                           day_gan, day_gan_wuxing, day_gan_yinyang)

            ln_zhi_benqi = ZhiCangGan.get(ln_zhi, {}).get("主氣", ln_zhi)
            ln_zhi_benqi_wuxing = TianGanWuXing.get(ln_zhi_benqi, "")
            ln_zhi_benqi_yinyang = TianGanYinYang.get(ln_zhi_benqi, "陽")
            ln_zhi_shishen = get_shi_shen(ln_zhi_benqi, ln_zhi_benqi_wuxing, ln_zhi_benqi_yinyang,
                                           day_gan, day_gan_wuxing, day_gan_yinyang)

            # 十二長生
            ln_chang_sheng = TianGanZhangSheng.get(day_gan, {}).get(ln_zhi, "")

            liunian_analysis.append({
                "大運序號": dayun_idx + 1,
                "大運": dayun["大運"],
                "流年序號": liunian_idx + 1,
                "流年": ln_gan + ln_zhi,
                "虛歲": liunian_age,
                "天干": {
                    "干": ln_gan,
                    "五行": ln_gan_wuxing,
                    "與日干關係": ln_gan_sheng_ke_day,
                    "十神": ln_gan_shishen,
                },
                "地支": {
                    "支": ln_zhi,
                    "五行": ln_zhi_wuxing,
                    "與日支關係": ln_zhi_sheng_ke_day,
                    "十神": ln_zhi_shishen,
                    "十二長生": ln_chang_sheng,
                },
                "用神忌神": {
                    "用神到位": yong_shen_dao_wei,
                    "喜神到位": xishen_dao_wei,
                    "忌神到位": ji_shen_dao_wei,
                },
                "格局影響": ge_ju_ying_xiang,
                "歲運影響": sui_yun_ying_xiang,
                "評分": score,
                "吉凶": jixing,
            })

    return {
        "用神": yong_shen,
        "用神五行": yong_shen_wuxing,
        "相神": xiang_shen,
        "喜神": xishen_gans,
        "忌神": jishen_gans,
        "忌神五行": jishen_wuxing,
        "流年分析": liunian_analysis,
    }


# =============================================================================
# 歲運格局判斷（新增功能）
# 根據用戶需求：原局為一層，大運 + 流年為一層
# =============================================================================

def calculate_dayun_yingdong(
    ba_zi: str,
    dayun: dict,
    yuan_ju_ge_ju: dict
) -> dict:
    """
    計算大運對原局格局的引動

    Args:
        ba_zi: 八字字符串
        dayun: 大運字典，包含"大運"、"大運支"等鍵
        yuan_ju_ge_ju: 原局格局結果

    Returns:
        {
            "大運": str,
            "大運天干": str,
            "大運地支": str,
            "引動原局": dict,
            "對格局影響": str,  # 增強/減弱/不變
            "大運十神": str,
        }
    """
    dayun_gan_zhi = dayun.get("大運", "")
    if not dayun_gan_zhi or len(dayun_gan_zhi) != 2:
        return {"大運": "", "大運天干": "", "大運地支": "", "引動原局": {}, "對格局影響": "無", "大運十神": ""}

    dayun_gan = dayun_gan_zhi[0]
    dayun_zhi = dayun_gan_zhi[1]

    # 獲取原局信息
    day_gan = ba_zi.split()[2][0]  # 日天干
    yong_shen = yuan_ju_ge_ju.get("用神", "")
    xiang_shen = yuan_ju_ge_ju.get("相神", [])
    ji_shen = yuan_ju_ge_ju.get("忌神", [])
    yong_shen_wuxing = yuan_ju_ge_ju.get("用神五行", "")

    # 大運天干十神
    dayun_gan_wuxing = TIAN_GAN_WU_XING.get(dayun_gan, "")
    dayun_gan_yinyang = TIAN_GAN_YIN_YANG.get(dayun_gan, "")
    day_gan_wuxing = TIAN_GAN_WU_XING.get(day_gan, "")
    day_gan_yinyang = TIAN_GAN_YIN_YANG.get(day_gan, "")
    dayun_shishen = get_shi_shen(dayun_gan, dayun_gan_wuxing, dayun_gan_yinyang,
                                  day_gan, day_gan_wuxing, day_gan_yinyang)

    # 判斷大運對格局的影響
    ying_xiang = "不變"
    yin_dong_shuo_ming = []

    # 大運天干為用神
    if dayun_gan == yong_shen:
        ying_xiang = "增強"
        yin_dong_shuo_ming.append(f"大運天干{dayun_gan}為用神到位")

    # 大運天干為忌神
    if dayun_gan in ji_shen:
        ying_xiang = "減弱"
        yin_dong_shuo_ming.append(f"大運天干{dayun_gan}為忌神")

    # 大運天干生用神
    if WU_XING_SHENG.get(dayun_gan_wuxing) == yong_shen_wuxing:
        ying_xiang = "增強"
        yin_dong_shuo_ming.append(f"大運天干{dayun_gan}生用神")

    # 大運天干剋用神
    if WU_XING_KE.get(dayun_gan_wuxing) == yong_shen_wuxing:
        ying_xiang = "減弱"
        yin_dong_shuo_ming.append(f"大運天干{dayun_gan}剋用神")

    return {
        "大運": dayun_gan_zhi,
        "大運天干": dayun_gan,
        "大運地支": dayun_zhi,
        "引動原局": {
            "天干作用": "；".join(yin_dong_shuo_ming) if yin_dong_shuo_ming else "無特殊作用",
        },
        "對格局影響": ying_xiang,
        "大運十神": dayun_shishen,
    }


def calculate_liunian_yingdong(
    ba_zi: str,
    dayun: dict,
    liunian: dict,
    yuan_ju_ge_ju: dict,
    dayun_yingdong: dict
) -> dict:
    """
    計算流年對原局 + 大運的引動

    Args:
        ba_zi: 八字字符串
        dayun: 大運字典
        liunian: 流年字典，包含"流年"、"天干"、"地支"等鍵
        yuan_ju_ge_ju: 原局格局結果
        dayun_yingdong: 大運引動結果

    Returns:
        {
            "流年": str,
            "流年天干": str,
            "流年地支": str,
            "字碰字": dict,
            "對格局影響": str,
            "流年十神": str,
        }
    """
    liunian_gan_zhi = liunian.get("流年", "")
    if not liunian_gan_zhi or len(liunian_gan_zhi) != 2:
        return {"流年": "", "流年天干": "", "流年地支": "", "字碰字": {}, "對格局影響": "無", "流年十神": ""}

    liunian_gan = liunian_gan_zhi[0]
    liunian_zhi = liunian_gan_zhi[1]

    # 獲取原局信息
    pillars = ba_zi.split()
    day_gan = pillars[2][0]
    yong_shen = yuan_ju_ge_ju.get("用神", "")
    ji_shen = yuan_ju_ge_ju.get("忌神", [])
    yong_shen_wuxing = yuan_ju_ge_ju.get("用神五行", "")

    # 流年天干十神
    liunian_gan_wuxing = TIAN_GAN_WU_XING.get(liunian_gan, "")
    liunian_gan_yinyang = TIAN_GAN_YIN_YANG.get(liunian_gan, "")
    day_gan_wuxing = TIAN_GAN_WU_XING.get(day_gan, "")
    day_gan_yinyang = TIAN_GAN_YIN_YANG.get(day_gan, "")
    liunian_shishen = get_shi_shen(liunian_gan, liunian_gan_wuxing, liunian_gan_yinyang,
                                    day_gan, day_gan_wuxing, day_gan_yinyang)

    # 字碰字：天干碰天干
    tian_gan_peng = []
    for i, pillar in enumerate(pillars):
        p_gan = pillar[0]
        if p_gan == liunian_gan:
            tian_gan_peng.append({"碰": f"{['年', '月', '日', '時'][i]}干{p_gan}", "關係": "比肩"})
        elif WU_XING_SHENG.get(p_gan) == liunian_gan_wuxing:
            tian_gan_peng.append({"碰": f"{['年', '月', '日', '時'][i]}干{p_gan}", "關係": "印"})
        elif WU_XING_SHENG.get(liunian_gan_wuxing) == TIAN_GAN_WU_XING.get(p_gan, ""):
            tian_gan_peng.append({"碰": f"{['年', '月', '日', '時'][i]}干{p_gan}", "關係": "食傷"})

    # 字碰字：地支碰地支
    di_zhi_peng = []
    for i, pillar in enumerate(pillars):
        p_zhi = pillar[1]
        if p_zhi == liunian_zhi:
            di_zhi_peng.append({"碰": f"{['年', '月', '日', '時'][i]}支{p_zhi}", "關係": "伏吟"})
        for c1, c2 in ZHI_LIU_CHONG:
            if (p_zhi == c1 and liunian_zhi == c2) or (p_zhi == c2 and liunian_zhi == c1):
                di_zhi_peng.append({"碰": f"{['年', '月', '日', '時'][i]}支{p_zhi}", "關係": "沖"})
                break

    # 判斷流年對格局的影響
    ying_xiang = []

    # 流年天干為用神
    if liunian_gan == yong_shen:
        ying_xiang.append("用神到位")

    # 流年天干為忌神
    if liunian_gan in ji_shen:
        ying_xiang.append("忌神到位")

    # 流年地支沖原局用神根氣
    yong_shen_gen_qi = yuan_ju_ge_ju.get("根氣地支", [])
    for gen_zhi in yong_shen_gen_qi:
        for c1, c2 in ZHI_LIU_CHONG:
            if (gen_zhi == c1 and liunian_zhi == c2) or (gen_zhi == c2 and liunian_zhi == c1):
                ying_xiang.append(f"流年沖用神根氣{gen_zhi}")

    return {
        "流年": liunian_gan_zhi,
        "流年天干": liunian_gan,
        "流年地支": liunian_zhi,
        "字碰字": {
            "天干碰": tian_gan_peng,
            "地支碰": di_zhi_peng,
        },
        "對格局影響": "；".join(ying_xiang) if ying_xiang else "平穩",
        "流年十神": liunian_shishen,
    }


def calculate_suiyun_geju(
    yuan_ju_ge_ju: dict,
    dayun_yingdong: dict,
    liunian_yingdong: dict
) -> dict:
    """
    綜合判斷歲運格局成敗

    Args:
        yuan_ju_ge_ju: 原局格局結果
        dayun_yingdong: 大運引動結果
        liunian_yingdong: 流年引動結果

    Returns:
        {
            "格局類型": "歲運",
            "原局格局": str,
            "歲運格局狀態": str,  # 成格/破格/平
            "綜合判斷": str,
            "應事": list,
            "斷語": str,
        }
    """
    yuan_ju_ge = yuan_ju_ge_ju.get("格局", "")
    yuan_ju_chengbai = yuan_ju_ge_ju.get("成敗", "")

    dayun_ying_xiang = dayun_yingdong.get("對格局影響", "不變")
    liunian_ying_xiang = liunian_yingdong.get("對格局影響", "平穩")

    # 綜合判斷
    ying_xiang_factors = []

    # 大運增強
    if dayun_ying_xiang == "增強":
        ying_xiang_factors.append(("+", "大運增強格局"))
    elif dayun_ying_xiang == "減弱":
        ying_xiang_factors.append(("-", "大運減弱格局"))

    # 流年用神到位
    if "用神到位" in liunian_ying_xiang:
        ying_xiang_factors.append(("+", "流年用神到位"))

    # 流年忌神到位
    if "忌神到位" in liunian_ying_xiang:
        ying_xiang_factors.append(("-", "流年忌神到位"))

    # 流年沖根氣
    if "沖用神根氣" in liunian_ying_xiang:
        ying_xiang_factors.append(("-", "流年沖用神根氣"))

    # 計算吉凶
    positive = sum(1 for s, _ in ying_xiang_factors if s == "+")
    negative = sum(1 for s, _ in ying_xiang_factors if s == "-")

    if positive > negative:
        geju_zhuangtai = "成格"
        duan_yu = f"{yuan_ju_ge}，歲運扶助，主吉"
    elif negative > positive:
        geju_zhuangtai = "破格"
        duan_yu = f"{yuan_ju_ge}，歲運剋損，主凶"
    else:
        geju_zhuangtai = "平"
        duan_yu = f"{yuan_ju_ge}，歲運平穩"

    # 應事
    ying_shi = []
    if "用神到位" in liunian_ying_xiang:
        if yuan_ju_ge == "正官格":
            ying_shi.append("升遷")
            ying_shi.append("名譽")
        elif yuan_ju_ge in ["正財格", "偏財格"]:
            ying_shi.append("進財")
        elif yuan_ju_ge in ["正印格", "偏印格"]:
            ying_shi.append("學習進步")
            ying_shi.append("貴人相助")

    if "忌神到位" in liunian_ying_xiang:
        ying_shi.append("壓力")
        ying_shi.append("阻礙")

    if "沖用神根氣" in liunian_ying_xiang:
        ying_shi.append("變動")
        ying_shi.append("不穩")

    return {
        "格局類型": "歲運",
        "原局格局": yuan_ju_ge,
        "原局成敗": yuan_ju_chengbai,
        "歲運格局狀態": geju_zhuangtai,
        "綜合判斷": "；".join([f for _, f in ying_xiang_factors]) if ying_xiang_factors else "歲運無特殊影響",
        "應事": ying_shi,
        "斷語": duan_yu,
    }
