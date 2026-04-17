# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## 項目概述

中式八字（Four Pillars of Destiny）計算器，包含：
- Web 界面（FastAPI）
- MCP 服務器
- 完整八字排盤功能

## 常用命令

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行 Web 界面
python app.py  # 訪問：http://127.0.0.1:8080

# 運行 MCP 服務器
python mcp_server.py  # 訪問：http://localhost:8001/mcp

# 測試
pytest tests/ -v
```

## 架構

```
bazi/
├── core/
│   ├── calculator.py    # 主類
│   ├── constants.py     # 天干地支、五行、神煞常數
│   └── utils.py         # 真太陽時、農曆轉換
├── calculations/        # 計算模塊
│   ├── pillar.py        # 四柱計算
│   ├── canggan.py       # 地支藏干
│   ├── relations.py     # 天干五合、地支關係
│   ├── wangshuai.py     # 旺衰判斷
│   ├── changsheng.py    # 十二長生
│   ├── shishen.py       # 十神計算
│   ├── shensha.py       # 神煞計算
│   ├── ganzhi.py        # 干支生剋
│   ├── jieqi.py         # 節氣信息
│   └── dayun.py         # 大運計算（含移花接木）
├── analysis/            # 分析模塊
│   ├── geju.py          # 格局判斷（含兩格並存）
│   ├── gongwei.py       # 宮位分析
│   ├── bingyuan.py      # 先天病源
│   ├── dayun_liunian.py # 大運流年判斷
│   ├── integrated.py    # 整合分析（格局為核心）
│   ├── yizhu.py         # 一柱論命（60 甲子斷語）
│   ├── ganzhi_xiang.py  # 干支象法（臟腑、意象、疾病）
│   └── duanyu_db.py     # 斷語數據庫
└── models/              # 數據模型
```

## 核心算法

### 真太陽時
```python
出生時間 + (城市經度 - 120°) × 4 分鐘
```

### 大運計算
- 陽男陰女順排，陰男陽女逆排
- 起運年齡 = 節氣天數 ÷ 3

### 流年計算
```python
# 流年從出生年份連續順推，不每個大運重新計算
ln_gan_idx = (year_gan_idx + liunian_age) % 10
ln_zhi_idx = (year_zhi_idx + liunian_age) % 12
```

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

## 新增功能（2026-04-06）

- **一柱論命**（`yizhu.py`）：60 組甲子日柱斷語
- **干支象法**（`ganzhi_xiang.py`）：臟腑、意象、疾病預測
- **斷語庫**（`duanyu_db.py`）：十神事件斷語
- **歲運進階**（`dayun.py`、`geju.py`）：移花接木、兩格並存

## BaZiCalculator 主要屬性

```python
calculator.ba_zi              # 四柱
calculator.cang_gan           # 藏干
calculator.wang_shuai         # 旺衰
calculator.shi_shen           # 十神
calculator.ge_ju              # 格局判斷
calculator.integrated_analysis # 整合分析
calculator.dayun_pan_duan     # 大運判斷
calculator.liunian_pan_duan   # 流年判斷
calculator.yi_zhu             # 一柱論命
calculator.ganzhi_xiang       # 干支象法
calculator.liang_ge_bing_cun  # 兩格並存
calculator.yuan_ju_ge_ju      # 原局格局
calculator.suiyun_ge_ju       # 歲運格局
```

## 依賴

- `sxtwl` - 農曆/節氣計算
- `fastapi`/`uvicorn` - Web 框架
- `mcp` - MCP 服務器
- `pydantic-settings` - 配置管理

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
