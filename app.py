"""
八字排盤系統 - Web 應用主入口
© 2024-2026 Antigravity. All rights reserved.
Unauthorized copying, modification, or distribution of this code is strictly prohibited.
使用 Jinja2 模板渲染，靜態文件分離到 static/ 目錄
"""

import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from bazi import BaZiCalculator
import uvicorn
from api.routes import (
    router,
    compute_bazi,
    render_shishen_personality,
    get_wuxing_class,
    get_canggan_shishen,
    GAN_WU_XING,
    ZHI_WU_XING,
)

app = FastAPI(title="八字算命網頁版")

# 掛載靜態文件目錄
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含 API 路由
app.include_router(router)

# 設置 Jinja2 模板環境
env = Environment(loader=FileSystemLoader("templates"))


def render_index_html() -> str:
    """渲染首頁 HTML"""
    template = env.get_template("index.html")
    return template.render()


def generate_gongwei_jixiong_html(gong_wei_ji_xiong: list) -> str:
    """生成宮位吉凶 HTML"""
    if not gong_wei_ji_xiong:
        return '<div class="text-stone-500 text-sm">暫無數據</div>'

    html_parts = []
    for gw in gong_wei_ji_xiong:
        pillar_name = gw.get('柱', '')
        tian_gan = gw.get('天干', {})
        di_zhi = gw.get('地支', {})

        tian_gan_class = 'text-green-600' if tian_gan.get('吉凶') == '大吉' else 'text-red-600' if tian_gan.get('吉凶') == '凶' else 'text-stone-600'
        di_zhi_class = 'text-green-600' if di_zhi.get('吉凶') == '大吉' else 'text-red-600' if di_zhi.get('吉凶') == '凶' else 'text-stone-600'

        html_parts.append(f"""
        <div class="p-3 rounded-lg bg-stone-50 border border-stone-200">
            <div class="text-xs font-bold text-stone-600 mb-2">{pillar_name}</div>
            <div class="text-xs space-y-1">
                <div><span class="text-stone-400">天干：</span><span class="{tian_gan_class}">{tian_gan.get('天干', '')} - {tian_gan.get('吉凶', '平')}</span></div>
                <div><span class="text-stone-400">地支：</span><span class="{di_zhi_class}">{di_zhi.get('地支', '')} - {di_zhi.get('吉凶', '平')}</span></div>
            </div>
        </div>
        """)
    return "".join(html_parts)


def generate_jibing_lunduan_html(ji_bing_lun_duan: list) -> str:
    """生成疾病論斷 HTML"""
    if not ji_bing_lun_duan:
        return '<div class="text-stone-500 text-sm">暫無數據</div>'

    html_parts = []
    for item in ji_bing_lun_duan:
        item_type = item.get('類型', '')
        item_desc = item.get('說明', '')
        item_ying_qi = item.get('應期', '')
        item_jian_yi = item.get('建議', '')

        html_parts.append(f"""
        <div class="p-3 rounded-lg bg-stone-50 border border-stone-200">
            <div class="text-xs font-bold text-stone-600 mb-1">{item_type}</div>
            <div class="text-xs text-stone-700">{item_desc}</div>
            {f'<div class="text-xs text-amber-600 mt-1">應期：{item_ying_qi}</div>' if item_ying_qi else ''}
            {f'<div class="text-xs text-blue-600 mt-1">建議：{item_jian_yi}</div>' if item_jian_yi else ''}
        </div>
        """)
    return "".join(html_parts)


def generate_wuxing_fenbu_biao_html(wu_xing_fen_bu: dict) -> str:
    """生成五行分布表 HTML"""
    if not wu_xing_fen_bu:
        return '<span class="text-stone-500 text-sm">暫無數據</span>'

    wu_xing_colors = {
        '木': 'bg-green-50 text-green-700 border-green-200',
        '火': 'bg-red-50 text-red-700 border-red-200',
        '土': 'bg-yellow-50 text-yellow-700 border-yellow-200',
        '金': 'bg-gray-50 text-gray-700 border-gray-200',
        '水': 'bg-blue-50 text-blue-700 border-blue-200'
    }

    html_parts = []
    for wx, info in wu_xing_fen_bu.items():
        count = info.get('數量', 0)
        status = info.get('狀態', '')
        color_class = wu_xing_colors.get(wx, 'bg-stone-50 text-stone-700 border-stone-200')
        html_parts.append(f'<span class="px-2 py-1 rounded text-xs {color_class}">{wx}:{count} ({status})</span>')

    return "".join(html_parts)


def generate_dayun_panduan_html(da_yun_pan_duan: list) -> str:
    """生成大運判斷 HTML"""
    if not da_yun_pan_duan:
        return '<div class="text-stone-500 text-sm">暫無數據</div>'

    html_parts = []
    for dy in da_yun_pan_duan:
        yun_name = dy.get('大運', '')
        yun_shi_shen = dy.get('十神', '')
        yun_desc = dy.get('大運影響', '')
        yun_geju = dy.get('格局影響', '')

        geju_class = 'text-green-600' if '用神' in yun_geju or '喜神' in yun_geju else 'text-red-600' if '忌神' in yun_geju else 'text-stone-600'

        html_parts.append(f"""
        <div class="p-3 rounded-lg bg-stone-50 border border-stone-200">
            <div class="text-xs font-bold text-stone-600 mb-1">{yun_name} ({yun_shi_shen})</div>
            <div class="text-xs text-stone-700">{yun_desc}</div>
            <div class="text-xs {geju_class} mt-1">格局影響：{yun_geju}</div>
        </div>
        """)
    return "".join(html_parts)


def generate_liunian_panduan_html(liu_nian_pan_duan: list) -> str:
    """生成流年判斷 HTML"""
    if not liu_nian_pan_duan:
        return '<div class="text-stone-500 text-sm">暫無數據</div>'

    html_parts = []
    for ln in liu_nian_pan_duan:
        nian_name = ln.get('流年', '')
        nian_shi_shen = ln.get('流年十神', '')
        nian_desc = ln.get('格局影響', '')

        geju_class = 'text-green-600' if '用神' in nian_desc or '喜神' in nian_desc else 'text-red-600' if '忌神' in nian_desc else 'text-stone-600'

        html_parts.append(f"""
        <div class="p-3 rounded-lg bg-stone-50 border border-stone-200">
            <div class="text-xs font-bold text-stone-600 mb-1">{nian_name} ({nian_shi_shen})</div>
            <div class="text-xs {geju_class} mt-1">{nian_desc}</div>
        </div>
        """)
    return "".join(html_parts)


def generate_zangfu_html(zang_fu: dict) -> str:
    """生成臟腑對應 HTML"""
    if not zang_fu:
        return '<span class="text-stone-500 text-sm">暫無數據</span>'

    html_parts = []
    for key, value in zang_fu.items():
        html_parts.append(f'<span class="px-2 py-1 rounded text-xs bg-stone-100 text-stone-700">{key}: {value}</span>')

    return "".join(html_parts)


def generate_bazi_result_html(res: dict, pillars: list, ji_shens: list, yong_shens: list) -> str:
    """使用模板生成八字命盤結果 HTML"""
    template = env.get_template("result.html")

    # 準備模板數據
    ba_zi_parts = res['八字'].split()
    day_gan = ba_zi_parts[2][0]

    # 大運數據 - 使用整合分析中的大運分析數據
    # JavaScript 需要的結構：{'天干': {'干': 'X', '十神': 'X'}, '地支': {'支': 'X', '藏干': {...}}, ...}
    integrated = res.get('整合分析', {})
    # 大運數據直接從 詳細大運 取，結構正確
    da_yun_fen_xi = res.get('詳細大運', {}).get('十個大運', [])
    dayun_data = []
    for dy in da_yun_fen_xi:
        dy_gan = dy.get('大運干', '')
        dy_zhi = dy.get('大運支', '')
        dy_shishen = dy.get('十神', '')
        dy_qiyun = dy.get('起運年齡', 0)
        # 藏干從地支數據取
        dy_zhi_data = dy.get('地支', {})
        dayun_data.append({
            '天干': {'干': dy_gan, '十神': dy_shishen},
            '地支': {'支': dy_zhi, '藏干': dy_zhi_data.get('藏干', {}), '十二長生': dy_zhi_data.get('十二長生', '')},
            '起運年齡': dy_qiyun
        })

    # 流年數據 - 直接從 流年判斷 取，不從整合分析取
    liu_nian_fen_xi = res.get('流年判斷', {}).get('流年分析', [])
    # 從流年判斷獲取格局影響數據（包含正確的喜神/忌神判斷）
    liu_nian_pan_duan_list = res.get('流年判斷', {}).get('流年分析', [])

    # 將 100 個流年按大運分組（每 10 個一組）
    liunian_by_dayun = {}
    for i, ln in enumerate(liu_nian_fen_xi):
        dayun_idx = i // 10  # 每 10 個流年屬於一個大運
        if dayun_idx not in liunian_by_dayun:
            liunian_by_dayun[dayun_idx] = []

        # 從嵌套結構獲取數據（新模塊返回嵌套結構）
        # 新結構：{ "天干": {"干": ..., "十神": ...}, "地支": {"支": ..., "十二長生": ...}, ... }
        tian_gan_data = ln.get('天干', {})
        zhi_data = ln.get('地支', {})
        tian_gan = tian_gan_data.get('干', ln.get('流年天干', ''))
        zhi = zhi_data.get('支', ln.get('流年地支', ''))
        tian_gan_shishen = tian_gan_data.get('十神', ln.get('流年十神', ''))
        chang_sheng = zhi_data.get('十二長生', ln.get('十二長生', ''))

        # 獲取藏干 - 優先從 res['流年判斷'] 獲取完整數據
        canggan = {}
        liu_nian_pan_duan = res.get('流年判斷', {}).get('流年分析', [])
        if i < len(liu_nian_pan_duan):
            original_ln = liu_nian_pan_duan[i]
            # 嘗試從原始數據獲取藏干
            if '藏干' in original_ln:
                canggan = original_ln.get('藏干', {})
            else:
                # 從地支獲取藏干（使用 ZhiCangGan 查找表）
                from bazi.core.constants import ZHI_CANG_GAN
                if zhi in ZHI_CANG_GAN:
                    zhi_canggan = ZHI_CANG_GAN[zhi]
                    # 計算藏干的十神（使用共享函數）
                    if zhi_canggan.get('主氣'):
                        canggan['主氣'] = {'干': zhi_canggan['主氣'], '十神': get_canggan_shishen(zhi_canggan['主氣'], day_gan)}
                    if zhi_canggan.get('中氣'):
                        canggan['中氣'] = {'干': zhi_canggan['中氣'], '十神': get_canggan_shishen(zhi_canggan['中氣'], day_gan)}
                    if zhi_canggan.get('餘氣'):
                        canggan['餘氣'] = {'干': zhi_canggan['餘氣'], '十神': get_canggan_shishen(zhi_canggan['餘氣'], day_gan)}
        else:
            # 簡化版本：只顯示主氣
            canggan = {'主氣': {'干': zhi, '十神': zhi_shishen}} if zhi else {}

        # 從流年判斷獲取格局影響（優先使用，因為有正確的喜神/忌神判斷）
        ge_ju_ying_xiang = '平穩'
        if i < len(liu_nian_pan_duan_list):
            ge_ju_ying_xiang = liu_nian_pan_duan_list[i].get('格局影響', '平穩')
        # 如果流年判斷沒有，才用整合分析的
        if ge_ju_ying_xiang == '平穩' and '格局影響' in ln:
            ge_ju_ying_xiang = ln.get('格局影響', '平穩')

        liunian_by_dayun[dayun_idx].append({
            '流年天干': tian_gan,
            '流年地支': zhi,
            '流年十神': tian_gan_shishen,
            '藏干': canggan,
            '十二長生': chang_sheng,
            '格局影響': ge_ju_ying_xiang,
            '大運序號': ln.get('大運序號', 1),
            '流年序號': ln.get('流年序號', 1),
            '虛歲': ln.get('虛歲', 0)
        })

    # 兼容舊代碼：保留 all_liunian_data 扁平結構（使用 liunian_by_dayun 的第一個大運數據）
    all_liunian_data = liunian_by_dayun.get(0, [])

    # ========== 流月計算 ==========
    # 流月地支固定：寅卯辰巳午未申酉戌亥子丑
    YUE_LING_ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
    YUE_LING_NAMES = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']

    # 五虎遁：根據流年天干確定正月天干
    # 甲己→丙寅，乙庚→戊寅，丙辛→庚寅，丁壬→壬寅，戊癸→甲寅
    WU_HU_DUN = {
        '甲': '丙', '己': '丙',
        '乙': '戊', '庚': '戊',
        '丙': '庚', '辛': '庚',
        '丁': '壬', '壬': '壬',
        '戊': '甲', '癸': '甲'
    }

    def get_yue_gan(nian_gan, yue_zhi_index):
        """根據流年天干和月份索引計算流月天干"""
        zheng_yue_gan = WU_HU_DUN.get(nian_gan, '甲')
        # 天干順序：甲乙丙丁戊己庚辛壬癸
        tian_gan_order = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        start_idx = tian_gan_order.index(zheng_yue_gan)
        return tian_gan_order[(start_idx + yue_zhi_index) % 10]

    def get_yue_shishen(yue_gan, day_gan):
        """計算流月天干的十神"""
        if not yue_gan or not day_gan:
            return ''
        from bazi.core.constants import TIAN_GAN_YIN_YANG
        gan_wx = GAN_WU_XING.get(yue_gan, '')
        gan_yy = TIAN_GAN_YIN_YANG.get(yue_gan, '')
        day_gan_wx = GAN_WU_XING.get(day_gan, '')
        day_gan_yy = TIAN_GAN_YIN_YANG.get(day_gan, '')

        sheng_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        ke_map = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

        # 同五行
        if gan_wx == day_gan_wx:
            return "比肩" if gan_yy == day_gan_yy else "劫財"
        # 生我者（印）
        if sheng_map.get(gan_wx) == day_gan_wx:
            return "偏印" if gan_yy == day_gan_yy else "正印"
        # 我生者（食傷）
        if sheng_map.get(day_gan_wx) == gan_wx:
            return "食神" if gan_yy == day_gan_yy else "傷官"
        # 剋我者（官殺）
        if ke_map.get(gan_wx) == day_gan_wx:
            return "七殺" if gan_yy == day_gan_yy else "正官"
        # 我剋者（財）
        if ke_map.get(day_gan_wx) == gan_wx:
            return "偏財" if gan_yy == day_gan_yy else "正財"
        return ''

    # 流月數據：每個流年對應 12 個流月
    # 結構：liuyue_by_liunian[dayun_idx][liunian_idx] = [12 個流月]
    liuyue_by_liunian = {}
    day_gan = res['八字'].split()[2][0] if len(res['八字'].split()) > 2 else '甲'

    for dayun_idx, liunian_list in liunian_by_dayun.items():
        liuyue_by_liunian[dayun_idx] = []
        for liunian_idx, liunian in enumerate(liunian_list):
            nian_gan = liunian['流年天干']
            yue_list = []
            for yue_idx, yue_zhi in enumerate(YUE_LING_ZHI):
                yue_gan = get_yue_gan(nian_gan, yue_idx)
                yue_shishen = get_yue_shishen(yue_gan, day_gan)
                yue_name = f"{yue_gan}{yue_zhi}"

                # 流月藏干（以月支為主）
                from bazi.core.constants import ZHI_CANG_GAN
                canggan = {}
                if yue_zhi in ZHI_CANG_GAN:
                    zhi_canggan = ZHI_CANG_GAN[yue_zhi]

                    # 使用共享函數計算藏干十神
                    if zhi_canggan.get('主氣'):
                        canggan['主氣'] = {'干': zhi_canggan['主氣'], '十神': get_canggan_shishen(zhi_canggan['主氣'], day_gan)}
                    if zhi_canggan.get('中氣'):
                        canggan['中氣'] = {'干': zhi_canggan['中氣'], '十神': get_canggan_shishen(zhi_canggan['中氣'], day_gan)}
                    if zhi_canggan.get('餘氣'):
                        canggan['餘氣'] = {'干': zhi_canggan['餘氣'], '十神': get_canggan_shishen(zhi_canggan['餘氣'], day_gan)}

                # 流月十二長生（以日干查月支）
                from bazi.core.constants import TIAN_GAN_ZHANG_SHENG
                chang_sheng = ''
                if day_gan in TIAN_GAN_ZHANG_SHENG and yue_zhi in TIAN_GAN_ZHANG_SHENG.get(day_gan, {}):
                    chang_sheng = TIAN_GAN_ZHANG_SHENG[day_gan][yue_zhi]

                yue_list.append({
                    '流月天干': yue_gan,
                    '流月地支': yue_zhi,
                    '流月名稱': yue_name,
                    '月份': YUE_LING_NAMES[yue_idx],
                    '流月十神': yue_shishen,
                    '藏干': canggan,
                    '十二長生': chang_sheng
                })

            liuyue_by_liunian[dayun_idx].append(yue_list)


    # 第一個大運和流年（使用 liunian_by_dayun 的數據）
    first_dayun = dayun_data[0] if dayun_data else {}
    first_liunian = all_liunian_data[0] if all_liunian_data else {}

    # 第一個流月（第一個流年第一個流月）
    first_liuyue = {}
    if liuyue_by_liunian.get(0) and liuyue_by_liunian[0][0]:
        first_liuyue = liuyue_by_liunian[0][0][0]  # [dayun_idx][liunian_idx][yue_idx]

    # 生成大運藏幹 HTML
    dayun_canggan_html = ''
    if first_dayun:
        canggan = first_dayun.get('地支', {}).get('藏干', {})
        if canggan and canggan.get('主氣'):
            main_qi = canggan['主氣']
            gan_wx = GAN_WU_XING.get(main_qi.get('干', ''), '')
            gan_class = get_wuxing_class(gan_wx)
            dayun_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{main_qi.get("干", "")}</span><span class="text-stone-400">{main_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('中氣'):
            mid_qi = canggan['中氣']
            if mid_qi:
                gan_wx = GAN_WU_XING.get(mid_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                dayun_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{mid_qi.get("干", "")}</span><span class="text-stone-400">{mid_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('餘氣'):
            rest_qi = canggan['餘氣']
            if rest_qi:
                gan_wx = GAN_WU_XING.get(rest_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                dayun_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{rest_qi.get("干", "")}</span><span class="text-stone-400">{rest_qi.get("十神", "")}</span></div>'

    # 生成流年藏干 HTML
    liunian_canggan_html = ''
    if first_liunian:
        canggan = first_liunian.get('藏干', {})
        if canggan and canggan.get('主氣'):
            main_qi = canggan['主氣']
            gan_wx = GAN_WU_XING.get(main_qi.get('干', ''), '')
            gan_class = get_wuxing_class(gan_wx)
            liunian_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{main_qi.get("干", "")}</span><span class="text-stone-400">{main_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('中氣'):
            mid_qi = canggan['中氣']
            if mid_qi:
                gan_wx = GAN_WU_XING.get(mid_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                liunian_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{mid_qi.get("干", "")}</span><span class="text-stone-400">{mid_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('餘氣'):
            rest_qi = canggan['餘氣']
            if rest_qi:
                gan_wx = GAN_WU_XING.get(rest_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                liunian_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{rest_qi.get("干", "")}</span><span class="text-stone-400">{rest_qi.get("十神", "")}</span></div>'

    # 生成流月藏干 HTML
    liuyue_canggan_html = ''
    if first_liuyue:
        canggan = first_liuyue.get('藏干', {})
        if canggan and canggan.get('主氣'):
            main_qi = canggan['主氣']
            gan_wx = GAN_WU_XING.get(main_qi.get('干', ''), '')
            gan_class = get_wuxing_class(gan_wx)
            liuyue_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{main_qi.get("干", "")}</span><span class="text-stone-400">{main_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('中氣'):
            mid_qi = canggan['中氣']
            if mid_qi:
                gan_wx = GAN_WU_XING.get(mid_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                liuyue_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{mid_qi.get("干", "")}</span><span class="text-stone-400">{mid_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('餘氣'):
            rest_qi = canggan['餘氣']
            if rest_qi:
                gan_wx = GAN_WU_XING.get(rest_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                liuyue_canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{rest_qi.get("干", "")}</span><span class="text-stone-400">{rest_qi.get("十神", "")}</span></div>'

    # 生成四柱 HTML - 順序：時、日、月、年（從左到右）
    # pillars 是 [年柱、月柱、日柱、時柱]，需要反轉
    pillar_html = ""
    for i in reversed(range(len(pillars))):  # 時柱->日柱->月柱->年柱
        p = pillars[i]
        pillar_html += f"""
        <div class="pillar-card flex flex-col items-center gap-1 p-2 bg-stone-50 rounded-xl border border-stone-200/50 min-w-[90px]" id="pillar-container-{i}">
            <span class="text-xs text-stone-400 font-medium tracking-widest uppercase">{p['name']}</span>
            <span class="text-[10px] text-stone-500 h-4" id="pillar-{i}-shishen">{p['shi_shen']}</span>
            <div class="w-11 h-11 flex items-center justify-center text-2xl font-serif font-bold rounded-full {get_wuxing_class(p['gan_wuxing'])['bg']} {get_wuxing_class(p['gan_wuxing'])['text']} border-2 {get_wuxing_class(p['gan_wuxing'])['border']}">
                {p['gan']}
            </div>
            <div class="w-11 h-11 flex items-center justify-center text-2xl font-serif font-bold {get_wuxing_class(p['zhi_wuxing'])['text']}">
                {p['zhi']}
            </div>
            <div class="flex flex-col gap-0.5 mt-1 items-center w-full min-h-[3.2rem]" id="pillar-{i}-canggan">
                {f"""<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{get_wuxing_class(GAN_WU_XING.get(p['zhugan'],''))['text'] if p['zhugan'] else ''}">{p['zhugan'] or ''}</span><span class="text-stone-400">{p['zhugan_shishen']}</span></div>""" if p['zhugan'] else ''}
                {f"""<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{get_wuxing_class(GAN_WU_XING.get(p['zhongqi'],''))['text'] if p['zhongqi'] else ''}">{p['zhongqi'] or ''}</span><span class="text-stone-400">{p['zhongqi_shishen']}</span></div>""" if p['zhongqi'] else ''}
                {f"""<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{get_wuxing_class(GAN_WU_XING.get(p['yuqi'],''))['text'] if p['yuqi'] else ''}">{p['yuqi'] or ''}</span><span class="text-stone-400">{p['yuqi_shishen']}</span></div>""" if p['yuqi'] else ''}
            </div>
            <div class="text-[9px] text-stone-500 font-medium">{p['chang_sheng']}</div>
        </div>
        """

    # 生成大運選擇 HTML - 使用整合分析中的大運分析數據（與 dayunData 一致）
    dayun_pillars_html = ""
    for i, dy in enumerate(dayun_data):
        active_class = 'border-indigo-500 bg-indigo-50' if i == 0 else 'border-stone-200 bg-stone-50 hover:bg-stone-100'

        # 生成藏干 HTML
        canggan = dy.get('地支', {}).get('藏干', {})
        canggan_html = ''
        if canggan and canggan.get('主氣'):
            main_qi = canggan['主氣']
            gan_wx = GAN_WU_XING.get(main_qi.get('干', ''), '')
            gan_class = get_wuxing_class(gan_wx)
            canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{main_qi.get("干", "")}</span><span class="text-stone-400">{main_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('中氣'):
            mid_qi = canggan['中氣']
            if mid_qi:
                gan_wx = GAN_WU_XING.get(mid_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{mid_qi.get("干", "")}</span><span class="text-stone-400">{mid_qi.get("十神", "")}</span></div>'
        if canggan and canggan.get('餘氣'):
            rest_qi = canggan['餘氣']
            if rest_qi:
                gan_wx = GAN_WU_XING.get(rest_qi.get('干', ''), '')
                gan_class = get_wuxing_class(gan_wx)
                canggan_html += f'<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="{gan_class["text"]}">{rest_qi.get("干", "")}</span><span class="text-stone-400">{rest_qi.get("十神", "")}</span></div>'

        # 獲取大運干支
        dy_gan = dy.get('天干', {}).get('干', '')
        dy_zhi = dy.get('地支', {}).get('支', '')
        dy_shishen = dy.get('天干', {}).get('十神', '')
        dy_qiyun = dy.get('起運年齡', 0)

        dayun_pillars_html += f"""
        <div id="dayun-pillar-{i}" class="dayun-pillar-select cursor-pointer pillar-card flex flex-col items-center gap-1 p-2 rounded-xl border min-w-[80px] transition-all {active_class}" onclick="selectDayun({i})">
            <span class="text-xs text-stone-400 font-medium">{dy_qiyun}歲</span>
            <span class="text-[10px] text-stone-500 h-4">{dy_shishen}</span>
            <div class="w-10 h-10 flex items-center justify-center text-2xl font-serif font-bold rounded-full {get_wuxing_class(GAN_WU_XING.get(dy_gan,''))['bg']} {get_wuxing_class(GAN_WU_XING.get(dy_gan,''))['text']} border-2 {get_wuxing_class(GAN_WU_XING.get(dy_gan,''))['border']}">
                {dy_gan}
            </div>
            <div class="w-10 h-10 flex items-center justify-center text-2xl font-serif font-bold {get_wuxing_class(ZHI_WU_XING.get(dy_zhi,''))['text']}">
                {dy_zhi}
            </div>
            <div class="flex flex-col gap-0.5 mt-1 items-center w-full min-h-[3.2rem]" id="dayun-pillar-{i}-canggan">
                {canggan_html}
            </div>
        </div>
        """

    # 生成地支關係 HTML - 使用中文 key
    zhi_relations = res.get('地支關係', {})
    zhi_relations_html = ""

    # 直接使用中文 key 匹配
    relation_keys = [
        ('六合', '六合'), ('六沖', '六沖'), ('三合局', '三合局'),
        ('半合局', '半合局'), ('拱局', '拱局'), ('閘合局', '閘合局'),
        ('三會方', '三會方'), ('刑', '刑'), ('穿', '穿'), ('破', '破')
    ]

    for key, label in relation_keys:
        if key in zhi_relations and zhi_relations[key]:
            items = zhi_relations[key]
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        # 獲取關係字符串 - 根據不同類型取不同字段
                        # 六合、六沖、刑、穿、破等取對應字段
                        relation_str = item.get('合', item.get('沖', item.get('刑', item.get('穿', item.get('破', item.get('局', ''))))))
                        position = item.get('位置', '')
                        status = item.get('狀態', '')
                        combo = item.get('組合', '')

                        # 構建顯示字符串
                        if relation_str:
                            display = relation_str
                        elif combo:
                            # 三合局、半合局等用組合
                            display = combo
                        else:
                            display = label

                        if position:
                            display += f' ({position})'
                        if status:
                            display += f' [{status}]'
                        zhi_relations_html += f'<span class="px-3 py-1.5 rounded-lg text-sm bg-blue-50 text-blue-700 border border-blue-200">{label}: {display}</span>'
                    elif isinstance(item, str):
                        zhi_relations_html += f'<span class="px-3 py-1.5 rounded-lg text-sm bg-blue-50 text-blue-700 border border-blue-200">{label}: {item}</span>'
                    elif isinstance(item, list):
                        zhi_relations_html += f'<span class="px-3 py-1.5 rounded-lg text-sm bg-blue-50 text-blue-700 border border-blue-200">{label}: {"-".join(item)}</span>'
            elif isinstance(items, str):
                zhi_relations_html += f'<span class="px-3 py-1.5 rounded-lg text-sm bg-blue-50 text-blue-700 border border-blue-200">{label}: {items}</span>'

    # 十神性格 HTML
    shishen_personality_html = render_shishen_personality(res['格局'].get('十神性格', {}))

    # 格局形式
    ge_ju_forms = res['格局'].get('格局形式', [])
    ge_ju_forms_str = ', '.join([f['形式'] for f in ge_ju_forms]) if ge_ju_forms and ge_ju_forms[0].get('形式') != '普通格' else ''

    # 格局形式詳解 HTML
    ge_ju_forms_detail_html = ''
    if ge_ju_forms and ge_ju_forms[0].get('形式') != '普通格':
        form_details = []
        for form in ge_ju_forms:
            form_name = form.get('形式', '')
            form_desc = form.get('說明', '')
            form_feature = form.get('特徵', '')
            form_details.append(f"""
            <div class="p-3 rounded-lg bg-white border border-amber-200">
                <div class="text-sm font-bold text-amber-800 mb-1">{form_name}</div>
                <div class="text-xs text-stone-600 mb-1">{form_desc}</div>
                <div class="text-xs text-amber-600">特徵：{form_feature}</div>
            </div>
            """)
        ge_ju_forms_detail_html = ''.join(form_details)

    # 格局成敗樣式
    ge_cheng_bai = res['格局']['成敗']
    if '成' in ge_cheng_bai and '不成' not in ge_cheng_bai:
        ge_cheng_bai_class = 'bg-green-50 border-green-200'
        ge_cheng_bai_text_class = 'text-green-600'
    elif '不成' in ge_cheng_bai or '破格' in ge_cheng_bai:
        ge_cheng_bai_class = 'bg-red-50 border-red-200'
        ge_cheng_bai_text_class = 'text-red-600'
    else:
        ge_cheng_bai_class = 'bg-amber-50 border-amber-200'
        ge_cheng_bai_text_class = 'text-amber-600'

    # 格局成敗分析 HTML
    ge_cheng_bai_analysis_html = ''.join([f"<div>• {a}</div>" for a in res['格局']['成敗分析']])

    # 喜神忌神
    xi_shen_wu_xing = ', '.join(res['格局'].get('喜神五行', [])) if res['格局'].get('喜神五行') else '無'
    ji_shen_wu_xing = ', '.join(res['格局'].get('忌神五行', [])) if res['格局'].get('忌神五行') else '無'

    # 用神五行
    yong_shen_wu_xing = res['格局'].get('用神', '')
    yong_shen_xing_zhi = res['格局'].get('用神性質', '中性')
    if yong_shen_xing_zhi == '吉神':
        yong_shen_xing_zhi_class = 'text-green-600'
    elif yong_shen_xing_zhi == '凶神':
        yong_shen_xing_zhi_class = 'text-red-600'
    else:
        yong_shen_xing_zhi_class = 'text-stone-600'

    # 整合分析數據
    integrated = res.get('整合分析', {})
    ge_ju_core = integrated.get('格局核心', {})
    yong_shen_core = ge_ju_core.get('用神', '')
    xiang_shen_core = ', '.join(ge_ju_core.get('相神', [])) if ge_ju_core.get('相神') else '待定'
    xi_shen_core = ', '.join(ge_ju_core.get('喜神十神', [])) if ge_ju_core.get('喜神十神') else '無'
    xi_shen_core_wu_xing = ', '.join(ge_ju_core.get('喜神五行', [])) if ge_ju_core.get('喜神五行') else '無'
    ji_shen_core = ', '.join(ge_ju_core.get('忌神十神', [])) if ge_ju_core.get('忌神十神') else '無'
    ji_shen_core_wu_xing = ', '.join(ge_ju_core.get('忌神五行', [])) if ge_ju_core.get('忌神五行') else '無'

    # 格局解讀
    ge_ju_jie_du = integrated.get('格局解讀', {})
    yong_shen_jie_du = ge_ju_jie_du.get('用神解讀', '')
    ji_shen_jie_du = ge_ju_jie_du.get('忌神解讀', '')

    # 根氣強度 HTML
    gen_qi_table_html = ''.join([f"""
    <tr class="hover:bg-stone-50/50">
        <td class="p-2 border border-stone-200">{dg['柱']}</td>
        <td class="p-2 border border-stone-200 font-medium">{dg['地支']}</td>
        <td class="p-2 border border-stone-200 {'text-green-600' if dg['日主得根'] else 'text-red-600'}">{'是' if dg['日主得根'] else '否'}</td>
        <td class="p-2 border border-stone-200">{dg.get('日主根氣強度', 0)}</td>
        <td class="p-2 border border-stone-200 text-xs text-stone-600">{', '.join([f"{k}{v}" for k,v in dg['藏干'].items()])}</td>
    </tr>
    """ for dg in res['旺衰']['地支得根']])

    gen_qi_total_html = ''.join([f"""
    <div class="p-2 bg-stone-50 rounded-lg border border-stone-200">
        <div class="text-xs text-stone-500 mb-1">{['年干','月干','日干','時干'][i]}（{GAN_WU_XING.get(res['八字'].split()[i][0], '')}</div>
        <div class="text-sm font-medium">
            總根氣：<span class="text-stone-700">{res['旺衰'].get(res['八字'].split()[i][0] + '_總根氣', 0)}</span>
        </div>
        <div class="text-xs text-stone-600 mt-1">
            {res['旺衰'].get(res['八字'].split()[i][0] + '_根氣論斷', '虛浮無根')}
        </div>
    </div>
    """ for i in range(4)])

    # 先天病源 HTML
    xian_tian_bing_yuan = res.get('先天病源', {})
    yue_ling = xian_tian_bing_yuan.get('月令', {}).get('月支', '')
    dang_ling_wu_xing = xian_tian_bing_yuan.get('月令', {}).get('當令五行', '')

    wu_xing_fen_bu_html = ''.join([f"""<span class="px-2 py-1 rounded text-xs bg-stone-200">{wx}:{info['數量']}個 ({info['狀態']})</span>""" for wx, info in xian_tian_bing_yuan.get('五行分布', {}).items()])

    wu_xing_guo_wang_html = ''.join([f"""<div class="text-sm text-red-700 mb-1">• {item['五行']}:{item['數量']}個 ({item['臟腑']})</div>""" for item in xian_tian_bing_yuan.get('五行過旺', {}).get('列表', [])])
    wu_xing_que_shi_html = ''.join([f"""<div class="text-sm text-red-700 mb-1">• {item['五行']}缺失 ({item['臟腑']})</div>""" for item in xian_tian_bing_yuan.get('五行缺失', {}).get('列表', [])])
    gai_tou_jie_jiao_html = ''.join([f"""<div class="text-sm text-amber-700 mb-1">• {item['位置']}({item['干支']}): {item['類型']} - {item['說明']}</div>""" for item in xian_tian_bing_yuan.get('蓋頭截腳', {}).get('列表', [])])

    # 宮位數據
    gong_wei = res.get('宮位', {})
    liu_qin_gong_wei = gong_wei.get('六親宮位', {})

    # 神煞數據
    shen_sha = res.get('神煞', {})
    shi_yong_shen_sha = shen_sha.get('實用神煞', [])
    can_kao_shen_sha = shen_sha.get('參考神煞', [])

    shi_yong_shen_sha_html = ''.join([f"""
    <div class="px-3 py-2 rounded-lg text-sm bg-green-50 text-green-700 border border-green-200">
        <span class="font-medium">{ss['神煞']}</span>
        <span class="opacity-70 text-xs ml-1">({ss['位置']})</span>
    </div>
    """ for ss in shi_yong_shen_sha])

    can_kao_shen_sha_html = ''.join([f"""
    <div class="px-3 py-2 rounded-lg text-sm bg-stone-50 text-stone-600 border border-stone-200">
        <span class="font-medium">{ss['神煞']}</span>
        <span class="opacity-70 text-xs ml-1">({ss['位置']})</span>
    </div>
    """ for ss in can_kao_shen_sha])

    # 六十甲子
    liu_shi_jia_zi = res.get('六十甲子', {})
    liu_qin_lei_hua_html = ''.join([f"""<span class="px-2 py-1 rounded bg-stone-100 text-sm">{lq['干支']}({lq['六親']})</span>""" for lq in liu_shi_jia_zi.get('六親類化', [])])

    # 準備模板上下文
    context = {
        'name': res['姓名'],
        'gender': res['性別'],
        'solar_time': res['出生時間']['公曆'],
        'solar_date': res['出生時間']['公曆'],
        'lunar_date': res['出生時間']['農曆'],
        'birth_city': res['出生城市'],
        'jie_qi': res['節氣'],
        'da_yun': res['大運'],
        'dayun_gender': res['詳細大運']['性別'],
        'dayun_paifa': res['詳細大運']['排法'],

        # 四柱
        'pillar_html': pillar_html,

        # 大運流年
        'dayun_pillars_html': dayun_pillars_html,
        'dayun_shishen': first_dayun.get('天干', {}).get('十神', ''),
        'dayun_gan': first_dayun.get('天干', {}).get('干', ''),
        'dayun_zhi': first_dayun.get('地支', {}).get('支', ''),
        'dayun_gan_class': get_wuxing_class(GAN_WU_XING.get(first_dayun.get('天干', {}).get('干', ''), ''))['bg'] + ' ' + get_wuxing_class(GAN_WU_XING.get(first_dayun.get('天干', {}).get('干', ''), ''))['text'] + ' ' + get_wuxing_class(GAN_WU_XING.get(first_dayun.get('天干', {}).get('干', ''), ''))['border'],
        'dayun_zhi_class': get_wuxing_class(ZHI_WU_XING.get(first_dayun.get('地支', {}).get('支', ''), ''))['text'],
        'dayun_changsheng': first_dayun.get('地支', {}).get('十二長生', ''),
        'dayun_canggan_html': dayun_canggan_html,
        'liunian_shishen': first_liunian.get('流年十神', ''),
        'liunian_gan': first_liunian.get('流年天干', ''),
        'liunian_zhi': first_liunian.get('流年地支', ''),
        'liunian_gan_class': get_wuxing_class(GAN_WU_XING.get(first_liunian.get('流年天干', ''), ''))['bg'] + ' ' + get_wuxing_class(GAN_WU_XING.get(first_liunian.get('流年天干', ''), ''))['text'] + ' ' + get_wuxing_class(GAN_WU_XING.get(first_liunian.get('流年天干', ''), ''))['border'],
        'liunian_zhi_class': get_wuxing_class(ZHI_WU_XING.get(first_liunian.get('流年地支', ''), ''))['text'],
        'liunian_canggan_html': liunian_canggan_html,
        'liunian_changsheng': first_liunian.get('十二長生', ''),

        # 流月（默認第一個流月 - 正月）
        'liuyue_by_liunian_json': json.dumps(liuyue_by_liunian),
        'liuyue_shishen': first_liuyue.get('流月十神', ''),
        'liuyue_gan': first_liuyue.get('流月天干', ''),
        'liuyue_zhi': first_liuyue.get('流月地支', ''),
        'liuyue_gan_class': get_wuxing_class(GAN_WU_XING.get(first_liuyue.get('流月天干', ''), ''))['bg'] + ' ' + get_wuxing_class(GAN_WU_XING.get(first_liuyue.get('流月天干', ''), ''))['text'] + ' ' + get_wuxing_class(GAN_WU_XING.get(first_liuyue.get('流月天干', ''), ''))['border'],
        'liuyue_zhi_class': get_wuxing_class(ZHI_WU_XING.get(first_liuyue.get('流月地支', ''), ''))['text'],
        'liuyue_canggan_html': liuyue_canggan_html,
        'liuyue_changsheng': first_liuyue.get('十二長生', ''),

        # 十神性格
        'shishen_personality_html': shishen_personality_html,

        # 格局
        'ge_ju_name': res['格局']['格局'],
        'ge_ju_forms': ge_ju_forms_str,
        'ge_ju_forms_detail': ge_ju_forms if ge_ju_forms else [],
        'ge_ju_forms_detail_html': ge_ju_forms_detail_html,
        'yong_shen': res['格局']['用神'],
        'yong_shen_xing_zhi': yong_shen_xing_zhi,
        'yong_shen_xing_zhi_class': yong_shen_xing_zhi_class,
        'yong_shen_fang_shi': res['格局'].get('用神方式', ''),
        'xiang_shen': ', '.join(res['格局'].get('相神', ['待定'])),
        'ding_ge_lai_yuan': res['格局']['定格來源'],
        'xiang_shen_chong_tu': res['格局'].get('相神衝突', ''),
        'ge_cheng_bai': ge_cheng_bai,
        'ge_cheng_bai_class': ge_cheng_bai_class,
        'ge_cheng_bai_text_class': ge_cheng_bai_text_class,
        'ge_cheng_bai_analysis_html': ge_cheng_bai_analysis_html,
        'xi_shen_wu_xing': xi_shen_wu_xing,
        'ji_shen_wu_xing': ji_shen_wu_xing,

        # 整合分析
        'yong_shen_jie_du': yong_shen_jie_du,
        'ji_shen_jie_du': ji_shen_jie_du,
        'yong_shen_core': yong_shen_core,
        'xiang_shen_core': xiang_shen_core,
        'xi_shen_core': xi_shen_core,
        'xi_shen_core_wu_xing': xi_shen_core_wu_xing,
        'ji_shen_core': ji_shen_core,
        'ji_shen_core_wu_xing': ji_shen_core_wu_xing,

        # 根氣強度
        'gen_qi_table_html': gen_qi_table_html,
        'gen_qi_total_html': gen_qi_total_html,
        'ri_zhu_gen_qi_zong': res['旺衰'].get('日主旺衰', {}).get('根氣強度', 0),
        'gen_qi_lun_duan': res['旺衰'].get('根氣論斷', '虛浮無根'),

        # 先天病源
        'yue_ling': yue_ling,
        'dang_ling_wu_xing': dang_ling_wu_xing,
        'wu_xing_fen_bu_html': wu_xing_fen_bu_html,
        'wu_xing_guo_wang': xian_tian_bing_yuan.get('五行過旺', {}).get('列表', []),
        'wu_xing_guo_wang_html': wu_xing_guo_wang_html,
        'wu_xing_que_shi': xian_tian_bing_yuan.get('五行缺失', {}).get('列表', []),
        'wu_xing_que_shi_html': wu_xing_que_shi_html,
        'gai_tou_jie_jiao': xian_tian_bing_yuan.get('蓋頭截腳', {}).get('列表', []),
        'gai_tou_jie_jiao_html': gai_tou_jie_jiao_html,

        # 六十甲子
        'ri_zhu': liu_shi_jia_zi.get('日柱', ''),
        'suo_shu_xun': liu_shi_jia_zi.get('所屬旬', ''),
        'xun_cheng_yuan': ' '.join(liu_shi_jia_zi.get('旬成員', [])),
        'liu_qin_lei_hua_html': liu_qin_lei_hua_html,

        # 神煞
        'has_shen_sha': bool(shi_yong_shen_sha or can_kao_shen_sha),
        'shi_yong_shen_sha_count': len(shi_yong_shen_sha),
        'shi_yong_shen_sha_html': shi_yong_shen_sha_html,
        'can_kao_shen_sha': bool(can_kao_shen_sha),
        'can_kao_shen_sha_count': len(can_kao_shen_sha),
        'can_kao_shen_sha_html': can_kao_shen_sha_html,

        # 宮位
        'nian_gan_liu_qin': liu_qin_gong_wei.get('年柱', {}).get('祖輩宮', {}).get('年干', ''),
        'nian_zhi_liu_qin': liu_qin_gong_wei.get('年柱', {}).get('祖輩宮', {}).get('年支', ''),
        'yue_gan_liu_qin': liu_qin_gong_wei.get('月柱', {}).get('父母兄弟宮', {}).get('月干', ''),
        'yue_zhi_liu_qin': liu_qin_gong_wei.get('月柱', {}).get('父母兄弟宮', {}).get('月支', ''),
        'ri_gan_liu_qin': liu_qin_gong_wei.get('日柱', {}).get('夫妻宮', {}).get('日干', ''),
        'ri_zhi_liu_qin': liu_qin_gong_wei.get('日柱', {}).get('夫妻宮', {}).get('日支', ''),
        'shi_gan_liu_qin': liu_qin_gong_wei.get('時柱', {}).get('晚輩宮', {}).get('時干', ''),
        'shi_zhi_liu_qin': liu_qin_gong_wei.get('時柱', {}).get('晚輩宮', {}).get('時支', ''),
        'nian_zhu_shen_ti': gong_wei.get('身體宮位', {}).get('年柱', {}).get('宮位', ''),
        'nian_zhu_shi_xu': gong_wei.get('身體宮位', {}).get('年柱', {}).get('時序', ''),
        'yue_zhu_shen_ti': gong_wei.get('身體宮位', {}).get('月柱', {}).get('宮位', ''),
        'yue_zhu_shi_xu': gong_wei.get('身體宮位', {}).get('月柱', {}).get('時序', ''),
        'ri_zhu_shen_ti': gong_wei.get('身體宮位', {}).get('日柱', {}).get('宮位', ''),
        'ri_zhu_shi_xu': gong_wei.get('身體宮位', {}).get('日柱', {}).get('時序', ''),
        'shi_zhu_shen_ti': gong_wei.get('身體宮位', {}).get('時柱', {}).get('宮位', ''),
        'shi_zhu_shi_xu': gong_wei.get('身體宮位', {}).get('時柱', {}).get('時序', ''),

        # 宮位吉凶
        'gong_wei_ji_xiong': gong_wei.get('宮位吉凶', []),
        'gong_wei_ji_xiong_html': generate_gongwei_jixiong_html(gong_wei.get('宮位吉凶', [])),

        # 疾病論斷
        'ji_bing_lun_duan': gong_wei.get('疾病論斷', {}),
        'ji_jie_ti_zhi': gong_wei.get('疾病論斷', {}).get('季節體質', '未知'),
        'ji_bing_lun_duan_count': len(gong_wei.get('疾病論斷', {}).get('疾病論斷', [])),
        'ji_bing_lun_duan_html': generate_jibing_lunduan_html(gong_wei.get('疾病論斷', {}).get('疾病論斷', [])),

        # 天干地支對應臟腑
        'tian_gan_zang_fu': generate_zangfu_html(gong_wei.get('天干對應臟腑', {})),
        'zhi_zang_fu': generate_zangfu_html(gong_wei.get('地支對應臟腑', {})),

        # 五行分布表
        'wu_xing_fen_bu_biao_html': generate_wuxing_fenbu_biao_html(xian_tian_bing_yuan.get('五行分布', {})),

        # 大運判斷
        'da_yun_pan_duan': res.get('大運判斷', {}),
        'da_yun_pan_duan_html': generate_dayun_panduan_html(res.get('大運判斷', {}).get('十個大運分析', [])),

        # 流年判斷
        'liu_nian_pan_duan': res.get('流年判斷', {}),
        'liu_nian_pan_duan_html': generate_liunian_panduan_html(res.get('流年判斷', {}).get('流年分析', [])[:10]),

        # ========== 兩層格局 ==========
        # 原局格局
        'yuan_ju_ge_ju': res.get('原局格局', {}),

        # 歲運格局（compute_bazi 已提取內層數據）
        'sui_yun_ge_ju': res.get('歲運格局', {}),

        # ========== 其他新功能 ==========
        # 一柱論命
        'yi_zhu': res.get('一柱論命', {}),

        # 八字卦
        'bazi_gua': res.get('bazi_gua', {}),

        # 十神組合斷語 (從整合分析中提取)
        'shishen_combinations': res.get('整合分析', {}).get('十神組合斷語', []),

        # 健康建議 (從整合分析中提取)
        'health_suggestions': res.get('整合分析', {}).get('健康分析', {}).get('生活調理', {}),

        # 干支象法
        'ganzhi_xiang': res.get('干支象法', {}),

        # 移花接木
        'yi_hua_jie_mu': res.get('移花接木', {}),

        # 兩格並存
        'liang_ge_bing_cun': res.get('兩格並存', {}),

        # JSON 數據（供 JavaScript 使用）
        'all_liunian_data_json': json.dumps(all_liunian_data, ensure_ascii=False),
        'liunian_by_dayun_json': json.dumps(liunian_by_dayun, ensure_ascii=False),
        'liuyue_by_liunian_json': json.dumps(liuyue_by_liunian, ensure_ascii=False),
        'four_pillars_json': json.dumps(res['八字'].split(), ensure_ascii=False),
        'dayun_data_json': json.dumps(dayun_data, ensure_ascii=False),

        # 歲運格局數據（供動態切換使用）
        'sui_yun_ge_ju_all_json': json.dumps(res.get('歲運格局全部', []), ensure_ascii=False),

        # 地支關係
        'zhi_relations_html': zhi_relations_html,

        # 其他
        'has_zhi_relations': any(res['地支關係'].values()),
    }

    return template.render(**context)


@app.get("/", response_class=HTMLResponse)
async def index():
    """首頁"""
    return render_index_html()


@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    name: str = Form(""), gender: str = Form(...), calendar: str = Form(...),
    year: int = Form(...), month: int = Form(...), day: int = Form(...),
    hour: int = Form(...), minute: int = Form(...), birth_city: str = Form(...)
):
    """計算八字（日期輸入模式）"""
    calendar_map = {"公曆": "公曆", "農曆": "農曆"}
    calendar_std = calendar_map.get(calendar, calendar)

    data = {
        "name": name, "gender": gender, "calendar": calendar_std,
        "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "birth_city": birth_city
    }
    res = compute_bazi(data)

    # 解析八字 - 生成 pillars 數組（順序：年柱、月柱、日柱、時柱）
    ba_zi_list = res['八字'].split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]
    pillars = []
    for i in range(4):  # 年 -> 時
        p = ba_zi_list[i]
        gan = p[0]
        zhi = p[1]
        pillar_name = pillar_names[i]

        # 新版 shi_shen 結構：{ "年柱": { "天干十神": ..., "藏干十神": {...} }, ... }
        pillar_shishen = res['十神'].get(pillar_name, {})
        cang_gan_data = res['藏干'].get(pillar_name, {})

        # 獲取天干十神（日干是日主，不顯示十神）
        if i == 2:  # 日柱索引是 2
            shi_shen = ''  # 日干是日主，不顯示十神
        else:
            shi_shen = pillar_shishen.get('天干十神', '')

        # 獲取藏干十神
        canggan_shishen = pillar_shishen.get('藏干十神', {})
        zhugan_shishen = canggan_shishen.get('主氣', {}) or {}
        zhongqi_shishen = canggan_shishen.get('中氣', {}) or {}
        yuqi_shishen = canggan_shishen.get('餘氣', {}) or {}

        # 獲取十二長生（兼容新舊字段名）
        chang_sheng_data = res['十二長生'].get(pillar_name, {})
        chang_sheng = chang_sheng_data.get('十二長生', chang_sheng_data.get('長生狀態', ''))

        pillars.append({
            "name": pillar_names[i],
            "gan": gan,
            "zhi": zhi,
            "gan_wuxing": GAN_WU_XING[gan],
            "zhi_wuxing": ZHI_WU_XING[zhi],
            "shi_shen": shi_shen,
            "zhugan": cang_gan_data.get('主氣'),
            "zhugan_shishen": zhugan_shishen.get('十神', ''),
            "zhongqi": cang_gan_data.get('中氣'),
            "zhongqi_shishen": zhongqi_shishen.get('十神', ''),
            "yuqi": cang_gan_data.get('餘氣'),
            "yuqi_shishen": yuqi_shishen.get('十神', ''),
            "chang_sheng": chang_sheng,
            "wangshuai": "",
            "degeng": "",
        })

    ji_shens = [js['五行'] for js in res['先天病源']['忌神分析']['忌神列表']]
    yong_shens = [ys['五行'] for ys in res['先天病源']['用神分析']['用神列表']]

    return generate_bazi_result_html(res, pillars, ji_shens, yong_shens)


@app.post("/calculate_from_pillars", response_class=HTMLResponse)
async def calculate_from_pillars(
    name: str = Form(""),
    gender: str = Form(...),
    year_gan: str = Form(...), year_zhi: str = Form(...),
    month_gan: str = Form(...), month_zhi: str = Form(...),
    day_gan: str = Form(...), day_zhi: str = Form(...),
    hour_gan: str = Form(...), hour_zhi: str = Form(...)
):
    """從四柱反推出生日時並計算八字"""
    possible_dates = BaZiCalculator.calculate_date_from_pillars(
        year_gan, year_zhi, month_gan, month_zhi,
        day_gan, day_zhi, hour_gan, hour_zhi
    )

    if not possible_dates:
        return show_pillar_error_html(f"無法在 1900-2100 年範圍內找到匹配的四柱：{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}")

    if len(possible_dates) == 1:
        data = {
            "name": name, "gender": gender,
            "calendar": possible_dates[0]['calendar'],
            "year": possible_dates[0]['year'],
            "month": possible_dates[0]['month'],
            "day": possible_dates[0]['day'],
            "hour": possible_dates[0]['hour'],
            "minute": possible_dates[0]['minute'],
            "birth_city": "香港"
        }
        res = compute_bazi(data)
        return render_pillar_result_html(res, data, possible_dates[0])

    return show_date_selection_html(possible_dates, name, gender)


def show_pillar_error_html(error_message: str) -> str:
    """顯示四柱反推錯誤信息"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-HK">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>錯誤 - 八字排盤</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body class="bg-stone-100 min-h-screen">
        <header class="bg-white border-b border-stone-200 sticky top-0 z-20 shadow-sm">
            <div class="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <span class="w-8 h-8 bg-stone-900 text-white flex items-center justify-center rounded-lg text-sm font-bold">八字</span>
                    <span class="text-lg font-serif font-bold text-stone-900">命盤排盤系統</span>
                </div>
            </div>
        </header>
        <main class="max-w-6xl mx-auto px-4 py-6">
            <div class="bg-white rounded-2xl shadow-sm border border-red-200 p-6">
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                        <span class="text-red-600 text-xl">!</span>
                    </div>
                    <h2 class="text-xl font-bold text-red-800">反推失敗</h2>
                </div>
                <p class="text-stone-700 mb-6">{error_message}</p>
                <div class="bg-stone-50 rounded-lg p-4 text-sm text-stone-600">
                    <p>可能原因：</p>
                    <ul class="list-disc list-inside mt-2 space-y-1">
                        <li>四柱組合在 1900-2100 年範圍內不存在</li>
                        <li>月柱與年干不匹配（五虎遁）</li>
                        <li>時柱與日干不匹配（五鼠遁）</li>
                    </ul>
                </div>
                <a href="/" class="mt-6 inline-block bg-stone-900 text-white px-6 py-2 rounded-lg hover:bg-black transition">返回首頁</a>
            </div>
        </main>
        <script src="/static/js/app.js"></script>
    </body>
    </html>
    """


def show_date_selection_html(possible_dates: list, name: str, gender: str) -> str:
    """顯示日期選擇界面"""
    date_options_html = ""
    for i, date in enumerate(possible_dates):
        date_options_html += f"""
        <div class="p-4 bg-stone-50 rounded-lg border border-stone-200 hover:border-stone-400 transition">
            <div class="flex items-center justify-between mb-2">
                <div class="font-bold text-stone-800">{date['year']}年{date['month']}月{date['day']}日</div>
                <form action="/select_date" method="post" class="inline">
                    <input type="hidden" name="name" value="{name}">
                    <input type="hidden" name="gender" value="{gender}">
                    <input type="hidden" name="selected_index" value="{i}">
                    <input type="hidden" name="year" value="{date['year']}">
                    <input type="hidden" name="month" value="{date['month']}">
                    <input type="hidden" name="day" value="{date['day']}">
                    <input type="hidden" name="hour" value="{date['hour']}">
                    <input type="hidden" name="minute" value="{date['minute']}">
                    <input type="hidden" name="calendar" value="{date['calendar']}">
                    <button type="submit" class="bg-stone-900 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-black transition">選擇此日期</button>
                </form>
            </div>
            <p class="text-sm text-stone-600">{date['note']}</p>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="zh-HK">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>選擇日期 - 八字排盤</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body class="bg-stone-100 min-h-screen">
        <header class="bg-white border-b border-stone-200 sticky top-0 z-20 shadow-sm">
            <div class="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <span class="w-8 h-8 bg-stone-900 text-white flex items-center justify-center rounded-lg text-sm font-bold">八字</span>
                    <span class="text-lg font-serif font-bold text-stone-900">命盤排盤系統</span>
                </div>
            </div>
        </header>
        <main class="max-w-6xl mx-auto px-4 py-6">
            <div class="bg-white rounded-2xl shadow-sm border border-stone-100 p-6">
                <h2 class="text-xl font-bold text-stone-800 mb-2">找到多個可能的出生日期</h2>
                <p class="text-stone-600 mb-6">由於六十甲子 60 年一循環，以下日期都匹配您輸入的四柱。請選擇正確的日期：</p>
                <div class="space-y-4">
                    {date_options_html}
                </div>
                <a href="/" class="mt-6 inline-block text-stone-600 hover:text-stone-800 transition">← 返回重新輸入</a>
            </div>
        </main>
        <script src="/static/js/app.js"></script>
    </body>
    </html>
    """


def render_pillar_result_html(res: dict, data: dict, selected_date: dict) -> str:
    """渲染四柱反推結果頁面"""
    # 解析八字 - 生成 pillars 數組（順序：年柱、月柱、日柱、時柱）
    ba_zi_list = res['八字'].split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]
    pillars = []
    for i in range(4):  # 年 -> 時
        p = ba_zi_list[i]
        gan = p[0]
        zhi = p[1]
        pillar_name = pillar_names[i]

        # 新版 shi_shen 結構：{ "年柱": { "天干十神": ..., "藏干十神": {...} }, ... }
        pillar_shishen = res['十神'].get(pillar_name, {})
        cang_gan_data = res['藏干'].get(pillar_name, {})

        # 獲取天干十神（日干是日主，不顯示十神）
        if i == 2:  # 日柱索引是 2
            shi_shen = ''  # 日干是日主，不顯示十神
        else:
            shi_shen = pillar_shishen.get('天干十神', '')

        # 獲取藏干十神
        canggan_shishen = pillar_shishen.get('藏干十神', {})
        zhugan_shishen = canggan_shishen.get('主氣', {}) or {}
        zhongqi_shishen = canggan_shishen.get('中氣', {}) or {}
        yuqi_shishen = canggan_shishen.get('餘氣', {}) or {}

        # 獲取十二長生（兼容新舊字段名）
        chang_sheng_data = res['十二長生'].get(pillar_name, {})
        chang_sheng = chang_sheng_data.get('十二長生', chang_sheng_data.get('長生狀態', ''))

        pillars.append({
            "name": pillar_names[i],
            "gan": gan,
            "zhi": zhi,
            "gan_wuxing": GAN_WU_XING[gan],
            "zhi_wuxing": ZHI_WU_XING[zhi],
            "shi_shen": shi_shen,
            "zhugan": cang_gan_data.get('主氣'),
            "zhugan_shishen": zhugan_shishen.get('十神', ''),
            "zhongqi": cang_gan_data.get('中氣'),
            "zhongqi_shishen": zhongqi_shishen.get('十神', ''),
            "yuqi": cang_gan_data.get('餘氣'),
            "yuqi_shishen": yuqi_shishen.get('十神', ''),
            "chang_sheng": chang_sheng,
            "wangshuai": "",
            "degeng": "",
        })

    ji_shens = [js['五行'] for js in res['先天病源']['忌神分析']['忌神列表']]
    yong_shens = [ys['五行'] for ys in res['先天病源']['用神分析']['用神列表']]

    main_html = generate_bazi_result_html(res, pillars, ji_shens, yong_shens)

    # 添加反推信息提示
    pillar_info_html = f"""
    <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <div class="flex items-center gap-2 mb-2">
            <span class="text-green-600 text-lg">✓</span>
            <span class="font-bold text-green-800">四柱反推成功</span>
        </div>
        <p class="text-sm text-green-700">
            反推結果：<span class="font-medium">{selected_date['year']}年{selected_date['month']}月{selected_date['day']}日 {selected_date['hour']}:{selected_date['minute']:02d}</span> ({selected_date['calendar']})
        </p>
        <p class="text-xs text-green-600 mt-2">{selected_date['note']}</p>
    </div>
    """
    main_html = main_html.replace('<main class="max-w-6xl mx-auto px-4 py-6 space-y-6">',
                                   '<main class="max-w-6xl mx-auto px-4 py-6 space-y-6">' + pillar_info_html)
    return main_html


@app.post("/select_date", response_class=HTMLResponse)
async def select_date(
    name: str = Form(""), gender: str = Form(...),
    year: int = Form(...), month: int = Form(...), day: int = Form(...),
    hour: int = Form(...), minute: int = Form(...),
    calendar: str = Form(...), selected_index: str = Form("")
):
    """用戶選擇日期後計算八字"""
    data = {
        "name": name, "gender": gender, "calendar": calendar,
        "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "birth_city": "香港"
    }
    res = compute_bazi(data)

    ba_zi_list = res['八字'].split()
    pillars = []
    for i, p in enumerate(ba_zi_list):
        pillars.append({
            "name": ["年柱", "月柱", "日柱", "時柱"][i],
            "gan": p[0],
            "zhi": p[1],
            "gan_wuxing": GAN_WU_XING[p[0]],
            "zhi_wuxing": ZHI_WU_XING[p[1]],
        })

    ji_shens = [js['五行'] for js in res['先天病源']['忌神分析']['忌神列表']]
    yong_shens = [ys['五行'] for ys in res['先天病源']['用神分析']['用神列表']]

    selected_date = {"year": year, "month": month, "day": day, "hour": hour, "minute": minute, "calendar": calendar, "note": ""}
    return render_pillar_result_html(res, data, selected_date)


@app.post("/save", response_class=Response)
async def save_bazi(request: Request):
    """保存命盤為 HTML 文件"""
    try:
        data = await request.json()
        res = data

        # 解析八字 - 生成 pillars 數組（順序：年柱、月柱、日柱、時柱）
        ba_zi_list = res['八字'].split()
        pillar_names = ["年柱", "月柱", "日柱", "時柱"]
        pillars = []
        for i in range(4):  # 年 -> 時
            p = ba_zi_list[i]
            gan = p[0]
            zhi = p[1]
            pillar_data = res['十神']['十神'][i]
            cang_gan_data = res['藏干'][pillar_names[i]]

            shi_shen = pillar_data['十神']
            zhugan_shishen = pillar_data.get('主氣十神', {})
            zhongqi_shishen = pillar_data.get('中氣十神', {})
            yuqi_shishen = pillar_data.get('餘氣十神', {})
            chang_sheng = res['十二長生']['十二長生'][i]['長生狀態']

            pillars.append({
                "name": pillar_names[i],
                "gan": gan,
                "zhi": zhi,
                "gan_wuxing": GAN_WU_XING[gan],
                "zhi_wuxing": ZHI_WU_XING[zhi],
                "shi_shen": shi_shen,
                "zhugan": cang_gan_data.get('主氣'),
                "zhugan_shishen": zhugan_shishen.get('十神', ''),
                "zhongqi": cang_gan_data.get('中氣'),
                "zhongqi_shishen": zhongqi_shishen.get('十神', ''),
                "yuqi": cang_gan_data.get('餘氣'),
                "yuqi_shishen": yuqi_shishen.get('十神', ''),
                "chang_sheng": chang_sheng,
                "wangshuai": "",
                "degeng": "",
            })

        xian_tian_bing_yuan = res.get('先天病源', {})
        ji_shens = []
        yong_shens = []

        if xian_tian_bing_yuan:
            ji_shen_analysis = xian_tian_bing_yuan.get('忌神分析', {})
            yong_shen_analysis = xian_tian_bing_yuan.get('用神分析', {})
            ji_shens = [js['五行'] for js in ji_shen_analysis.get('忌神列表', []) if '五行' in js]
            yong_shens = [ys['五行'] for ys in yong_shen_analysis.get('用神列表', []) if '五行' in ys]

        html_content = generate_bazi_result_html(res, pillars, ji_shens, yong_shens)

        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={res['姓名']}_八字命盤.html"}
        )
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Save error: {error_msg}")
        return Response(
            content=f"<html><body><h1>Error</h1><pre>{error_msg}</pre></body></html>",
            media_type="text/html",
            status_code=500
        )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
