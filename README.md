# 八字計算器 (BaZi Calculator)

中式八字（Four Pillars of Destiny）計算器，提供完整的八字排盤、格局分析、大運流年推算功能。

- Web 界面（FastAPI）
- MCP 服務器（支持 AI Agent 集成）
- Docker 部署支持

## 功能特色

### 核心計算
- 四柱排盤（年柱、月柱、日柱、時柱）
- 地支藏干
- 真太陽時校正（根據城市經緯度）
- 旺衰判斷（根氣強度分析）
- 十神計算
- 神煞計算
- 十二長生
- 天干五合、地支關係
- 大運計算（含移花接木）
- 流年推算

### 分析模塊
- 格局判斷（支持兩格並存）
- 宮位分析
- 先天病源
- 大運流年斷語
- 整合分析（格局為核心）
- 一柱論命（60 甲子斷語）
- 干支象法（臟腑、意象、疾病預測）
- 八字卦象

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 運行 Web 界面

```bash
python app.py
# 訪問：http://127.0.0.1:8080
```

### 運行 MCP 服務器

```bash
python mcp_server.py
# 訪問：http://localhost:8001/mcp
```

### Docker 部署

```bash
docker compose up --build
```

## 項目結構

```
├── app.py                     # Web 應用入口（FastAPI）
├── mcp_server.py              # MCP 服務器
├── requirements.txt           # Python 依賴
├── Dockerfile                 # Docker 鏡像
├── docker-compose.yml         # Docker Compose
├── smithery.yaml              # Smithery MCP 配置
├── region.json                # 城市經緯度數據
├── bazi/                      # 核心計算模塊
│   ├── core/                  # 主類與工具
│   │   ├── calculator.py      # BaZiCalculator 主類
│   │   ├── constants.py       # 天干地支、五行、神煞常數
│   │   └── utils.py           # 真太陽時、農曆轉換
│   ├── calculations/          # 計算模塊
│   │   ├── pillar.py          # 四柱計算
│   │   ├── canggan.py         # 地支藏干
│   │   ├── relations.py       # 天干五合、地支關係
│   │   ├── wangshuai.py       # 旺衰判斷
│   │   ├── changsheng.py      # 十二長生
│   │   ├── shishen.py         # 十神計算
│   │   ├── shensha.py         # 神煞計算
│   │   ├── ganzhi.py          # 干支生剋
│   │   ├── jieqi.py           # 節氣信息
│   │   ├── dayun.py           # 大運計算（含移花接木）
│   │   └── liushijiazi.py     # 六十甲子計算
│   ├── analysis/              # 分析模塊
│   │   ├── geju.py            # 格局判斷（含兩格並存）
│   │   ├── gongwei.py         # 宮位分析
│   │   ├── bingyuan.py        # 先天病源
│   │   ├── dayun_liunian.py   # 大運流年判斷
│   │   ├── integrated.py      # 整合分析（格局為核心）
│   │   ├── yizhu.py           # 一柱論命（60 甲子斷語）
│   │   ├── ganzhi_xiang.py    # 干支象法（臟腑、意象、疾病）
│   │   ├── duanyu_db.py       # 斷語數據庫
│   │   └── bazi_gua.py        # 八字卦象
│   ├── models/                # 數據模型
│   │   ├── bazi_result.py
│   │   └── birth_info.py
│   ├── exceptions/            # 異常定義
│   └── validators/            # 輸入驗證
├── config/                    # 配置模塊
│   └── settings.py
├── api/                       # API 路由
│   └── routes.py
├── templates/                 # Web 模板
│   ├── index.html
│   └── result.html
├── static/                    # 靜態資源
│   ├── css/style.css
│   └── js/app.js
└── tests/                     # 測試
    ├── test_config.py
    ├── test_constants.py
    ├── test_exceptions.py
    ├── test_integration.py
    ├── test_new_features.py
    ├── test_relations.py
    └── test_validators.py
```

## MCP 集成

將八字計算器作為 MCP 服務器接入 AI Agent：

```json
{
  "mcpServers": {
    "bazi": {
      "url": "http://localhost:8001/mcp"
    }
  }
}
```

## 測試

```bash
pytest tests/ -v
```

## 核心算法

### 真太陽時

```
出生時間 + (城市經度 - 120°) × 4 分鐘
```

### 大運計算

- 陽男陰女順排，陰男陽女逆排
- 起運年齡 = 節氣天數 ÷ 3

### 流年計算

流年從出生年份連續順推，不每個大運重新計算：

```python
ln_gan_idx = (year_gan_idx + liunian_age) % 10
ln_zhi_idx = (year_zhi_idx + liunian_age) % 12
```

### 格局判斷規則

1. 天干官殺 → 月令藏干透干 → 月令主氣
2. 官殺混雜：陰日干以七殺定格，陽日干官殺混雜破格
3. 辰戌丑未土必須透干才能以土定格

### 旺衰判斷（根氣強度）

| 位置 | 強度 |
|------|------|
| 月支 | 4 |
| 時支 | 3 |
| 日支 | 2 |
| 年支 | 1 |

**總根氣：** ≥8 極旺 | 5-7 旺 | 3-4 中 | 1-2 微 | 0 虛浮
