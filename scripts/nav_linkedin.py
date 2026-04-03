import requests
import json
import websocket
import time

# 获取 CDP 目标列表
resp = requests.get('http://localhost:9222/json')
targets = resp.json()

# 找到页面标签
page_target = None
for t in targets:
    if t.get('type') == 'page':
        page_target = t
        break

if page_target:
    print(f"找到页面: {page_target.get('url', 'about:blank')}")
    
    # 连接 WebSocket
    ws_url = page_target['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url)
    
    # 发送 Page.navigate 命令
    cmd = {'id': 1, 'method': 'Page.navigate', 'params': {'url': 'https://www.linkedin.com/feed'}}
    ws.send(json.dumps(cmd))
    
    time.sleep(3)
    
    try:
        result = ws.recv()
        print(f"导航结果: {result[:200]}")
    except:
        pass
    
    ws.close()
    print("已导航到 LinkedIn Feed")
else:
    print("未找到页面目标")