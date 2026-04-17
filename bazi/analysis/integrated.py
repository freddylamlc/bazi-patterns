"""
整合分析模塊 - 以格局為核心的綜合分析
"""


def calculate_integrated_analysis(
    ba_zi: str,
    ge_ju: dict,
    gong_wei: dict,
    zhi_relations: dict,
    dayun_pan_duan: dict,
    liunian_pan_duan: dict,
    bing_yuan: dict = None,
    bazi_gua: dict = None
) -> dict:
    """
    整合分析：以格局為核心

    以格局判斷為核心輸出，其他所有分析圍繞格局結果作為輔助解讀

    Args:
        ba_zi: 八字字符串
        ge_ju: 格局判斷結果
        gong_wei: 宮位分析結果
        zhi_relations: 地支關係
        dayun_pan_duan: 大運判斷結果
        liunian_pan_duan: 流年判斷結果

    Returns:
        整合分析結果字典
    """
    from bazi.core.constants import TIAN_GAN_WU_XING

    ba_zi_parts = ba_zi.split()
    day_gan = ba_zi_parts[2][0]  # 日柱的天干

    # 提取格局核心資訊
    ge_name = ge_ju.get("格局", "無格局")
    yongshen = ge_ju.get("用神", "")
    yongshen_xingzhi = ge_ju.get("用神性質", "中性")
    xiangshen = ge_ju.get("相神", [])
    xishen = ge_ju.get("喜神", [])
    jishen = ge_ju.get("忌神", [])
    ge_chengbai = ge_ju.get("成敗", "")
    chengbai_fenxi = ge_ju.get("成敗分析", "")

    # 用神天干的五行
    yongshen_wuxing = TIAN_GAN_WU_XING.get(yongshen, "") if yongshen else ""

    # 直接使用格局判斷中計算好的喜神忌神
    xishen_jishen_info = {
        "喜神": ge_ju.get("喜神", []),
        "喜神十神": ge_ju.get("喜神十神", []),
        "忌神": ge_ju.get("忌神", []),
        "忌神十神": ge_ju.get("忌神十神", []),
        "忌神五行": ge_ju.get("忌神五行", []),
    }

    # 宮位解讀（以格局為核心）
    def interpret_gongwei_with_geju():
        """根據格局解讀宮位"""
        result = {}
        gongwei = gong_wei

        # 獲取用神、忌神所在的天干
        yongshen_gan = yongshen
        jishen_list = jishen

        for key, value in gongwei.items():
            if isinstance(value, dict):
                gan = value.get("天干", "")
                zhi = value.get("地支", "")

                # 判斷該宮位與格局的關係
                if gan == yongshen_gan:
                    jiedu = "用神宮位-格局用神所在"
                elif gan in jishen_list:
                    jiedu = "忌神宮位-格局忌神所在"
                elif "六親" in key:
                    # 根據六親類型判斷
                    if "父母" in key:
                        jiedu = "父母宮"
                    elif "配偶" in key:
                        jiedu = "配偶宮"
                    elif "子女" in key:
                        jiedu = "子女宮"
                    else:
                        jiedu = "六親宮位"
                else:
                    jiedu = "一般宮位"

                result[key] = {**value, "格局解讀": jiedu}

        return result

    # 地支關係影響（以格局為核心）
    def interpret_zhi_relations_with_geju():
        """根據格局解讀地支關係"""
        result = {}

        # 獲取格局相關的地支
        month_zhi = ba_zi_parts[1][1]
        day_zhi = ba_zi_parts[2][1]

        for rel_type, rel_data in zhi_relations.items():
            if isinstance(rel_data, list):
                new_rel_data = []
                for item in rel_data:
                    if isinstance(item, dict):
                        zhi1 = item.get("地支一", "")
                        zhi2 = item.get("地支二", "")

                        # 判斷對格局的影響
                        impact = "無直接影響"
                        if zhi1 == month_zhi or zhi2 == month_zhi:
                            impact = "月支關係-影響格局根基"
                        elif zhi1 == day_zhi or zhi2 == day_zhi:
                            impact = "日支關係-影響日主"

                        # 根據關係類型判斷
                        if "合" in rel_type:
                            impact = impact + "-合來助力" if "月支" in impact or "日支" in impact else impact
                        elif "沖" in rel_type:
                            impact = impact + "-沖動變化" if "月支" in impact or "日支" in impact else impact
                        elif "刑" in rel_type:
                            impact = impact + "-刑動消耗" if "月支" in impact or "日支" in impact else impact

                        new_item = {**item, "格局影響": impact}
                        new_rel_data.append(new_item)
                    else:
                        new_rel_data.append(item)
                result[rel_type] = new_rel_data
            else:
                result[rel_type] = rel_data

        return result

    # 大運解讀（以格局為核心）- 直接使用 dayun_pan_duan 的格局影響
    def interpret_dayun_with_geju():
        """直接使用大運判斷中計算好的格局影響"""
        result = []
        dayun = dayun_pan_duan.get("十個大運分析", [])

        for dy in dayun:
            if isinstance(dy, dict):
                # 直接使用大運判斷中計算好的格局影響
                ge_impact = dy.get("格局影響", "平穩")
                new_dy = {**dy, "格局影響": ge_impact}
                result.append(new_dy)
            else:
                result.append(dy)

        return result

    # 流年解讀（以格局為核心）- 直接使用 liunian_pan_duan 的格局影響
    def interpret_liunian_with_geju():
        """直接使用流年判斷中計算好的格局影響"""
        result = []
        liunian = liunian_pan_duan.get("流年分析", [])

        for ln in liunian:
            if isinstance(ln, dict):
                # 直接使用流年判斷中計算好的格局影響
                ge_impact = ln.get("格局影響", "平穩")
                new_ln = {**ln, "格局影響": ge_impact}
                result.append(new_ln)
            else:
                result.append(ln)

        return result

    # 1. 提取十神組合斷語 (從 API 返回的數據結構中提取)
    combinations = []

    # 獲取各柱天干十神
    # 結構推導：ge_ju 有時不帶十神，我們直接嘗試從傳入的參數或全局查找
    # 在 calculator.py 中，shi_shen 已經計算好

    # 嘗試獲取所有柱的天干十神（排除日主）
    # 這裡我們通過傳入的 ba_zi 計算出的十神來識別
    from bazi.calculations.shishen import get_shi_shen
    tian_gan_shishen = []

    # 年干、月干、時干的十神
    for i in [0, 1, 3]:
        gan = ba_zi_parts[i][0]
        s = get_shi_shen(gan, day_gan)
        if s: tian_gan_shishen.append(s)

    # 邏輯判斷
    if ("正官" in tian_gan_shishen or "七殺" in tian_gan_shishen) and ("正印" in tian_gan_shishen or "偏印" in tian_gan_shishen):
        combinations.append({"組合": "官殺配印", "斷語": "柱中有官殺有印星化解或護衛，主為人聰明有謀略，利於公職與名聲。"})

    if "傷官" in tian_gan_shishen and ("正官" in tian_gan_shishen or "七殺" in tian_gan_shishen):
        combinations.append({"組合": "傷官見官", "斷語": "四柱天干傷官與官星並見。主性格清高、不服約束，才華橫溢但工作中需防是非。"})

    if ("正財" in tian_gan_shishen or "偏財" in tian_gan_shishen) and ("正官" in tian_gan_shishen or "七殺" in tian_gan_shishen):
        combinations.append({"組合": "財官相生", "斷語": "財能生官，主事業根基穩固，具備領導潛質，財運亦佳。"})

    if "食神" in tian_gan_shishen and ("正財" in tian_gan_shishen or "偏財" in tian_gan_shishen):
        combinations.append({"組合": "食神生財", "斷語": "食神為財之源。主口才好、食祿豐富，且具備優秀的掙錢能力。"})

    if ("劫財" in tian_gan_shishen or "比肩" in tian_gan_shishen) and ("正財" in tian_gan_shishen or "偏財" in tian_gan_shishen):
        combinations.append({"組合": "比劫奪財", "斷語": "天干比劫與財星同存。主為人豪爽大方，但日常開支較大，需注意理財規劃。"})

    if not combinations:
        # 如果天干組合不明顯，檢查地支（選配）
        combinations.append({"組合": "格局中和", "斷語": "天干十神搭配勻稱，性格穩健，凡事能持之以恆，一生平穩。"})

    # 2. 健康建議邏輯
    health_suggestions = "建議：平時應注意起居有常，多接觸五行所喜之色彩與環境。"
    if bing_yuan:
        health_list = bing_yuan.get("五行過旺", {}).get("列表", [])
        if health_list:
            health_suggestions = f"分析您五行中 {health_list[0]['五行']} 過旺，對應 {health_list[0]['臟腑']} 壓力較大。建議：{bing_yuan.get('建議', '注意均衡飲食。')}"
        else:
            health_suggestions = bing_yuan.get("建議", "注意平衡五行，規律作息。")

    # 構建整合輸出
    integrated = {
        "十神組合斷語": combinations,
        "健康分析": {
            "生活調理": health_suggestions
        },
        "格局核心": {
            "格局": ge_name,
            "用神": yongshen,
            "用神五行": yongshen_wuxing,
            "用神性質": yongshen_xingzhi,
            "相神": xiangshen,
            "喜神": xishen_jishen_info.get("喜神", []),
            "喜神十神": xishen_jishen_info.get("喜神十神", []),
            "喜神五行": ge_ju.get("喜神五行", []),
            "忌神": xishen_jishen_info.get("忌神", []),
            "忌神十神": xishen_jishen_info.get("忌神十神", []),
            "忌神五行": xishen_jishen_info.get("忌神五行", []),
            "成敗": ge_chengbai,
            "成敗分析": chengbai_fenxi,
            "格局脈絡": {
                "定格來源": ge_ju.get("定格來源", ""),
                "用神方式": ge_ju.get("用神方式", ""),
                "相神衝突": ge_ju.get("相神衝突", ""),
                "吉凶神數": f"吉{ge_ju.get('吉神數', 0)}凶{ge_ju.get('凶神數', 0)}",
            },
        },
        "格局解讀": {
            "用神解讀": f"{yongshen}為格局用神，屬{yongshen_xingzhi}，五行{yongshen_wuxing}，喜{', '.join(xishen_jishen_info.get('喜神十神', []))}" if yongshen else "無明確用神",
            "忌神解讀": f"忌{', '.join(xishen_jishen_info.get('忌神十神', []))}" if xishen_jishen_info.get("忌神十神") else "無明確忌神",
        },
        "宮位解讀": interpret_gongwei_with_geju(),
        "地支關係影響": interpret_zhi_relations_with_geju(),
        "大運分析": interpret_dayun_with_geju(),
        "流年分析": interpret_liunian_with_geju(),
    }

    return integrated