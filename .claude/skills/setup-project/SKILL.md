---
name: setup-project
description: 完整的 Kepware 專案初始化 - 一鍵設定所有標準檔案和配置
---

為新的 Kepware 相關專案建立完整的開發環境設定，包括所有標準檔案、配置和 Skills。

## 自動建立的內容

### 1. .gitignore（Git 忽略規則）
- Python 相關（__pycache__, *.pyc, venv/）
- 資料庫檔案（*.db, *.sqlite, *.duckdb）
- Kepware 報表輸出（reports/, *.xlsx）
- 敏感設定（.env, config.json, credentials.json）
- IDE 設定（.vscode/, .idea/）

### 2. .claude/settings.json（Claude Code 設定）
- 權限設定：自動允許常用操作（Read, Grep, Glob, git 指令）
- PreToolUse Hook：保護敏感設定檔
- Stop Hook：提醒 Git 提交

### 3. WORKFLOW.md（工作流程檢查清單）
- 開始工作前的檢查項目
- 開發過程中的注意事項
- 完成工作後的檢查清單
- 回公司前的準備事項
- 常見問題處理

### 4. .claude/skills/add-personal-context/（自訂 Skill）
- 複製 add-personal-context Skill 到新專案
- 確保新專案也能使用 /add-personal-context

### 5. claude.md（專案說明 + 個人背景）
- 自動執行 /add-personal-context
- 包含使用者背景、專業背景、設計標準
- 預留專案特定說明的空間

## 執行步驟

### 步驟 1：檢查環境
1. 確認當前目錄是新專案的根目錄
2. 檢查是否已有 Git 初始化（如沒有則建議初始化）
3. 提醒使用者這會建立/覆蓋多個檔案

### 步驟 2：建立 .gitignore
使用標準的 Python + Kepware 專案範本：

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

### 步驟 3：建立 .claude/settings.json
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

### 步驟 4：建立 WORKFLOW.md
完整的工作流程檢查清單，包含：
- 開始工作前：資料去識別化、環境準備
- 開發過程中：定期儲存、Git 提交
- 完成工作後：程式碼檢查、測試
- 回公司前：Git 推送、準備部署文件

（使用與 /home/user/20190417/WORKFLOW.md 相同的範本）

### 步驟 5：複製 add-personal-context Skill
```bash
mkdir -p .claude/skills
cp -r [來源專案]/.claude/skills/add-personal-context .claude/skills/
```

### 步驟 6：建立初始 claude.md 並加入個人背景
1. 建立基本的專案說明範本
2. 執行內嵌的 add-personal-context 邏輯
3. 提示使用者補充專案特定的資訊

### 步驟 7：提交到 Git
```bash
git add .gitignore .claude/ WORKFLOW.md claude.md
git commit -m "chore: 初始化 Kepware 專案標準設定

- 建立 .gitignore（Python + 資料庫 + Kepware 報表）
- 建立 .claude/settings.json（權限 + hooks）
- 建立 WORKFLOW.md（工作流程檢查清單）
- 建立 claude.md（包含個人背景與設計標準）
- 加入 add-personal-context Skill"
```

## 完成後的專案結構

```
new-project/
├── .gitignore                           # Git 忽略規則
├── .claude/
│   ├── settings.json                    # Claude Code 設定
│   └── skills/
│       └── add-personal-context/        # 可複用的 Skill
│           └── SKILL.md
├── WORKFLOW.md                          # 工作流程檢查清單
└── claude.md                            # 專案說明 + 個人背景
```

## 使用後的提示訊息

向使用者顯示：

```
✅ Kepware 專案初始化完成！

已建立的檔案：
- .gitignore（保護敏感資料）
- .claude/settings.json（權限與 hooks）
- WORKFLOW.md（工作流程指南）
- claude.md（包含個人背景與設計標準）
- .claude/skills/add-personal-context/（可在其他專案重複使用）

📝 下一步：
1. 補充 claude.md 中的專案特定資訊（資料庫結構、報表需求等）
2. 建立 config.json.example 範本
3. 開始開發！

💡 提示：
- 使用 /add-personal-context 可隨時重新加入個人背景
- 參考 WORKFLOW.md 確保不會遺漏重要步驟
```

## 注意事項

1. **覆蓋警告**：如果檔案已存在，詢問是否覆蓋
2. **來源專案路徑**：需要知道 add-personal-context Skill 的來源位置
   - 預設：`/home/user/20190417/.claude/skills/add-personal-context`
   - 如果不存在，提示使用者提供路徑
3. **Git 檢查**：如果目錄還沒 git init，建議先初始化
4. **專案特定資訊**：提醒使用者之後要補充的內容
