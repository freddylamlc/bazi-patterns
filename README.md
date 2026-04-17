# 八字計算器 - Python與iOS雙版本

本項目包含兩個版本的八字計算器應用：

## 項目結構

```
├── README.md                    # 當前文件 - 項目總覽
├── CLAUDE.md                   # 項目說明文檔
├── requirements.txt            # Python依賴文件
├── app.py                     # Python Web應用入口
├── mcp_server.py              # MCP服務器
├── bazi/                      # Python版八字計算核心模塊
├── config/                    # 配置模塊
├── templates/                 # Web界面模板
├── static/                    # 靜態資源
├── api/                       # API模塊
├── tests/                     # 測試文件
├── region.json                # 城市經緯度數據
├── query_longitude.py         # 城市經度查詢工具
├── ios_version/               # iOS版本目錄
│   └── BaZiCalculator/        # iOS版八字計算器完整項目
│       ├── Sources/
│       │   ├── App/
│       │   ├── Core/
│       │   ├── Models/
│       │   ├── Services/
│       │   └── UI/
│       ├── Info.plist
│       └── README.md
└── ...
```

## Python版本 (主版本)

### 功能特色
- Web界面，基於FastAPI
- 完整的八字計算功能（四柱、藏干、旺衰、十神、格局等）
- 真太陽時校正
- 格局分析與十神判斷
- 大運流年推算
- 神煞分析
- MCP服務器支持

### 運行方式
```bash
# 安裝依賴
pip install -r requirements.txt

# 運行Web應用
python app.py

# 訪問：http://127.0.0.1:8080
```

## iOS版本

### 功能特色
- 原生iOS應用，基於SwiftUI
- 完整的八字計算功能
- 完全離線運行，無需服務器
- 精確的真太陽時計算
- 直觀的用戶界面
- 歷史記錄和數據持久化

### 開發環境
- 需要在macOS上使用Xcode打開
- 適用於iOS 15.0及以上版本
- 支持iPhone和iPad

### 項目結構
```
BaZiCalculator/
├── Sources/
│   ├── App/           # 應用入口
│   ├── Core/          # 核心計算邏輯
│   ├── Models/        # 數據模型
│   ├── Services/      # 服務層（位置、數據持久化等）
│   └── UI/            # 用戶界面組件
├── Info.plist         # 應用配置文件
└── README.md          # 詳細說明文檔
```

## 技術對比

| 方面 | Python版 | iOS版 |
|------|----------|-------|
| 運行環境 | Web瀏覽器 | iOS設備 |
| 服務器依賴 | 需要 | 無需 |
| 離線功能 | 需要本地服務 | 完全離線 |
| 用戶體驗 | 網頁界面 | 原生App |
| 平台支持 | 任意設備 | 僅iOS |
| 數據存儲 | 服務器/本地 | 設備本地 |

## 使用場景

- **Python版**：適合開發調試、服務器部署、跨平台使用
- **iOS版**：適合移動端使用、離線計算、原生體驗

兩個版本都實現了相同的八字計算算法，確保計算結果的一致性。
