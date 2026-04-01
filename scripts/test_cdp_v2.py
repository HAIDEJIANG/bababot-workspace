#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v2 - 带页面导航和等待"""
from cdp_client import CDPClient
import time

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()
print(f'Found {len(tabs)} tabs')

li_tab = client.find_linkedin_feed()
if li_tab:
    print(f"LinkedIn tab: {li_tab['title']}")
    ws_url = li_tab['webSocketDebuggerUrl']
    
    if client.connect(ws_url):
        print("Connected to LinkedIn Feed")
        
        # 先导航到 Feed 页面确保激活
        print("\nNavigating to feed...")
        client.navigate("https://www.linkedin.com/feed/")
        time.sleep(3)  # 等待页面加载
        
        # 获取页面内容
        print("Getting page content...")
        content = client.get_page_content()
        print(f'Page content length: {len(content)} chars')
        
        if len(content) > 1000:
            print(f'\nFirst 300 chars:\n{content[:300]}')
        
        # 提取帖子
        print("\nExtracting posts...")
        posts = client.extract_posts()
        print(f'Extracted {len(posts)} posts')
        
        for i, post in enumerate(posts[:5]):
            author = post.get('author', 'Unknown')[:30]
            text_len = len(post.get('text', ''))
            print(f"  {i+1}. {author}... ({text_len} chars)")
        
        client.disconnect()
else:
    print("No LinkedIn feed found")
