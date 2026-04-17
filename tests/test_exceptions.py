"""
異常模塊測試
"""

import pytest
from bazi.exceptions import (
    BaZiException,
    ValidationError,
    InvalidBirthTimeError,
    InvalidBirthYearError,
    InvalidBirthMonthError,
    InvalidBirthDayError,
    InvalidBirthHourError,
    InvalidGenderError,
    InvalidCalendarError,
    InvalidCityError,
    CalculationError,
    LunarCalendarError,
    SolarTimeCalculationError,
    PillarCalculationError,
    DaYunCalculationError,
    ResourceError,
    CityNotFoundError,
    ConfigNotFoundError,
    FileResourceError,
    AnalysisError,
    GeJuAnalysisError,
    WangShuaiAnalysisError,
    ShenShaAnalysisError,
)


class TestExceptionHierarchy:
    """測試異常層級結構"""

    def test_bazi_exception_base(self):
        """測試基礎異常"""
        exc = BaZiException("測試錯誤")
        assert str(exc) == "測試錯誤"
        assert isinstance(exc, Exception)

    def test_validation_error_base(self):
        """測試驗證錯誤基礎類"""
        exc = ValidationError("驗證失敗", "field", "value")
        assert exc.message == "驗證失敗"
        assert exc.field == "field"
        assert exc.value == "value"
        assert isinstance(exc, BaZiException)


class TestValidationErrors:
    """測試驗證異常"""

    def test_invalid_gender_error(self):
        """測試性別錯誤"""
        exc = InvalidGenderError("性別無效", "gender", "未知")
        assert exc.message == "性別無效"
        assert exc.field == "gender"
        assert exc.value == "未知"
        assert isinstance(exc, ValidationError)

    def test_invalid_calendar_error(self):
        """測試曆法錯誤"""
        exc = InvalidCalendarError("曆法無效", "calendar", "陽曆")
        assert exc.message == "曆法無效"
        assert exc.field == "calendar"
        assert exc.value == "陽曆"

    def test_invalid_city_error(self):
        """測試城市錯誤"""
        exc = InvalidCityError("城市未找到", "city", "未知城市")
        assert exc.message == "城市未找到"
        assert exc.field == "city"
        assert exc.value == "未知城市"

    def test_birth_time_errors(self):
        """測試出生時間錯誤"""
        # InvalidBirthTimeError
        exc = InvalidBirthTimeError("時間無效")
        assert exc.message == "時間無效"

        # InvalidBirthYearError
        exc = InvalidBirthYearError("年份無效", "year", 1800)
        assert exc.message == "年份無效"
        assert exc.value == 1800

        # InvalidBirthMonthError
        exc = InvalidBirthMonthError("月份無效", "month", 13)
        assert exc.message == "月份無效"

        # InvalidBirthDayError
        exc = InvalidBirthDayError("日期無效", "day", 32)
        assert exc.message == "日期無效"

        # InvalidBirthHourError
        exc = InvalidBirthHourError("小時無效", "hour", 25)
        assert exc.message == "小時無效"


class TestCalculationErrors:
    """測試計算異常"""

    def test_calculation_error_base(self):
        """測試計算錯誤基礎類"""
        exc = CalculationError("計算失敗", "step", {"detail": "info"})
        assert exc.message == "計算失敗"
        assert exc.step == "step"
        assert exc.details == {"detail": "info"}
        assert isinstance(exc, BaZiException)

    def test_lunar_calendar_error(self):
        """測試農曆錯誤"""
        exc = LunarCalendarError("農曆轉換失敗", "lunar_conversion")
        assert exc.message == "農曆轉換失敗"
        assert exc.step == "lunar_conversion"

    def test_solar_time_error(self):
        """測試真太陽時錯誤"""
        exc = SolarTimeCalculationError("真太陽時計算失敗", "solar_time")
        assert exc.message == "真太陽時計算失敗"

    def test_pillar_error(self):
        """測試四柱錯誤"""
        exc = PillarCalculationError("四柱計算失敗", "pillar_calculation")
        assert exc.message == "四柱計算失敗"

    def test_dayun_error(self):
        """測試大運錯誤"""
        exc = DaYunCalculationError("大運計算失敗", "dayun_calculation")
        assert exc.message == "大運計算失敗"


class TestResourceErrors:
    """測試資源異常"""

    def test_resource_error_base(self):
        """測試資源錯誤基礎類"""
        exc = ResourceError("資源未找到", "resource_type")
        assert exc.message == "資源未找到"
        assert exc.resource_type == "resource_type"
        assert isinstance(exc, BaZiException)

    def test_city_not_found_error(self):
        """測試城市未找到錯誤"""
        exc = CityNotFoundError("城市未找到", "未知城市")
        assert exc.message == "城市未找到"
        assert exc.city_name == "未知城市"
        assert exc.resource_type == "city"

    def test_config_not_found_error(self):
        """測試配置未找到錯誤"""
        exc = ConfigNotFoundError("配置未找到", "api_key")
        assert exc.message == "配置未找到"
        assert exc.config_key == "api_key"

    def test_file_resource_error(self):
        """測試文件資源錯誤"""
        exc = FileResourceError("文件讀取失敗", "/path/to/file")
        assert exc.message == "文件讀取失敗"
        assert exc.file_path == "/path/to/file"


class TestAnalysisErrors:
    """測試分析異常"""

    def test_analysis_error_base(self):
        """測試分析錯誤基礎類"""
        exc = AnalysisError("分析失敗", "analysis_type")
        assert exc.message == "分析失敗"
        assert exc.analysis_type == "analysis_type"
        assert isinstance(exc, BaZiException)

    def test_geju_analysis_error(self):
        """測試格局分析錯誤"""
        exc = GeJuAnalysisError("格局判斷失敗", "正官格")
        assert exc.message == "格局判斷失敗"
        assert exc.ge_ju == "正官格"

    def test_wangshuai_analysis_error(self):
        """測試旺衰分析錯誤"""
        exc = WangShuaiAnalysisError("旺衰判斷失敗", "甲")
        assert exc.message == "旺衰判斷失敗"
        assert exc.day_gan == "甲"

    def test_shensha_analysis_error(self):
        """測試神煞分析錯誤"""
        exc = ShenShaAnalysisError("神煞計算失敗", "文昌貴人")
        assert exc.message == "神煞計算失敗"
        assert exc.shen_sha == "文昌貴人"


class TestExceptionInheritance:
    """測試異常繼承關係"""

    def test_all_validation_errors_inherit_from_bazi(self):
        """測試所有驗證錯誤繼承自 BaZiException"""
        errors = [
            InvalidGenderError("msg"),
            InvalidCalendarError("msg"),
            InvalidCityError("msg"),
            InvalidBirthTimeError("msg"),
            InvalidBirthYearError("msg"),
            InvalidBirthMonthError("msg"),
            InvalidBirthDayError("msg"),
            InvalidBirthHourError("msg"),
        ]
        for exc in errors:
            assert isinstance(exc, BaZiException)

    def test_all_calculation_errors_inherit_from_bazi(self):
        """測試所有計算錯誤繼承自 BaZiException"""
        errors = [
            LunarCalendarError("msg"),
            SolarTimeCalculationError("msg"),
            PillarCalculationError("msg"),
            DaYunCalculationError("msg"),
        ]
        for exc in errors:
            assert isinstance(exc, BaZiException)

    def test_all_resource_errors_inherit_from_bazi(self):
        """測試所有資源錯誤繼承自 BaZiException"""
        errors = [
            CityNotFoundError("msg"),
            ConfigNotFoundError("msg"),
            FileResourceError("msg"),
        ]
        for exc in errors:
            assert isinstance(exc, BaZiException)

    def test_all_analysis_errors_inherit_from_bazi(self):
        """測試所有分析錯誤繼承自 BaZiException"""
        errors = [
            GeJuAnalysisError("msg"),
            WangShuaiAnalysisError("msg"),
            ShenShaAnalysisError("msg"),
        ]
        for exc in errors:
            assert isinstance(exc, BaZiException)
