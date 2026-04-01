#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v4 - 截图验证"""
from cdp_client import CDPClient
import time
import requests
import base64

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()

li_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        li_tab = tab
        break

if li_tab:
    print(f"Target: {li_tab['title']}")
    ws_url = li_tab.get('webSocketDebuggerUrl')
    
    if client.connect(ws_url):
        print("Connected!\n")
        
        # 启用 Page domain
        client.send("Page.enable")
        time.sleep(0.5)
        
        # 尝试截图
        print("Taking screenshot...")
        result = client.send("Page.captureScreenshot", {"format": "png"})
        
        if 'result' in result and 'data' in result['result']:
            data = base64.b64decode(result['result']['data'])
            with open('linkedin_screenshot.png', 'wb') as f:
                f.write(data)
            print("[OK] Screenshot saved to linkedin_screenshot.png")
        else:
            print(f"[ERR] Screenshot failed: {result}")
        
        # 获取页面 URL（确认我们在正确的页面）
        result = client.evaluate("window.location.href")
        url = result.get('result', {}).get('value', 'N/A')
        print(f"\nCurrent URL: {url}")
        
        # 获取页面标题
        result = client.evaluate("document.title")
        title = result.get('result', {}).get('value', 'N/A')
        print(f"Document title: {title}")
        
        # 检查页面加载状态
        result = client.evaluate("document.readyState")
        ready_state = result.get('result', {}).get('value', 'N/A')
        print(f"Ready state: {ready_state}")
        
        # 获取 HTML
        result = client.evaluate("document.documentElement.outerHTML")
        html = result.get('result', {}).get('value', '')
        print(f"\nHTML length: {len(html)} chars")
        if len(html) > 500:
            print(f"First 500 chars:\n{html[:500]}")
        
        client.disconnect()
else:
    print("No LinkedIn feed found")
