# Kepware Tag 月報生成器

自動從 DuckDB 讀取 Kepware tag 資料，生成適合匯入 Power BI 的 Excel 月報。

## 📋 功能特色

- ✅ 自動統計 Tag 使用狀況
- ✅ 多維度分析（廠區、部門、Driver、專案等）
- ✅ 處理資料不完整的情況（顯示「未分類」）
- ✅ 計算資料完成度
- ✅ 生成 Excel 多工作表報表
- ✅ 適合匯入 Power BI 進行視覺化

## 📊 報表內容

生成的 Excel 包含以下工作表：

| 工作表名稱 | 內容 |
|-----------|------|
| 總覽 | Tag 總數、本月新增、專案數、資料完成度 |
| 廠區分布 | 各廠區的 Tag 數量、部門數、負責人數 |
| 部門分布 | 各部門在各廠區的 Tag 分布 |
| Driver統計 | 各 Driver 類型的使用量與百分比 |
| 資料類型統計 | 各資料類型的分布 |
| 專案統計 | 各專案的 Tag 數量與時間範圍 |
| 負責人統計 | 各負責人管理的 Tag 數量 |
| 新增趨勢 | 過去 12 個月的 Tag 新增趨勢 |

## 🚀 使用方式

### 1. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

需要的套件：
- duckdb
- pandas
- openpyxl
- xlsxwriter

### 2. 設定資料庫路徑

複製設定檔範本：
```bash
cp config.json.example config.json
```

編輯 `config.json`，修改資料庫路徑：
```json
{
  "database": {
    "path": "D:/您的路徑/tags.duckdb"
  },
  "report": {
    "output_dir": "./reports",
    "file_prefix": "Kepware月報"
  }
}
```

### 3. 執行報表生成

```bash
python kepware_monthly_report.py
```

### 4. 查看報表

報表會自動儲存在 `reports/` 資料夾中，檔名格式：`Kepware月報_YYYYMM.xlsx`

## 📁 專案結構

```
kepware_reports/
├── config.json.example          # 設定檔範本
├── config.json                  # 實際設定（請自行建立）
├── kepware_monthly_report.py   # 主程式
├── requirements.txt             # Python 套件清單
├── reports/                     # 報表輸出資料夾
│   └── Kepware月報_202602.xlsx
└── README.md                    # 本說明文件
```

## 💡 Power BI 匯入建議

1. **開啟 Power BI Desktop**
2. **取得資料** → **Excel 活頁簿**
3. **選擇生成的報表檔案**
4. **勾選需要的工作表** （建議全選）
5. **載入資料**

建議在 Power BI 中建立的視覺化：
- 📊 Tag 總數卡片
- 📈 月增長趨勢折線圖
- 🏭 廠區分布橫條圖
- 🔧 Driver 類型圓餅圖
- 📁 專案排名表

## ⚠️ 注意事項

### 資料完成度
- 目前資料完成度約 75%
- 空值欄位會顯示為「未分類」
- 「總覽」工作表會顯示各欄位的完成度百分比

### 資料庫權限
- 程式使用唯讀模式連接資料庫
- 不會修改任何資料
- 安全無虞

### 資安提醒
- `config.json` 已加入 `.gitignore`，不會被上傳
- 請確保資料庫路徑不包含機敏資訊
- 生成的報表請確認資料已去識別化後再分享

## 🔧 進階設定

### 自訂報表輸出位置

修改 `config.json` 中的 `output_dir`：
```json
{
  "report": {
    "output_dir": "D:/Reports/Kepware",
    "file_prefix": "月報"
  }
}
```

### 修改報表內容

如需調整統計內容，可直接編輯 `kepware_monthly_report.py` 中的 SQL 查詢語句。

## 📞 問題排除

### 找不到 config.json
```
❌ 找不到 config.json！
```
**解決方式**：複製 `config.json.example` 為 `config.json`

### 資料庫連接失敗
```
❌ 發生錯誤: IO Error: Cannot open file...
```
**解決方式**：檢查 `config.json` 中的資料庫路徑是否正確

### 套件未安裝
```
ModuleNotFoundError: No module named 'duckdb'
```
**解決方式**：執行 `pip install -r requirements.txt`

## 📝 更新紀錄

- **v1.0** (2026-02-04)
  - 初始版本
  - 支援基本統計與 Excel 輸出
  - 處理資料不完整情況
  - 適配 Power BI 匯入

---

*建立日期：2026-02-04*
