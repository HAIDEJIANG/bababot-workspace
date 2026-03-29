#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 联系人深度分析脚本 - 稳定版
用于生产环境，包含自动重连和优化的熔断机制
"""

import time
import json
import sys
import io
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import csv
import traceback
from typing import Optional, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 webtop 模块路径
sys.path.insert(0, str(Path(__file__).parent / 'webtop'))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ==================== 配置 ====================

DATA_DIR = Path(r"C:\Users\Haide\Desktop\LINKEDIN")
OUTPUT_DIR = DATA_DIR / "ANALYSIS_20260326"
OUTPUT_DIR.mkdir(exist_ok=True)

ALL_CONTACTS_FILE = DATA_DIR / "all_contacts_current.csv"

PROFILE_OUTPUT = OUTPUT_DIR / "contact_profiles_full.csv"
POSTS_OUTPUT = OUTPUT_DIR / "contact_posts_90days.csv"
LEADS_OUTPUT = OUTPUT_DIR / "business_leads.csv"

# 优化后的熔断配置
MAX_CONSECUTIVE_FAILURES = 10  # 10 次失败才熔断
FAILURE_PAUSE_MINUTES = 15     # 熔断 15 分钟
FAILURE_RESET_MINUTES = 10     # 10 分钟无失败则重置

# 执行节奏
MIN_INTERVAL_SECONDS = 20
MAX_INTERVAL_SECONDS = 40

# 浏览器配置
MAX_BROWSER_RECONNECT = 3      # 最多重试 3 次
BROWSER_CHECK_INTERVAL = 300   # 每 5 分钟检查浏览器健康

# 业务关键词
BUSINESS_KEYWORDS = [
    'WTB', 'WTS', 'RFQ', 'quote', 'price', 'stock', 'inventory',
    'CFM56', 'V2500', 'A320', 'B737', 'Engine', 'APU', 'Aviation'
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
    """浏览器管理器 - 负责浏览器连接和自动重连"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.last_health_check = None
        self.reconnect_count = 0
    
    def start(self) -> bool:
        """启动浏览器"""
        try:
            log("启动浏览器...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(
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
            
            self.page.set_default_timeout(30000)
            self.page.set_default_navigation_timeout(30000)
            
            log("浏览器启动成功")
            self.reconnect_count = 0
            return True
            
        except Exception as e:
            log(f"浏览器启动失败：{e}", 'ERROR')
            return False
    
    def check_health(self) -> bool:
        """检查浏览器健康状态"""
        try:
            if not self.page:
                return False
            
            # 尝试访问空白页
            self.page.goto('about:blank', timeout=5000)
            return True
            
        except:
            return False
    
    def reconnect(self) -> bool:
        """自动重连浏览器"""
        if self.reconnect_count >= MAX_BROWSER_RECONNECT:
            log(f"已达到最大重连次数 ({MAX_BROWSER_RECONNECT})，放弃重连", 'ERROR')
            return False
        
        log(f"尝试重连浏览器 ({self.reconnect_count + 1}/{MAX_BROWSER_RECONNECT})...")
        
        # 关闭旧连接
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        
        time.sleep(2)
        
        # 尝试新连接
        if self.start():
            self.reconnect_count += 1
            log("浏览器重连成功", 'INFO')
            return True
        
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

# ==================== 进度管理 ====================

class ProgressTracker:
    def __init__(self):
        self.total_contacts = 3185
        self.processed_contacts = 0
        self.failed_contacts = 0
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.pause_until = None
        self.start_time = datetime.now()
        self.load_progress()
    
    def load_progress(self):
        """从 CSV 文件加载实际进度"""
        if PROFILE_OUTPUT.exists():
            try:
                with open(PROFILE_OUTPUT, 'r', encoding='utf-8', errors='replace') as f:
                    reader = csv.reader(f)
                    urls = set()
                    for row in reader:
                        if row and row[0].startswith('https://www.linkedin.com/in/'):
                            urls.add(row[0])
                    self.processed_contacts = len(urls)
                    log(f"从 CSV 加载进度：{self.processed_contacts} 人已采集")
            except Exception as e:
                log(f"加载进度失败：{e}", 'WARNING')
    
    def record_success(self):
        """记录成功"""
        self.processed_contacts += 1
        self.consecutive_failures = 0
        self.last_failure_time = None
    
    def record_failure(self):
        """记录失败"""
        self.failed_contacts += 1
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()
        
        # 检查是否需要熔断
        if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            self.pause_until = datetime.now() + timedelta(minutes=FAILURE_PAUSE_MINUTES)
            log(f"触发熔断：连续失败 {self.consecutive_failures} 次，暂停 {FAILURE_PAUSE_MINUTES} 分钟", 'ERROR')
    
    def should_pause(self) -> bool:
        """检查是否应该暂停"""
        if self.pause_until and datetime.now() < self.pause_until:
            remaining = (self.pause_until - datetime.now()).seconds // 60
            log(f"熔断中，剩余 {remaining} 分钟", 'WARNING')
            return True
        
        # 熔断时间已到，恢复
        if self.pause_until and datetime.now() >= self.pause_until:
            log("熔断时间已到，恢复采集", 'INFO')
            self.pause_until = None
            self.consecutive_failures = 0
        
        return False
    
    def reset_failure_counter(self):
        """重置失败计数器"""
        if self.last_failure_time:
            time_since_failure = (datetime.now() - self.last_failure_time).total_seconds() / 60
            if time_since_failure >= FAILURE_RESET_MINUTES:
                log(f"已超过 {FAILURE_RESET_MINUTES} 分钟无失败，重置失败计数器", 'INFO')
                self.consecutive_failures = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        return {
            'total': self.total_contacts,
            'processed': self.processed_contacts,
            'failed': self.failed_contacts,
            'progress': self.processed_contacts / self.total_contacts * 100,
            'remaining': self.total_contacts - self.processed_contacts,
            'speed': self.processed_contacts / elapsed if elapsed > 0 else 0,
            'elapsed_hours': elapsed
        }

# ==================== 采集逻辑 ====================

class ContactAnalyzer:
    def __init__(self, browser_mgr: BrowserManager):
        self.browser_mgr = browser_mgr
    
    def analyze_contact(self, contact_url: str) -> bool:
        """分析单个联系人"""
        try:
            # 访问 Profile
            if not self.visit_profile(contact_url):
                return False
            
            # 提取数据
            profile_data = self.extract_profile(contact_url)
            if not profile_data:
                return False
            
            # 保存数据
            self.save_profile(profile_data)
            
            return True
            
        except Exception as e:
            log(f"分析失败：{e}", 'ERROR')
            return False
    
    def visit_profile(self, url: str) -> bool:
        """访问 Profile 页面"""
        try:
            log(f"访问：{url[:60]}...")
            self.browser_mgr.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(random.uniform(2, 4))
            return True
        except PlaywrightTimeout:
            log("访问超时", 'ERROR')
            return False
        except Exception as e:
            log(f"访问失败：{e}", 'ERROR')
            return False
    
    def extract_profile(self, url: str) -> Optional[Dict]:
        """提取 Profile 数据"""
        try:
            # 提取姓名
            name = ''
            try:
                name = self.browser_mgr.page.locator('h1').first.inner_text(timeout=5000)
            except:
                pass
            
            if not name or 'Join' in name:
                log("无法提取姓名", 'WARNING')
                return None
            
            return {
                'contact_id': contact_id,
                'name': name,
                'profile_url': url,
                'crawl_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            log(f"提取失败：{e}", 'ERROR')
            return None
    
    def save_profile(self, data: Dict):
        """保存 Profile 数据"""
        try:
            file_exists = PROFILE_OUTPUT.exists()
            with open(PROFILE_OUTPUT, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
        except Exception as e:
            log(f"保存失败：{e}", 'ERROR')

# ==================== 主程序 ====================

def load_contacts() -> list:
    """加载联系人列表"""
    if not ALL_CONTACTS_FILE.exists():
        log(f"输入文件不存在：{ALL_CONTACTS_FILE}", 'ERROR')
        return []
    
    contacts = []
    with open(ALL_CONTACTS_FILE, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].startswith('https://www.linkedin.com/in/'):
                contacts.append(row[0])
    
    log(f"加载 {len(contacts)} 位联系人")
    return contacts

def main():
    """主程序"""
    log("="*60)
    log("LinkedIn 联系人采集 - 稳定版")
    log("="*60)
    
    # 初始化
    browser_mgr = BrowserManager()
    progress = ProgressTracker()
    analyzer = ContactAnalyzer(browser_mgr)
    
    # 加载联系人
    contacts = load_contacts()
    if not contacts:
        return
    
    # 启动浏览器
    if not browser_mgr.start():
        log("无法启动浏览器，退出", 'ERROR')
        return
    
    # 开始采集
    log(f"开始采集，已采集 {progress.processed_contacts}/{progress.total_contacts}")
    
    try:
        for i, contact_url in enumerate(contacts):
            # 检查是否应该暂停
            if progress.should_pause():
                time.sleep(60)  # 每分钟检查一次
                continue
            
            # 重置失败计数器
            progress.reset_failure_counter()
            
            # 检查浏览器健康
            if not browser_mgr.check_health():
                log("浏览器连接断开，尝试重连...", 'WARNING')
                if not browser_mgr.reconnect():
                    log("重连失败，退出", 'ERROR')
                    break
            
            # 分析联系人
            success = analyzer.analyze_contact(contact_url)
            
            if success:
                progress.record_success()
            else:
                progress.record_failure()
            
            # 间隔等待
            if i < len(contacts) - 1:
                interval = random.randint(MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS)
                time.sleep(interval)
            
            # 每小时报告进度
            stats = progress.get_stats()
            if int(stats['elapsed_hours'] * 10) % 10 == 0:
                log(f"进度：{progress.processed_contacts}/{progress.total_contacts} ({stats['progress']:.2f}%) - 速度：{stats['speed']:.1f}人/小时")
    
    except KeyboardInterrupt:
        log("\n用户中断", 'INFO')
    except Exception as e:
        log(f"\n异常：{e}", 'ERROR')
        traceback.print_exc()
    finally:
        browser_mgr.close()
        
        # 输出最终统计
        stats = progress.get_stats()
        log("\n" + "="*60)
        log("采集完成统计")
        log("="*60)
        log(f"总联系人：{progress.total_contacts}")
        log(f"已采集：{progress.processed_contacts} ({stats['progress']:.2f}%)")
        log(f"失败：{progress.failed_contacts}")
        log(f"速度：{stats['speed']:.1f} 人/小时")
        log(f"耗时：{stats['elapsed_hours']:.2f} 小时")
        log("="*60)

if __name__ == '__main__':
    main()
