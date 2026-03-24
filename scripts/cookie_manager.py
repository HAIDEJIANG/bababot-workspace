#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cookie 管理工具
功能：导出/导入浏览器 Cookie，用于无头模式登录
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

COOKIE_FILE = Path(__file__).parent / "linkedin_cookies.json"

def export_cookies():
    """从已登录的浏览器导出 Cookie"""
    print("正在连接浏览器...")
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
        context = browser.contexts[0]
        
        # 获取所有 Cookie
        cookies = context.cookies()
        
        # 过滤 LinkedIn 相关 Cookie
        linkedin_cookies = [c for c in cookies if 'linkedin.com' in c.get('domain', '')]
        
        # 保存到文件
        data = {
            'exported_at': datetime.now().isoformat(),
            'cookies': linkedin_cookies,
            'count': len(linkedin_cookies)
        }
        
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        browser.close()
        
        print(f"✅ Cookie 导出成功！")
        print(f"   文件：{COOKIE_FILE}")
        print(f"   数量：{len(linkedin_cookies)} 个")
        return len(linkedin_cookies)

def import_cookies(context):
    """导入 Cookie 到浏览器上下文"""
    if not COOKIE_FILE.exists():
        print(f"❌ Cookie 文件不存在：{COOKIE_FILE}")
        return False
    
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cookies = data.get('cookies', [])
    if not cookies:
        print("❌ Cookie 为空")
        return False
    
    context.add_cookies(cookies)
    print(f"✅ 导入 {len(cookies)} 个 Cookie")
    return True

def check_cookies():
    """检查 Cookie 是否有效"""
    if not COOKIE_FILE.exists():
        print("❌ Cookie 文件不存在")
        return False
    
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cookies = data.get('cookies', [])
    print(f"Cookie 文件信息:")
    print(f"   导出时间：{data.get('exported_at', '未知')}")
    print(f"   数量：{len(cookies)} 个")
    
    # 检查关键 Cookie
    key_cookies = ['li_at', 'JSESSIONID']
    found = [c['name'] for c in cookies if c['name'] in key_cookies]
    print(f"   关键 Cookie: {', '.join(found) if found else '无'}")
    
    return len(cookies) > 0

def main():
    print("=" * 60)
    print("LinkedIn Cookie 管理工具")
    print("=" * 60)
    print()
    print("请选择操作:")
    print("1. 导出 Cookie (从已登录的浏览器)")
    print("2. 检查 Cookie")
    print("3. 测试 Cookie (启动无头浏览器验证)")
    print()
    
    choice = input("输入选项 (1-3): ").strip()
    
    if choice == "1":
        export_cookies()
    elif choice == "2":
        check_cookies()
    elif choice == "3":
        print("\n测试 Cookie...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            if import_cookies(context):
                page = context.new_page()
                page.goto("https://www.linkedin.com/feed/", timeout=30000)
                
                if "feed" in page.url.lower():
                    print("✅ Cookie 有效！可以访问 Feed 页面")
                else:
                    print(f"❌ Cookie 可能已失效，跳转到：{page.url}")
            else:
                print("❌ 无法导入 Cookie")
            
            browser.close()
    else:
        print("无效选项")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
