#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 1 小时采集脚本 - 专用版本
直接启动浏览器，采集 Feed 信息流 60 分钟
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
USER_DATA_DIR = r"C:\Users\Haide\AppData\Local\OpenClaw\BrowserData"
DURATION_MINUTES = 60
SCROLL_PAUSE = 3

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("=" * 70)
    log("LinkedIn Feed 采集 - 60 分钟任务")
    log(f"输出目录：{OUTPUT_DIR}")
    log("=" * 70)
    
    start_time = datetime.now()
    all_posts = []
    seen_hashes = set()
    
    with sync_playwright() as p:
        # 启动浏览器
        log("启动浏览器...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
            timeout=60000
        )
        log("浏览器启动成功")
        
        # 获取或创建页面
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # 访问 LinkedIn
        log("访问 LinkedIn Feed...")
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=60000)
        
        # 检查登录状态
        if "sign-in" in page.url.lower():
            log("⚠️ 检测到登录页面，等待手动登录...")
            log("请在浏览器窗口中登录 LinkedIn")
            for i in range(60):  # 最多等待 60 秒
                time.sleep(1)
                if "feed" in page.url.lower():
                    log("✅ 登录成功！")
                    break
            else:
                if "sign-in" in page.url.lower():
                    log("❌ 登录超时，继续尝试...")
        
        log(f"当前页面：{page.url}")
        log("开始采集，目标时长：60 分钟")
        log("-" * 70)
        
        batch_num = 0
        while (datetime.now() - start_time).total_seconds() < DURATION_MINUTES * 60:
            batch_num += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            log(f"\n【批次 {batch_num}】已运行 {elapsed:.1f} 分钟")
            
            # 滚动页面
            log("滚动页面...")
            for i in range(5):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(SCROLL_PAUSE)
            
            # 提取帖子
            try:
                posts_data = page.evaluate('''() => {
                    const posts = [];
                    const elements = document.querySelectorAll('div[class*="update"], div[data-id*="urn:li:activity"]');
                    elements.forEach(el => {
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
            if batch_num % 2 == 0:
                save_results(all_posts, start_time)
                log(f"已保存 {len(all_posts)} 条记录")
            
            # 刷新页面（每 15 分钟）
            if batch_num % 5 == 0:
                log("刷新页面...")
                page.reload(timeout=30000)
                time.sleep(5)
            
            # 检查是否应该停止
            remaining = DURATION_MINUTES - (datetime.now() - start_time).total_seconds() / 60
            if remaining <= 0:
                break
        
        # 最终保存
        save_results(all_posts, start_time)
        log("\n" + "=" * 70)
        log(f"采集完成！总计 {len(all_posts)} 条唯一帖子")
        log(f"输出文件：{OUTPUT_DIR / 'linkedin_1hour_collection.csv'}")
        log("=" * 70)
        
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
