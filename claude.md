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

*最後更新：2026-02-04*
