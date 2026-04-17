"""
大運計算模塊 - 計算大運信息和詳細大運
"""

import math
from bazi.core.constants import (
    TIAN_GAN_WU_XING,
    TIAN_GAN_YIN_YANG,
    ZHI_CANG_GAN,
    TIAN_GAN_ZHANG_SHENG,
    GAN,
    ZHI,
)


def calculate_da_yun_info(ba_zi: str, gender: str, lunar_date) -> str:
    """
    計算大運基本信息

    Args:
        ba_zi: 八字字符串
        gender: 性別（"男" 或 "女"）
        lunar_date: sxtwl 庫的農曆日期對象

    Returns:
        大運信息字符串，如 "陽男，順排，起運時間5年6月，6歲起运"
    """
    # 獲取年干
    year_gz = ba_zi[:2]
    year_tg = year_gz[0]

    # 判斷年干陰陽
    yang_tian_gan = ["甲", "丙", "戊", "庚", "壬"]
    is_year_tg_yang = year_tg in yang_tian_gan

    # 判斷性别
    is_male = gender == "男"

    # 判斷大运顺逆排
    # 陽男陰女順排，陰男陽女逆排
    is_forward = (is_year_tg_yang and is_male) or (not is_year_tg_yang and not is_male)
    da_yun_direction = "順排" if is_forward else "逆排"

    # 計算起運時間
    # 首先獲取節氣信息
    current_day = lunar_date

    if is_forward:
        # 順排：查找下一個節氣
        jie_qi_day = current_day
        days_to_jie_qi = 0

        # 向后查找最多30天
        for i in range(30):
            if jie_qi_day.hasJieQi():
                break
            jie_qi_day = jie_qi_day.after(1)
            days_to_jie_qi += 1
    else:
        # 逆排：查找上一個節氣
        jie_qi_day = current_day
        days_to_jie_qi = 0

        # 向前查找最多30天
        for i in range(30):
            if jie_qi_day.hasJieQi():
                break
            jie_qi_day = jie_qi_day.before(1)
            days_to_jie_qi += 1

    # 計算起運時間（天數轉年數）
    # 起運時間 = 節氣天數 ÷ 3
    qi_yun_years_float = days_to_jie_qi / 3.0
    qi_yun_years = int(qi_yun_years_float)
    qi_yun_months = int(round((qi_yun_years_float - qi_yun_years) * 12))

    # 計算起运歲數
    # 起運時間為整數，起运歲數 = 起運時間
    # 如果起運時間為餘數，起运歲數 = 起運時間向上取整
    qi_yun_age = int(math.ceil(qi_yun_years_float))

    # 格式化输出
    # 根据规则显示性别和年干信息
    if is_male:
        gender_info = "陽男" if is_year_tg_yang else "陰男"
    else:
        gender_info = "陽女" if is_year_tg_yang else "陰女"

    return f"{gender_info}，{da_yun_direction}，起運時間{qi_yun_years}年{qi_yun_months}月，{qi_yun_age}歲起运"


def get_shi_shen(gan: str, day_gan: str) -> str:
    """
    計算天干相對於日主的十神

    Args:
        gan: 要計算的天干
        day_gan: 日主天干

    Returns:
        十神名稱
    """
    gan_wuxing = TIAN_GAN_WU_XING.get(gan, "")
    gan_yinyang = TIAN_GAN_YIN_YANG.get(gan, "")
    day_gan_wuxing = TIAN_GAN_WU_XING.get(day_gan, "")
    day_gan_yinyang = TIAN_GAN_YIN_YANG.get(day_gan, "")

    if not gan_wuxing or not day_gan_wuxing:
        return ""

    # 五行生剋關係
    # 木生火，火生土，土生金，金生水，水生木
    sheng_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    # 木剋土，土剋水，水剋火，火剋金，金剋木
    ke_map = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    # 同五行
    if gan_wuxing == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "比肩"
        else:
            return "劫財"

    # 生我者（印）
    if sheng_map.get(gan_wuxing) == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "偏印"
        else:
            return "正印"

    # 我生者（食傷）
    if sheng_map.get(day_gan_wuxing) == gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "食神"
        else:
            return "傷官"

    # 剋我者（官殺）
    if ke_map.get(gan_wuxing) == day_gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "七殺"
        else:
            return "正官"

    # 我剋者（財）
    if ke_map.get(day_gan_wuxing) == gan_wuxing:
        if gan_yinyang == day_gan_yinyang:
            return "偏財"
        else:
            return "正財"

    return "普通"


def calculate_detailed_dayun(ba_zi: str, gender: str, lunar_date) -> dict:
    """
    計算詳細十個大運

    Args:
        ba_zi: 八字字符串
        gender: 性別（"男" 或 "女"）
        lunar_date: sxtwl 庫的農曆日期對象

    Returns:
        {
            "性別": "陽男" 或 "陰男" 等,
            "排法": "順排" 或 "逆排",
            "月柱": "月柱干支",
            "十個大運": [...]
        }
    """
    ba_zi_parts = ba_zi.split()
    month_pillar = ba_zi_parts[1]  # 月柱
    month_gan = month_pillar[0]
    month_zhi = month_pillar[1]

    # 獲取年干
    year_tg = ba_zi_parts[0][0]

    # 判斷年干陰陽
    yang_tian_gan = ["甲", "丙", "戊", "庚", "壬"]
    is_year_tg_yang = year_tg in yang_tian_gan

    # 判斷性别
    is_male = gender == "男"

    # 判斷大运顺逆
    # 陽男陰女順排，陰男陽女逆排
    is_forward = (is_year_tg_yang and is_male) or (not is_year_tg_yang and not is_male)

    # 獲取日干（用于計算十神）
    day_gan = ba_zi_parts[2][0]

    # 天干顺序
    gan_order = GAN
    # 地支顺序
    zhi_order = ZHI

    # 獲取月柱在天干地支中的索引
    month_gan_idx = gan_order.index(month_gan)
    month_zhi_idx = zhi_order.index(month_zhi)

    # 計算实际起运年龄
    # 使用与 calculate_da_yun_info 相同的逻辑
    current_day = lunar_date
    if is_forward:
        # 順排：查找下一個節氣（不包含当天）
        jie_qi_day = current_day.after(1)
        days_to_jie_qi = 1
        for i in range(1, 30):
            if jie_qi_day.hasJieQi():
                break
            jie_qi_day = jie_qi_day.after(1)
            days_to_jie_qi += 1
    else:
        # 逆排：查找上一個節氣（不包含当天）
        jie_qi_day = current_day.before(1)
        days_to_jie_qi = 1
        for i in range(1, 30):
            if jie_qi_day.hasJieQi():
                break
            jie_qi_day = jie_qi_day.before(1)
            days_to_jie_qi += 1

    # 起運時間 = 節氣天數 ÷ 3
    qi_yun_years_float = days_to_jie_qi / 3.0
    first_start_age = int(math.ceil(qi_yun_years_float))

    # 計算十個大運
    dayuns = []
    for i in range(10):
        if is_forward:
            # 順行：加1
            gan_idx = (month_gan_idx + i + 1) % 10
            zhi_idx = (month_zhi_idx + i + 1) % 12
        else:
            # 逆行：减1
            gan_idx = (month_gan_idx - i - 1) % 10
            zhi_idx = (month_zhi_idx - i - 1) % 12

        dayun_gan = gan_order[gan_idx]
        dayun_zhi = zhi_order[zhi_idx]

        # 計算十神
        shi_shen = get_shi_shen(dayun_gan, day_gan)

        # 起运年龄：第一个大运从实际起运年龄开始，每10年递增
        start_age = first_start_age + i * 10

        # 計算大運支藏干（主氣、中氣、餘氣）
        canggan = ZHI_CANG_GAN.get(dayun_zhi, {})
        benqi = canggan.get("主氣", "")
        zhongqi = canggan.get("中氣", "")
        yuqi = canggan.get("餘氣", "")

        # 計算藏干十神
        benqi_shishen = get_shi_shen(benqi, day_gan) if benqi else ""
        zhongqi_shishen = get_shi_shen(zhongqi, day_gan) if zhongqi else ""
        yuqi_shishen = get_shi_shen(yuqi, day_gan) if yuqi else ""

        # 計算大運地支十二長生（以日干為基準）
        chang_sheng = TIAN_GAN_ZHANG_SHENG.get(day_gan, {}).get(dayun_zhi, "")

        dayuns.append({
            "序號": i + 1,
            "大運干": dayun_gan,
            "大運支": dayun_zhi,
            "大運": dayun_gan + dayun_zhi,
            "十神": shi_shen,
            "起運年齡": start_age,
            "地支": {
                "藏干": {
                    "主氣": {"干": benqi, "十神": benqi_shishen} if benqi else None,
                    "中氣": {"干": zhongqi, "十神": zhongqi_shishen} if zhongqi else None,
                    "餘氣": {"干": yuqi, "十神": yuqi_shishen} if yuqi else None,
                },
                "十二長生": chang_sheng
            }
        })

    # 判斷性别信息
    if is_male:
        gender_info = "陽男" if is_year_tg_yang else "陰男"
    else:
        gender_info = "陽女" if is_year_tg_yang else "陰女"

    return {
        "性別": gender_info,
        "排法": "順排" if is_forward else "逆排",
        "月柱": month_pillar,
        "十個大運": dayuns,
    }


# =============================================================================
# 移花接木判斷（歲運進階功能）
# 來源：22_歲運真機.docx
# =============================================================================

# 四庫地支（移花接木的關鍵地支）
YI_HUA_JIE_MU_ZHI = ["辰", "戌", "丑", "未"]


def calculate_yi_hua_jie_mu(dayun_list: list) -> dict:
    """
    移花接木判斷

    根據 22_歲運真機.docx：
    - 移花接木：大運遇到辰、戌、丑、未四庫地支時，如同移花接木
    - 四庫為土，主變化、轉折

    Args:
        dayun_list: 大運列表，每個元素包含"大運支"鍵

    Returns:
        {
            "四庫大運": list,  # 遇到辰戌丑未的大運
            "說明": str,
        }
    """
    si_ku_dayun = []

    for i, dayun in enumerate(dayun_list):
        zhi = dayun.get("大運支", "")

        if zhi in YI_HUA_JIE_MU_ZHI:
            si_ku_dayun.append({
                "大運": dayun.get("大運", ""),
                "大運支": zhi,
                "序號": i + 1,
                "說明": f"行運至{zhi}庫，移花接木之際，主變化轉折",
            })

    return {
        "四庫大運": si_ku_dayun,
        "說明": "移花接木：大運遇辰、戌、丑、未四庫，如同園藝移花接木，主人生變化轉折。",
    }