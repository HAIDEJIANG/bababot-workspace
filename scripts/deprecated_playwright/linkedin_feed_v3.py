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
    log("LinkedIn Feed 采集 - data-test-id 选择器")
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
        
        # 查找所有可能的帖子选择器
        log("查找帖子容器...")
        selectors_test = [
            '[data-test-id="feed-update"]',
            '[data-test-id="update"]',
            '[data-id*="urn:li:activity"]',
            '[data-id*="urn:li:share"]',
            '.update-v2',
            'article',
            'div.update-v2',
        ]
        
        for sel in selectors_test:
            try:
                count = target.evaluate(f'''() => document.querySelectorAll('{sel}').length''')
                log(f"  {sel}: {count}个")
            except:
                log(f"  {sel}: 无法查询")
        
        log("\n开始采集 (30 分钟)...")
        posts = []
        seen = set()
        start = time.time()
        end = start + 30*60
        scroll = 0
        
        while time.time() < end:
            try:
                # 使用多种选择器组合
                data = target.evaluate('''() => {
                    var posts = [];
                    // 尝试所有可能的选择器
                    var selectors = [
                        '[data-id*="urn:li:activity"]',
                        '[data-id*="urn:li:share"]',
                        'article',
                        'div.update-v2'
                    ];
                    
                    for(var s of selectors) {
                        var els = document.querySelectorAll(s);
                        for(var i=0; i<els.length; i++) {
                            var t = els[i].innerText;
                            if(t && t.length > 150 && t.length < 5000) {
                                // 排除 CSS/JS 内容
                                if(t.indexOf('cursor:pointer') < 0 &&
                                   t.indexOf('data-v-') < 0 &&
                                   t.indexOf('.upgrade-dialog') < 0 &&
                                   t.indexOf('function(') < 0) {
                                    posts.push(t.replace(/\\n/g, ' ').substring(0, 2000));
                                }
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
