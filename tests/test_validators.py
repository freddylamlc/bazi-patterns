"""
驗證器測試
"""

import pytest
from bazi.validators import (
    validate_birth_info,
    validate_calendar,
    validate_city,
    validate_name,
    validate_bazi_input,
    validate_gender_extended,
    validate_complete_input,
)
from bazi.exceptions import (
    InvalidGenderError,
    InvalidBirthYearError,
    InvalidBirthMonthError,
    InvalidBirthDayError,
    InvalidBirthHourError,
    InvalidBirthTimeError,
    InvalidCalendarError,
    InvalidCityError,
)


class TestValidateBirthInfo:
    """測試出生信息驗證"""

    def test_valid_birth_info(self):
        """測試有效的出生信息"""
        # 不應該拋出異常
        validate_birth_info("男", 1995, 11, 24, 12, 0)
        validate_birth_info("女", 2000, 1, 1, 0, 0)
        validate_birth_info("男", 1900, 12, 31, 23, 59)

    def test_invalid_gender(self):
        """測試無效性別"""
        with pytest.raises(InvalidGenderError):
            validate_birth_info("未知", 1995, 11, 24, 12, 0)
        with pytest.raises(InvalidGenderError):
            validate_birth_info("", 1995, 11, 24, 12, 0)

    def test_invalid_year(self):
        """測試無效年份"""
        with pytest.raises(InvalidBirthYearError):
            validate_birth_info("男", 1899, 11, 24, 12, 0)
        with pytest.raises(InvalidBirthYearError):
            validate_birth_info("男", 2101, 11, 24, 12, 0)

    def test_invalid_month(self):
        """測試無效月份"""
        with pytest.raises(InvalidBirthMonthError):
            validate_birth_info("男", 1995, 0, 24, 12, 0)
        with pytest.raises(InvalidBirthMonthError):
            validate_birth_info("男", 1995, 13, 24, 12, 0)

    def test_invalid_day(self):
        """測試無效日期"""
        with pytest.raises(InvalidBirthDayError):
            validate_birth_info("男", 1995, 11, 0, 12, 0)
        with pytest.raises(InvalidBirthDayError):
            validate_birth_info("男", 1995, 11, 32, 12, 0)

    def test_invalid_hour(self):
        """測試無效小時"""
        with pytest.raises(InvalidBirthHourError):
            validate_birth_info("男", 1995, 11, 24, -1, 0)
        with pytest.raises(InvalidBirthHourError):
            validate_birth_info("男", 1995, 11, 24, 24, 0)

    def test_invalid_minute(self):
        """測試無效分鐘"""
        with pytest.raises(InvalidBirthTimeError):
            validate_birth_info("男", 1995, 11, 24, 12, -1)
        with pytest.raises(InvalidBirthTimeError):
            validate_birth_info("男", 1995, 11, 24, 12, 60)


class TestValidateCalendar:
    """測試曆法驗證"""

    def test_valid_calendar(self):
        """測試有效的曆法"""
        validate_calendar("公曆")
        validate_calendar("農曆")

    def test_invalid_calendar(self):
        """測試無效的曆法"""
        with pytest.raises(InvalidCalendarError):
            validate_calendar("陽曆")
        with pytest.raises(InvalidCalendarError):
            validate_calendar("")
        with pytest.raises(InvalidCalendarError):
            validate_calendar("invalid")


class TestValidateCity:
    """測試城市驗證"""

    def test_valid_city(self):
        """測試有效的城市"""
        validate_city("香港")
        validate_city("台北市")
        validate_city("北京市")

    def test_required_city(self):
        """測試必填城市"""
        with pytest.raises(InvalidCityError):
            validate_city("", required=True)
        with pytest.raises(InvalidCityError):
            validate_city(None, required=True)

    def test_optional_city(self):
        """測試可選城市"""
        # 不應該拋出異常
        validate_city("", required=False)
        validate_city(None, required=False)

    def test_city_too_short(self):
        """測試城市名稱太短"""
        with pytest.raises(InvalidCityError):
            validate_city("A")


class TestValidateName:
    """測試姓名驗證"""

    def test_valid_name(self):
        """測試有效的姓名"""
        result = validate_name("張三")
        assert result == "張三"

        result = validate_name(" 李四 ")
        assert result == "李四"

    def test_optional_name(self):
        """測試可選姓名"""
        result = validate_name("", required=False)
        assert result is None

        result = validate_name(None, required=False)
        assert result is None

    def test_required_name(self):
        """測試必填姓名"""
        with pytest.raises(InvalidBirthTimeError):
            validate_name("", required=True)

    def test_name_too_long(self):
        """測試姓名太長"""
        with pytest.raises(InvalidBirthTimeError):
            validate_name("A" * 51, max_length=50)


class TestValidateBaziInput:
    """測試八字輸入驗證"""

    def test_valid_bazi_input(self):
        """測試有效的八字輸入"""
        validate_bazi_input("甲", "子", "丙", "寅", "戊", "辰", "壬", "子")

    def test_invalid_gan(self):
        """測試無效天干"""
        with pytest.raises(InvalidBirthTimeError):
            validate_bazi_input("X", "子", "丙", "寅", "戊", "辰", "壬", "子")

    def test_invalid_zhi(self):
        """測試無效地支"""
        with pytest.raises(InvalidBirthTimeError):
            validate_bazi_input("甲", "X", "丙", "寅", "戊", "辰", "壬", "子")


class TestValidateGenderExtended:
    """測試擴展性別驗證"""

    def test_valid_gender_formats(self):
        """測試有效的性別格式"""
        # 中文
        validate_gender_extended("男")
        validate_gender_extended("女")

        # 英文單詞
        validate_gender_extended("male")
        validate_gender_extended("female")

        # 英文縮寫
        validate_gender_extended("M")
        validate_gender_extended("F")

        # 完整格式
        validate_gender_extended("男 (乾造)")
        validate_gender_extended("女 (坤造)")

    def test_invalid_gender_format(self):
        """測試無效的性別格式"""
        with pytest.raises(InvalidGenderError):
            validate_gender_extended("未知")
        with pytest.raises(InvalidGenderError):
            validate_gender_extended("")


class TestValidateCompleteInput:
    """測試完整輸入驗證"""

    def test_valid_complete_input(self):
        """測試有效的完整輸入"""
        result = validate_complete_input(
            name="測試",
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
        assert result[0] == "測試"
        assert result[1] == "男"
        assert result[8] == "香港"

    def test_complete_input_with_invalid_data(self):
        """測試完整輸入包含無效數據"""
        with pytest.raises(InvalidGenderError):
            validate_complete_input(
                name="測試",
                gender="未知",
                calendar="公曆",
                year=1995,
                month=11,
                day=24,
                hour=12,
                minute=0,
                birth_city="香港"
            )

        with pytest.raises(InvalidBirthYearError):
            validate_complete_input(
                name="測試",
                gender="男",
                calendar="公曆",
                year=1800,
                month=11,
                day=24,
                hour=12,
                minute=0,
                birth_city="香港"
            )
