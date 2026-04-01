#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 - 调试版"""
from cdp_client import CDPClient

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()
print(f'Found {len(tabs)} tabs')

li_tab = client.find_linkedin_feed()
if li_tab:
    print(f"LinkedIn tab: {li_tab['title']}")
    ws_url = li_tab['webSocketDebuggerUrl']
    
    if client.connect(ws_url):
        # 测试页面内容
        print("\nTesting page content...")
        content = client.get_page_content()
        print(f'Page content length: {len(content)} chars')
        print(f'First 500 chars:\n{content[:500]}')
        
        # 尝试不同的选择器
        print("\n\nTesting different selectors...")
        
        selectors = [
            'article',
            'div.update-v2',
            'div[role="article"]',
            'div.feed-update',
            'div.update',
            'div.jobs-update',
            'div.shared-update',
            'div.ember-view'
        ]
        
        for selector in selectors:
            js = f"document.querySelectorAll('{selector}').length"
            result = client.evaluate(js)
            count = result.get('result', {}).get('value', 0)
            print(f"  {selector}: {count} elements")
        
        client.disconnect()
else:
    print("No LinkedIn feed found")
