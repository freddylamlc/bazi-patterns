# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## 項目概述

中式八字（Four Pillars of Destiny）計算器，包含：
- Web 界面（FastAPI + Jinja2 模板）
- MCP 服務器（支持 AI Agent 集成）
- CRM 客戶管理系統（SQLite）
- 完整八字排盤、格局分析、大運流年功能

GitHub: https://github.com/freddylamlc/bazi

## 常用命令

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行 Web 界面
python app.py  # 訪問：http://127.0.0.1:8080

# 運行 MCP 服務器
python mcp_server.py  # 訪問：http://localhost:8001/mcp

# Docker 部署
docker compose up --build

# 測試（pytest 配置在 pytest.ini）
pytest tests/ -v                        # 所有測試
pytest tests/ -v -m unit                # 僅單元測試
pytest tests/ -v -m integration         # 僅集成測試
pytest tests/test_integration.py -v     # 單個測試文件
pytest tests/ -v --cov=bazi --cov-report=term-missing  # 含覆蓋率
```

## 架構

### 數據流

```
用戶輸入 (表單/MCP)
    → api/routes.py (compute_bazi) 或 mcp_server.py
        → bazi/core/calculator.py (BaZiCalculator)
            → calculations/ 模塊（四柱、藏干、旺衰、十神、神煞、大運…）
            → analysis/ 模塊（格局、宮位、病源、整合分析…）
        → 返回結果 dict
    → templates/result.html (Jinja2 渲染) 或 MCP JSON response
```

### 目錄結構

```
bazi/
├── core/
│   ├── calculator.py    # BaZiCalculator 主類，協調所有模塊
│   ├── constants.py     # 天干地支、五行、神煞、藏干等常數
│   └── utils.py         # 真太陽時計算、農曆轉換
├── calculations/        # 純計算模塊（輸入數據 → 計算結果）
│   ├── pillar.py        # 四柱計算
│   ├── canggan.py       # 地支藏干
│   ├── relations.py     # 天干五合、地支刑沖合害
│   ├── wangshuai.py     # 旺衰判斷（根氣強度）
│   ├── changsheng.py    # 十二長生
│   ├── shishen.py       # 十神計算
│   ├── shensha.py       # 神煞計算
│   ├── ganzhi.py        # 干支生剋
│   ├── jieqi.py         # 節氣信息
│   ├── dayun.py         # 大運計算（含移花接木）
│   └── liushijiazi.py   # 六十甲子計算
├── analysis/            # 分析模塊（計算結果 → 命理解讀）
│   ├── geju.py          # 格局判斷（含兩格並存）
│   ├── gongwei.py       # 宮位分析
│   ├── bingyuan.py      # 先天病源
│   ├── dayun_liunian.py # 大運流年判斷、歲運格局
│   ├── integrated.py    # 整合分析（格局為核心）
│   ├── yizhu.py         # 一柱論命（60 甲子斷語、干支關係、六親分析）
│   ├── ganzhi_xiang.py  # 干支象法（臟腑、意象、疾病）
│   ├── duanyu_db.py     # 斷語數據庫
│   └── bazi_gua.py      # 八字卦象
├── models/              # Pydantic 數據模型（birth_info, bazi_result）
├── exceptions/          # 自定義異常
├── validators/          # 輸入驗證
└── db.py                # SQLite 客戶管理（CRM）
config/settings.py       # pydantic-settings 配置（環境變量覆蓋）
api/routes.py            # FastAPI 路由（Web 端點 + CRM API）
static/js/app.js         # 前端 JS：大運流年流月選擇、沖刑穿破、天干五合
static/css/style.css     # 自定義樣式（五行顏色、吉凶標籤）
templates/macros.html    # Jinja2 宏（柱卡片、藏干、十神渲染）
templates/result.html    # 結果頁主模板
region.json              # 城市經緯度數據（真太陽時用）
```

### 兩個入口的差異

- **app.py** → FastAPI Web 應用，Jinja2 渲染 HTML，掛載靜態文件，初始化 SQLite DB
- **mcp_server.py** → FastMCP 服務器，返回 JSON，供 AI Agent 調用

### CRM 系統

`bazi/db.py` 管理 SQLite 數據庫 (`bazi.db`)：
- 保存/查詢/刪除客戶命盤
- 每個客戶支持區塊批注（annotations，JSON 存儲）
- API 端點在 `api/routes.py` 中（`/api/clients/*`）

## 核心算法

### 真太陽時
```python
出生時間 + (城市經度 - 120°) × 4 分鐘
```
城市經度從 `region.json` 或 `calculator.py` 中的 `inquire()` 回退字典獲取。

### 大運計算
- 陽男陰女順排，陰男陽女逆排
- 起運年齡 = 節氣天數 ÷ 3

### 流年計算
```python
# 流年從出生年份連續順推，不每個大運重新計算
ln_gan_idx = (year_gan_idx + liunian_age) % 10
ln_zhi_idx = (year_zhi_idx + liunian_age) % 12
```

### 年柱與公曆年份轉換
```python
# 立春前出生的人，年柱屬於前一年（如 1995-01-01 → 甲戌年=1994）
# api/routes.py 中 _get_chinese_year_from_pillar() 從年柱反推公曆年份
# 以甲子=1984 為基準，用六十甲子序列計算偏移
```

### 前端自動跳轉
- 頁面載入時自動跳轉到當前年份對應的大運和流年
- `birthYear` 使用年柱推算的中國年份（非公曆出生年），確保立春前出生者計算正確
- `app.js` 僅在結果頁執行初始化（通過檢測 `#liunian-pillar-container` 守衛）

### 前端五行顏色更新
- 點擊大運/流年/流月時，頂部排盤的天干地支需同步更新五行顏色
- `selectDayun()` 和 `updateLiunianDisplay()` 通過 `className` 設置 Tailwind 五行色類
- 參照 `updateLiuyueDisplay()` 的模式：查找 `ganWuXing`/`zhiWuXing` → `wuXingColors` → 設置 `className`

### Jinja2 模板注意事項
- **必須**使用 `{%- ... -%}` 白空格控制，避免宏輸出中的 `\n` 汙染 `class=""` 屬性
- Jinja2 環境已設置 `trim_blocks=True` 和 `lstrip_blocks=True`
- 五行顏色宏：`render_wuxing_class(wx)`（天干背景色）和 `render_wuxing_text_class(wx)`（地支文字色）

## 格局判斷規則

### 定格優先級
1. 天干官殺 → 月令藏干透干 → 月令主氣
2. 官殺混雜：陰日干以七殺定格，陽日干官殺混雜破格
3. 辰戌丑未土必須透干才能以土定格

### 四吉神與四凶神
- **吉神**（順用成格）：正官、正印、偏印、正財、偏財、食神
- **凶神**（逆用成格）：七殺、傷官、比肩、劫財

### 根氣被剋判斷
- **吉神**：單一根氣被剋 → 格局失敗
- **吉神**：多根氣單一被剋 → 不判斷失敗
- **凶神**：單一根氣被剋 → 損格

## 旺衰判斷（根氣強度）

| 位置 | 強度 |
|------|------|
| 月支 | 4 |
| 時支 | 3 |
| 日支 | 2 |
| 年支 | 1 |

**總根氣：** ≥8 極旺 | 5-7 旺 | 3-4 中 | 1-2 微 | 0 虛浮

## 先天病源優先級

1. 忌神所在干支
2. 蓋頭截腳干支
3. 相神/喜神被沖地支
4. 五行過旺（≥4 個）
5. 五行缺失

## BaZiCalculator 主要屬性

```python
calculator.ba_zi              # 四柱（空格分隔字符串）
calculator.cang_gan           # 藏干
calculator.wang_shuai         # 旺衰
calculator.shi_shen           # 十神
calculator.ge_ju              # 格局判斷
calculator.integrated_analysis # 整合分析（含十神組合斷語、干支生剋斷語、五行斷語、格局斷語）
calculator.dayun_pan_duan     # 大運判斷
calculator.liunian_pan_duan   # 流年判斷
calculator.yi_zhu             # 一柱論命
calculator.ganzhi_xiang       # 干支象法
calculator.liang_ge_bing_cun  # 兩格並存
calculator.yuan_ju_ge_ju      # 原局格局
calculator.suiyun_ge_ju       # 歲運格局
calculator.bazi_gua           # 八字卦象
calculator.yi_hua_jie_mu      # 移花接木
calculator.fan_sheng_ke       # 反生為剋/反剋為生
calculator.get_liuyue(dayun_gz, liunian_gz)  # 流月分析（12 個月，含格局影響）
```

## 新增分析功能（2026-05）

### 根氣映射修正
- `wangshuai.py` 和 `geju.py` 使用 `TIAN_GAN_DE_GEN` 常數取代簡化的 `wuxing_to_zhi`
- 例：甲根在寅卯辰未亥，不再只取寅卯

### 降格概念（geju.py）
- 格局成敗三分：成格 / 降格 / 破格
- 吉神單根被剋但有印星化解 → 降格
- 凶神單根被剋但有食傷/印星制化 → 降格

### 反生為剋 / 反剋為生（ganzhi.py）
- `calculate_fan_sheng_ke(ba_zi)` 檢查所有 6 組天干對
- 反生為剋：目標根氣 ≥3 或 ≥2 且得令
- 反剋為生：目標根氣 =0 且不得令

### 神煞增強（shensha.py）
- 新增：孤鸞煞、陰陽差錯、八專（淫慾煞）、九醜（妨害煞）
- 桃花統一計算，區分墻內（年月）/墻外（日時）
- `calculate_shensha(ba_zi, gender)` 接受性別參數

### 十二長生關鍵階段（changsheng.py）
- 7 個關鍵階段標記：長生、臨官、帝旺、墓、絕、沐浴、死
- 輸出含「是否關鍵階段」和「關鍵階段」列表

### 疾病預測增強（gongwei.py）
- 藏干入墓：檢查藏干五行對應墓庫是否在四柱
- 地支沖剋臟腑：六沖配對映射臟腑
- 日主長生階段：病/死/墓標記體質弱點

### 三刑跨歲運（relations.py + dayun_liunian.py）
- `check_san_xing_suiyun(natal_zhi, suiyun_zhi)` 檢查丑戌未/寅巳申/子卯/自刑
- 大運和流年判斷中自動調用

### 斷語數據庫整合（integrated.py）
- 十神組合斷語改為數據驅動（`SHISHEN_COMBINATION_DUAN_YU`）
- 新增輸出鍵：干支生剋斷語、五行斷語、格局斷語

### 流月分析（dayun_liunian.py）
- `calculate_liuyue_pan_duan()` 使用五虎遁計算 12 個月天干
- 每月含格局影響、吉凶、用神/喜神/忌神到位分析
- API 路由已整合，前端可展示

### 大運格局轉化（geju.py + dayun_liunian.py）
- `calculate_dayun_geju_transformation()` 分析大運對格局的影響
- 類型：用神到位/相神到位/忌神到位/沖動/成格遇忌神/破格遇救神
- 結果附在 `calculate_dayun_yingdong()` 返回值中

## 配置系統

`config/settings.py` 使用 pydantic-settings，支持環境變量覆蓋：
- 應用前綴：`BAZI_`（如 `BAZI_DEBUG=true`）
- 格局配置前綴：`GEJU_`（如 `GEJU_ENABLE_BING_YUAN=false`）

## 依賴

- `sxtwl` - 農曆/節氣計算（C 擴展）
- `fastapi`/`uvicorn` - Web 框架
- `jinja2` - HTML 模板
- `mcp` - MCP 服務器
- `pydantic-settings` - 配置管理
- `python-docx` - 文檔導出

## MCP 配置

```json
{
  "mcpServers": {
    "bazi": {
      "url": "http://localhost:8001/mcp"
    }
  }
}
```
