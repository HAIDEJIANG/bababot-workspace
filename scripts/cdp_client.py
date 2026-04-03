#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP (Chrome DevTools Protocol) 客户端 v2
通过 WebSocket 直接连接浏览器，使用 Target.attachToTarget 方式
支持 Edge/Chrome 的远程调试端口
"""
import json
import websocket
import time
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime

class CDPClient:
    """CDP 客户端 - 通过 WebSocket 连接浏览器（使用 Target.attachToTarget）"""
    
    def __init__(self, host: str = "localhost", port: int = 9222):
        self.host = host
        self.port = port
        self.ws: Optional[websocket.WebSocket] = None
        self.session_id: Optional[str] = None
        self.msg_id = 0
        
    def get_browser_tabs(self) -> List[Dict[str, Any]]:
        """获取浏览器所有标签页信息"""
        try:
            response = requests.get(f"http://{self.host}:{self.port}/json", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[CDP] [ERR] 获取标签页失败：{e}")
            return []
    
    def find_linkedin_feed(self) -> Optional[Dict[str, Any]]:
        """查找已登录的 LinkedIn Feed 页面"""
        tabs = self.get_browser_tabs()
        for tab in tabs:
            url = tab.get('url', '')
            if 'linkedin.com/feed' in url and 'sign-in' not in url:
                return tab
        return None
    
    def connect(self, target_id: Optional[str] = None) -> bool:
        """连接到浏览器并附加到指定 target"""
        try:
            # 获取浏览器级别 WS URL
            version = requests.get(f"http://{self.host}:{self.port}/json/version", timeout=5).json()
            browser_ws_url = version.get('webSocketDebuggerUrl')
            
            if not browser_ws_url:
                print("[CDP] [ERR] 无法获取浏览器 WebSocket URL")
                return False
            
            # 连接浏览器（添加 origin header 解决 403 问题）
            origin = f"http://localhost:{self.port}"
            self.ws = websocket.create_connection(browser_ws_url, timeout=10, header=["Origin: " + origin])
            print(f"[CDP] [OK] 已连接到浏览器 (origin: {origin})")
            
            # 如果没有指定 target，使用第一个 LinkedIn Feed
            if not target_id:
                tab = self.find_linkedin_feed()
                if tab:
                    target_id = tab.get('id')
            
            if not target_id:
                print("[CDP] [ERR] 未找到目标页面")
                return False
            
            # 启用 Target 发现
            self._send("Target.setDiscoverTargets", {"discover": True})
            
            # 附加到 target
            result = self._send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
            self.session_id = result.get('result', {}).get('sessionId')
            
            if not self.session_id:
                print("[CDP] [ERR] 无法获取 Session ID")
                return False
            
            print(f"[CDP] [OK] 已附加到 target {target_id[:16]}... (Session: {self.session_id[:16]}...)")
            
            # 启用必要的 domains
            self._send_session("Page.enable")
            self._send_session("Runtime.enable")
            
            # 等待执行上下文创建（接收 Runtime.executionContextCreated 事件）
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"[CDP] [ERR] 连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.ws:
            self.ws.close()
            self.ws = None
            self.session_id = None
    
    def _send(self, method: str, params: Optional[Dict] = None) -> Dict:
        """发送 CDP 命令（浏览器级别）"""
        if not self.ws:
            return {"error": "Not connected"}
        
        self.msg_id += 1
        msg_id = self.msg_id
        message = {
            "id": msg_id,
            "method": method,
            "params": params or {}
        }
        
        self.ws.send(json.dumps(message))
        
        # 接收响应（可能需要跳过一些事件）
        while True:
            response = json.loads(self.ws.recv())
            if 'id' in response and response['id'] == msg_id:
                return response
    
    def _send_session(self, method: str, params: Optional[Dict] = None) -> Dict:
        """发送 CDP 命令（session 级别）"""
        if not self.ws or not self.session_id:
            return {"error": "Not connected"}
        
        self.msg_id += 1
        msg_id = self.msg_id
        message = {
            "id": msg_id,
            "method": method,
            "params": params or {},
            "sessionId": self.session_id
        }
        
        self.ws.send(json.dumps(message))
        
        # 接收响应（可能需要跳过一些事件）
        while True:
            response = json.loads(self.ws.recv())
            if 'id' in response and response['id'] == msg_id:
                return response
    
    def evaluate(self, expression: str) -> Dict:
        """执行 JavaScript 表达式"""
        return self._send_session("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
    
    def scroll_page(self, pixels: int = 500) -> bool:
        """向下滚动页面"""
        expr = f"window.scrollBy(0, {pixels});"
        result = self.evaluate(expr)
        return 'error' not in result
    
    def get_page_info(self) -> Dict:
        """获取页面基本信息"""
        info = {}
        
        # 获取标题
        result = self.evaluate("document.title")
        info['title'] = result.get('result', {}).get('result', {}).get('value', 'N/A')
        
        # 获取 URL
        result = self.evaluate("window.location.href")
        info['url'] = result.get('result', {}).get('result', {}).get('value', 'N/A')
        
        # 获取 readyState
        result = self.evaluate("document.readyState")
        info['readyState'] = result.get('result', {}).get('result', {}).get('value', 'N/A')
        
        # 获取正文长度
        result = self.evaluate("document.body ? document.body.innerText.length : 0")
        info['bodyTextLen'] = result.get('result', {}).get('result', {}).get('value', 0)
        
        return info
    
    def extract_posts(self) -> List[Dict[str, Any]]:
        """提取 LinkedIn 帖子 - v3 版本（全文分段法）"""
        # 先获取帖子数量
        js_count = """
        (function() {
            var fullText = document.body ? document.body.innerText : '';
            var segments = fullText.split('Feed post');
            return segments.length - 1;
        })()
        """
        result = self._send_session("Runtime.evaluate", {
            "expression": js_count,
            "returnByValue": True,
            "awaitPromise": True
        })
        
        post_count = result.get('result', {}).get('result', {}).get('value', 0)
        if post_count == 0:
            return []
        
        # 分批提取每个帖子（避免单次返回数据过大）
        posts = []
        for i in range(1, min(post_count + 1, 15)):  # 最多提取 14 个帖子
            js_extract = f"""
            (function() {{
                var fullText = document.body ? document.body.innerText : '';
                var segments = fullText.split('Feed post');
                if (segments.length < {i + 1}) return null;
                
                var segment = segments[{i}].trim();
                if (segment.length < 100) return null;
                
                var lines = segment.split('\\n').filter(function(l) {{ return l.trim().length > 0; }});
                if (lines.length < 2) return null;
                
                var author = lines[0].trim();
                var timestamp = null;
                var content = '';
                
                // 查找时间标记（如 "6h •", "18h •"）
                for (var j = 1; j < Math.min(5, lines.length); j++) {{
                    var line = lines[j];
                    if (line.match(/^[0-9]+[hm]s?[.•]/) || line.match(/[0-9]+[hm].*[•]/)) {{
                        timestamp = line.trim();
                        content = lines.slice(j + 1).join('\\n').substring(0, 1500);
                        break;
                    }}
                }}
                
                if (!timestamp) {{
                    content = lines.slice(1).join('\\n').substring(0, 1500);
                }}
                
                // 提取联系方式
                var contact = null;
                var emailMatch = content.match(/[\\w\\.-]+@[\\w\\.-]+\\.\\w+/);
                if (emailMatch) contact = emailMatch[0];
                
                return {{
                    author: author,
                    text: content,
                    timestamp: timestamp,
                    contact: contact,
                    hash: content.substring(0, 100)
                }};
            }})()
            """
            result = self._send_session("Runtime.evaluate", {
                "expression": js_extract,
                "returnByValue": True,
                "awaitPromise": True
            })
            
            post_data = result.get('result', {}).get('result', {}).get('value')
            if post_data:
                posts.append(post_data)
        
        return posts


def log(msg: str):
    """日志输出"""
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)


if __name__ == "__main__":
    log("CDP 客户端 v2 测试")
    client = CDPClient(port=9222)
    
    tabs = client.get_browser_tabs()
    log(f"找到 {len(tabs)} 个标签页")
    
    li_tab = client.find_linkedin_feed()
    if li_tab:
        log(f"[OK] 找到 LinkedIn Feed: {li_tab.get('title')}")
        
        if client.connect(li_tab.get('id')):
            log("获取页面信息...")
            info = client.get_page_info()
            log(f"  Title: {info.get('title', 'N/A')}")
            log(f"  URL: {info.get('url', 'N/A')}")
            log(f"  ReadyState: {info.get('readyState', 'N/A')}")
            log(f"  BodyText: {info.get('bodyTextLen', 0)} chars")
            
            log("\n提取帖子...")
            posts = client.extract_posts()
            log(f"找到 {len(posts)} 条帖子")
            
            for i, post in enumerate(posts[:5]):
                log(f"  [{i+1}] {post.get('author', 'Unknown')[:30]}... ({len(post.get('text', ''))} chars)")
            
            client.disconnect()
    else:
        log("[ERR] 未找到 LinkedIn Feed 页面")
