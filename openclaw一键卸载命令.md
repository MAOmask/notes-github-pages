```powershell
Invoke-Expression @'
Write-Host "=== 清理 npm 包装脚本 ===" -ForegroundColor Yellow

$npmPrefix = "$env:APPDATA\npm"
$targets = @("openclaw", "clawhub", "clawdbot")

foreach ($name in $targets) {
    # 删除所有可能的 npm 包装文件
    $files = @(
        "$npmPrefix\$name",
        "$npmPrefix\$name.cmd",
        "$npmPrefix\$name.ps1",
        "$npmPrefix\$name.bat",
        "$npmPrefix\$name.mjs",
        "$npmPrefix\$name.js"
    )
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
            if (-not (Test-Path $file)) {
                Write-Host "✅ 已删除: $file" -ForegroundColor Green
            } else {
                Write-Host "❌ 删除失败: $file" -ForegroundColor Red
            }
        }
    }
}

# 清理可能存在的其他目录
$extraDirs = @(
    "$env:APPDATA\npm\node_modules\openclaw",
    "$env:APPDATA\npm\node_modules\clawhub",
    "$env:APPDATA\npm\node_modules\clawdbot",
    "$env:USERPROFILE\.openclaw"
)
foreach ($dir in $extraDirs) {
    if (Test-Path $dir) {
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
        if (-not (Test-Path $dir)) {
            Write-Host "✅ 已删除目录: $dir" -ForegroundColor Green
        } else {
            Write-Host "❌ 删除目录失败: $dir" -ForegroundColor Red
        }
    }
}

# 刷新并验证
Write-Host "`n=== 验证清理结果 ===" -ForegroundColor Cyan
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
Start-Sleep -Seconds 1

$hasOpenclaw = Get-Command openclaw -ErrorAction SilentlyContinue
$hasClawhub = Get-Command clawhub -ErrorAction SilentlyContinue

if (-not $hasOpenclaw -and -not $hasClawhub) {
    Write-Host "🎉 彻底清理完成！openclaw 和 clawhub 已完全移除" -ForegroundColor Green
} else {
    if ($hasOpenclaw) { Write-Host "❌ openclaw 仍存在: $($hasOpenclaw.Source)" -ForegroundColor Red }
    if ($hasClawhub) { Write-Host "❌ clawhub 仍存在: $($hasClawhub.Source)" -ForegroundColor Red }
}
'@
```