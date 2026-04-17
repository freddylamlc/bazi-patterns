"""
集成測試 - 測試 API 端點和完整流程
"""

import pytest
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestBaZiCalculatorIntegration:
    """測試 BaZiCalculator 集成"""

    def test_import_bazi_calculator(self):
        """測試導入 BaZiCalculator"""
        try:
            from bazi import BaZiCalculator
            assert BaZiCalculator is not None
        except ImportError as e:
            pytest.fail(f"無法導入 BaZiCalculator: {e}")

    def test_import_bazi_package(self):
        """測試導入 bazi 包"""
        try:
            from bazi import BaZiCalculator
            assert BaZiCalculator is not None
        except ImportError as e:
            pytest.fail(f"無法導入 bazi 包：{e}")

    def test_calculator_basic_instantiation(self):
        """測試計算器基本實例化"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        assert calc is not None
        assert calc.name == "測試"
        assert calc.gender == "男"

    def test_calculator_bazi_output(self):
        """測試計算器八字輸出"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        # 檢查八字輸出 - ba_zi 返回字串（"甲子 乙丑 丙寅 丁卯" 格式）
        assert hasattr(calc, 'ba_zi')
        assert calc.ba_zi is not None
        # ba_zi 可以是字串或 dict，取決於實現
        if isinstance(calc.ba_zi, str):
            # 字串格式："乙亥 丁亥 己未 庚午"
            assert len(calc.ba_zi.split()) == 4  # 四個柱
        elif isinstance(calc.ba_zi, dict):
            # dict 格式：{'年柱': '乙亥', '月柱': '丁亥', ...}
            assert '年柱' in calc.ba_zi
            assert '月柱' in calc.ba_zi
            assert '日柱' in calc.ba_zi
            assert '時柱' in calc.ba_zi

    def test_calculator_canggan_output(self):
        """測試計算器藏干輸出"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        assert hasattr(calc, 'cang_gan')
        assert calc.cang_gan is not None

    def test_calculator_shishen_output(self):
        """測試計算器十神輸出"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        assert hasattr(calc, 'shi_shen')
        assert calc.shi_shen is not None

    def test_calculator_geju_output(self):
        """測試計算器格局輸出"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        assert hasattr(calc, 'ge_ju')
        assert calc.ge_ju is not None
        assert '格局' in calc.ge_ju

    def test_calculator_dayun_output(self):
        """測試計算器大運輸出"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        assert hasattr(calc, 'da_yun_info')
        assert calc.da_yun_info is not None

    def test_calculator_gongwei_output(self):
        """測試計算器宮位輸出"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        assert hasattr(calc, 'gong_wei')
        assert calc.gong_wei is not None

    def test_calculator_bingyuan_output(self):
        """測試計算器先天病源輸出"""
        from bazi import BaZiCalculator

        calc = BaZiCalculator(
            name="測試",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
        )

        assert hasattr(calc, 'xian_tian_bing_yuan')
        assert calc.xian_tian_bing_yuan is not None


class TestConfigIntegration:
    """測試配置集成"""

    def test_config_load(self):
        """測試配置加載"""
        from config.settings import Settings

        settings = Settings.load()
        assert settings is not None
        assert settings.app_name == "八字計算器"

    def test_get_settings(self):
        """測試獲取配置"""
        from config.settings import get_settings

        settings = get_settings()
        assert settings is not None


class TestValidatorIntegration:
    """測試驗證器集成"""

    def test_validate_complete_flow(self):
        """測試完整驗證流程"""
        from bazi.validators import validate_complete_input

        result = validate_complete_input(
            name="張三",
            gender="男",
            calendar="公曆",
            year=1995,
            month=11,
            day=24,
            hour=12,
            minute=0,
            birth_city="香港",
            current_city="台北"
        )

        assert result[0] == "張三"
        assert result[1] == "男"
        assert result[2] == "公曆"
        assert result[3] == 1995


class TestExceptionIntegration:
    """測試異常集成"""

    def test_exception_hierarchy(self):
        """測試異常層級"""
        from bazi.exceptions import BaZiException, InvalidGenderError

        try:
            raise InvalidGenderError("測試錯誤", "gender", "未知")
        except BaZiException as e:
            assert isinstance(e, InvalidGenderError)
            assert e.message == "測試錯誤"
