"""
核心模塊測試 - 測試天干地支、五行等常數
"""

import pytest
from bazi.core.constants import (
    Gan,
    Zhi,
    TIAN_GAN_WU_XING,
    ZHI_WU_XING,
    TIAN_GAN_YIN_YANG,
    WU_XING_SHENG,
    WU_XING_KE,
    ZHI_LIU_HE,
    ZHI_LIU_CHONG,
    ZHI_SAN_HE_JU,
    TIAN_GAN_WU_HE,
)


class TestGan:
    """測試天干常數"""

    def test_gan_count(self):
        """測試天干數量"""
        assert len(Gan) == 10

    def test_gan_order(self):
        """測試天干順序"""
        expected = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        assert list(Gan) == expected

    def test_gan_contains(self):
        """測試天干包含"""
        assert "甲" in Gan
        assert "癸" in Gan
        assert "X" not in Gan


class TestZhi:
    """測試地支常數"""

    def test_zhi_count(self):
        """測試地支數量"""
        assert len(Zhi) == 12

    def test_zhi_order(self):
        """測試地支順序"""
        expected = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        assert list(Zhi) == expected

    def test_zhi_contains(self):
        """測試地支包含"""
        assert "子" in Zhi
        assert "亥" in Zhi
        assert "X" not in Zhi


class TestGanWuXing:
    """測試天干五行"""

    def test_gan_wu_xing_mapping(self):
        """測試天干五行映射"""
        assert TIAN_GAN_WU_XING["甲"] == "木"
        assert TIAN_GAN_WU_XING["乙"] == "木"
        assert TIAN_GAN_WU_XING["丙"] == "火"
        assert TIAN_GAN_WU_XING["丁"] == "火"
        assert TIAN_GAN_WU_XING["戊"] == "土"
        assert TIAN_GAN_WU_XING["己"] == "土"
        assert TIAN_GAN_WU_XING["庚"] == "金"
        assert TIAN_GAN_WU_XING["辛"] == "金"
        assert TIAN_GAN_WU_XING["壬"] == "水"
        assert TIAN_GAN_WU_XING["癸"] == "水"

    def test_gan_wu_xing_completeness(self):
        """測試天干五行完整性"""
        for gan in Gan:
            assert gan in TIAN_GAN_WU_XING


class TestZhiWuXing:
    """測試地支五行"""

    def test_zhi_wu_xing_mapping(self):
        """測試地支五行映射"""
        assert ZHI_WU_XING["子"] == "水"
        assert ZHI_WU_XING["丑"] == "土"
        assert ZHI_WU_XING["寅"] == "木"
        assert ZHI_WU_XING["卯"] == "木"
        assert ZHI_WU_XING["辰"] == "土"
        assert ZHI_WU_XING["巳"] == "火"
        assert ZHI_WU_XING["午"] == "火"
        assert ZHI_WU_XING["未"] == "土"
        assert ZHI_WU_XING["申"] == "金"
        assert ZHI_WU_XING["酉"] == "金"
        assert ZHI_WU_XING["戌"] == "土"
        assert ZHI_WU_XING["亥"] == "水"

    def test_zhi_wu_xing_completeness(self):
        """測試地支五行完整性"""
        for zhi in Zhi:
            assert zhi in ZHI_WU_XING


class TestTianGanYinYang:
    """測試天干陰陽"""

    def test_yang_gans(self):
        """測試陽天干"""
        assert TIAN_GAN_YIN_YANG["甲"] == "陽"
        assert TIAN_GAN_YIN_YANG["丙"] == "陽"
        assert TIAN_GAN_YIN_YANG["戊"] == "陽"
        assert TIAN_GAN_YIN_YANG["庚"] == "陽"
        assert TIAN_GAN_YIN_YANG["壬"] == "陽"

    def test_yin_gans(self):
        """測試陰天干"""
        assert TIAN_GAN_YIN_YANG["乙"] == "陰"
        assert TIAN_GAN_YIN_YANG["丁"] == "陰"
        assert TIAN_GAN_YIN_YANG["己"] == "陰"
        assert TIAN_GAN_YIN_YANG["辛"] == "陰"
        assert TIAN_GAN_YIN_YANG["癸"] == "陰"

    def test_yin_yang_alternation(self):
        """測試陰陽交替"""
        for i, gan in enumerate(Gan):
            expected = "陽" if i % 2 == 0 else "陰"
            assert TIAN_GAN_YIN_YANG[gan] == expected


class TestWuXingSheng:
    """測試五行相生"""

    def test_wu_xing_sheng(self):
        """測試五行相生"""
        assert WU_XING_SHENG["木"] == "火"
        assert WU_XING_SHENG["火"] == "土"
        assert WU_XING_SHENG["土"] == "金"
        assert WU_XING_SHENG["金"] == "水"
        assert WU_XING_SHENG["水"] == "木"


class TestWuXingKe:
    """測試五行相剋"""

    def test_wu_xing_ke(self):
        """測試五行相剋"""
        assert WU_XING_KE["木"] == "土"
        assert WU_XING_KE["火"] == "金"
        assert WU_XING_KE["土"] == "水"
        assert WU_XING_KE["金"] == "木"
        assert WU_XING_KE["水"] == "火"

    def test_wu_xing_ke_reverse(self):
        """測試五行被剋"""
        # 木剋土，土被木剋
        assert WU_XING_KE["土"] == "水"  # 土剋水
        # 验证相剋關係
        for element, ke_element in WU_XING_KE.items():
            # 每個元素剋另一個元素
            assert ke_element in WU_XING_SHENG or ke_element in WU_XING_KE


class TestZhiLiuHe:
    """測試地支六合"""

    def test_liu_he_pairs(self):
        """測試六合配對"""
        # 子丑合 - key 是 "子丑" 和 "丑子"
        assert "子丑" in ZHI_LIU_HE
        assert "丑子" in ZHI_LIU_HE
        # 驗證六合配對完整性
        expected_keys = ["子丑", "丑子", "寅亥", "亥寅", "卯戌", "戌卯", "辰酉", "酉辰", "巳申", "申巳", "午未", "未午"]
        for key in expected_keys:
            assert key in ZHI_LIU_HE

    def test_liu_he_completeness(self):
        """測試六合完整性"""
        # 六合：子丑、寅亥、卯戌、辰酉、巳申、午未
        expected_pairs = [
            ("子", "丑"),
            ("寅", "亥"),
            ("卯", "戌"),
            ("辰", "酉"),
            ("巳", "申"),
            ("午", "未"),
        ]
        for gan, zhi in expected_pairs:
            key1 = f"{gan}{zhi}"
            key2 = f"{zhi}{gan}"
            assert key1 in ZHI_LIU_HE
            assert key2 in ZHI_LIU_HE


class TestZhiLiuChong:
    """測試地支六沖"""

    def test_liu_chong_pairs(self):
        """測試六沖配對"""
        # 六沖是一個 list of tuples: [("子", "午"), ("丑", "未"), ...]
        # 注意：list 中只有單向配對，沒有反向
        assert ("子", "午") in ZHI_LIU_CHONG
        # 反向配對不存在於 list 中
        assert ("午", "子") not in ZHI_LIU_CHONG

    def test_liu_chong_completeness(self):
        """測試六沖完整性"""
        # 六沖：子午、丑未、寅申、卯酉、辰戌、巳亥（只有單向）
        expected_pairs = [
            ("子", "午"),
            ("丑", "未"),
            ("寅", "申"),
            ("卯", "酉"),
            ("辰", "戌"),
            ("巳", "亥"),
        ]
        for gan, zhi in expected_pairs:
            assert (gan, zhi) in ZHI_LIU_CHONG


class TestZhiSanHe:
    """測試地支三合"""

    def test_san_heju(self):
        """測試三合局"""
        # 三合局結構：{"水局": {"長生": "申", "帝旺": "子", "墓庫": "辰", "化氣": "水"}, ...}
        # 申子辰合水局
        assert "水局" in ZHI_SAN_HE_JU
        assert ZHI_SAN_HE_JU["水局"]["長生"] == "申"
        assert ZHI_SAN_HE_JU["水局"]["帝旺"] == "子"
        assert ZHI_SAN_HE_JU["水局"]["墓庫"] == "辰"
        assert ZHI_SAN_HE_JU["水局"]["化氣"] == "水"

        # 驗證所有三合局
        assert "火局" in ZHI_SAN_HE_JU  # 寅午戌
        assert "金局" in ZHI_SAN_HE_JU  # 巳酉丑
        assert "木局" in ZHI_SAN_HE_JU  # 亥卯未


class TestTianGanWuHe:
    """測試天干五合"""

    def test_wu_he_pairs(self):
        """測試五合配對"""
        # 甲己合 - key 是 "甲己"
        assert "甲己" in TIAN_GAN_WU_HE
        # 驗證五合的結構
        assert TIAN_GAN_WU_HE["甲己"]["合名"] == "甲己合"
        assert TIAN_GAN_WU_HE["甲己"]["化氣"] == "土"

    def test_wu_he_completeness(self):
        """測試五合完整性"""
        # 五合：甲己、乙庚、丙辛、丁壬、戊癸
        expected_pairs = [
            ("甲", "己"),
            ("乙", "庚"),
            ("丙", "辛"),
            ("丁", "壬"),
            ("戊", "癸"),
        ]
        for gan1, gan2 in expected_pairs:
            key = f"{gan1}{gan2}"
            assert key in TIAN_GAN_WU_HE


class TestConstantsCompleteness:
    """測試常數完整性"""

    def test_all_gans_have_wu_xing(self):
        """測試所有天干都有五行"""
        for gan in Gan:
            assert gan in TIAN_GAN_WU_XING, f"天干 {gan} 缺少五行定義"

    def test_all_zhis_have_wu_xing(self):
        """測試所有地支都有五行"""
        for zhi in Zhi:
            assert zhi in ZHI_WU_XING, f"地支 {zhi} 缺少五行定義"

    def test_all_gans_have_yin_yang(self):
        """測試所有天干都有陰陽"""
        for gan in Gan:
            assert gan in TIAN_GAN_YIN_YANG, f"天干 {gan} 缺少陰陽定義"
