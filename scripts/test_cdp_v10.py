#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v10 - 正确处理 attachedToTarget 事件"""
import websocket
import json
import time
import requests

# 获取浏览器 WS URL
version = requests.get("http://localhost:9222/json/version", timeout=5).json()
browser_ws_url = version.get('webSocketDebuggerUrl')

# 获取所有标签页
tabs = requests.get("http://localhost:9222/json", timeout=5).json()
li_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        li_tab = tab
        break

if not li_tab:
    print("No LinkedIn feed found")
    exit()

print(f"LinkedIn tab: {li_tab['title']}")
print(f"Target ID: {li_tab['id']}\n")

# 连接浏览器 WS
ws = websocket.create_connection(browser_ws_url, timeout=10)
print("Connected to browser\n")

msg_counter = [0]
def send_cdp_and_recv(method, params=None):
    """发送 CDP 命令并接收响应（可能先收到事件）"""
    msg_counter[0] += 1
    message = {
        "id": msg_counter[0],
        "method": method,
        "params": params or {}
    }
    ws.send(json.dumps(message))
    
    # 可能先收到事件，需要循环直到收到响应
    while True:
        msg = json.loads(ws.recv())
        if 'id' in msg and msg['id'] == msg_counter[0]:
            return msg
        else:
            print(f"Received event: {msg.get('method', 'N/A')[:50]}")

# 启用 Target 域
send_cdp_and_recv("Target.setDiscoverTargets", {"discover": True})

# 附加到 target
print(f"Attaching to target {li_tab['id']}...")
result = send_cdp_and_recv("Target.attachToTarget", {"targetId": li_tab['id'], "flatten": True})
print(f"Attach result: {result}")

# 从响应或事件中获取 session ID
session_id = None
if 'sessionId' in result.get('result', {}):
    session_id = result['result']['sessionId']
elif 'sessionId' in result.get('params', {}):
    session_id = result['params']['sessionId']

if not session_id:
    print("No session ID found")
    ws.close()
    exit()

print(f"Session ID: {session_id}\n")

# 通过 session 发送命令
def send_session(method, params=None):
    msg_counter[0] += 1
    message = {
        "id": msg_counter[0],
        "method": method,
        "params": params or {},
        "sessionId": session_id
    }
    ws.send(json.dumps(message))
    
    while True:
        msg = json.loads(ws.recv())
        if 'id' in msg and msg['id'] == msg_counter[0]:
            return msg
        elif 'sessionId' in msg and msg['sessionId'] == session_id:
            print(f"Session event: {msg.get('method', 'N/A')[:50]}")

# 启用 domains
print("Enabling domains...")
send_session("Page.enable")
send_session("Runtime.enable")
time.sleep(2)

# 获取页面信息
print("\nGetting page info...")
result = send_session("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
title = result.get('result', {}).get('value', 'N/A')
print(f"Title: {title}")

result = send_session("Runtime.evaluate", {"expression": "window.location.href", "returnByValue": True})
url = result.get('result', {}).get('value', 'N/A')
print(f"URL: {url}")

# 获取 HTML
result = send_session("Runtime.evaluate", {"expression": "document.documentElement.outerHTML", "returnByValue": True})
html = result.get('result', {}).get('value', '')
print(f"\nHTML length: {len(html)}")

if len(html) > 300:
    print(f"First 300 chars:\n{html[:300]}\n")

# 查找 article
result = send_session("Runtime.evaluate", {"expression": "document.querySelectorAll('article').length", "returnByValue": True})
count = result.get('result', {}).get('value', 0)
print(f"Article count: {count}")

ws.close()
print("\nDone")
