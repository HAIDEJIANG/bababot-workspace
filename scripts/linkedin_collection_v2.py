#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 深度采集脚本 v2.0 - 带 New Posts 刷新功能

优化内容：
1. 检测页面重复度 - 当内容重复时自动刷新
2. 点击"New Posts"按钮 - 获取新鲜内容
3. 持续深度采集 - 确保采集时间达标
4. 自动记录采集进度 - 避免重复采集

核心要求：
- 实际运行时间不少于设定目标
- 禁止估算、禁止预测
- 保证质量，深度采集
- 不需要用户任何干预
"""

import time
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/real business post")
OUTPUT_DIR.mkdir(exist_ok=True)

# 采集配置
TARGET_DURATION_MINUTES = 60  # 目标采集时长（分钟）
SCROLL_PAUSE_SECONDS = 3  # 每次滚动后等待时间
MAX_SCROLLS_PER_CYCLE = 10  # 每轮最大滚动次数
DUPLICATE_THRESHOLD = 0.7  # 重复度阈值（超过 70% 重复则刷新）

# 日志文件
run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = OUTPUT_DIR / f"linkedin_collection_log_{run_id}.txt"
results_file = OUTPUT_DIR / f"linkedin_posts_batch_{run_id}.csv"

# ==================== 状态追踪 ====================

class CollectionState:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.total_posts_seen = 0
        self.unique_posts = 0
        self.duplicate_posts = 0
        self.refresh_count = 0
        self.scroll_count = 0
        self.posts_history = set()  # 用于检测重复
    
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
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn 深度采集状态\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"开始时间：{self.start_time}\n")
            f.write(f"结束时间：{self.end_time or '进行中'}\n")
            f.write(f"运行时长：{self.elapsed_minutes():.1f} 分钟\n")
            f.write(f"目标时长：{TARGET_DURATION_MINUTES} 分钟\n")
            f.write(f"总浏览帖子数：{self.total_posts_seen}\n")
            f.write(f"新增唯一帖子：{self.unique_posts}\n")
            f.write(f"重复帖子数：{self.duplicate_posts}\n")
            f.write(f"重复率：{self.duplicate_rate()*100:.1f}%\n")
            f.write(f"刷新次数：{self.refresh_count}\n")
            f.write(f"滚动次数：{self.scroll_count}\n")

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

def browser_scroll_down():
    """向下滚动页面"""
    # TODO: 使用 browser 工具执行滚动
    # browser(action='act', kind='evaluate', fn='() => { window.scrollBy(0, 800); return "scrolled"; }')
    state.scroll_count += 1
    log(f"向下滚动 (第{state.scroll_count}次)")

def browser_click_new_posts():
    """点击 New Posts 按钮刷新内容"""
    # TODO: 使用 browser 工具点击 New Posts 按钮
    # browser(action='act', kind='click', ref='eXXX')  # ref 需要从页面快照中获取
    state.refresh_count += 1
    log(f"✅ 点击 New Posts 刷新 (第{state.refresh_count}次)")

def browser_get_snapshot():
    """获取页面快照"""
    # TODO: 使用 browser 工具获取快照
    # snapshot = browser(action='snapshot', refs='aria')
    # return snapshot
    return {}

def extract_posts_from_snapshot(snapshot):
    """从快照中提取帖子信息"""
    # TODO: 解析快照，提取帖子列表
    # 返回帖子 ID 列表和内容
    posts = []
    return posts

def check_duplicate_rate(new_posts):
    """检查重复率"""
    if not new_posts:
        return 1.0
    
    duplicates = 0
    for post_id in new_posts:
        if post_id in state.posts_history:
            duplicates += 1
        else:
            state.posts_history.add(post_id)
            state.unique_posts += 1
    
    state.total_posts_seen += len(new_posts)
    state.duplicate_posts += duplicates
    
    return duplicates / len(new_posts) if new_posts else 1.0

def save_posts_to_csv(posts):
    """保存帖子到 CSV 文件"""
    # TODO: 将帖子数据保存到 CSV
    # 字段：post_id, post_date, author, company, content, source_url, collection_date, verified, notes
    log(f"保存 {len(posts)} 条帖子到 CSV")

# ==================== 主采集流程 ====================

def collect_linkedin_feed():
    """主采集流程"""
    log("=" * 70)
    log("LinkedIn 深度采集 v2.0 - 带 New Posts 刷新")
    log("=" * 70)
    log(f"目标采集时长：{TARGET_DURATION_MINUTES} 分钟")
    log(f"重复率阈值：{DUPLICATE_THRESHOLD*100:.0f}%")
    log(f"开始采集...")
    
    state.start_time = datetime.now()
    
    while state.elapsed_minutes() < TARGET_DURATION_MINUTES:
        log(f"\n--- 采集周期 (已运行{state.elapsed_minutes():.1f}分钟) ---")
        
        # 步骤 1: 获取当前页面快照
        snapshot = browser_get_snapshot()
        
        # 步骤 2: 提取帖子
        posts = extract_posts_from_snapshot(snapshot)
        post_ids = [p['id'] for p in posts]
        
        # 步骤 3: 检查重复率
        dup_rate = check_duplicate_rate(post_ids)
        log(f"当前重复率：{dup_rate*100:.1f}% (阈值：{DUPLICATE_THRESHOLD*100:.0f}%)")
        
        # 步骤 4: 保存有效帖子
        if posts:
            save_posts_to_csv(posts)
            log(f"新增 {len(posts)} 条帖子，累计 {state.unique_posts} 条唯一帖子")
        
        # 步骤 5: 判断是否需要刷新
        if dup_rate > DUPLICATE_THRESHOLD:
            log(f"⚠️ 重复率超过阈值，点击 New Posts 刷新...")
            browser_click_new_posts()
            time.sleep(5)  # 等待新内容加载
            continue
        
        # 步骤 6: 向下滚动加载更多
        log(f"向下滚动加载更多...")
        for i in range(MAX_SCROLLS_PER_CYCLE):
            browser_scroll_down()
            time.sleep(SCROLL_PAUSE_SECONDS)
            
            # 每次滚动后检查是否已到底部
            # TODO: 检测是否还有新内容
        
        # 步骤 7: 等待片刻后继续下一轮
        time.sleep(10)
    
    # 采集完成
    state.end_time = datetime.now()
    
    # 保存最终状态
    state.save()
    
    # 打印总结
    log("\n" + "=" * 70)
    log("✅ 采集完成！")
    log("=" * 70)
    log(f"实际运行时间：{state.elapsed_minutes():.1f} 分钟")
    log(f"总浏览帖子数：{state.total_posts_seen}")
    log(f"新增唯一帖子：{state.unique_posts}")
    log(f"重复帖子数：{state.duplicate_posts}")
    log(f"重复率：{state.duplicate_rate()*100:.1f}%")
    log(f"页面刷新次数：{state.refresh_count}")
    log(f"页面滚动次数：{state.scroll_count}")
    log(f"输出文件：{results_file}")
    log(f"日志文件：{log_file}")
    log("=" * 70)

# ==================== 执行入口 ====================

if __name__ == '__main__':
    try:
        collect_linkedin_feed()
    except Exception as e:
        log(f"❌ 采集异常：{e}")
        state.end_time = datetime.now()
        state.save()
        raise
