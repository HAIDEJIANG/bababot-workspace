#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本"""
from cdp_client import CDPClient

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()
print(f'Found {len(tabs)} tabs')

li_tab = client.find_linkedin_feed()
if li_tab:
    print(f"LinkedIn tab: {li_tab['title']}")
    ws_url = li_tab['webSocketDebuggerUrl']
    
    if client.connect(ws_url):
        print("Testing post extraction...")
        posts = client.extract_posts()
        print(f'Extracted {len(posts)} posts')
        
        for i, post in enumerate(posts[:5]):
            author = post.get('author', 'Unknown')[:30]
            text_len = len(post.get('text', ''))
            print(f"  {i+1}. {author}... ({text_len} chars)")
        
        client.disconnect()
else:
    print("No LinkedIn feed found")
