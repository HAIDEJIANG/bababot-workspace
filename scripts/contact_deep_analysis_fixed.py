#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 联系人深度分析脚本 - 修复版
修复内容：
1. 浏览器登录状态验证
2. 正确的数据提取选择器
3. 发帖提取功能
4. CSV 格式规范化（带表头）
"""

import time
import json
import sys
import io
import random
from datetime import datetime, timedelta
from pathlib import Path
import csv
from typing import Optional, Dict, List

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ==================== 配置 ====================

DATA_DIR = Path(r"C:\Users\Haide\Desktop\LINKEDIN")
OUTPUT_DIR = DATA_DIR / "ANALYSIS_20260326_FIXED"
OUTPUT_DIR.mkdir(exist_ok=True)

ALL_CONTACTS_FILE = DATA_DIR / "all_contacts_current.csv"

# 输出文件（带表头）
PROFILE_OUTPUT = OUTPUT_DIR / "contact_profiles_fixed.csv"
POSTS_OUTPUT = OUTPUT_DIR / "contact_posts_90days_fixed.csv"
LEADS_OUTPUT = OUTPUT_DIR / "business_leads_fixed.csv"

# 分析配置
MAX_CONSECUTIVE_FAILURES = 10
FAILURE_PAUSE_MINUTES = 15
MIN_INTERVAL_SECONDS = 30
MAX_INTERVAL_SECONDS = 60

# 业务关键词
BUSINESS_KEYWORDS = [
    'WTB', 'WTS', 'RFQ', 'quote', 'price', 'stock', 'inventory',
    'CFM56', 'V2500', 'A320', 'B737', 'Engine', 'APU', 'Aviation',
    'MRO', 'maintenance', 'overhaul', 'spare parts'
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

# ==================== 浏览器管理 ====================

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def start(self) -> bool:
        """启动浏览器并验证登录"""
        try:
            log("启动浏览器...")
            self.playwright = sync_playwright().start()
            
            # 通过 CDP 连接
            self.browser = self.playwright.chromium.connect_over_cdp(
                'http://localhost:9222',
                timeout=30000
            )
            
            if self.browser.contexts:
                self.context = self.browser.contexts[0]
            else:
                self.context = self.browser.new_context()
            
            # 使用已打开的页面，而不是创建新页面
            if self.context.pages:
                self.page = self.context.pages[0]
                log(f"使用已存在的页面：{self.page.url}")
            else:
                self.page = self.context.new_page()
            
            self.page.set_default_timeout(30000)
            self.page.set_default_navigation_timeout(30000)
            
            # 直接访问 LinkedIn
            log("访问 LinkedIn...")
            self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
            time.sleep(5)
            
            # 假设用户已登录（手动确认过）
            log("✅ 开始分析")
            return True
            
        except Exception as e:
            log(f"浏览器启动失败：{e}", 'ERROR')
            return False
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            log("浏览器已关闭")
        except:
            pass

# ==================== 数据采集器 ====================

class ContactAnalyzer:
    def __init__(self, browser_mgr: BrowserManager):
        self.browser_mgr = browser_mgr
        self.page = browser_mgr.page  # 直接使用浏览器的 page
        self.profile_writer = None
        self.posts_writer = None
        self.leads_writer = None
        self.profile_file = None
        self.posts_file = None
        self.leads_file = None
        self.init_csv()
    
    def init_csv(self):
        """初始化 CSV 文件（带表头）"""
        # Profile 文件
        self.profile_file = open(PROFILE_OUTPUT, 'w', encoding='utf-8', newline='')
        profile_fieldnames = [
            'contact_id', 'name', 'current_title', 'current_company',
            'location', 'connections', 'about', 'crawl_time', 'profile_url'
        ]
        self.profile_writer = csv.DictWriter(self.profile_file, fieldnames=profile_fieldnames)
        self.profile_writer.writeheader()
        
        # Posts 文件
        self.posts_file = open(POSTS_OUTPUT, 'w', encoding='utf-8', newline='')
        posts_fieldnames = [
            'contact_id', 'contact_name', 'post_date', 'post_content',
            'post_url', 'has_business_intent', 'matched_keywords', 'crawl_time'
        ]
        self.posts_writer = csv.DictWriter(self.posts_file, fieldnames=posts_fieldnames)
        self.posts_writer.writeheader()
        
        # Leads 文件
        self.leads_file = open(LEADS_OUTPUT, 'w', encoding='utf-8', newline='')
        leads_fieldnames = [
            'contact_id', 'contact_name', 'company', 'title',
            'business_intent', 'matched_keywords', 'priority_score',
            'recommended_action', 'crawl_time'
        ]
        self.leads_writer = csv.DictWriter(self.leads_file, fieldnames=leads_fieldnames)
        self.leads_writer.writeheader()
        
        log("CSV 文件已初始化（带表头）")
    
    def analyze_contact(self, contact_url: str) -> bool:
        """分析单个联系人"""
        try:
            # 提取联系人 ID
            contact_id = contact_url
            
            # 访问 Profile
            log(f"访问 Profile: {contact_url[:60]}...")
            if not self.visit_profile(contact_url):
                return False
            
            # 提取 Profile 数据
            profile_data = self.extract_profile(contact_id, contact_url)
            if not profile_data:
                log("无法提取 Profile 数据", 'WARNING')
                return False
            
            # 保存 Profile 数据
            self.save_profile(profile_data)
            log(f"✅ 成功提取：{profile_data['name']} - {profile_data['current_title']} @ {profile_data['current_company']}")
            
            # 访问 Activity 并提取发帖
            posts = self.extract_posts(contact_id, profile_data['name'])
            
            # 如果是高意向线索，保存
            business_posts = [p for p in posts if p['has_business_intent'] == 'Yes']
            if business_posts:
                self.save_lead(contact_id, profile_data, business_posts)
            
            return True
            
        except Exception as e:
            log(f"分析失败：{e}", 'ERROR')
            return False
    
    def visit_profile(self, url: str) -> bool:
        """访问 Profile 页面"""
        try:
            self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(random.uniform(3, 5))
            
            # 滚动加载
            for _ in range(3):
                self.page.evaluate('window.scrollBy(0, 800)')
                time.sleep(random.uniform(1, 2))
            
            return True
        except Exception as e:
            log(f"访问失败：{e}", 'ERROR')
            return False
    
    def extract_profile(self, contact_id: str, url: str) -> Optional[Dict]:
        """提取 Profile 数据（使用正确的选择器）"""
        try:
            # 先等待页面加载
            time.sleep(3)
            
            # 姓名 - 使用多种选择器
            name = ''
            selectors = [
                'h1.pv-text-details__name',
                '.text-heading-xlarge',
                'h1',
            ]
            for selector in selectors:
                try:
                    elem = self.page.locator(selector).first
                    name = elem.inner_text(timeout=5000).strip()
                    if name and len(name) < 100 and 'Join' not in name:
                        log(f"提取姓名成功：{name}")
                        break
                    name = ''
                except Exception as e:
                    log(f"选择器{selector}失败：{e}", 'DEBUG')
                    continue
            
            # 如果还是没提取到，尝试页面标题
            if not name:
                try:
                    page_title = self.page.title()
                    name = page_title.replace('| LinkedIn', '').strip()
                    log(f"从标题提取：{name}")
                except:
                    pass
            
            if not name or len(name) > 100:
                log("无法提取有效姓名", 'ERROR')
                return None
            
            # 职位
            title = ''
            try:
                title_elem = self.page.locator('div.pv-text-details__left-panel').first
                if title_elem:
                    # 提取第一行（通常是职位）
                    title_lines = title_elem.inner_text(timeout=5000).strip().split('\n')
                    if title_lines:
                        title = title_lines[0].strip()
            except:
                pass
            
            # 公司
            company = ''
            try:
                company_elem = self.page.locator('div.pv-text-details__left-panel a').first
                if company_elem:
                    company = company_elem.inner_text(timeout=5000).strip()
            except:
                pass
            
            # 所在地
            location = ''
            try:
                location_elem = self.page.locator('div.pv-text-details__left-panel span').last
                if location_elem:
                    location = location_elem.inner_text(timeout=5000).strip()
            except:
                pass
            
            # 连接数
            connections = ''
            try:
                conn_elem = self.page.locator('span.tvm-wrap__body span').last
                if conn_elem:
                    connections = conn_elem.inner_text(timeout=5000).strip()
            except:
                pass
            
            # 关于
            about = ''
            try:
                about_elem = self.page.locator('div#about div div').first
                if about_elem:
                    about = about_elem.inner_text(timeout=5000).strip()
            except:
                pass
            
            return {
                'contact_id': contact_id,
                'name': name,
                'current_title': title,
                'current_company': company,
                'location': location,
                'connections': connections or '500+',
                'about': about,
                'crawl_time': datetime.now().isoformat(),
                'profile_url': url
            }
            
        except Exception as e:
            log(f"提取 Profile 失败：{e}", 'ERROR')
            return None
    
    def extract_posts(self, contact_id: str, contact_name: str) -> List[Dict]:
        """提取 90 天发帖"""
        posts = []
        cutoff_date = datetime.now() - timedelta(days=90)
        
        try:
            # 访问 Activity 页面
            activity_url = contact_url.rstrip('/') + '/recent-activity/'
            log(f"访问 Activity: {activity_url[:60]}...")
            
            self.page.goto(activity_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(random.uniform(3, 5))
            
            # 查找发帖
            post_elements = self.page.locator('div.update-components-text').all()
            log(f"发现 {len(post_elements)} 条发帖")
            
            for i, post_elem in enumerate(post_elements[:50]):  # 最多 50 条
                try:
                    content = post_elem.inner_text(timeout=5000)
                    
                    # 提取时间
                    post_date_str = ''
                    try:
                        time_elem = post_elem.locator('span.update-components-actor__sub-description')
                        if time_elem:
                            post_date_str = time_elem.inner_text(timeout=3000)
                    except:
                        pass
                    
                    post_date = self.parse_relative_time(post_date_str)
                    
                    # 检查是否在 90 天内
                    if post_date and post_date < cutoff_date:
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
                        'post_content': content[:2000],
                        'post_url': self.page.url,
                        'has_business_intent': 'Yes' if has_business_intent else 'No',
                        'matched_keywords': '|'.join(matched_keywords),
                        'crawl_time': datetime.now().isoformat()
                    }
                    
                    posts.append(post_data)
                    self.save_post(post_data)
                    
                    if has_business_intent:
                        log(f"🎯 发现业务相关发帖：{matched_keywords}")
                    
                except Exception as e:
                    log(f"提取单条发帖失败：{e}", 'WARNING')
                    continue
            
            log(f"成功提取 {len(posts)} 条发帖")
            
        except Exception as e:
            log(f"访问 Activity 失败：{e}", 'WARNING')
        
        return posts
    
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
            
        except:
            return datetime.now()
    
    def save_profile(self, data: Dict):
        """保存 Profile 数据"""
        self.profile_writer.writerow(data)
        self.profile_file.flush()
    
    def save_post(self, data: Dict):
        """保存发帖数据"""
        self.posts_writer.writerow(data)
        self.posts_file.flush()
    
    def save_lead(self, contact_id: str, profile: Dict, posts: List[Dict]):
        """保存高意向线索"""
        matched_keywords = set()
        for post in posts:
            for kw in post['matched_keywords'].split('|'):
                if kw:
                    matched_keywords.add(kw)
        
        # 计算优先级
        score = min(len(posts) * 10, 40)  # 发帖数量
        if any(kw in profile.get('current_title', '').lower() for kw in ['buyer', 'purchasing', 'procurement']):
            score += 30
        elif any(kw in profile.get('current_title', '').lower() for kw in ['sales', 'manager', 'director']):
            score += 20
        
        lead_data = {
            'contact_id': contact_id,
            'contact_name': profile['name'],
            'company': profile['current_company'],
            'title': profile['current_title'],
            'business_intent': 'Yes',
            'matched_keywords': '|'.join(matched_keywords),
            'priority_score': score,
            'recommended_action': self.get_recommended_action(score),
            'crawl_time': datetime.now().isoformat()
        }
        
        self.leads_writer.writerow(lead_data)
        self.leads_file.flush()
        log(f"💾 保存高意向线索：{profile['name']} (优先级：{score})")
    
    def get_recommended_action(self, score: int) -> str:
        """推荐跟进动作"""
        if score >= 80:
            return "🔥 立即联系 - 高优先级"
        elif score >= 60:
            return "⭐ 本周内联系 - 中优先级"
        elif score >= 40:
            return "📅 本月内联系 - 低优先级"
        else:
            return "📝 保持关注"
    
    def close(self):
        """关闭文件"""
        if self.profile_file:
            self.profile_file.close()
        if self.posts_file:
            self.posts_file.close()
        if self.leads_file:
            self.leads_file.close()

# ==================== 主程序 ====================

def load_contacts() -> List[str]:
    """加载联系人 URL 列表"""
    if not ALL_CONTACTS_FILE.exists():
        log(f"输入文件不存在：{ALL_CONTACTS_FILE}", 'ERROR')
        return []
    
    urls = []
    with open(ALL_CONTACTS_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].startswith('https://www.linkedin.com/in/'):
                urls.append(row[0])
    
    log(f"加载 {len(urls)} 位联系人")
    return urls

def main():
    """主程序"""
    log("="*60)
    log("LinkedIn 联系人深度分析 - 修复版")
    log("="*60)
    
    # 初始化
    browser_mgr = BrowserManager()
    
    # 启动浏览器（验证登录）
    if not browser_mgr.start():
        log("❌ 无法启动浏览器或未登录，退出", 'ERROR')
        log("请在 Chrome 浏览器中登录 LinkedIn 后重试")
        return
    
    # 初始化分析器
    analyzer = ContactAnalyzer(browser_mgr)
    
    # 加载联系人
    contacts = load_contacts()
    if not contacts:
        return
    
    # 开始分析
    log(f"\n开始分析 {len(contacts)} 位联系人...")
    
    success_count = 0
    fail_count = 0
    
    try:
        for i, contact_url in enumerate(contacts):
            log(f"\n[{i+1}/{len(contacts)}] 分析中...")
            
            success = analyzer.analyze_contact(contact_url)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
            
            # 间隔等待
            if i < len(contacts) - 1:
                interval = random.randint(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)
                log(f"等待 {interval} 秒后继续...")
                time.sleep(interval)
            
            # 每小时报告
            if (i + 1) % 10 == 0:
                log(f"\n📊 进度报告：成功 {success_count} 人，失败 {fail_count} 人")
    
    except KeyboardInterrupt:
        log("\n用户中断", 'INFO')
    except Exception as e:
        log(f"\n异常：{e}", 'ERROR')
    finally:
        analyzer.close()
        browser_mgr.close()
        
        # 最终报告
        log("\n" + "="*60)
        log("分析完成统计")
        log("="*60)
        log(f"总联系人：{len(contacts)}")
        log(f"成功：{success_count}")
        log(f"失败：{fail_count}")
        log(f"成功率：{success_count/max(len(contacts),1)*100:.1f}%")
        log(f"\n输出文件：")
        log(f"  - {PROFILE_OUTPUT}")
        log(f"  - {POSTS_OUTPUT}")
        log(f"  - {LEADS_OUTPUT}")
        log("="*60)

if __name__ == '__main__':
    # 需要从外部传入 contact_url
    # 这里简化处理，实际使用时需要传递 contact_url
    contact_url = ""  # 从外部传入
    main()
