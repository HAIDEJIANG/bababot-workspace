#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集 - 最简版本
使用 CDP 直接操作已打开的 Edge 标签页，不创建新页面
"""

import time
import sys
import io
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
    log("=" * 70)
    log("LinkedIn 采集 - CDP 直连模式")
    log("=" * 70)
    
    with sync_playwright() as p:
        # 连接浏览器
        log("连接 Edge 浏览器 (CDP)...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
        log("连接成功")
        
        # 列出所有页面
        contexts = browser.contexts
        log(f"找到 {len(contexts)} 个浏览器上下文")
        
        all_pages = []
        for ctx in contexts:
            pages = ctx.pages
            for page in pages:
                try:
                    url = page.url
                    title = page.title()
                    all_pages.append((page, url, title))
                    log(f"  页面：{url[:80]}... - {title[:50]}...")
                except:
                    pass
        
        if not all_pages:
            log("没有找到任何页面")
            browser.close()
            return
        
        # 查找 LinkedIn 页面
        linkedin_page = None
        for page, url, title in all_pages:
            if "linkedin.com" in url.lower():
                linkedin_page = page
                log(f"\n找到 LinkedIn 页面：{url}")
                break
        
        if not linkedin_page:
            log("未找到已打开的 LinkedIn 页面")
            log("请在 Edge 浏览器中打开 https://www.linkedin.com/feed/")
            log("等待 60 秒...")
            time.sleep(60)
            
            # 再检查一次
            for ctx in contexts:
                for page in ctx.pages:
                    try:
                        if "linkedin.com" in page.url.lower():
                            linkedin_page = page
                            log(f"找到 LinkedIn 页面：{page.url}")
                            break
                    except:
                        pass
        
        if not linkedin_page:
            log("仍未找到 LinkedIn 页面，结束")
            browser.close()
            return
        
        # 切换到 LinkedIn 页面
        page = linkedin_page
        page.bring_to_front()
        
        log(f"\n当前页面：{page.url}")
        log("等待 5 秒让页面稳定...")
        time.sleep(5)
        
        # 尝试获取帖子
        log("\n尝试提取帖子...")
        try:
            posts = page.evaluate('''() => {
                const results = [];
                const elements = document.querySelectorAll('[data-id*="urn:li:activity"], div[class*="update"]');
                elements.forEach(el => {
                    const text = el.innerText;
                    if (text && text.length > 100) {
                        results.push(text.substring(0, 500));
                    }
                });
                return results;
            }''')
            
            log(f"找到 {len(posts)} 个帖子")
            for i, post in enumerate(posts[:3]):
                log(f"\n帖子 {i+1}:")
                log(f"{post[:200]}...")
                
        except Exception as e:
            log(f"提取失败：{e}")
        
        log("\n" + "=" * 70)
        log("测试完成")
        browser.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"错误：{e}")
        import traceback
        traceback.print_exc()
