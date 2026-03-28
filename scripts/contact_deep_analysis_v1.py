#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 联系人深度分析脚本 v2.0 - 动态增量版
目标：全部联系人动态分析（支持新增/更新）
节奏：10-15 人/小时（间隔 240-360 秒）
安全：即时保存 + 断点续传 + 异常熔断
特性：增量分析 + 动态联系人列表 + 定期更新
"""

import time
import json
import sys
import io
import random
from datetime import datetime, timedelta
from pathlib import Path
import csv
import traceback

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright

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
SUMMARY_OUTPUT = OUTPUT_DIR / "analysis_summary.json"
DELTA_REPORT = OUTPUT_DIR / "delta_report.md"

PROGRESS_FILE = OUTPUT_DIR / "progress.json"
BACKUP_DIR = OUTPUT_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

ANALYSIS_MODE = 'full'
REFRESH_ANALYZED_DAYS = 90

# 使用 Cookie 后，可以降低间隔时间
MIN_INTERVAL_SECONDS = 15
MAX_INTERVAL_SECONDS = 25

# Cookie 配置（用于绕过验证墙）
try:
    from linkedin_cookie_config import LINKEDIN_COOKIE, HEADERS
    USE_COOKIE = True
    print(f"[INFO] Cookie 配置已加载")
except:
    USE_COOKIE = False
    print(f"[WARNING] Cookie 配置未找到，将不使用 Cookie")

MAX_CONSECUTIVE_FAILURES = 5
FAILURE_RESET_MINUTES = 30
MAX_PROFILE_SCROLLS = 5
MAX_POSTS_PER_CONTACT = 100

BUSINESS_KEYWORDS = [
    'WTB', 'WTS', 'WTP', 'want to buy', 'want to sell',
    'RFQ', 'request for quote', 'for sale', 'available',
    'stock', 'inventory', 'looking for', 'need',
    'offer', 'quote', 'price', 'USD',
    'WhatsApp', 'email me', 'contact me',
    'urgent', 'AOG', 'immediate',
    'PN#', 'Part Number', 'S/N', 'serial',
    'CFM56', 'V2500', 'PW4000', 'LEAP', 'Trent',
    'A320', 'B737', 'B777', 'A350', 'APU',
    'Landing Gear', 'Engine', 'Spare parts', 'Aviation'
]

EXCLUDE_KEYWORDS = [
    'hiring', 'recruiting', 'we are hiring',
    'conference', 'event', 'webinar', 'summit',
    'award', 'promotion', 'proud to announce',
    'article', 'blog', 'read more'
]

run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = OUTPUT_DIR / f"analysis_log_{run_id}.txt"

def log(message, level='INFO'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] [{level}] {message}"
    print(line)
    with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
        f.write(line + '\n')

class ProgressTracker:
    def __init__(self):
        self.total_contacts = 0
        self.processed_contacts = 0
        self.failed_contacts = 0
        self.new_contacts_count = 0
        self.updated_contacts_count = 0
        self.skipped_contacts_count = 0
        self.current_contact_index = 0
        self.start_time = None
        self.last_save_time = None
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.contacts_queue = []
        self.analysis_mode = ANALYSIS_MODE
        self.load()
    
    def load(self):
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.total_contacts = data.get('total_contacts', 0)
                self.processed_contacts = data.get('processed_contacts', 0)
                self.failed_contacts = data.get('failed_contacts', 0)
                self.new_contacts_count = data.get('new_contacts_count', 0)
                self.updated_contacts_count = data.get('updated_contacts_count', 0)
                self.skipped_contacts_count = data.get('skipped_contacts_count', 0)
                self.current_contact_index = data.get('current_contact_index', 0)
                self.start_time = data.get('start_time')
                self.contacts_queue = data.get('contacts_queue', [])
                self.analysis_mode = data.get('analysis_mode', ANALYSIS_MODE)
                log(f"加载进度：已处理 {self.processed_contacts} 人，失败 {self.failed_contacts} 人，剩余 {len(self.contacts_queue)} 人")
            except Exception as e:
                log(f"加载进度失败：{e}", 'WARNING')
                self.contacts_queue = []
    
    def save(self):
        data = {
            'total_contacts': self.total_contacts,
            'processed_contacts': self.processed_contacts,
            'failed_contacts': self.failed_contacts,
            'new_contacts_count': self.new_contacts_count,
            'updated_contacts_count': self.updated_contacts_count,
            'skipped_contacts_count': self.skipped_contacts_count,
            'current_contact_index': self.current_contact_index,
            'start_time': self.start_time,
            'contacts_queue': self.contacts_queue,
            'analysis_mode': self.analysis_mode,
            'last_save_time': datetime.now().isoformat()
        }
        temp_file = PROGRESS_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(PROGRESS_FILE)
        if self.processed_contacts % 10 == 0:
            backup_file = BACKUP_DIR / f"progress_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log(f"进度备份：{backup_file.name}")
        self.last_save_time = datetime.now()
    
    def check_meltdown(self):
        if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds() / 60
                if time_since_failure < FAILURE_RESET_MINUTES:
                    log(f"触发熔断：连续失败 {self.consecutive_failures} 次，暂停 30 分钟", 'ERROR')
                    return True
            self.consecutive_failures = 0
            log("重置失败计数器（超过 30 分钟无失败）")
        return False
    
    def record_success(self, is_new_contact=False):
        self.processed_contacts += 1
        self.consecutive_failures = 0
        if is_new_contact:
            self.new_contacts_count += 1
        else:
            self.updated_contacts_count += 1
        self.save()
    
    def record_failure(self):
        self.failed_contacts += 1
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()
        self.save()
    
    def record_skipped(self):
        self.skipped_contacts_count += 1
        self.save()

class DataSaver:
    def __init__(self):
        self.profile_file = None
        self.posts_file = None
        self.leads_file = None
        self.profile_writer = None
        self.posts_writer = None
        self.leads_writer = None
        self.initialize()
    
    def initialize(self):
        profile_fieldnames = [
            'contact_id', 'name', 'current_company', 'current_title',
            'location', 'industry', 'connections', 'about',
            'experience', 'education', 'skills', 'crawl_time', 'profile_url'
        ]
        posts_fieldnames = [
            'contact_id', 'contact_name', 'post_date', 'post_content',
            'post_url', 'has_business_intent', 'matched_keywords',
            'crawl_time'
        ]
        leads_fieldnames = [
            'contact_id', 'contact_name', 'company', 'title',
            'business_intent', 'matched_keywords', 'last_post_date',
            'priority_score', 'recommended_action', 'crawl_time'
        ]
        is_new_profile = not PROFILE_OUTPUT.exists()
        is_new_posts = not POSTS_OUTPUT.exists()
        is_new_leads = not LEADS_OUTPUT.exists()
        self.profile_file = open(PROFILE_OUTPUT, 'a', encoding='utf-8', newline='')
        self.profile_writer = csv.DictWriter(self.profile_file, fieldnames=profile_fieldnames)
        if is_new_profile:
            self.profile_writer.writeheader()
        self.posts_file = open(POSTS_OUTPUT, 'a', encoding='utf-8', newline='')
        self.posts_writer = csv.DictWriter(self.posts_file, fieldnames=posts_fieldnames)
        if is_new_posts:
            self.posts_writer.writeheader()
        self.leads_file = open(LEADS_OUTPUT, 'a', encoding='utf-8', newline='')
        self.leads_writer = csv.DictWriter(self.leads_file, fieldnames=leads_fieldnames)
        if is_new_leads:
            self.leads_writer.writeheader()
        log(f"数据文件初始化完成")
        log(f"  - Profile: {PROFILE_OUTPUT}")
        log(f"  - Posts: {POSTS_OUTPUT}")
        log(f"  - Leads: {LEADS_OUTPUT}")
    
    def save_profile(self, profile_data):
        self.profile_writer.writerow(profile_data)
        self.profile_file.flush()
    
    def save_post(self, post_data):
        self.posts_writer.writerow(post_data)
        self.posts_file.flush()
    
    def save_lead(self, lead_data):
        self.leads_writer.writerow(lead_data)
        self.leads_file.flush()
    
    def close(self):
        if self.profile_file:
            self.profile_file.close()
        if self.posts_file:
            self.posts_file.close()
        if self.leads_file:
            self.leads_file.close()

class LinkedInContactAnalyzer:
    def __init__(self, progress, saver):
        self.progress = progress
        self.saver = saver
        self.browser = None
        self.context = None
        self.page = None
    
    def start_browser(self):
        log("启动浏览器...")
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.connect_over_cdp(
            'http://localhost:9222',
            timeout=30000
        )
        self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        log("浏览器启动完成")
    
    def close_browser(self):
        if self.browser:
            self.browser.close()
            log("浏览器已关闭")
    
    def visit_profile(self, contact_url):
        try:
            log(f"访问 Profile: {contact_url}")
            self.page.goto(contact_url, wait_until='domcontentloaded', timeout=30000)
            # 等待页面关键元素加载
            time.sleep(random.uniform(5, 8))
            # 滚动加载更多内容
            for _ in range(MAX_PROFILE_SCROLLS):
                self.page.evaluate('window.scrollBy(0, 1000)')
                time.sleep(random.uniform(1, 2))
            # 再次等待确保数据完全加载
            time.sleep(random.uniform(2, 4))
            return True
        except Exception as e:
            log(f"访问 Profile 失败：{e}", 'ERROR')
            return False
    
    def extract_profile_data(self, contact_id, contact_url):
        try:
            # 使用更可靠的选择器（LinkedIn 页面结构已更新）
            # 姓名：多个备选方案
            name = ''
            try:
                name = self.page.locator('h1').first.inner_text(timeout=5000)
            except:
                try:
                    name = self.page.locator('.text-heading-xlarge').inner_text(timeout=5000)
                except:
                    try:
                        name = self.page.locator('h2').first.inner_text(timeout=5000)
                    except:
                        name = 'Unknown'
            
            # 职位：多个备选方案
            title = ''
            try:
                title = self.page.locator('div.text-body-medium.break-words').first.inner_text(timeout=3000)
            except:
                try:
                    title = self.page.locator('.text-body-medium').first.inner_text(timeout=3000)
                except:
                    title = ''
            
            # 所在地：多个备选方案
            location = ''
            try:
                location = self.page.locator('div.tvm-wrap__body span[aria-hidden="true"]').first.inner_text(timeout=3000)
            except:
                try:
                    location = self.page.locator('span[aria-hidden="true"]').first.inner_text(timeout=3000)
                except:
                    location = ''
            
            # 关于：可选
            about = ''
            try:
                about = self.page.locator('div#about div div').first.inner_text(timeout=3000) if self.page.locator('div#about div div').count() > 0 else ''
            except:
                about = ''
            
            # 连接数：可选
            connections = ''
            try:
                connections = self.page.locator('div.tvm-wrap__body span').last.inner_text(timeout=3000)
            except:
                connections = '500+'
            profile_data = {
                'contact_id': contact_id,
                'name': name,
                'current_title': title,
                'current_company': '',
                'location': location,
                'industry': '',
                'connections': connections,
                'about': about,
                'experience': '',
                'education': '',
                'skills': '',
                'crawl_time': datetime.now().isoformat(),
                'profile_url': contact_url
            }
            log(f"提取 Profile 成功：{name}")
            return profile_data
        except Exception as e:
            log(f"提取 Profile 数据失败：{e}", 'ERROR')
            return None
    
    def visit_activity(self, contact_url):
        try:
            activity_url = contact_url.rstrip('/') + '/recent-activity/'
            log(f"访问 Activity: {activity_url}")
            self.page.goto(activity_url, wait_until='networkidle', timeout=30000)
            time.sleep(random.uniform(3, 6))
            return True
        except Exception as e:
            log(f"访问 Activity 失败：{e}", 'ERROR')
            return False
    
    def extract_posts(self, contact_id, contact_name):
        posts = []
        cutoff_date = datetime.now() - timedelta(days=90)
        try:
            post_elements = self.page.locator('div.update-components-text').all()
            log(f"发现 {len(post_elements)} 条发帖")
            for i, post_elem in enumerate(post_elements[:MAX_POSTS_PER_CONTACT]):
                try:
                    content = post_elem.inner_text(timeout=5000)
                    time_elem = post_elem.locator('span.update-components-actor__sub-description')
                    post_time_str = time_elem.inner_text(timeout=5000) if time_elem else ''
                    post_date = self.parse_relative_time(post_time_str)
                    if post_date and post_date < cutoff_date:
                        log(f"发帖超出 90 天范围，停止抓取")
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
                    post_url = self.page.url
                    post_data = {
                        'contact_id': contact_id,
                        'contact_name': contact_name,
                        'post_date': post_date.isoformat() if post_date else '',
                        'post_content': content[:5000],
                        'post_url': post_url,
                        'has_business_intent': 'Yes' if has_business_intent else 'No',
                        'matched_keywords': '|'.join(matched_keywords),
                        'crawl_time': datetime.now().isoformat()
                    }
                    posts.append(post_data)
                    self.saver.save_post(post_data)
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
    
    def parse_relative_time(self, time_str):
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
    
    def calculate_priority_score(self, profile_data, posts):
        score = 0
        business_posts = [p for p in posts if p['has_business_intent'] == 'Yes']
        post_score = min(len(business_posts) * 10, 40)
        score += post_score
        title = profile_data.get('current_title', '').lower()
        if any(kw in title for kw in ['buyer', 'purchasing', 'procurement', 'supply']):
            score += 30
        elif any(kw in title for kw in ['sales', 'manager', 'director']):
            score += 20
        if len(posts) > 0:
            score += min(len(posts) * 2, 20)
        connections = profile_data.get('connections', '')
        if '500+' in connections:
            score += 10
        elif '100' in connections:
            score += 5
        return score
    
    def analyze_contact(self, contact):
        contact_id = contact.get('id', contact.get('contact_id', ''))
        contact_url = contact.get('profile_url', contact.get('linkedin_url', ''))
        contact_name = contact.get('name', '')
        analyzed_ids = set()
        is_new_contact = contact_id not in analyzed_ids
        log(f"\n{'='*60}")
        log(f"开始分析：{contact_name} ({contact_id}) - {'新增' if is_new_contact else '更新'}")
        log(f"{'='*60}")
        if not self.visit_profile(contact_url):
            log("访问 Profile 失败，跳过", 'ERROR')
            self.progress.record_failure()
            return False
        profile_data = self.extract_profile_data(contact_id, contact_url)
        if not profile_data:
            log("提取 Profile 数据失败，跳过", 'ERROR')
            self.progress.record_failure()
            return False
        self.saver.save_profile(profile_data)
        if not self.visit_activity(contact_url):
            log("访问 Activity 失败，继续", 'WARNING')
            posts = []
        else:
            posts = self.extract_posts(contact_id, contact_name)
        priority_score = self.calculate_priority_score(profile_data, posts)
        business_posts = [p for p in posts if p['has_business_intent'] == 'Yes']
        if len(business_posts) > 0 or priority_score >= 50:
            lead_data = {
                'contact_id': contact_id,
                'contact_name': contact_name,
                'company': profile_data.get('current_company', ''),
                'title': profile_data.get('current_title', ''),
                'business_intent': 'Yes' if len(business_posts) > 0 else 'No',
                'matched_keywords': '|'.join(set(kw for p in business_posts for kw in p['matched_keywords'].split('|') if kw)),
                'last_post_date': business_posts[0]['post_date'] if business_posts else '',
                'priority_score': priority_score,
                'recommended_action': self.get_recommended_action(priority_score),
                'crawl_time': datetime.now().isoformat()
            }
            self.saver.save_lead(lead_data)
            log(f"保存高意向线索：优先级 {priority_score}")
        self.progress.record_success(is_new_contact)
        self.update_analyzed_history(contact, profile_data, posts)
        return True
    
    def get_recommended_action(self, score):
        if score >= 80:
            return "立即联系 - 高优先级"
        elif score >= 60:
            return "本周内联系 - 中优先级"
        elif score >= 40:
            return "本月内联系 - 低优先级"
        else:
            return "保持关注 - 暂不联系"
    
    def update_analyzed_history(self, contact, profile_data, posts):
        contact_id = contact.get('id', contact.get('contact_id', ''))
        history = []
        if ANALYZED_HISTORY_FILE.exists():
            try:
                with open(ANALYZED_HISTORY_FILE, 'r', encoding='utf-8', errors='replace') as f:
                    reader = csv.DictReader(f)
                    history = list(reader)
            except:
                history = []
        found = False
        for row in history:
            if row.get('contact_id', '') == contact_id:
                row['last_analyzed'] = datetime.now().isoformat()
                row['posts_count'] = str(len(posts))
                row['profile_url'] = contact.get('profile_url', '')
                row['company'] = profile_data.get('current_company', '')
                row['title'] = profile_data.get('current_title', '')
                found = True
                break
        if not found:
            history.append({
                'contact_id': contact_id,
                'name': contact.get('name', ''),
                'profile_url': contact.get('profile_url', ''),
                'last_analyzed': datetime.now().isoformat(),
                'posts_count': str(len(posts)),
                'company': profile_data.get('current_company', ''),
                'title': profile_data.get('current_title', '')
            })
        if history:
            try:
                temp_file = ANALYZED_HISTORY_FILE.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=history[0].keys())
                    writer.writeheader()
                    writer.writerows(history)
                temp_file.replace(ANALYZED_HISTORY_FILE)
            except Exception as e:
                log(f"保存分析历史失败：{e}", 'WARNING')

def load_contacts():
    log(f"分析模式：{ANALYSIS_MODE}")
    if not ALL_CONTACTS_FILE.exists():
        log(f"全部联系人文件不存在：{ALL_CONTACTS_FILE}", 'ERROR')
        return []
    all_contacts = []
    with open(ALL_CONTACTS_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_contacts.append(row)
    log(f"当前 LinkedIn 全部联系人：{len(all_contacts)} 位")
    analyzed_history = {}
    if ANALYZED_HISTORY_FILE.exists():
        with open(ANALYZED_HISTORY_FILE, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact_id = row.get('contact_id', row.get('id', ''))
                if contact_id:
                    analyzed_history[contact_id] = row
    log(f"已分析历史记录：{len(analyzed_history)} 位")
    queue = []
    cutoff_date = datetime.now() - timedelta(days=REFRESH_ANALYZED_DAYS)
    if ANALYSIS_MODE == 'full':
        queue = all_contacts
        log(f"全量模式：待分析 {len(queue)} 人")
    elif ANALYSIS_MODE == 'incremental':
        for contact in all_contacts:
            contact_id = contact.get('contact_id', contact.get('id', contact.get('profile_url', '')))
            if contact_id and contact_id not in analyzed_history:
                queue.append(contact)
        log(f"增量模式：新增 {len(queue)} 人")
    elif ANALYSIS_MODE == 'update':
        for contact in all_contacts:
            contact_id = contact.get('contact_id', contact.get('id', contact.get('profile_url', '')))
            if contact_id and contact_id in analyzed_history:
                last_analyzed = analyzed_history[contact_id].get('last_analyzed', '')
                if last_analyzed:
                    try:
                        last_date = datetime.fromisoformat(last_analyzed)
                        if last_date < cutoff_date:
                            queue.append(contact)
                    except:
                        queue.append(contact)
                else:
                    queue.append(contact)
        log(f"更新模式：需更新 {len(queue)} 人（超过 {REFRESH_ANALYZED_DAYS} 天未分析）")
    if queue:
        with open(QUEUE_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=queue[0].keys())
            writer.writeheader()
            writer.writerows(queue)
        log(f"待分析队列已保存：{QUEUE_FILE}")
    return queue

def save_analysis_summary(progress):
    summary = {
        'analysis_mode': progress.analysis_mode,
        'total_contacts': progress.total_contacts,
        'processed_contacts': progress.processed_contacts,
        'failed_contacts': progress.failed_contacts,
        'new_contacts_count': progress.new_contacts_count,
        'updated_contacts_count': progress.updated_contacts_count,
        'skipped_contacts_count': progress.skipped_contacts_count,
        'start_time': progress.start_time,
        'end_time': datetime.now().isoformat(),
        'success_rate': progress.processed_contacts / max(progress.total_contacts, 1) * 100,
        'output_files': {
            'profiles': str(PROFILE_OUTPUT),
            'posts': str(POSTS_OUTPUT),
            'leads': str(LEADS_OUTPUT)
        }
    }
    with open(SUMMARY_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(DELTA_REPORT, 'w', encoding='utf-8') as f:
        f.write(f"# LinkedIn 联系人分析增量报告\n\n")
        f.write(f"**分析模式**: {progress.analysis_mode}\n\n")
        f.write(f"**分析时间**: {progress.start_time} - {datetime.now().isoformat()}\n\n")
        f.write(f"## 统计汇总\n\n")
        f.write(f"| 指标 | 数值 |\n")
        f.write(f"|------|------|\n")
        f.write(f"| 总联系人 | {progress.total_contacts} |\n")
        f.write(f"| 成功处理 | {progress.processed_contacts} |\n")
        f.write(f"| 失败 | {progress.failed_contacts} |\n")
        f.write(f"| 新增联系人 | {progress.new_contacts_count} |\n")
        f.write(f"| 更新联系人 | {progress.updated_contacts_count} |\n")
        f.write(f"| 跳过联系人 | {progress.skipped_contacts_count} |\n")
        f.write(f"| 成功率 | {progress.processed_contacts / max(progress.total_contacts, 1) * 100:.1f}% |\n")
    log(f"汇总报告已保存：{SUMMARY_OUTPUT}")
    log(f"增量报告已保存：{DELTA_REPORT}")

def main():
    log("="*60)
    log("LinkedIn 联系人深度分析 v2.0 - 动态增量版")
    log("="*60)
    progress = ProgressTracker()
    saver = DataSaver()
    analyzer = LinkedInContactAnalyzer(progress, saver)
    contacts = load_contacts()
    if not contacts:
        log("没有待分析的联系人，退出", 'WARNING')
        return
    progress.total_contacts = len(contacts)
    progress.start_time = datetime.now().isoformat()
    if progress.contacts_queue:
        contacts = progress.contacts_queue
        log(f"从断点续传：剩余 {len(contacts)} 人")
    else:
        progress.contacts_queue = contacts
        progress.save()
    try:
        analyzer.start_browser()
    except Exception as e:
        log(f"启动浏览器失败：{e}", 'ERROR')
        log("请确保 Chrome 已启动并开启 CDP 端口 9222")
        saver.close()
        return
    start_time = datetime.now()
    try:
        for i, contact in enumerate(contacts):
            if progress.check_meltdown():
                log("触发熔断，暂停 30 分钟...")
                time.sleep(1800)
            success = analyzer.analyze_contact(contact)
            if contact in progress.contacts_queue:
                progress.contacts_queue.remove(contact)
            if i < len(contacts) - 1:
                interval = random.randint(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)
                log(f"\n等待 {interval} 秒后继续... (进度：{progress.processed_contacts}/{progress.total_contacts})")
                time.sleep(interval)
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
            if elapsed_hours > 0:
                rate = progress.processed_contacts / elapsed_hours
                log(f"\n当前速度：{rate:.1f} 人/小时")
    except KeyboardInterrupt:
        log("\n用户中断，保存进度后退出")
    except Exception as e:
        log(f"\n程序异常：{e}", 'ERROR')
        traceback.print_exc()
    finally:
        progress.save()
        analyzer.close_browser()
        saver.close()
        log("\n" + "="*60)
        log("分析完成统计")
        log("="*60)
        log(f"分析模式：{progress.analysis_mode}")
        log(f"总联系人：{progress.total_contacts}")
        log(f"成功处理：{progress.processed_contacts}")
        log(f"失败：{progress.failed_contacts}")
        log(f"新增联系人：{progress.new_contacts_count}")
        log(f"更新联系人：{progress.updated_contacts_count}")
        log(f"跳过联系人：{progress.skipped_contacts_count}")
        log(f"成功率：{progress.processed_contacts / max(progress.total_contacts, 1) * 100:.1f}%")
        log(f"输出文件：")
        log(f"  - {PROFILE_OUTPUT}")
        log(f"  - {POSTS_OUTPUT}")
        log(f"  - {LEADS_OUTPUT}")
        log(f"  - {SUMMARY_OUTPUT}")
        log(f"  - {DELTA_REPORT}")
        log("="*60)
        save_analysis_summary(progress)

if __name__ == '__main__':
    main()
