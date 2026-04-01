#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打开可见浏览器供用户登录 LinkedIn"""
from playwright.sync_api import sync_playwright
import time

print("启动可见浏览器...")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=[
            "--remote-debugging-port=9222",
            "--no-sandbox",
        ]
    )
    
    context = browser.contexts[0]
    page = context.new_page()
    
    print("请访问：https://www.linkedin.com/feed")
    print("并登录您的账号")
    print("\n按 Ctrl+C 停止浏览器")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n关闭浏览器...")
    
    browser.close()
