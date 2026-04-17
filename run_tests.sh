#!/bin/bash
# 運行所有測試

echo "======================================"
echo "八字計算器 - 測試套件"
echo "======================================"

# 切換到項目目錄
cd "$(dirname "$0")"

# 安裝測試依賴（如果需要）
echo ""
echo "檢查測試依賴..."
pip install -q pytest pytest-cov 2>/dev/null

# 運行測試
echo ""
echo "運行測試..."
echo ""

# 運行所有測試並生成覆蓋率報告
pytest tests/ \
    --cov=bazi \
    --cov=bazi_tool \
    --cov=config \
    --cov-report=term-missing \
    -v \
    "$@"

# 顯示測試結果摘要
echo ""
echo "======================================"
echo "測試完成"
echo "======================================"
