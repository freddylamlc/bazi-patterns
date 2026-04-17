import pytest
from bazi.calculations.relations import calculate_tian_gan_wu_he

def test_normal_wu_he():
    """測試單一正常的五合"""
    ba_zi = "甲子 己丑 丙寅 丁卯"
    results = calculate_tian_gan_wu_he(ba_zi)
    # 找甲己合
    res = next((r for r in results if r["合"] == "甲己合"), None)
    assert res is not None
    assert res["狀態"] == "可化" # 丑是土，可以化

def test_zheng_he_2_yang_1_yin():
    """測試爭合：二陽合一陰 (甲己甲)"""
    ba_zi = "甲子 己丑 甲寅 丁卯"
    results = calculate_tian_gan_wu_he(ba_zi)
    jia_ji_results = [r for r in results if r["合"] == "甲己合"]
    assert len(jia_ji_results) == 2
    for r in jia_ji_results:
        assert "爭合" in r["狀態"]

def test_du_he_2_yin_1_yang():
    """測試妒合：二陰合一陽 (丙辛辛)"""
    # 根據計劃：兩辛合一丙為妒合
    ba_zi = "丙子 辛丑 辛卯 丁卯"
    results = calculate_tian_gan_wu_he(ba_zi)
    bing_xin_results = [r for r in results if r["合"] == "丙辛合"]
    assert len(bing_xin_results) == 2
    for r in bing_xin_results:
        assert "妒合" in r["狀態"]

def test_complex_multi_he():
    """測試複雜的多重合 (例如 3 己合 1 甲)"""
    ba_zi = "己丑 己巳 己未 甲子"
    results = calculate_tian_gan_wu_he(ba_zi)
    jia_ji_results = [r for r in results if r["合"] == "甲己合"]
    assert len(jia_ji_results) == 3
    for r in jia_ji_results:
        # 超過 2 個通常也視為爭合/妒合的一種
        assert "爭合" in r["狀態"] or "妒合" in r["狀態"]
