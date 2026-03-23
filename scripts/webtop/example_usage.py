#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WebTop Local 使用示例
演示如何在现有脚本中使用持久化浏览器
"""

import sys
from pathlib import Path

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent))

from browser_config import get_browser_config, create_browser_context
from playwright.sync_api import sync_playwright

def example_linkedin_style():
    """LinkedIn 采集脚本风格的示例"""
    print("=" * 50)
    print("示例：LinkedIn 风格的数据采集")
    print("=" * 50)
    
    with sync_playwright() as p:
        # 连接到持久化浏览器
        browser = create_browser_context(p)
        
        # 获取第一个页面（或创建新页面）
        context = browser.contexts[0] if hasattr(browser, 'contexts') else browser
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            # 访问 LinkedIn
            print("🔗 访问 LinkedIn...")
            page.goto("https://www.linkedin.com/feed/", timeout=30000)
            
            # 等待页面加载
            page.wait_for_load_state("networkidle", timeout=30000)
            
            # 获取页面标题
            title = page.title()
            print(f"✅ 页面加载成功：{title}")
            
            # 检查是否已登录
            if "sign-in" in page.url.lower():
                print("⚠️  未登录状态，需要手动登录")
                print("📝 请在浏览器中完成登录，Cookie 将自动保存")
            else:
                print("✅ 已登录状态")
            
            # 示例：提取动态内容
            print("\n📊 页面信息:")
            print(f"   URL: {page.url}")
            print(f"   标题：{title}")
            
        except Exception as e:
            print(f"❌ 操作失败：{e}")
        finally:
            # 注意：不要关闭浏览器，保持持久化运行
            # browser.close()
            print("\n✅ 示例完成，浏览器保持运行")

def example_rfq_style():
    """RFQ 提交脚本风格的示例"""
    print("=" * 50)
    print("示例：RFQ 提交风格的操作")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = create_browser_context(p)
        
        context = browser.contexts[0] if hasattr(browser, 'contexts') else browser
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            # 访问 StockMarket.aero
            print("🔗 访问 StockMarket.aero...")
            page.goto("https://stockmarket.aero/", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=30000)
            
            print(f"✅ 页面加载成功")
            print(f"   URL: {page.url}")
            
            # 检查登录状态
            if "login" in page.url.lower() or "sign-in" in page.url.lower():
                print("⚠️  需要登录")
                print("📝 请在浏览器中完成登录")
            else:
                print("✅ 已登录状态，可以开始 RFQ 操作")
            
        except Exception as e:
            print(f"❌ 操作失败：{e}")
        finally:
            print("\n✅ 示例完成")

def main():
    print("\n🌐 WebTop Local 使用示例\n")
    print("请选择示例:")
    print("1. LinkedIn 风格")
    print("2. RFQ 风格")
    print("3. 查看浏览器配置")
    print()
    
    choice = input("输入选项 (1-3): ").strip()
    
    if choice == "1":
        example_linkedin_style()
    elif choice == "2":
        example_rfq_style()
    elif choice == "3":
        config = get_browser_config()
        print("\n浏览器配置:")
        import json
        print(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        print("无效选项")

if __name__ == "__main__":
    main()
