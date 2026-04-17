"""
八字排盤系統 - API 路由模塊
包含所有 API 端點和 HTML 生成邏輯
"""

import json
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi import Request
from bazi import BaZiCalculator
from bazi.core.constants import TIAN_GAN_YIN_YANG, TIAN_GAN_WU_XING as GAN_WU_XING, ZHI_WU_XING
from bazi.calculations.shishen import get_shi_shen

router = APIRouter()

# 五行顏色映射
WU_XING_COLORS = {
    "木": {"bg": "bg-green-50", "text": "text-green-700", "border": "border-green-200"},
    "火": {"bg": "bg-red-50", "text": "text-red-700", "border": "border-red-200"},
    "土": {"bg": "bg-yellow-50", "text": "text-yellow-700", "border": "border-yellow-200"},
    "金": {"bg": "bg-gray-50", "text": "text-gray-700", "border": "border-gray-200"},
    "水": {"bg": "bg-blue-50", "text": "text-blue-700", "border": "border-blue-200"},
}


def get_wuxing_class(wx):
    return WU_XING_COLORS.get(wx, {"bg": "bg-stone-50", "text": "text-stone-700", "border": "border-stone-200"})


def get_canggan_shishen(gan: str, day_gan: str) -> str:
    """
    計算藏干的十神

    Args:
        gan: 藏干天干
        day_gan: 日天干

    Returns:
        十神名稱
    """
    return get_shi_shen(gan, day_gan)


def render_shishen_personality(shishen_data: dict) -> str:
    """渲染十神性格 HTML"""
    if not shishen_data:
        return '<div class="text-stone-500 text-sm">暫無數據</div>'

    html_parts = []
    for shishen_name, info in shishen_data.items():
        status = info.get("狀態", "")
        shishen_type = info.get("類型", "其他")
        is_ke_zhi = info.get("是否受剋", False)

        if "相神" in status and "被剋" not in status:
            card_class = "bg-green-50 border-green-200 border"
            title_class = "text-green-700"
            desc_class = "text-green-800"
        elif "相神" in status and "被剋" in status:
            card_class = "bg-red-100 border-red-300 border-2"
            title_class = "text-red-800 font-bold"
            desc_class = "text-red-900 font-bold"
        elif "忌神" in status and "被制" in status:
            card_class = "bg-green-50 border-green-200 border"
            title_class = "text-green-700"
            desc_class = "text-green-800"
        elif "忌神" in status and "被制" not in status:
            card_class = "bg-red-50 border-red-200 border"
            title_class = "text-red-700"
            desc_class = "text-red-800"
        else:
            card_class = "bg-stone-50 border-stone-200 border"
            title_class = "text-stone-600"
            desc_class = "text-stone-500"

        shen_wang_note = ""
        if info.get("身旺衰說明"):
            shen_wang_note = f'<div class="text-xs text-stone-400 mt-2">{info["身旺衰說明"]}</div>'

        ke_zhi_badge = ""
        if is_ke_zhi:
            ke_zhi_badge = '<span class="text-xs px-2 py-0.5 rounded bg-red-200 text-red-700 ml-2">受剋</span>'

        html_parts.append(f"""
        <div class="p-3 rounded-xl {card_class}">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-bold {title_class}">{shishen_name}{ke_zhi_badge}</span>
                <span class="text-xs text-stone-400">{info.get("狀態", "")}</span>
            </div>
            <div class="text-xs {desc_class} leading-relaxed">{info.get("心性描述", "")}</div>
            {shen_wang_note}
        </div>
        """)

    return "".join(html_parts)


def compute_bazi(data: dict):
    """計算八字"""
    calculator = BaZiCalculator(
        name=data['name'],
        gender=data['gender'],
        calendar=data['calendar'],
        year=data['year'],
        month=data['month'],
        day=data['day'],
        hour=data['hour'],
        minute=data['minute'],
        birth_city=data['birth_city'],
        current_city=data.get('current_city'),
    )

    gender_text = "男 (乾造)" if calculator.gender == "男" else "女 (坤造)"

    # ===== 臨時調試：打印數據結構 =====
    print("\n[DEBUG] 詳細大運 keys:", list(calculator.detailed_dayun.keys()))
    print("[DEBUG] 詳細大運 十個大運 長度:", len(calculator.detailed_dayun.get('十個大運', [])))
    if calculator.detailed_dayun.get('十個大運'):
        first_dy = calculator.detailed_dayun['十個大運'][0]
        print("[DEBUG] 第一個大運 keys:", list(first_dy.keys()))
        print("[DEBUG] 第一個大運 完整數據:", first_dy)
        if first_dy.get('地支'):
            print("[DEBUG] 第一個大運 地支 keys:", list(first_dy['地支'].keys()) if isinstance(first_dy['地支'], dict) else first_dy['地支'])
    print("[DEBUG] 流年判斷 流年分析 第一個:", calculator.liunian_pan_duan.get('流年分析', [{}])[0])
    # ===== 調試結束 =====


    solar_date_str = f"{calculator.solar_time.year}年{calculator.solar_time.month}月{calculator.solar_time.day}日{calculator.solar_time.hour:02d}:{calculator.solar_time.minute:02d}"
    lunar_year = calculator.lunar_date.getLunarYear()
    lunar_month = calculator.lunar_date.getLunarMonth()
    lunar_day = calculator.lunar_date.getLunarDay()
    is_leap = "(閏月)" if calculator.lunar_date.isLunarLeap() else ""
    lunar_date_str = f"{lunar_year}年{lunar_month}月{lunar_day}日{calculator.solar_time.hour:02d}:{calculator.solar_time.minute:02d} {is_leap}"

    return {
        "姓名": calculator.name,
        "性別": gender_text,
        "出生時間": {"公曆": solar_date_str, "農曆": lunar_date_str},
        "出生城市": f"{calculator.birth_city} (經度：{calculator.birth_longitude}°E)",
        "八字": calculator.ba_zi,
        "藏干": calculator.cang_gan,
        "天干五合": calculator.tian_gan_wu_he,
        "地支關係": calculator.zhi_relations,
        "干支生剋": calculator.gan_zhi_sheng_ke,
        "旺衰": calculator.wang_shuai,
        "十二長生": calculator.chang_sheng,
        "十神": calculator.shi_shen,
        "神煞": calculator.shen_sha,
        "六十甲子": calculator.liu_shi_jia_zi,
        "節氣": calculator.jie_qi_info,
        "大運": calculator.da_yun_info,
        "詳細大運": calculator.detailed_dayun,
        "格局": calculator.ge_ju,  # 原局格局（與 yuan_ju_ge_ju 相同）
        "整合分析": calculator.integrated_analysis,
        "宮位": calculator.gong_wei,
        "先天病源": calculator.xian_tian_bing_yuan,
        "大運判斷": calculator.dayun_pan_duan,
        "流年判斷": calculator.liunian_pan_duan,
        # ========== 兩層格局 ==========
        "原局格局": calculator.yuan_ju_ge_ju,
        # 注意：calculator.suiyun_ge_ju 包含 {dayun_index, liunian_index, 大運，流年，sui_yun_ge_ju}
        # 需要提取內層的 sui_yun_ge_ju 字典
        "歲運格局": calculator.suiyun_ge_ju.get('sui_yun_ge_ju', {}) if isinstance(calculator.suiyun_ge_ju, dict) else {},
        "歲運格局全部": calculator.all_suiyun_geju,  # 所有大運流年的歲運格局數據
        # ========== 其他新功能 ==========
        "一柱論命": calculator.yi_zhu,
        "干支象法": calculator.ganzhi_xiang,
        "移花接木": calculator.yi_hua_jie_mu,
        "兩格並存": calculator.liang_ge_bing_cun,
        "bazi_gua": calculator.bazi_gua,
    }
