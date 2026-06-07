# Kepware 專案設定範本

這個檔案包含所有在新專案中需要建立的檔案內容。在新的雲端專案中，複製貼上這些內容即可。

---

## 📁 檔案 1：.gitignore

**位置：** 專案根目錄 `.gitignore`

```gitignore
# ===== Python 相關 =====
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
.venv/
env/
ENV/
.Python
pip-log.txt
.ipynb_checkpoints/
.coverage
.pytest_cache/

# ===== 敏感資料保護 =====
.env
.env.local
*.env
config.json
config.local.json
credentials.json
secrets.json

# ===== Claude Code 個人設定 =====
.claude/settings.local.json
.claude/*.local.*
CLAUDE.local.md

# ===== 資料庫檔案 =====
*.db
*.sqlite
*.sqlite3
*.duckdb

# ===== Kepware 報表輸出 =====
kepware_reports/reports/
kepware_reports/*.xlsx
kepware_reports/*.xls
reports/
*.xlsx
*.xls

# ===== 常見暫存檔案 =====
*.log
*.tmp
*.bak
*.swp
*~
.DS_Store
Thumbs.db
desktop.ini

# ===== IDE 與編輯器 =====
.vscode/
.idea/
*.sublime-*
.spyderproject
.spyproject
```

---

## 📁 檔案 2：.claude/settings.json

**位置：** `.claude/settings.json`

**操作：** 建立 `.claude` 目錄，然後建立此檔案

```json
{
  "description": "Kepware 專案標準設定",

  "permissions": {
    "allow": [
      "Read(*)",
      "Glob(*)",
      "Grep(*)",
      "Bash(ls *)",
      "Bash(pwd)",
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(python --version)",
      "Bash(pip list)",
      "Bash(which python*)"
    ]
  },

  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "description": "保護重要設定檔不被修改",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$TOOL_INPUT\" | jq -r '.tool_input.file_path // empty' | grep -qE '(\\.env$|credentials|secrets|config\\.json$)' && echo '⚠️  警告：這是敏感設定檔，請確認是否要修改' && exit 1 || exit 0"
          }
        ]
      }
    ],

    "Stop": [
      {
        "matcher": "",
        "description": "完成任務時提醒檢查並提交",
        "hooks": [
          {
            "type": "command",
            "command": "git status --short | grep -q . && echo '\\n📝 提醒：有檔案變更，記得檢查並提交到 Git' || exit 0"
          }
        ]
      }
    ]
  }
}
```

---

## 📁 檔案 3：.claude/skills/add-personal-context/SKILL.md

**位置：** `.claude/skills/add-personal-context/SKILL.md`

**操作：** 建立目錄結構，然後建立此檔案

```markdown
---
name: add-personal-context
description: 在專案的 claude.md 加入個人背景、設計標準和通用知識
---

在現有專案的 claude.md 中加入使用者的個人背景和標準設定。

## 要加入的內容

在專案 claude.md 的**最前面**加入以下章節：

---

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

## 執行步驟

1. 讀取專案根目錄的 `claude.md`（如果不存在則提示使用者先執行 `/init`）
2. 將上述「使用者背景與標準」內容加在檔案最前面
3. 用清楚的分隔線區隔通用背景與專案特定內容
4. 儲存更新後的 claude.md
5. 向使用者顯示摘要：
   - ✅ 已加入的章節列表
   - 📝 提示：這些標準會在所有使用此專案的 session 中自動套用

**重要提醒：**
- 此 Skill 會**保留專案的原有內容**
- 只在檔案最前面加入通用背景資訊
- 如果 claude.md 已包含部分通用資訊，會智能合併而非重複
```

---

## 🎯 在新專案使用這些範本

### **標準流程**（每個新專案都這樣做）

```
1. 開啟新專案的 Claude Code session

2. 告訴 Claude：
   「請幫我建立以下檔案：
   
   檔案 1：.gitignore
   [複製貼上 SETUP-TEMPLATE.md 中的 .gitignore 內容]
   
   檔案 2：.claude/settings.json
   [複製貼上 SETUP-TEMPLATE.md 中的 settings.json 內容]
   
   檔案 3：.claude/skills/add-personal-context/SKILL.md
   [複製貼上 SETUP-TEMPLATE.md 中的 SKILL.md 內容]」

3. 建立完成後執行：
   /add-personal-context
   
4. 補充專案特定的資訊（資料庫結構、報表需求等）

5. 提交到 Git
```

---

## 💡 更簡化的方式

您也可以把這個 SETUP-TEMPLATE.md 放到一個公開的 GitHub Gist 或 repo，
新專案只需要：

```
「請從 [Gist URL] 讀取設定範本並建立所有檔案」
```

---

**建議：** 把這個 SETUP-TEMPLATE.md 加到您的書籤或筆記中，
每次新專案就能快速複製貼上！
