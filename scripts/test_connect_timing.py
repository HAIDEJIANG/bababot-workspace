#!/usr/bin/env python3
from cdp_client import CDPClient
import time

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()
li = client.find_linkedin_feed()

if li:
    print(f'Found: {li["title"]}')
    
    # 连接
    if client.connect(li['id']):
        # 立即获取
        print("\nImmediately after connect:")
        info = client.get_page_info()
        print(f"  Title: {info.get('title', 'N/A')}")
        print(f"  BodyText: {info.get('bodyTextLen', 0)} chars")
        
        # 等待 2 秒
        print("\nWaiting 2 seconds...")
        time.sleep(2)
        
        print("\nAfter 2s wait:")
        info = client.get_page_info()
        print(f"  Title: {info.get('title', 'N/A')}")
        print(f"  BodyText: {info.get('bodyTextLen', 0)} chars")
        
        # 等待 5 秒
        print("\nWaiting 5 more seconds...")
        time.sleep(5)
        
        print("\nAfter 5s wait:")
        info = client.get_page_info()
        print(f"  Title: {info.get('title', 'N/A')}")
        print(f"  BodyText: {info.get('bodyTextLen', 0)} chars")
        
        # 提取帖子
        print("\nExtracting posts...")
        posts = client.extract_posts()
        print(f"Posts found: {len(posts)}")
        
        client.disconnect()
