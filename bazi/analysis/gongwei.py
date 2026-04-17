"""
宮位分析模塊

根據講義內容實現宮位分析：
- 六親宮位（祖輩宮、父母兄弟宮、夫妻宮、晚輩宮）
- 身體宮位（頭面、胸背、腹腰、足部）
- 宮位吉凶判斷
- 疾病論斷
"""

from bazi.core.constants import (
    TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG, ZHI_WU_XING, WU_XING_KE, WU_XING_SHENG,
    TIAN_GAN_ZANG_FU, ZHI_ZANG_FU, ZHI_LIU_CHONG,
)

# 別名（兼容舊代碼）
TianGanWuXing = TIAN_GAN_WU_XING
TianGanYinYang = TIAN_GAN_YIN_YANG
ZhiWuXing = ZHI_WU_XING
WuXingKe = WU_XING_KE
WuXingSheng = WU_XING_SHENG
TianGanZangFu = TIAN_GAN_ZANG_FU
ZhiZangFu = ZHI_ZANG_FU
ZhiLiuChong = ZHI_LIU_CHONG


# 六親宮位
LIU_QIN_GONG_WEI = {
    "年柱": {
        "祖輩宮": {
            "年干": "外親 (外祖父母)",
            "年支": "內親 (內祖父母)"
        }
    },
    "月柱": {
        "父母兄弟宮": {
            "月干": "外親 (岳父母/伯叔嬸姨)",
            "月支": "內親 (父母/兄弟姐妹)"
        }
    },
    "日柱": {
        "夫妻宮": {
            "日干": "自己",
            "日支": "配偶及兄弟姐妹"
        }
    },
    "時柱": {
        "晚輩宮": {
            "時干": "兒子/弟子/部屬",
            "時支": "女兒/女婿/兒媳"
        }
    }
}


# 身體宮位（詳細）
SHEN_TI_GONG_WEI = {
    "年柱": {
        "宮位": "頭面",
        "天干": "甲乙頭面、丙丁眼、戊己鼻、庚辛筋骨、壬癸耳腎",
        "地支": "戌亥子 - 頭、丑寅 - 頸、卯辰巳 - 胸背",
        "時序": "幼年（1-15 歲）"
    },
    "月柱": {
        "宮位": "胸背",
        "天干": "丙丁肩胸、戊己腹、庚辛肋、壬癸腎",
        "地支": "午未申 - 腹、酉戌 - 腰、亥子 - 足",
        "時序": "青年（16-30 歲）"
    },
    "日柱": {
        "宮位": "腹腰",
        "天干": "戊己腹、庚辛筋骨、壬癸腎陰",
        "地支": "寅卯 - 膝、辰巳午 - 腹、未申酉 - 腰",
        "時序": "壯年（31-45 歲）"
    },
    "時柱": {
        "宮位": "足部",
        "天干": "庚辛足、壬癸足陰",
        "地支": "戌亥 - 足、子丑 - 足跟、寅卯 - 足趾",
        "時序": "中晚年（46 歲之後）",
        "特殊": "時干 - 外陰；時支 - 內陰、精卵"
    }
}


# 天干對應身體部位
TIAN_GAN_BU_WEI = {
    "甲": "頭膽", "乙": "肝膽",
    "丙": "小腸", "丁": "心臟",
    "戊": "胃", "己": "脾",
    "庚": "大腸", "辛": "肺",
    "壬": "膀胱", "癸": "腎",
}


# 地支對應身體部位
ZHI_BU_WEI = {
    "子": "會陰/膀胱", "丑": "脾/腳氣", "寅": "膽/手腕", "卯": "肝/神經",
    "辰": "胃/皮膚", "巳": "心臟/小腸", "午": "心臟/血液", "未": "脾/消化",
    "申": "大腸/骨骼", "酉": "肺/牙齒", "戌": "胃/皮膚", "亥": "腎臟/膀胱",
}


def check_zhi_chong(zhi: str, all_zhis: list) -> tuple:
    """
    檢查地支是否被沖

    Args:
        zhi: 要檢查的地支
        all_zhis: 命局所有地支

    Returns:
        (是否被沖，沖的地支)
    """
    for ch1, ch2 in ZhiLiuChong:
        if zhi == ch1 and ch2 in all_zhis:
            return True, ch2
        if zhi == ch2 and ch1 in all_zhis:
            return True, ch1
    return False, None


def check_gai_tou_jie_jiao(pillar: tuple) -> tuple:
    """
    檢查蓋頭截腳

    Args:
        pillar: (天干，地支) 元組

    Returns:
        (類型，說明) 或 (None, None)
    """
    tg, zhi = pillar
    tg_wuxing = TianGanWuXing[tg]
    zhi_wuxing = ZhiWuXing[zhi]

    if WuXingKe.get(tg_wuxing) == zhi_wuxing:
        return "蓋頭", f"{tg}剋{zhi}（{tg_wuxing}剋{zhi_wuxing}）"
    elif WuXingKe.get(zhi_wuxing) == tg_wuxing:
        return "截腳", f"{zhi}剋{tg}（{zhi_wuxing}剋{tg_wuxing}）"
    return None, None


def calculate_ji_bing_lun_duan(ba_zi_parts: list, ji_shen_wuxing: list,
                                xi_shen_shishen: list, ji_shen_shishen: list) -> dict:
    """
    計算疾病論斷

    根據《12_宮位干支象法.docx》的疾病論斷規則：
    1. 季節體質：生於夏季易患燥熱之症，生於冬季易患寒濕之症
    2. 五行過旺：四柱過旺過多的五行為病
    3. 五行所缺：四柱所缺的五行為病
    4. 忌神所在：忌神天干地支相應的臟腑為病源
    5. 蓋頭截腳：天干剋地支或地支剋天干為病
    6. 特殊論斷：土多糖尿病、燥土腫瘤等
    7. 五行生剋：金剋木肝膽病等
    """
    # 獲取月支（判斷季節）
    month_zhi = ba_zi_parts[1][1]
    season_map = {
        "巳": "夏季", "午": "夏季", "未": "夏季",
        "亥": "冬季", "子": "冬季", "丑": "冬季",
        "寅": "春季", "卯": "春季", "辰": "春季",
        "申": "秋季", "酉": "秋季", "戌": "秋季",
    }
    season = season_map.get(month_zhi, "未知")

    # 五行分布統計
    wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pillar in ba_zi_parts:
        tg_wuxing = TianGanWuXing.get(pillar[0], "")
        zhi_wuxing = ZhiWuXing.get(pillar[1], "")
        if tg_wuxing:
            wuxing_count[tg_wuxing] += 1
        if zhi_wuxing:
            wuxing_count[zhi_wuxing] += 1

    # 疾病論斷列表
    ji_bing_list = []

    # 1. 季節體質
    if season == "夏季":
        ji_bing_list.append({
            "類型": "季節體質",
            "說明": "生於夏季，易患燥熱之症",
            "應期": "火旺的大運或流年",
            "建議": "宜滋陰清熱，避免辛辣燥熱食物"
        })
    elif season == "冬季":
        ji_bing_list.append({
            "類型": "季節體質",
            "說明": "生於冬季，易患寒濕之症",
            "應期": "水旺的大運或流年",
            "建議": "宜溫陽散寒，避免生冷寒涼食物"
        })

    # 2. 五行過旺（≥4 個）
    for wx, count in wuxing_count.items():
        if count >= 4:
            ji_bing_list.append({
                "類型": "五行過旺",
                "說明": f"{wx}行過旺（{count}個），易患相關疾病",
                "應期": f"{wx}旺的大運或流年",
                "建議": f"宜洩{wx}之氣，避免{wx}旺的方位和行業"
            })

    # 3. 五行所缺
    for wx, count in wuxing_count.items():
        if count == 0:
            ji_bing_list.append({
                "類型": "五行所缺",
                "說明": f"五行缺{wx}，先天不足",
                "應期": f"{wx}弱的大運或流年",
                "建議": f"宜補{wx}，多接觸{wx}相關的方位和行業"
            })

    # 4. 忌神所在
    for wx in ji_shen_wuxing:
        ji_bing_list.append({
            "類型": "忌神所在",
            "說明": f"忌神五行{wx}相應的臟腑為病源",
            "應期": f"{wx}旺的大運或流年",
            "建議": f"注意{wx}對應臟腑的保養"
        })

    # 5. 特殊疾病論斷
    # 土多或過旺（≥4 個）：糖尿病
    if wuxing_count.get("土", 0) >= 4:
        ji_bing_list.append({
            "類型": "特殊論斷",
            "說明": "土多或過旺，易患糖尿病",
            "應期": "土旺的大運或流年",
            "建議": "控制飲食，定期檢查血糖"
        })

    # 燥土多或過旺：腫瘤
    # 燥土 = 戌未（不含丑辰濕土）
    zao_tu = wuxing_count.get("土", 0)
    if zao_tu >= 3:
        ji_bing_list.append({
            "類型": "特殊論斷",
            "說明": "燥土（戌未）多，易患腫瘤",
            "應期": "燥土旺的大運或流年",
            "建議": "定期健康檢查，注意腫瘤篩查"
        })

    # 群木剋土（木≥3，土≤1）：傷疤
    if wuxing_count.get("木", 0) >= 3 and wuxing_count.get("土", 0) <= 1:
        ji_bing_list.append({
            "類型": "特殊論斷",
            "說明": "群木剋土，易有傷疤",
            "應期": "木旺的年份",
            "建議": "避免危險活動，注意皮膚保養"
        })

    # 土旺水虛（土≥3，水≤1）：腎虛
    if wuxing_count.get("土", 0) >= 3 and wuxing_count.get("水", 0) <= 1:
        ji_bing_list.append({
            "類型": "特殊論斷",
            "說明": "土旺水虛，易患腎虛",
            "應期": "土旺水弱的年份",
            "建議": "補腎固本，避免過度勞累"
        })

    # 6. 五行生剋疾病
    # 金剋木：肝膽病
    if wuxing_count.get("金", 0) >= 2 and wuxing_count.get("木", 0) <= 2:
        ji_bing_list.append({
            "類型": "五行生剋",
            "說明": "金剋木，易患肝膽疾病",
            "應期": "金旺木弱的年份",
            "建議": "疏肝理氣，保持心情舒暢"
        })

    # 水剋火：心血管病
    if wuxing_count.get("水", 0) >= 2 and wuxing_count.get("火", 0) <= 2:
        ji_bing_list.append({
            "類型": "五行生剋",
            "說明": "水剋火，易患心血管、小腸疾病",
            "應期": "水旺火弱的年份",
            "建議": "保護心臟，避免過度緊張"
        })

    # 木剋土：脾胃病
    if wuxing_count.get("木", 0) >= 2 and wuxing_count.get("土", 0) <= 2:
        ji_bing_list.append({
            "類型": "五行生剋",
            "說明": "木剋土，易患脾胃、消化系統疾病",
            "應期": "木旺土弱的年份",
            "建議": "調養脾胃，飲食規律"
        })

    # 火剋金：肺病
    if wuxing_count.get("火", 0) >= 2 and wuxing_count.get("金", 0) <= 2:
        ji_bing_list.append({
            "類型": "五行生剋",
            "說明": "火剋金，易患肺病、氣管炎、呼吸系統疾病",
            "應期": "火旺金弱的年份",
            "建議": "保護呼吸系統，避免煙霧刺激"
        })

    # 土剋水：腎臟病
    if wuxing_count.get("土", 0) >= 2 and wuxing_count.get("水", 0) <= 2:
        ji_bing_list.append({
            "類型": "五行生剋",
            "說明": "土剋水，易患腎臟、膀胱、泌尿系統疾病",
            "應期": "土旺水弱的年份",
            "建議": "補腎固本，多喝水"
        })

    return {
        "季節體質": season,
        "五行分布": wuxing_count,
        "疾病論斷": ji_bing_list,
    }


def calculate_gongwei(ba_zi: str, canggan: dict, shi_shen: dict,
                      ge_ju: dict = None, integrated_analysis: dict = None) -> dict:
    """
    計算宮位分析

    Args:
        ba_zi: 八字字符串
        canggan: 藏干字典
        shi_shen: 十神字典
        ge_ju: 格局判斷（可選）
        integrated_analysis: 整合分析（可選）

    Returns:
        宮位分析字典
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    # 獲取格局信息
    if ge_ju:
        yong_shen = ge_ju.get("用神", "")
        xiang_shen = ge_ju.get("相神", [])
        ji_shen_wuxing = ge_ju.get("忌神五行", [])
    else:
        yong_shen = ""
        xiang_shen = []
        ji_shen_wuxing = []

    # 從整合分析獲取喜神忌神十神
    xi_shen_shishen = []
    ji_shen_shishen = []
    if integrated_analysis:
        integrated = integrated_analysis
        xi_shen_shishen = integrated.get("格局核心", {}).get("喜神十神", [])
        ji_shen_shishen = integrated.get("格局核心", {}).get("忌神十神", [])

    # 獲取十神信息
    shi_shen_data = shi_shen.get("十神", []) if isinstance(shi_shen, dict) else []

    # 宮位吉凶分析
    gong_wei_ji_xiong = []
    all_zhis = [p[1] for p in ba_zi_parts]

    for i, (pillar, pillar_name) in enumerate(zip(ba_zi_parts, pillar_names)):
        tg = pillar[0]
        zhi = pillar[1]
        tg_wuxing = TianGanWuXing[tg]
        zhi_wuxing = ZhiWuXing[zhi]

        # 獲取該柱的十神
        if isinstance(shi_shen_data, list) and i < len(shi_shen_data):
            pillar_shi_shen = shi_shen_data[i]
            tg_shi_shen = pillar_shi_shen.get("十神", "") if isinstance(pillar_shi_shen, dict) else ""
            zhi_shi_shen = pillar_shi_shen.get("主氣十神", {}) if isinstance(pillar_shi_shen, dict) else {}
        else:
            tg_shi_shen = ""
            zhi_shi_shen = {}

        # 判斷天干十神是喜是忌
        tg_is_xi = tg_shi_shen in xi_shen_shishen
        tg_is_ji = tg_shi_shen in ji_shen_shishen or tg_wuxing in ji_shen_wuxing

        # 判斷地支十神是喜是忌
        zhi_shi_shen_name = zhi_shi_shen.get("十神", "") if isinstance(zhi_shi_shen, dict) else ""
        zhi_is_xi = zhi_shi_shen_name in xi_shen_shishen
        zhi_is_ji = zhi_shi_shen_name in ji_shen_shishen or zhi_wuxing in ji_shen_wuxing

        # 檢查沖剋
        zhi_being_chong, chong_zhi = check_zhi_chong(zhi, all_zhis)

        # 檢查蓋頭截腳
        gai_tou_type, gai_tou_desc = check_gai_tou_jie_jiao(pillar)

        # 綜合判斷吉凶
        tg_ji_xiong = "平"
        tg_reason = []
        zhi_ji_xiong = "平"
        zhi_reason = []

        # 天干吉凶判斷
        if tg_is_xi and not gai_tou_type:
            tg_ji_xiong = "大吉"
            tg_reason.append("喜神透干")
        elif tg_is_xi and gai_tou_type:
            tg_ji_xiong = "吉中帶凶"
            tg_reason.append(f"喜神但{gai_tou_type}")
        elif tg_is_ji:
            tg_ji_xiong = "凶"
            tg_reason.append("忌神")
        elif gai_tou_type:
            tg_ji_xiong = "不吉"
            tg_reason.append(gai_tou_desc)
        else:
            tg_reason.append("無特殊")

        # 地支吉凶判斷
        if zhi_is_xi and not zhi_being_chong:
            zhi_ji_xiong = "大吉"
            zhi_reason.append("喜神坐實")
        elif zhi_is_xi and zhi_being_chong:
            zhi_ji_xiong = "吉中帶凶"
            zhi_reason.append(f"喜神被{chong_zhi}沖")
        elif zhi_is_ji:
            zhi_ji_xiong = "凶"
            zhi_reason.append("忌神")
        elif zhi_being_chong:
            zhi_ji_xiong = "不吉"
            zhi_reason.append(f"地支被沖 ({chong_zhi})")
        else:
            zhi_reason.append("無特殊")

        gong_wei_ji_xiong.append({
            "宮位": pillar_name,
            "天干": {
                "天干": tg,
                "五行": tg_wuxing,
                "十神": tg_shi_shen,
                "吉凶": tg_ji_xiong,
                "原因": tg_reason,
                "臟腑": TianGanZangFu.get(tg, ""),
                "部位": TIAN_GAN_BU_WEI.get(tg, ""),
            },
            "地支": {
                "地支": zhi,
                "五行": zhi_wuxing,
                "十神": zhi_shi_shen_name,
                "吉凶": zhi_ji_xiong,
                "原因": zhi_reason,
                "臟腑": ZhiZangFu.get(zhi, ""),
                "部位": ZHI_BU_WEI.get(zhi, ""),
                "被沖": zhi_being_chong,
                "沖支": chong_zhi,
            },
            "蓋頭截腳": {
                "類型": gai_tou_type,
                "說明": gai_tou_desc,
            } if gai_tou_type else {"類型": "無", "說明": "無蓋頭截腳"},
        })

    # 計算疾病論斷
    ji_bing_lun_duan = calculate_ji_bing_lun_duan(
        ba_zi_parts, ji_shen_wuxing, xi_shen_shishen, ji_shen_shishen
    )

    return {
        "六親宮位": LIU_QIN_GONG_WEI,
        "身體宮位": SHEN_TI_GONG_WEI,
        "宮位吉凶": gong_wei_ji_xiong,
        "天干對應部位": TIAN_GAN_BU_WEI,
        "天干對應臟腑": TianGanZangFu,
        "地支對應部位": ZHI_BU_WEI,
        "地支對應臟腑": ZhiZangFu,
        "疾病論斷": ji_bing_lun_duan,
    }
