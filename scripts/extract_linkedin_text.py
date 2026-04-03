#!/usr/bin/env python3
"""LinkedIn Feed 文本提取器 - 直接提取页面文本内容"""
import json
import websocket
import requests
import time
import re
from datetime import datetime

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

# 启用 Target 发现并附加
ws.send(json.dumps({"id": 1, "method": "Target.setDiscoverTargets", "params": {"discover": True}}))
time.sleep(0.5)

ws.send(json.dumps({"id": 2, "method": "Target.attachToTarget", "params": {"targetId": linkedin_tab.get('id'), "flatten": True}}))
time.sleep(1)

# 等待响应获取 session_id
session_id = None
responses = []
while True:
    try:
        ws.settimeout(2)
        response = json.loads(ws.recv())
        responses.append(response)
        if 'result' in response and 'sessionId' in response.get('result', {}):
            session_id = response['result']['sessionId']
            print(f"找到 session_id: {session_id[:16]}...")
            break
        if 'id' in response and response['id'] == 2 and 'result' in response:
            session_id = response.get('result', {}).get('sessionId')
            if session_id:
                break
    except websocket.WebSocketTimeoutException:
        break

if not session_id:
    print("无法获取 session_id")
    print(f"收到的响应: {responses}")
    ws.close()
    exit()

print(f"Session ID: {session_id[:16]}...")

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

# 提取页面全部文本内容
js_text = """
(function() {
    // 直接提取页面 body 的全部文本
    var body = document.body;
    if (!body) return {text: '', length: 0};
    
    // 获取所有文本节点
    var walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, null, false);
    var textNodes = [];
    while (walker.nextNode()) {
        var node = walker.currentNode;
        var text = node.textContent.trim();
        if (text.length > 20) {  // 过滤短文本
            var parent = node.parentElement;
            var parentClass = parent ? parent.className : '';
            textNodes.push({
                text: text.substring(0, 500),
                parentClass: parentClass.substring(0, 100)
            });
        }
    }
    
    // 按 parentClass 分组
    var groups = {};
    for (var i = 0; i < textNodes.length; i++) {
        var cls = textNodes[i].parentClass || 'unknown';
        if (!groups[cls]) groups[cls] = [];
        groups[cls].push(textNodes[i].text);
    }
    
    // 找到文本最多的组（可能是帖子内容）
    var maxGroup = null;
    var maxLen = 0;
    for (var cls in groups) {
        var totalLen = groups[cls].reduce((sum, t) => sum + t.length, 0);
        if (totalLen > maxLen) {
            maxLen = totalLen;
            maxGroup = cls;
        }
    }
    
    return {
        totalTextNodes: textNodes.length,
        groupsCount: Object.keys(groups).length,
        largestGroup: {
            className: maxGroup,
            texts: groups[maxGroup] || []
        },
        fullText: body.innerText.substring(0, 5000)
    };
})()
"""

ws.send(json.dumps({
    "id": 4,
    "method": "Runtime.evaluate",
    "params": {"expression": js_text, "returnByValue": True},
    "sessionId": session_id
}))

response = json.loads(ws.recv())
if 'result' in response and 'result' in response['result']:
    result = response['result']['result']['value']
    
    # 保存全文到文件（不打印避免编码问题）
    output_path = r'C:\Users\Haide\.openclaw\workspace\linkedin_feed_text.txt'
    full_text = result.get('fullText', '')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"=== LinkedIn Feed Page Text ===\n")
        f.write(f"Time: {datetime.now().isoformat()}\n\n")
        f.write(full_text)
    
    # 输出统计信息（避免特殊字符）
    print(f"Total text nodes: {result.get('totalTextNodes', 0)}")
    print(f"Groups count: {result.get('groupsCount', 0)}")
    print(f"Full text length: {len(full_text)} chars")
    print(f"Saved to: {output_path}")

ws.close()