"""
應用設置模塊 - 使用 pydantic-settings 管理配置
支持環境變量覆蓋
"""

from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeJuSettings(BaseSettings):
    """
    格局判斷規則配置

    可通過環境變量覆蓋：
    - GEJU_ENABLE_SHI_SHEN_PERSONALITY: 啟用十神性格分析 (default: true)
    - GEJU_ENABLE_BING_YUAN: 启用先天病源分析 (default: true)
    - GEJU_ENABLE_GONG_WEI: 启用宮位分析 (default: true)
    - GEJU_ENABLE_DAYUN_LIUNIAN: 启用大運流年分析 (default: true)
    """

    # 格局分析開關
    enable_shi_shen_personality: bool = Field(
        default=True,
        description="啟用十神性格分析"
    )
    enable_bing_yuan: bool = Field(
        default=True,
        description="啟用先天病源分析"
    )
    enable_gong_wei: bool = Field(
        default=True,
        description="啟用宮位分析"
    )
    enable_dayun_liunian: bool = Field(
        default=True,
        description="啟用大運流年分析"
    )

    # 格局判斷規則
    enable_special_conditions: bool = Field(
        default=True,
        description="啟用特殊條件（陽日干見正財、陰日干見正官，不論生剋）"
    )

    # 根氣被剋判斷
    enable_genqi_beike_check: bool = Field(
        default=True,
        description="啟用根氣被剋判斷（影響格局成敗）"
    )

    # 十神性格判斷
    shishen_personality_consider_shenwang: bool = Field(
        default=True,
        description="十神性格判斷是否考慮身旺衰"
    )

    # 大運流年判斷
    dayun_liunian_check_special_condition: bool = Field(
        default=True,
        description="大運流年判斷是否檢查特殊條件"
    )

    # 顯示控制
    max_dayun_display: int = Field(
        default=10,
        description="最大顯示大運數量",
        ge=1,
        le=12
    )
    max_liunian_display: int = Field(
        default=100,
        description="最大顯示流年數量",
        ge=10,
        le=120
    )

    model_config = SettingsConfigDict(
        env_prefix="GEJU_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class Settings(BaseSettings):
    """
    應用主配置

    可通過環境變量覆蓋：
    - APP_NAME: 應用名稱
    - APP_VERSION: 應用版本
    - DEBUG: 調試模式
    - DEFAULT_LONGITUDE: 默認經度 (default: 120.0)
    - BIRTH_YEAR_MIN: 最小出生年份 (default: 1900)
    - BIRTH_YEAR_MAX: 最大出生年份 (default: 2100)
    """

    # 應用配置
    app_name: str = Field(
        default="八字計算器",
        description="應用名稱"
    )
    app_version: str = Field(
        default="1.0.0",
        description="應用版本"
    )
    debug: bool = Field(
        default=False,
        description="調試模式"
    )

    # 服務器配置
    host: str = Field(
        default="127.0.0.1",
        description="服務器主機"
    )
    port: int = Field(
        default=8080,
        description="服務器端口",
        ge=1024,
        le=65535
    )

    # 八字計算配置
    default_longitude: float = Field(
        default=120.0,
        description="默認經度（用於真太陽時計算）"
    )
    birth_year_min: int = Field(
        default=1900,
        description="最小出生年份"
    )
    birth_year_max: int = Field(
        default=2100,
        description="最大出生年份"
    )

    # 子配置
    geju: GeJuSettings = Field(
        default_factory=GeJuSettings,
        description="格局判斷配置"
    )

    model_config = SettingsConfigDict(
        env_prefix="BAZI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @classmethod
    def load(cls) -> "Settings":
        """加載配置"""
        return cls()


# 全局配置實例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """獲取全局配置實例"""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reload_settings() -> Settings:
    """重新加載配置"""
    global _settings
    _settings = Settings.load()
    return _settings
