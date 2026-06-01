"""
名人匹配 API 路由
提供按出生日期查詢匹配名人的端點。
"""

import calendar
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from bazi.data.celebrity_matcher import find_matching_celebrities

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/celebrities", tags=["celebrities"])


@router.get("/match")
async def match_celebrities(
    year: int = Query(..., ge=1900, le=2100, description="公曆年份"),
    month: int = Query(..., ge=1, le=12, description="公曆月份"),
    day: int = Query(..., ge=1, le=31, description="公曆日期"),
):
    """
    根據出生日期匹配名人。

    回傳三個類別:
    - 同月同日: 出生月日相同（任何年份，排除近似日期）
    - 同年: 出生年份相同
    - 同月: 出生月份相同（最多 10 筆，按年份接近排序）
    """
    # 驗證日期有效性
    max_day = calendar.monthrange(year, month)[1]
    if day > max_day:
        raise HTTPException(
            status_code=400,
            detail=f"日期無效：{month}月最多{max_day}天",
        )

    try:
        result = find_matching_celebrities(year, month, day)
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception("名人匹配錯誤")
        return JSONResponse(
            status_code=500,
            content={"error": "匹配名人時發生錯誤，請稍後再試。"},
        )
