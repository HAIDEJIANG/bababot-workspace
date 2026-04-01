#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, time
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9223", timeout=15000)
    context = browser.contexts[0]
    
    for page in context.pages:
        if "linkedin.com/feed" in page.url:
            print("找到 Feed 页面")
            time.sleep(5)
            
            posts = page.evaluate("""() => {
                var posts = [];
                var all = document.querySelectorAll('*');
                for(var i=0; i<all.length; i++) {
                    var t = all[i].innerText;
                    if(t && t.length > 200 && t.length < 3000 && t.indexOf('Feed post') >= 0) {
                        posts.push(t.replace(/\\n/g, ' ').substring(0, 2000));
                    }
                }
                return posts;
            }""")
            
            print(f"找到 {len(posts)} 条帖子")
            
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv = OUTPUT_DIR / f"linkedin_feed_{ts}.csv"
            with open(csv, "w", encoding="utf-8") as f:
                f.write("序号，内容，时间\n")
                for i, p in enumerate(posts):
                    f.write(f'{i},"{p[:500]}","{datetime.now().isoformat()}"\n')
            
            print(f"已保存：{csv}")
            break
    
    browser.close()
