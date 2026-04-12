# Hyper-V 效能基線收集系統 — 環境測試流程

**文件用途**：正式實作前的環境驗證  
**版本**：v1.0  
**執行方式**：依序完成每個 Step，每步驗收通過後再往下

---

## 測試前準備

- [ ] 確認你有 Hyper-V 主機的管理員帳號
- [ ] 確認你的執行環境（二選一，勾選適用的）：
  - [ ] **管理機模式**：另一台 Windows 電腦，可透過網路連到 Hyper-V 主機
  - [ ] **直連模式**：直接 RDP 登入 Hyper-V 主機操作

> 以下指令在**管理機模式**時於管理機執行；**直連模式**時於主機本機執行。  
> 涉及 `-ComputerName` 的指令，直連模式可省略該參數（或填入 `localhost`）。

---

## Step 1：確認 WinRM 服務狀態

> **目的**：確認 Hyper-V 主機的遠端管理服務正在運行。  
> **執行位置**：直接在 **Hyper-V 主機**上執行（RDP 登入後）。

```powershell
Get-Service WinRM | Select-Object Name, Status, StartType
```

**預期結果：**

```
Name  Status StartType
----  ------ ---------
WinRM Running Automatic
```

- [ ] Status 為 `Running` ✅
- [ ] StartType 為 `Automatic` ✅

**若 Status 不是 Running：**
```powershell
# 啟動 WinRM（需管理員權限）
Start-Service WinRM
Set-Service WinRM -StartupType Automatic
```

---

## Step 2：確認遠端查詢可通（管理機模式適用）

> **目的**：確認從管理機可以遠端查詢 Hyper-V 主機。  
> **執行位置**：**管理機**上執行。  
> 直連模式請跳至 Step 3。

```powershell
# 將 HV-HOST 替換為你的 Hyper-V 主機名稱或 IP
$hv = "HV-HOST"

Test-NetConnection -ComputerName $hv -Port 5985
```

**預期結果：**
```
TcpTestSucceeded : True
```

- [ ] `TcpTestSucceeded` 為 `True` ✅

**若失敗**，在 Hyper-V 主機上執行以下指令開放防火牆：
```powershell
# 於 Hyper-V 主機上執行
Enable-PSRemoting -Force
```

---

## Step 3：確認 Hyper-V VM 清單可查詢

> **目的**：確認帳號有足夠權限讀取 VM 資訊。

```powershell
# 管理機模式（替換 HV-HOST）
Get-VM -ComputerName "HV-HOST" | Select-Object Name, State, ProcessorCount, MemoryAssigned

# 直連模式
Get-VM | Select-Object Name, State, ProcessorCount, MemoryAssigned
```

**預期結果範例：**
```
Name         State   ProcessorCount MemoryAssigned
----         -----   -------------- --------------
P-DC-SQL-01  Running              8    34359738368
P-DC-APP-01  Running              4     8589934592
P-DC-AD-01   Running              2     4294967296
```

- [ ] 可以看到 VM 清單 ✅
- [ ] ProcessorCount 數值合理 ✅
- [ ] MemoryAssigned 有數值（單位為 Bytes，除以 1MB 得 MB 數）✅

**若出現權限錯誤：**  
確認執行帳號已加入 Hyper-V 主機的 `Hyper-V Administrators` 群組。

---

## Step 4：確認 CPU Performance Counter 可讀取

> **目的**：這是最關鍵的測試，確認可以從主機外部取得 VM 的 CPU 使用率。  
> ⚠️ 此指令需要約 **2–3 秒**等待採樣，屬正常現象。

```powershell
# 管理機模式（替換 HV-HOST）
Get-Counter '\Hyper-V Hypervisor Virtual Processor(*)\% Guest Run Time' `
  -ComputerName "HV-HOST" | `
  Select-Object -ExpandProperty CounterSamples | `
  Select-Object InstanceName, CookedValue | `
  Sort-Object CookedValue -Descending | `
  Select-Object -First 10

# 直連模式
Get-Counter '\Hyper-V Hypervisor Virtual Processor(*)\% Guest Run Time' | `
  Select-Object -ExpandProperty CounterSamples | `
  Select-Object InstanceName, CookedValue | `
  Sort-Object CookedValue -Descending | `
  Select-Object -First 10
```

**預期結果範例：**
```
InstanceName              CookedValue
------------              -----------
p-dc-sql-01:hv vp 0          45.2341
p-dc-sql-01:hv vp 1          38.7612
p-dc-app-01:hv vp 0          12.4521
_total                        8.3201
```

- [ ] 可以看到 Counter 資料 ✅
- [ ] InstanceName 格式為 `vmname:hv vp N` ✅
- [ ] CookedValue 數值在 0–100 之間 ✅

> **記錄 InstanceName 的格式**，因為不同 Windows Server 版本格式略有差異，  
> 實作時 Python 需要依此格式做名稱清洗。請將實際看到的格式記錄下來：

```
實際觀察到的 InstanceName 格式：___________________________
（範例：p-dc-sql-01:hv vp 0 / P-DC-SQL-01:Hv VP 0）
```

---

## Step 5：確認記憶體與磁碟 Counter 可讀取

```powershell
# 記憶體壓力（Dynamic Memory）
# 管理機模式
Get-Counter '\Hyper-V Dynamic Memory VM(*)\Current Pressure' `
  -ComputerName "HV-HOST" | `
  Select-Object -ExpandProperty CounterSamples | `
  Select-Object InstanceName, CookedValue

# 磁碟讀寫
Get-Counter @(
  '\Hyper-V Virtual Storage Device(*)\Read Bytes/sec',
  '\Hyper-V Virtual Storage Device(*)\Write Bytes/sec'
) -ComputerName "HV-HOST" | `
  Select-Object -ExpandProperty CounterSamples | `
  Select-Object InstanceName, CookedValue | `
  Select-Object -First 10
```

- [ ] 記憶體 Counter 有回傳資料（使用 Static Memory 的 VM 此項可能為空，屬正常）✅
- [ ] 磁碟 Counter 有回傳資料 ✅
- [ ] 記錄磁碟 InstanceName 格式：`___________________________`

---

## Step 6：確認網路 Counter 可讀取

```powershell
Get-Counter @(
  '\Hyper-V Virtual Network Adapter(*)\Bytes Received/sec',
  '\Hyper-V Virtual Network Adapter(*)\Bytes Sent/sec'
) -ComputerName "HV-HOST" | `
  Select-Object -ExpandProperty CounterSamples | `
  Select-Object InstanceName, CookedValue | `
  Select-Object -First 10
```

- [ ] 網路 Counter 有回傳資料 ✅
- [ ] 記錄網路 InstanceName 格式：`___________________________`

---

## Step 7：確認 Python 環境（管理機）

> **執行位置**：管理機（或你打算跑 collector.py 的電腦）。

```powershell
python --version
```

**預期結果：**
```
Python 3.10.x  （或更高版本）
```

- [ ] Python 版本 3.10 以上 ✅

```powershell
# 確認 openpyxl 可安裝（report.py 匯出 Excel 需要）
pip install openpyxl
```

- [ ] openpyxl 安裝成功 ✅

---

## Step 8：端對端快速驗證

> **目的**：用一段簡短的 Python 腳本確認整個資料流可以跑通。  
> 將以下內容存為 `test_collect.py` 並執行。

```python
# test_collect.py
import subprocess, json, sqlite3, datetime

HV_HOST = "HV-HOST"   # 直連模式改為 "localhost"

PS_SCRIPT = f"""
$vms = Get-VM -ComputerName {HV_HOST} |
       Select-Object Name, State, ProcessorCount,
                     @{{N='RAM_MB';E={{[int]($_.MemoryAssigned/1MB)}}}}
$vms | ConvertTo-Json -Depth 2
"""

result = subprocess.run(
    ["powershell", "-NoProfile", "-NonInteractive",
     "-ExecutionPolicy", "Bypass", "-Command", PS_SCRIPT],
    capture_output=True, text=True, encoding="utf-8", timeout=30
)

print("=== PowerShell 回傳 ===")
print(result.stdout[:500])

data = json.loads(result.stdout)
if isinstance(data, dict):
    data = [data]

print(f"\n=== 解析成功，共 {len(data)} 台 VM ===")
for vm in data:
    print(f"  {vm['Name']:<20} {vm['State']:<10} {vm['ProcessorCount']} vCPU  {vm['RAM_MB']} MB")

# 寫入 SQLite 測試
conn = sqlite3.connect("test_baseline.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS test_vm (
        collected_at TEXT, vm_name TEXT, vm_state TEXT,
        vcpu INTEGER, ram_mb INTEGER
    )
""")
ts = datetime.datetime.utcnow().isoformat()
for vm in data:
    conn.execute("INSERT INTO test_vm VALUES (?,?,?,?,?)",
                 (ts, vm['Name'], vm['State'],
                  vm['ProcessorCount'], vm['RAM_MB']))
conn.commit()
conn.close()

print("\n=== SQLite 寫入成功：test_baseline.db ===")
```

```powershell
python test_collect.py
```

**預期結果：**
```
=== PowerShell 回傳 ===
[{"Name": "P-DC-SQL-01", "State": "Running", ...}]

=== 解析成功，共 12 台 VM ===
  P-DC-SQL-01          Running    8 vCPU  32768 MB
  P-DC-APP-01          Running    4 vCPU  8192 MB
  ...

=== SQLite 寫入成功：test_baseline.db ===
```

- [ ] PowerShell 有回傳 VM 清單 ✅
- [ ] JSON 解析成功，VM 數量正確 ✅
- [ ] SQLite 檔案建立成功 ✅

---

## 測試結果彙整

測試完成後，請填寫以下資訊，帶給 Claude Code 作為實作依據：

```
測試日期：_______________
執行環境：□ 管理機模式  □ 直連模式

Hyper-V 主機名稱 / IP：_______________
Python 版本：_______________

Counter InstanceName 格式記錄：
  CPU Counter    ：_______________（例：vmname:hv vp 0）
  磁碟 Counter   ：_______________（例：vmname ide controller 0）
  網路 Counter   ：_______________（例：vmname_網卡名稱）

VM 總數：_____ 台
  Running 狀態：_____ 台
  Off 狀態    ：_____ 台

使用 Dynamic Memory 的 VM：□ 有  □ 無  □ 混用

異常或特殊觀察：
_______________________________________________
```

---

## 常見問題

**Q：Get-Counter 跑很久沒有回應？**  
A：屬正常，`Get-Counter` 預設採樣間隔為 1 秒，執行約 2–3 秒後才會回傳。若超過 30 秒無回應，請確認 Hyper-V 服務是否正常運行。

**Q：Counter 回傳的是空的，但 Get-VM 正常？**  
A：確認 Hyper-V 主機的 Performance Counter 服務正常：
```powershell
Get-Service PerfHost | Select Status
```

**Q：InstanceName 看起來是亂碼或有特殊字元？**  
A：記錄原始格式並帶給 Claude Code，讓它在 Python 端處理名稱清洗邏輯。

**Q：管理機無法連線到主機（Step 2 失敗）？**  
A：先確認網路可通（`ping HV-HOST`），再確認防火牆設定。若公司有跳板機或堡壘主機，需先登入跳板再執行。

---

*測試完成後，將「測試結果彙整」一節的填寫內容連同本文件帶給 Claude Code，即可開始正式實作。*
