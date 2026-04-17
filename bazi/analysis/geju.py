"""
格局判斷分析模塊

根據講義內容實現格局判斷邏輯：
- 正官格、七殺格、印格、財格、傷官格、食神格、建祿格、月劫格
- 成敗判斷、相神、喜神、忌神
- 根氣被剋判斷、十神性格
"""

from bazi.core.constants import (
    ZHI_CANG_GAN, TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG, WU_XING_SHENG, WU_XING_KE,
    TIAN_GAN_YANG, TIAN_GAN_YIN, ZHI_LIU_CHONG, ZHI_XING, ZHI_CHUAN, ZHI_PO,
    ZHI_WU_XING,
)

# 別名（兼容舊代碼）
ZhiCangGan = ZHI_CANG_GAN
TianGanWuXing = TIAN_GAN_WU_XING
TianGanYinYang = TIAN_GAN_YIN_YANG
WuXingSheng = WU_XING_SHENG
WuXingKe = WU_XING_KE
TianGanYang = TIAN_GAN_YANG
TianGanYin = TIAN_GAN_YIN
ZhiLiuChong = ZHI_LIU_CHONG
ZhiXing = ZHI_XING
ZhiChuan = ZHI_CHUAN
ZhiPo = ZHI_PO
ZhiWuXing = ZHI_WU_XING


def get_shi_shen(gan: str, gan_wuxing: str, gan_yinyang: str,
                 day_gan: str, day_gan_wuxing: str, day_gan_yinyang: str) -> str:
    """
    計算十神關係

    Args:
        gan: 天干
        gan_wuxing: 天干五行
        gan_yinyang: 天干陰陽
        day_gan: 日天干
        day_gan_wuxing: 日天干五行
        day_gan_yinyang: 日天干陰陽

    Returns:
        十神名稱
    """
    # 同五行（比肩、劫財）
    if gan_wuxing == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "比肩"
        else:
            return "劫財"

    # 日主生（食神、傷官）- gan 是日主所生
    if WuXingSheng.get(day_gan_wuxing) == gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "食神"
        else:
            return "傷官"

    # 日主剋（偏財、正財）- gan 是日主所剋
    if WuXingKe.get(day_gan_wuxing) == gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "偏財"
        else:
            return "正財"

    # 剋日主（七殺、正官）- gan 剋日主
    if WuXingKe.get(gan_wuxing) == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "七殺"
        else:
            return "正官"

    # 生日主（偏印、正印）- gan 生日主
    if WuXingSheng.get(gan_wuxing) == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "偏印"
        else:
            return "正印"

    return "未知"


def get_all_gans_in_pillars(pillars: list) -> list:
    """獲取命局所有天干（含藏干）"""
    gans = []
    for p in pillars:
        gans.append(p[0])  # 天干
        zhi = p[1]
        cang_gan = ZhiCangGan.get(zhi, {})
        for qi in ["主氣", "中氣", "餘氣"]:
            if cang_gan.get(qi):
                gans.append(cang_gan[qi])
    return gans


def get_xiang_shen(ge_name: str, day_gan: str, pillars: list,
                   is_auspicious: bool = True, yongshen_gan: str = None) -> dict:
    """
    獲取相神

    **吉神順用**：生用神的五行（如：用神為木，水生木，水為相神）

    **凶神逆用**：1. 剋用神的五行，2. 用神所生的五行
                  兩種相神只能存在一個，否則破格
    """
    all_gans = get_all_gans_in_pillars(pillars)
    day_gan_wuxing = TianGanWuXing.get(day_gan, "")
    day_gan_yinyang = TianGanYinYang.get(day_gan, "")

    # 用神天干的五行
    if yongshen_gan:
        ge_wuxing = TianGanWuXing.get(yongshen_gan, "")
    else:
        # 用神對應的五行（備用）
        ge_wuxing_map = {
            "正官": "金", "七殺": "金",
            "正印": "水", "偏印": "水",
            "正財": "土", "偏財": "土",
            "食神": "火", "傷官": "火",
            "比肩": "木", "劫財": "木",
        }
        ge_wuxing = ge_wuxing_map.get(ge_name, "")

    if not ge_wuxing:
        return {"相神": ["待定"], "破格": False}

    # 生用神的五行
    sheng_ge_wuxing = None
    for src, tgt in WuXingSheng.items():
        if tgt == ge_wuxing:
            sheng_ge_wuxing = src
            break

    # 用神所生的五行
    ge_sheng_wuxing = WuXingSheng.get(ge_wuxing, "")

    # 剋用神的五行
    ke_ge_wuxing = None
    for src, tgt in WuXingKe.items():
        if tgt == ge_wuxing:
            ke_ge_wuxing = src
            break

    xiang_list = []

    # 根據吉凶神確定相神五行
    if is_auspicious:
        # 吉神順用：生用神的五行
        for g in all_gans:
            gw = TianGanWuXing.get(g, "")
            gy = TianGanYinYang.get(g, "")
            rel = get_shi_shen(g, gw, gy, day_gan, day_gan_wuxing, day_gan_yinyang)
            if gw == sheng_ge_wuxing:
                xiang_list.append(rel)
    else:
        # 凶神逆用：1. 剋用神的五行，2. 用神所生的五行
        has_ke_yongshen = False
        has_yongshen_sheng = False

        ke_yongshen_gans = []
        yongshen_sheng_gans = []

        for g in all_gans:
            gw = TianGanWuXing.get(g, "")
            gy = TianGanYinYang.get(g, "")
            rel = get_shi_shen(g, gw, gy, day_gan, day_gan_wuxing, day_gan_yinyang)
            if gw == ke_ge_wuxing:
                has_ke_yongshen = True
                ke_yongshen_gans.append(rel)
            elif gw == ge_sheng_wuxing:
                has_yongshen_sheng = True
                yongshen_sheng_gans.append(rel)

        # 兩種相神同時存在 → 標記為待判定
        if has_ke_yongshen and has_yongshen_sheng:
            xiang_list = list(set(ke_yongshen_gans)) + list(set(yongshen_sheng_gans))
            xiang_list = list(set(xiang_list))
            return {"相神": xiang_list, "破格": False, "待判定": True,
                    "破格原因": "凶神逆用時兩種相神並存，需檢查截腳"}

        if has_ke_yongshen:
            xiang_list = list(set(ke_yongshen_gans))
        elif has_yongshen_sheng:
            xiang_list = list(set(yongshen_sheng_gans))

    xiang_list = list(set(xiang_list))
    return {"相神": xiang_list if xiang_list else ["待定"], "破格": False}


def check_zhi_damaged(zhi: str, zhi_list: list) -> list:
    """檢查地支是否被沖、刑、穿、破"""
    damaged_by = []
    for other_zhi in zhi_list:
        if other_zhi == zhi:
            continue
        # 檢查六沖
        for c1, c2 in ZhiLiuChong:
            if (zhi == c1 and other_zhi == c2) or (zhi == c2 and other_zhi == c1):
                damaged_by.append(f"{other_zhi}沖")
                break
        # 檢查刑
        if zhi + other_zhi in ZhiXing or other_zhi + zhi in ZhiXing:
            damaged_by.append(f"{other_zhi}刑")
        # 檢查穿
        for c1, c2 in ZhiChuan:
            if (zhi == c1 and other_zhi == c2) or (zhi == c2 and other_zhi == c1):
                damaged_by.append(f"{other_zhi}穿")
                break
        # 檢查破
        for c1, c2 in ZhiPo:
            if (zhi == c1 and other_zhi == c2) or (zhi == c2 and other_zhi == c1):
                damaged_by.append(f"{other_zhi}破")
                break
    return damaged_by


def judge_ge_chengbai(ge: str, pillars: list, day_gan: str,
                      month_zhi: str, yongshen_gan: str = None) -> dict:
    """
    判斷格局成敗（根據講義內容更新）

    成格規則：
    - 正官格：佩印（主要）、財生、身健。破格：重官、混殺、逢傷、官逢沖刑穿破
    - 七殺格：食制、傷合、刃合、佩印。破格：財生、混官無去留
    - 印格：官殺生；比劫護衛。破格：財剋、印逢沖刑穿破
    - 財格：食傷生助；官星護衛、身健。破格：比劫奪財、生殺攻身
    - 傷官格：佩印、生財。破格：逢官
    - 食神格：生財；比劫、身健。破格：梟印奪食、食逢沖刑穿破
    """
    analysis = []
    all_gans = get_all_gans_in_pillars(pillars)
    zhi_list = [p[1] for p in pillars]

    # 獲取十神關係
    def get_shi_shen_relation(gan):
        gan_wuxing = TianGanWuXing.get(gan, "")
        gan_yinyang = TianGanYinYang.get(gan, "")
        day_gan_wuxing = TianGanWuXing.get(day_gan, "")
        day_gan_yinyang = TianGanYinYang.get(day_gan, "")
        return get_shi_shen(gan, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang)

    # 統計各十神
    shishen_count = {}
    shishen_gans = {}
    for gan in all_gans:
        ss = get_shi_shen_relation(gan)
        shishen_count[ss] = shishen_count.get(ss, 0) + 1
        if ss not in shishen_gans:
            shishen_gans[ss] = []
        shishen_gans[ss].append(gan)

    # 檢查日主是否有根
    def day_gan_has_root():
        day_gan_wuxing = TianGanWuXing.get(day_gan, "")
        wuxing_to_zhi = {
            "木": ["寅", "卯"], "火": ["巳", "午"], "土": ["辰", "戌", "丑", "未"],
            "金": ["申", "酉"], "水": ["亥", "子"],
        }
        target_zhi = wuxing_to_zhi.get(day_gan_wuxing, [])
        return any(z in target_zhi for z in zhi_list)

    # 檢查六沖
    def has_clash(zhi1, zhi2):
        for c1, c2 in ZhiLiuChong:
            if (zhi1 == c1 and zhi2 == c2) or (zhi1 == c2 and zhi2 == c1):
                return True
        return False

    # 檢查官殺混雜
    def has_guan_sha_hun_za():
        return "正官" in shishen_count and "七殺" in shishen_count

    # 獲取用神根氣地支
    def get_yongshen_genqi_zhi(yongshen):
        if not yongshen:
            return []
        yongshen_wuxing = TianGanWuXing.get(yongshen, "")
        wuxing_to_zhi = {
            "木": ["寅", "卯"], "火": ["巳", "午"], "土": ["辰", "戌", "丑", "未"],
            "金": ["申", "酉"], "水": ["亥", "子"],
        }
        target_zhi = wuxing_to_zhi.get(yongshen_wuxing, [])
        return [z for z in target_zhi if z in zhi_list]

    # ========== 各格局成敗判斷 ==========

    if ge == "正官格":
        has_yin = "正印" in shishen_count or "偏印" in shishen_count
        has_cai = "正財" in shishen_count or "偏財" in shishen_count
        has_shang_guan = "傷官" in shishen_count
        has_qi_sha = "七殺" in shishen_count
        has_gen = day_gan_has_root()
        zhong_guan = shishen_count.get("正官", 0) >= 2
        guan_sha_hun_za = has_guan_sha_hun_za()

        analysis.append(f"有印：{has_yin}, 有財：{has_cai}, 有根：{has_gen}")

        if has_yin:
            if has_shang_guan:
                analysis.append("有印但見傷官，佩印受制")
                conclusion = "半成（佩印受制）"
            else:
                analysis.append("佩印護官，成格")
                conclusion = "成格"
        elif has_cai and not has_shang_guan and not guan_sha_hun_za:
            analysis.append("財星生官，無傷官破格")
            conclusion = "成格"
        elif has_cai and has_shang_guan:
            analysis.append("有財生官但見傷官，需印制傷")
            if has_yin:
                conclusion = "半成（傷官見印）"
            else:
                conclusion = "不成格（傷官破格）"
        elif guan_sha_hun_za:
            analysis.append("官殺混雜，破格")
            conclusion = "破格（官殺混雜）"
        elif zhong_guan:
            analysis.append("重官不貴，破格")
            conclusion = "破格（重官）"
        elif has_shang_guan:
            analysis.append("傷官見官，為禍百端")
            conclusion = "破格（傷官見官）"
        elif has_gen and has_cai:
            analysis.append("身健財生，可成格")
            conclusion = "成格"
        else:
            conclusion = "不成格"

    elif ge == "七殺格":
        has_shi_shen = "食神" in shishen_count
        has_shang_guan = "傷官" in shishen_count
        has_yin = "正印" in shishen_count or "偏印" in shishen_count
        has_jie_cai = "劫財" in shishen_count
        has_cai = "正財" in shishen_count or "偏財" in shishen_count
        has_guan = "正官" in shishen_count

        # 陽刃（只有陽日干才有）
        day_gan_wuxing = TianGanWuXing.get(day_gan, "")
        day_gan_yinyang = TianGanYinYang.get(day_gan, "")
        is_yang_day_gan = day_gan_yinyang == "陽"
        yang_ren_zhi = {"木": "卯", "火": "午", "土": "未", "金": "酉", "水": "子"}.get(day_gan_wuxing, "")
        has_yang_ren = is_yang_day_gan and yang_ren_zhi in zhi_list

        analysis.append(f"食神：{has_shi_shen}, 傷官：{has_shang_guan}, 印：{has_yin}, 劫財：{has_jie_cai}, 陽刃：{has_yang_ren}")

        if has_yin:
            if has_cai:
                analysis.append("殺印相生但財星破印")
                conclusion = "半成（財破印）"
            else:
                analysis.append("殺印相生，成格")
                conclusion = "成格"
        elif has_shi_shen:
            analysis.append("食神制殺，成格")
            conclusion = "成格"
        elif has_jie_cai or has_yang_ren:
            analysis.append("劫財/陽刃合殺，成格")
            conclusion = "成格"
        elif has_cai:
            if not has_yin and not has_shi_shen:
                analysis.append("財滋弱殺，成格")
                conclusion = "成格"
            else:
                analysis.append("財星生殺，破格")
                conclusion = "破格（財生殺）"
        elif has_guan:
            analysis.append("官殺混雜，需去留")
            conclusion = "半成（官殺混雜）"
        else:
            analysis.append("無制化，七殺攻身")
            conclusion = "不成格"

    elif ge in ["正印格", "偏印格"]:
        has_guan_sha = "正官" in shishen_count or "七殺" in shishen_count
        has_bi_jie = "比肩" in shishen_count or "劫財" in shishen_count
        has_cai = "正財" in shishen_count or "偏財" in shishen_count
        has_shi_shang = "食神" in shishen_count or "傷官" in shishen_count
        yin_count = shishen_count.get("正印", 0) + shishen_count.get("偏印", 0)

        analysis.append(f"官殺：{has_guan_sha}, 比劫：{has_bi_jie}, 財星：{has_cai}, 印數：{yin_count}")

        if has_cai and not has_bi_jie:
            analysis.append("財星破印，無比劫救應")
            conclusion = "破格（財破印）"
        elif has_cai and has_bi_jie:
            analysis.append("財破印，幸有比劫制財護印")
            conclusion = "半成（比劫救應）"
        elif has_guan_sha:
            analysis.append("官殺生印，成格")
            conclusion = "成格"
        elif yin_count >= 3 and has_cai:
            analysis.append("印多棄印就財，成格")
            conclusion = "成格（棄印就財）"
        elif yin_count >= 3 and has_shi_shang:
            analysis.append("印多食傷洩秀，成格")
            conclusion = "成格（食傷洩秀）"
        elif has_bi_jie and not has_guan_sha:
            analysis.append("印喜比劫，成格")
            conclusion = "成格"
        elif not has_cai:
            analysis.append("無財破印，可成格")
            conclusion = "成格"
        else:
            conclusion = "不成格"

    elif ge in ["正財格", "偏財格"]:
        has_shi_shang = "食神" in shishen_count or "傷官" in shishen_count
        has_guan = "正官" in shishen_count
        has_sha = "七殺" in shishen_count
        has_yin = "正印" in shishen_count or "偏印" in shishen_count
        has_bi_jie = "比肩" in shishen_count or "劫財" in shishen_count
        has_gen = day_gan_has_root()
        cai_count = shishen_count.get("正財", 0) + shishen_count.get("偏財", 0)

        analysis.append(f"食傷：{has_shi_shang}, 官星：{has_guan}, 比劫：{has_bi_jie}, 有根：{has_gen}, 財數：{cai_count}")

        if has_bi_jie and cai_count >= 3:
            if has_guan or has_sha:
                analysis.append("財多比劫助，但見官殺洩財")
                conclusion = "半成"
            else:
                analysis.append("財多比劫助，成格")
                conclusion = "成格（財喜比劫）"
        elif has_shi_shang and has_gen:
            analysis.append("食傷生財，身健能任")
            conclusion = "成格（食傷生財）"
        elif has_yin and not has_shi_shang:
            if not has_guan and not has_sha:
                analysis.append("財星佩印，無食傷破印")
                conclusion = "成格（財星佩印）"
            else:
                analysis.append("財星佩印但見官殺，財官印相生")
                conclusion = "成格"
        elif has_guan and not has_bi_jie:
            analysis.append("財旺生官，成格")
            conclusion = "成格（財旺生官）"
        elif has_bi_jie and cai_count < 3:
            analysis.append("比劫奪財，破格")
            conclusion = "破格（比劫奪財）"
        elif has_gen and has_shi_shang:
            analysis.append("身健食傷生財，成格")
            conclusion = "成格"
        else:
            conclusion = "不成格"

    elif ge == "傷官格":
        has_yin = "正印" in shishen_count or "偏印" in shishen_count
        has_cai = "正財" in shishen_count or "偏財" in shishen_count
        has_guan = "正官" in shishen_count
        has_sha = "七殺" in shishen_count
        has_bi_jie = "比肩" in shishen_count or "劫財" in shishen_count
        has_gen = day_gan_has_root()
        guan_sha_jin_jue = not has_guan and not has_sha

        analysis.append(f"印：{has_yin}, 財：{has_cai}, 官：{has_guan}, 殺：{has_sha}")

        if has_yin:
            if has_cai:
                analysis.append("傷官佩印但財星破印")
                conclusion = "半成（財破印）"
            else:
                analysis.append("傷官佩印，貴格")
                conclusion = "成格（傷官佩印）"
        elif has_cai and has_gen:
            analysis.append("傷官生財，身健能任")
            conclusion = "成格（傷官生財）"
        elif guan_sha_jin_jue and not has_cai:
            analysis.append("傷官傷盡，不見官星")
            conclusion = "成格（傷官傷盡）"
        elif has_guan and has_yin:
            analysis.append("傷官見官，有印制傷護官")
            conclusion = "半成"
        elif has_guan:
            analysis.append("傷官見官，為禍百端")
            conclusion = "破格（傷官見官）"
        elif has_sha:
            analysis.append("傷官駕殺，以技藝取貴")
            conclusion = "成格（傷官駕殺）"
        elif has_bi_jie:
            analysis.append("比劫生傷，背祿逐馬")
            conclusion = "不成格"
        else:
            analysis.append("無財印制化，傷官洩身太過")
            conclusion = "不成格"

    elif ge == "食神格":
        has_cai = "正財" in shishen_count or "偏財" in shishen_count
        has_sha = "七殺" in shishen_count
        has_bi_jie = "比肩" in shishen_count or "劫財" in shishen_count
        has_yin = "偏印" in shishen_count
        has_zheng_yin = "正印" in shishen_count
        has_guan = "正官" in shishen_count
        has_gen = day_gan_has_root()
        shi_shen_count_num = shishen_count.get("食神", 0)

        analysis.append(f"財：{has_cai}, 殺：{has_sha}, 比劫：{has_bi_jie}, 梟神：{has_yin}")

        if has_yin:
            if has_cai:
                analysis.append("梟神奪食，幸有財星制梟")
                conclusion = "半成（財制梟）"
            else:
                analysis.append("梟神奪食，破格")
                conclusion = "破格（梟神奪食）"
        elif has_cai and has_gen:
            analysis.append("食神生財格")
            conclusion = "成格（食神生財）"
        elif has_sha and has_gen:
            analysis.append("食神制殺，以技藝獲取名利")
            conclusion = "成格（食神制殺）"
        elif has_bi_jie and not has_cai and not has_guan and not has_sha:
            analysis.append("食神喜比劫，體胖富人之格")
            conclusion = "成格（食喜比劫）"
        elif has_zheng_yin and has_guan:
            analysis.append("棄食就印格")
            conclusion = "成格（棄食就印）"
        elif has_gen:
            analysis.append("食神身健，可成格")
            conclusion = "成格"
        else:
            analysis.append("食神洩身太過，身弱難任")
            conclusion = "不成格"

    elif ge == "建祿格":
        has_cai = "正財" in shishen_count or "偏財" in shishen_count
        has_guan_sha = "正官" in shishen_count or "七殺" in shishen_count
        has_shi_shang = "食神" in shishen_count or "傷官" in shishen_count

        if has_cai and has_guan_sha:
            analysis.append("建祿用財官，成格")
            conclusion = "成格"
        elif has_cai:
            analysis.append("建祿生財，成格")
            conclusion = "成格（建祿生財）"
        elif has_guan_sha:
            analysis.append("建祿用官，成格")
            conclusion = "成格（建祿用官）"
        elif has_shi_shang:
            analysis.append("建祿洩秀，以技藝謀生")
            conclusion = "半成"
        else:
            analysis.append("建祿無財官，自立更生")
            conclusion = "不成格"

    elif ge == "月劫格":
        has_guan_sha = "正官" in shishen_count or "七殺" in shishen_count
        has_shi_shang = "食神" in shishen_count or "傷官" in shishen_count
        has_cai = "正財" in shishen_count or "偏財" in shishen_count

        if has_guan_sha:
            analysis.append("官殺制劫，成格")
            conclusion = "成格"
        elif has_shi_shang and has_cai:
            analysis.append("食傷洩秀生財，成格")
            conclusion = "成格（食傷生財）"
        elif has_shi_shang:
            analysis.append("食傷洩秀，以技藝謀生")
            conclusion = "半成"
        else:
            analysis.append("月劫無制，爭奪財官")
            conclusion = "不成格"

    else:
        analysis.append("無法判斷格局")
        conclusion = "普通"

    if not analysis:
        analysis.append("格局資訊不足")

    # 根氣被剋判斷
    ge_name = ge.replace("格", "")
    ji_shens = ["正官", "正印", "偏印", "正財", "偏財", "食神"]
    xiong_shens = ["七殺", "傷官", "比肩", "劫財"]

    # 獲取用神根氣地支（用用神天干來找）
    def get_yongshen_genqi_zhi(yongshen):
        if not yongshen:
            return []
        yongshen_wuxing = TianGanWuXing.get(yongshen, "")
        wuxing_to_zhi = {
            "木": ["寅", "卯"], "火": ["巳", "午"], "土": ["辰", "戌", "丑", "未"],
            "金": ["申", "酉"], "水": ["亥", "子"],
        }
        target_zhi = wuxing_to_zhi.get(yongshen_wuxing, [])
        return [z for z in target_zhi if z in zhi_list]

    # 檢查地支是否被沖、刑、穿、破
    def check_zhi_damaged(target_zhi):
        damaged_by = []
        for other_zhi in zhi_list:
            if other_zhi == target_zhi:
                continue
            # 檢查六沖
            for c1, c2 in ZhiLiuChong:
                if (target_zhi == c1 and other_zhi == c2) or (target_zhi == c2 and other_zhi == c1):
                    damaged_by.append(f"{other_zhi}沖")
                    break
            # 檢查刑
            if (target_zhi + other_zhi) in ZhiXing or (other_zhi + target_zhi) in ZhiXing:
                damaged_by.append(f"{other_zhi}刑")
            # 檢查穿
            for c1, c2 in ZhiChuan:
                if (target_zhi == c1 and other_zhi == c2) or (target_zhi == c2 and other_zhi == c1):
                    damaged_by.append(f"{other_zhi}穿")
                    break
            # 檢查破
            for c1, c2 in ZhiPo:
                if (target_zhi == c1 and other_zhi == c2) or (target_zhi == c2 and other_zhi == c1):
                    damaged_by.append(f"{other_zhi}破")
                    break
        return damaged_by

    # 計算用神根氣地支
    genqi_zhi = get_yongshen_genqi_zhi(yongshen_gan)

    # 檢查每個根氣地支是否被剋
    damaged_genqi = []
    undamaged_genqi = []
    for zhi in genqi_zhi:
        damaged_by = check_zhi_damaged(zhi)
        if damaged_by:
            damaged_genqi.append((zhi, damaged_by))
        else:
            undamaged_genqi.append(zhi)

    # 根氣被剋影響判斷
    root_damage_impact = None

    if ge_name in ji_shens:
        # 吉神：只有一個地支有根氣，但根氣的地支被剋 → 判斷為失敗
        if len(genqi_zhi) == 1 and len(damaged_genqi) == 1:
            zhi, damaged_by = damaged_genqi[0]
            root_damage_impact = {
                "狀態": "根氣被剋",
                "說明": f"吉神唯一根氣「{zhi}」被{', '.join(damaged_by)}，格局失敗",
                "建議": "需從其他透出天干的十神按優先級別查找替代用神"
            }
            conclusion = "破格（根氣被剋）"
            analysis.append(f"【根氣被剋】吉神唯一根氣「{zhi}」被{', '.join(damaged_by)}")
        # 吉神：根氣多於一個，且只有一個被剋 → 不判斷失敗
        elif len(genqi_zhi) > 1 and len(damaged_genqi) == 1:
            zhi, damaged_by = damaged_genqi[0]
            analysis.append(f"【根氣被剋】{zhi}被{', '.join(damaged_by)}，但另有根氣「{','.join(undamaged_genqi)}」不破")
        # 多個根氣被剋
        elif len(damaged_genqi) > 1:
            analysis.append(f"【根氣被剋】多個根氣被剋：{', '.join([z for z, _ in damaged_genqi])}")

    elif ge_name in xiong_shens:
        # 凶神：只有一個地支有根氣，但根氣的地支被剋 → 判斷為損格
        if len(genqi_zhi) == 1 and len(damaged_genqi) == 1:
            zhi, damaged_by = damaged_genqi[0]
            root_damage_impact = {
                "狀態": "根氣被剋",
                "說明": f"凶神唯一根氣「{zhi}」被{', '.join(damaged_by)}，格局受損",
                "建議": "凶神根氣被剋反而減輕凶性，但仍屬損格"
            }
            conclusion = "損格（根氣被剋）"
            analysis.append(f"【根氣被剋】凶神唯一根氣「{zhi}」被{', '.join(damaged_by)}，格局受損")
        # 凶神：根氣多於一個，且只有一個被剋 → 不判斷損格
        elif len(genqi_zhi) > 1 and len(damaged_genqi) == 1:
            zhi, damaged_by = damaged_genqi[0]
            analysis.append(f"【根氣被剋】{zhi}被{', '.join(damaged_by)}，但另有根氣「{','.join(undamaged_genqi)}」不破，不判損格")
        # 多個根氣被剋
        elif len(damaged_genqi) > 1:
            analysis.append(f"【根氣被剋】多個凶神根氣被剋：{', '.join([z for z, _ in damaged_genqi])}")

    return {
        "結論": conclusion,
        "分析": analysis,
        "根氣被剋影響": root_damage_impact,
        "根氣地支": genqi_zhi,
        "被剋根氣": damaged_genqi,
        "完好根氣": undamaged_genqi,
    }


def get_ge_form(ge: str, pillars: list, day_gan: str, all_gans: list) -> list:
    """獲取格局形式（如官印相生、殺印相生、食神生財等）"""
    day_gan_wuxing = TianGanWuXing.get(day_gan, "")
    day_gan_yinyang = TianGanYinYang.get(day_gan, "")

    def get_gan_relation(gan):
        gan_wuxing = TianGanWuXing.get(gan, "")
        gan_yinyang = TianGanYinYang.get(gan, "")
        return get_shi_shen(gan, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang)

    shishen_present = {}
    for gan in all_gans:
        rel = get_gan_relation(gan)
        if rel not in shishen_present:
            shishen_present[rel] = []
        shishen_present[rel].append(gan)

    forms = []

    if ge == "正官格":
        if "正印" in shishen_present or "偏印" in shishen_present:
            forms.append({"形式": "官印相生格", "說明": "以印星護衛正官，文貴之格", "特徵": "適合公職、文教事業"})
        if "正財" in shishen_present or "偏財" in shishen_present:
            if "正印" not in shishen_present and "偏印" not in shishen_present:
                forms.append({"形式": "正官喜財格", "說明": "財星生助正官，富貴雙全", "特徵": "適合商業、金融業"})
        if "傷官" in shishen_present:
            if "正財" not in shishen_present and "偏財" not in shishen_present:
                forms.append({"形式": "棄官就傷格", "說明": "棄官從藝，技藝成名", "特徵": "適合技術、藝術領域"})

    elif ge == "七殺格":
        if "正印" in shishen_present or "偏印" in shishen_present:
            forms.append({"形式": "殺印相生格", "說明": "以印星化殺生身，文貴之格", "特徵": "適合管理、公職"})
        if "食神" in shishen_present:
            forms.append({"形式": "食神制殺格", "說明": "以食神制伏七殺，武貴之格", "特徵": "適合軍警、司法"})
        if "正財" in shishen_present or "偏財" in shishen_present:
            if "正印" not in shishen_present and "偏印" not in shishen_present and "食神" not in shishen_present:
                forms.append({"形式": "財滋弱殺格", "說明": "財星生助七殺，以財取貴", "特徵": "適合商業、企業管理"})
        if "劫財" in shishen_present:
            forms.append({"形式": "殺以劫合格", "說明": "以劫財合殺，化敵為友", "特徵": "適合合作創業"})

    elif ge in ["正印格", "偏印格"]:
        if "正官" in shishen_present or "七殺" in shishen_present:
            forms.append({"形式": "印喜官殺格", "說明": "官殺生印，貴氣顯現", "特徵": "適合公職、管理"})
        if "比肩" in shishen_present or "劫財" in shishen_present:
            forms.append({"形式": "印喜比劫格", "說明": "比劫護印，不畏財剋", "特徵": "適合合作、創業"})
        if "食神" in shishen_present or "傷官" in shishen_present:
            forms.append({"形式": "印喜食傷格", "說明": "食傷洩秀，多才多藝", "特徵": "適合藝術、技術"})
        if "正財" in shishen_present or "偏財" in shishen_present:
            if "正官" not in shishen_present and "七殺" not in shishen_present:
                forms.append({"形式": "棄印就財格", "說明": "棄文從商，經商致富", "特徵": "適合商業、貿易"})

    elif ge in ["正財格", "偏財格"]:
        if "食神" in shishen_present or "傷官" in shishen_present:
            forms.append({"形式": "財喜食傷格", "說明": "食傷生財，經商致富", "特徵": "適合創業、投資"})
        if "正印" in shishen_present or "偏印" in shishen_present:
            forms.append({"形式": "財星佩印格", "說明": "身弱佩印，富而有貴", "特徵": "適合文教、專業"})
        if "比肩" in shishen_present or "劫財" in shishen_present:
            forms.append({"形式": "財喜比劫格", "說明": "身弱財旺，比劫幫身", "特徵": "適合合作求財"})
        if "正官" in shishen_present or "七殺" in shishen_present:
            if "食神" not in shishen_present and "傷官" not in shishen_present:
                forms.append({"形式": "財旺生官格", "說明": "財旺生官，富貴雙全", "特徵": "適合政商兩界"})

    elif ge == "傷官格":
        if "正財" in shishen_present or "偏財" in shishen_present:
            forms.append({"形式": "傷官生財格", "說明": "以技藝得財，富格", "特徵": "適合技術、專業"})
        if "正印" in shishen_present or "偏印" in shishen_present:
            forms.append({"形式": "傷官佩印格", "說明": "印制傷官，貴格", "特徵": "適合文教、管理"})
        if "正官" in shishen_present or "七殺" in shishen_present:
            forms.append({"形式": "傷官喜官格", "說明": "傷官見官，交戰之象", "特徵": "多變、適合自由業"})
        if "正官" not in shishen_present and "七殺" not in shishen_present:
            if "正財" not in shishen_present and "偏財" not in shishen_present:
                forms.append({"形式": "傷官制官格", "說明": "傷官傷盡，不忌見官", "特徵": "適合改革、開創"})

    elif ge == "食神格":
        if "正財" in shishen_present or "偏財" in shishen_present:
            forms.append({"形式": "食神生財格", "說明": "食神生財，以技得財", "特徵": "適合技術、餐飲"})
        if "七殺" in shishen_present:
            forms.append({"形式": "食神制殺格", "說明": "食神制殺，技藝成名", "特徵": "適合專業、技術"})
        if "比肩" in shishen_present or "劫財" in shishen_present:
            forms.append({"形式": "食喜比劫格", "說明": "身旺食神，富態之格", "特徵": "適合穩定行業"})
        if "正印" in shishen_present or "偏印" in shishen_present:
            if "正財" not in shishen_present and "偏財" not in shishen_present:
                forms.append({"形式": "棄食就印格", "說明": "棄藝從文，貴格", "特徵": "適合文教、研究"})

    elif ge == "建祿格":
        if "正財" in shishen_present or "偏財" in shishen_present:
            forms.append({"形式": "建祿生財格", "說明": "身旺生財，自手起家", "特徵": "適合創業"})
        if "正官" in shishen_present or "七殺" in shishen_present:
            forms.append({"形式": "建祿用官格", "說明": "身旺用官，貴氣顯現", "特徵": "適合公職"})

    elif ge == "月劫格":
        if "正官" in shishen_present or "七殺" in shishen_present:
            forms.append({"形式": "官殺制劫格", "說明": "以官殺制約劫財", "特徵": "適合管理、紀律"})
        if "食神" in shishen_present or "傷官" in shishen_present:
            forms.append({"形式": "食傷泄秀格", "說明": "以食傷洩秀氣", "特徵": "適合藝術、表達"})

    if not forms:
        return [{"形式": "普通格", "說明": "無特殊形式", "特徵": "平穩"}]

    return forms


def get_ji_shen_shishen(ge_name: str) -> list:
    """
    獲取忌神對應的十神名稱

    忌神：破壞格局的十神
    """
    ji_shen_map = {
        "正官": ["傷官", "七殺"],
        "七殺": ["正財", "偏財", "正官"],
        "正印": ["正財", "偏財"],
        "偏印": ["食神"],
        "正財": ["比肩", "劫財"],
        "偏財": ["比肩", "劫財"],
        "傷官": ["正官"],
        "食神": ["偏印"],
        "比肩": ["正官", "七殺"],
        "劫財": ["正官", "七殺"],
        "建祿": ["比肩", "劫財"],
        "月劫": ["比肩", "劫財"],
    }
    return ji_shen_map.get(ge_name, [])


# 十神心性描述（從十神訣提取，根據講義 09_十神訣.docx）
SHISHEN_PERSONALITY = {
    "正官": {
        "正面": "知禮守法、自律自制、秉公尚義、品行端正磊落、做事認真、具名譽心、自尊心重",
        "負面": "自我壓抑、呆板保守、膽小怕事、優柔寡斷、諂媚逢迎、貪圖虛名",
        "簡化": "名氣、壓力、規範、名譽、地位、責任、管理、權力",
    },
    "七殺": {
        "正面": "膽氣、魄力、霸氣、心機、殺氣、勇敢、機智、伶俐、機警、多疑、急躁",
        "負面": "偏激、陰沉、膽怯、萎靡、狡猾多變、詭計多端、虛詐不實、貪戀酒色",
        "簡化": "天災、人禍、壓力、戰爭、武職、軍警、司法、小人、災病",
    },
    "正印": {
        "正面": "尊重傳統、以德報怨、惜情念舊、注重涵養、溫文儒雅、知足淡泊、愛惜面子、慈善、文靜、信仰宗教",
        "負面": "依賴成性、懶惰無為、貪生怕死、不務實際、食古不化、喜歡空想、自恃清高、常生悶氣、包庇過失、吝嗇迂腐",
        "簡化": "庇蔭、文飾、文化、安全、穩定、母親、老師、神明、學歷、文憑",
    },
    "偏印": {
        "正面": "機智敏銳、思想怪異、鬥志高昂、領悟力強、創造力強、應變力強、淡泊名利",
        "負面": "孤僻、不合群、言行怪異、內向多疑、喜怒無常、刻薄寡情、愛恨極端、厭惡世俗",
        "簡化": "非正規資訊、非常規技藝、偏門學術、兼職、特殊技能、繼母",
    },
    "正財": {
        "正面": "勤儉務實、恪守本分、明辨是非、不使心機、公正嚴明",
        "負面": "吝嗇、貪婪、懦弱、世俗、刻薄、愚魯、缺乏修養、重財輕義、重色輕友、膽小怕事",
        "簡化": "財物、薪資、資源、妻子 (男)、勤儉、務實",
    },
    "偏財": {
        "正面": "人緣佳、機智敏銳、性偏急躁、喜歡一步到位、慷慨大方、仗義輕財、樂心助人、精於投機、善於交際、活動力強",
        "負面": "貪財好色、放縱情慾、輕挑浮華、玩世不恭、好賭好嫖、奢侈浪費、虛詐不實",
        "簡化": "意外財物、投機、獎金、情人 (男)、交際、慷慨、企業家",
    },
    "食神": {
        "正面": "清高、溫和、內向、多情、聰敏、度量寬大、貪口福、好享受、行為脫俗、言語流暢、思想清新",
        "負面": "任性、倔強、懶散、孤僻、被動、多愁善感、不專心、欠缺靈活、無親和力、外華內虛",
        "簡化": "吃喝、才華、溫和、享受、藝術、烹飪、福氣、長壽",
    },
    "傷官": {
        "正面": "外向、熱情、精力充沛、多才多藝、領悟力高、創造力強、敢於創新、追求完美",
        "負面": "叛逆任性、多疑善變、心懷叵測、肆意妄為、博學不精、志大才疏、喜新厭舊、眼高手低、憤世嫉俗",
        "簡化": "才華、魅力、自由、任性、創造、表現、藝術、改革",
    },
    "比肩": {
        "正面": "得人氣、自信有為、獨立自主、樂觀進取、坦蕩不虛偽、剛健不急切、自尊心強、公平競爭、變通不足",
        "負面": "失人氣、喜爭鬥、魯莽不雅、攻擊性強、固執己見、心浮氣躁、自制力差、不服管束、目中無人、投機取巧",
        "簡化": "朋友、同事、合作、競爭、兄弟 (男)、自立、人氣",
    },
    "劫財": {
        "正面": "精力充沛、熱情坦率、雄心勃勃、永不服輸、獨立頑強、佔有慾強、臨機應變、善於交際、雙重性格",
        "負面": "反覆無常、想做就做、膽大妄為、魯莽無禮、剛強粗野、攻擊性強、對親人冷漠、情緒無常",
        "簡化": "朋友、投機、競爭、姐妹 (男)、揮霍、野心、投機者",
    },
}


def _calculate_day_gan_genqi(day_gan: str, pillars: list) -> int:
    """計算日干根氣強度"""
    day_gan_wuxing = TianGanWuXing.get(day_gan, "")

    # 五行對應的地支
    wuxing_to_zhi = {
        "木": ["寅", "卯"],
        "火": ["巳", "午"],
        "土": ["辰", "戌", "丑", "未"],
        "金": ["申", "酉"],
        "水": ["亥", "子"],
    }

    target_zhi = wuxing_to_zhi.get(day_gan_wuxing, [])
    zhi_list = [p[1] for p in pillars]

    # 計算根氣強度（月支 4 > 時支 3 > 日支 2 > 年支 1）
    genqi_score = 0
    genqi_weights = {"年支": 1, "月支": 4, "日支": 2, "時支": 3}
    pillar_names = ["年支", "月支", "日支", "時支"]

    for i, zhi in enumerate(zhi_list):
        if zhi in target_zhi:
            genqi_score += genqi_weights[pillar_names[i]]

    return genqi_score


def _get_shishen_gans(shishen_name: str, day_gan: str) -> list:
    """根據十神名稱和日干獲取對應的天干"""
    day_gan_wuxing = TianGanWuXing.get(day_gan, "")
    day_gan_yinyang = TianGanYinYang.get(day_gan, "")

    # 十神對應的五行和陰陽
    shishen_map = {
        "正官": ("金" if day_gan_wuxing == "木" else
                "水" if day_gan_wuxing == "火" else
                "木" if day_gan_wuxing == "土" else
                "火" if day_gan_wuxing == "金" else "土", "異性"),
        "七殺": ("金" if day_gan_wuxing == "木" else
                "水" if day_gan_wuxing == "火" else
                "木" if day_gan_wuxing == "土" else
                "火" if day_gan_wuxing == "金" else "土", "同性"),
        "正印": ("水" if day_gan_wuxing == "木" else
                "木" if day_gan_wuxing == "火" else
                "火" if day_gan_wuxing == "土" else
                "土" if day_gan_wuxing == "金" else "金", "異性"),
        "偏印": ("水" if day_gan_wuxing == "木" else
                "木" if day_gan_wuxing == "火" else
                "火" if day_gan_wuxing == "土" else
                "土" if day_gan_wuxing == "金" else "金", "同性"),
        "正財": ("土" if day_gan_wuxing == "木" else
                "金" if day_gan_wuxing == "火" else
                "水" if day_gan_wuxing == "土" else
                "木" if day_gan_wuxing == "金" else "火", "異性"),
        "偏財": ("土" if day_gan_wuxing == "木" else
                "金" if day_gan_wuxing == "火" else
                "水" if day_gan_wuxing == "土" else
                "木" if day_gan_wuxing == "金" else "火", "同性"),
        "食神": ("火" if day_gan_wuxing == "木" else
                "土" if day_gan_wuxing == "火" else
                "金" if day_gan_wuxing == "土" else
                "水" if day_gan_wuxing == "金" else "木", "同性"),
        "傷官": ("火" if day_gan_wuxing == "木" else
                "土" if day_gan_wuxing == "火" else
                "金" if day_gan_wuxing == "土" else
                "水" if day_gan_wuxing == "金" else "木", "異性"),
        "比肩": (day_gan_wuxing, day_gan_yinyang),
        "劫財": (day_gan_wuxing, "陰" if day_gan_yinyang == "陽" else "陽"),
    }

    target_wuxing, target_yinyang = shishen_map.get(shishen_name, (None, None))
    if not target_wuxing:
        return []

    # 找出對應的天干
    result = []
    for gan, wuxing in TianGanWuXing.items():
        if wuxing == target_wuxing:
            gan_yinyang = TianGanYinYang.get(gan, "")
            if target_yinyang == "異性":
                if gan_yinyang != day_gan_yinyang:
                    result.append(gan)
            elif target_yinyang == "同性":
                if gan_yinyang == day_gan_yinyang:
                    result.append(gan)
            else:
                result.append(gan)
    return result


def _get_shishen_wuxing(shishen_name: str, day_gan: str) -> str:
    """根據十神名稱和日干獲取對應的五行"""
    day_gan_wuxing = TianGanWuXing.get(day_gan, "")

    # 十神對應的五行
    shishen_wuxing_map = {
        "正官": "金" if day_gan_wuxing == "木" else
                "水" if day_gan_wuxing == "火" else
                "木" if day_gan_wuxing == "土" else
                "火" if day_gan_wuxing == "金" else "土",
        "七殺": "金" if day_gan_wuxing == "木" else
                "水" if day_gan_wuxing == "火" else
                "木" if day_gan_wuxing == "土" else
                "火" if day_gan_wuxing == "金" else "土",
        "正印": "水" if day_gan_wuxing == "木" else
                "木" if day_gan_wuxing == "火" else
                "火" if day_gan_wuxing == "土" else
                "土" if day_gan_wuxing == "金" else "金",
        "偏印": "水" if day_gan_wuxing == "木" else
                "木" if day_gan_wuxing == "火" else
                "火" if day_gan_wuxing == "土" else
                "土" if day_gan_wuxing == "金" else "金",
        "正財": "土" if day_gan_wuxing == "木" else
                "金" if day_gan_wuxing == "火" else
                "水" if day_gan_wuxing == "土" else
                "木" if day_gan_wuxing == "金" else "火",
        "偏財": "土" if day_gan_wuxing == "木" else
                "金" if day_gan_wuxing == "火" else
                "水" if day_gan_wuxing == "土" else
                "木" if day_gan_wuxing == "金" else "火",
        "食神": "火" if day_gan_wuxing == "木" else
                "土" if day_gan_wuxing == "火" else
                "金" if day_gan_wuxing == "土" else
                "水" if day_gan_wuxing == "金" else "木",
        "傷官": "火" if day_gan_wuxing == "木" else
                "土" if day_gan_wuxing == "火" else
                "金" if day_gan_wuxing == "土" else
                "水" if day_gan_wuxing == "金" else "木",
        "比肩": day_gan_wuxing,
        "劫財": day_gan_wuxing,
    }

    return shishen_wuxing_map.get(shishen_name, "")


def _check_shishen_tian_gan_ke(shishen_gans: list, pillars: list, day_gan: str) -> bool:
    """檢查十神天干是否受剋（顯性）"""
    if not shishen_gans:
        return False

    tian_gan_list = [p[0] for p in pillars]

    # 檢查是否有剋制該十神的天干存在
    for gan in shishen_gans:
        gan_wuxing = TianGanWuXing.get(gan, "")
        ke_wuxing = WuXingKe.get(gan_wuxing, "")  # 剋該五行的五行

        # 檢查是否有天干屬於剋制五行
        for other_gan in tian_gan_list:
            if other_gan == gan:
                continue
            other_wuxing = TianGanWuXing.get(other_gan, "")
            if other_wuxing == ke_wuxing:
                return True

    return False


def _check_shishen_genqi_ke(shishen_name: str, shishen_gans: list, pillars: list, day_gan: str) -> bool:
    """檢查十神地支根氣是否受剋（隱性）"""
    if not shishen_gans:
        return False

    # 獲取十神五行對應的根氣地支
    shishen_wuxing = TianGanWuXing.get(shishen_gans[0], "")
    wuxing_to_zhi = {
        "木": ["寅", "卯"],
        "火": ["巳", "午"],
        "土": ["辰", "戌", "丑", "未"],
        "金": ["申", "酉"],
        "水": ["亥", "子"],
    }
    genqi_zhi = wuxing_to_zhi.get(shishen_wuxing, [])
    zhi_list = [p[1] for p in pillars]

    # 檢查命局中存在的根氣
    present_genqi = [z for z in genqi_zhi if z in zhi_list]

    if not present_genqi:
        return False

    # 檢查每個根氣是否被沖/刑/穿/破
    for zhi in present_genqi:
        for other_zhi in zhi_list:
            if other_zhi == zhi:
                continue
            # 檢查六沖
            for c1, c2 in ZhiLiuChong:
                if (zhi == c1 and other_zhi == c2) or (zhi == c2 and other_zhi == c1):
                    return True
            # 檢查刑
            if zhi + other_zhi in ZhiXing or other_zhi + zhi in ZhiXing:
                return True
            # 檢查穿
            for c1, c2 in ZhiChuan:
                if (zhi == c1 and other_zhi == c2) or (zhi == c2 and other_zhi == c1):
                    return True
            # 檢查破
            for c1, c2 in ZhiPo:
                if (zhi == c1 and other_zhi == c2) or (zhi == c2 and other_zhi == c1):
                    return True

    return False


def calculate_shishen_personality(ge_name: str, xiang_shen: list, ji_shen_shishen: list,
                                   pillars: list, day_gan: str) -> dict:
    """
    計算十神性格

    Args:
        ge_name: 格局名稱
        xiang_shen: 相神列表
        ji_shen_shishen: 忌神十神列表
        pillars: 四柱列表
        day_gan: 日天干

    Returns:
        十神性格字典
    """
    # 計算日干旺衰（根氣強度）
    ri_gan_genqi = _calculate_day_gan_genqi(day_gan, pillars)
    is_shen_wang = ri_gan_genqi >= 5  # 根氣 >= 5 為身旺

    result = {}

    # 對每個十神進行判斷
    for shishen_name, desc in SHISHEN_PERSONALITY.items():
        # 判斷該十神是相神還是忌神
        is_xiang_shen = shishen_name in xiang_shen
        is_ji_shen = shishen_name in ji_shen_shishen

        # 獲取該十神對應的天干（用於檢查是否受剋）
        shishen_gans = _get_shishen_gans(shishen_name, day_gan)

        # 檢查天干是否受剋（顯性）
        tian_gan_ke_zhi = _check_shishen_tian_gan_ke(shishen_gans, pillars, day_gan)

        # 檢查地支根氣是否受剋（隱性）
        genqi_ke_zhi = _check_shishen_genqi_ke(shishen_name, shishen_gans, pillars, day_gan)

        # 綜合判斷是否受剋
        is_ke_zhi = tian_gan_ke_zhi or genqi_ke_zhi

        # 判斷心性表現
        if is_xiang_shen:
            # 相神
            if is_ke_zhi:
                # 相神被剋 → 轉為負面
                xing_xing = desc["負面"]
                xing_xing_type = "相神被剋（負面）"
                is_positive = False
            else:
                # 相神不受剋 → 正面
                xing_xing = desc["正面"]
                xing_xing_type = "相神（正面）"
                is_positive = True
        elif is_ji_shen:
            # 忌神
            if is_ke_zhi:
                # 忌神被剋 → 轉為正面
                xing_xing = desc["正面"]
                xing_xing_type = "忌神被制（正面）"
                is_positive = True
            else:
                # 忌神無制 → 負面
                xing_xing = desc["負面"]
                xing_xing_type = "忌神（負面）"
                is_positive = False
        else:
            # 非相神非忌神，簡化顯示
            xing_xing = desc["簡化"]
            xing_xing_type = "其他"
            is_positive = None

        # 身旺衰影響
        wang_shuai_note = ""
        if is_xiang_shen or is_ji_shen:
            if is_shen_wang:
                wang_shuai_note = "身旺，心性發揮充分"
            else:
                wang_shuai_note = "身衰，心性發揮受限"

        result[shishen_name] = {
            "狀態": xing_xing_type,
            "是否為相神": is_xiang_shen,
            "是否為忌神": is_ji_shen,
            "是否受剋": is_ke_zhi,
            "天干受剋": tian_gan_ke_zhi,
            "地支受剋": genqi_ke_zhi,
            "心性描述": xing_xing,
            "正面描述": desc["正面"],
            "負面描述": desc["負面"],
            "類型": "正面" if is_positive else ("負面" if is_positive is False else "其他"),
            "身旺衰說明": wang_shuai_note,
            "身旺": is_shen_wang,
            "根氣強度": ri_gan_genqi,
        }

    return result


def calculate_geju(ba_zi: str, canggan: dict, day_gan: str, month_zhi: str,
                   pillars: list) -> dict:
    """
    計算格局判斷

    定格優先級（根據講義）：
    1. 天干官殺優先 - 檢查年、月、時柱天干是否有正官/七殺
    2. 官殺混雜 - 陰日干以七殺定格，陽日干官殺混雜破格
    3. 月支藏干透干 - 本氣→中氣→餘氣，四庫土必須透干
    4. 月令同五行 - 優先找其他天干：官殺 > 財 > 食傷 > 比劫
    5. 外格 - 從財格等

    Args:
        ba_zi: 八字字符串
        canggan: 藏干字典
        day_gan: 日天干
        month_zhi: 月支
        pillars: 四柱列表

    Returns:
        格局判斷字典
    """
    # 從月支本氣定格
    ZhiGeJu = {
        "子": {"本氣": "癸", "中氣": None, "餘氣": None, "本氣格局": "正官"},
        "丑": {"本氣": "己", "中氣": "癸", "餘氣": "辛", "本氣格局": "食神"},
        "寅": {"本氣": "甲", "中氣": "丙", "餘氣": "戊", "本氣格局": "七殺"},
        "卯": {"本氣": "乙", "中氣": None, "餘氣": None, "本氣格局": "七殺"},
        "辰": {"本氣": "戊", "中氣": "乙", "餘氣": "癸", "本氣格局": "偏印"},
        "巳": {"本氣": "丙", "中氣": "戊", "餘氣": "庚", "本氣格局": "正印"},
        "午": {"本氣": "丁", "中氣": "己", "餘氣": None, "本氣格局": "正印"},
        "未": {"本氣": "己", "中氣": "丁", "餘氣": "乙", "本氣格局": "傷官"},
        "申": {"本氣": "庚", "中氣": "壬", "餘氣": "戊", "本氣格局": "七殺"},
        "酉": {"本氣": "辛", "中氣": None, "餘氣": None, "本氣格局": "正官"},
        "戌": {"本氣": "戊", "中氣": "辛", "餘氣": "丁", "本氣格局": "食神"},
        "亥": {"本氣": "壬", "中氣": "甲", "餘氣": None, "本氣格局": "正印"},
    }

    # 獲取日干五行和陰陽
    day_gan_wuxing = TianGanWuXing.get(day_gan, "")
    day_gan_yinyang = TianGanYinYang.get(day_gan, "")

    # 陰日干列表
    yin_day_gan = ["乙", "丁", "己", "辛", "癸"]
    is_yin_day = day_gan in yin_day_gan

    # 獲取月支藏干信息
    zhi_info = ZhiGeJu.get(month_zhi, {})
    month_zhi_benqi = zhi_info.get("本氣")
    month_zhi_zhongqi = zhi_info.get("中氣")
    month_zhi_yuqi = zhi_info.get("餘氣")

    # 四庫土（辰戌丑未）
    si_ku_zhi = ["辰", "戌", "丑", "未"]

    # 獲取所有天干（含藏干）
    all_gans = get_all_gans_in_pillars(pillars)

    # 獲取其他天干（年、月、時柱天干，不包括日干）
    year_pillar = pillars[0]
    month_pillar = pillars[1]
    hour_pillar = pillars[3]
    other_gans = [year_pillar[0], month_pillar[0], hour_pillar[0]]

    # ========== 第一步：統計天干中的正官和七殺 ==========
    zhengguan_count = 0
    qisha_count = 0
    zhengguan_gans = []
    qisha_gans = []

    for gan in other_gans:
        gan_wuxing = TianGanWuXing.get(gan, "")
        gan_yinyang = TianGanYinYang.get(gan, "")
        relation = get_shi_shen(gan, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang)
        if relation == "正官":
            zhengguan_count += 1
            zhengguan_gans.append(gan)
        elif relation == "七殺":
            qisha_count += 1
            qisha_gans.append(gan)

    # ========== 第二步：官殺混雜判斷 ==========
    is_guansha_hunza = zhengguan_count > 0 and qisha_count > 0

    priority_ge = None
    priority_gan = None
    priority_source = None

    if is_guansha_hunza:
        if is_yin_day:
            # 陰日干以七殺定格
            priority_ge = "七殺格"
            priority_gan = qisha_gans[0]
            priority_source = "天干(官殺混雜以殺定格)"
        else:
            # 陽日干官殺混雜破格
            priority_ge = "破格(官殺混雜)"
            priority_gan = None
            priority_source = "官殺混雜"
    elif zhengguan_count > 0:
        priority_ge = "正官格"
        priority_gan = zhengguan_gans[0]
        priority_source = "天干"
    elif qisha_count > 0:
        priority_ge = "七殺格"
        priority_gan = qisha_gans[0]
        priority_source = "天干"

    # ========== 第三步：月支藏干透干判斷 ==========
    def is_gan_present_in_tian_gan(gan, pillars):
        """只檢查天干是否出現在年、月、時柱天干中，不包括日干"""
        for i, pillar in enumerate(pillars):
            if i == 2:  # 跳過日柱
                continue
            if gan == pillar[0]:
                return True
        return False

    if not priority_ge:
        def can_use_as_ge(gan):
            # 四庫土必須透干才能以土定格
            if month_zhi in si_ku_zhi:
                benqi_wuxing = TianGanWuXing.get(month_zhi_benqi, "")
                if benqi_wuxing == "土":
                    return is_gan_present_in_tian_gan(gan, pillars)
            return is_gan_present_in_tian_gan(gan, pillars)

        # 按本氣→中氣→餘氣順序檢查
        # 注意：月支本氣如果是日干本身，不算透干
        if month_zhi_benqi and month_zhi_benqi != day_gan and can_use_as_ge(month_zhi_benqi):
            gan_wuxing = TianGanWuXing.get(month_zhi_benqi, "")
            gan_yinyang = TianGanYinYang.get(month_zhi_benqi, "")
            priority_ge = get_shi_shen(month_zhi_benqi, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang) + "格"
            priority_gan = month_zhi_benqi
            priority_source = "月支本氣"
        elif month_zhi_zhongqi and month_zhi_zhongqi != day_gan and can_use_as_ge(month_zhi_zhongqi):
            gan_wuxing = TianGanWuXing.get(month_zhi_zhongqi, "")
            gan_yinyang = TianGanYinYang.get(month_zhi_zhongqi, "")
            priority_ge = get_shi_shen(month_zhi_zhongqi, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang) + "格"
            priority_gan = month_zhi_zhongqi
            priority_source = "月支中氣"
        elif month_zhi_yuqi and month_zhi_yuqi != day_gan and can_use_as_ge(month_zhi_yuqi):
            gan_wuxing = TianGanWuXing.get(month_zhi_yuqi, "")
            gan_yinyang = TianGanYinYang.get(month_zhi_yuqi, "")
            priority_ge = get_shi_shen(month_zhi_yuqi, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang) + "格"
            priority_gan = month_zhi_yuqi
            priority_source = "月支餘氣"

    # ========== 第四步：月令主氣（月支與日干同五行）==========
    if not priority_ge:
        month_zhi_wuxing_map = {
            "寅": "木", "卯": "木", "巳": "火", "午": "火",
            "申": "金", "酉": "金", "亥": "水", "子": "水",
            "辰": "土", "戌": "土", "丑": "土", "未": "土",
        }
        month_zhi_wuxing = month_zhi_wuxing_map.get(month_zhi, "")

        if month_zhi_wuxing == day_gan_wuxing:
            # 月令和日干同五行
            # 優先：正官、七殺 > 偏財、正財 > 食神、傷官 > 比肩、劫財
            other_gans_priority = [month_pillar[0], hour_pillar[0], year_pillar[0]]

            # 優先找官殺
            for gan in other_gans_priority:
                gan_wuxing = TianGanWuXing.get(gan, "")
                gan_yinyang = TianGanYinYang.get(gan, "")
                rel = get_shi_shen(gan, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang)
                if rel in ["正官", "七殺"]:
                    priority_ge = rel + "格"
                    priority_gan = gan
                    priority_source = "月令同五行(官殺)"
                    break

            # 沒官殺，找偏財正財
            if not priority_ge:
                for gan in other_gans_priority:
                    gan_wuxing = TianGanWuXing.get(gan, "")
                    gan_yinyang = TianGanYinYang.get(gan, "")
                    rel = get_shi_shen(gan, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang)
                    if rel in ["偏財", "正財"]:
                        priority_ge = rel + "格"
                        priority_gan = gan
                        priority_source = "月令同五行(透出)"
                        break

            # 沒偏財正財，找食神傷官
            if not priority_ge:
                for gan in other_gans_priority:
                    gan_wuxing = TianGanWuXing.get(gan, "")
                    gan_yinyang = TianGanYinYang.get(gan, "")
                    rel = get_shi_shen(gan, gan_wuxing, gan_yinyang, day_gan, day_gan_wuxing, day_gan_yinyang)
                    if rel in ["食神", "傷官"]:
                        priority_ge = rel + "格"
                        priority_gan = gan
                        priority_source = "月令同五行(透出)"
                        break

            # 沒有官殺也沒有其他十神，看有沒有同五行的天干
            if not priority_ge:
                same_wuxing_gan = [g for g in other_gans_priority if TianGanWuXing.get(g, "") == day_gan_wuxing]
                if same_wuxing_gan:
                    same_yy = [g for g in same_wuxing_gan if TianGanYinYang.get(g, "") == day_gan_yinyang]
                    if same_yy:
                        priority_ge = "比肩格" if day_gan_yinyang == "陽" else "劫財格"
                        priority_gan = same_yy[0]
                    else:
                        priority_ge = "劫財格" if day_gan_yinyang == "陽" else "比肩格"
                        priority_gan = same_wuxing_gan[0]
                    priority_source = "月令同五行"

            # 最後才用月令主氣（建祿/月劫）
            if not priority_ge:
                # 陽日干 → 建祿格，陰日干 → 月劫格
                if day_gan_yinyang == "陽":
                    priority_ge = "建祿格"
                else:
                    priority_ge = "月劫格"
                priority_gan = month_zhi_benqi
                priority_source = "月令主氣"

    # ========== 第五步：外格判斷 ==========
    if not priority_ge:
        # 從財格：財星 >= 3 個
        cai_count = sum(1 for g in all_gans if TianGanWuXing.get(g, "") == WuXingKe.get(day_gan_wuxing, ""))
        if cai_count >= 3:
            priority_ge = "從財格"
            priority_gan = "財"
            priority_source = "外格(從財)"

    # 無格局
    if not priority_ge:
        priority_ge = "無格局"
        priority_gan = None
        priority_source = "無可用格局"

    ge = priority_ge

    # 判斷格局成敗
    chengbai_result = judge_ge_chengbai(ge, pillars, day_gan, month_zhi, priority_gan)

    # 獲取相神
    ge_name = ge.replace("格", "").replace("(官殺混雜)", "").replace("破格", "")
    ji_shens = ["正官", "正印", "偏印", "正財", "偏財", "食神"]
    xiong_shens = ["七殺", "傷官", "比肩", "劫財"]

    if ge_name in ji_shens:
        is_auspicious = True
        use_type = "順用"
    elif ge_name in xiong_shens:
        is_auspicious = False
        use_type = "逆用"
    else:
        is_auspicious = None
        use_type = "待定"

    xiang_shen_result = get_xiang_shen(ge_name, day_gan, pillars, is_auspicious, priority_gan)
    xiang_shen_list = xiang_shen_result.get("相神", [])

    # 獲取格局形式
    forms = get_ge_form(ge, pillars, day_gan, all_gans)

    # 獲取忌神
    ji_shen_shishen = get_ji_shen_shishen(ge_name)

    # 計算喜神（相神 + 生助相神的五行）
    xi_shen_shishen = []
    for xs in xiang_shen_list:
        if xs not in xi_shen_shishen:
            xi_shen_shishen.append(xs)

    # 計算十神性格
    shishen_personality = calculate_shishen_personality(
        ge_name,
        xiang_shen_list,
        ji_shen_shishen,
        pillars,
        day_gan
    )

    # 計算喜神/忌神（天干和五行）
    xi_shen_gans = []  # 喜神天干列表
    xi_shen_wuxing_list = []  # 喜神五行列表
    ji_shen_gans = []  # 忌神天干列表
    ji_shen_wuxing_list = []  # 忌神五行列表

    # 用神五行
    yong_shen_wuxing = TianGanWuXing.get(priority_gan, "") if priority_gan else ""

    # 喜神天干：相神對應的天干 + 生助相神的五行對應的天干
    for xs in xiang_shen_list:
        if xs == "待定":
            continue
        # 找到對應的天干
        xs_gans = _get_shishen_gans(xs, day_gan)
        for gan in xs_gans:
            if gan not in xi_shen_gans and gan in all_gans:
                xi_shen_gans.append(gan)
                wx = TianGanWuXing.get(gan, "")
                if wx and wx not in xi_shen_wuxing_list:
                    xi_shen_wuxing_list.append(wx)

    # 生助相神的五行為喜神
    for xs in xiang_shen_list:
        if xs == "待定":
            continue
        xs_wuxing = _get_shishen_wuxing(xs, day_gan)
        if xs_wuxing:
            # 找生助相神的五行
            for src, tgt in WuXingSheng.items():
                if tgt == xs_wuxing:
                    # 如果生助相神的五行是用神五行或用神所生的五行（財星），不加入喜神
                    if src == yong_shen_wuxing:
                        continue
                    for gan in all_gans:
                        if TianGanWuXing.get(gan, "") == src and gan not in xi_shen_gans:
                            xi_shen_gans.append(gan)
                            if src not in xi_shen_wuxing_list:
                                xi_shen_wuxing_list.append(src)
                    break

    # 忌神天干：剋制相神的五行對應的天干
    for xs in xiang_shen_list:
        if xs == "待定":
            continue
        xs_wuxing = _get_shishen_wuxing(xs, day_gan)
        if xs_wuxing:
            # 找剋制相神的五行
            for src, tgt in WuXingKe.items():
                if tgt == xs_wuxing:
                    for gan in all_gans:
                        if TianGanWuXing.get(gan, "") == src and gan != day_gan and gan not in ji_shen_gans:
                            # 如果該五行本身是相神的五行，不列為忌神（兩種相神並存時）
                            if src in xi_shen_wuxing_list:
                                continue
                            ji_shen_gans.append(gan)
                            if src not in ji_shen_wuxing_list:
                                ji_shen_wuxing_list.append(src)
                    break

    # 檢查相神衝突（凶神逆用時兩種相神並存）
    xiang_shen_chongtu = ""
    xiong_shen_po_ge = False
    po_ge_yuan_yin = ""
    jie_jiao_pan_duan = ""

    if not is_auspicious and xiang_shen_result.get("待判定"):
        xiang_shen_chongtu = "凶神逆用時兩種相神並存，需檢查截腳"
        # 檢查截腳
        if priority_gan:
            for pillar in pillars:
                if pillar[0] == priority_gan:
                    tg = pillar[0]
                    zhi = pillar[1]
                    tg_wx = TianGanWuXing.get(tg, "")
                    zhi_wx = ZhiWuXing.get(zhi, "")
                    # 截腳：地支剋天干
                    if WuXingKe.get(zhi_wx) == tg_wx:
                        jie_jiao_pan_duan = f"{tg}坐{zhi}為截腳"
                        xiong_shen_po_ge = True
                        po_ge_yuan_yin = "截腳破格"
                    break

    return {
        "格局類型": "原局",  # 新增：標記為原局格局
        "月支": month_zhi,
        "月支本氣": month_zhi_benqi,
        "月支中氣": month_zhi_zhongqi,
        "月支餘氣": month_zhi_yuqi,
        "格局": ge,
        "格局形式": forms,
        "用神": priority_gan or "",
        "用神性質": "吉神" if is_auspicious else ("凶神" if is_auspicious is False else "中性"),
        "用神方式": use_type,
        "用神五行": TianGanWuXing.get(priority_gan, "") if priority_gan else "",
        "相神": xiang_shen_list,
        "相神衝突": xiang_shen_chongtu,
        "凶神破格": xiong_shen_po_ge,
        "破格原因": po_ge_yuan_yin,
        "截腳判斷": jie_jiao_pan_duan,
        "喜神": xi_shen_gans,
        "喜神五行": xi_shen_wuxing_list,
        "喜神十神": xi_shen_shishen,
        "忌神": ji_shen_gans,
        "忌神五行": ji_shen_wuxing_list,
        "忌神十神": ji_shen_shishen,
        "成敗": chengbai_result["結論"],
        "成敗分析": chengbai_result["分析"],
        "根氣被剋影響": chengbai_result.get("根氣被剋影響"),
        "根氣地支": chengbai_result.get("根氣地支", []),
        "被剋根氣": chengbai_result.get("被剋根氣", []),
        "定格來源": priority_source,
        "十神性格": shishen_personality,
    }


# =============================================================================
# 兩格並存判斷（歲運進階功能）
# 來源：補充資料.docx
# =============================================================================

def calculate_liang_ge_bing_cun(ba_zi: str, ge_ju: dict) -> dict:
    """
    兩格並存判斷

    根據補充資料.docx：
    - 雙格局：同一個八字存在兩個或以上格局
    - 兩種格局個別論吉凶，兩種格局個別論成格或破格
    - 這種命式只要有其中一格沒破，就不真正的破格
    - 兩格都成格就看大運支持哪一格？就論那一格

    Args:
        ba_zi: 八字字符串
        ge_ju: 格局判斷結果（來自 calculate_geju）

    Returns:
        {
            "雙格局": str,
            "說明": str,
        }
    """
    # 獲取原局格局信息
    ge_name = ge_ju.get("格局", "無格局")

    # 檢查是否有雙格局（後續開發完整邏輯）
    # 目前暫显示原局格局
    if ge_name and ge_name != "無格局":
        shuang_ge_ju = f"{ge_name}"
    else:
        shuang_ge_ju = "無格局"

    return {
        "雙格局": shuang_ge_ju,
        "說明": "同一個八字存在兩個或以上格局。兩種格局個別論吉凶，兩種格局個別論成格或破格。這種命式只要有其中一格沒破，就不真正的破格。兩格都成格就看大運支持哪一格。",
    }


def _analyze_side_geju(pillars: list, main_ge_ju: dict) -> dict:
    """
    分析單邊格局（左邊或右邊）

    Args:
        pillars: 兩柱列表
        main_ge_ju: 主格局判斷結果

    Returns:
        {
            "格局": str,
            "成格": bool,
            "說明": str,
        }
    """
    if len(pillars) != 2:
        return {"格局": "無", "成格": False, "說明": "柱數不足"}

    # 取第二柱的地支為月令（對左邊是年支，對右邊是日支）
    zhi = pillars[1][1]

    # 檢查是否有主氣
    from bazi.core.constants import ZHI_CANG_GAN
    cang_gan = ZHI_CANG_GAN.get(zhi, {})
    ben_qi = cang_gan.get("主氣", "") if isinstance(cang_gan, dict) else ""

    # 檢查天干透出
    tian_gan_tou_chu = pillars[0][0]

    if not ben_qi:
        return {"格局": "無", "成格": False, "說明": "無主氣"}

    # 簡化成格判斷
    # 實際上應該重複 calculate_geju 的邏輯，這裡簡化處理
    cheng_ge = True  # 預設成格
    ge_name = "待定格"

    return {
        "格局": ge_name,
        "成格": cheng_ge,
        "說明": f"{pillars[0]}-{pillars[1]}，主氣{ben_qi}，天干{tian_gan_tou_chu}",
    }
