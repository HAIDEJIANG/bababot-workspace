#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 联系人深度分析脚�?v3.1 - 全面优化�?优化目标�?1. 解决熔断频繁触发问题
2. 提高浏览器连接稳定�?3. 改进 Profile 提取成功�?4. 优化资源管理器锁机制
5. 增强错误处理和重试逻辑
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
import threading
import requests
from typing import Optional, Tuple, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 使用全局浏览器连接（CDP 端口 9222�?
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

# 优化后的执行节奏配置（已调整�?MIN_INTERVAL_SECONDS = 15  # 增加�?60 秒（减少风控�?MAX_INTERVAL_SECONDS = 20  # 增加�?90 秒（减少风控�?TARGET_PER_HOUR = 60 / (MIN_INTERVAL_SECONDS + MAX_INTERVAL_SECONDS) / 2  # �?40-60 �?小时

# 优化后的超时配置
PAGE_LOAD_TIMEOUT = 45000  # 增加�?45 秒（更宽松）
ELEMENT_WAIT_TIMEOUT = 8000  # 增加�?8 秒（更宽松）
ACTIVITY_CHECK_TIMEOUT = 15000  # 增加�?15 秒（更宽松）

# 优化后的重试配置
MAX_BROWSER_RECONNECT = 5  # 增加�?5 次重�?MAX_RETRY_PER_CONTACT = 3  # 增加�?3 次重�?MAX_CONSECUTIVE_FAILURES = 10  # 增加�?10 次（减少熔断�? 
FAILURE_RESET_MINUTES = 60  # 增加�?60 分钟（更宽松�?
# 优化后的页面滚动配置
MAX_PROFILE_SCROLLS = 3  # 减少�?3 次（降低触发风控概率�?MAX_POSTS_PER_CONTACT = 50  # 减少�?50 条（更高效）

# 业务意图关键�?BUSINESS_KEYWORDS = [
    'WTB', 'WTS', 'WTP', 'want to buy', 'want to sell',
    'RFQ', 'request for quote', 'for sale', 'available',
    'stock', 'inventory', 'looking for', 'need',
    'offer', 'quote', 'price', 'USD', '$',
    'WhatsApp', 'email me', 'contact me', 'DM me',
    'urgent', 'AOG', 'immediate', 'ASAP', 'emergency',
    'PN#', 'Part Number', 'S/N', 'serial',
    'CFM56', 'V2500', 'PW4000', 'LEAP', 'Trent',
    'A320', 'B737', 'B777', 'A350', 'APU',
    'Landing Gear', 'Engine', 'Spare parts', 'Aviation',
    'MRO', 'maintenance', 'overhaul', 'repair'
]

EXCLUDE_KEYWORDS = [
    'hiring', 'recruiting', 'we are hiring',
    'conference', 'event', 'webinar', 'summit',
    'award', 'promotion', 'proud to announce',
    'article', 'blog', 'read more', 'news'
]

# 日志配置
run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = OUTPUT_DIR / f"analysis_log_{run_id}.txt"

def log(message: str, level: str = 'INFO'):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] [{level}] {message}"
    print(line)
    with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
        f.write(line + '\n')

# ==================== 优化后的文件操作 ====================

def safe_save_progress(data: dict, progress_file: Path):
    """安全保存进度（避免文件锁定）"""
    try:
        # 使用临时文件 + 原子重命�?        temp_file = progress_file.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 短暂延迟避免并发
        time.sleep(0.2)
        
        # 原子替换
        if progress_file.exists():
            progress_file.unlink()
        temp_file.rename(progress_file)
        
    except Exception as e:
        log(f"保存进度失败：{e}", 'ERROR')

# ==================== 优化后的资源管理�?====================

class OptimizedResourceManager:
    """优化后的资源管理�?- 减少锁冲突，增加重试"""
    
    def __init__(self):
        # 资源�?        self.browser_lock = threading.Lock()
        self.gmail_lock = threading.Lock()
        self.linkedin_lock = threading.Lock()
        self.stockmarket_lock = threading.Lock()
        
        # 文件锁字�?        self.file_locks = {}
        self.file_locks_lock = threading.Lock()
        
        # 使用统计
        self.usage_stats = {
            'browser_acquired': 0,
            'browser_released': 0,
            'browser_timeout': 0,
            'file_locks': 0,
            'file_unlocks': 0
        }
        
        # 锁状态（避免死锁�?        self.locked_resources = {}
    
    def acquire_browser(self, subagent_id: str, timeout: int = 600):
        """优化浏览器获取（更宽松的超时�?""
        start_time = time.time()
        acquired = self.browser_lock.acquire(timeout=timeout)
        
        if not acquired:
            wait_time = time.time() - start_time
            self.usage_stats['browser_timeout'] += 1
            log(f"获取浏览器失败（超时 {timeout} 秒）：{subagent_id}", 'WARNING')
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待浏览器超时（{timeout}秒）")
        
        wait_time = time.time() - start_time
        self.usage_stats['browser_acquired'] += 1
        log(f"获取浏览器成功（等待 {wait_time:.1f} 秒）：{subagent_id}")
        
        # 记录锁状�?        self.locked_resources[f"browser_{subagent_id}"] = datetime.now()
        
        return BrowserLockContext(self, subagent_id)
    
    def acquire_file(self, filepath: str, subagent_id: str, timeout: int = 120):
        """优化文件锁获取（更长超时�?""
        filepath = str(filepath)
        
        # 创建文件锁（如果不存在）
        with self.file_locks_lock:
            if filepath not in self.file_locks:
                self.file_locks[filepath] = threading.Lock()
        
        acquired = self.file_locks[filepath].acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Sub-Agent {subagent_id} 等待文件锁超时：{filepath}")
        
        self.usage_stats['file_locks'] += 1
        log(f"获取文件锁成功：{filepath} ({subagent_id})")
        
        # 记录锁状�?        self.locked_resources[f"file_{filepath}_{subagent_id}"] = datetime.now()
        
        return FileLockContext(self.file_locks[filepath], self, subagent_id, filepath)

# 优化后的锁上下文管理�?class BrowserLockContext:
    def __init__(self, resource_manager, subagent_id):
        self.resource_manager = resource_manager
        self.subagent_id = subagent_id
        self.lock = resource_manager.browser_lock
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
        self.resource_manager.usage_stats['browser_released'] += 1
        self.resource_manager.locked_resources.pop(f"browser_{self.subagent_id}", None)
        log(f"释放浏览器：{self.subagent_id}")

class FileLockContext:
    def __init__(self, lock, resource_manager, subagent_id, filepath):
        self.lock = lock
        self.resource_manager = resource_manager
        self.subagent_id = subagent_id
        self.filepath = filepath
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
        self.resource_manager.usage_stats['file_unlocks'] += 1
        self.resource_manager.locked_resources.pop(f"file_{self.filepath}_{self.subagent_id}", None)
        log(f"释放文件锁：{self.filepath} ({self.subagent_id})")

# 全局资源管理器实�?resource_manager = OptimizedResourceManager()

# ==================== 优化后的进度管理�?====================

class OptimizedProgressTracker:
    def __init__(self):
        self.total_contacts = 0
        self.processed_contacts = 0
        self.failed_contacts = 0
        self.no_posts_contacts = 0  # 无发帖联系人
        self.timeout_contacts = 0  # 超时联系�?        self.success_posts_contacts = 0  # 成功提取发帖
        self.current_contact_index = 0
        self.start_time = None
        self.last_save_time = None
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.contacts_queue = []
        self.analysis_mode = ANALYSIS_MODE
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
                log(f"加载进度：已处理 {self.processed_contacts} �?)
            except Exception as e:
                log(f"加载进度失败：{e}", 'WARNING')
                self.contacts_queue = []
    
    def save(self):
        """安全保存进度"""
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
            'analysis_mode': self.analysis_mode,
            'last_save_time': datetime.now().isoformat()
        }
        
        safe_save_progress(data, PROGRESS_FILE)
        
        # 定期备份
        if self.processed_contacts % 20 == 0:  # �?20 人备�?            backup_file = BACKUP_DIR / f"progress_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                log(f"进度备份：{backup_file.name}")
            except Exception as e:
                log(f"备份失败：{e}", 'WARNING')
        
        self.last_save_time = datetime.now()
    
    def check_meltdown(self) -> bool:
        """优化熔断检查（更宽松的阈值）"""
        if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds() / 60
                if time_since_failure < FAILURE_RESET_MINUTES:
                    log(f"触发熔断：连续失�?{self.consecutive_failures} 次，暂停 {FAILURE_RESET_MINUTES} 分钟", 'ERROR')
                    return True
            self.consecutive_failures = 0
            log("重置失败计数�?)
        return False
    
    def record_success(self, posts_status: str = 'unknown'):
        """记录成功（区分发帖状态）"""
        self.processed_contacts += 1
        self.consecutive_failures = 0
        
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
    
    def get_status_summary(self) -> Dict[str, Any]:
        """获取状态摘�?""
        return {
            'total_contacts': self.total_contacts,
            'processed_contacts': self.processed_contacts,
            'failed_contacts': self.failed_contacts,
            'no_posts_contacts': self.no_posts_contacts,
            'timeout_contacts': self.timeout_contacts,
            'success_posts_contacts': self.success_posts_contacts,
            'progress_percentage': (self.processed_contacts / max(self.total_contacts, 1)) * 100,
            'consecutive_failures': self.consecutive_failures,
            'current_speed_per_hour': self.get_current_speed()
        }
    
    def get_current_speed(self) -> float:
        """计算当前速度（人/小时�?""
        if not self.start_time:
            return 0.0
        
        start_time = datetime.fromisoformat(self.start_time)
        elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
        return self.processed_contacts / elapsed_hours if elapsed_hours > 0 else 0.0

# ==================== 优化后的 LinkedIn 分析�?====================

class OptimizedLinkedInAnalyzer:
    def __init__(self, progress: OptimizedProgressTracker):
        self.progress = progress
        self.browser = None
        self.context = None
        self.page = None
        self.reconnect_count = 0
        self.max_reconnect = MAX_BROWSER_RECONNECT
    
    def start_browser(self) -> bool:
        """优化浏览器启动（自动重连 + 登录状态检测）"""
        for attempt in range(self.max_reconnect):
            try:
                log(f"启动浏览�?.. (尝试 {attempt + 1}/{self.max_reconnect})")
                
                # 等待浏览器可�?                time.sleep(2)
                
                # 连接浏览器（CDP 方式�?                playwright = sync_playwright().start()
                self.browser = playwright.chromium.connect_over_cdp(
                    'http://localhost:9222',
                    timeout=60000
                )
                
                # 获取上下�?                if self.browser.contexts:
                    self.context = self.browser.contexts[0]
                else:
                    self.context = self.browser.new_context()
                
                # 获取页面
                if self.context.pages:
                    self.page = self.context.pages[0]
                else:
                    self.page = self.context.new_page()
                
                # 设置更宽松的超时
                self.page.set_default_timeout(45000)
                self.page.set_default_navigation_timeout(45000)
                
                # 检�?LinkedIn 登录状�?                log("检�?LinkedIn 登录状�?..", 'INFO')
                try:
                    self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
                    time.sleep(3)
                    
                    current_url = self.page.url
                    if 'login' in current_url.lower() or 'authwall' in current_url.lower():
                        log("⚠️ 未登�?LinkedIn！请在浏览器中登录后重试", 'ERROR')
                        return False
                    
                    if 'feed' in current_url.lower() or 'mynetwork' in current_url.lower():
                        log("�?LinkedIn 已登�?, 'INFO')
                    else:
                        log(f"⚠️ 不确定登录状态，当前 URL: {current_url}", 'WARNING')
                    
                except Exception as e:
                    log(f"检测登录状态失败：{e}", 'WARNING')
                
                log("浏览器启动完�?)
                self.reconnect_count = 0
                return True
                
            except Exception as e:
                log(f"浏览器启动失败（�?{attempt + 1} 次）：{e}", 'ERROR')
                self.reconnect_count += 1
                
                if attempt < self.max_reconnect - 1:
                    log(f"等待 10 秒后重试...", 'INFO')
                    time.sleep(10)
        
        log(f"浏览器启动失败，已尝�?{self.max_reconnect} �?, 'ERROR')
        return False
    
    def close_browser(self):
        """关闭浏览�?""
        try:
            if self.browser:
                self.browser.close()
                log("浏览器已关闭")
        except Exception as e:
            log(f"关闭浏览器失败：{e}", 'WARNING')
    
    def visit_profile(self, contact_url: str) -> bool:
        """访问 Profile 页面（带重定向自动重�?+ 浏览器健康检查）"""
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                # 检查浏览器健康状�?                if not self.page or not self.browser:
                    log("浏览器已关闭，需要重�?, 'ERROR')
                    return False
                
                log(f"访问 Profile: {contact_url} (尝试 {attempt+1}/{max_retries})", 'INFO')
                
                # 导航到目标页�?                self.page.goto(contact_url, wait_until='domcontentloaded', timeout=30000)
                
                # 等待 1 秒让 LinkedIn �?JS 执行
                time.sleep(1)
                
                # 验证当前 URL 是否与目标一�?                current_url = self.page.url
                if contact_url not in current_url:
                    log(f"⚠️ 被重定向到：{current_url}", 'WARNING')
                    
                    # 立即返回并重�?                    if attempt < max_retries - 1:
                        log("立即重试...", 'INFO')
                        time.sleep(2)  # 短暂等待后重�?                        continue
                    else:
                        log("重试失败，跳�?, 'ERROR')
                        return False
                
                # 等待 Profile 关键元素加载
                try:
                    self.page.wait_for_selector('main h2', timeout=5000)
                    log("Profile 页面加载成功", 'INFO')
                except:
                    log("Profile 元素未加载，重试...", 'WARNING')
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                
                # 滚动加载更多内容
                for _ in range(MAX_PROFILE_SCROLLS):
                    self.page.evaluate('window.scrollBy(0, 800)')
                    time.sleep(random.uniform(1, 2))
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                log(f"访问失败：{e}", 'ERROR')
                
                # 如果是浏览器关闭错误，不重试（需要重启浏览器�?                if 'closed' in error_msg.lower() or 'crashed' in error_msg.lower():
                    log("浏览器已关闭，跳过此联系�?, 'ERROR')
                    return False
                
                if attempt < max_retries - 1:
                    log("重试...", 'INFO')
                    time.sleep(2)
                    continue
        
        return False
    
    def extract_profile_data(self, contact_id: str, contact_url: str) -> Optional[dict]:
        """优化 Profile 数据提取（多选择器容�?+ 显式等待�?""
        try:
            # 先检查是否被重定向到登录�?            current_url = self.page.url
            if 'login' in current_url or 'authwall' in current_url or 'checkpoint' in current_url:
                log(f"页面被重定向到登�?验证页：{current_url}", 'ERROR')
                return None
            
            # 等待 Profile 页面加载
            time.sleep(3)  # 给页面时间加�?            
            # 尝试多种选择器（按成功率排序�? 使用 LinkedIn 最新结�?            selectors_to_try = [
                'main h2',  # main 区域内的 h2（排除顶部导航）
                '.pv-text-details__left-panel h2',  # Profile 左侧面板 h2
                '.pv-text-details__left-panel span:first-child',  # 左侧面板第一�?span
                '.text-heading-xlarge',  # 大标题文�?            ]
            
            name = ''
            for selector in selectors_to_try:
                try:
                    element = self.page.locator(selector).first
                    name = element.inner_text(timeout=8000)
                    # 验证姓名有效性（排除 "0 notifications" 等）
                    if name.strip() and len(name) < 100 and 'Join' not in name and 'Sign' not in name and '登录' not in name and '领英' not in name and 'notifications' not in name.lower():
                        log(f"成功提取姓名（选择器：{selector}）：{name}", 'INFO')
                        break
                    else:
                        log(f"选择�?{selector} 返回无效内容�?{name[:50]}...'", 'DEBUG')
                        name = ''
                except Exception as e:
                    log(f"选择�?{selector} 失败：{e}", 'DEBUG')
                    continue
            
            if not name.strip():
                log(f"提取姓名失败 - 所有选择器都失败", 'ERROR')
                return None
            
            # 提取职位（使�?LinkedIn 最新结构）
            title = ''
            title_selectors = [
                '.pv-text-details__left-panel div:nth-child(2) span',  # 左侧面板第二�?span
                '.pv-text-details__left-panel span:nth-child(2)',  # 左侧面板第二�?span
                '.artdeco-entity-lockup__subtitle',  # 副标�?            ]
            for selector in title_selectors:
                try:
                    element = self.page.locator(selector).first
                    title = element.inner_text(timeout=5000)
                    if title.strip() and len(title) < 200:
                        log(f"成功提取职位：{title[:50]}", 'INFO')
                        break
                except:
                    continue
            
            # 提取公司
            company = ''
            company_selectors = [
                '.pv-text-details__left-panel div:nth-child(2) a',  # 左侧面板公司链接
                '.pv-text-details__left-panel a',  # 左侧面板链接
                '.artdeco-entity-lockup__subtitle a',  # 副标题链�?            ]
            for selector in company_selectors:
                try:
                    element = self.page.locator(selector).first
                    company = element.inner_text(timeout=5000)
                    if company.strip() and len(company) < 200:
                        log(f"成功提取公司：{company[:50]}", 'INFO')
                        break
                except:
                    continue
            
            # 提取地点
            location_selectors = [
                '.text-body-small.inline-block',
                '.pv-top-card--location',
                '.location'
            ]
            
            location = ''
            for selector in location_selectors:
                try:
                    element = self.page.locator(selector).first
                    location = element.inner_text(timeout=ELEMENT_WAIT_TIMEOUT)
                    if location.strip():
                        break
                except:
                    continue
            
            # 提取连接�?            connections_selectors = [
                '.pv-recent-activity-section__additional-views',
                '.text-body-small span:last-child',
                '.connections-count'
            ]
            
            connections = ''
            for selector in connections_selectors:
                try:
                    element = self.page.locator(selector).first
                    connections = element.inner_text(timeout=ELEMENT_WAIT_TIMEOUT)
                    if connections.strip():
                        break
                except:
                    continue
            
            profile_data = {
                'contact_id': contact_id,
                'name': name.strip(),
                'current_title': title.strip(),
                'current_company': company.strip(),
                'location': location.strip(),
                'industry': '',
                'connections': connections.strip() or '500+',
                'about': '',
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
    
    def visit_activity(self, contact_url: str) -> Tuple[bool, str]:
        """
        优化 Activity 访问（区分不同情况）
        返回�?是否成功，状态：'loaded'/'timeout'/'no_posts'/'redirected')
        """
        try:
            activity_url = contact_url.rstrip('/') + '/recent-activity/'
            log(f"访问 Activity: {activity_url}")
            
            # 访问页面
            response = self.page.goto(activity_url, wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
            
            # 检查是否被重定�?            current_url = self.page.url
            if 'authwall' in current_url or 'challenge' in current_url:
                log(f"Activity 页面被重定向到验证页：{current_url}", 'WARNING')
                return False, 'redirected'
            
            # 等待页面元素（优化：区分"无发�?�?超时"�?            try:
                # 先检查是否有"无内�?提示
                no_content_selectors = [
                    '[data-test-id="no-content"]',
                    'text=Nothing to see',
                    'text=No recent activity',
                    'text=No posts'
                ]
                
                for selector in no_content_selectors:
                    try:
                        has_no_content = self.page.query_selector(selector) is not None
                        if has_no_content:
                            log("该用户没有发�?, 'INFO')
                            return True, 'no_posts'
                    except:
                        continue
                
                # 等待发帖元素出现（更短超时，避免等待太久�?                self.page.wait_for_selector('div.feed-shared-update-v2', timeout=ELEMENT_WAIT_TIMEOUT)
                log("发现发帖内容", 'INFO')
                return True, 'loaded'
                
            except PlaywrightTimeout:
                # 再次检查是否真的无发帖
                for selector in no_content_selectors:
                    try:
                        has_no_content = self.page.query_selector(selector) is not None
                        if has_no_content:
                            log("该用户没有发�?, 'INFO')
                            return True, 'no_posts'
                    except:
                        continue
                
                log("Activity 页面检查超�?, 'WARNING')
                return False, 'timeout'
            
        except PlaywrightTimeout:
            log("Activity 页面加载超时", 'ERROR')
            return False, 'timeout'
        except Exception as e:
            log(f"访问 Activity 失败：{e}", 'ERROR')
            return False, 'error'
    
    def extract_posts(self, contact_id: str, contact_name: str) -> list:
        """优化发帖提取（更智能的选择器）"""
        posts = []
        cutoff_date = datetime.now() - timedelta(days=90)
        
        try:
            # 使用更通用的选择�?            post_selectors = [
                'div.feed-shared-update-v2',
                'div.update-components-text',
                'article[data-id]',
                'div[data-test-id="feed-shared-update-v2"]'
            ]
            
            post_elements = []
            for selector in post_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    if elements:
                        post_elements = elements
                        break
                except:
                    continue
            
            log(f"发现 {len(post_elements)} 条发�?)
            
            for i, post_elem in enumerate(post_elements[:MAX_POSTS_PER_CONTACT]):
                try:
                    # 提取内容
                    content_selectors = [
                        'div.update-components-text',
                        'span[aria-hidden="true"]',
                        'p',
                        'div'
                    ]
                    
                    content = ''
                    for content_selector in content_selectors:
                        try:
                            content_elem = post_elem.locator(content_selector).first
                            content = content_elem.inner_text(timeout=3000)
                            if content.strip():
                                break
                        except:
                            continue
                    
                    if not content.strip():
                        continue
                    
                    # 提取时间（优化）
                    time_selectors = [
                        'span.update-components-actor__sub-description',
                        'time',
                        'span.tvm__text--neutral'
                    ]
                    
                    post_time_str = ''
                    for time_selector in time_selectors:
                        try:
                            time_elem = post_elem.locator(time_selector).first
                            post_time_str = time_elem.inner_text(timeout=3000)
                            if post_time_str.strip():
                                break
                        except:
                            continue
                    
                    # 解析时间
                    post_date = self.parse_relative_time(post_time_str)
                    
                    if post_date and post_date < cutoff_date:
                        log(f"发帖超出 90 天范围，停止提取")
                        break
                    
                    # 业务意图识别
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
            
            log(f"成功提取 {len(posts)} 条发�?)
            return posts
            
        except Exception as e:
            log(f"提取发帖数据失败：{e}", 'ERROR')
            return []
    
    def parse_relative_time(self, time_str: str) -> Optional[datetime]:
        """优化时间解析"""
        if not time_str:
            return datetime.now()
        
        try:
            time_str = time_str.lower().strip()
            
            if 'just now' in time_str or '刚刚' in time_str:
                return datetime.now()
            
            if 'minute' in time_str or 'min' in time_str:
                minutes = int(''.join(filter(str.isdigit, time_str)))
                return datetime.now() - timedelta(minutes=minutes)
            
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
            
            # 如果�?ISO 格式
            try:
                return datetime.fromisoformat(time_str.replace('z', '+00:00'))
            except:
                pass
            
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def calculate_priority_score(self, profile_data: dict, posts: list) -> int:
        """优化优先级打分算�?""
        score = 0
        
        # 职位相关性（40 分）
        title = profile_data.get('current_title', '').lower()
        if any(kw in title for kw in ['ceo', 'president', 'director', 'vp', 'manager']):
            score += 40
        elif any(kw in title for kw in ['purchasing', 'procurement', 'buyer', 'sourcing']):
            score += 35
        elif any(kw in title for kw in ['sales', 'business', 'bd', 'marketing']):
            score += 30
        elif any(kw in title for kw in ['engineer', 'technician', 'maintenance', 'mro']):
            score += 25
        elif any(kw in title for kw in ['analyst', 'specialist', 'consultant']):
            score += 20
        else:
            score += 15  # 其他职位
        
        # 公司类型�?5 分）
        company = profile_data.get('current_company', '').lower()
        if any(kw in company for kw in ['airline', 'airlines', 'cargo', 'aviation', 'aero']):
            score += 25
        elif any(kw in company for kw in ['mro', 'technics', 'maintenance', 'repair', 'overhaul']):
            score += 23
        elif any(kw in company for kw in ['engine', 'aircraft', 'components', 'parts', 'spares']):
            score += 20
        elif any(kw in company for kw in ['trading', 'leasing', 'finance', 'capital']):
            score += 18
        else:
            score += 10  # 其他公司类型
        
        # 业务意图�?0 分）
        business_posts = [p for p in posts if p['has_business_intent'] == 'Yes']
        score += min(len(business_posts) * 10, 20)
        
        # 连接数（15 分）
        connections = profile_data.get('connections', '500+')
        if '500+' in connections:
            score += 15
        elif '100' in connections:
            score += 10
        elif '50' in connections:
            score += 5
        else:
            score += 3
        
        return min(score, 120)  # 最�?120 �?
    def analyze_contact(self, contact: dict) -> bool:
        """优化单个联系人分析流�?""
        contact_id = contact.get('id', contact.get('contact_id', ''))
        contact_url = contact.get('profile_url', contact.get('linkedin_url', ''))
        contact_name = contact.get('name', '')
        
        log(f"\n{'='*60}")
        log(f"开始分析：{contact_name} ({contact_id})")
        log(f"{'='*60}")
        
        # Step 1: 访问 Profile
        if not self.visit_profile(contact_url):
            log("访问 Profile 失败，跳�?, 'ERROR')
            self.progress.record_failure()
            return False
        
        # Step 2: 提取 Profile 数据
        profile_data = self.extract_profile_data(contact_id, contact_url)
        if not profile_data:
            log("提取 Profile 数据失败，跳�?, 'ERROR')
            self.progress.record_failure()
            return False
        
        # 保存 Profile 数据
        self.save_profile(profile_data)
        
        # Step 3: 访问 Activity
        success, status = self.visit_activity(contact_url)
        
        if not success:
            if status == 'timeout':
                log("Activity 页面超时，跳过发帖提�?, 'WARNING')
                posts = []
                posts_status = 'timeout'
            elif status == 'redirected':
                log("Activity 页面被重定向，跳过发帖提�?, 'WARNING')
                posts = []
                posts_status = 'redirected'
            else:
                log("Activity 访问失败，继�?, 'WARNING')
                posts = []
                posts_status = 'error'
        else:
            if status == 'no_posts':
                log("该用户没有发�?, 'INFO')
                posts = []
                posts_status = 'no_posts'
            else:
                # Step 4: 提取发帖数据
                posts = self.extract_posts(contact_id, contact_name)
                posts_status = 'success' if posts else 'no_posts'
        
        # Step 5: 计算优先�?        priority_score = self.calculate_priority_score(profile_data, posts)
        
        # Step 6: 如果是高意向线索，保�?        business_posts = [p for p in posts if p['has_business_intent'] == 'Yes']
        if len(business_posts) > 0 or priority_score >= 80:
            lead_data = {
                'contact_id': contact_id,
                'name': contact_name,
                'company': profile_data.get('current_company', ''),
                'position': profile_data.get('current_title', ''),
                'post_date': business_posts[0]['post_date'] if business_posts else '',
                'post_content': business_posts[0]['post_content'][:200] if business_posts else '',
                'business_intent': 'Yes' if business_posts else 'No',
                'matched_keywords': '|'.join(set(kw for p in business_posts for kw in p['matched_keywords'].split('|') if kw)),
                'priority_score': priority_score,
                'recommended_action': self.get_recommended_action(priority_score, business_posts),
                'crawl_time': datetime.now().isoformat()
            }
            self.save_lead(lead_data)
            log(f"保存高意向线索：优先�?{priority_score}")
        
        # 记录成功（区分发帖状态）
        self.progress.record_success(posts_status)
        
        return True
    
    def save_profile(self, profile_data: dict):
        """保存 Profile 数据（优化）"""
        try:
            file_exists = PROFILE_OUTPUT.exists()
            with open(PROFILE_OUTPUT, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=profile_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(profile_data)
        except Exception as e:
            log(f"保存 Profile 数据失败：{e}", 'ERROR')

    def save_lead(self, lead_data: dict):
        """保存线索数据（优化）"""
        try:
            file_exists = LEADS_OUTPUT.exists()
            with open(LEADS_OUTPUT, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=lead_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(lead_data)
        except Exception as e:
            log(f"保存线索数据失败：{e}", 'ERROR')

    def get_recommended_action(self, score: int, business_posts: list) -> str:
        """优化推荐动作"""
        if business_posts:
            if 'urgent' in str(business_posts).lower() or 'aog' in str(business_posts).lower():
                return '🔥 立即联系（紧急需求）'
            elif '采购意向' in str(business_posts):
                return '💰 准备报价（采购意向）'
            elif '出售意向' in str(business_posts):
                return '📦 评估库存（出售意向）'
            elif '合作意向' in str(business_posts):
                return '🤝 商务洽谈（合作意向）'
        
        if score >= 100:
            return '�?高优先级跟进'
        elif score >= 80:
            return '�?优先跟进'
        elif score >= 60:
            return '�?常规跟进'
        else:
            return '�?保持关注'

# ==================== 主程�?====================

def load_contacts() -> list:
    """加载联系人列表（优化�?""
    if not ALL_CONTACTS_FILE.exists():
        log(f"输入文件不存在：{ALL_CONTACTS_FILE}", 'ERROR')
        return []
    
    contacts = []
    try:
        with open(ALL_CONTACTS_FILE, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append(row)
    except Exception as e:
        log(f"读取输入文件失败：{e}", 'ERROR')
        return []
    
    log(f"加载 {len(contacts)} 位联系人")
    return contacts

def main():
    """主程�?""
    log("="*60)
    log("LinkedIn 联系人深度分�?v3.1 - 全面优化�?)
    log("="*60)
    
    progress = OptimizedProgressTracker()
    analyzer = OptimizedLinkedInAnalyzer(progress)
    
    contacts = load_contacts()
    if not contacts:
        log("没有联系人数据，退�?, 'ERROR')
        return
    
    progress.total_contacts = len(contacts)
    progress.start_time = datetime.now().isoformat()
    
    if progress.contacts_queue:
        contacts = progress.contacts_queue
        log(f"从断点续传：剩余 {len(contacts)} �?)
    else:
        progress.contacts_queue = contacts
        progress.save()
    
    # 启动浏览�?    if not analyzer.start_browser():
        log("无法启动浏览器，退�?, 'ERROR')
        return
    
    start_time = datetime.now()
    
    try:
        for i, contact in enumerate(contacts):
            # 检查熔�?            if progress.check_meltdown():
                log(f"触发熔断，暂�?{FAILURE_RESET_MINUTES} 分钟...")
                time.sleep(FAILURE_RESET_MINUTES * 60)
            
            # 分析联系�?            success = analyzer.analyze_contact(contact)
            
            # 从队列移�?            if contact in progress.contacts_queue:
                progress.contacts_queue.remove(contact)
            
            # 计算间隔
            if i < len(contacts) - 1:
                interval = random.randint(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)
                log(f"\n等待 {interval} 秒后继续... (进度：{progress.processed_contacts}/{progress.total_contacts})")
                time.sleep(interval)
            
            # 每小时统�?            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
            if elapsed_hours > 0:
                rate = progress.processed_contacts / elapsed_hours
                log(f"\n当前速度：{rate:.1f} �?小时")
                
                # 发帖统计
                if progress.processed_contacts > 0:
                    no_posts_pct = (progress.no_posts_contacts / progress.processed_contacts) * 100
                    timeout_pct = (progress.timeout_contacts / progress.processed_contacts) * 100
                    success_pct = (progress.success_posts_contacts / progress.processed_contacts) * 100
                    log(f"发帖统计：无发帖{no_posts_pct:.1f}% | 超时{timeout_pct:.1f}% | 成功{success_pct:.1f}%")

    except KeyboardInterrupt:
        log("\n用户中断，保存进度后退�?)
    except Exception as e:
        log(f"\n程序异常：{e}", 'ERROR')
        traceback.print_exc()
    finally:
        progress.save()
        analyzer.close_browser()
        
        # 保存最终摘�?        summary = progress.get_status_summary()
        summary_file = SUMMARY_OUTPUT
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        log("\n" + "="*60)
        log("分析完成统计")
        log("="*60)
        log(f"总联系人：{progress.total_contacts}")
        log(f"成功处理：{progress.processed_contacts}")
        log(f"失败：{progress.failed_contacts}")
        log(f"无发帖：{progress.no_posts_contacts}")
        log(f"超时：{progress.timeout_contacts}")
        log(f"成功提取发帖：{progress.success_posts_contacts}")
        log(f"成功率：{progress.processed_contacts / max(progress.total_contacts, 1) * 100:.1f}%")
        log(f"当前速度：{summary['current_speed_per_hour']:.1f} �?小时")
        log(f"输出文件�?)
        log(f"  - {PROFILE_OUTPUT}")
        log(f"  - {POSTS_OUTPUT}")
        log(f"  - {LEADS_OUTPUT}")
        log(f"  - {SUMMARY_OUTPUT}")
        log("="*60)

if __name__ == '__main__':
    main()
