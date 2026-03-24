#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 LinkedIn 和 StockMarket.aero 登录状态
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

CDP_ENDPOINT = "http://localhost:9222"

print("=" * 60)
print("验证登录状态测试")
print("=" * 60)

with sync_playwright() as p:
    # 连接到现有浏览器
    print("\n[连接] 连接到浏览器...")
    browser = p.chromium.connect_over_cdp(CDP_ENDPOINT, timeout=10000)
    context = browser.contexts[0]
    
    # 测试 LinkedIn
    print("\n" + "-" * 60)
    print("[1/2] 测试 LinkedIn 登录状态")
    print("-" * 60)
    
    page = context.new_page()
    page.goto("https://www.linkedin.com/feed/", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=30000)
    
    # 检查是否登录
    current_url = page.url
    if "sign-in" in current_url.lower() or "checkpoint" in current_url.lower():
        print("状态：未登录")
        print(f"当前 URL: {current_url}")
    else:
        print("状态：已登录")
        print(f"当前 URL: {current_url}")
        
        # 尝试获取用户信息
        try:
            user_name = page.evaluate('''() => {
                const nav = document.querySelector('[class*="welcome-message"]');
                return nav ? nav.innerText.trim() : "未知用户";
            }''')
            print(f"欢迎：{user_name}")
        except:
            print("欢迎：(无法获取用户名)")
    
    # 测试 StockMarket.aero
    print("\n" + "-" * 60)
    print("[2/2] 测试 StockMarket.aero 登录状态")
    print("-" * 60)
    
    page.goto("https://stockmarket.aero/", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=30000)
    
    current_url = page.url
    if "login" in current_url.lower() or "sign-in" in current_url.lower():
        print("状态：未登录")
        print(f"当前 URL: {current_url}")
    else:
        print("状态：已登录")
        print(f"当前 URL: {current_url}")
        
        # 检查是否有用户菜单
        try:
            user_menu = page.evaluate('''() => {
                const menu = document.querySelector('[class*="user"]');
                return menu ? "找到用户菜单" : "未找到";
            }''')
            print(f"用户菜单：{user_menu}")
        except:
            print("用户菜单：(无法检测)")
    
    browser.close()
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)
