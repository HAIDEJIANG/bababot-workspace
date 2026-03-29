#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 联系人深度分析脚本 v3.0 - 优化版
修复：
1. 区分"无发帖"和"页面超时"
2. 增加浏览器重连机制
3. 优化 Cookie 使用
4. 修复文件锁定问题
"""

import time
import sys
import io
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import csv
import traceback
from typing import Optional, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from browser_config import create_browser_context

# ==================== 配置 ====================

INPUT_DIR = Path(r"C:/Users/Haide/Desktop/LINKEDIN")
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/LINKEDIN/ANALYSIS_20260326")
OUTPUT_DIR.mkdir(exist_ok=True)

ALL_CONTACTS_FILE = INPUT_DIR / "all_contacts_current.csv"
ANALYZED_HISTORY_FILE = INPUT_DIR / "analyzed_history.csv"
QUEUE_FILE = INPUT_DIR / "analysis_queue.csv"

PROFILE_OUTPUT = OUTPUT_DIR / "contact_profiles_full.csv"
POSTS_OUTPUT = OUTPUT_DIR / "contact_posts_90days.csv"
LEADS_OUTPUT = OUTPUT_DIR / "business_leads.csv"

PROGRESS_FILE = OUTPUT_DIR / "progress.json"
BACKUP_DIR = OUTPUT_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# 执行节奏配置
MIN_INTERVAL_SECONDS = 15
MAX_INTERVAL_SECONDS = 25

# 超时配置（优化）
PAGE_LOAD_TIMEOUT = 30000  # 页面加载超时 30 秒
ELEMENT_WAIT_TIMEOUT = 5000  # 元素等待超时 5 秒
ACTIVITY_CHECK_TIMEOUT = 10000  # Activity 检查超时 10 秒

# 重试配置
MAX_BROWSER_RECONNECT = 3  # 浏览器重连次数
MAX_RETRY_PER_CONTACT = 2  # 每个联系人重试次数

# 业务意图关键词
BUSINESS_KEYWORDS = [
    'WTB', 'WTS', 'WTP', 'want to buy', 'want to sell',
    'RFQ', 'request for quote', 'quote', 'price',
    'stock', 'inventory', 'looking for', 'need',
    'offer', 'available', 'for sale', 'selling'
]

EXCLUDE_KEYWORDS = [
    'hiring', 'recruiting', 'we are hiring',
    'conference', 'event', 'webinar', 'summit',
    'award', 'promotion', 'proud to announce'
]

# 日志配置
run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = OUTPUT_DIR / f"analysis_log_{run_id}.txt"

# ==================== 日志工具 ====================

def log(message: str, level: str = 'INFO'):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] [{level}] {message}"
    print(line)
    with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
        f.write(line + '\n')

# ==================== 文件操作优化 ====================

def safe_save_progress(data: dict, progress_file: Path):
    """安全保存进度（避免文件锁定）"""
    try:
        # 使用临时文件
        temp_file = progress_file.with_suffix('.tmp')
        
        # 写入临时文件
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 延迟后重命名（避免锁定）
        time.sleep(0.1)
        
        # 如果目标文件存在，先删除
        if progress_file.exists():
            try:
                progress_file.unlink()
            except:
                pass
        
        # 重命名临时文件
        temp_file.rename(progress_file)
        
    except Exception as e:
        log(f"保存进度失败：{e}", 'ERROR')

# ==================== 进度管理 ====================

class ProgressTracker:
    def __init__(self):
        self.total_contacts = 0
        self.processed_contacts = 0
        self.failed_contacts = 0
        self.no_posts_contacts = 0  # 无发帖联系人
        self.timeout_contacts = 0  # 超时联系人
        self.success_posts_contacts = 0  # 成功提取发帖
        self.current_contact_index = 0
        self.start_time = None
        self.last_save_time = None
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.contacts_queue = []
        self.load()
    
    def load(self):
        """加载进度"""
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.total_contacts = data.get('total_contacts', 0)
                self.processed_contacts = data.get('processed_contacts', 0)
                self.failed_contacts = data.get('failed_contacts', 0)
                self.no_posts_contacts = data.get('no_posts_contacts', 0)
                self.timeout_contacts = data.get('timeout_contacts', 0)
                self.success_posts_contacts = data.get('success_posts_contacts', 0)
                self.current_contact_index = data.get('current_contact_index', 0)
                self.start_time = data.get('start_time')
                self.contacts_queue = data.get('contacts_queue', [])
                log(f"加载进度：已处理 {self.processed_contacts} 人")
            except Exception as e:
                log(f"加载进度失败：{e}", 'WARNING')
                self.contacts_queue = []
    
    def save(self):
        """保存进度"""
        data = {
            'total_contacts': self.total_contacts,
            'processed_contacts': self.processed_contacts,
            'failed_contacts': self.failed_contacts,
            'no_posts_contacts': self.no_posts_contacts,
            'timeout_contacts': self.timeout_contacts,
            'success_posts_contacts': self.success_posts_contacts,
            'current_contact_index': self.current_contact_index,
            'start_time': self.start_time,
            'contacts_queue': self.contacts_queue,
            'last_save_time': datetime.now().isoformat()
        }
        
        # 使用安全保存
        safe_save_progress(data, PROGRESS_FILE)
        
        # 定期备份
        if self.processed_contacts % 10 == 0:
            backup_file = BACKUP_DIR / f"progress_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                log(f"进度备份：{backup_file.name}")
            except Exception as e:
                log(f"备份失败：{e}", 'WARNING')
        
        self.last_save_time = datetime.now()
    
    def check_meltdown(self) -> bool:
        """检查熔断"""
        if self.consecutive_failures >= 5:
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds() / 60
                if time_since_failure < 30:
                    log(f"触发熔断：连续失败 {self.consecutive_failures} 次，暂停 30 分钟", 'ERROR')
                    return True
            self.consecutive_failures = 0
            log("重置失败计数器")
        return False
    
    def record_success(self, posts_status: str):
        """记录成功"""
        self.processed_contacts += 1
        self.consecutive_failures = 0
        
        # 统计发帖状态
        if posts_status == 'no_posts':
            self.no_posts_contacts += 1
        elif posts_status == 'success':
            self.success_posts_contacts += 1
        elif posts_status == 'timeout':
            self.timeout_contacts += 1
        
        self.save()
    
    def record_failure(self):
        """记录失败"""
        self.failed_contacts += 1
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()
        self.save()

# ==================== LinkedIn 爬虫 ====================

class LinkedInContactAnalyzer:
    def __init__(self, progress: ProgressTracker):
        self.progress = progress
        self.browser = None
        self.context = None
        self.page = None
        self.reconnect_count = 0
    
    def start_browser(self) -> bool:
        """启动浏览器（带重连）"""
        for attempt in range(MAX_BROWSER_RECONNECT):
            try:
                log(f"启动浏览器... (尝试 {attempt + 1}/{MAX_BROWSER_RECONNECT})")
                playwright = sync_playwright().start()
                
                self.browser = playwright.chromium.connect_over_cdp(
                    'http://localhost:9222',
                    timeout=30000
                )
                
                self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
                self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
                
                log("浏览器启动完成")
                self.reconnect_count = 0
                return True
                
            except Exception as e:
                log(f"浏览器启动失败：{e}", 'ERROR')
                self.reconnect_count += 1
                if attempt < MAX_BROWSER_RECONNECT - 1:
                    log("等待 5 秒后重试...", 'INFO')
                    time.sleep(5)
        
        return False
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
                log("浏览器已关闭")
        except Exception as e:
            log(f"关闭浏览器失败：{e}", 'WARNING')
    
    def visit_profile(self, contact_url: str) -> bool:
        """访问 Profile 页面"""
        try:
            log(f"访问 Profile: {contact_url}")
            self.page.goto(contact_url, wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(random.uniform(2, 4))
            return True
        except PlaywrightTimeout:
            log(f"Profile 页面加载超时", 'ERROR')
            return False
        except Exception as e:
            log(f"访问 Profile 失败：{e}", 'ERROR')
            return False
    
    def extract_profile_data(self, contact_id: str, contact_url: str) -> Optional[dict]:
        """提取 Profile 数据"""
        try:
            name = self.page.locator('h1').first.inner_text(timeout=5000)
            
            title_elem = self.page.locator('div.text-body-medium.break-words').first
            title = title_elem.inner_text(timeout=5000) if title_elem else ''
            
            location_elem = self.page.locator('div.tvm-wrap__body span[aria-hidden="true"]').first
            location = location_elem.inner_text(timeout=5000) if location_elem else ''
            
            about_elem = self.page.locator('div#about div div')
            about = about_elem.inner_text(timeout=5000) if about_elem else ''
            
            connections_elem = self.page.locator('div.tvm-wrap__body span').last
            connections = connections_elem.inner_text(timeout=5000) if connections_elem else ''
            
            return {
                'contact_id': contact_id,
                'name': name,
                'current_title': title,
                'current_company': '',
                'location': location,
                'industry': '',
                'connections': connections,
                'about': about,
                'crawl_time': datetime.now().isoformat(),
                'profile_url': contact_url
            }
            
        except Exception as e:
            log(f"提取 Profile 数据失败：{e}", 'ERROR')
            return None
    
    def visit_activity(self, contact_url: str) -> Tuple[bool, str]:
        """
        访问 Activity 页面
        返回：(是否成功，状态：'loaded'/'timeout'/'no_posts')
        """
        try:
            activity_url = contact_url.rstrip('/') + '/recent-activity/'
            log(f"访问 Activity: {activity_url}")
            
            # 访问页面
            self.page.goto(activity_url, wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
            
            # 等待页面元素（优化：区分"无发帖"和"超时"）
            try:
                # 先检查是否有"无内容"提示
                no_posts_selector = 'text=Nothing to see for now'
                has_no_posts = self.page.query_selector(no_posts_selector) is not None
                
                if has_no_posts:
                    log("该用户没有发帖", 'INFO')
                    return True, 'no_posts'
                
                # 等待发帖元素出现
                self.page.wait_for_selector('div.update-components-text', timeout=ELEMENT_WAIT_TIMEOUT)
                log("发现发帖内容", 'INFO')
                return True, 'loaded'
                
            except PlaywrightTimeout:
                # 检查是否真的无发帖
                no_posts_selector = 'text=Nothing to see'
                has_no_posts = self.page.query_selector(no_posts_selector) is not None
                
                if has_no_posts:
                    log("该用户没有发帖", 'INFO')
                    return True, 'no_posts'
                else:
                    log("Activity 页面检查超时", 'WARNING')
                    return False, 'timeout'
            
        except PlaywrightTimeout:
            log("Activity 页面加载超时", 'ERROR')
            return False, 'timeout'
        except Exception as e:
            log(f"访问 Activity 失败：{e}", 'ERROR')
            return False, 'error'
    
    def extract_posts(self, contact_id: str, contact_name: str) -> list:
        """提取发帖数据"""
        posts = []
        cutoff_date = datetime.now() - timedelta(days=90)
        
        try:
            post_elements = self.page.locator('div.update-components-text').all()
            log(f"发现 {len(post_elements)} 条发帖")
            
            for i, post_elem in enumerate(post_elements[:50]):  # 最多提取 50 条
                try:
                    content = post_elem.inner_text(timeout=5000)
                    
                    time_elem = post_elem.locator('span.update-components-actor__sub-description')
                    post_time_str = time_elem.inner_text(timeout=5000) if time_elem else ''
                    
                    post_date = self.parse_relative_time(post_time_str)
                    
                    if post_date and post_date < cutoff_date:
                        break
                    
                    matched_keywords = []
                    for kw in BUSINESS_KEYWORDS:
                        if kw.lower() in content.lower():
                            matched_keywords.append(kw)
                    
                    is_excluded = False
                    for kw in EXCLUDE_KEYWORDS:
                        if kw.lower() in content.lower():
                            is_excluded = True
                            break
                    
                    has_business_intent = len(matched_keywords) > 0 and not is_excluded
                    
                    post_data = {
                        'contact_id': contact_id,
                        'contact_name': contact_name,
                        'post_date': post_date.isoformat() if post_date else '',
                        'post_content': content[:5000],
                        'post_url': self.page.url,
                        'has_business_intent': 'Yes' if has_business_intent else 'No',
                        'matched_keywords': '|'.join(matched_keywords),
                        'crawl_time': datetime.now().isoformat()
                    }
                    
                    posts.append(post_data)
                    
                    if has_business_intent:
                        log(f"发现业务相关发帖：{matched_keywords}")
                    
                except Exception as e:
                    log(f"提取单条发帖失败：{e}", 'WARNING')
                    continue
            
            log(f"成功提取 {len(posts)} 条发帖")
            return posts
            
        except Exception as e:
            log(f"提取发帖数据失败：{e}", 'ERROR')
            return []
    
    def parse_relative_time(self, time_str: str) -> Optional[datetime]:
        """解析相对时间"""
        try:
            time_str = time_str.lower().strip()
            
            if 'just now' in time_str or '刚刚' in time_str:
                return datetime.now()
            
            if 'hour' in time_str or 'h' in time_str:
                hours = int(''.join(filter(str.isdigit, time_str)))
                return datetime.now() - timedelta(hours=hours)
            
            if 'day' in time_str or 'd' in time_str:
                days = int(''.join(filter(str.isdigit, time_str)))
                return datetime.now() - timedelta(days=days)
            
            if 'week' in time_str or 'w' in time_str:
                weeks = int(''.join(filter(str.isdigit, time_str)))
                return datetime.now() - timedelta(weeks=weeks)
            
            if 'month' in time_str or 'mo' in time_str:
                months = int(''.join(filter(str.isdigit, time_str)))
                return datetime.now() - timedelta(days=months * 30)
            
            return None
            
        except Exception:
            return None
    
    def analyze_contact(self, contact: dict) -> bool:
        """分析单个联系人"""
        contact_id = contact.get('id', contact.get('contact_id', ''))
        contact_url = contact.get('profile_url', contact.get('linkedin_url', ''))
        contact_name = contact.get('name', '')
        
        log(f"\n{'='*60}")
        log(f"开始分析：{contact_name} ({contact_id})")
        log(f"{'='*60}")
        
        # Step 1: 访问 Profile
        if not self.visit_profile(contact_url):
            log("访问 Profile 失败，跳过", 'ERROR')
            self.progress.record_failure()
            return False
        
        # Step 2: 提取 Profile 数据
        profile_data = self.extract_profile_data(contact_id, contact_url)
        if not profile_data:
            log("提取 Profile 数据失败，跳过", 'ERROR')
            self.progress.record_failure()
            return False
        
        # 保存 Profile 数据
        self.save_profile(profile_data)
        
        # Step 3: 访问 Activity
        success, status = self.visit_activity(contact_url)
        
        if not success:
            if status == 'timeout':
                log("Activity 页面超时，跳过发帖提取", 'WARNING')
                self.progress.timeout_contacts += 1
            else:
                log("Activity 访问失败，跳过发帖提取", 'WARNING')
            posts = []
            posts_status = 'timeout'
        else:
            if status == 'no_posts':
                log("该用户没有发帖", 'INFO')
                posts = []
                posts_status = 'no_posts'
            else:
                # Step 4: 提取发帖数据
                posts = self.extract_posts(contact_id, contact_name)
                posts_status = 'success' if posts else 'no_posts'
        
        # 记录成功
        self.progress.record_success(posts_status)
        
        return True
    
    def save_profile(self, profile_data: dict):
        """保存 Profile 数据"""
        try:
            file_exists = PROFILE_OUTPUT.exists()
            with open(PROFILE_OUTPUT, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=profile_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(profile_data)
        except Exception as e:
            log(f"保存 Profile 数据失败：{e}", 'ERROR')

# ==================== 主程序 ====================

def load_contacts() -> list:
    """加载联系人列表"""
    if not ALL_CONTACTS_FILE.exists():
        log(f"输入文件不存在：{ALL_CONTACTS_FILE}", 'ERROR')
        return []
    
    contacts = []
    with open(ALL_CONTACTS_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    
    log(f"加载 {len(contacts)} 位联系人")
    return contacts

def main():
    """主程序"""
    log("="*60)
    log("LinkedIn 联系人深度分析 v3.0 - 优化版")
    log("="*60)
    
    progress = ProgressTracker()
    analyzer = LinkedInContactAnalyzer(progress)
    
    contacts = load_contacts()
    if not contacts:
        log("没有联系人数据，退出", 'ERROR')
        return
    
    progress.total_contacts = len(contacts)
    progress.start_time = datetime.now().isoformat()
    
    if progress.contacts_queue:
        contacts = progress.contacts_queue
        log(f"从断点续传：剩余 {len(contacts)} 人")
    else:
        progress.contacts_queue = contacts
        progress.save()
    
    # 启动浏览器
    if not analyzer.start_browser():
        log("无法启动浏览器，退出", 'ERROR')
        return
    
    start_time = datetime.now()
    
    try:
        for i, contact in enumerate(contacts):
            # 检查熔断
            if progress.check_meltdown():
                log("触发熔断，暂停 30 分钟...")
                time.sleep(1800)
            
            # 分析联系人
            analyzer.analyze_contact(contact)
            
            # 从队列移除
            if contact in progress.contacts_queue:
                progress.contacts_queue.remove(contact)
            
            # 计算间隔
            if i < len(contacts) - 1:
                interval = random.randint(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)
                log(f"\n等待 {interval} 秒后继续... (进度：{progress.processed_contacts}/{progress.total_contacts})")
                time.sleep(interval)
            
            # 每小时统计
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
            if elapsed_hours > 0:
                rate = progress.processed_contacts / elapsed_hours
                log(f"\n当前速度：{rate:.1f} 人/小时")
                
                # 统计发帖情况
                if progress.processed_contacts > 0:
                    no_posts_pct = (progress.no_posts_contacts / progress.processed_contacts) * 100
                    timeout_pct = (progress.timeout_contacts / progress.processed_contacts) * 100
                    success_pct = (progress.success_posts_contacts / progress.processed_contacts) * 100
                    log(f"发帖统计：无发帖{no_posts_pct:.1f}% | 超时{timeout_pct:.1f}% | 成功{success_pct:.1f}%")
    
    except KeyboardInterrupt:
        log("\n用户中断，保存进度后退出")
    except Exception as e:
        log(f"\n程序异常：{e}", 'ERROR')
        traceback.print_exc()
    finally:
        progress.save()
        analyzer.close_browser()
        
        log("\n" + "="*60)
        log("分析完成统计")
        log("="*60)
        log(f"总联系人：{progress.total_contacts}")
        log(f"成功处理：{progress.processed_contacts}")
        log(f"失败：{progress.failed_contacts}")
        log(f"无发帖：{progress.no_posts_contacts}")
        log(f"超时：{progress.timeout_contacts}")
        log(f"成功提取发帖：{progress.success_posts_contacts}")
        log("="*60)

if __name__ == '__main__':
    main()
