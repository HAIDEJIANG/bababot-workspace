#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, time
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("="*60)
    log("LinkedIn Feed 采集 - 精准选择器版")
    log("="*60)
    
    with sync_playwright() as p:
        log("连接 Edge (CDP 9223)...")
        browser = p.chromium.connect_over_cdp("http://localhost:9223", timeout=15000)
        
        context = browser.contexts[0]
        target = None
        
        for page in context.pages:
            try:
                if 'linkedin.com/feed' in page.url and 'sign-in' not in page.url:
                    target = page
                    log("✅ 找到 Feed 页面")
                    break
            except: continue
        
        if not target:
            log("❌ 未找到 Feed 页面")
            browser.close()
            return
        
        log("等待页面加载...")
        time.sleep(10)
        
        log("开始采集 (30 分钟)...")
        posts = []
        seen = set()
        start = time.time()
        end = start + 30*60
        scroll = 0
        
        while time.time() < end:
            try:
                # 使用精准选择器提取帖子
                data = target.evaluate('''() => {
                    var posts = [];
                    // LinkedIn 帖子标准选择器
                    var articles = document.querySelectorAll('div.update-v2, article, div[data-id*="urn:li:activity"]');
                    
                    for(var i=0; i<articles.length; i++) {
                        var text = articles[i].innerText;
                        
                        // 过滤条件
                        if(text && text.length > 150 && text.length < 5000) {
                            // 排除非帖子内容
                            if(text.indexOf('Start a post') < 0 && 
                               text.indexOf('Upgrade to') < 0 &&
                               text.indexOf('.upgrade-dialog') < 0 &&
                               text.indexOf('data-v-') < 0 &&
                               text.indexOf('cursor:pointer') < 0) {
                                
                                posts.push(text.replace(/\\n/g, ' ').substring(0, 2000));
                            }
                        }
                    }
                    return posts;
                }''')
                
                new = 0
                for t in data:
                    h = hash(t)
                    if h not in seen:
                        seen.add(h)
                        posts.append({'text': t, 'time': datetime.now().isoformat()})
                        new += 1
                
                elapsed = int(time.time() - start) // 60
                log(f"滚动#{scroll} | 累计:{len(posts)} | 新增:{new} | {elapsed}m")
                
                # 滚动
                target.evaluate('window.scrollBy(0, 1500)')
                scroll += 1
                time.sleep(10)
                
            except Exception as e:
                log(f"错误：{str(e)[:100]}")
                time.sleep(5)
        
        # 保存
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv = OUTPUT_DIR / f"linkedin_feed_{ts}.csv"
        with open(csv, 'w', encoding='utf-8') as f:
            f.write("序号，内容，时间\n")
            for i, p in enumerate(posts):
                text = p["text"][:500].replace('"', '""')
                f.write(f'{i},"{text}","{p["time"]}"\n')
        
        log(f"\n✅ 完成！采集 {len(posts)} 条帖子")
        log(f"保存：{csv}")
        browser.close()

if __name__ == '__main__':
    main()
