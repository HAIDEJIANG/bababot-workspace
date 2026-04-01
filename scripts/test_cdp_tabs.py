#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 - 检查所有标签页"""
from cdp_client import CDPClient
import json

client = CDPClient(port=9222)
tabs = client.get_browser_tabs()

print(f'Found {len(tabs)} tabs\n')

linkedin_tabs = [t for t in tabs if 'linkedin' in t.get('url', '').lower()]
print(f'LinkedIn tabs: {len(linkedin_tabs)}\n')

for i, tab in enumerate(linkedin_tabs):
    print(f"{i+1}. {tab.get('title', 'N/A')[:60]}")
    print(f"   URL: {tab.get('url', 'N/A')[:100]}")
    print(f"   ID: {tab.get('id', 'N/A')}")
    print()
