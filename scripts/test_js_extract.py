#!/usr/bin/env python3
"""测试 LinkedIn Feed 帖子提取 JS"""
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

if not linkedin_tab:
    print("未找到 LinkedIn Feed 页面")
    ws.close()
    exit()

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

# 测试简化版帖子提取
js_simple = """
(function() {
    var fullText = document.body ? document.body.innerText : '';
    if (!fullText) return [];
    
    var segments = fullText.split('Feed post');
    var posts = [];
    
    for (var i = 1; i < segments.length && i < 10; i++) {
        var segment = segments[i].trim();
        if (segment.length < 100) continue;
        
        var lines = segment.split('\n').filter(function(l) { return l.trim().length > 0; });
        if (lines.length < 2) continue;
        
        posts.push({
            author: lines[0].trim(),
            textPreview: segment.substring(0, 500),
            lineCount: lines.length
        });
    }
    
    return posts;
})()
"""

ws.send(json.dumps({
    "id": 4,
    "method": "Runtime.evaluate",
    "params": {"expression": js_simple, "returnByValue": True},
    "sessionId": session_id
}))

response = json.loads(ws.recv())
print(f"\n=== 响应结构 ===")
print(f"Response keys: {response.keys()}")

if 'result' in response:
    result_obj = response['result']
    print(f"result keys: {result_obj.keys()}")
    
    if 'result' in result_obj:
        inner_result = result_obj['result']
        print(f"result.result keys: {inner_result.keys()}")
        
        if 'value' in inner_result:
            posts = inner_result['value']
            print(f"\n=== 提取结果 ===")
            print(f"Posts count: {len(posts)}")
            for p in posts[:5]:
                print(f"Author: {p.get('author')}")
                print(f"Preview: {p.get('textPreview')[:100]}...")
                print("---")

ws.close()