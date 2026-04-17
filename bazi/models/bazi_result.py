"""
八字結果數據類 - 用於封裝八字計算結果
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BaZiResult:
    """八字計算結果數據類"""

    # 基本信息
    name: str = ""
    """姓名"""

    gender: str = ""
    """性別"""

    solar_time: str = ""
    """公曆時間"""

    lunar_time: str = ""
    """農曆時間"""

    birth_city: str = ""
    """出生城市"""

    birth_longitude: float = 0.0
    """出生城市經度"""

    # 八字核心
    ba_zi: str = ""
    """四柱八字"""

    cang_gan: dict = field(default_factory=dict)
    """地支藏干"""

    tian_gan_wu_he: list = field(default_factory=list)
    """天干五合"""

    zhi_relations: dict = field(default_factory=dict)
    """地支關係"""

    gan_zhi_sheng_ke: dict = field(default_factory=dict)
    """干支生剋"""

    wang_shuai: dict = field(default_factory=dict)
    """旺衰"""

    chang_sheng: dict = field(default_factory=dict)
    """十二長生"""

    shi_shen: dict = field(default_factory=dict)
    """十神"""

    shen_sha: dict = field(default_factory=dict)
    """神煞"""

    liu_shi_jia_zi: dict = field(default_factory=dict)
    """六十甲子"""

    jie_qi_info: dict = field(default_factory=dict)
    """節氣信息"""

    da_yun_info: dict = field(default_factory=dict)
    """大運信息"""

    detailed_dayun: list = field(default_factory=list)
    """詳細大運"""

    # 格局分析
    ge_ju: dict = field(default_factory=dict)
    """格局判斷"""

    integrated_analysis: dict = field(default_factory=dict)
    """整合分析"""

    # 宮位與病源
    gong_wei: dict = field(default_factory=dict)
    """宮位分析"""

    xian_tian_bing_yuan: dict = field(default_factory=dict)
    """先天病源"""

    # 運勢分析
    dayun_pan_duan: dict = field(default_factory=dict)
    """大運判斷"""

    liunian_pan_duan: dict = field(default_factory=dict)
    """流年判斷"""

    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "姓名": self.name,
            "性別": self.gender,
            "公曆時間": self.solar_time,
            "農曆時間": self.lunar_time,
            "出生城市": self.birth_city,
            "出生經度": self.birth_longitude,
            "八字": self.ba_zi,
            "藏干": self.cang_gan,
            "天干五合": self.tian_gan_wu_he,
            "地支關係": self.zhi_relations,
            "干支生剋": self.gan_zhi_sheng_ke,
            "旺衰": self.wang_shuai,
            "十二長生": self.chang_sheng,
            "十神": self.shi_shen,
            "神煞": self.shen_sha,
            "六十甲子": self.liu_shi_jia_zi,
            "節氣": self.jie_qi_info,
            "大運": self.da_yun_info,
            "詳細大運": self.detailed_dayun,
            "格局": self.ge_ju,
            "整合分析": self.integrated_analysis,
            "宮位": self.gong_wei,
            "先天病源": self.xian_tian_bing_yuan,
            "大運判斷": self.dayun_pan_duan,
            "流年判斷": self.liunian_pan_duan,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BaZiResult":
        """從字典創建"""
        return cls(
            name=data.get("姓名", ""),
            gender=data.get("性別", ""),
            solar_time=data.get("公曆時間", ""),
            lunar_time=data.get("農曆時間", ""),
            birth_city=data.get("出生城市", ""),
            birth_longitude=data.get("出生經度", 0.0),
            ba_zi=data.get("八字", ""),
            cang_gan=data.get("藏干", {}),
            tian_gan_wu_he=data.get("天干五合", []),
            zhi_relations=data.get("地支關係", {}),
            gan_zhi_sheng_ke=data.get("干支生剋", {}),
            wang_shuai=data.get("旺衰", {}),
            chang_sheng=data.get("十二長生", {}),
            shi_shen=data.get("十神", {}),
            shen_sha=data.get("神煞", {}),
            liu_shi_jia_zi=data.get("六十甲子", {}),
            jie_qi_info=data.get("節氣", {}),
            da_yun_info=data.get("大運", {}),
            detailed_dayun=data.get("詳細大運", []),
            ge_ju=data.get("格局", {}),
            integrated_analysis=data.get("整合分析", {}),
            gong_wei=data.get("宮位", {}),
            xian_tian_bing_yuan=data.get("先天病源", {}),
            dayun_pan_duan=data.get("大運判斷", {}),
            liunian_pan_duan=data.get("流年判斷", {}),
        )
