"""
一柱論命模塊

根據六十甲子體象論的邏輯，分析旬中六親狀態生成斷語
來源：11_六十甲子體象論.docx

核心邏輯：
- 以旬為單位分析六親分布
- 男命用陽天干為先天，女命用陰天干為先天
- 根據六親在旬中的干支狀態（十二長生、五行旺衰）判斷緣份深淺
- 日支與其他六親干支的關係（刑沖合會）
"""

from bazi.calculations.liushijiazi import (
    calculate_liu_shi_jia_zi,
    get_xun,
    LIU_SHI_JIA_ZI_ORDER,
)
from bazi.core.constants import (
    TIAN_GAN_WU_XING,
    TIAN_GAN_YIN_YANG,
    TIAN_GAN_ZHANG_SHENG,
    WU_XING_KE,
    WU_XING_SHENG,
)


# =============================================================================
# 六十甲子體象描述 (日柱斷語)
# 來源：11_六十甲子體象論.docx
# =============================================================================

YIZHU_DESCRIPTIONS = {
    "甲子": "甲坐子敗地，沐浴桃花，有色情之災。形象溫雅，內心多疑，自尊心強。",
    "乙丑": "乙坐丑臨官墓，事業不順遂，女命另有夫緣弱之象。為財勞碌，性格倔強。",
    "丙寅": "丙坐寅長生，智慧高，學習力強。充滿熱情，有執行力，文采出眾。",
    "丁卯": "丁坐卯病地，心思細膩但易多愁善感。為人溫和，富有同情心，但意志不堅。",
    "戊辰": "戊坐辰冠帶，自我意識強，注重名譽。做事有條理，有財庫，性格穩重。",
    "己巳": "己坐巳帝旺，精力充沛，有開創精神。多才多藝，但有時過於主觀。",
    "庚午": "庚坐午沐浴，為人熱情但帶剛正之氣。有正義感，異性緣佳，事業起伏較大。",
    "辛未": "辛坐未衰地，性格內斂且保守。做事謹慎，有藝術天分，內心孤獨。",
    "壬申": "壬坐申長生，機智聰明，適應力強。人生多變動，有貴人相助，多文法。",
    "癸酉": "癸坐酉病地，思想獨特，善於研究。內向冷淡，但領悟力極高。",
    "甲戌": "甲坐戌養地，為人仁慈，得人提攜。勤儉持家，但性格較為保守。",
    "乙亥": "乙坐亥死地，聰明但缺乏行動力。有母慈之心，喜研習哲學藝術。",
    "丙子": "丙坐子胎地，有創意但需耐性。陰陽煞，感情起伏大，注重外表。",
    "丁丑": "丁坐丑墓地，保守深沉，不善表達。陰陽差錯，有理財能力，晚年有福。",
    "戊寅": "戊坐寅長生，有領導才華，魄力十足。為人正直，但早年多勞苦。",
    "己卯": "己坐卯病地，心思敏感，多才多藝。為人隨和，但易受他人影響。",
    "庚辰": "庚坐辰養地，魁罡日，性格剛烈且有主見。有官運，但不服管束。",
    "辛巳": "辛坐巳死地，內心多疑，做事周密。有神祕感，喜愛獨居研究。",
    "壬午": "壬坐午胎地，熱情有禮，為人慷慨。財官同宮，一生財運佳。",
    "癸未": "癸坐未墓地，性格穩重，善於守成。有奉獻精神，但早年奔波。",
    "甲申": "甲坐申絕地，機智善變，適應力強。有冒險精神，人生多轉折。",
    "乙酉": "乙坐酉絕地，內心孤癖且清高。做事乾脆，但易招是非。",
    "丙戌": "丙坐戌墓地，性格熱情但易衝動。有財庫，做事有始有終。",
    "丁亥": "丁坐亥胎地，為人淳樸，得人信任。官印相生，性格文雅。",
    "戊子": "戊坐子胎地，誠實可靠，注重現實。財運不俗，但較為操勞。",
    "己丑": "己坐丑墓地，內向穩重，善於計畫。外柔內剛，有理財天分。",
    "庚寅": "庚坐寅絕地，性格剛毅，有開創性。人生起伏大，多波折。",
    "辛卯": "辛坐卯絕地，聰明機敏但不專注。感情豐富，多愁善感。",
    "壬辰": "壬坐辰墓地，魁罡日，性格強硬。有大志向，但人生波折多。",
    "癸巳": "癸坐巳胎地，為人乖巧，富於機會。財官相生，一生富裕。",
    "甲午": "甲坐午死地，熱情但缺乏後勁。有文藝才華，但感情多波折。",
    "乙未": "乙坐未養地，溫和隨和，注重家庭。有貴人運，性格柔順。",
    "丙申": "丙坐申病地，聰明有才，做事周全。異性緣佳，但易感疲累。",
    "丁酉": "丁坐酉長生，文采出眾，品格高尚。一生多貴人，聰明好學。",
    "戊戌": "戊坐戌墓地，性格穩重且剛毅。有原則，做事踏實。",
    "己亥": "己坐亥胎地，心地善良，樂於助人。財官有祿，一生衣食無憂。",
    "庚子": "庚坐子死地，冷靜睿智，不畏困難。有研究精神，但性格較孤獨。",
    "辛丑": "辛坐丑養地，性格溫順，善於理財。晚年亨通，人生平穩。",
    "壬寅": "壬坐寅病地，才華橫溢，喜歡自由。人緣佳，但做事缺乏定力。",
    "癸卯": "癸坐卯長生，聰明可愛，有人緣。衣祿豐盈，性格溫和。",
    "甲辰": "甲坐辰衰地，性格沈穩，注重現實。做事周到，但進取心稍弱。",
    "乙巳": "乙坐巳沐浴，多才多藝，注重形象。桃花旺，感情生活豐富。",
    "丙午": "丙坐午帝旺，陽刃日，氣勢如虹。權威性強，但性格暴躁。",
    "丁未": "丁坐未冠帶，文雅有禮，受人尊敬。做事有條理，晚年幸福。",
    "戊申": "戊坐申病地，聰明伶俐，反應快。事業多動，但易感力不從心。",
    "己酉": "己坐酉長生，文雅出眾，有美感。才華橫溢，受人賞識。",
    "庚戌": "庚坐戌衰地，性格剛正不阿。有修養，但有時過於固執。",
    "辛亥": "辛坐亥沐浴，口才極佳，有感染力。感情豐富，異性緣極佳。",
    "壬子": "壬坐子帝旺，氣勢強盛，不畏艱難。領向力強，一生波折。",
    "癸丑": "癸坐丑冠帶，性格冷靜，有規劃力。做事踏實，晚景更佳。",
    "甲寅": "甲坐寅臨官，性格剛強，有領導力。大器晚成，性格獨立。",
    "乙卯": "乙坐卯臨官，為人溫和，富有同情心。人緣佳，事業平穩。",
    "丙辰": "丙坐辰冠帶，自我意識強，注重儀表。多才多藝，有正義感。",
    "丁巳": "丁坐巳帝旺，熱情奔放，有開創性。事業有成，但性格較急。",
    "戊午": "戊坐午帝旺，陽刃日，剛強武斷。事業有成，但需防衝動。",
    "己未": "己坐未冠帶，為人厚道，做事踏實。晚年享福，有人緣。",
    "庚申": "庚坐申臨官，性格剛正，有執行力。事業有成，但缺乏變通。",
    "辛酉": "辛坐酉臨官，品格高潔，有審美觀。一生平順，有名聲。",
    "壬戌": "壬坐戌冠帶，熱情而沈穩。注重信義，晚年福厚。",
    "癸亥": "癸坐亥帝旺，聰明睿智，志向遠大。人際關係好，一生顯達。"
}


def _get_chang_sheng(gan: str, zhi: str) -> str:
    """取得天干在地支的十二長生狀態"""
    if not gan or not zhi:
        return ""
    if gan not in TIAN_GAN_ZHANG_SHENG:
        return ""
    if zhi not in TIAN_GAN_ZHANG_SHENG.get(gan, {}):
        return ""
    return TIAN_GAN_ZHANG_SHENG[gan][zhi]


def _analyze_gan_zhi(gan: str, zhi: str) -> dict:
    """
    分析干支組合的狀態

    Returns:
        {
            "十二長生": str,
            "狀態描述": str,
            "吉凶": str,
        }
    """
    chang_sheng = _get_chang_sheng(gan, zhi)

    # 十二長生吉凶判斷
    ji_xiong_map = {
        "長生": "吉", "臨官": "吉", "帝旺": "吉", "冠帶": "吉",
        "養": "平", "胎": "平",
        "沐浴": "平", "衰": "平",
        "病": "凶", "死": "凶", "墓": "凶", "絕": "凶",
    }

    # 狀態描述
    desc_map = {
        "長生": "源源不絕，有發展潛力",
        "沐浴": "桃花之地，感情豐富",
        "冠帶": "漸入佳境，注重名譽",
        "臨官": "得祿得位，事業有成",
        "帝旺": "氣勢強盛，精力充沛",
        "衰": "氣勢漸退，穩中求進",
        "病": "多思多慮，易有困擾",
        "死": "氣數已盡，難有作為",
        "墓": "收藏閉塞，不善表達",
        "絕": "絕地逢生，另起爐灶",
        "胎": "新的開始，需要培養",
        "養": "依賴照顧，逐步成長",
    }

    return {
        "十二長生": chang_sheng,
        "狀態描述": desc_map.get(chang_sheng, ""),
        "吉凶": ji_xiong_map.get(chang_sheng, "平"),
    }


def _analyze_liu_qin_status(liu_qin_list: list, day_gan: str, day_zhi: str, gender: str) -> dict:
    """
    分析旬中六親的狀態

    Args:
        liu_qin_list: 六親類化列表
        day_gan: 日天干
        day_zhi: 日地支
        gender: 性別

    Returns:
        {
            "妻子狀態": dict,
            "子女狀態": dict,
            "父母狀態": dict,
            "婚姻判斷": str,
            "六親判斷": str,
        }
    """
    result = {
        "妻子狀態": None,
        "丈夫狀態": None,
        "兒子狀態": None,
        "女兒狀態": None,
        "父親狀態": None,
        "母親狀態": None,
        "婚姻判斷": [],
        "六親判斷": [],
    }

    for lq in liu_qin_list:
        liu_qin_name = lq.get("六親", "")
        gan_zhi = lq.get("干支", "")
        if not gan_zhi or len(gan_zhi) < 2:
            continue

        member_gan = gan_zhi[0]
        member_zhi = gan_zhi[1]
        status = _analyze_gan_zhi(member_gan, member_zhi)
        status["干支"] = gan_zhi

        # 分類存儲
        if liu_qin_name == "妻子":
            result["妻子狀態"] = status
        elif liu_qin_name == "丈夫":
            result["丈夫狀態"] = status
        elif liu_qin_name == "兒子":
            result["兒子狀態"] = status
        elif liu_qin_name == "女兒":
            result["女兒狀態"] = status
        elif liu_qin_name == "父親":
            result["父親狀態"] = status
        elif liu_qin_name == "母親":
            result["母親狀態"] = status

    # 生成婚姻判斷
    is_male = gender == "男"
    if is_male:
        wife = result["妻子狀態"]
        if wife:
            # 妻星狀態分析
            if wife["吉凶"] == "吉":
                result["婚姻判斷"].append(f"妻星坐{wife['十二長生']}，妻有能力")
            elif wife["吉凶"] == "凶":
                if wife["十二長生"] == "絕":
                    result["婚姻判斷"].append("妻星坐絕，妻緣較弱")
                elif wife["十二長生"] == "墓":
                    result["婚姻判斷"].append("妻星入墓，妻多病或緣薄")
                elif wife["十二長生"] == "死":
                    result["婚姻判斷"].append("妻星坐死，婚姻不順")
            else:  # 平
                result["婚姻判斷"].append(f"妻星坐{wife['十二長生']}，{wife['狀態描述']}")
            # 五行分析
            wife_wx = TIAN_GAN_WU_XING.get(wife["干支"][0], "")
            if wife_wx == "火":
                result["婚姻判斷"].append("妻星屬火，性格熱情")
            elif wife_wx == "水":
                result["婚姻判斷"].append("妻星屬水，聰明機智")
            elif wife_wx == "木":
                result["婚姻判斷"].append("妻星屬木，仁慈溫和")
            elif wife_wx == "金":
                result["婚姻判斷"].append("妻星屬金，剛毅果斷")
            elif wife_wx == "土":
                result["婚姻判斷"].append("妻星屬土，穩重踏實")
    else:
        husband = result["丈夫狀態"]
        if husband:
            if husband["吉凶"] == "吉":
                result["婚姻判斷"].append(f"夫星坐{husband['十二長生']}，夫有能力")
            elif husband["吉凶"] == "凶":
                if husband["十二長生"] == "絕":
                    result["婚姻判斷"].append("夫星坐絕，夫緣較弱")
                elif husband["十二長生"] == "墓":
                    result["婚姻判斷"].append("夫星入墓，夫多病或緣薄")
                elif husband["十二長生"] == "死":
                    result["婚姻判斷"].append("夫星坐死，婚姻不順")
            else:  # 平
                result["婚姻判斷"].append(f"夫星坐{husband['十二長生']}，{husband['狀態描述']}")
            # 五行分析
            husband_wx = TIAN_GAN_WU_XING.get(husband["干支"][0], "")
            if husband_wx == "火":
                result["婚姻判斷"].append("夫星屬火，性格熱情")
            elif husband_wx == "水":
                result["婚姻判斷"].append("夫星屬水，聰明機智")
            elif husband_wx == "木":
                result["婚姻判斷"].append("夫星屬木，仁慈溫和")
            elif husband_wx == "金":
                result["婚姻判斷"].append("夫星屬金，剛毅果斷")
            elif husband_wx == "土":
                result["婚姻判斷"].append("夫星屬土，穩重踏實")

    # 生成六親判斷
    # 子女分析
    son = result["兒子狀態"]
    daughter = result["女兒狀態"]
    if son or daughter:
        child_parts = []
        if son and son["吉凶"] == "吉":
            child_parts.append(f"子坐{son['十二長生']}")
        elif son and son["吉凶"] == "凶":
            child_parts.append(f"子坐{son['十二長生']}，子緣較淺")
        if daughter and daughter["吉凶"] == "吉":
            child_parts.append(f"女坐{daughter['十二長生']}")
        elif daughter and daughter["吉凶"] == "凶":
            child_parts.append(f"女坐{daughter['十二長生']}，女緣較淺")
        if child_parts:
            result["六親判斷"].append("，".join(child_parts))

    # 父母分析
    father = result["父親狀態"]
    mother = result["母親狀態"]
    if father or mother:
        parent_parts = []
        if father:
            if father["吉凶"] == "吉":
                parent_parts.append(f"父坐{father['十二長生']}")
            else:
                parent_parts.append(f"父坐{father['十二長生']}，父緣較淺")
        if mother:
            if mother["吉凶"] == "吉":
                parent_parts.append(f"母坐{mother['十二長生']}")
            else:
                parent_parts.append(f"母坐{mother['十二長生']}，母緣較淺")
        if parent_parts:
            result["六親判斷"].append("，".join(parent_parts))

    return result


def _analyze_day_zhi(day_gan: str, day_zhi: str) -> dict:
    """
    分析日支（夫妻宮）的狀態

    Returns:
        {
            "日干狀態": dict,
            "性格判斷": str,
            "健康判斷": str,
            "事業判斷": str,
        }
    """
    day_status = _analyze_gan_zhi(day_gan, day_zhi)

    # 性格判斷（基於十二長生）
    xingge_map = {
        "長生": "好學上進，有仁心，發展潛力大",
        "沐浴": "風流多情，注重外表，異性緣佳",
        "冠帶": "重名譽，有上進心，愛面子",
        "臨官": "穩重踏實，有領導力，能掌權",
        "帝旺": "性格剛強，精力旺盛，主觀意識強",
        "衰": "保守謹慎，穩中求進，不冒險",
        "病": "心思細膩，善於謀劃，多思多慮",
        "死": "固執己見，不善變通，缺乏活力",
        "墓": "內斂深沉，善於收藏，不善表達",
        "絕": "機智應變，適應力強，絕處逢生",
        "胎": "新的開始，需要培養，依賴性強",
        "養": "溫和包容，得人照顧，逐步成長",
    }

    # 健康判斷（基於日干五行）
    wu_xing = TIAN_GAN_WU_XING.get(day_gan, "")
    health_map = {
        "木": "肝膽、筋骨、眼睛、神經系統",
        "火": "心血管、小腸、眼睛、血壓",
        "土": "脾胃、消化系統、皮膚、肌肉",
        "金": "肺、大腸、呼吸系統、皮膚",
        "水": "腎、膀胱、生殖系統、耳、骨",
    }

    # 事業判斷（基於十二長生）
    career_map = {
        "長生": "適合開創性事業，有發展潛力",
        "沐浴": "適合藝術、演藝、美妝行業",
        "冠帶": "適合公職、文教、名譽相關",
        "臨官": "適合管理、公職、獨立經營",
        "帝旺": "適合創業、領導、武職",
        "衰": "適合穩定工作，不宜冒險",
        "病": "適合研究、謀劃、顧問",
        "死": "適合固定工作，不宜變動",
        "墓": "適合研究、收藏、幕後工作",
        "絕": "適合變動性行業、技術工作",
        "胎": "適合學習階段，不宜獨立",
        "養": "適合輔助性工作，得人提攜",
    }

    return {
        "日干狀態": day_status,
        "性格判斷": xingge_map.get(day_status["十二長生"], ""),
        "健康判斷": health_map.get(wu_xing, ""),
        "事業判斷": career_map.get(day_status["十二長生"], ""),
    }


def _check_special_conditions(day_pillar: str, liu_qin_analysis: dict, gender: str) -> list:
    """
    檢查特殊條件（旬首、空亡、神煞等）

    Returns:
        特殊斷語列表
    """
    special = []

    # 旬首檢查
    if day_pillar and day_pillar[0] == "甲":
        special.append("旬首日，如為長男長女吉，否則損同胞")

    # 空亡檢查
    xun_tuple = get_xun(day_pillar) if day_pillar else None
    if xun_tuple:
        xun_name = xun_tuple[0]
        xun_idx = LIU_SHI_JIA_ZI_ORDER.index(xun_name) if xun_name in LIU_SHI_JIA_ZI_ORDER else 0
        kong1 = LIU_SHI_JIA_ZI_ORDER[(xun_idx + 10) % 60][1]
        kong2 = LIU_SHI_JIA_ZI_ORDER[(xun_idx + 11) % 60][1]

        # 檢查六親是否落空亡
        wife = liu_qin_analysis.get("妻子狀態")
        if wife and wife.get("干支", "")[1] in [kong1, kong2]:
            if gender == "男":
                special.append(f"妻星落空亡（{kong1}{kong2}），婚緣遲或薄")

    # 陰陽差錯煞檢查
    yin_yang_cha_cuo = ["丙子", "丁丑", "戊寅", "辛卯", "壬辰", "癸巳",
                        "丙午", "丁未", "戊申", "辛酉", "壬戌", "癸亥"]
    if day_pillar in yin_yang_cha_cuo:
        if gender == "男":
            special.append("陰陽差錯日，與妻家是非寡合")
        else:
            special.append("陰陽差錯日，與夫家緣薄")

    # 孤鸞煞檢查
    gu_luan = ["甲寅", "乙巳", "丙午", "丁巳", "戊午", "戊申", "辛亥", "壬子"]
    if day_pillar in gu_luan:
        if gender == "男":
            special.append("孤鸞煞，剋妻")
        else:
            special.append("孤鸞煞，剋夫")

    return special


def _generate_duan_yu(liu_shi_jia_zi_data: dict, gender: str) -> dict:
    """
    根據六十甲子體象論數據生成斷語
    """
    day_pillar = liu_shi_jia_zi_data.get("日柱", "")
    day_gan = day_pillar[0] if day_pillar else ""
    day_zhi = day_pillar[1] if day_pillar else ""

    # 獲取旬信息
    xun_tuple = get_xun(day_pillar) if day_pillar else None
    xun_name = xun_tuple[0] + "旬" if xun_tuple else ""

    # 計算空亡
    if xun_tuple:
        xun_idx = LIU_SHI_JIA_ZI_ORDER.index(xun_tuple[0]) if xun_tuple[0] in LIU_SHI_JIA_ZI_ORDER else 0
        kong_wang = f"{LIU_SHI_JIA_ZI_ORDER[(xun_idx + 10) % 60][1]}{LIU_SHI_JIA_ZI_ORDER[(xun_idx + 11) % 60][1]}"
    else:
        kong_wang = ""

    # 分析六親狀態
    liu_qin_list = liu_shi_jia_zi_data.get("六親類化", [])
    liu_qin_analysis = _analyze_liu_qin_status(liu_qin_list, day_gan, day_zhi, gender)

    # 分析日支狀態
    day_analysis = _analyze_day_zhi(day_gan, day_zhi)

    # 檢查特殊條件
    special_conditions = _check_special_conditions(day_pillar, liu_qin_analysis, gender)

    # 生成婚姻斷語
    marriage_parts = liu_qin_analysis["婚姻判斷"]
    if not marriage_parts:
        # 如果沒有具體判斷，用日支狀態
        if day_analysis["日干狀態"]["十二長生"]:
            marriage_parts.append(f"日坐{day_analysis['日干狀態']['十二長生']}")
    marriage = "；".join(marriage_parts) if marriage_parts else "以歲運引動論"

    # 生成六親斷語
    liu_qin_parts = liu_qin_analysis["六親判斷"]
    liu_qin = "；".join(liu_qin_parts) if liu_qin_parts else "以歲運引動論"

    # 生成健康斷語
    health = day_analysis["健康判斷"]

    # 生成性格斷語
    personality = day_analysis["性格判斷"]

    # 生成事業斷語
    career = day_analysis["事業判斷"]

    # 生成特殊斷語
    special = "；".join(special_conditions) if special_conditions else ""

    return {
        "日柱": day_pillar,
        "性別": gender,
        "所屬旬": xun_name,
        "空亡": kong_wang,
        "婚姻斷語": marriage,
        "六親斷語": liu_qin,
        "健康斷語": health,
        "性格斷語": personality,
        "事業斷語": career,
        "特殊斷語": special,
    }


def calculate_yi_zhu(day_pillar: str, gender: str = "男") -> dict:
    """
    一柱論命計算（使用六十甲子體象論邏輯）

    Args:
        day_pillar: 日柱干支（如"甲子"）
        gender: 性別

    Returns:
        {
            "日柱": str,
            "所屬旬": str,
            "空亡": str,
            "婚姻斷語": str,
            "六親斷語": str,
            "健康斷語": str,
            "性格斷語": str,
            "事業斷語": str,
            "特殊斷語": str,
        }
    """
    if not day_pillar or day_pillar not in LIU_SHI_JIA_ZI_ORDER:
        return {
            "日柱": day_pillar,
            "所屬旬": "未知",
            "空亡": "未知",
            "婚姻斷語": "暫無數據",
            "六親斷語": "暫無數據",
            "健康斷語": "暫無數據",
            "性格斷語": "暫無數據",
            "事業斷語": "暫無數據",
            "特殊斷語": "暫無數據",
        }

    # 構建簡化八字（只用日柱，其他三柱用假值）
    # 六十甲子體象論只需要日柱來計算旬中六親
    fake_ba_zi = f"甲子 甲子 {day_pillar} 甲子"

    liu_shi_jia_zi_data = calculate_liu_shi_jia_zi(fake_ba_zi, gender)

    # 生成斷語
    duan_yu = _generate_duan_yu(liu_shi_jia_zi_data, gender)

    return duan_yu
