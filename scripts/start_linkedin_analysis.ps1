# LinkedIn 联系人深度分析 - 快速启动脚本
# 用法：.\start_linkedin_analysis.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LinkedIn 联系人深度分析 v2.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查工作目录
$scriptPath = "C:\Users\Haide\.openclaw\workspace\scripts\contact_deep_analysis_v1.py"
if (!(Test-Path $scriptPath)) {
    Write-Host "错误：脚本不存在 - $scriptPath" -ForegroundColor Red
    exit 1
}

# 检查输入文件
$inputFile = "C:\Users\Haide\Desktop\LINKEDIN\all_contacts_current.csv"
if (!(Test-Path $inputFile)) {
    Write-Host "警告：输入文件不存在 - $inputFile" -ForegroundColor Yellow
    Write-Host "请先准备联系人 CSV 文件" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "按任意键退出..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# 检查浏览器进程
$chromeProcesses = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*9222*" }
if (!$chromeProcesses) {
    Write-Host "检测到 WebTop 浏览器未运行" -ForegroundColor Yellow
    Write-Host "是否现在启动？(Y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "启动 WebTop 浏览器..." -ForegroundColor Green
        Start-Process python -ArgumentList "C:\Users\Haide\.openclaw\workspace\scripts\webtop\webtop_local.py", "--start"
        Write-Host "请在打开的浏览器中登录 LinkedIn" -ForegroundColor Cyan
        Write-Host "等待 10 秒..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
    } else {
        Write-Host "请先手动启动浏览器并登录 LinkedIn" -ForegroundColor Yellow
        Write-Host "按任意键继续..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# 显示分析模式
Write-Host ""
Write-Host "当前分析模式：" -ForegroundColor Cyan
Select-String -Path $scriptPath -Pattern "ANALYSIS_MODE = " | ForEach-Object {
    Write-Host $_.Line.Trim() -ForegroundColor Green
}

Write-Host ""
Write-Host "输入文件：$inputFile" -ForegroundColor Cyan
$contactCount = (Get-Content $inputFile | Measure-Object -Line).Lines - 1
Write-Host "联系人数量：$contactCount" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始分析..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 运行分析脚本
Set-Location "C:\Users\Haide\.openclaw\workspace\scripts"
python contact_deep_analysis_v1.py

Write-Host ""
Write-Host "分析完成！" -ForegroundColor Green
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
