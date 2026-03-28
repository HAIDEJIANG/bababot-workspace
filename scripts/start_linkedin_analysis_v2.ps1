# LinkedIn 联系人深度分析 - 优化版启动脚本
# 功能：检查浏览器状态，启动分析脚本，监控进程

$ErrorActionPreference = "Stop"

# 配置
$SCRIPT_DIR = "C:\Users\Haide\.openclaw\workspace\scripts"
$ANALYSIS_SCRIPT = "contact_deep_analysis_v2_optimized.py"
$LOG_DIR = "C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326"
$BROWSER_CHECK_URL = "http://localhost:9222"

Write-Host "========================================"
Write-Host "LinkedIn 联系人分析 - 优化版启动脚本"
Write-Host "========================================"
Write-Host ""

# 1. 检查浏览器状态
Write-Host "[1/3] 检查 Browser Relay 状态..."
try {
    $response = Invoke-WebRequest -Uri $BROWSER_CHECK_URL -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Browser Relay 正常运行" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Browser Relay 响应异常" -ForegroundColor Red
        Write-Host "  请先启动浏览器并启用 Browser Relay 扩展"
        exit 1
    }
} catch {
    Write-Host "  ✗ 无法连接到 Browser Relay (localhost:9222)" -ForegroundColor Red
    Write-Host "  请确保："
    Write-Host "  1. Chrome/Edge 浏览器已启动"
    Write-Host "  2. Browser Relay 扩展已启用"
    Write-Host "  3. 浏览器监听 9222 端口"
    exit 1
}

# 2. 检查脚本
Write-Host ""
Write-Host "[2/3] 检查分析脚本..."
if (Test-Path "$SCRIPT_DIR\$ANALYSIS_SCRIPT") {
    Write-Host "  ✓ 脚本存在：$ANALYSIS_SCRIPT" -ForegroundColor Green
} else {
    Write-Host "  ✗ 脚本不存在：$ANALYSIS_SCRIPT" -ForegroundColor Red
    exit 1
}

# 3. 启动分析
Write-Host ""
Write-Host "[3/3] 启动分析脚本..."
Write-Host ""

# 设置工作目录
Set-Location $SCRIPT_DIR

# 启动脚本（后台运行）
$job = Start-Job -ScriptBlock {
    Set-Location $using:SCRIPT_DIR
    python $using:ANALYSIS_SCRIPT
}

Write-Host "  ✓ 分析脚本已在后台启动" -ForegroundColor Green
Write-Host "  作业 ID: $($job.Id)"
Write-Host ""
Write-Host "监控命令："
Write-Host "  查看日志：Get-Content $LOG_DIR\analysis_log_*.txt -Tail 50 -Wait"
Write-Host "  查看进度：python -c `"import json; print(json.load(open('$LOG_DIR/progress.json'))['processed_contacts'])`""
Write-Host "  停止任务：Stop-Job $($job.Id)"
Write-Host ""
Write-Host "========================================"
