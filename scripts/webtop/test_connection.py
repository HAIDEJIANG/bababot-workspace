#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
浏览器连接测试脚本
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright

CDP_ENDPOINT = "http://localhost:9222"

print("=" * 50)
print("浏览器连接测试")
print("=" * 50)

try:
    with sync_playwright() as p:
        print("\n[1/3] 连接到浏览器...")
        browser = p.chromium.connect_over_cdp(CDP_ENDPOINT, timeout=10000)
        print("     连接成功!")
        
        print("\n[2/3] 获取页面...")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        print(f"     当前页面数：{len(context.pages)}")
        
        print("\n[3/3] 测试页面加载...")
        page.goto("about:blank", timeout=10000)
        print(f"     页面标题：{page.title()}")
        
        print("\n" + "=" * 50)
        print("测试通过！浏览器运行正常")
        print("=" * 50)
        
        browser.close()
        
except Exception as e:
    print(f"\n测试失败：{e}")
    import traceback
    traceback.print_exc()
