"""
八字計算器主類 - 協調各模塊提供統一接口
© 2024-2026 Antigravity. All rights reserved.
Developed by AI Agent. Anti-theft Tag: Antigravity-BZ-8888
完全模塊化版本，不再依賴 bazi_tool.py
"""

import datetime
from typing import Any
import sxtwl

def inquire(city: str) -> float:
    """基礎經緯度查詢（本地化回退版本）"""
    city_data = {
        "北京": 116.40, "上海": 121.47, "廣州": 113.26, "深圳": 114.05,
        "香港": 114.17, "台北": 121.50, "澳門": 113.54, "成都": 104.06,
        "杭州": 120.15, "重慶": 106.50, "西安": 108.93, "武漢": 114.30,
        "湛江": 110.36
    }
    return city_data.get(city, 120.0)  # 默認使用東八區標準經度

from bazi.core.constants import (
    GAN, ZHI, LIU_SHI_JIA_ZI,
    TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG,
)
from bazi.core.utils import (
    calculate_solar_time as calc_solar_time,
    convert_to_lunar as conv_to_lunar,
)

# 導入計算模塊
from bazi.calculations.pillar import calculate_pillars, format_ba_zi
from bazi.calculations.canggan import calculate_canggan
from bazi.calculations.relations import calculate_tian_gan_wu_he, calculate_relations
from bazi.calculations.wangshuai import calculate_wangshuai
from bazi.calculations.changsheng import calculate_changsheng
from bazi.calculations.shishen import calculate_shishen
from bazi.calculations.shensha import calculate_shensha
from bazi.calculations.ganzhi import calculate_ganzhi_shengke
from bazi.calculations.jieqi import calculate_jie_qi_info
from bazi.calculations.dayun import calculate_da_yun_info, calculate_detailed_dayun, calculate_yi_hua_jie_mu
from bazi.calculations.liushijiazi import calculate_liu_shi_jia_zi

# 導入分析模塊
from bazi.analysis import (
    calculate_geju,
    calculate_gongwei,
    calculate_bingyuan,
    calculate_dayun_pan_duan,
    calculate_liunian_pan_duan,
    calculate_integrated_analysis,
    calculate_yi_zhu,
    calculate_ganzhi_xiang,
)
from bazi.analysis.bazi_gua import calculate_bazi_gua

# 導入歲運格局模塊
from bazi.analysis.dayun_liunian import calculate_dayun_yingdong, calculate_liunian_yingdong, calculate_suiyun_geju


class BaZiCalculator:
    """
    八字計算器 - 完全模塊化版本

    使用新的模塊化架構，完全獨立於舊版 bazi_tool.py
    """

    def __init__(self, name, gender, calendar, year, month, day, hour, minute, birth_city, current_city=None):
        """
        初始化八字計算器

        Args:
            name: 姓名
            gender: 性別（"男" 或 "女"）
            calendar: 曆法（"公曆" 或 "農曆"）
            year: 年份
            month: 月份
            day: 日期
            hour: 小時
            minute: 分鐘
            birth_city: 出生城市
            current_city: 現居城市（可選）
        """
        # 基本參數
        self.name = name
        self.gender = gender
        self.calendar = calendar
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.birth_city = birth_city
        self.current_city = current_city

        # 獲取出生城市經度
        self.birth_longitude = inquire(birth_city)

        # 計算真太陽時
        self.solar_time = self._calculate_solar_time()

        # 轉換為農曆
        self.lunar_date = self._convert_to_lunar()

        # 計算八字
        self.ba_zi = self._compute_ba_zi()

        # 計算地支藏干
        self.cang_gan = calculate_canggan(self.ba_zi)

        # 計算天干五合
        self.tian_gan_wu_he = calculate_tian_gan_wu_he(self.ba_zi)

        # 計算地支關係
        self.zhi_relations = calculate_relations(self.ba_zi)

        # 計算干支生剋
        self.gan_zhi_sheng_ke = calculate_ganzhi_shengke(self.ba_zi)

        # 計算旺衰
        self.wang_shuai = calculate_wangshuai(self.ba_zi)

        # 計算十二長生
        self.chang_sheng = calculate_changsheng(self.ba_zi)

        # 計算十神
        self.shi_shen = calculate_shishen(self.ba_zi, self.cang_gan)

        # 計算神煞
        self.shen_sha = calculate_shensha(self.ba_zi)

        # 計算六十甲子體象論
        self.liu_shi_jia_zi = calculate_liu_shi_jia_zi(self.ba_zi, self.gender)

        # 計算節氣信息
        self.jie_qi_info = calculate_jie_qi_info(self.lunar_date)

        # 計算大運信息
        self.da_yun_info = calculate_da_yun_info(self.ba_zi, self.gender, self.lunar_date)

        # 計算詳細十個大運
        self.detailed_dayun = calculate_detailed_dayun(self.ba_zi, self.gender, self.lunar_date)

        # ========== 使用新模塊計算分析模塊 ==========
        ba_zi_parts = self.get_ba_zi_parts()
        day_gan = self.get_day_gan()
        month_zhi = self.get_month_zhi()

        # 1. 格局判斷
        self.ge_ju = calculate_geju(
            ba_zi=self.ba_zi,
            canggan=self.cang_gan,
            day_gan=day_gan,
            month_zhi=month_zhi,
            pillars=ba_zi_parts
        )

        # 2. 宮位分析（需要格局信息）
        self.gong_wei = calculate_gongwei(
            ba_zi=self.ba_zi,
            canggan=self.cang_gan,
            shi_shen=self.shi_shen,
            ge_ju=self.ge_ju,
            integrated_analysis=None  # 初次計算時暫無整合分析
        )

        # 3. 先天病源（需要格局和宮位信息）
        self.xian_tian_bing_yuan = calculate_bingyuan(
            ba_zi=self.ba_zi,
            ge_ju=self.ge_ju,
            gong_wei=self.gong_wei,
            integrated_analysis=None
        )

        # 4. 大運判斷（需要格局信息）
        self.dayun_pan_duan = calculate_dayun_pan_duan(
            ba_zi=self.ba_zi,
            ge_ju=self.ge_ju,
            detailed_dayun=self.detailed_dayun,
            gender=self.gender
        )

        # 5. 流年判斷（需要格局和大運信息）
        self.liunian_pan_duan = calculate_liunian_pan_duan(
            ba_zi=self.ba_zi,
            ge_ju=self.ge_ju,
            dayun_pan_duan=self.dayun_pan_duan,
            detailed_dayun=self.detailed_dayun
        )

        # 6. 整合分析（以格局為核心）
        self.integrated_analysis = calculate_integrated_analysis(
            ba_zi=self.ba_zi,
            ge_ju=self.ge_ju,
            gong_wei=self.gong_wei,
            zhi_relations=self.zhi_relations,
            dayun_pan_duan=self.dayun_pan_duan,
            liunian_pan_duan=self.liunian_pan_duan
        )

        # ========== 新增功能（歲運進階、一柱論命、干支象法） ==========

        # 7. 移花接木判斷（歲運進階）
        self.yi_hua_jie_mu = calculate_yi_hua_jie_mu(self.detailed_dayun.get("十個大運", []))

        # 9. 一柱論命（以日柱為主）
        day_pillar = self.ba_zi.split()[2] if len(self.ba_zi.split()) > 2 else ""
        self.yi_zhu = calculate_yi_zhu(day_pillar, self.gender)

        # 10. 干支象法（傳入六十甲子數據以獲取六親信息）
        self.ganzhi_xiang = calculate_ganzhi_xiang(self.ba_zi, self.shi_shen, self.liu_shi_jia_zi)

        # 11. 八字卦計算
        year_zhi = self.ba_zi.split()[0][1]
        day_zhi = self.ba_zi.split()[2][1]
        self.bazi_gua = calculate_bazi_gua(year_zhi, day_zhi)

        # ========== 歲運格局（兩層架構） ==========

        # 11. 原局格局（標記）
        self.yuan_ju_ge_ju = self.ge_ju  # 別名引用，ge_ju 已包含"格局類型：原局"

        # 12. 歲運格局（大運 + 流年）- 預計算所有大運流年的組合
        self.all_suiyun_geju = self._calculate_all_suiyun_geju()

        # 13. 默認顯示第一個大運第一個人流年的歲運格局（向後兼容）
        if self.all_suiyun_geju and len(self.all_suiyun_geju) > 0:
            self.suiyun_ge_ju = self.all_suiyun_geju[0]
        else:
            self.suiyun_ge_ju = {}

    def _calculate_all_suiyun_geju(self) -> list:
        """
        預計算所有大運流年的歲運格局數據

        Returns:
            列表，每個元素包含：
            - dayun_index: 大運索引
            - liunian_index: 流年索引
            - sui_yun_ge_ju: 歲運格局結果
        """
        result = []
        dayun_list = self.detailed_dayun.get("十個大運", [])
        liunian_list = self.liunian_pan_duan.get("流年分析", [])

        # liunian_list 是 100 個流年的扁平列表，需要按大運分組（每 10 個一組）
        for dayun_idx, dayun in enumerate(dayun_list):
            # 從扁平列表中取出該大運對應的 10 個流年
            start_idx = dayun_idx * 10
            end_idx = start_idx + 10
            if start_idx < len(liunian_list):
                dayun_liunian_list = liunian_list[start_idx:end_idx]
            else:
                dayun_liunian_list = []

            # 計算大運引動
            dayun_yingdong = calculate_dayun_yingdong(
                ba_zi=self.ba_zi,
                dayun=dayun,
                yuan_ju_ge_ju=self.yuan_ju_ge_ju
            ) if dayun else {}

            for liunian_idx, liunian in enumerate(dayun_liunian_list):
                # 計算流年引動
                liunian_yingdong = calculate_liunian_yingdong(
                    ba_zi=self.ba_zi,
                    dayun=dayun,
                    liunian=liunian,
                    yuan_ju_ge_ju=self.yuan_ju_ge_ju,
                    dayun_yingdong=dayun_yingdong
                ) if liunian else {}

                # 歲運綜合判斷
                sui_yun_ge_ju = calculate_suiyun_geju(
                    yuan_ju_ge_ju=self.yuan_ju_ge_ju,
                    dayun_yingdong=dayun_yingdong,
                    liunian_yingdong=liunian_yingdong
                ) if dayun_yingdong and liunian_yingdong else {}

                result.append({
                    "dayun_index": dayun_idx,
                    "liunian_index": liunian_idx,
                    "大運": dayun.get("大運", ""),
                    "流年": liunian.get("流年", ""),
                    "sui_yun_ge_ju": sui_yun_ge_ju,
                })

        return result

    def _calculate_solar_time(self) -> datetime.datetime:
        """
        計算真太陽時

        Returns:
            真太陽時 datetime 對象
        """
        return calc_solar_time(
            self.year, self.month, self.day,
            self.hour, self.minute, self.birth_longitude
        )

    def _convert_to_lunar(self) -> Any:
        """
        將公曆日期轉換為農曆

        Returns:
            農曆日期對象
        """
        return conv_to_lunar(self.solar_time, self.calendar)

    def _compute_ba_zi(self) -> str:
        """
        計算八字

        Returns:
            八字字符串
        """
        year_pillar, month_pillar, day_pillar, hour_pillar = calculate_pillars(
            self.lunar_date, self.solar_time
        )
        return format_ba_zi(year_pillar, month_pillar, day_pillar, hour_pillar)

    def format_output(self) -> str:
        """
        格式化輸出

        Returns:
            格式化的八字命盤字符串
        """
        output = []
        output.append(f"姓名：{self.name}")
        output.append(f"性別：{self.gender}")
        output.append(f"出生城市：{self.birth_city}")
        output.append(f"真太陽時：{self.solar_time}")
        output.append(f"八字：{self.ba_zi}")
        output.append(f"格局：{self.ge_ju.get('格局', '無格局')}")
        return "\n".join(output)

    def get_ba_zi_parts(self) -> list:
        """
        獲取四柱列表

        Returns:
            四柱列表 [["年干", "年支"], ["月干", "月支"], ["日干", "日支"], ["時干", "時支"]]
        """
        return [list(pillar) for pillar in self.ba_zi.split()]

    def get_day_gan(self) -> str:
        """
        獲取日天干

        Returns:
            日天干
        """
        return self.ba_zi.split()[2][0]

    def get_month_zhi(self) -> str:
        """
        獲取月支

        Returns:
            月支
        """
        return self.ba_zi.split()[1][1]

    @staticmethod
    def calculate_date_from_pillars(
        year_gan, year_zhi, month_gan, month_zhi,
        day_gan, day_zhi, hour_gan, hour_zhi
    ) -> list:
        """
        從四柱反推出生年月日時（1900-2100 年範圍）

        算法思路：
        1. 年柱 → 確定年份範圍（1900-2100 內匹配的年柱）
        2. 月柱 → 根據年干和月支，使用「五虎遁」確定月干，再找匹配節氣
        3. 日柱 → 遍歷該年該月找到匹配的日柱
        4. 時柱 → 根據日干和時支，使用「五鼠遁」驗證時干

        Args:
            year_gan, year_zhi: 年柱天干地支
            month_gan, month_zhi: 月柱天干地支
            day_gan, day_zhi: 日柱天干地支
            hour_gan, hour_zhi: 時柱天干地支

        Returns:
            可能的日期列表
        """
        results = []

        # 五虎遁口訣：甲己之年丙作首，乙庚之歲戊為頭，丙辛之年尋庚上，丁壬壬寅順水流，戊癸之年甲寅頭
        wu_hu_dun_start = {
            "甲": "丙", "己": "丙",
            "乙": "戊", "庚": "戊",
            "丙": "庚", "辛": "庚",
            "丁": "壬", "壬": "壬",
            "戊": "甲", "癸": "甲",
        }

        # 五鼠遁口訣：甲己還加甲，乙庚丙作初，丙辛從戊起，丁壬庚子居，戊癸何方發，壬子是真途
        wu_shu_dun_start = {
            "甲": "甲", "己": "甲",
            "乙": "丙", "庚": "丙",
            "丙": "戊", "辛": "戊",
            "丁": "庚", "壬": "庚",
            "戊": "壬", "癸": "壬",
        }

        # 月支與月份對應（以節氣為準）
        month_zhi_to_index = {
            "寅": 1, "卯": 2, "辰": 3, "巳": 4, "午": 5, "未": 6,
            "申": 7, "酉": 8, "戌": 9, "亥": 10, "子": 11, "丑": 12
        }

        # 時支與小時對應
        hour_zhi_to_hour = {
            "子": (23, 1), "丑": (1, 3), "寅": (3, 5), "卯": (5, 7),
            "辰": (7, 9), "巳": (9, 11), "午": (11, 13), "未": (13, 15),
            "申": (15, 17), "酉": (17, 19), "戌": (19, 21), "亥": (21, 23)
        }

        # 遍歷 1900-2100 年
        for year in range(1900, 2101):
            # 檢查年柱是否匹配
            try:
                lunar = sxtwl.fromSolar(year, 1, 1)
                year_gan_check = GAN[lunar.getYearGan()]
                year_zhi_check = ZHI[lunar.getYearZhi()]

                if year_gan_check != year_gan or year_zhi_check != year_zhi:
                    continue
            except Exception:
                continue

            # 遍歷每個月
            for month in range(1, 13):
                try:
                    # 檢查月柱
                    lunar = sxtwl.fromSolar(year, month, 15)
                    month_gan_check = GAN[lunar.getMonthGan()]
                    month_zhi_check = ZHI[lunar.getMonthZhi()]

                    if month_gan_check != month_gan or month_zhi_check != month_zhi:
                        continue

                    # 遍歷每一天
                    for day in range(1, 32):
                        try:
                            lunar = sxtwl.fromSolar(year, month, day)
                            day_gan_check = GAN[lunar.getDayGan()]
                            day_zhi_check = ZHI[lunar.getDayZhi()]

                            if day_gan_check != day_gan or day_zhi_check != day_zhi:
                                continue

                            # 檢查時柱
                            for hour_idx, (hour_zhi, (start_h, end_h)) in enumerate(hour_zhi_to_hour.items()):
                                # 計算時干
                                day_gan_idx = GAN.index(day_gan)
                                start_gan = wu_shu_dun_start.get(day_gan, "甲")
                                start_gan_idx = GAN.index(start_gan)
                                hour_gan_idx = (start_gan_idx + hour_idx) % 10
                                hour_gan_check = GAN[hour_gan_idx]

                                if hour_gan_check == hour_gan and hour_zhi == hour_zhi:
                                    results.append({
                                        "year": year,
                                        "month": month,
                                        "day": day,
                                        "hour": start_h,
                                        "minute": 0
                                    })
                        except Exception:
                            continue
                except Exception:
                    continue

        return results