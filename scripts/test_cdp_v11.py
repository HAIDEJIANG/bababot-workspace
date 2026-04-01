#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CDP 测试脚本 v11 - 使用正确的执行上下文"""
import websocket
import json
import time
import requests

version = requests.get("http://localhost:9222/json/version", timeout=5).json()
browser_ws_url = version.get('webSocketDebuggerUrl')

tabs = requests.get("http://localhost:9222/json", timeout=5).json()
li_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        li_tab = tab
        break

if not li_tab:
    print("No LinkedIn feed found")
    exit()

print(f"Target: {li_tab['title']} (ID: {li_tab['id']})\n")

ws = websocket.create_connection(browser_ws_url, timeout=10)

msg_counter = [0]
def send_recv(method, params=None):
    msg_counter[0] += 1
    ws.send(json.dumps({"id": msg_counter[0], "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if 'id' in msg and msg['id'] == msg_counter[0]:
            return msg

# 附加到 target
send_recv("Target.setDiscoverTargets", {"discover": True})
result = send_recv("Target.attachToTarget", {"targetId": li_tab['id'], "flatten": True})
session_id = result.get('result', {}).get('sessionId')
print(f"Session ID: {session_id}\n")

def send_sess(method, params=None):
    msg_counter[0] += 1
    ws.send(json.dumps({"id": msg_counter[0], "method": method, "params": params or {}, "sessionId": session_id}))
    while True:
        msg = json.loads(ws.recv())
        if 'id' in msg and msg['id'] == msg_counter[0]:
            return msg

# 启用 Runtime
send_sess("Runtime.enable")
time.sleep(1)

# 获取所有执行上下文
js = """
(function() {
    return {
        title: document.title,
        url: window.location.href,
        readyState: document.readyState,
        bodyText: document.body ? document.body.innerText.length : 0,
        htmlLen: document.documentElement ? document.documentElement.outerHTML.length : 0
    };
})()
"""

print("Evaluating page...")
result = send_sess("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True})
print(f"Result: {json.dumps(result, indent=2)}")

# 尝试使用 callFunctionOn
print("\n\nTrying callFunctionOn...")
result = send_sess("Runtime.callFunctionOn", {
    "functionDeclaration": "function() { return document.title; }",
    "returnByValue": True
})
print(f"Title via callFunctionOn: {result}")

ws.close()
print("\nDone")
