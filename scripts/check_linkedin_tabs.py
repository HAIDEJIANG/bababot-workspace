#!/usr/bin/env python3
import requests

tabs = requests.get("http://localhost:9222/json", timeout=5).json()

print(f"总标签页数：{len(tabs)}\n")

linkedin_tabs = [t for t in tabs if 'linkedin' in t.get('url', '').lower()]
print(f"LinkedIn 标签页：{len(linkedin_tabs)}\n")

for i, tab in enumerate(linkedin_tabs):
    print(f"{i+1}. {tab.get('title', 'N/A')[:60]}")
    print(f"   URL: {tab.get('url', 'N/A')[:120]}")
    print(f"   Type: {tab.get('type', 'N/A')}")
    print()
