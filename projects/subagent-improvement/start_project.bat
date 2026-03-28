#!/usr/bin/env powershell
# Sub-Agent 项目一键启动脚本
# 执行完整的 LinkedIn 联系人分析流程

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LinkedIn 联系人深度分析项目 - 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查前置条件
$workspace = "C:\Users\Haide\.openclaw\workspace\projects\subagent-improvement"
$inputs = @(
    "C:\Users\Haide\Desktop\OPENCLAW\LINKEDIN\LINKEDIN Connections_with_posts_FINAL.csv",
    "C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\contact_profiles_full.csv",
    "C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\contact_posts_90days.csv"
)

Write-Host "检查输入文件..." -ForegroundColor Yellow
foreach ($input in $inputs) {
    if (Test-Path $input) {
        Write-Host "  ✅ $((Get-Item $input).Name)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $input" -ForegroundColor Red
        Write-Host "      文件不存在，退出" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "检查浏览器连接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9222/json/version" -TimeoutSec 10
    Write-Host "  ✅ 浏览器已连接（CDP 端口 9222）" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 浏览器未连接，请先启动 Chrome 并开启 CDP 端口" -ForegroundColor Red
    Write-Host "      命令：Start-Process chrome -ArgumentList '--remote-debugging-port=9222'" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "检查项目文件..." -ForegroundColor Yellow
$projectFiles = @(
    "src\subagent_base.py",
    "src\resource_manager.py", 
    "src\subagent_monitor.py",
    "agents\subagent_data_merge.py",
    "agents\subagent_intent_analysis.py",
    "agents\subagent_lead_screening.py",
    "agents\subagent_priority_ranking.py"
)

foreach ($file in $projectFiles) {
    if (Test-Path "$workspace\$file") {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始执行 Sub-Agent 项目" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: 智能优先级打分
Write-Host "[1/4] 执行：智能优先级打分 Sub-Agent" -ForegroundColor Yellow
Set-Location $workspace
Start-Process python -ArgumentList "agents\subagent_priority_ranking.py" -Wait
Write-Host "  ✅ 优先级打分完成" -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] 执行：数据合并 Sub-Agent" -ForegroundColor Yellow
Start-Process python -ArgumentList "agents\subagent_data_merge.py" -Wait
Write-Host "  ✅ 数据合并完成" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] 执行：业务意图分析 Sub-Agent" -ForegroundColor Yellow
Start-Process python -ArgumentList "agents\subagent_intent_analysis.py" -Wait
Write-Host "  ✅ 业务意图分析完成" -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] 执行：线索筛选 Sub-Agent" -ForegroundColor Yellow
Start-Process python -ArgumentList "agents\subagent_lead_screening.py" -Wait
Write-Host "  ✅ 线索筛选完成" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Sub-Agent 项目执行完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "输出文件：" -ForegroundColor Cyan
Write-Host "  - linkedin_master_database.csv" -ForegroundColor White
Write-Host "  - linkedin_business_intents.csv" -ForegroundColor White  
Write-Host "  - linkedin_high_value_leads.csv" -ForegroundColor White
Write-Host "  - linkedin_recommended_actions.csv" -ForegroundColor White
Write-Host "  - priority_ranking.csv" -ForegroundColor White

Write-Host ""
Write-Host "查看结果：" -ForegroundColor Cyan
Write-Host "  python src\subagent_monitor.py summary" -ForegroundColor White

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
