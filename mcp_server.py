# mcp_server.py

import os
from mcp.server.fastmcp import FastMCP
from bazi import BaZiCalculator

# Create an MCP server
mcp = FastMCP(name="BaZi Tool")

# Configure server settings
mcp.settings.port = int(os.environ.get("PORT", "8001"))
mcp.settings.host = "0.0.0.0"

@mcp.tool()
def bazi(
    name: str,
    gender: str,
    calendar: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    birth_city: str,
    current_city: str | None = None,
) -> dict:
    """
    Calculate BaZi (八字) information.

    Args:
        name: The name of the person.
        gender: The gender of the person ('男' for male, '女' for female).
        calendar: The calendar type for the birth date ('公曆' for Gregorian, '農曆' for Lunar).
        year: The year of birth.
        month: The month of birth.
        day: The day of birth.
        hour: The hour of birth (0-23).
        minute: The minute of birth (0-59).
        birth_city: The city of birth.
        current_city: The current city of residence (optional).

    Returns:
        A dictionary containing the BaZi information.
    """
    calculator = BaZiCalculator(
        name=name,
        gender=gender,
        calendar=calendar,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        birth_city=birth_city,
        current_city=current_city,
    )

    gender_text = "男 (乾造)" if calculator.gender == "男" else "女 (坤造)"

    if calculator.calendar == "公曆":
        solar_date_str = f"{calculator.solar_time.year}年{calculator.solar_time.month}月{calculator.solar_time.day}日{calculator.solar_time.hour:02d}:{calculator.solar_time.minute:02d}"
        lunar_year = calculator.lunar_date.getLunarYear()
        lunar_month = calculator.lunar_date.getLunarMonth()
        lunar_day = calculator.lunar_date.getLunarDay()
        is_leap = "(閏月)" if calculator.lunar_date.isLunarLeap() else ""
        lunar_date_str = f"{lunar_year}年{lunar_month}月{lunar_day}日{calculator.solar_time.hour:02d}:{calculator.solar_time.minute:02d} {is_leap}"
        birth_time_info = {
            "公曆": solar_date_str,
            "農曆": lunar_date_str
        }
    else:  # 農曆
        lunar_year = calculator.lunar_date.getLunarYear()
        lunar_month = calculator.lunar_date.getLunarMonth()
        lunar_day = calculator.lunar_date.getLunarDay()
        is_leap = "(閏月)" if calculator.lunar_date.isLunarLeap() else ""
        lunar_date_str = f"{lunar_year}年{lunar_month}月{lunar_day}日{calculator.solar_time.hour:02d}:{calculator.solar_time.minute:02d} {is_leap}"
        solar_date_str = f"{calculator.solar_time.year}年{calculator.solar_time.month}月{calculator.solar_time.day}日{calculator.solar_time.hour:02d}:{calculator.solar_time.minute:02d}"
        birth_time_info = {
            "農曆": lunar_date_str,
            "公曆": solar_date_str
        }

    result = {
        "姓名": calculator.name,
        "性別": gender_text,
        "出生時間": birth_time_info,
        "出生城市": f"{calculator.birth_city} (經度：{calculator.birth_longitude}°E)",
        "現居城市": calculator.current_city,
        "八字": calculator.ba_zi,
        "節氣": calculator.jie_qi_info,
        "大運": calculator.da_yun_info,
    }
    return result

if __name__ == "__main__":
    # Per mcp.json, the server should run on port 8001.
    # The default mount path for streamable-http is /mcp, which matches the config.
    mcp.run(transport="streamable-http")
