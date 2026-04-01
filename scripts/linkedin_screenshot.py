#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 截图脚本 - CDP 协议版

用法：
  python scripts/linkedin_screenshot.py
  python scripts/linkedin_screenshot.py --full-page
"""

import sys
import io
import time
import argparse
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from cdp_client import CDPClient

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")

def main(full_page: bool = True):
    log("=" * 60)
    log("LinkedIn Feed 截图")
    log("=" * 60)
    
    client = CDPClient(port=9222)
    
    # 查找 LinkedIn Feed 页面
    linkedin_tab = client.find_linkedin_feed()
    if not linkedin_tab:
        log("❌ 未找到 Feed 页面")
        log("请先在 Edge 中打开 LinkedIn Feed 并登录")
        return
    
    log(f"✅ 找到页面：{linkedin_tab.get('title', 'N/A')}")
    
    # 连接
    ws_url = linkedin_tab.get('webSocketDebuggerUrl')
    if not client.connect(ws_url):
        log("❌ 连接失败")
        return
    
    # 等待内容加载
    log("等待内容加载 (15 秒)...")
    time.sleep(15)
    
    # 截图
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = OUTPUT_DIR / f"linkedin_feed_screenshot_{ts}.png"
    
    log(f"截取{'全屏' if full_page else '可视区域'}截图...")
    if client.screenshot(str(screenshot_path), full_page=full_page):
        log(f"✅ 截图已保存：{screenshot_path}")
    else:
        log("❌ 截图失败")
    
    client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn Feed 截图')
    parser.add_argument('--no-full-page', action='store_true', help='只截取可视区域')
    args = parser.parse_args()
    
    try:
        main(full_page=not args.no_full_page)
    except Exception as e:
        log(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
