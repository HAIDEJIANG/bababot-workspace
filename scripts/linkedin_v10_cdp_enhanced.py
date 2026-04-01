#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集脚本 v10.0 - CDP 协议增强版

改进内容：
1. 使用 LinkedIn 内部数据属性（data-id, urn:li:activity）而非 CSS 选择器
2. 通过 JavaScript 注入提取帖子，绕过动态类名问题
3. 使用多个特征识别帖子容器

用法：
  python scripts/linkedin_v10_cdp_enhanced.py --duration 5
"""

import sys
import io
import time
import json
import re
import argparse
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from cdp_client import CDPClient, log

# ==================== 配置 ====================

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_DURATION_MINUTES = 5
SCROLL_PAUSE = 3
SCROLL_PIXELS = 800

# PN 号识别正则
PN_PATTERNS = [
    r'\b[0-9]{6,}-[0-9]{2,}\b',
    r'\b[A-Z]{2,}[0-9]{4,}-[0-9]{2,}\b',
    r'\b[0-9]{4,}[A-Z]{1,3}-[0-9]{2,}\b',
]

# 业务关键词
BUSINESS_KEYWORDS = [
    'available', 'stock', 'price', 'quote', 'RFQ', 'offer',
    '现货', '价格', '询价', '报价', '出售', '采购',
    'PN', 'P/N', 'Part Number', '件号',
    'CFM56', 'V2500', 'A320', 'B737', 'engine', 'landing gear', 'APU',
]

# ==================== 工具函数 ====================

def extract_pn(text: str) -> list:
    pns = []
    for pattern in PN_PATTERNS:
        pns.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(pns))

def has_business_intent(text: str) -> bool:
    text_lower = text.lower()
    score = 0
    for keyword in BUSINESS_KEYWORDS:
        if keyword.lower() in text_lower:
            score += 1
    return score >= 2

def save_posts(posts: list, output_file: Path):
    if not posts:
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("采集时间，发帖人，发布时间，内容摘要，零件号，业务意图，原始链接\n")
        
        for post in posts:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            author = post.get('author', 'Unknown').replace(',', ' ')
            pub_time = post.get('timestamp', '') or ''
            content = post.get('text', '')[:500].replace(',', ' ').replace('\n', ' ')
            pns = ','.join(post.get('pn', []))
            business = '是' if post.get('business_intent') else '否'
            link = post.get('link', '')
            
            f.write(f"{timestamp},{author},{pub_time},{content},{pns},{business},{link}\n")
    
    log(f"[OK] 已保存 {len(posts)} 条帖子到：{output_file}")

def save_raw_posts(posts: list, output_file: Path):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    log(f"[OK] 已保存原始数据到：{output_file}")

# ==================== 增强版帖子提取 ====================

def extract_linkedin_posts_enhanced(client: CDPClient) -> list:
    """
    增强版 LinkedIn 帖子提取
    使用多种方法识别帖子，不依赖 CSS 类名
    """
    
    # 方法 1: 通过 LinkedIn 内部数据 ID 识别
    js_extract = """
    (function() {
        var posts = [];
        
        // 方法 1: 查找包含 urn:li:activity 或 urn:li:share 的元素
        var allElements = document.querySelectorAll('*');
        var seenUrls = new Set();
        
        for (var i = 0; i < allElements.length; i++) {
            var el = allElements[i];
            
            // 检查是否有 LinkedIn 活动 ID
            var urnId = el.getAttribute('data-id');
            var ariaLabel = el.getAttribute('aria-label');
            
            if (urnId && (urnId.includes('urn:li:activity') || urnId.includes('urn:li:share'))) {
                if (seenUrls.has(urnId)) continue;
                seenUrls.add(urnId);
                
                // 获取帖子文本
                var text = el.innerText || '';
                if (text.length < 100) continue;
                
                // 获取发帖人
                var authorEl = el.querySelector('[href*="/in/"]');
                var author = authorEl ? authorEl.innerText : 'Unknown';
                
                // 获取时间
                var timeEl = el.querySelector('time');
                var timestamp = timeEl ? timeEl.getAttribute('datetime') : null;
                
                posts.push({
                    id: urnId,
                    author: author,
                    text: text.substring(0, 3000),
                    timestamp: timestamp,
                    hash: text.substring(0, 200)
                });
            }
        }
        
        // 方法 2: 查找包含完整帖子结构的 article 标签
        var articles = document.querySelectorAll('article');
        for (var i = 0; i < articles.length; i++) {
            var el = articles[i];
            var text = el.innerText || '';
            
            if (text.length < 200) continue;
            
            // 检查是否有 LinkedIn 特征
            var hasLinkedinFeature = text.includes(' reposted this') || 
                                     text.includes(' liked this') ||
                                     text.includes('See less') ||
                                     text.includes('See more');
            
            if (!hasLinkedinFeature) continue;
            
            var authorEl = el.querySelector('[href*="/in/"]');
            var author = authorEl ? authorEl.innerText : 'Unknown';
            
            var timeEl = el.querySelector('time');
            var timestamp = timeEl ? timeEl.getAttribute('datetime') : null;
            
            // 生成唯一 ID
            var postId = 'article_' + i + '_' + text.substring(0, 50);
            
            posts.push({
                id: postId,
                author: author,
                text: text.substring(0, 3000),
                timestamp: timestamp,
                hash: text.substring(0, 200)
            });
        }
        
        return posts;
    })()
    """
    
    result = client._send_session("Runtime.evaluate", {
        "expression": js_extract,
        "returnByValue": True,
        "awaitPromise": True
    })
    
    posts = result.get('result', {}).get('value', [])
    return posts if posts else []

# ==================== 主采集流程 ====================

def collect_linkedin_posts(duration_minutes: int, port: int):
    log("=" * 70)
    log("LinkedIn 采集 v10.0 - CDP 协议增强版")
    log("=" * 70)
    log(f"采集时长：{duration_minutes} 分钟")
    log(f"CDP 端口：{port}")
    log(f"输出目录：{OUTPUT_DIR}")
    
    client = CDPClient(port=port)
    
    tabs = client.get_browser_tabs()
    if not tabs:
        log("[ERR] 无法连接到浏览器")
        return
    
    log(f"[OK] 浏览器已连接，找到 {len(tabs)} 个标签页")
    
    linkedin_tab = client.find_linkedin_feed()
    if not linkedin_tab:
        log("[ERR] 未找到 LinkedIn Feed 页面")
        return
    
    log(f"[OK] 找到 LinkedIn Feed: {linkedin_tab.get('title', 'N/A')}")
    
    if not client.connect(linkedin_tab.get('id')):
        log("[ERR] CDP 连接失败")
        return
    
    page_info = client.get_page_info()
    log(f"页面信息：Title={page_info.get('title', 'N/A')}, BodyText={page_info.get('bodyTextLen', 0)} chars")
    
    if page_info.get('bodyTextLen', 0) == 0:
        log("[WARN] 页面内容为空，等待加载...")
        time.sleep(3)
    
    log("\n" + "=" * 70)
    log("开始采集...")
    log("=" * 70)
    
    posts_collected = []
    seen_hashes = set()
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    scroll_count = 0
    
    while time.time() < end_time:
        try:
            # 使用增强版提取
            posts = extract_linkedin_posts_enhanced(client)
            new_count = 0
            
            for post_data in posts:
                post_hash = hash(post_data.get('hash', ''))
                
                if post_hash not in seen_hashes:
                    seen_hashes.add(post_hash)
                    
                    pns = extract_pn(post_data.get('text', ''))
                    business = has_business_intent(post_data.get('text', ''))
                    
                    post_record = {
                        'author': post_data.get('author', 'Unknown'),
                        'text': post_data.get('text', ''),
                        'timestamp': post_data.get('timestamp'),
                        'pn': pns,
                        'business_intent': business,
                        'link': f"https://www.linkedin.com/feed/update/{post_data.get('id', '')}",
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    posts_collected.append(post_record)
                    new_count += 1
                    
                    if business or pns:
                        log(f"[TARGET] 高价值帖子：{post_data.get('author', 'Unknown')[:30]} | PN: {pns if pns else 'N/A'}")
            
            if new_count > 0:
                log(f"[NEW] 新增 {new_count} 条帖子（总计：{len(posts_collected)}）")
            else:
                log(f"[INFO] 本轮未找到新帖子，当前总计：{len(posts_collected)}")
            
            # 滚动页面
            log(f"[SCROLL] 滚动页面 (第 {scroll_count + 1} 次)")
            client.scroll_page(SCROLL_PIXELS)
            scroll_count += 1
            time.sleep(SCROLL_PAUSE)
            
            # 每 5 分钟保存一次进度
            elapsed = (time.time() - start_time) / 60
            if int(elapsed) % 5 == 0 and int(elapsed) > 0:
                temp_file = OUTPUT_DIR / f"linkedin_posts_temp_{datetime.now().strftime('%H%M')}.json"
                save_raw_posts(posts_collected, temp_file)
        
        except Exception as e:
            log(f"[WARN] 采集异常：{e}")
            time.sleep(5)
    
    client.disconnect()
    
    elapsed_minutes = (time.time() - start_time) / 60
    log("\n" + "=" * 70)
    log("采集完成")
    log("=" * 70)
    log(f"运行时长：{elapsed_minutes:.1f} 分钟")
    log(f"采集帖子：{len(posts_collected)} 条")
    log(f"滚动次数：{scroll_count} 次")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = OUTPUT_DIR / f"linkedin_posts_{timestamp}.csv"
    json_file = OUTPUT_DIR / f"linkedin_posts_{timestamp}.json"
    
    save_posts(posts_collected, csv_file)
    save_raw_posts(posts_collected, json_file)
    
    high_value = [p for p in posts_collected if p.get('business_intent') or p.get('pn')]
    if high_value:
        log(f"\n[TARGET] 高价值帖子：{len(high_value)} 条")
        for post in high_value[:10]:
            log(f"  - {post.get('author', 'Unknown')[:40]} | PN: {post.get('pn', ['N/A'])[0]}")
    
    return len(posts_collected)

# ==================== 命令行入口 ====================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn 采集 v10 - CDP 增强版')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION_MINUTES,
                        help=f'采集时长（分钟），默认 {DEFAULT_DURATION_MINUTES}')
    parser.add_argument('--port', type=int, default=9222,
                        help='CDP 调试端口，默认 9222')
    
    args = parser.parse_args()
    
    try:
        collect_linkedin_posts(args.duration, args.port)
    except KeyboardInterrupt:
        log("\n[WARN] 用户中断")
    except Exception as e:
        log(f"\n[ERR] 程序异常：{e}")
        import traceback
        traceback.print_exc()
