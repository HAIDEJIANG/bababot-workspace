# LinkedIn Contact Scraper - Fast Write-Through Mode
# Designed for continuous extraction without rate limiting

$csvPath = "C:\Users\Haide\.openclaw\workspace\linkedin_connections_full.csv"
$startTime = Get-Date
$totalExtracted = 0

Write-Host "Starting fast LinkedIn contact extraction..."
Write-Host "CSV Path: $csvPath"
Write-Host "Start Time: $startTime"
Write-Host ""

# Check current progress
$currentLines = (Get-Content $csvPath | Measure-Object -Line).Lines
$currentCount = $currentLines - 1  # Exclude header
Write-Host "Current progress: $currentCount contacts already extracted"
Write-Host ""

# This script works with the browser already open and positioned
# It's designed to be called repeatedly from the main agent loop
Write-Host "Script ready. Waiting for browser automation calls..."
Write-Host "Target: 3,182 total connections"
Write-Host "Remaining: $($3182 - $currentCount) contacts"
