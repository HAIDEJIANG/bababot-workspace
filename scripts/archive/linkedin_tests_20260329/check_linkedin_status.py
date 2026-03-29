#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 LinkedIn 登录状态和页面内容
"""

import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\Haide\AppData\Local\OpenClaw\BrowserData"

with sync_playwright() as p:
    # 启动浏览器
    print("启动浏览器...")
    browser = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        timeout=60000
    )
    
    # 获取或创建页面
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # 访问 LinkedIn
    print("访问 LinkedIn...")
    page.goto("https://www.linkedin.com/feed/", timeout=60000)
    time.sleep(5)
    
    # 检查状态
    print(f"\n当前 URL: {page.url}")
    print(f"页面标题：{page.title()}")
    
    # 检查是否登录
    if "sign-in" in page.url.lower() or "login" in page.url.lower():
        print("\n[WARN] 未登录状态 - 需要手动登录")
        print("[INFO] 请在打开的浏览器窗口中登录 LinkedIn")
    else:
        print("\n[OK] 已登录状态")
    
    # 尝试查找帖子
    posts = page.evaluate('''() => {
        const elements = document.querySelectorAll('div[class*="update"], div[data-id*="urn:li:activity"], article');
        return elements.length;
    }''')
    
    print(f"\n页面上找到 {posts} 个潜在的帖子元素")
    
    # 保持浏览器打开 30 秒供观察
    print("\n浏览器保持打开 30 秒，请观察窗口...")
    time.sleep(30)
    
    browser.close()
    print("完成")
