#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Browser Watchdog - 浏览器健康监控（后台运行版）

功能：
- 定期检查浏览器连接状态
- 浏览器无响应时自动重启
- 记录监控日志
- 后台静默运行

使用：
python browser_watchdog.py
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright
from browser_config import get_browser_config

# 配置
CHECK_INTERVAL = 60  # 检查间隔（秒）
MAX_RETRIES = 3  # 最大重试次数
LOG_FILE = Path(__file__).parent / "watchdog.log"
STATE_FILE = Path(__file__).parent / "webtop-state.json"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def check_browser_health():
    """检查浏览器健康状态"""
    config = get_browser_config()
    
    if not config.get('is_running'):
        log("⚠️  浏览器未运行")
        return False
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(
                config['cdp_endpoint'],
                timeout=5000
            )
            
            # 简单测试
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("about:blank", timeout=5000)
            
            browser.close()
            
            return True
            
    except Exception as e:
        log(f"❌ 健康检查失败：{e}")
        return False

def restart_browser():
    """重启浏览器"""
    log("🔄 正在重启浏览器...")
    
    # 停止浏览器
    import subprocess
    subprocess.Popen([
        sys.executable,
        str(Path(__file__).parent / 'webtop_local.py'),
        '--stop'
    ])
    
    time.sleep(3)
    
    # 启动浏览器
    subprocess.Popen([
        sys.executable,
        str(Path(__file__).parent / 'webtop_local.py'),
        '--start'
    ])
    
    time.sleep(10)
    log("✅ 浏览器已重启")

def update_watchdog_state(status, last_check, last_restart=None):
    """更新 Watchdog 状态"""
    state = {
        'watchdog_status': status,
        'watchdog_last_check': last_check,
        'watchdog_last_restart': last_restart
    }
    
    state_file = Path(__file__).parent / "watchdog-state.json"
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def main():
    """主循环"""
    log("=" * 50)
    log("Browser Watchdog 启动")
    log("=" * 50)
    log(f"检查间隔：{CHECK_INTERVAL}秒")
    log(f"最大重试：{MAX_RETRIES}")
    
    consecutive_failures = 0
    last_restart = None
    
    try:
        while True:
            current_time = datetime.now().isoformat()
            
            # 健康检查
            if check_browser_health():
                log("✅ 浏览器健康")
                consecutive_failures = 0
                update_watchdog_state('healthy', current_time, last_restart)
            else:
                consecutive_failures += 1
                log(f"⚠️  浏览器异常 (连续{consecutive_failures}次)")
                
                if consecutive_failures >= MAX_RETRIES:
                    log("❌ 达到最大重试次数，重启浏览器")
                    restart_browser()
                    consecutive_failures = 0
                    last_restart = current_time
                    update_watchdog_state('restarted', current_time, last_restart)
                else:
                    update_watchdog_state('unhealthy', current_time, last_restart)
            
            # 等待下次检查
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        log("\n👋 Watchdog 停止")
        update_watchdog_state('stopped', datetime.now().isoformat(), last_restart)
    except Exception as e:
        log(f"\n❌ Watchdog 错误：{e}")
        update_watchdog_state('error', datetime.now().isoformat(), last_restart)

if __name__ == "__main__":
    main()
