#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 1 小时采集脚本 - Edge 浏览器版 (v2)
复用已登录的 Edge 浏览器会话，更温和的采集方式
"""

import time
import json
import sys
import io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

# 配置
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)
DURATION_MINUTES = 60
SCROLL_PAUSE = 2

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - 60 分钟任务 (Edge 浏览器)")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        # 连接到 Edge 浏览器
        log("连接 Edge 浏览器...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=30000)
        log("连接成功")
        
        # 获取现有页面
        context = browser.contexts[0]
        pages = context.pages
        
        if len(pages) > 0:
            page = pages[0]
            log(f"使用现有页面：{page.url}")
        else:
            page = context.new_page()
            log("创建新页面")
        
        # 检查当前页面是否是 LinkedIn
        current_url = page.url
        
        if "linkedin.com" not in current_url.lower():
            log("当前页面不是 LinkedIn，尝试导航...")
            # 使用更温和的导航方式
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
        
        # 检查登录状态
        if "sign-in" in page.url.lower() or "login" in page.url.lower():
            log("等待登录确认...")
            for i in range(30):
                time.sleep(1)
                current_url = page.url
                if "feed" in current_url.lower() or "home" in current_url.lower():
                    log("登录确认成功！")
                    break
            else:
                log(f"当前 URL: {page.url}")
        
        log(f"当前页面：{page.url}")
        log(f"页面标题：{page.title()}")
        log("开始采集，目标时长：60 分钟")
        log("-" * 70)
        
        # 等待页面加载
        log("等待页面内容加载...")
        time.sleep(5)
        
        batch_num = 0
        while (datetime.now() - start_time).total_seconds() < DURATION_MINUTES * 60:
            batch_num += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            log(f"\n【批次 {batch_num}】已运行 {elapsed:.1f} 分钟")
            
            # 先检查页面是否还在
            try:
                current_url = page.url
                if "linkedin" not in current_url.lower():
                    log(f"页面已跳转到：{current_url}，尝试返回...")
                    page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
            except:
                log("页面连接丢失，尝试恢复...")
                try:
                    page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                except:
                    log("无法恢复页面，结束采集")
                    break
            
            # 滚动页面
            log("滚动页面...")
            for i in range(3):
                try:
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(SCROLL_PAUSE)
                except:
                    log("滚动失败，继续...")
                    break
            
            # 提取帖子
            try:
                posts_data = page.evaluate('''() => {
                    const posts = [];
                    // 尝试多种选择器
                    const selectors = [
                        'div[class*="update"]',
                        'div[data-id*="urn:li:activity"]',
                        'article',
                        'div[class*="feed-shared-update"]'
                    ];
                    
                    let elements = [];
                    selectors.forEach(sel => {
                        try {
                            const found = document.querySelectorAll(sel);
                            if (found.length > 0) {
                                elements = Array.from(found);
                            }
                        } catch(e) {}
                    });
                    
                    if (elements.length === 0) {
                        // 如果上面都没找到，尝试获取所有较大的文本块
                        const allDivs = document.querySelectorAll('div');
                        elements = Array.from(allDivs).filter(d => d.innerText.length > 200);
                    }
                    
                    elements.slice(0, 20).forEach(el => {
                        try {
                            const text = el.innerText;
                            if (text && text.trim().length > 100) {
                                posts.push({
                                    text: text.substring(0, 1000).replace(/\\n/g, ' '),
                                    url: window.location.href,
                                    time: new Date().toISOString()
                                });
                            }
                        } catch(e) {}
                    });
                    return posts;
                }''')
                
                new_count = 0
                for post in posts_data:
                    post_hash = hash(post['text'])
                    if post_hash not in seen_hashes:
                        seen_hashes.add(post_hash)
                        all_posts.append(post)
                        new_count += 1
                
                log(f"看到 {len(posts_data)} 个帖子，新增 {new_count} 个，总计 {len(all_posts)} 个")
                
            except Exception as e:
                log(f"提取失败：{e}")
            
            # 保存中间结果
            if batch_num % 2 == 0 and len(all_posts) > 0:
                save_results(all_posts, start_time)
                log(f"已保存 {len(all_posts)} 条记录")
            
            # 刷新页面（每 15 分钟）
            if batch_num % 5 == 0:
                log("刷新页面...")
                try:
                    page.reload(wait_until="domcontentloaded", timeout=30000)
                    time.sleep(5)
                except:
                    log("刷新失败，继续...")
            
            # 检查是否应该停止
            remaining = DURATION_MINUTES - (datetime.now() - start_time).total_seconds() / 60
            if remaining <= 0:
                break
        
        # 最终保存
        if len(all_posts) > 0:
            save_results(all_posts, start_time)
            log("\n" + "=" * 70)
            log(f"采集完成！总计 {len(all_posts)} 条唯一帖子")
            log(f"输出文件：{OUTPUT_DIR / 'linkedin_1hour_collection.csv'}")
            log("=" * 70)
        else:
            log("\n未采集到数据")
        
        browser.close()

def save_results(posts, start_time):
    """保存结果到 CSV"""
    output_file = OUTPUT_DIR / "linkedin_1hour_collection.csv"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("timestamp,text,url\n")
        for post in posts:
            text_escaped = post['text'].replace('"', '""')
            f.write(f'"{post["time"]}","{text_escaped}","{post["url"]}"\n')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n用户中断")
    except Exception as e:
        log(f"错误：{e}")
        import traceback
        traceback.print_exc()
