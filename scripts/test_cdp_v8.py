#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v8 - 使用浏览器级别连接 + AttachToTarget"""
import websocket
import json
import time
import requests

# 获取浏览器版本信息获取浏览器级别 WS URL
version = requests.get("http://localhost:9222/json/version", timeout=5).json()
browser_ws_url = version.get('webSocketDebuggerUrl')
print(f"Browser WS URL: {browser_ws_url}\n")

# 获取所有标签页
tabs = requests.get("http://localhost:9222/json", timeout=5).json()
print(f"Found {len(tabs)} tabs")

li_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        li_tab = tab
        break

if li_tab:
    print(f"LinkedIn tab: {li_tab['title']}")
    print(f"Target ID: {li_tab['id']}\n")
else:
    print("No LinkedIn feed found\n")

# 连接浏览器级别 WS
print("Connecting to browser...")
ws = websocket.create_connection(browser_ws_url, timeout=10)
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

# 列出所有 target
print("Listing targets...")
result = send_cdp("Target.getTargets")
print(f"Targets: {json.dumps(result, indent=2)[:500]}\n")

# 附加到 LinkedIn target
if li_tab:
    print(f"Attaching to target {li_tab['id']}...")
    result = send_cdp("Target.attachToTarget", {"targetId": li_tab['id'], "flatten": True})
    print(f"Attach result: {result}\n")
    
    session_id = result.get('result', {}).get('sessionId')
    if session_id:
        print(f"Session ID: {session_id}\n")
        
        # 通过 session 发送命令
        def send_to_session(method, params=None):
            msg_counter[0] += 1
            message = {
                "id": msg_counter[0],
                "method": method,
                "params": params or {},
                "sessionId": session_id
            }
            ws.send(json.dumps(message))
            return json.loads(ws.recv())
        
        # 启用 domains
        send_to_session("Page.enable")
        send_to_session("Runtime.enable")
        time.sleep(2)
        
        # 获取页面信息
        print("Getting page info...")
        result = send_to_session("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
        print(f"Title: {result.get('result', {}).get('value', 'N/A')}")
        
        result = send_to_session("Runtime.evaluate", {"expression": "window.location.href", "returnByValue": True})
        print(f"URL: {result.get('result', {}).get('value', 'N/A')}")
        
        # 获取 HTML
        result = send_to_session("Runtime.evaluate", {"expression": "document.documentElement.outerHTML", "returnByValue": True})
        html = result.get('result', {}).get('value', '')
        print(f"\nHTML length: {len(html)}")
        
        if len(html) > 300:
            print(f"First 300 chars:\n{html[:300]}")
        
        # 查找 article
        result = send_to_session("Runtime.evaluate", {"expression": "document.querySelectorAll('article').length", "returnByValue": True})
        count = result.get('result', {}).get('value', 0)
        print(f"\nArticle count: {count}")

ws.close()
print("\nDone")
