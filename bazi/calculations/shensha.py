"""
神煞計算模塊 - 區分實用神煞和參考神煞
"""

from bazi.core.constants import (
    TAI_JI_GUI_REN, HONG_YAN, YANG_REN, FEI_REN,
    TIAN_YI_GUI_REN, YI_MA, TAO_HUA, JIANG_XING, HUA_GAI,
    JIE_SHA, WANG_SHEN, WEN_CHANG, TIAN_DE, YUE_DE,
    HONG_LUAN, TIAN_XI, PI_TOU, JIAN_FENG,
    XUE_TANG, YUE_DE_HE, KUI_GANG, YIN_YANG_SHA, SAN_SHA_KU,
    GAN_ZHI_KONG_WANG
)


def calculate_shensha_for_day_gan(day_gan: str, zhi_list: list) -> list:
    """
    計算日干對應的實用神煞

    Args:
        day_gan: 日天干
        zhi_list: 地支列表

    Returns:
        神煞列表
    """
    results = []

    # 太極貴人
    tai_ji_zhis = TAI_JI_GUI_REN.get(day_gan, [])
    for zhi in zhi_list:
        if zhi in tai_ji_zhis:
            results.append({"神煞": "太極貴人", "地支": zhi, "位置": zhi, "說明": "主研究哲理、玄學、宗教，與神佛有緣"})

    # 紅艷
    hong_yan_zhi = HONG_YAN.get(day_gan, "")
    if hong_yan_zhi and hong_yan_zhi in zhi_list:
        results.append({"神煞": "紅艷", "地支": hong_yan_zhi, "位置": hong_yan_zhi, "說明": "主風流多情，人緣佳，異性緣旺"})

    # 陽刃（日干對照）
    yang_ren_zhi = YANG_REN.get(day_gan, "")
    if yang_ren_zhi and yang_ren_zhi in zhi_list:
        results.append({"神煞": "陽刃", "地支": yang_ren_zhi, "位置": yang_ren_zhi, "說明": "主性格剛烈，膽大妄為，易衝動"})

    # 飛刃（陽刃的六沖位）
    fei_ren_zhi = FEI_REN.get(day_gan, "")
    if fei_ren_zhi and fei_ren_zhi in zhi_list:
        results.append({"神煞": "飛刃", "地支": fei_ren_zhi, "位置": fei_ren_zhi, "說明": "主意外血光，外傷，手術"})

    # 文昌
    wen_chang_zhi = WEN_CHANG.get(day_gan, "")
    if wen_chang_zhi and wen_chang_zhi in zhi_list:
        results.append({"神煞": "文昌貴人", "地支": wen_chang_zhi, "位置": wen_chang_zhi, "說明": "主文藝才能，聰明好學，多才多藝"})

    return results


def calculate_shensha_for_nian_zhi(nian_zhi: str, zhi_list: list) -> list:
    """
    計算年支對應的神煞

    Args:
        nian_zhi: 年支
        zhi_list: 地支列表

    Returns:
        神煞列表
    """
    results = []

    # 驛馬
    yi_ma_zhi = YI_MA.get(nian_zhi, "")
    if yi_ma_zhi and yi_ma_zhi in zhi_list:
        results.append({"神煞": "驛馬", "地支": yi_ma_zhi, "位置": yi_ma_zhi, "說明": "主移動、奔波、遠行、變動"})

    # 桃花（年支對照）
    tao_hua_zhis = TAO_HUA.get(nian_zhi, [])
    for zhi in zhi_list:
        if zhi in tao_hua_zhis:
            results.append({"神煞": "桃花", "地支": zhi, "位置": zhi, "說明": "主情慾、人緣、藝術才華"})

    # 將星
    jiang_xing_zhi = JIANG_XING.get(nian_zhi, "")
    if jiang_xing_zhi and jiang_xing_zhi in zhi_list:
        results.append({"神煞": "將星", "地支": jiang_xing_zhi, "位置": jiang_xing_zhi, "說明": "主領導能力，權威"})

    # 華蓋（年支對照）
    hua_gai_zhi = HUA_GAI.get(nian_zhi, "")
    if hua_gai_zhi and hua_gai_zhi in zhi_list:
        results.append({"神煞": "華蓋", "地支": hua_gai_zhi, "位置": hua_gai_zhi, "說明": "主思想獨特，與神佛有緣"})

    # 劫煞
    jie_sha_zhi = JIE_SHA.get(nian_zhi, "")
    if jie_sha_zhi and jie_sha_zhi in zhi_list:
        results.append({"神煞": "劫煞", "地支": jie_sha_zhi, "位置": jie_sha_zhi, "說明": "主破財、劫難"})

    # 亡神
    wang_shen_zhi = WANG_SHEN.get(nian_zhi, "")
    if wang_shen_zhi and wang_shen_zhi in zhi_list:
        results.append({"神煞": "亡神", "地支": wang_shen_zhi, "位置": wang_shen_zhi, "說明": "主失脫、亡失"})

    # 披頭
    pi_tou_zhi = PI_TOU.get(nian_zhi, "")
    if pi_tou_zhi and pi_tou_zhi in zhi_list:
        results.append({"神煞": "披頭", "地支": pi_tou_zhi, "位置": pi_tou_zhi, "說明": "主喪事、孝服"})

    # 劍鋒
    jian_feng_zhi = JIAN_FENG.get(nian_zhi, "")
    if jian_feng_zhi and jian_feng_zhi in zhi_list:
        results.append({"神煞": "劍鋒", "地支": jian_feng_zhi, "位置": jian_feng_zhi, "說明": "主血光、外傷"})

    return results


def calculate_shensha_for_ri_zhi(ri_zhi: str, zhi_list: list) -> list:
    """
    計算日支對應的神煞

    Args:
        ri_zhi: 日支
        zhi_list: 地支列表

    Returns:
        神煞列表
    """
    results = []

    # 桃花（日支對照）
    tao_hua_zhis = TAO_HUA.get(ri_zhi, [])
    for zhi in zhi_list:
        if zhi in tao_hua_zhis:
            results.append({"神煞": "桃花", "地支": zhi, "位置": zhi, "說明": "主情慾、人緣、藝術才華"})

    # 華蓋（日支對照）
    hua_gai_zhi = HUA_GAI.get(ri_zhi, "")
    if hua_gai_zhi and hua_gai_zhi in zhi_list:
        results.append({"神煞": "華蓋", "地支": hua_gai_zhi, "位置": hua_gai_zhi, "說明": "主思想獨特，與神佛有緣"})

    # 紅鸞
    hong_luan_zhi = HONG_LUAN.get(ri_zhi, "")
    if hong_luan_zhi and hong_luan_zhi in zhi_list:
        results.append({"神煞": "紅鸞", "地支": hong_luan_zhi, "位置": hong_luan_zhi, "說明": "主婚喜、喜事"})

    # 天喜
    tian_xi_zhi = TIAN_XI.get(ri_zhi, "")
    if tian_xi_zhi and tian_xi_zhi in zhi_list:
        results.append({"神煞": "天喜", "地支": tian_xi_zhi, "位置": tian_xi_zhi, "說明": "主喜慶、吉祥"})

    return results


def calculate_shensha_for_yue_zhi(yue_zhi: str, gan_list: list) -> list:
    """
    計算月支對應的神煞

    Args:
        yue_zhi: 月支
        gan_list: 天干列表

    Returns:
        神煞列表
    """
    results = []

    # 天德貴人
    tian_de_gan = TIAN_DE.get(yue_zhi, "")
    if tian_de_gan and tian_de_gan in gan_list:
        results.append({"神煞": "天德貴人", "天干": tian_de_gan, "位置": tian_de_gan, "說明": "至吉之神，主福祿壽考"})

    # 月德貴人
    yue_de_gan = YUE_DE.get(yue_zhi, "")
    if yue_de_gan and yue_de_gan in gan_list:
        results.append({"神煞": "月德貴人", "天干": yue_de_gan, "位置": yue_de_gan, "說明": "主福份深，有人緣，貴人多"})

    # 月德合
    yue_de_he_gan = YUE_DE_HE.get(yue_zhi, "")
    if yue_de_he_gan and yue_de_he_gan in gan_list:
        results.append({"神煞": "月德合", "天干": yue_de_he_gan, "位置": yue_de_he_gan, "說明": "主女貴人相助"})

    return results


def calculate_shensha_for_ri_gan(ri_gan: str) -> list:
    """
    計算日干對應的參考神煞

    Args:
        ri_gan: 日天干

    Returns:
        神煞列表
    """
    results = []

    # 學堂
    xue_tang_zhi = XUE_TANG.get(ri_gan, "")
    results.append({"神煞": "學堂", "地支": xue_tang_zhi, "位置": xue_tang_zhi, "說明": "主聰明智慧，利學習"})

    return results


def calculate_kui_gang(ri_pillar: str) -> list:
    """
    計算魁罡

    Args:
        ri_pillar: 日柱

    Returns:
        魁罡列表
    """
    results = []

    if ri_pillar in KUI_GANG:
        results.append({"神煞": "魁罡", "日柱": ri_pillar, "位置": ri_pillar, "說明": "主性格剛烈、聲宏氣壯、大嗓頭、不服輸、擅決斷"})

    return results


def calculate_kong_wang(ri_pillar: str, zhi_list: list) -> list:
    """
    計算空亡

    Args:
        ri_pillar: 日柱
        zhi_list: 地支列表

    Returns:
        空亡列表
    """
    results = []

    kong_wang_zhis = GAN_ZHI_KONG_WANG.get(ri_pillar, ())
    for zhi in zhi_list:
        if zhi in kong_wang_zhis:
            results.append({"神煞": "空亡", "地支": zhi, "位置": zhi, "說明": "隱匿消散的虛無之星，主聰明，易在玄學哲學宗教有成就"})

    return results


def calculate_shensha(ba_zi: str) -> dict:
    """
    計算八字神煞（區分實用神煞和參考神煞）

    Args:
        ba_zi: 八字字符串

    Returns:
        神煞字典
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    # 提取天干和地支
    gan_list = [p[0] for p in ba_zi_parts]
    zhi_list = [p[1] for p in ba_zi_parts]

    nian_zhi = zhi_list[0]
    yue_zhi = zhi_list[1]
    ri_zhi = zhi_list[2]
    ri_gan = gan_list[2]

    shi_yong_shen_sha = []
    can_kao_shen_sha = []

    # 實用神煞
    shi_yong_shen_sha.extend(calculate_shensha_for_day_gan(ri_gan, zhi_list))
    shi_yong_shen_sha.extend(calculate_shensha_for_nian_zhi(nian_zhi, zhi_list))
    shi_yong_shen_sha.extend(calculate_shensha_for_ri_zhi(ri_zhi, zhi_list))
    shi_yong_shen_sha.extend(calculate_shensha_for_yue_zhi(yue_zhi, gan_list))

    # 參考神煞
    can_kao_shen_sha.extend(calculate_shensha_for_ri_gan(ri_gan))
    can_kao_shen_sha.extend(calculate_kui_gang(ba_zi_parts[2]))
    can_kao_shen_sha.extend(calculate_kong_wang(ba_zi_parts[2], zhi_list))

    # 陰陽煞、三煞庫（參考神煞）
    yin_yang_sha_zhi = YIN_YANG_SHA.get(yue_zhi, "")
    if yin_yang_sha_zhi and yin_yang_sha_zhi in zhi_list:
        can_kao_shen_sha.append({"神煞": "陰陽煞", "地支": yin_yang_sha_zhi, "位置": yin_yang_sha_zhi, "說明": "陰陽交錯，主感情波折"})

    san_sha_ku_zhi = SAN_SHA_KU.get(nian_zhi, "")
    if san_sha_ku_zhi and san_sha_ku_zhi in zhi_list:
        can_kao_shen_sha.append({"神煞": "三煞庫", "地支": san_sha_ku_zhi, "位置": san_sha_ku_zhi, "說明": "主財庫，但也帶煞氣"})

    return {
        "實用神煞": shi_yong_shen_sha,
        "參考神煞": can_kao_shen_sha,
        "神煞總數": len(shi_yong_shen_sha) + len(can_kao_shen_sha),
    }
