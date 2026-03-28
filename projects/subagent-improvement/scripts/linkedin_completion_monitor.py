#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集完成监控脚本
定期检查采集进度，完成后自动通知老板
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from subagent_base import SubAgentBase

# ==================== 配置 ====================

PROGRESS_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\progress.json")
PROJECT_CONFIG_FILE = Path(r"C:\Users\Haide\.openclaw\workspace\projects\subagent-improvement\project_config.json")
TOTAL_CONTACTS = 3185
CHECK_INTERVAL_SECONDS = 600  # 10 分钟检查一次
MAX_CHECKS = 144  # 最多检查 24 小时

# ==================== 监控函数 ====================

def check_linkedin_progress():
    """检查 LinkedIn 采集进度"""
    if not PROGRESS_FILE.exists():
        return None, 0, 0
    
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        processed = progress.get('processed_contacts', 0)
        failed = progress.get('failed_contacts', 0)
        
        return progress, processed, failed
    except Exception as e:
        print(f"读取进度文件失败：{e}")
        return None, 0, 0

def update_project_status(status, completed_at=None):
    """更新项目配置状态"""
    if not PROJECT_CONFIG_FILE.exists():
        return
    
    try:
        with open(PROJECT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['status'] = status
        if completed_at:
            config['completed_at'] = completed_at
        
        with open(PROJECT_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"更新项目配置失败：{e}")

def send_completion_notification(processed, failed, elapsed_hours):
    """发送完成通知"""
    message = f"""
═══════════════════════════════════════════════════
🎉 LinkedIn 联系人信息采集已完成！
═══════════════════════════════════════════════════

📊 采集统计：
   - 总计：{processed}/3185 (100%)
   - 成功：{processed - failed} 位
   - 失败：{failed} 位
   - 成功率：{(processed-failed)/processed*100:.1f}%
   - 耗时：约{elapsed_hours:.1f}小时

📁 输出文件：
   - contact_profiles_full.csv（Profile 数据）
   - contact_posts_90days.csv（90 天发帖）
   - business_leads.csv（高意向线索）
   - analysis_summary.json（分析摘要）

🚀 Sub-Agent 改进项目已就绪！
   - 老板，LinkedIn 采集已完成，是否立即开始执行 Sub-Agent？
   - 预计执行时间：4-7 小时
   - 预期产出：
     - linkedin_master_database.csv（完整数据库）
     - linkedin_business_leads.csv（高意向线索）

请指示是否开始执行 Sub-Agent 项目！✈️
"""
    
    print(message)
    
    # 保存到通知文件
    notification_file = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\collection_complete_notification.txt")
    with open(notification_file, 'w', encoding='utf-8') as f:
        f.write(f"通知时间：{datetime.now().isoformat()}\n")
        f.write(message)
    
    # 更新项目状态
    update_project_status('linkedin_collection_completed', datetime.now().isoformat())

def main():
    """主监控程序"""
    print("="*60)
    print("LinkedIn 采集完成监控")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标：{TOTAL_CONTACTS} 位联系人")
    print(f"检查间隔：{CHECK_INTERVAL_SECONDS//60} 分钟")
    print("="*60)
    
    start_time = datetime.now()
    
    for check_num in range(MAX_CHECKS):
        progress, processed, failed = check_linkedin_progress()
        
        if progress:
            progress_pct = (processed / TOTAL_CONTACTS) * 100
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检查 #{check_num+1}")
            print(f"进度：{processed}/{TOTAL_CONTACTS} ({progress_pct:.1f}%)")
            print(f"失败：{failed} 位")
            print(f"耗时：{elapsed_hours:.1f} 小时")
            print(f"预计完成：{(TOTAL_CONTACTS - processed) / max((processed / max(elapsed_hours, 0.1)), 1) * 1.0:.1f} 小时")
        else:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 进度文件不存在，等待采集开始...")
        
        # 检查是否完成
        if processed >= TOTAL_CONTACTS:
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
            print(f"\n🎉 采集完成！总耗时：{elapsed_hours:.1f} 小时")
            
            send_completion_notification(processed, failed, elapsed_hours)
            return True
        
        # 等待下次检查
        print(f"等待 {CHECK_INTERVAL_SECONDS//60} 分钟后下次检查...")
        time.sleep(CHECK_INTERVAL_SECONDS)
    
    print(f"\n⚠️ 达到最大检查次数（{MAX_CHECKS}次），停止监控")
    return False

if __name__ == '__main__':
    main()
