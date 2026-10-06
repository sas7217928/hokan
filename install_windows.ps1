<#
.SYNOPSIS
  明日の天気ポップアップを Windows のログイン時に自動起動するよう登録し、今すぐ起動する。

.EXAMPLE
  .\install_windows.ps1                                   # 東京・12:00
  .\install_windows.ps1 -Place 大阪 -Lat 34.6937 -Lon 135.5023
  .\install_windows.ps1 -Uninstall                        # 登録解除
#>
param(
    [string]$At = "12:00",
    [string]$Place = "東京",
    [string]$Lat = "35.6895",
    [string]$Lon = "139.6917",
    [switch]$Uninstall
)
$ErrorActionPreference = "Stop"

$script   = Join-Path $PSScriptRoot "weather_notify.py"
$startup  = [Environment]::GetFolderPath("Startup")
$lnkPath  = Join-Path $startup "HokanWeather.lnk"

# 既に常駐しているものを止める(再インストール時の二重起動防止)
Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" |
    Where-Object { $_.CommandLine -like "*weather_notify.py*--daemon*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

if ($Uninstall) {
    if (Test-Path $lnkPath) { Remove-Item $lnkPath }
    Write-Host "解除しました。"
    return
}

# pythonw.exe (コンソール窓なしで動く Python) を探す
$pythonw = $null
$cmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if ($cmd) { $pythonw = $cmd.Source }
if (-not $pythonw -and (Get-Command py.exe -ErrorAction SilentlyContinue)) {
    $exe = & py -3 -c "import sys; print(sys.executable)"
    $candidate = Join-Path (Split-Path $exe) "pythonw.exe"
    if (Test-Path $candidate) { $pythonw = $candidate }
}
if (-not $pythonw) {
    Write-Error "Python が見つかりません。次を実行して入れ直してください: winget install Python.Python.3.12"
}

# 動作確認(ネットワークと天気取得が通るか)
$python = Join-Path (Split-Path $pythonw) "python.exe"
Write-Host "天気を取得して確認します..."
& $python $script --place $Place --lat $Lat --lon $Lon
if ($LASTEXITCODE -ne 0) { Write-Error "天気の取得に失敗しました。ネットワークを確認してください。" }

# スタートアップにショートカットを作成
$arguments = "`"$script`" --daemon --at $At --place `"$Place`" --lat $Lat --lon $Lon"
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut($lnkPath)
$lnk.TargetPath       = $pythonw
$lnk.Arguments        = $arguments
$lnk.WorkingDirectory = $PSScriptRoot
$lnk.WindowStyle      = 7   # 最小化
$lnk.Save()

# 今すぐ起動
Start-Process -FilePath $pythonw -ArgumentList $arguments -WorkingDirectory $PSScriptRoot -WindowStyle Hidden

Write-Host ""
Write-Host "完了: 毎日 $At に $Place の明日の天気をポップアップ表示します。"
Write-Host "ログイン時に自動で起動します。解除: .\install_windows.ps1 -Uninstall"
Write-Host "今すぐ表示を試す: python weather_notify.py --popup"
