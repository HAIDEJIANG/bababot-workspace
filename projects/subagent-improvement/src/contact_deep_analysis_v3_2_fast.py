#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 联系人深度分析脚本 v3.2 - 快速版
优化：间隔 15-20 秒，使用真实浏览器
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
from typing import Optional, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 配置 ====================

INPUT_DIR = Path(r"C:/Users/Haide/Desktop/LINKEDIN")
OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/LINKEDIN/ANALYSIS_20260326")
OUTPUT_DIR.mkdir(exist_ok=True)

PROGRESS_FILE = OUTPUT_DIR / "progress.json"
BACKUP_DIR = OUTPUT_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# 执行节奏配置（已调整）
MIN_INTERVAL_SECONDS = 15  # 15 秒
MAX_INTERVAL_SECONDS = 20  # 20 秒

# 浏览器配置
MAX_BROWSER_RECONNECT = 5

# 业务关键词
BUSINESS_KEYWORDS = [
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

# ==================== 进度管理 ====================

class ProgressTracker:
    def __init__(self):
        self.total_contacts = 0
        self.processed_contacts = 0
        self.failed_contacts = 0
        self.success_with_posts = 0
        self.timeout_count = 0
        self.current_contact_index = 0
        self.start_time = None
        self.contacts_queue = []
        self.load()
    
    def load(self):
        """加载进度"""
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.processed_contacts = data.get('processed_contacts', 0)
                self.failed_contacts = data.get('failed_contacts', 0)
                self.success_with_posts = data.get('success_with_posts', 0)
                self.timeout_count = data.get('timeout_count', 0)
                self.contacts_queue = data.get('contacts_queue', [])
                log(f"加载进度：已处理 {self.processed_contacts} 人")
            except Exception as e:
                log(f"加载进度失败：{e}", 'WARNING')
                self.contacts_queue = []
    
    def save(self):
        """保存进度"""
        data = {
            'processed_contacts': self.processed_contacts,
            'failed_contacts': self.failed_contacts,
            'success_with_posts': self.success_with_posts,
            'timeout_count': self.timeout_count,
            'contacts_queue': self.contacts_queue,
            'last_save_time': datetime.now().isoformat()
        }
        
        temp_file = PROGRESS_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(PROGRESS_FILE)
        
        # 定期备份
        if self.processed_contacts % 10 == 0:
            backup_file = BACKUP_DIR / f"progress_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log(f"进度备份：{backup_file.name}")
    
    def record_success(self, has_posts: bool = False):
        """记录成功"""
        self.processed_contacts += 1
        if has_posts:
            self.success_with_posts += 1
        self.save()
    
    def record_failure(self, is_timeout: bool = False):
        """记录失败"""
        self.failed_contacts += 1
        if is_timeout:
            self.timeout_count += 1
        self.save()

# ==================== LinkedIn 分析器 ====================

class LinkedInAnalyzer:
    def __init__(self, progress: ProgressTracker):
        self.progress = progress
        self.browser = None
        self.context = None
        self.page = None
        self.reconnect_count = 0
        self.max_reconnect = MAX_BROWSER_RECONNECT
    
    def start_browser(self) -> bool:
        """启动浏览器"""
        for attempt in range(self.max_reconnect):
            try:
                log(f"启动浏览器... (尝试 {attempt + 1}/{self.max_reconnect})")
                time.sleep(2)
                
                from playwright.sync_api import sync_playwright
                playwright = sync_playwright().start()
                self.browser = playwright.chromium.connect_over_cdp(
                    'http://localhost:9222',
                    timeout=60000
                )
                
                if self.browser.contexts:
                    self.context = self.browser.contexts[0]
                else:
                    self.context = self.browser.new_context()
                
                if self.context.pages:
                    self.page = self.context.pages[0]
                else:
                    self.page = self.context.new_page()
                
                self.page.set_default_timeout(45000)
                self.page.set_default_navigation_timeout(45000)
                
                # 检测登录状态
                log("检测 LinkedIn 登录状态...", 'INFO')
                try:
                    self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
                    time.sleep(3)
                    
                    current_url = self.page.url
                    if 'login' in current_url.lower() or 'authwall' in current_url.lower():
                        log("⚠️ 未登录 LinkedIn！", 'ERROR')
                        return False
                    
                    if 'feed' in current_url.lower() or 'mynetwork' in current_url.lower():
                        log("✅ LinkedIn 已登录", 'INFO')
                    
                except Exception as e:
                    log(f"检测登录状态失败：{e}", 'WARNING')
                
                log("浏览器启动完成")
                self.reconnect_count = 0
                return True
                
            except Exception as e:
                log(f"浏览器启动失败（第 {attempt + 1} 次）：{e}", 'ERROR')
                self.reconnect_count += 1
                
                if attempt < self.max_reconnect - 1:
                    log("等待 10 秒后重试...", 'INFO')
                    time.sleep(10)
        
        log(f"浏览器启动失败，已尝试 {self.max_reconnect} 次", 'ERROR')
        return False
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
                log("浏览器已关闭")
        except Exception as e:
            log(f"关闭浏览器失败：{e}", 'WARNING')
    
    def restart_browser(self) -> bool:
        """重启浏览器连接"""
        try:
            log("重启浏览器连接...", 'INFO')
            
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass
            
            time.sleep(2)
            
            from playwright.sync_api import sync_playwright
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.connect_over_cdp(
                'http://localhost:9222',
                timeout=30000
            )
            
            if self.browser.contexts:
                self.context = self.browser.contexts[0]
            else:
                self.context = self.browser.new_context()
            
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()
            
            self.page.set_default_timeout(45000)
            self.page.set_default_navigation_timeout(45000)
            
            log("浏览器连接已恢复", 'INFO')
            return True
            
        except Exception as e:
            log(f"浏览器重启失败：{e}", 'ERROR')
            return False
    
    def visit_profile(self, contact_url: str) -> bool:
        """访问 Profile 页面"""
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                # 检查浏览器健康状态
                if not self.page or not self.browser:
                    log("浏览器已关闭，尝试重启...", 'ERROR')
                    if not self.restart_browser():
                        return False
                
                log(f"访问 Profile: {contact_url}")
                
                self.page.goto(contact_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(1)
                
                # 验证 URL
                current_url = self.page.url
                if contact_url not in current_url:
                    log(f"⚠️ 被重定向到：{current_url}", 'WARNING')
                    return False
                
                # 等待元素加载
                try:
                    self.page.wait_for_selector('main h2', timeout=5000)
                    log("Profile 页面加载成功", 'INFO')
                except:
                    log("Profile 元素未加载，跳过", 'WARNING')
                    return False
                
                # 滚动
                for _ in range(3):
                    self.page.evaluate('window.scrollBy(0, 800)')
                    time.sleep(random.uniform(1, 2))
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                log(f"访问失败：{e}", 'ERROR')
                
                if 'closed' in error_msg.lower() or 'crashed' in error_msg.lower() or 'Target page' in error_msg:
                    log("检测到浏览器崩溃，尝试重启...", 'ERROR')
                    if attempt < max_retries - 1:
                        if self.restart_browser():
                            log("浏览器重启成功，继续", 'INFO')
                            continue
                        else:
                            log("浏览器重启失败，跳过", 'ERROR')
                            return False
                    else:
                        log("浏览器重启失败，跳过此联系人", 'ERROR')
                        return False
                
                return False
        
        return False
    
    def extract_profile_data(self, contact_id: str, contact_url: str) -> Optional[Dict[str, Any]]:
        """提取 Profile 数据"""
        try:
            # 尝试多种选择器
            selectors_to_try = [
                'main h2',
                '.pv-text-details__left-panel h2',
                'h2',
                '.text-heading-xlarge',
            ]
            
            name = ''
            for selector in selectors_to_try:
                try:
                    element = self.page.locator(selector).first
                    name = element.inner_text(timeout=8000)
                    if name.strip() and len(name) < 100 and 'Join' not in name and 'Sign' not in name and 'notifications' not in name.lower():
                        log(f"成功提取姓名（选择器：{selector}）：{name}", 'INFO')
                        break
                    else:
                        log(f"选择器 {selector} 返回无效内容", 'DEBUG')
                        name = ''
                except Exception as e:
                    log(f"选择器 {selector} 失败：{e}", 'DEBUG')
                    continue
            
            if not name.strip():
                log(f"提取姓名失败", 'ERROR')
                return None
            
            # 提取职位
            title = ''
            try:
                title_elem = self.page.locator('.pv-text-details__left-panel div:nth-child(2) span').first
                title = title_elem.inner_text(timeout=5000)
            except:
                pass
            
            # 提取公司
            company = ''
            try:
                company_elem = self.page.locator('.pv-text-details__left-panel div:nth-child(2) a').first
                company = company_elem.inner_text(timeout=5000)
            except:
                pass
            
            return {
                'contact_id': contact_id,
                'name': name.strip(),
                'current_title': title.strip() if title else '',
                'current_company': company.strip() if company else '',
                'crawl_time': datetime.now().isoformat(),
                'profile_url': contact_url
            }
            
        except Exception as e:
            log(f"提取 Profile 数据失败：{e}", 'ERROR')
            return None
    
    def extract_posts(self, contact_id: str, contact_name: str) -> list:
        """提取发帖数据"""
        posts = []
        cutoff_date = datetime.now() - timedelta(days=90)
        
        try:
            activity_url = contact_url.rstrip('/') + '/recent-activity/'
            log(f"访问 Activity: {activity_url}")
            self.page.goto(activity_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(2)
            
            # 检查是否有发帖
            post_elements = self.page.locator('div.update-components-text').all()
            if not post_elements:
                log("该用户没有发帖", 'INFO')
                return []
            
            log(f"发现 {len(post_elements)} 条发帖", 'INFO')
            
            for i, post_elem in enumerate(post_elements[:50]):
                try:
                    content = post_elem.inner_text(timeout=5000)
                    
                    # 检查时间
                    time_elem = post_elem.locator('span.update-components-actor__sub-description')
                    post_time_str = time_elem.inner_text(timeout=5000) if time_elem else ''
                    
                    post_date = self.parse_relative_time(post_time_str)
                    if post_date and post_date < cutoff_date:
                        log("发帖超出 90 天范围，停止提取", 'INFO')
                        break
                    
                    # 业务意图识别
                    matched_keywords = []
                    for kw in BUSINESS_KEYWORDS:
                        if kw.lower() in content.lower():
                            matched_keywords.append(kw)
                    
                    has_business_intent = len(matched_keywords) > 0
                    
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
                        log(f"发现业务相关发帖：{matched_keywords}", 'INFO')
                    
                except Exception as e:
                    log(f"提取单条发帖失败：{e}", 'WARNING')
                    continue
            
            log(f"成功提取 {len(posts)} 条发帖", 'INFO')
            return posts
            
        except Exception as e:
            log(f"访问 Activity 失败：{e}", 'WARNING')
            return []
    
    def parse_relative_time(self, time_str: str) -> Optional[datetime]:
        """解析相对时间"""
        if not time_str:
            return datetime.now()
        
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
            
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def analyze_contact(self, contact: Dict[str, Any]) -> bool:
        """分析单个联系人"""
        contact_id = contact.get('id', contact.get('contact_id', ''))
        contact_url = contact.get('profile_url', contact.get('linkedin_url', ''))
        contact_name = contact.get('name', '')
        
        log(f"\n{'='*60}")
        log(f"开始分析：{contact_name} ({contact_id})")
        log(f"{'='*60}")
        
        # 访问 Profile
        if not self.visit_profile(contact_url):
            log("访问 Profile 失败，跳过", 'ERROR')
            self.progress.record_failure()
            return False
        
        # 提取 Profile 数据
        profile_data = self.extract_profile_data(contact_id, contact_url)
        if not profile_data:
            log("提取 Profile 数据失败，跳过", 'ERROR')
            self.progress.record_failure()
            return False
        
        log(f"提取 Profile 成功：{profile_data['name']}", 'INFO')
        
        # 提取发帖
        posts = self.extract_posts(contact_id, contact_name)
        has_posts = len(posts) > 0
        
        # 记录成功
        self.progress.record_success(has_posts)
        
        return True

# ==================== 主程序 ====================

def load_contacts() -> list:
    """加载联系人列表"""
    input_file = INPUT_DIR / "all_contacts_current.csv"
    
    if not input_file.exists():
        log(f"输入文件不存在：{input_file}", 'ERROR')
        return []
    
    contacts = []
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    
    log(f"加载 {len(contacts)} 位联系人", 'INFO')
    return contacts

def main():
    """主程序"""
    log("="*60)
    log("LinkedIn 联系人深度分析 v3.2 - 快速版")
    log("="*60)
    
    progress = ProgressTracker()
    analyzer = LinkedInAnalyzer(progress)
    
    contacts = load_contacts()
    if not contacts:
        log("没有联系人数据，退出", 'ERROR')
        return
    
    progress.total_contacts = len(contacts)
    progress.start_time = datetime.now().isoformat()
    
    if progress.contacts_queue:
        contacts = progress.contacts_queue
        log(f"从断点续传：剩余 {len(contacts)} 人", 'INFO')
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
            success = analyzer.analyze_contact(contact)
            
            if contact in progress.contacts_queue:
                progress.contacts_queue.remove(contact)
            
            # 间隔等待
            if i < len(contacts) - 1:
                interval = random.randint(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)
                log(f"\n等待 {interval} 秒后继续... (进度：{progress.processed_contacts}/{progress.total_contacts})")
                time.sleep(interval)
            
            # 每小时统计
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
            if elapsed_hours > 0:
                rate = progress.processed_contacts / elapsed_hours
                success_rate = (progress.success_with_posts / max(progress.processed_contacts, 1)) * 100
                log(f"\n当前速度：{rate:.1f} 人/小时")
                log(f"发帖统计：无发帖{100-success_rate:.1f}% | 成功{success_rate:.1f}%")
    
    except KeyboardInterrupt:
        log("\n用户中断，保存进度后退出", 'INFO')
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
        log(f"有发帖：{progress.success_with_posts}")
        log(f"成功率：{progress.processed_contacts / max(progress.total_contacts, 1) * 100:.1f}%")
        log("="*60)

if __name__ == '__main__':
    main()
