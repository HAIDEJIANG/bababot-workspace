#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cookie 导出工具 - 非交互式版本
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

COOKIE_FILE = Path(__file__).parent / "linkedin_cookies.json"

def main():
    print("正在连接浏览器...")
    
    try:
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
            
            # 显示关键 Cookie
            key_cookies = ['li_at', 'JSESSIONID', 'X-LI-IDC']
            found = [c['name'] for c in linkedin_cookies if c['name'] in key_cookies]
            print(f"   关键 Cookie: {', '.join(found) if found else '无'}")
            
    except Exception as e:
        print(f"❌ 导出失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
