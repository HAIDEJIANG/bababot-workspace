#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Heartbeat Optimized Script for OpenClaw
Performs system status checks and reports health status.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(r"C:\Users\Haide\.openclaw\workspace")
MEMORY_DIR = WORKSPACE / "memory"
REPORT_FILE = MEMORY_DIR / "heartbeat_report.md"
TASK_PROGRESS_FILE = MEMORY_DIR / "task_progress.json"

def ensure_dirs():
    """Ensure required directories exist."""
    MEMORY_DIR.mkdir(exist_ok=True)

def get_git_status():
    """Get git status of the workspace."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout.strip():
            return f"⚠️ 有未提交的更改:\n```\n{result.stdout}\n```"
        return "✅ Git 工作区干净"
    except Exception as e:
        return f"❌ Git 检查失败：{e}"

def check_subagents():
    """Check for active subagents (placeholder - would need OpenClaw API)."""
    return "ℹ️ 子代理检查需要 OpenClaw API 访问"

def check_active_tasks():
    """Check progress of active automation tasks from actual CSV files."""
    tasks_status = []
    
    # Get accurate LinkedIn collection progress from actual CSV files
    linkedin_csv = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\contact_profiles_full.csv")
    if linkedin_csv.exists():
        try:
            import csv
            unique_urls = set()
            with open(linkedin_csv, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) > 0 and row[0].startswith('https://www.linkedin.com/in/'):
                        unique_urls.add(row[0])
            
            total = 3185
            collected = len(unique_urls)
            progress = collected / total * 100
            remaining = total - collected
            
            tasks_status.append(f"✅ LinkedIn 采集：{collected:,}/{total:,} ({progress:.2f}%) - 剩余 {remaining:,} 位")
        except Exception as e:
            tasks_status.append(f"⚠️ LinkedIn 进度检查失败：{e}")
    else:
        tasks_status.append("⚠️ LinkedIn 数据文件不存在")
    
    return "\n".join(tasks_status) if tasks_status else "ℹ️ 无配置的任务"

def check_browser_relay():
    """Check Browser Relay watchdog state."""
    watchdog_file = WORKSPACE / "scripts" / "relay-watchdog-state.json"
    if watchdog_file.exists():
        try:
            # Try utf-8-sig to handle UTF-8 BOM
            with open(watchdog_file, 'r', encoding='utf-8-sig') as f:
                state = json.load(f)
            last_check = state.get('lastCheck', '未知')
            status = state.get('status', '未知')
            return f"✅ Browser Relay: {status} (最后检查：{last_check})"
        except Exception as e:
            return f"⚠️ Watchdog 状态读取失败：{e}"
    return "ℹ️ Watchdog 状态文件不存在"

def generate_report():
    """Generate heartbeat report."""
    ensure_dirs()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Heartbeat Report

**时间**: {timestamp}

## 系统状态

### Git 状态
{get_git_status()}

### 任务状态
{check_active_tasks()}

### Browser Relay
{check_browser_relay()}

### 子代理
{check_subagents()}

## 建议操作

- 如有未提交更改，考虑提交到 GitHub
- 检查 LinkedIn 采集任务是否正常运行
- 确认 Browser Relay 连接状态

---
*此报告由 heartbeat_optimized.py 自动生成*
"""
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    return report

def main():
    """Main entry point."""
    try:
        generate_report()
        print("\n✅ 心跳检查完成")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 心跳检查失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
