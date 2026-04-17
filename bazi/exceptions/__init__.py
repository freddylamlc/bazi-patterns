"""
異常模塊 - 包含所有自定義異常類

使用層級結構：
- BaZiException (基礎異常)
  - ValidationError (驗證異常)
    - InvalidBirthTimeError
    - InvalidBirthYearError
    - InvalidBirthMonthError
    - InvalidBirthDayError
    - InvalidBirthHourError
    - InvalidGenderError
    - InvalidCalendarError
  - CalculationError (計算異常)
    - LunarCalendarError
    - SolarTimeCalculationError
    - PillarCalculationError
  - ResourceError (資源異常)
    - CityNotFoundError
    - ConfigNotFoundError
  - AnalysisError (分析異常)
    - GeJuAnalysisError
    - WangShuaiAnalysisError
"""


class BaZiException(Exception):
    """八字計算器基礎異常類"""
    pass


# =============================================
# 驗證異常
# =============================================

class ValidationError(BaZiException):
    """驗證錯誤基礎類"""
    def __init__(self, message: str, field: str = None, value: any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class InvalidBirthTimeError(ValidationError):
    """無效的出生時間異常"""
    def __init__(self, message: str, field: str = "birth_time", value: any = None):
        super().__init__(message, field, value)


class InvalidBirthYearError(ValidationError):
    """無效的出生年份異常"""
    def __init__(self, message: str, field: str = "year", value: any = None):
        super().__init__(message, field, value)


class InvalidBirthMonthError(ValidationError):
    """無效的出生月份異常"""
    def __init__(self, message: str, field: str = "month", value: any = None):
        super().__init__(message, field, value)


class InvalidBirthDayError(ValidationError):
    """無效的出生日子異常"""
    def __init__(self, message: str, field: str = "day", value: any = None):
        super().__init__(message, field, value)


class InvalidBirthHourError(ValidationError):
    """無效的出生時辰異常"""
    def __init__(self, message: str, field: str = "hour", value: any = None):
        super().__init__(message, field, value)


class InvalidGenderError(ValidationError):
    """無效的性別異常"""
    def __init__(self, message: str, field: str = "gender", value: any = None):
        super().__init__(message, field, value)


class InvalidCalendarError(ValidationError):
    """無效的曆法異常"""
    def __init__(self, message: str, field: str = "calendar", value: any = None):
        super().__init__(message, field, value)


class InvalidCityError(ValidationError):
    """無效的城市異常"""
    def __init__(self, message: str, field: str = "city", value: any = None):
        super().__init__(message, field, value)


# =============================================
# 計算異常
# =============================================

class CalculationError(BaZiException):
    """計算過程異常"""
    def __init__(self, message: str, step: str = None, details: dict = None):
        self.message = message
        self.step = step
        self.details = details or {}
        super().__init__(self.message)


class LunarCalendarError(CalculationError):
    """農曆轉換異常"""
    def __init__(self, message: str, step: str = "lunar_conversion", details: dict = None):
        super().__init__(message, step, details)


class SolarTimeCalculationError(CalculationError):
    """真太陽時計算異常"""
    def __init__(self, message: str, step: str = "solar_time", details: dict = None):
        super().__init__(message, step, details)


class PillarCalculationError(CalculationError):
    """四柱計算異常"""
    def __init__(self, message: str, step: str = "pillar_calculation", details: dict = None):
        super().__init__(message, step, details)


class DaYunCalculationError(CalculationError):
    """大運計算異常"""
    def __init__(self, message: str, step: str = "dayun_calculation", details: dict = None):
        super().__init__(message, step, details)


# =============================================
# 資源異常
# =============================================

class ResourceError(BaZiException):
    """資源錯誤基礎類"""
    def __init__(self, message: str, resource_type: str = None):
        self.message = message
        self.resource_type = resource_type
        super().__init__(self.message)


class CityNotFoundError(ResourceError):
    """城市未找到異常"""
    def __init__(self, message: str, city_name: str = None):
        self.city_name = city_name
        super().__init__(message, "city")


class ConfigNotFoundError(ResourceError):
    """配置未找到異常"""
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message, "config")


class FileResourceError(ResourceError):
    """文件資源錯誤"""
    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message, "file")


# =============================================
# 分析異常
# =============================================

class AnalysisError(BaZiException):
    """分析錯誤基礎類"""
    def __init__(self, message: str, analysis_type: str = None):
        self.message = message
        self.analysis_type = analysis_type
        super().__init__(self.message)


class GeJuAnalysisError(AnalysisError):
    """格局分析異常"""
    def __init__(self, message: str, ge_ju: str = None):
        self.ge_ju = ge_ju
        super().__init__(message, "ge_ju")


class WangShuaiAnalysisError(AnalysisError):
    """旺衰分析異常"""
    def __init__(self, message: str, day_gan: str = None):
        self.day_gan = day_gan
        super().__init__(message, "wang_shuai")


class ShenShaAnalysisError(AnalysisError):
    """神煞分析異常"""
    def __init__(self, message: str, shen_sha: str = None):
        self.shen_sha = shen_sha
        super().__init__(message, "shen_sha")


__all__ = [
    # 基礎異常
    "BaZiException",

    # 驗證異常
    "ValidationError",
    "InvalidBirthTimeError",
    "InvalidBirthYearError",
    "InvalidBirthMonthError",
    "InvalidBirthDayError",
    "InvalidBirthHourError",
    "InvalidGenderError",
    "InvalidCalendarError",
    "InvalidCityError",

    # 計算異常
    "CalculationError",
    "LunarCalendarError",
    "SolarTimeCalculationError",
    "PillarCalculationError",
    "DaYunCalculationError",

    # 資源異常
    "ResourceError",
    "CityNotFoundError",
    "ConfigNotFoundError",
    "FileResourceError",

    # 分析異常
    "AnalysisError",
    "GeJuAnalysisError",
    "WangShuaiAnalysisError",
    "ShenShaAnalysisError",
]
