#!/usr/bin/env python3
"""简化测试 LinkedIn Feed 帖子提取"""
import json
import websocket
import requests
import time

port = 9222

# 连接 CDP
version = requests.get(f"http://localhost:{port}/json/version", timeout=5).json()
browser_ws_url = version.get('webSocketDebuggerUrl')
origin = f"http://localhost:{port}"
ws = websocket.create_connection(browser_ws_url, timeout=10, header=["Origin: " + origin])

# 获取 LinkedIn Feed 标签页
tabs = requests.get(f"http://localhost:{port}/json").json()
linkedin_tab = None
for tab in tabs:
    if 'linkedin.com/feed' in tab.get('url', '') and 'sign-in' not in tab.get('url', ''):
        linkedin_tab = tab
        break

# 启用并附加
ws.send(json.dumps({"id": 1, "method": "Target.setDiscoverTargets", "params": {"discover": True}}))
time.sleep(0.5)
ws.send(json.dumps({"id": 2, "method": "Target.attachToTarget", "params": {"targetId": linkedin_tab.get('id'), "flatten": True}}))
time.sleep(1)

# 获取 session_id
session_id = None
while True:
    try:
        ws.settimeout(2)
        response = json.loads(ws.recv())
        if 'result' in response and 'sessionId' in response.get('result', {}):
            session_id = response['result']['sessionId']
            break
    except:
        break

print(f"Session: {session_id[:16]}...")

# 启用 Runtime
ws.send(json.dumps({"id": 3, "method": "Runtime.enable", "sessionId": session_id}))
time.sleep(2)

# 清空缓冲
try:
    while True:
        ws.settimeout(0.1)
        ws.recv()
except:
    pass

# 测试 1: 简单计数
js_count = "document.body.innerText.split('Feed post').length"
ws.send(json.dumps({
    "id": 4,
    "method": "Runtime.evaluate",
    "params": {"expression": js_count, "returnByValue": True},
    "sessionId": session_id
}))
response = json.loads(ws.recv())
print(f"Feed post segments count: {response.get('result', {}).get('result', {}).get('value', 'N/A')}")

# 测试 2: 获取第一个帖子内容
js_first = """
(function() {
    var fullText = document.body.innerText;
    var segments = fullText.split('Feed post');
    if (segments.length < 2) return 'No segments';
    return segments[1].substring(0, 300);
})()
"""
ws.send(json.dumps({
    "id": 5,
    "method": "Runtime.evaluate",
    "params": {"expression": js_first, "returnByValue": True},
    "sessionId": session_id
}))
response = json.loads(ws.recv())
result_value = response.get('result', {}).get('result', {}).get('value', 'N/A')
# 写入文件避免编码问题
with open(r'C:\Users\Haide\.openclaw\workspace\linkedin_segment.txt', 'w', encoding='utf-8') as f:
    f.write(result_value)
print(f"First segment saved to file (length: {len(result_value)} chars)")

# 测试 3: 提取帖子数组（简化版）
js_posts = """
(function() {
    var fullText = document.body.innerText;
    var segments = fullText.split('Feed post');
    var count = segments.length - 1;
    return count.toString();
})()
"""
ws.send(json.dumps({
    "id": 6,
    "method": "Runtime.evaluate",
    "params": {"expression": js_posts, "returnByValue": True},
    "sessionId": session_id
}))
response = json.loads(ws.recv())
print(f"Post count: {response.get('result', {}).get('result', {}).get('value', 'N/A')}")

ws.close()