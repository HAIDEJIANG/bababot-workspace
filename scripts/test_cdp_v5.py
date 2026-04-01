#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v5 - 使用正确的连接方式"""
import websocket
import json
import time
import requests

# 获取浏览器信息
version_info = requests.get("http://localhost:9222/json/version", timeout=5).json()
print(f"Browser: {version_info.get('Browser', 'N/A')}")
print(f"WebSocket: {version_info.get('webSocketDebuggerUrl', 'N/A')}")

# 获取所有标签页
tabs = requests.get("http://localhost:9222/json", timeout=5).json()
print(f"\nFound {len(tabs)} tabs\n")

# 找到 LinkedIn Feed
li_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        li_tab = tab
        break

if not li_tab:
    print("No LinkedIn feed found")
    exit()

print(f"Target: {li_tab['title']}")
print(f"ID: {li_tab['id']}")

ws_url = li_tab.get('webSocketDebuggerUrl')
print(f"WS URL: {ws_url}\n")

# 创建 WebSocket 连接
print("Connecting...")
ws = websocket.create_connection(ws_url, timeout=10)
print("Connected!\n")

# 发送 CDP 命令
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

# 启用 Page domain
print("Enabling Page domain...")
result = send_cdp("Page.enable")
print(f"Result: {result}\n")

# 等待页面加载
time.sleep(2)

# 获取当前 URL
print("Getting current URL...")
result = send_cdp("Page.getCurrentFrame")
print(f"Current frame: {result}\n")

# 执行 JavaScript
print("Executing JavaScript...")
js_expr = "document.title"
result = send_cdp("Runtime.evaluate", {"expression": js_expr, "returnByValue": True})
print(f"Title result: {result}\n")

# 获取 HTML
js_expr = "document.documentElement.outerHTML"
result = send_cdp("Runtime.evaluate", {"expression": js_expr, "returnByValue": True})
html = result.get('result', {}).get('value', '')
print(f"HTML length: {len(html)}")
if len(html) > 300:
    print(f"First 300 chars:\n{html[:300]}\n")

# 查找文章
js_expr = "document.querySelectorAll('article').length"
result = send_cdp("Runtime.evaluate", {"expression": js_expr, "returnByValue": True})
count = result.get('result', {}).get('value', 0)
print(f"Article count: {count}\n")

ws.close()
print("Done")
