#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 登录检查脚本
"""

import time
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright

def check_login():
    with sync_playwright() as p:
        print("连接浏览器...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
            print("连接成功")
        except Exception as e:
            print(f"连接失败：{e}")
            print("请确保 webtop_local.py 正在运行")
            return
        
        context = browser.contexts[0] if hasattr(browser, 'contexts') and browser.contexts else browser
        page = context.pages[0] if context.pages else browser.new_page()
        
        print(f"当前 URL: {page.url}")
        
        # 导航到 LinkedIn feed
        print("导航到 LinkedIn Feed...")
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        time.sleep(5)
        
        print(f"当前 URL: {page.url}")
        
        # 检查是否登录
        if "sign-in" in page.url.lower() or "login" in page.url.lower():
            print("未登录状态")
            print("请在浏览器中手动登录 LinkedIn")
            print("等待 120 秒...")
            for i in range(120, 0, -10):
                print(f"  剩余 {i} 秒...")
                time.sleep(10)
            
            # 再次检查
            if "sign-in" in page.url.lower() or "login" in page.url.lower():
                print("仍然未登录，退出")
            else:
                print("登录成功")
                print(f"当前 URL: {page.url}")
        else:
            print("已登录状态")
            
            # 尝试查找帖子
            print("\n查找帖子元素...")
            selectors = [
                'div[role="article"]',
                '[data-id*="urn:li:activity"]',
                '[class*="update"]',
                'article',
            ]
            
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    print(f"{selector}: {len(elements)} 个元素")
                except Exception as e:
                    print(f"{selector}: 错误 - {e}")

if __name__ == '__main__':
    check_login()
