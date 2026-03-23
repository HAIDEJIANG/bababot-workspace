#!/usr/bin/env python3
"""测试 CDP 连接"""
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:18800"

print(f"正在连接 CDP: {CDP_URL}...")
try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL, timeout=30000)
        print("[OK] 连接成功!")
        
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        
        print(f"当前 URL: {page.url}")
        print(f"页面标题：{page.title()}")
        
        browser.close()
        print("[OK] 测试完成!")
except Exception as e:
    print(f"[ERROR] {e}")
