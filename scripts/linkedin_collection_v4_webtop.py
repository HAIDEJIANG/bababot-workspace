#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 深度采集脚本 v4.0 - WebTop 持久化浏览器版

更新内容：
1. ✅ 使用 WebTop 持久化浏览器（Cookie 永久保存）
2. ✅ 无需反复登录 LinkedIn
3. ✅ 支持多脚本共享浏览器会话
4. ✅ 自动连接已运行的浏览器实例

使用前提：
- 先运行：python scripts/webtop/webtop_local.py --start
- 首次需要手动登录 LinkedIn
"""

import time
import json
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright
from browser_config import create_browser_context

# ==================== 配置 ====================

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

# 采集配置
TARGET_DURATION_MINUTES = 60  # 目标采集时长（分钟）
BATCH_DURATION_MINUTES = 15  # 每批次时长
BATCH_COUNT = 4  # 批次数
BATCH_INTERVAL_SECONDS = 30  # 批次间等待

# 重复度控制
DUPLICATE_THRESHOLD_INITIAL = 0.5  # 初始阈值 50%
DUPLICATE_THRESHOLD_MAX = 0.8  # 最大阈值 80%

# 浏览器管理
SCROLL_PAUSE_SECONDS = 3  # 滚动等待时间
MAX_SCROLLS_PER_CYCLE = 10  # 每轮最大滚动次数

# 日志文件
run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = OUTPUT_DIR / f"linkedin_collection_log_v4_{run_id}.txt"
results_file = OUTPUT_DIR / f"linkedin_posts_batch_v4_{run_id}.csv"
state_file = OUTPUT_DIR / f"linkedin_collection_state_v4_{run_id}.json"

# ==================== 状态追踪 ====================

class CollectionState:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.current_batch = 0
        self.total_posts_seen = 0
        self.unique_posts = 0
        self.duplicate_posts = 0
        self.refresh_count = 0
        self.scroll_count = 0
        self.posts_history = set()
    
    def elapsed_minutes(self):
        if not self.start_time:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds() / 60
    
    def duplicate_rate(self):
        if self.total_posts_seen == 0:
            return 0
        return self.duplicate_posts / self.total_posts_seen
    
    def save(self):
        """保存状态到文件"""
        state = {
            'start_time': str(self.start_time) if self.start_time else None,
            'end_time': str(self.end_time) if self.end_time else None,
            'current_batch': self.current_batch,
            'elapsed_minutes': self.elapsed_minutes(),
            'total_posts_seen': self.total_posts_seen,
            'unique_posts': self.unique_posts,
            'duplicate_posts': self.duplicate_posts,
            'duplicate_rate': self.duplicate_rate(),
            'refresh_count': self.refresh_count,
            'scroll_count': self.scroll_count
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        # 同时写入日志
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"状态保存 - {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"{'='*70}\n")
            f.write(f"运行时长：{self.elapsed_minutes():.1f} 分钟\n")
            f.write(f"当前批次：{self.current_batch}/{BATCH_COUNT}\n")
            f.write(f"总浏览帖子数：{self.total_posts_seen}\n")
            f.write(f"新增唯一帖子：{self.unique_posts}\n")
            f.write(f"重复率：{self.duplicate_rate()*100:.1f}%\n")
            f.write(f"刷新次数：{self.refresh_count}\n")

state = CollectionState()

# ==================== 日志函数 ====================

def log(message):
    """写入日志并打印"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

# ==================== 浏览器操作函数 ====================

def browser_scroll_down(page):
    """向下滚动页面"""
    page.evaluate("window.scrollBy(0, 800)")
    state.scroll_count += 1
    log(f"📜 向下滚动 (第{state.scroll_count}次)")

def browser_click_new_posts(page):
    """点击 New Posts 按钮刷新内容"""
    try:
        # 尝试多种选择器
        selectors = [
            'button:has-text("New posts")',
            'button:has-text("新帖子")',
            '[class*="new-posts"]',
        ]
        
        for selector in selectors:
            try:
                page.click(selector, timeout=3000)
                state.refresh_count += 1
                log(f"🔄 点击 New Posts 刷新 (第{state.refresh_count}次)")
                time.sleep(5)
                return True
            except:
                continue
        
        log("⚠️ 未找到 New Posts 按钮")
        return False
    except Exception as e:
        log(f"❌ 刷新失败：{e}")
        return False

def browser_get_snapshot(page):
    """获取页面内容"""
    return page.content()

def extract_posts(page):
    """提取帖子信息"""
    posts = []
    
    try:
        # 使用 JavaScript 提取帖子
        posts_data = page.evaluate('''() => {
            const posts = [];
            const postElements = document.querySelectorAll('[class*="feed-shared-update-v2"]');
            
            postElements.forEach(post => {
                try {
                    const text = post.innerText.substring(0, 500);
                    if (text.trim().length > 20) {
                        posts.push({
                            text: text,
                            timestamp: new Date().toISOString(),
                            url: window.location.href
                        });
                    }
                } catch(e) {}
            });
            
            return posts;
        }''')
        
        posts = posts_data[:20]  # 限制每次提取数量
    except Exception as e:
        log(f"⚠️ 提取帖子失败：{e}")
    
    return posts

def process_posts(posts):
    """处理提取的帖子"""
    for post in posts:
        post_hash = hash(post['text'])
        state.total_posts_seen += 1
        
        if post_hash not in state.posts_history:
            state.posts_history.add(post_hash)
            state.unique_posts += 1
            
            # 保存到文件
            save_post(post)
        else:
            state.duplicate_posts += 1

def save_post(post):
    """保存单个帖子"""
    with open(results_file, 'a', encoding='utf-8') as f:
        f.write(f"{post['timestamp']}|{post['url']}|{post['text']}\n")

# ==================== 主采集流程 ====================

def run_collection():
    """执行采集任务"""
    log("=" * 70)
    log("LinkedIn 深度采集 v4.0 - WebTop 持久化浏览器")
    log("=" * 70)
    
    state.start_time = datetime.now()
    
    with sync_playwright() as p:
        # 连接到持久化浏览器
        log("连接浏览器...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222", timeout=15000)
            log("浏览器连接成功")
        except Exception as e:
            log(f"连接失败：{e}")
            log("尝试启动新浏览器...")
            browser = create_browser_context(p)
        
        # 获取或创建页面
        context = browser.contexts[0] if hasattr(browser, 'contexts') else browser
        page = context.pages[0] if context.pages else browser.new_page()
        
        log("浏览器已就绪")
        
        # 访问 LinkedIn
        log("访问 LinkedIn...")
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        
        # 检查登录状态
        if "sign-in" in page.url.lower():
            log("未登录状态")
            log("请在浏览器中手动登录 LinkedIn")
            log("等待 60 秒...")
            time.sleep(60)
            
            # 再次检查
            if "sign-in" in page.url.lower():
                log("仍未登录，退出")
                return
            else:
                log("登录成功")
        else:
            log("已登录状态")
        
        # 开始采集
        log("开始采集...")
        
        for batch in range(BATCH_COUNT):
            state.current_batch = batch + 1
            log(f"\n批次 {batch+1}/{BATCH_COUNT}")
            
            batch_start = time.time()
            
            # 采集循环
            while (time.time() - batch_start) < (BATCH_DURATION_MINUTES * 60):
                # 获取快照/提取帖子
                posts = extract_posts(page)
                log(f"提取到 {len(posts)} 个帖子")
                
                # 处理帖子
                process_posts(posts)
                
                # 检查重复率
                if state.duplicate_rate() > state.get_adaptive_threshold():
                    log(f"重复率过高 ({state.duplicate_rate()*100:.1f}%)，刷新内容")
                    browser_click_new_posts(page)
                else:
                    # 滚动页面
                    for _ in range(MAX_SCROLLS_PER_CYCLE):
                        browser_scroll_down(page)
                        time.sleep(SCROLL_PAUSE_SECONDS)
                
                # 保存状态
                state.save()
            
            # 批次间等待
            if batch < BATCH_COUNT - 1:
                log(f"批次完成，等待 {BATCH_INTERVAL_SECONDS} 秒")
                time.sleep(BATCH_INTERVAL_SECONDS)
        
        # 完成
        state.end_time = datetime.now()
        state.save()
        
        log("\n" + "=" * 70)
        log("采集完成！")
        log("=" * 70)
        log(f"总运行时长：{state.elapsed_minutes():.1f} 分钟")
        log(f"总浏览帖子：{state.total_posts_seen}")
        log(f"新增唯一帖：{state.unique_posts}")
        log(f"最终重复率：{state.duplicate_rate()*100:.1f}%")
        log(f"刷新次数：{state.refresh_count}")
        log(f"\n结果保存至：{results_file}")
        
        # 注意：不要关闭浏览器，保持持久化运行
        log("\n浏览器保持运行，其他脚本可继续使用")

def main():
    """主函数"""
    try:
        run_collection()
    except KeyboardInterrupt:
        log("\n👋 用户中断")
        state.save()
    except Exception as e:
        log(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        state.save()

if __name__ == "__main__":
    main()
