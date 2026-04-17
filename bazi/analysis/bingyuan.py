"""
先天病源分析模塊

根據講義內容實現先天病源分析：
- 忌神所在（第一優先）
- 蓋頭截腳（第二優先）
- 相神喜神被沖（第三優先）
- 五行過旺（第四優先）
- 五行所缺（第五優先）
"""

from bazi.core.constants import (
    TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG, ZHI_WU_XING, WU_XING_KE,
    TIAN_GAN_ZANG_FU, ZHI_ZANG_FU, ZHI_LIU_CHONG,
)

# 別名（兼容舊代碼）
TianGanWuXing = TIAN_GAN_WU_XING
TianGanYinYang = TIAN_GAN_YIN_YANG
ZhiWuXing = ZHI_WU_XING
WuXingKe = WU_XING_KE
TianGanZangFu = TIAN_GAN_ZANG_FU
ZhiZangFu = ZHI_ZANG_FU
ZhiLiuChong = ZHI_LIU_CHONG


# 月令當令五行
YUE_LING_DANG_LING = {
    "寅": "木", "卯": "木",
    "巳": "火", "午": "火",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
    "申": "金", "酉": "金",
    "亥": "水", "子": "水",
}


# 五行對應臟腑
WU_XING_ZANG_FU = {
    "木": "肝膽",
    "火": "心臟小腸",
    "土": "脾胃",
    "金": "肺大腸",
    "水": "腎膀胱",
}


def calculate_bingyuan(ba_zi: str, ge_ju: dict, gong_wei: dict = None,
                       integrated_analysis: dict = None) -> dict:
    """
    計算先天病源

    優先級順序：
    1. 忌神所在的天干和地支（第一優先）
    2. 蓋頭和截腳的天干和地支（第二優先）
    3. 相神或喜神被沖的地支（第三優先）
    4. 同五行太多（>=4 個字，只計主氣）（第四優先）
    5. 五行所缺（第五優先）

    Args:
        ba_zi: 八字字符串
        ge_ju: 格局判斷字典
        gong_wei: 宮位分析字典（可選）
        integrated_analysis: 整合分析字典（可選）

    Returns:
        先天病源字典
    """
    ba_zi_parts = ba_zi.split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]

    # 獲取格局信息
    yong_shen = ge_ju.get("用神", "")
    xiang_shen = ge_ju.get("相神", [])
    ji_shen_wuxing = ge_ju.get("忌神五行", [])

    # 從整合分析獲取喜神忌神十神
    xi_shen_shishen = []
    ji_shen_shishen = []
    if integrated_analysis:
        integrated = integrated_analysis
        xi_shen_shishen = integrated.get("格局核心", {}).get("喜神十神", [])
        ji_shen_shishen = integrated.get("格局核心", {}).get("忌神十神", [])

    # 結果列表（按優先級排序）
    bing_yuan_list = []

    # ========== 第一優先：忌神所在的天干和地支 ==========
    ji_shen_positions = []
    for pillar, pillar_name in zip(ba_zi_parts, pillar_names):
        tg = pillar[0]
        zhi = pillar[1]
        tg_wuxing = TianGanWuXing[tg]
        zhi_wuxing = ZhiWuXing[zhi]

        if tg_wuxing in ji_shen_wuxing:
            ji_shen_positions.append({
                "柱": f"{pillar_name}天干",
                "位置": f"{pillar_name}天干",
                "干支": pillar,
                "五行": tg_wuxing,
                "臟腑": TianGanZangFu.get(tg, ""),
                "類型": "忌神天干"
            })

        if zhi_wuxing in ji_shen_wuxing:
            ji_shen_positions.append({
                "柱": f"{pillar_name}地支",
                "位置": f"{pillar_name}地支",
                "干支": pillar,
                "五行": zhi_wuxing,
                "臟腑": ZhiZangFu.get(zhi, ""),
                "類型": "忌神地支"
            })

    for pos in ji_shen_positions:
        bing_yuan_list.append({
            "優先級": 1,
            "病源": f"{pos['位置']}({pos['干支']})",
            "影響臟腑": pos['臟腑'],
            "說明": f"忌神{pos['五行']}所在，先天易損"
        })

    # ========== 第二優先：蓋頭和截腳 ==========
    gai_tou_jie_jiao = []
    for pillar, pillar_name in zip(ba_zi_parts, pillar_names):
        tg = pillar[0]
        zhi = pillar[1]
        tg_wuxing = TianGanWuXing[tg]
        zhi_wuxing = ZhiWuXing[zhi]

        # 蓋頭：天干剋地支
        if WuXingKe.get(tg_wuxing) == zhi_wuxing:
            gai_tou_jie_jiao.append({
                "柱": pillar_name,
                "位置": pillar_name,
                "干支": pillar,
                "類型": "蓋頭",
                "天干臟腑": TianGanZangFu.get(tg, ""),
                "地支臟腑": ZhiZangFu.get(zhi, ""),
                "說明": f"{tg}剋{zhi}，天干{tg_wuxing}剋地支{zhi_wuxing}"
            })
        # 截腳：地支剋天干
        elif WuXingKe.get(zhi_wuxing) == tg_wuxing:
            gai_tou_jie_jiao.append({
                "柱": pillar_name,
                "位置": pillar_name,
                "干支": pillar,
                "類型": "截腳",
                "天干臟腑": TianGanZangFu.get(tg, ""),
                "地支臟腑": ZhiZangFu.get(zhi, ""),
                "說明": f"{zhi}剋{tg}，地支{zhi_wuxing}剋天干{tg_wuxing}"
            })

    for gtjj in gai_tou_jie_jiao:
        bing_yuan_list.append({
            "優先級": 2,
            "病源": f"{gtjj['位置']}({gtjj['干支']})",
            "影響臟腑": f"{gtjj['天干臟腑']}、{gtjj['地支臟腑']}",
            "說明": f"{gtjj['類型']}：{gtjj['說明']}"
        })

    # ========== 第三優先：相神或喜神被沖的地支 ==========
    chong_positions = []

    # 獲取用神/相神所在的地支
    yong_xiang_zhi = []
    for pillar, pillar_name in zip(ba_zi_parts, pillar_names):
        zhi = pillar[1]
        zhi_wuxing = ZhiWuXing[zhi]
        if yong_shen and zhi_wuxing == yong_shen:
            yong_xiang_zhi.append((pillar_name, pillar, zhi))

    # 檢查被沖
    for pillar_name, pillar, zhi in yong_xiang_zhi:
        chong_zhi = None
        for ch1, ch2 in ZhiLiuChong:
            if zhi == ch1:
                chong_zhi = ch2
                break
            elif zhi == ch2:
                chong_zhi = ch1
                break
        if chong_zhi and chong_zhi in [p[1] for p in ba_zi_parts]:
            chong_positions.append({
                "柱": pillar_name,
                "位置": pillar_name,
                "干支": pillar,
                "被沖": chong_zhi,
                "臟腑": ZhiZangFu.get(zhi, ""),
                "說明": f"{zhi}被{chong_zhi}沖"
            })

    for cp in chong_positions:
        bing_yuan_list.append({
            "優先級": 3,
            "病源": f"{cp['位置']}({cp['干支']})",
            "影響臟腑": cp['臟腑'],
            "說明": f"喜神/相神地支{cp['說明']}"
        })

    # ========== 第四優先：同五行太多（>=4 個字） ==========
    wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pillar in ba_zi_parts:
        tg = pillar[0]
        zhi = pillar[1]
        tg_wuxing = TianGanWuXing[tg]
        zhi_wuxing = ZhiWuXing[zhi]
        wuxing_count[tg_wuxing] += 1
        wuxing_count[zhi_wuxing] += 1

    guo_duo_wuxing = []
    wu_xing_guo_wang_bing = []  # 五行過旺病（字符串列表）
    for wx, count in wuxing_count.items():
        if count >= 4:
            zang_fu_list = []
            for pillar, pillar_name in zip(ba_zi_parts, pillar_names):
                tg = pillar[0]
                zhi = pillar[1]
                if TianGanWuXing[tg] == wx:
                    zang_fu_list.append(TianGanZangFu.get(tg, ""))
                if ZhiWuXing[zhi] == wx:
                    zang_fu_list.append(ZhiZangFu.get(zhi, ""))
            zang_fu_str = "、".join(set(zang_fu_list))
            guo_duo_wuxing.append({
                "五行": wx,
                "數量": count,
                "臟腑": zang_fu_str
            })
            # 添加五行過旺病描述
            wu_xing_guo_wang_bing.append(f"{wx}過旺（{count}個）：{zang_fu_str}易患病")

    for gd in guo_duo_wuxing:
        bing_yuan_list.append({
            "優先級": 4,
            "病源": f"{gd['五行']}過旺",
            "影響臟腑": gd['臟腑'],
            "說明": f"{gd['五行']}共{gd['數量']}個，過旺為病"
        })

    # ========== 第五優先：五行所缺 ==========
    que_shi_wuxing = []
    wu_xing_que_shi_bing = []  # 五行缺失病（字符串列表）
    for wx, count in wuxing_count.items():
        if count == 0:
            zang_fu = WU_XING_ZANG_FU.get(wx, "")
            que_shi_wuxing.append({
                "五行": wx,
                "臟腑": zang_fu
            })
            # 添加五行缺失病描述
            wu_xing_que_shi_bing.append(f"{wx}缺失：{zang_fu}先天不足")

    for qs in que_shi_wuxing:
        bing_yuan_list.append({
            "優先級": 5,
            "病源": f"{qs['五行']}缺失",
            "影響臟腑": qs['臟腑'],
            "說明": f"{qs['五行']}缺失，先天不足"
        })

    # 計算月令當令五行
    month_zhi = ba_zi_parts[1][1]
    dang_ling_wuxing = YUE_LING_DANG_LING.get(month_zhi, "土")

    # 五行分布統計
    wuxing_status = {}
    for wx, count in wuxing_count.items():
        if count >= 3:
            status = "過旺"
        elif count == 0:
            status = "缺失"
        else:
            status = "適中"
        wuxing_status[wx] = {"數量": count, "狀態": status}

    # 構建忌神列表（帶原因和數量）
    ji_shen_list = []
    for wx in ji_shen_wuxing:
        count = wuxing_count.get(wx, 0)
        ji_shen_list.append({
            "五行": wx,
            "原因": "格局忌神",
            "數量": count
        })

    # 構建用神列表（帶原因）
    yong_shen_list = []
    if yong_shen:
        yong_shen_list.append({
            "五行": yong_shen,
            "原因": "格局用神"
        })

    # 組裝結果
    result = {
        "病源列表": bing_yuan_list,
        "用神分析": {
            "說明": "格局用神所在的天干地支為先天健康關鍵",
            "用神": yong_shen if yong_shen else "無",
            "用神列表": yong_shen_list
        },
        "忌神分析": {
            "說明": "格局忌神所在的天干地支為先天病源第一優先",
            "忌神五行": ji_shen_wuxing,
            "忌神位置": ji_shen_positions,
            "忌神列表": ji_shen_list
        },
        "蓋頭截腳": {
            "說明": "蓋頭截腳的天干地支對應臟腑為第二優先病源",
            "列表": gai_tou_jie_jiao
        },
        "沖剋病源": {
            "說明": "相神/喜神地支被沖為第三優先病源",
            "列表": chong_positions
        },
        "五行過旺": {
            "說明": "同五行>=4 個為過旺，第四優先",
            "列表": guo_duo_wuxing
        },
        "五行缺失": {
            "說明": "五行缺失為第五優先病源",
            "列表": que_shi_wuxing
        },
        "五行分布": wuxing_status,
        "月令": {
            "月支": month_zhi,
            "當令五行": dang_ling_wuxing
        },
        # 與未重構版本輸出邏輯兼容的字段
        "五行缺失病": wu_xing_que_shi_bing,
        "五行過旺病": wu_xing_guo_wang_bing,
        "特殊格局病": [],  # 暫時為空，可根據特殊格局添加
        "入墓五行": []  # 暫時為空，可根據長生狀態計算
    }

    return result
