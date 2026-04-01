#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v7 - 带导航和等待"""
import websocket
import json
import time
import requests

tabs = requests.get("http://localhost:9222/json", timeout=5).json()
li_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        li_tab = tab
        break

if not li_tab:
    print("No LinkedIn feed found - opening browser...")
    import subprocess
    subprocess.Popen(['msedge', 'https://www.linkedin.com/feed/'])
    time.sleep(5)
    tabs = requests.get("http://localhost:9222/json", timeout=5).json()
    for tab in tabs:
        if 'linkedin.com/feed' in tab.get('url', ''):
            li_tab = tab
            break

if not li_tab:
    print("Still no LinkedIn feed")
    exit()

print(f"Target: {li_tab['title']}")
print(f"URL: {li_tab['url']}")
ws_url = li_tab.get('webSocketDebuggerUrl')

ws = websocket.create_connection(ws_url, timeout=10)
print("Connected!\n")

msg_counter = [0]
def send_cdp(method, params=None):
    msg_counter[0] += 1
    message = {
        "id": msg_counter[0],
        "method": method,
        "params": params or {}
    }
    ws.send(json.dumps(message))
    return json.loads(ws.recv())

# 启用 domains
send_cdp("Page.enable")
send_cdp("Runtime.enable")

# 等待页面加载
print("Waiting for page to load...")
for i in range(10):
    time.sleep(1)
    result = send_cdp("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
    state = result.get('result', {}).get('value', 'unknown')
    print(f"  [{i+1}s] Ready state: {state}")
    if state == 'complete':
        break

# 获取页面信息
print("\nGetting page info...")
result = send_cdp("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
print(f"Title: {result.get('result', {}).get('value', 'N/A')}")

result = send_cdp("Runtime.evaluate", {"expression": "window.location.href", "returnByValue": True})
print(f"URL: {result.get('result', {}).get('value', 'N/A')}")

# 获取 HTML
result = send_cdp("Runtime.evaluate", {"expression": "document.documentElement.outerHTML", "returnByValue": True})
html = result.get('result', {}).get('value', '')
print(f"\nHTML length: {len(html)}")

if len(html) > 0:
    print(f"First 300 chars:\n{html[:300]}\n")
    
    # 查找 article
    result = send_cdp("Runtime.evaluate", {"expression": "document.querySelectorAll('article').length", "returnByValue": True})
    count = result.get('result', {}).get('value', 0)
    print(f"Article count: {count}")
else:
    print("HTML is empty - page may not be loaded yet")

ws.close()
print("\nDone")
