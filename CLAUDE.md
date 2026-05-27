# CLAUDE.md

中式八字計算器 — FastAPI Web + MCP Server + SQLite CRM

## 常用命令

```bash
python app.py              # Web: http://127.0.0.1:8080
python mcp_server.py       # MCP: http://localhost:8001/mcp
docker compose up --build
pytest tests/ -v --cov=bazi --cov-report=term-missing
```

## 數據流

```
表單/MCP → api/routes.py 或 mcp_server.py
  → BaZiCalculator (bazi/core/calculator.py)
    → calculations/ (四柱、藏干、旺衰、十神、神煞、大運)
    → analysis/ (格局、宮位、病源、整合分析、流月、歲運)
  → result.html 或 JSON
```

## 目錄結構

```
bazi/core/           calculator.py (主類), constants.py, utils.py
bazi/calculations/   pillar, canggan, relations, wangshuai, changsheng,
                     shishen, shensha, ganzhi, jieqi, dayun, liushijiazi
bazi/analysis/       geju, gongwei, bingyuan, dayun_liunian, integrated,
                     yizhu, ganzhi_xiang, duanyu_db, bazi_gua
bazi/models/         Pydantic 數據模型
bazi/validators/     輸入驗證
bazi/db.py           SQLite CRM (客戶命盤 + 批注)
config/settings.py   pydantic-settings (前綴 BAZI_ / GEJU_)
api/routes.py        FastAPI 路由 + CRM API
static/js/app.js     前端：大運流年流月選擇、五行顏色更新
templates/           result.html, macros.html
```

**入口差異：** `app.py` = Web (Jinja2 + 靜態文件 + SQLite)；`mcp_server.py` = MCP JSON

## 核心算法

- **真太陽時：** 出生時間 + (城市經度 - 120°) × 4 分鐘
- **大運：** 陽男陰女順排，陰男陽女逆排；起運年齡 = 節氣天數 ÷ 3
- **流年：** 從出生年份連續順推 `(year_idx + age) % 10/12`
- **年柱：** 立春前出生者年柱屬前一年；`_get_chinese_year_from_pillar()` 以甲子=1984 為基準反推
- **流月：** 五虎遁計算每月天干（甲己年丙寅起，乙庚年戊寅起…）

## 格局規則

**定格優先級：** 天干官殺 → 月令藏干透干 → 月令主氣。辰戌丑未土必須透干。

**吉神**（順用）：正官、正印、偏印、正財、偏財、食神
**凶神**（逆用）：七殺、傷官、比肩、劫財

**根氣被剋：** 吉神單根被剋→失敗；多根單一被剋→不失敗。凶神單根被剋→損格。
**降格：** 根氣被剋但有制化（印星/食傷）→ 降格而非破格。

**旺衰強度：** 月支=4, 時支=3, 日支=2, 年支=1。≥8極旺, 5-7旺, 3-4中, 1-2微, 0虛浮。
**根氣映射：** 使用 `TIAN_GAN_DE_GEN`（如甲根在寅卯辰未亥）。

## BaZiCalculator 屬性

```python
.ba_zi, .cang_gan, .wang_shuai, .shi_shen, .ge_ju
.integrated_analysis    # 十神組合/干支生剋/五行/格局斷語
.dayun_pan_duan, .liunian_pan_duan
.yuan_ju_ge_ju, .suiyun_ge_ju  # 原局/歲運格局
.yi_zhu, .ganzhi_xiang, .bazi_gua, .yi_hua_jie_mu
.fan_sheng_ke           # 反生為剋/反剋為生
.get_liuyue(dayun_gz, liunian_gz)  # 流月分析
```

## 分析功能速覽

| 模塊 | 功能 |
|------|------|
| shensha.py | 神煞（含孤鸞、陰陽差錯、八專、九醜）；桃花分墻內/墻外 |
| changsheng.py | 十二長生 7 個關鍵階段標記 |
| ganzhi.py | 反生為剋/反剋為生檢測 |
| geju.py | 降格概念；大運格局轉化分析 |
| gongwei.py | 疾病預測（藏干入墓、沖剋臟腑、長生階段） |
| relations.py | 三刑跨歲運引動 |
| dayun_liunian.py | 流月分析（五虎遁 + 格局影響）；大運引動含格局轉化 |
| integrated.py | 數據驅動斷語（duanyu_db） |
| yizhu.py | 旬中六親分析 |

## 前端注意

- 頁面載入自動跳轉到當前年份對應的大運/流年（`birthYear` 用年柱反推）
- 點擊大運/流年/流月時，排盤天干地支需同步更新五行顏色
- Jinja2 必須用 `{%- ... -%}` 控制空白；環境已設 `trim_blocks=True`, `lstrip_blocks=True`

## 先天病源優先級

1. 忌神所在干支 2. 蓋頭截腳 3. 相神/喜神被沖 4. 五行過旺(≥4) 5. 五行缺失

## MCP 配置

```json
{ "mcpServers": { "bazi": { "url": "http://localhost:8001/mcp" } } }
```
