#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WebTop Local - 本地持久化浏览器方案
提供类似 WebTop 的持久化浏览器环境，无需 Docker

功能：
- 持久化 Cookie/Session
- 自动重连机制
- Watchdog 监控
- CDP 端口暴露
"""

import os
import sys
import json
import time
import signal
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
BROWSER_DATA_DIR = Path(r"C:\Users\Haide\AppData\Local\OpenClaw\BrowserData")
CDP_PORT = 9222
WATCHDOG_INTERVAL = 30  # 秒
STATE_FILE = Path(__file__).parent / "webtop-state.json"

def ensure_dirs():
    """确保所需目录存在"""
    BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def start_browser(headless=False):
    """启动持久化浏览器"""
    ensure_dirs()
    
    print("🚀 启动持久化浏览器...")
    print(f"📁 用户数据目录：{BROWSER_DATA_DIR}")
    print(f"🔌 CDP 端口：{CDP_PORT}")
    
    # 使用 Playwright API 直接启动持久化上下文
    try:
        with sync_playwright() as p:
            # 启动持久化浏览器上下文
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_DATA_DIR),
                headless=headless,
                args=[
                    f"--remote-debugging-port={CDP_PORT}",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
                timeout=60000
            )
            
            # 获取第一个页面
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # 测试页面
            page.goto("about:blank", timeout=10000)
            title = page.title()
            
            print("✅ 浏览器启动成功！")
            print(f"📄 当前页面：{title}")
            
            # 保存状态
            save_state({
                "status": "running",
                "pid": os.getpid(),
                "cdp_port": CDP_PORT,
                "data_dir": str(BROWSER_DATA_DIR),
                "started_at": datetime.now().isoformat(),
                "last_check": datetime.now().isoformat()
            })
            
            # 保持浏览器运行（不关闭）
            print("\n📝 浏览器保持运行中...")
            print("   按 Ctrl+C 停止浏览器")
            print("   或其他脚本可通过 CDP 连接到此浏览器")
            
            try:
                # 保持运行，等待外部连接
                while True:
                    time.sleep(1)
                    # 定期检查浏览器是否还活着
                    try:
                        page.goto("about:blank", timeout=5000)
                    except:
                        print("⚠️ 浏览器似乎已关闭")
                        break
            except KeyboardInterrupt:
                print("\n👋 正在关闭浏览器...")
            
            browser.close()
            print("✅ 浏览器已关闭")
            
            # 更新状态
            save_state({
                "status": "stopped",
                "stopped_at": datetime.now().isoformat()
            })
            
            return None
            
    except Exception as e:
        print(f"❌ 浏览器启动失败：{e}")
        import traceback
        traceback.print_exc()
        return None

def stop_browser():
    """停止浏览器"""
    state = load_state()
    
    if state.get("status") != "running":
        print("ℹ️ 浏览器未运行")
        return
    
    pid = state.get("pid")
    if pid:
        try:
            process = subprocess.Popen(
                f"taskkill /F /PID {pid}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print("✅ 浏览器已停止")
            else:
                print(f"⚠️ 停止失败：{stderr.decode('gbk', errors='replace')}")
        except Exception as e:
            print(f"❌ 停止出错：{e}")
    
    # 清理状态
    save_state({
        "status": "stopped",
        "stopped_at": datetime.now().isoformat()
    })

def check_browser_health():
    """检查浏览器健康状态"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}", timeout=5000)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            # 简单测试
            page.goto("about:blank", timeout=5000)
            browser.close()
            
            return True
    except Exception as e:
        print(f"⚠️ 健康检查失败：{e}")
        return False

def watchdog_loop():
    """Watchdog 监控循环"""
    print(f"🐕 启动 Watchdog 监控（间隔：{WATCHDOG_INTERVAL}秒）")
    
    while True:
        try:
            state = load_state()
            
            if state.get("status") != "running":
                print(f"⏸️  浏览器未运行，跳过检查")
                time.sleep(WATCHDOG_INTERVAL)
                continue
            
            # 检查浏览器是否可连接
            if check_browser_health():
                print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] 浏览器健康")
                
                # 更新最后检查时间
                state["last_check"] = datetime.now().isoformat()
                save_state(state)
            else:
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] 浏览器无响应，尝试重启...")
                
                # 停止并重启
                stop_browser()
                time.sleep(3)
                start_browser()
                
        except KeyboardInterrupt:
            print("\n👋 Watchdog 停止")
            break
        except Exception as e:
            print(f"⚠️ Watchdog 错误：{e}")
            time.sleep(WATCHDOG_INTERVAL)

def get_connection_config():
    """获取浏览器连接配置（供其他脚本使用）"""
    return {
        "cdp_endpoint": f"http://localhost:{CDP_PORT}",
        "user_data_dir": str(BROWSER_DATA_DIR),
        "headless": False
    }

def main():
    parser = argparse.ArgumentParser(description="WebTop Local - 本地持久化浏览器")
    parser.add_argument("--start", action="store_true", help="启动浏览器")
    parser.add_argument("--stop", action="store_true", help="停止浏览器")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--watchdog", action="store_true", help="启动 Watchdog 监控")
    parser.add_argument("--config", action="store_true", help="输出连接配置（JSON）")
    parser.add_argument("--headless", action="store_true", help="无头模式启动")
    
    args = parser.parse_args()
    
    if args.start:
        start_browser(headless=args.headless)
    elif args.stop:
        stop_browser()
    elif args.status:
        state = load_state()
        print(json.dumps(state, indent=2, ensure_ascii=False))
    elif args.watchdog:
        watchdog_loop()
    elif args.config:
        print(json.dumps(get_connection_config(), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
