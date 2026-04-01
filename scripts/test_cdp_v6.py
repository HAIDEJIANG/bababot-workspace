#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v6 - 使用 Runtime.callFunctionOn"""
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
    print("No LinkedIn feed found")
    exit()

print(f"Target: {li_tab['title']}")
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

# 启用必要的 domains
send_cdp("Page.enable")
send_cdp("Runtime.enable")
time.sleep(1)

# 获取页面标题
result = send_cdp("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
print(f"Title: {result.get('result', {}).get('value', 'N/A')}")

# 获取页面 URL
result = send_cdp("Runtime.evaluate", {"expression": "window.location.href", "returnByValue": True})
print(f"URL: {result.get('result', {}).get('value', 'N/A')}")

# 尝试获取所有可见文本
js = """
(function() {
    var text = document.body.innerText;
    return {
        length: text.length,
        first500: text.substring(0, 500)
    };
})()
"""
result = send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True})
body_text = result.get('result', {}).get('value', {})
print(f"\nBody text length: {body_text.get('length', 0)}")
print(f"First 500 chars: {body_text.get('first500', 'N/A')[:200]}")

# 查找所有 article 元素
js = """
(function() {
    var articles = document.querySelectorAll('article');
    return articles.map(function(a, i) {
        return {
            index: i,
            textLen: a.innerText.length,
            classes: a.className.substring(0, 100)
        };
    }).slice(0, 10);
})()
"""
result = send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True})
articles = result.get('result', {}).get('value', [])
print(f"\nFound {len(articles)} articles:")
for art in articles:
    print(f"  [{art.get('index')}] {art.get('textLen')} chars - {art.get('classes', 'N/A')[:50]}")

# 尝试查找 LinkedIn 特定的选择器
selectors = [
    'div.update-v2',
    'div.feed-update',
    'div.ember-view',
    '[data-id="update"]',
    'article.svelte-ct-element'
]

print("\n\nTrying other selectors:")
for selector in selectors:
    js = f"document.querySelectorAll('{selector}').length"
    result = send_cdp("Runtime.evaluate", {"expression": js, "returnByValue": True})
    count = result.get('result', {}).get('value', 0)
    print(f"  {selector}: {count}")

ws.close()
print("\nDone")
