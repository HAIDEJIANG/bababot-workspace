#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Feed 采集 - 直接 CDP 协议
通过 WebSocket 连接 Edge 浏览器 (port 18800)
采集航材相关帖子，持续 60 分钟
"""

import sys
import io
import time
import json
import re
import requests
import websocket
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 配置 ====================

CDP_PORT = 18800
CDP_HTTP_URL = f"http://127.0.0.1:{CDP_PORT}"
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

DURATION_MINUTES = 60
SCROLL_PAUSE = 4
SCROLL_PIXELS = 800

# PN 号正则
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',
    r'\b[A-Z]{1,2}-[0-9]{4,}-[0-9]{2,}\b',
    r'\b[A-Z]{2}[0-9]{4}[A-Z]?\b',  # 如 HG2050BC
]

# 业务关键词
BUSINESS_KEYWORDS = [
    'available', 'stock', 'price', 'quote', 'RFQ', 'offer', 'sale', 'buy', 'urgent',
    '现货', '价格', '询价', '报价', '出售', '采购', '急购',
    'PN', 'P/N', 'Part Number', '件号', 'S/N', 'serial',
    'CFM56', 'V2500', 'A320', 'B737', 'LEAP', 'PW100', 'PW200', 'GE90', 'Trent',
    'engine', 'landing gear', 'APU', 'rotable', 'surplus', 'spare',
    'aircraft', 'helicopter', 'component', 'module', 'blade', 'fuel',
    'starter', 'generator', 'pump', 'valve', 'actuator', 'sensor',
    'ADIRU', 'MCP', 'TCAS', 'display', 'avionics',
]

# ==================== 工具函数 ====================

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def extract_pn(text: str) -> list:
    pns = []
    for pattern in PN_PATTERNS:
        pns.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(pns))

def has_business_intent(text: str) -> bool:
    text_lower = text.lower()
    for keyword in BUSINESS_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

class LinkedInCollector:
    def __init__(self):
        self.ws = None
        self.target_id = None
        self.session_id = None
        self.msg_id = 0
        
    def get_tabs(self):
        """获取所有浏览器标签页"""
        r = requests.get(f"{CDP_HTTP_URL}/json/list", timeout=10)
        return r.json()
    
    def find_linkedin_tab(self):
        """找到 LinkedIn Feed 标签页"""
        tabs = self.get_tabs()
        for tab in tabs:
            url = tab.get('url', '')
            title = tab.get('title', '')
            if 'linkedin.com' in url.lower() or 'linkedin' in title.lower():
                return tab
        return None
    
    def connect(self):
        """连接到 LinkedIn 标签页"""
        tab = self.find_linkedin_tab()
        if not tab:
            log("未找到 LinkedIn 标签页!")
            return False
        
        self.target_id = tab.get('id')
        ws_url = tab.get('webSocketDebuggerUrl')
        
        if not ws_url:
            log("无法获取 WebSocket URL!")
            return False
        
        log(f"连接标签页: {tab.get('title', 'LinkedIn')}")
        
        self.ws = websocket.create_connection(ws_url, timeout=10)
        
        # 发送 Page.enable 命令
        self.send_cmd("Page.enable")
        
        # 发送 Runtime.enable 命令
        self.send_cmd("Runtime.enable")
        
        return True
    
    def send_cmd(self, method, params=None):
        """发送 CDP 命令"""
        self.msg_id += 1
        msg = {
            "id": self.msg_id,
            "method": method,
            "params": params or {}
        }
        self.ws.send(json.dumps(msg))
        
        # 等待响应
        while True:
            resp = json.loads(self.ws.recv())
            if resp.get('id') == self.msg_id:
                return resp
    
    def scroll(self, pixels=SCROLL_PIXELS):
        """滚动页面"""
        self.send_cmd("Runtime.evaluate", {
            "expression": f"window.scrollBy(0, {pixels})"
        })
    
    def get_posts_text(self):
        """获取页面中的帖子文本"""
        result = self.send_cmd("Runtime.evaluate", {
            "expression": """
            (() => {
                let posts = [];
                let seen = new Set();
                
                // 遍历所有可见的文本块
                document.querySelectorAll('div, article, section, span, p').forEach(el => {
                    let text = el.innerText || '';
                    text = text.trim();
                    
                    // 去重
                    let key = text.slice(0, 100);
                    if (seen.has(key) || text.length < 50 || text.length > 3000) return;
                    seen.add(key);
                    
                    // 检查是否是帖子内容（包含业务关键词或 PN）
                    let keywords = ['CFM56', 'V2500', 'A320', 'B737', 'LEAP', 'engine', 'landing', 'APU', 
                                  'stock', 'price', 'available', 'PN', 'P/N', '件号', '现货', '出售',
                                  'starter', 'generator', 'pump', 'valve', 'actuator', 'sensor',
                                  'ADIRU', 'MCP', 'TCAS', 'surplus', 'rotable', 'aircraft'];
                    
                    for (let kw of keywords) {
                        if (text.toLowerCase().includes(kw.toLowerCase())) {
                            posts.push(text);
                            break;
                        }
                    }
                });
                
                return posts;
            })()
            """,
            "returnByValue": True
        })
        
        if 'result' in result and 'result' in result['result']:
            value = result['result']['result'].get('value', [])
            return value if isinstance(value, list) else []
        return []
    
    def close(self):
        if self.ws:
            self.ws.close()

def save_posts(posts: list, output_file: Path):
    """保存帖子到 CSV"""
    if not posts:
        return
    
    # 读取已有数据去重
    existing = set()
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[1:]:
                if line.strip():
                    existing.add(line[:100])
    
    # 追加新数据
    new_count = 0
    with open(output_file, 'a', encoding='utf-8') as f:
        if not output_file.exists() or output_file.stat().st_size == 0:
            f.write("采集时间,内容摘要,零件号,业务意图\n")
        
        for post in posts:
            text = post.get('text', '')[:500].replace(',', ' ').replace('\n', ' ').replace('\r', '')
            if text[:100] in existing:
                continue
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pns = ','.join(post.get('pn', []))
            business = '是' if post.get('business_intent') else '否'
            
            f.write(f"{timestamp},{text},{pns},{business}\n")
            new_count += 1
    
    return new_count

def main():
    log("=" * 60)
    log("LinkedIn Feed 采集 - CDP 直连")
    log(f"目标时长: {DURATION_MINUTES} 分钟")
    log("=" * 60)
    
    collector = LinkedInCollector()
    
    if not collector.connect():
        log("连接失败!")
        return
    
    # 输出文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = OUTPUT_DIR / f"LinkedIn_CDP_{timestamp}.csv"
    
    all_posts = []
    scroll_count = 0
    start_time = time.time()
    end_time = start_time + DURATION_MINUTES * 60
    
    log("开始采集...")
    
    while time.time() < end_time:
        scroll_count += 1
        remaining = int((end_time - time.time()) / 60)
        
        # 滚动
        collector.scroll()
        time.sleep(SCROLL_PAUSE)
        
        # 提取
        texts = collector.get_posts_text()
        
        found = 0
        for text in texts:
            pns = extract_pn(text)
            business = has_business_intent(text)
            
            if business or pns:
                post = {
                    'text': text,
                    'pn': pns,
                    'business_intent': business
                }
                all_posts.append(post)
                found += 1
        
        log(f"滚动 #{scroll_count} | 剩余 {remaining}分钟 | 发现 {found} 条 | 总计 {len(all_posts)} 条")
        
        # 每 10 次滚动保存
        if scroll_count % 10 == 0:
            new_count = save_posts(all_posts, output_file)
            log(f"  保存 {new_count} 条新帖子")
        
        # 随机等待
        wait = SCROLL_PAUSE + (scroll_count % 5) * 0.5
        time.sleep(wait)
    
    # 最终保存
    save_posts(all_posts, output_file)
    
    log("=" * 60)
    log("采集完成!")
    log(f"总滚动: {scroll_count} 次")
    log(f"总帖子: {len(all_posts)} 条")
    log(f"文件: {output_file}")
    log("=" * 60)
    
    collector.close()

if __name__ == "__main__":
    main()