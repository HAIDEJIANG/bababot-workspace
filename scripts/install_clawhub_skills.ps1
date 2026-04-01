# 批量安装 ClawHub 技能（带延时避免限流）
$skills = @("self-improving-agent", "ontology", "proactive-agent", "agent-browser")

Write-Host "=== 批量安装 ClawHub 技能 ==="
Write-Host "技能列表：$($skills -join ', ')"
Write-Host ""

$success = 0
$failed = 0
$skipped = 0
$index = 0

foreach ($skill in $skills) {
    $index++
    Write-Host "[$index/$($skills.Count)] 安装：$skill"
    
    # 检查是否已安装
    $skillPath = "C:\Users\Haide\.openclaw\workspace\skills\$skill"
    if (Test-Path $skillPath) {
        Write-Host "  已安装，跳过"
        $skipped++
        continue
    }
    
    # 执行安装
    Write-Host "  执行 clawhub install $skill ..."
    $result = clawhub install $skill 2>&1
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "  安装成功"
        $success++
    } elseif ($result -match "Already installed") {
        Write-Host "  已安装，跳过"
        $skipped++
    } else {
        Write-Host "  安装失败：$result"
        $failed++
    }
    
    # 避免限流，等待 15 秒
    if ($index -lt $skills.Count) {
        Write-Host "  等待 15 秒避免限流..."
        Start-Sleep -Seconds 15
    }
}

Write-Host ""
Write-Host "=== 安装完成 ==="
Write-Host "成功：$success | 跳过：$skipped | 失败：$failed"
