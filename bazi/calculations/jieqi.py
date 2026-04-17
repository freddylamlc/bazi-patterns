"""
節氣計算模塊 - 計算節氣相關信息
"""

import sxtwl


# 節氣名稱對照表（sxtwl 庫使用）
JIE_QI_MC = {
    1: "小寒", 2: "大寒", 3: "立春", 4: "雨水", 5: "驚蟄", 6: "春分",
    7: "清明", 8: "谷雨", 9: "立夏", 10: "小滿", 11: "芒種", 12: "夏至",
    13: "小暑", 14: "大暑", 15: "立秋", 16: "處暑", 17: "白露", 18: "秋分",
    19: "寒露", 20: "霜降", 21: "立冬", 22: "小雪", 23: "大雪", 24: "冬至",
}


def calculate_jie_qi_info(lunar_date) -> str:
    """
    計算節氣信息

    Args:
        lunar_date: sxtwl 庫的農曆日期對象

    Returns:
        節氣信息字符串，如 "生于小寒節氣后5天，大寒節氣前10天"
    """
    # 獲取当前日期的節氣信息
    current_day = lunar_date

    # 查找上一個節氣
    prev_jie_qi = None
    prev_jie_qi_day = current_day
    days_since_prev = 0

    # 向前查找最多30天
    for i in range(30):
        if prev_jie_qi_day.hasJieQi():
            prev_jie_qi = prev_jie_qi_day.getJieQi()
            break
        prev_jie_qi_day = prev_jie_qi_day.before(1)
        days_since_prev += 1

    # 查找下一個節氣
    next_jie_qi = None
    next_jie_qi_day = current_day
    days_to_next = 0

    # 向后查找最多30天
    for i in range(30):
        if next_jie_qi_day.hasJieQi():
            next_jie_qi = next_jie_qi_day.getJieQi()
            break
        next_jie_qi_day = next_jie_qi_day.after(1)
        days_to_next += 1

    # 格式化输出
    if prev_jie_qi is not None and next_jie_qi is not None:
        prev_jie_qi_name = JIE_QI_MC.get(prev_jie_qi, str(prev_jie_qi))
        next_jie_qi_name = JIE_QI_MC.get(next_jie_qi, str(next_jie_qi))
        return f"生于{prev_jie_qi_name}節氣后{days_since_prev}天，{next_jie_qi_name}節氣前{days_to_next}天"

    return ""


def get_prev_next_jie_qi(lunar_date) -> dict:
    """
    獲取前後節氣詳細信息

    Args:
        lunar_date: sxtwl 庫的農曆日期對象

    Returns:
        {
            "prev_jie_qi": 節氣名稱,
            "prev_jie_qi_days": 距前一節氣天數,
            "next_jie_qi": 節氣名稱,
            "next_jie_qi_days": 距下一節氣天數,
        }
    """
    current_day = lunar_date

    # 查找上一個節氣
    prev_jie_qi = None
    prev_jie_qi_day = current_day
    days_since_prev = 0

    for i in range(30):
        if prev_jie_qi_day.hasJieQi():
            prev_jie_qi = prev_jie_qi_day.getJieQi()
            break
        prev_jie_qi_day = prev_jie_qi_day.before(1)
        days_since_prev += 1

    # 查找下一個節氣
    next_jie_qi = None
    next_jie_qi_day = current_day
    days_to_next = 0

    for i in range(30):
        if next_jie_qi_day.hasJieQi():
            next_jie_qi = next_jie_qi_day.getJieQi()
            break
        next_jie_qi_day = next_jie_qi_day.after(1)
        days_to_next += 1

    return {
        "prev_jie_qi": JIE_QI_MC.get(prev_jie_qi, "") if prev_jie_qi else "",
        "prev_jie_qi_days": days_since_prev,
        "next_jie_qi": JIE_QI_MC.get(next_jie_qi, "") if next_jie_qi else "",
        "next_jie_qi_days": days_to_next,
    }