#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v3 - 使用正确的 Target ID"""
from cdp_client import CDPClient
import time
import requests

# 获取浏览器标签页信息
response = requests.get("http://localhost:9222/json", timeout=5)
tabs = response.json()

print(f'Found {len(tabs)} tabs\n')

# 找到 LinkedIn Feed 标签页
li_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        li_tab = tab
        break

if li_tab:
    print(f"Target: {li_tab['title']}")
    print(f"URL: {li_tab['url']}")
    print(f"ID: {li_tab['id']}")
    print(f"WebSocketDebuggerUrl: {li_tab.get('webSocketDebuggerUrl', 'N/A')[:60]}...")
    
    # 尝试直接访问页面
    print("\n\nTrying to access page via CDP...")
    
    client = CDPClient(port=9222)
    
    # 使用正确的 WebSocket URL
    ws_url = li_tab.get('webSocketDebuggerUrl')
    if client.connect(ws_url):
        print("Connected!\n")
        
        # 启用 Page domain
        client.send("Page.enable")
        time.sleep(1)
        
        # 尝试获取 DOM
        result = client.send("DOM.getDocument")
        print(f"DOM result keys: {result.keys()}")
        
        # 执行 JavaScript 获取标题
        result = client.evaluate("document.title")
        print(f"Document title: {result.get('result', {}).get('value', 'N/A')}")
        
        # 获取 body 文本
        result = client.evaluate("document.body.innerText")
        text = result.get('result', {}).get('value', '')
        print(f"Body text length: {len(text)}")
        if len(text) > 200:
            print(f"First 200 chars: {text[:200]}")
        
        # 查找文章元素
        result = client.evaluate("document.querySelectorAll('article').length")
        article_count = result.get('result', {}).get('value', 0)
        print(f"\nArticle elements found: {article_count}")
        
        # 尝试滚动
        print("\nScrolling page...")
        client.scroll_page(500)
        time.sleep(2)
        
        # 再次检查
        result = client.evaluate("document.querySelectorAll('article').length")
        article_count = result.get('result', {}).get('value', 0)
        print(f"After scroll - Article elements: {article_count}")
        
        # 提取帖子
        posts = client.extract_posts()
        print(f"\nExtracted posts: {len(posts)}")
        
        client.disconnect()
else:
    print("No LinkedIn feed found")
