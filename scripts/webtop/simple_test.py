#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试 - 验证登录状态
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

print("=" * 60)
print("验证登录状态")
print("=" * 60)

try:
    with sync_playwright() as p:
        # 连接浏览器
        print("\n连接浏览器...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
        context = browser.contexts[0]
        
        # 测试 LinkedIn
        print("\n[1/2] 检查 LinkedIn...")
        page = context.new_page()
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        page.wait_for_timeout(5000)
        
        url = page.url
        if "sign-in" in url.lower():
            print("LinkedIn: 未登录")
        else:
            print("LinkedIn: 已登录")
            print(f"当前 URL: {url}")
        
        # 测试 StockMarket
        print("\n[2/2] 检查 StockMarket.aero...")
        page.goto("https://stockmarket.aero/", timeout=60000)
        page.wait_for_timeout(5000)
        
        url = page.url
        if "login" in url.lower():
            print("StockMarket: 未登录")
        else:
            print("StockMarket: 已登录")
            print(f"当前 URL: {url}")
        
        browser.close()
        
        print("\n" + "=" * 60)
        print("验证完成！")
        print("=" * 60)
        
except Exception as e:
    print(f"\n错误：{e}")
