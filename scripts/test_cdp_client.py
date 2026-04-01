#!/usr/bin/env python3
from cdp_client import CDPClient
import json

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()
li = client.find_linkedin_feed()

if li:
    print(f'Found: {li["title"]}')
    if client.connect(li['id']):
        # 测试 evaluate
        result = client.evaluate("document.title")
        print(f"Title result: {json.dumps(result, indent=2)}")
        
        result = client.evaluate("document.body.innerText.length")
        print(f"\nBody text result: {json.dumps(result, indent=2)}")
        
        client.disconnect()
