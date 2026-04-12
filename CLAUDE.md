**# Global Guidelines**

**## Debugging**
1. 修 UI bug 時，先排除環境問題（瀏覽器快取、script 載入順序），確認問題可重現後再改程式碼
2. 修完前端 bug 後，提醒使用者 hard-refresh（Ctrl+Shift+R）或清除快取來驗證修復
3. 除錯時優先檢查 Console 錯誤和 Network tab 載入狀態，再決定是否需要改程式碼
4. 不要在未確認根因前反覆嘗試程式碼層面的修復，先區分是程式碼問題還是環境問

**# 全域開發規範**

**## 語言偏好**
- 回應與註解請使用繁體中文
- commit message 使用英文，conventional commit 格式

**## 搜尋規範**
- 優先使用 Grep 精確搜尋，避免整個讀取檔案
- 用 Grep 定位行號後再用 Read 讀取局部範圍

**## 通知/推播標準**
- 雙通道：Email + Webhook（已移除 LINE Notify）
- Email：內部 SMTP 直送，支援 CC，無需 TLS/驗證
- Webhook：`{{$variable}}` 模板語法，Token 內嵌 Body，Proxy/SSL 可選
- 參考標準：依照 KepwareMonitorOPC 模式
- 新專案如需通知功能，遵循此雙通道架構並與我做最後確認

**## 開發風格**
- 不加不必要的 docstring/comment
- 保持簡潔，只做被要求的變更
- 跨檔案變更後列出檔案清單再 commit
