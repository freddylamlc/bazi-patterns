"""
八字排盤系統 - API 路由模塊
包含所有 API 端點
"""

import json
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from bazi import BaZiCalculator
from bazi.core.constants import TIAN_GAN_YIN_YANG, TIAN_GAN_WU_XING as GAN_WU_XING, ZHI_WU_XING
from bazi.calculations.shishen import get_shi_shen
from bazi.db import save_client, get_client, update_annotation, search_clients, delete_client

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 提供給 Jinja 的全局常量
templates.env.globals['GAN_WU_XING'] = GAN_WU_XING
templates.env.globals['ZHI_WU_XING'] = ZHI_WU_XING


def get_canggan_shishen(gan: str, day_gan: str) -> str:
    """計算藏干的十神"""
    return get_shi_shen(gan, day_gan)


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
        longitude=data.get('longitude')
    )

    gender_text = "男 (乾造)" if calculator.gender == "男" else "女 (坤造)"

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
        "格局": calculator.ge_ju,
        "整合分析": calculator.integrated_analysis,
        "宮位": calculator.gong_wei,
        "先天病源": calculator.xian_tian_bing_yuan,
        "大運判斷": calculator.dayun_pan_duan,
        "流年判斷": calculator.liunian_pan_duan,
        "原局格局": calculator.yuan_ju_ge_ju,
        "歲運格局": calculator.suiyun_ge_ju.get('sui_yun_ge_ju', {}) if isinstance(calculator.suiyun_ge_ju, dict) else {},
        "歲運格局全部": calculator.all_suiyun_geju,
        "一柱論命": calculator.yi_zhu,
        "干支象法": calculator.ganzhi_xiang,
        "移花接木": calculator.yi_hua_jie_mu,
        "bazi_gua": calculator.bazi_gua,
    }


def build_pillar_view_models(res: dict) -> list:
    """提取四柱視圖模型邏輯，消除重複代碼"""
    ba_zi_list = res['八字'].split()
    pillar_names = ["年柱", "月柱", "日柱", "時柱"]
    pillars = []
    
    # 十神與藏干如果是在舊結構與新結構之間做了切換，統一處理
    shi_shen_dict = res.get('十神', {})
    if '十神' in shi_shen_dict and isinstance(shi_shen_dict['十神'], list):
        # 兼容 save 接口中可能有的舊結構
        shi_shen_list_mode = True
    else:
        shi_shen_list_mode = False

    for i in range(4):
        p = ba_zi_list[i]
        gan = p[0]
        zhi = p[1]
        pillar_name = pillar_names[i]

        if shi_shen_list_mode:
            pillar_data = shi_shen_dict['十神'][i]
            shi_shen = '' if i == 2 else pillar_data.get('十神', '')
            cang_gan_data = res.get('藏干', {}).get(pillar_name, {})
            zhugan_shishen = pillar_data.get('主氣十神', {})
            zhongqi_shishen = pillar_data.get('中氣十神', {})
            yuqi_shishen = pillar_data.get('餘氣十神', {})
            
            cs_data = res.get('十二長生', {})
            if '十二長生' in cs_data and isinstance(cs_data['十二長生'], list):
                chang_sheng = cs_data['十二長生'][i].get('長生狀態', '')
            else:
                chang_sheng = cs_data.get(pillar_name, {}).get('十二長生', cs_data.get(pillar_name, {}).get('長生狀態', ''))
        else:
            pillar_shishen = shi_shen_dict.get(pillar_name, {})
            shi_shen = '' if i == 2 else pillar_shishen.get('天干十神', '')
            cang_gan_data = res.get('藏干', {}).get(pillar_name, {})
            
            canggan_shishen = pillar_shishen.get('藏干十神', {})
            zhugan_shishen = canggan_shishen.get('主氣', {}) or {}
            zhongqi_shishen = canggan_shishen.get('中氣', {}) or {}
            yuqi_shishen = canggan_shishen.get('餘氣', {}) or {}
            
            chang_sheng_data = res.get('十二長生', {}).get(pillar_name, {})
            chang_sheng = chang_sheng_data.get('十二長生', chang_sheng_data.get('長生狀態', ''))

        canggan_dict = {}
        if cang_gan_data.get('主氣'):
            gan_val = cang_gan_data.get('主氣')
            canggan_dict['主氣'] = {'干': gan_val, '五行': GAN_WU_XING.get(gan_val, ''), '十神': zhugan_shishen.get('十神', '')}
        if cang_gan_data.get('中氣'):
            gan_val = cang_gan_data.get('中氣')
            canggan_dict['中氣'] = {'干': gan_val, '五行': GAN_WU_XING.get(gan_val, ''), '十神': zhongqi_shishen.get('十神', '')}
        if cang_gan_data.get('餘氣'):
            gan_val = cang_gan_data.get('餘氣')
            canggan_dict['餘氣'] = {'干': gan_val, '五行': GAN_WU_XING.get(gan_val, ''), '十神': yuqi_shishen.get('十神', '')}

        pillars.append({
            "name": pillar_name,
            "gan": gan,
            "zhi": zhi,
            "gan_wuxing": GAN_WU_XING.get(gan, ''),
            "zhi_wuxing": ZHI_WU_XING.get(zhi, ''),
            "shi_shen": shi_shen,
            "canggan_dict": canggan_dict,
            "chang_sheng": chang_sheng,
        })
    return pillars


def prepare_bazi_context(request: Request, res: dict) -> dict:
    """準備傳遞給模板的通用上下文"""
    pillars = build_pillar_view_models(res)
    
    # 先天病源
    xian_tian_bing_yuan = res.get('先天病源', {})
    ji_shen_analysis = xian_tian_bing_yuan.get('忌神分析', {})
    yong_shen_analysis = xian_tian_bing_yuan.get('用神分析', {})
    ji_shens = [js['五行'] for js in ji_shen_analysis.get('忌神列表', []) if '五行' in js]
    yong_shens = [ys['五行'] for ys in yong_shen_analysis.get('用神列表', []) if '五行' in ys]
    
    # 提取需要的數據
    ba_zi_parts = res['八字'].split()
    day_gan = ba_zi_parts[2][0] if len(ba_zi_parts) > 2 else '甲'

    da_yun_fen_xi = res.get('詳細大運', {}).get('十個大運', [])
    
    da_yun_fen_xi = res.get('詳細大運', {}).get('十個大運', [])
    first_dayun = da_yun_fen_xi[0] if da_yun_fen_xi else {}
    all_liunian_data = res.get('流年判斷', {}).get('流年分析', [])

    # 將 100 個流年按大運分組
    liunian_by_dayun = {}
    for i, ln in enumerate(all_liunian_data):
        dayun_idx = i // 10
        if dayun_idx not in liunian_by_dayun:
            liunian_by_dayun[dayun_idx] = []
            
        tian_gan_data = ln.get('天干', {})
        zhi_data = ln.get('地支', {})
        tian_gan = tian_gan_data.get('干', ln.get('流年天干', ''))
        zhi = zhi_data.get('支', ln.get('流年地支', ''))
        
        canggan = ln.get('藏干', {})
        if not canggan and zhi:
            # 根據地支獲取藏干
            from bazi.core.constants import ZHI_CANG_GAN
            zhi_canggan = ZHI_CANG_GAN.get(zhi, {})
            canggan = {}
            for qi_type in ['主氣', '中氣', '餘氣']:
                gan = zhi_canggan.get(qi_type)
                if gan:
                    # 使用 shared logic 獲取十神
                    from bazi.calculations.shishen import get_shi_shen
                    canggan[qi_type] = {
                        '干': gan,
                        '十神': get_shi_shen(gan, day_gan),
                        '五行': GAN_WU_XING.get(gan, '')
                    }

        liunian_by_dayun[dayun_idx].append({
            '流年天干': tian_gan,
            '流年地支': zhi,
            '流年十神': tian_gan_data.get('十神', ln.get('流年十神', '')),
            '藏干': canggan,
            '十二長生': zhi_data.get('十二長生', ln.get('十二長生', '')),
            '格局影響': ln.get('格局影響', '平穩'),
            '大運序號': ln.get('大運序號', 1),
            '流年序號': ln.get('流年序號', 1),
            '虛歲': ln.get('虛歲', 0)
        })

    first_liunian = liunian_by_dayun[0][0] if liunian_by_dayun and liunian_by_dayun.get(0) else {}

    # 流月數據（簡化處理）
    # 流月數據計算
    liuyue_by_liunian = {}
    YUE_LING_ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
    YUE_LING_NAMES = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    def get_yue_gan(nian_gan, yue_idx):
        if nian_gan in ["甲", "己"]: start = 2
        elif nian_gan in ["乙", "庚"]: start = 4
        elif nian_gan in ["丙", "辛"]: start = 6
        elif nian_gan in ["丁", "壬"]: start = 8
        else: start = 0
        return TIAN_GAN[(start + yue_idx) % 10]

    for dayun_idx, liunian_list in liunian_by_dayun.items():
        liuyue_by_liunian[dayun_idx] = []
        for liunian_idx, liunian in enumerate(liunian_list):
            nian_gan = liunian.get('天干', {}).get('干', '')
            if not nian_gan:
                # 兼容不同結構
                nian_gan = liunian.get('流年天干', '')
            
            yue_list = []
            for yue_idx, yue_zhi in enumerate(YUE_LING_ZHI):
                yue_gan = get_yue_gan(nian_gan, yue_idx)
                from bazi.calculations.shishen import get_shi_shen
                yue_shishen = get_shi_shen(yue_gan, day_gan)
                yue_name = f"{yue_gan}{yue_zhi}"

                canggan = {}
                from bazi.core.constants import ZHI_CANG_GAN
                zhi_canggan = ZHI_CANG_GAN.get(yue_zhi, {})
                for qi_type in ['主氣', '中氣', '餘氣']:
                    gan = zhi_canggan.get(qi_type)
                    if gan:
                        canggan[qi_type] = {
                            '干': gan,
                            '十神': get_shi_shen(gan, day_gan),
                            '五行': GAN_WU_XING.get(gan, '')
                        }
                
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

    first_liuyue = {}
    if liuyue_by_liunian.get(0) and liuyue_by_liunian[0]:
        first_liuyue = liuyue_by_liunian[0][0][0]

    ge_ju_forms = res.get('格局', {}).get('格局形式', [])
    ge_ju_forms_str = ', '.join([f['形式'] for f in ge_ju_forms]) if ge_ju_forms and ge_ju_forms[0].get('形式') != '普通格' else ''
    
    ge_cheng_bai = res.get('格局', {}).get('成敗', '')
    if '成' in ge_cheng_bai and '不成' not in ge_cheng_bai:
        ge_cheng_bai_class = 'bg-green-50 border-green-200'
        ge_cheng_bai_text_class = 'text-green-600'
    elif '不成' in ge_cheng_bai or '破格' in ge_cheng_bai:
        ge_cheng_bai_class = 'bg-red-50 border-red-200'
        ge_cheng_bai_text_class = 'text-red-600'
    else:
        ge_cheng_bai_class = 'bg-amber-50 border-amber-200'
        ge_cheng_bai_text_class = 'text-amber-600'

    yong_shen_xing_zhi = res.get('格局', {}).get('用神性質', '中性')
    yong_shen_xing_zhi_class = 'text-green-600' if yong_shen_xing_zhi == '吉神' else 'text-red-600' if yong_shen_xing_zhi == '凶神' else 'text-stone-600'

    integrated = res.get('整合分析', {})
    ge_ju_core = integrated.get('格局核心', {})
    ge_ju_jie_du = integrated.get('格局解讀', {})
    
    gong_wei = res.get('宮位', {})
    liu_qin_gong_wei = gong_wei.get('六親宮位', {})
    
    shen_sha = res.get('神煞', {})
    shi_yong_shen_sha = shen_sha.get('實用神煞', [])
    can_kao_shen_sha = shen_sha.get('參考神煞', [])

    return {
        "request": request,
        "name": res.get('姓名', ''),
        "gender": res.get('性別', ''),
        "solar_time": res.get('出生時間', {}).get('公曆', ''),
        "solar_date": res.get('出生時間', {}).get('公曆', ''),
        "lunar_date": res.get('出生時間', {}).get('農曆', ''),
        "birth_city": res.get('出生城市', ''),
        "jie_qi": res.get('節氣', ''),
        "da_yun": res.get('大運', ''),
        "dayun_gender": res.get('詳細大運', {}).get('性別', ''),
        "dayun_paifa": res.get('詳細大運', {}).get('排法', ''),
        
        # 組件數據
        "pillars": pillars,
        "dayun_data": da_yun_fen_xi,
        "first_dayun": first_dayun,
        "first_liunian": first_liunian,
        "first_liuyue": first_liuyue,
        
        "zhi_relations": res.get('地支關係', {}),
        "shishen_data": res.get('格局', {}).get('十神性格', {}),
        "ge_ju_name": res.get('格局', {}).get('格局', ''),
        "ge_ju_forms": ge_ju_forms_str,
        "ge_ju_forms_detail": ge_ju_forms if ge_ju_forms and ge_ju_forms[0].get('形式') != '普通格' else [],
        "yong_shen": res.get('格局', {}).get('用神', ''),
        "yong_shen_xing_zhi": yong_shen_xing_zhi,
        "yong_shen_xing_zhi_class": yong_shen_xing_zhi_class,
        "yong_shen_fang_shi": res.get('格局', {}).get('用神方式', ''),
        "xiang_shen": ', '.join(res.get('格局', {}).get('相神', ['待定'])),
        "ding_ge_lai_yuan": res.get('格局', {}).get('定格來源', ''),
        "xiang_shen_chong_tu": res.get('格局', {}).get('相神衝突', ''),
        "ge_cheng_bai": ge_cheng_bai,
        "ge_cheng_bai_class": ge_cheng_bai_class,
        "ge_cheng_bai_text_class": ge_cheng_bai_text_class,
        "ge_cheng_bai_analysis": res.get('格局', {}).get('成敗分析', []),
        
        "xi_shen_wu_xing": ', '.join(res.get('格局', {}).get('喜神五行', [])) or '無',
        "ji_shen_wu_xing": ', '.join(res.get('格局', {}).get('忌神五行', [])) or '無',
        
        "yong_shen_jie_du": ge_ju_jie_du.get('用神解讀', ''),
        "ji_shen_jie_du": ge_ju_jie_du.get('忌神解讀', ''),
        "yong_shen_core": ge_ju_core.get('用神', ''),
        "xiang_shen_core": ', '.join(ge_ju_core.get('相神', [])) or '待定',
        "xi_shen_core": ', '.join(ge_ju_core.get('喜神十神', [])) or '無',
        "xi_shen_core_wu_xing": ', '.join(ge_ju_core.get('喜神五行', [])) or '無',
        "ji_shen_core": ', '.join(ge_ju_core.get('忌神十神', [])) or '無',
        "ji_shen_core_wu_xing": ', '.join(ge_ju_core.get('忌神五行', [])) or '無',
        
        "di_zhi_de_gen": res.get('旺衰', {}).get('地支得根', []),
        "wang_shuai": res.get('旺衰', {}),
        "bazi_parts_gan": [p[0] for p in ba_zi_parts],
        "ri_zhu_gen_qi_zong": res.get('旺衰', {}).get('日主旺衰', {}).get('根氣強度', 0),
        "gen_qi_lun_duan": res.get('旺衰', {}).get('根氣論斷', '虛浮無根'),
        
        "yue_ling": xian_tian_bing_yuan.get('月令', {}).get('月支', ''),
        "dang_ling_wu_xing": xian_tian_bing_yuan.get('月令', {}).get('當令五行', ''),
        "wu_xing_fen_bu": xian_tian_bing_yuan.get('五行分布', {}),
        "wu_xing_guo_wang": xian_tian_bing_yuan.get('五行過旺', {}).get('列表', []),
        "wu_xing_que_shi": xian_tian_bing_yuan.get('五行缺失', {}).get('列表', []),
        "gai_tou_jie_jiao": xian_tian_bing_yuan.get('蓋頭截腳', {}).get('列表', []),
        
        "ri_zhu": res.get('六十甲子', {}).get('日柱', ''),
        "suo_shu_xun": res.get('六十甲子', {}).get('所屬旬', ''),
        "xun_cheng_yuan": ' '.join(res.get('六十甲子', {}).get('旬成員', [])),
        "liu_qin_lei_hua": res.get('六十甲子', {}).get('六親類化', []),
        
        "has_shen_sha": bool(shi_yong_shen_sha or can_kao_shen_sha),
        "shi_yong_shen_sha_count": len(shi_yong_shen_sha),
        "shi_yong_shen_sha": shi_yong_shen_sha,
        "can_kao_shen_sha": bool(can_kao_shen_sha),
        "can_kao_shen_sha_count": len(can_kao_shen_sha),
        "can_kao_shen_sha_list": can_kao_shen_sha,
        
        "nian_gan_liu_qin": liu_qin_gong_wei.get('年柱', {}).get('祖輩宮', {}).get('年干', ''),
        "nian_zhi_liu_qin": liu_qin_gong_wei.get('年柱', {}).get('祖輩宮', {}).get('年支', ''),
        "yue_gan_liu_qin": liu_qin_gong_wei.get('月柱', {}).get('父母兄弟宮', {}).get('月干', ''),
        "yue_zhi_liu_qin": liu_qin_gong_wei.get('月柱', {}).get('父母兄弟宮', {}).get('月支', ''),
        "ri_gan_liu_qin": liu_qin_gong_wei.get('日柱', {}).get('夫妻宮', {}).get('日干', ''),
        "ri_zhi_liu_qin": liu_qin_gong_wei.get('日柱', {}).get('夫妻宮', {}).get('日支', ''),
        "shi_gan_liu_qin": liu_qin_gong_wei.get('時柱', {}).get('晚輩宮', {}).get('時干', ''),
        "shi_zhi_liu_qin": liu_qin_gong_wei.get('時柱', {}).get('晚輩宮', {}).get('時支', ''),
        "nian_zhu_shen_ti": gong_wei.get('身體宮位', {}).get('年柱', {}).get('宮位', ''),
        "nian_zhu_shi_xu": gong_wei.get('身體宮位', {}).get('年柱', {}).get('時序', ''),
        "yue_zhu_shen_ti": gong_wei.get('身體宮位', {}).get('月柱', {}).get('宮位', ''),
        "yue_zhu_shi_xu": gong_wei.get('身體宮位', {}).get('月柱', {}).get('時序', ''),
        "ri_zhu_shen_ti": gong_wei.get('身體宮位', {}).get('日柱', {}).get('宮位', ''),
        "ri_zhu_shi_xu": gong_wei.get('身體宮位', {}).get('日柱', {}).get('時序', ''),
        "shi_zhu_shen_ti": gong_wei.get('身體宮位', {}).get('時柱', {}).get('宮位', ''),
        "shi_zhu_shi_xu": gong_wei.get('身體宮位', {}).get('時柱', {}).get('時序', ''),
        
        "gong_wei_ji_xiong": gong_wei.get('宮位吉凶', []),
        "ji_bing_lun_duan": gong_wei.get('疾病論斷', {}).get('疾病論斷', []),
        "ji_jie_ti_zhi": gong_wei.get('疾病論斷', {}).get('季節體質', '未知'),
        "ji_bing_lun_duan_count": len(gong_wei.get('疾病論斷', {}).get('疾病論斷', [])),
        "tian_gan_zang_fu": gong_wei.get('天干對應臟腑', {}),
        "zhi_zang_fu": gong_wei.get('地支對應臟腑', {}),
        
        "da_yun_pan_duan": res.get('大運判斷', {}).get('十個大運分析', []),
        "liu_nian_pan_duan": res.get('流年判斷', {}).get('流年分析', [])[:10],
        
        "yuan_ju_ge_ju": res.get('原局格局', {}),
        "sui_yun_ge_ju": res.get('歲運格局', {}),
        "yi_zhu": res.get('一柱論命', {}),
        "bazi_gua": res.get('bazi_gua', {}),
        "shishen_combinations": integrated.get('十神組合斷語', []),
        "health_suggestions": integrated.get('健康分析', {}).get('生活調理', {}),
        "ganzhi_xiang": res.get('干支象法', {}),
        "yi_hua_jie_mu": res.get('移花接木', {}),
        
        "all_liunian_data_json": json.dumps(all_liunian_data, ensure_ascii=False),
        "liunian_by_dayun_json": json.dumps(liunian_by_dayun, ensure_ascii=False),
        "liuyue_by_liunian_json": json.dumps(liuyue_by_liunian, ensure_ascii=False),
        "four_pillars_json": json.dumps(ba_zi_parts, ensure_ascii=False),
        "dayun_data_json": json.dumps(da_yun_fen_xi, ensure_ascii=False),
        "sui_yun_ge_ju_all_json": json.dumps(res.get('歲運格局全部', []), ensure_ascii=False),
        "has_zhi_relations": any(res.get('地支關係', {}).values()),
    }


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/calculate", response_class=HTMLResponse)
async def calculate(
    request: Request,
    name: str = Form(""), gender: str = Form(...), calendar: str = Form(...),
    year: int = Form(...), month: int = Form(...), day: int = Form(...),
    hour: int = Form(...), minute: int = Form(...), birth_city: str = Form(""), longitude: str = Form(None)
):
    """計算八字（日期輸入模式）"""
    calendar_map = {"公曆": "公曆", "農曆": "農曆"}
    calendar_std = calendar_map.get(calendar, calendar)

    data = {
        "name": name, "gender": gender, "calendar": calendar_std,
        "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "birth_city": birth_city,
        "longitude": longitude
    }
    res = compute_bazi(data)
    context = prepare_bazi_context(request, res)
    # 傳遞原始輸入表單資料，以便保存
    context["bazi_form_data"] = json.dumps(data, ensure_ascii=False)
    return templates.TemplateResponse("result.html", context)


@router.post("/calculate_from_pillars", response_class=HTMLResponse)
async def calculate_from_pillars(
    request: Request,
    name: str = Form(""),
    gender: str = Form(...),
    year_gan: str = Form(...), year_zhi: str = Form(...),
    month_gan: str = Form(...), month_zhi: str = Form(...),
    day_gan: str = Form(...), day_zhi: str = Form(...),
    hour_gan: str = Form(...), hour_zhi: str = Form(...)
):
    """從四柱反推出生年月日時並計算八字"""
    possible_dates = BaZiCalculator.calculate_date_from_pillars(
        year_gan, year_zhi, month_gan, month_zhi,
        day_gan, day_zhi, hour_gan, hour_zhi
    )

    if not possible_dates:
        error_msg = f"無法在 1900-2100 年範圍內找到匹配的四柱：{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}"
        return templates.TemplateResponse("error.html", {"request": request, "error_message": error_msg})

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
        context = prepare_bazi_context(request, res)
        context["selected_date"] = possible_dates[0]
        context["is_pillar_calc"] = True
        return templates.TemplateResponse("result.html", context)

    return templates.TemplateResponse("select_date.html", {
        "request": request,
        "possible_dates": possible_dates,
        "name": name,
        "gender": gender
    })


@router.post("/select_date", response_class=HTMLResponse)
async def select_date(
    request: Request,
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
    context = prepare_bazi_context(request, res)
    context["selected_date"] = {"year": year, "month": month, "day": day, "hour": hour, "minute": minute, "calendar": calendar, "note": ""}
    context["is_pillar_calc"] = True
    return templates.TemplateResponse("result.html", context)


@router.post("/save", response_class=Response)
async def save_bazi(request: Request):
    """保存命盤為 HTML 文件"""
    try:
        data = await request.json()
        res = data
        context = prepare_bazi_context(request, res)
        html_content = templates.get_template("result.html").render(**context)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={res.get('姓名', 'unknown')}_八字命盤.html"}
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

# ========== 客戶管理系統 (CRM) 端點 ==========

@router.get("/clients", response_class=HTMLResponse)
async def list_clients(request: Request, q: str = ""):
    """客戶管理列表頁面"""
    records = search_clients(q)
    return templates.TemplateResponse("clients.html", {"request": request, "records": records, "query": q})

@router.post("/api/clients")
async def create_client(request: Request):
    """保存為新客戶命盤"""
    data = await request.json()
    client_id = save_client(data)
    return {"client_id": client_id}

@router.get("/client/{client_id}", response_class=HTMLResponse)
async def view_client(request: Request, client_id: str):
    """查看已保存客戶的命盤（動態重算）"""
    client = get_client(client_id)
    if not client:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": "找不到該客戶紀錄"})
    
    data = {
        "name": client['name'],
        "gender": client['gender'],
        "calendar": client['calendar'],
        "year": client['year'],
        "month": client['month'],
        "day": client['day'],
        "hour": client['hour'],
        "minute": client['minute'],
        "birth_city": client['birth_city'],
        "longitude": client.get('longitude')
    }
    
    try:
        res = compute_bazi(data)
        context = prepare_bazi_context(request, res)
        context['client_id'] = client_id
        context['client_name'] = client['name']
        context['annotations'] = json.loads(client['annotations'] or "{}")
        context['bazi_form_data'] = json.dumps(data, ensure_ascii=False)
        return templates.TemplateResponse("result.html", context)
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error_message": f"排盤發生錯誤：{str(e)}"})

@router.post("/api/clients/{client_id}/annotations")
async def update_client_annotation(client_id: str, request: Request):
    """更新客戶的區塊批注"""
    data = await request.json()
    section_id = data.get("section_id")
    text = data.get("text")
    success = update_annotation(client_id, section_id, text)
    return {"success": success}

@router.delete("/api/clients/{client_id}")
async def delete_client_record(client_id: str):
    """刪除客戶紀錄"""
    success = delete_client(client_id)
    return {"success": success}
