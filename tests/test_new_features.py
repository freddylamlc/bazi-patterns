"""
新功能測試 - 測試一柱論命、干支象法、斷語庫、歲運進階功能
"""

import pytest
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestYiZhuLunMing:
    """測試一柱論命模塊"""

    def test_import_yi_zhu(self):
        """測試導入一柱論命模塊"""
        from bazi.analysis.yizhu import calculate_yi_zhu
        assert calculate_yi_zhu is not None

    def test_yi_zhu_basic(self):
        """測試一柱論命基本功能"""
        from bazi.analysis.yizhu import calculate_yi_zhu

        result = calculate_yi_zhu('甲子', '男')

        assert result is not None
        assert result['日柱'] == '甲子'
        assert '婚姻斷語' in result
        assert '六親斷語' in result
        assert '健康斷語' in result
        assert '性格斷語' in result
        assert '事業斷語' in result
        assert '特殊斷語' in result

    def test_yi_zhu_jia_zi(self):
        """測試甲子日斷語（六十甲子體象論邏輯）"""
        from bazi.analysis.yizhu import calculate_yi_zhu

        result = calculate_yi_zhu('甲子', '男')

        # 六十甲子體象論邏輯：甲子日坐沐浴桃花
        assert '所屬旬' in result
        assert result['所屬旬'] == '甲子旬'
        assert '空亡' in result
        assert result['空亡'] == '戌亥'

    def test_yi_zhu_jia_wu(self):
        """測試甲午日斷語（六十甲子體象論邏輯）"""
        from bazi.analysis.yizhu import calculate_yi_zhu

        result = calculate_yi_zhu('甲午', '男')

        # 六十甲子體象論邏輯：甲午日坐死地，旬首日
        assert '所屬旬' in result
        assert result['所屬旬'] == '甲午旬'
        assert '空亡' in result
        assert result['空亡'] == '辰巳'
        # 旬首日特殊斷語
        assert '旬首' in result['特殊斷語'] or '長' in result['特殊斷語']

    def test_yi_zhu_unknown(self):
        """測試未知日柱處理"""
        from bazi.analysis.yizhu import calculate_yi_zhu

        result = calculate_yi_zhu('無效', '男')

        assert result['日柱'] == '無效'
        assert result['婚姻斷語'] == '暫無數據'


class TestGanZhiXiang:
    """測試干支象法模塊"""

    def test_import_ganzhi_xiang(self):
        """測試導入干支象法模塊"""
        from bazi.analysis.ganzhi_xiang import calculate_ganzhi_xiang
        assert calculate_ganzhi_xiang is not None

    def test_ganzhi_xiang_basic(self):
        """測試干支象法基本功能"""
        from bazi.analysis.ganzhi_xiang import calculate_ganzhi_xiang

        result = calculate_ganzhi_xiang('甲子 乙丑 丙寅 丁卯')

        assert result is not None
        assert '四柱干支象' in result
        assert '五行化氣' in result
        assert '疾病預測' in result
        assert '特殊疾病' in result
        # 檢查四柱干支象結構
        assert len(result['四柱干支象']) == 4
        for pillar in result['四柱干支象']:
            assert '位置' in pillar
            assert '干支' in pillar
            assert '天干' in pillar
            assert '地支' in pillar
            assert '天干臟腑' in pillar
            assert '地支臟腑' in pillar
            assert '天干意象' in pillar
            assert '地支意象' in pillar
            assert '吉凶' in pillar

    def test_gan_zang_fu(self):
        """測試天干臟腑對應"""
        from bazi.analysis.ganzhi_xiang import GAN_ZHANG_FU

        assert GAN_ZHANG_FU['甲']['臟腑'] == '膽'
        assert GAN_ZHANG_FU['乙']['臟腑'] == '肝'
        assert GAN_ZHANG_FU['丙']['臟腑'] == '小腸'
        assert GAN_ZHANG_FU['丁']['臟腑'] == '心'

    def test_zhi_zang_fu(self):
        """測試地支臟腑對應"""
        from bazi.analysis.ganzhi_xiang import ZHI_ZHANG_FU

        assert ZHI_ZHANG_FU['子']['臟腑'] == '膀胱'
        assert ZHI_ZHANG_FU['午']['臟腑'] == '心'
        assert ZHI_ZHANG_FU['卯']['臟腑'] == '肝'
        assert ZHI_ZHANG_FU['酉']['臟腑'] == '肺'

    def test_ganzhi_yi_xiang(self):
        """測試干支意象"""
        from bazi.analysis.ganzhi_xiang import GAN_YI_XIANG, ZHI_YI_XIANG

        assert '直' in GAN_YI_XIANG['甲']
        assert '坎智' in ZHI_YI_XIANG['子']
        assert '青龍' in ZHI_YI_XIANG['寅']


class TestDuanYuDB:
    """測試斷語數據庫模塊"""

    def test_import_duanyu_db(self):
        """測試導入斷語數據庫模塊"""
        from bazi.analysis.duanyu_db import get_shishen_duan_yu
        assert get_shishen_duan_yu is not None

    def test_shishen_duan_yu_zheng_guan(self):
        """測試正官斷語"""
        from bazi.analysis.duanyu_db import get_shishen_duan_yu

        result = get_shishen_duan_yu('正官', False)

        assert result is not None
        assert '吉凶' in result
        assert '事件' in result
        assert '心性' in result
        assert '知禮守法' in result['心性']

    def test_shishen_duan_yu_qi_sha(self):
        """測試七殺斷語"""
        from bazi.analysis.duanyu_db import get_shishen_duan_yu

        result = get_shishen_duan_yu('七殺', False)

        assert result is not None
        assert '膽氣' in result['心性'] or '魄力' in result['心性']

    def test_shishen_duan_yu_ji_shen(self):
        """測試忌神斷語"""
        from bazi.analysis.duanyu_db import get_shishen_duan_yu

        result = get_shishen_duan_yu('正官', True)

        assert result['吉凶'] == '凶'
        assert '壓力' in result['事件'] or '負擔' in result['事件']


class TestYiHuaJieMu:
    """測試移花接木功能"""

    def test_import_yi_hua_jie_mu(self):
        """測試導入移花接木功能"""
        from bazi.calculations.dayun import calculate_yi_hua_jie_mu
        assert calculate_yi_hua_jie_mu is not None

    def test_yi_hua_jie_mu_basic(self):
        """測試移花接木基本功能"""
        from bazi.calculations.dayun import calculate_yi_hua_jie_mu

        test_dayun = [
            {'大運': '丙寅', '大運支': '寅'},
            {'大運': '丁卯', '大運支': '卯'},
            {'大運': '戊辰', '大運支': '辰'},
            {'大運': '己巳', '大運支': '巳'},
        ]

        result = calculate_yi_hua_jie_mu(test_dayun)

        assert result is not None
        assert '四庫大運' in result
        assert '說明' in result

    def test_yi_hua_jie_mu_chen(self):
        """測試辰土大運"""
        from bazi.calculations.dayun import calculate_yi_hua_jie_mu

        test_dayun = [
            {'大運': '丙寅', '大運支': '寅'},
            {'大運': '丁卯', '大運支': '卯'},
            {'大運': '戊辰', '大運支': '辰'},
            {'大運': '己巳', '大運支': '巳'},
        ]

        result = calculate_yi_hua_jie_mu(test_dayun)

        assert len(result['四庫大運']) == 1
        assert result['四庫大運'][0]['大運支'] == '辰'

    def test_yi_hua_jie_mu_si_ku(self):
        """測試四庫大運（辰戌丑未）"""
        from bazi.calculations.dayun import calculate_yi_hua_jie_mu

        test_dayun = [
            {'大運': '甲辰', '大運支': '辰'},
            {'大運': '乙巳', '大運支': '巳'},
            {'大運': '丙戌', '大運支': '戌'},
            {'大運': '丁亥', '大運支': '亥'},
            {'大運': '戊子', '大運支': '子'},
            {'大運': '己丑', '大運支': '丑'},
            {'大運': '庚寅', '大運支': '寅'},
            {'大運': '辛未', '大運支': '未'},
        ]

        result = calculate_yi_hua_jie_mu(test_dayun)

        # 應該有 4 個四庫大運：辰、戌、丑、未
        assert len(result['四庫大運']) == 4
        si_ku_zhi = [d['大運支'] for d in result['四庫大運']]
        assert set(si_ku_zhi) == {'辰', '戌', '丑', '未'}

    def test_yi_hua_jie_mu_no_si_ku(self):
        """測試無四庫大運"""
        from bazi.calculations.dayun import calculate_yi_hua_jie_mu

        test_dayun = [
            {'大運': '甲寅', '大運支': '寅'},
            {'大運': '乙卯', '大運支': '卯'},
            {'大運': '丙巳', '大運支': '巳'},
            {'大運': '丁午', '大運支': '午'},
        ]

        result = calculate_yi_hua_jie_mu(test_dayun)

        assert len(result['四庫大運']) == 0


class TestLiangGeBingCun:
    """測試兩格並存功能（簡化版）"""

    def test_import_liang_ge_bing_cun(self):
        """測試導入兩格並存功能"""
        from bazi.analysis.geju import calculate_liang_ge_bing_cun
        assert calculate_liang_ge_bing_cun is not None

    def test_liang_ge_bing_cun_basic(self):
        """測試兩格並存基本功能"""
        from bazi.analysis.geju import calculate_liang_ge_bing_cun

        result = calculate_liang_ge_bing_cun('甲子 乙丑 丙寅 丁卯', {'格局': '正官格'})

        assert result is not None
        assert '雙格局' in result
        assert '說明' in result

    def test_liang_ge_bing_cun_simple_output(self):
        """測試兩格並存簡化輸出（只返回雙格局和說明）"""
        from bazi.analysis.geju import calculate_liang_ge_bing_cun

        result = calculate_liang_ge_bing_cun('甲子 乙丑 丙寅 丁卯', {'格局': '正官格'})

        # 簡化後只返回雙格局和說明
        assert '雙格局' in result
        assert '說明' in result
        # 不再返回成格狀態、左邊格局、右邊格局
        assert '成格狀態' not in result
        assert '左邊格局' not in result
        assert '右邊格局' not in result

    def test_liang_ge_bing_cun_with_geju(self):
        """測試兩格並存顯示格局名稱"""
        from bazi.analysis.geju import calculate_liang_ge_bing_cun

        result = calculate_liang_ge_bing_cun('甲子 乙丑 丙寅 丁卯', {'格局': '正官格'})

        assert result['雙格局'] == '正官格'

    def test_liang_ge_bing_cun_no_geju(self):
        """測試兩格並存無格局情況"""
        from bazi.analysis.geju import calculate_liang_ge_bing_cun

        result = calculate_liang_ge_bing_cun('甲子 乙丑 丙寅 丁卯', {'格局': '無格局'})

        assert result['雙格局'] == '無格局'


class TestBaZiCalculatorIntegration:
    """測試 BaZiCalculator 集成新功能"""

    def test_yi_hua_jie_mu_integration(self):
        """測試移花接木集成"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name='測試',
            gender='男',
            calendar='公曆',
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city='香港',
        )

        assert hasattr(calc, 'yi_hua_jie_mu')
        assert '四庫大運' in calc.yi_hua_jie_mu
        assert '說明' in calc.yi_hua_jie_mu

    def test_yi_zhu_integration(self):
        """測試一柱論命集成"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name='測試',
            gender='男',
            calendar='公曆',
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city='香港',
        )

        assert hasattr(calc, 'yi_zhu')
        assert '日柱' in calc.yi_zhu
        assert '婚姻斷語' in calc.yi_zhu

    def test_ganzhi_xiang_integration(self):
        """測試干支象法集成"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name='測試',
            gender='男',
            calendar='公曆',
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city='香港',
        )

        assert hasattr(calc, 'ganzhi_xiang')
        assert '四柱干支象' in calc.ganzhi_xiang
        assert len(calc.ganzhi_xiang['四柱干支象']) == 4
        # 檢查第一柱是否有六亲和吉凶
        first_pillar = calc.ganzhi_xiang['四柱干支象'][0]
        assert '位置' in first_pillar
        assert '干支' in first_pillar
        assert '吉凶' in first_pillar

    def test_liang_ge_bing_cun_integration(self):
        """測試兩格並存集成（簡化版）"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name='測試',
            gender='男',
            calendar='公曆',
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city='香港',
        )

        assert hasattr(calc, 'liang_ge_bing_cun')
        assert '雙格局' in calc.liang_ge_bing_cun
        assert '說明' in calc.liang_ge_bing_cun
