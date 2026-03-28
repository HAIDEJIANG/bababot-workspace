#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 采集完成监控
检查 LinkedIn 联系人采集是否完成，完成后立即通知老板
"""

import json
import time
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

PROGRESS_FILE = Path(r"C:\Users\Haide\Desktop\LINKEDIN\ANALYSIS_20260326\progress.json")
PROJECT_CONFIG_FILE = Path(r"C:\Users\Haide\.openclaw\workspace\projects\subagent-improvement\project_config.json")
TOTAL_CONTACTS = 3185
CHECK_INTERVAL_MINUTES = 5
MAX_CHECKS = 300  # 最多检查 300 次（25 小时）

# ==================== 工具函数 ====================

def check_linkedin_progress():
    """检查 LinkedIn 采集进度"""
    if not PROGRESS_FILE.exists():
        return None, 0
    
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        processed = progress.get('processed_contacts', 0)
        return progress, processed
    except Exception as e:
        print(f"读取进度文件失败：{e}")
        return None, 0

def send_notification(processed, total):
    """发送完成通知"""
    # 加载项目配置
    try:
        with open(PROJECT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        config = {}
    
    # 估算耗时
    elapsed_hours = processed / 100  # 粗略估算（约 100 人/小时）
    
    # 构建通知消息
    message = config.get('notification', {}).get('message_template', '''
老板，LinkedIn 联系人信息采集已完成！

进度：{total}/3185 (100%)
耗时：约{elapsed_hours}小时

Sub-Agent 改进项目已就绪，是否立即开始执行？

预计执行时间：4-7 小时
预期产出：
- linkedin_master_database.csv（完整数据库）
- linkedin_business_leads.csv（高意向线索）
''')
    
    message = message.format(
        total=total,
        elapsed_hours=f"{elapsed_hours:.1f}",
        posts_count="待统计"
    )
    
    print("="*60)
    print("🔔 LinkedIn 采集完成通知")
    print("="*60)
    print(message)
    print("="*60)
    
    # 更新配置（标记已发送通知）
    config['notification']['sent'] = True
    config['notification']['sent_at'] = datetime.now().isoformat()
    
    with open(PROJECT_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return message

# ==================== 主程序 ====================

def main():
    print("="*60)
    print("LinkedIn 采集完成监控")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标：{TOTAL_CONTACTS} 位联系人")
    print(f"检查间隔：{CHECK_INTERVAL_MINUTES} 分钟")
    print("="*60)
    
    checks = 0
    
    while checks < MAX_CHECKS:
        checks += 1
        
        # 检查进度
        progress, processed = check_linkedin_progress()
        
        if progress:
            remaining = TOTAL_CONTACTS - processed
            progress_pct = (processed / TOTAL_CONTACTS) * 100
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"进度：{processed}/{TOTAL_CONTACTS} ({progress_pct:.1f}%) "
                  f"剩余：{remaining}")
        
        # 检查是否完成
        if processed >= TOTAL_CONTACTS:
            print("\n✅ LinkedIn 采集完成！")
            print(f"总耗时：约{processed / 100:.1f}小时")
            print(f"处理速度：约{processed / (processed / 100):.1f}人/小时")
            
            # 发送通知
            send_notification(processed, TOTAL_CONTACTS)
            
            print("\n等待老板确认是否执行 Sub-Agent 改进项目...")
            return True
        
        # 等待下次检查
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
    
    print("\n⚠️ 达到最大检查次数，监控结束")
    return False

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n监控被用户中断")
    except Exception as e:
        print(f"\n监控异常：{e}")
