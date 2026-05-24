# 使用者背景與標準

## 使用者背景

- **非 IT 背景**的廠務/SCADA 系統分析師
- 請用**非技術性的白話說明**，避免 IT 術語
- 介紹新概念時，先用**生活化的比喻**解釋
- 工作環境有網路限制：
  - 公司封鎖 Claude，只能在家使用 Claude Code
  - 公司資料無法攜出，在家只能進行程式開發
  - 在家開發 → Git 版本控制 → 帶回公司部署

---

## 專業背景

廠務系統數據分析與圖控應用管理，專注於工廠設施管理系統的數據處理、分析與視覺化應用。

**核心專業領域：**
- **廠務系統管理**：設施設備監控、能源管理系統 (EMS)、建築自動化系統 (BAS)
- **數據分析**：設備運行數據收集與分析、能耗分析、預測性維護、KPI 追蹤
- **圖控應用 (SCADA/HMI)**：人機介面設計、即時監控系統、報表設計

---

## Kepware 相關通用知識

- 使用**關聯式資料庫**（PostgreSQL / Oracle / MSSQL）管理所有 Kepware tag 點位
- Tag 資料涵蓋：廠區 (site)、樓層 (floor)、部門 (department)、負責人 (owner)、Driver 類型
- 透過 tag_projects 關聯表管理 tag 與專案的對應關係
- 報表需求：**Excel 格式**為主（可匯入 Power BI 視覺化）

---

## 開發環境

- **主要語言**：Python
- **資料庫**：PostgreSQL / Oracle / MSSQL（依專案而定）
- **報表工具**：pandas + xlsxwriter → Excel → Power BI
- **資料庫連線**：SQLAlchemy 或原生驅動（psycopg2, cx_Oracle, pymssql）

---

## 資安原則

⚠️ **重要提醒**：
- 所有程式碼和資料都已經過**去識別化處理**
- **不在程式碼中包含**公司網域、IP 位址等機敏資訊
- 使用 `.env` 或 `config.json` 管理連線資訊，**不提交到 Git**
- 測試資料使用假資料或已脫敏的資料

---

## 專案設計標準

### 資料庫連線服務標準

**必要功能：**
- 支援 PostgreSQL、Oracle、MSSQL 多種資料庫
- 使用連線池管理（SQLAlchemy 或原生）
- 從 config.json 或 .env 讀取連線資訊
- 自動重連機制（處理斷線）
- 交易管理（commit/rollback）

**配置管理：**
- 不在程式碼中寫死連線字串
- 提供 `config.json.example` 範本（去識別化）
- 支援多環境配置（dev/prod）

**錯誤處理：**
- 捕捉資料庫連線錯誤
- 記錄 SQL 執行日誌
- 逾時控制（避免長時間等待）

---

### Email 派報服務標準

參考檔案：`ase_email_service.py`

**必要功能：**
- 支援 HTML 格式郵件
- 支援多收件人（To、CC）
- 設定逾時控制（建議 30 秒）
- 完整的錯誤處理與日誌記錄
- 使用 context manager 確保連線正確關閉

**配置管理：**
- SMTP 伺服器、連接埠、寄件者等資訊
- 從 config.json 或 .env 讀取，不寫死在程式中

---

### Webhook 推播服務標準

參考檔案：`webhook_service.py`

**必要功能：**
- 支援模板渲染（`{{$variable}}` 語法）
- 連線逾時與讀取逾時分開控制
- HTTP 狀態碼 + API 回應雙重驗證
- 資料庫記錄請求/回應（用於追蹤）
- 提供 `test_send()` 方法驗證配置

**安全考量：**
- SSL 驗證控制（公司內部 API 可能用自簽憑證）
- 支援 proxy 設定
- 敏感資訊（token）從設定檔讀取

**錯誤處理：**
- 區分連線錯誤、逾時、HTTP 錯誤
- 詳細的診斷日誌
- 支援恢復狀態通知

---

### 通用設計原則

1. **配置管理**
   - 使用 config.json 或 .env 管理所有設定
   - 提供 config.json.example 範本
   - 敏感資訊不提交到 Git

2. **錯誤處理**
   - 使用 try-except 捕捉異常
   - logging 模組記錄所有重要操作
   - 提供明確的錯誤訊息

3. **測試支援**
   - 提供 test_*() 方法驗證配置
   - 回傳詳細的診斷資訊

4. **資料庫記錄**
   - 記錄外部通訊的請求/回應
   - 用於追蹤、除錯、審計

5. **逾時控制**
   - 設定合理的逾時時間
   - 避免程式長時間卡住

---

## Python/Excel 注意事項

**常見錯誤避免：**
- ❌ 不要使用 `writer.sheets[name].table.columns`（此屬性不存在）
- ✅ 應該用 `sheets_data` 字典儲存 DataFrame，再用 DataFrame 計算欄寬

**最佳實踐：**
- 執行腳本前先用 `python -m py_compile` 檢查語法
- 使用 xlsxwriter 引擎以支援格式設定
- 自動調整欄寬時，限制最大寬度（建議 50）

---

---

# Kepware Tag 管理系統 - 月報專案

## 專案說明

從 DuckDB 讀取 Kepware tag 資料，自動生成 Excel 月報，適合匯入 Power BI 進行視覺化。

## 資料庫結構

### tags 主表
| 欄位 | 說明 |
|------|------|
| tag_id | 主鍵 |
| tagname | Tag 名稱（唯一） |
| description | 描述 |
| node_name | 節點名稱 |
| driver_type | 驅動類型 |
| address | 位址 |
| tabname | 分頁名稱 |
| zone | 區域 |
| bu | 事業單位 |
| site | 廠區 |
| floor | 樓層 |
| owner | 負責人 |
| department | 部門 |
| data_type | 資料類型 |
| created_date | 建立日期 |
| updated_date | 更新日期 |

### projects 專案表
| 欄位 | 說明 |
|------|------|
| project_id | 主鍵 |
| project_name | 專案名稱（唯一） |
| created_date | 建立日期 |

### tag_projects 關聯表
| 欄位 | 說明 |
|------|------|
| tag_id | 外鍵 → tags |
| project_id | 外鍵 → projects |
| date | Tag 加入專案的日期 |

## 專案結構

```
kepware_reports/
├── kepware_monthly_report.py   # 主程式：生成 Excel 月報
├── config.json.example         # 設定檔範本（實際設定不上傳 Git）
├── requirements.txt            # Python 套件需求
├── README.md                   # 使用說明
└── reports/                    # 報表輸出目錄（不上傳 Git）
```

## 報表內容（Excel 8 個 Sheet）

1. **總覽**：Tag 總數、本月新增、專案總數、部門數、資料完成度
2. **廠區分布**：各 site 的 Tag 數量
3. **部門分布**：各 department 的 Tag 數量
4. **Driver 統計**：各 driver_type 的分布與百分比
5. **資料類型統計**：各 data_type 的分布
6. **專案統計**：各專案的 Tag 數量與加入日期
7. **負責人統計**：各 owner 管理的 Tag 數量
8. **新增趨勢**：每月新增 Tag 數量（最近 12 個月）

## 注意事項

- 資料現在完成度約 75%，空值欄位顯示為「未分類」
- config.json 放置實際的 DuckDB 路徑，不提交到 Git
- 報表輸出到 `reports/` 目錄，不提交到 Git

*最後更新：2026-05-19*
