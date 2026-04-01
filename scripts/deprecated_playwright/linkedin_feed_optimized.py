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
    log("LinkedIn Feed 采集 - 懒加载优化版")
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
        
        log("等待页面初始加载...")
        time.sleep(10)
        
        log("开始采集 (30 分钟，带懒加载)...")
        posts = []
        seen = set()
        start = time.time()
        end = start + 30*60
        scroll = 0
        consecutive_no_new = 0
        
        while time.time() < end:
            try:
                # 尝试点击 "New posts" 按钮
                try:
                    clicked = target.evaluate('''() => {
                        var btn = document.querySelector('button:has-text("New posts"), button:has-text("新帖子")');
                        if(btn) { btn.click(); return true; }
                        return false;
                    }''')
                    if clicked:
                        log("  🔄 点击了 New posts 按钮")
                        time.sleep(5)
                except:
                    pass
                
                # 提取帖子 - 使用更宽的选择器
                data = target.evaluate('''() => {
                    var posts = [];
                    var all = document.querySelectorAll('*');
                    for(var i=0; i<all.length; i++) {
                        var t = all[i].innerText;
                        if(t && t.length > 200 && t.length < 3000) {
                            if(t.indexOf('Feed post') >= 0 || t.indexOf('Start a post') < 0) {
                                if(posts.length < 100) {
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
                
                if new == 0:
                    consecutive_no_new += 1
                else:
                    consecutive_no_new = 0
                
                # 如果连续 5 次没有新增，等待更长时间让懒加载生效
                if consecutive_no_new >= 5:
                    log("  ⏳ 连续无新增，等待懒加载...")
                    time.sleep(15)
                    consecutive_no_new = 0
                
                # 滚动更长的距离
                target.evaluate('window.scrollBy(0, 2000)')
                scroll += 1
                
                # 等待更长时间让新内容加载
                time.sleep(12)
                
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
