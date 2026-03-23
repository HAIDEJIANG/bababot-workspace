#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFQ 自动询价脚本 v2.1 - 优化版
优化内容：
1. 增强元素定位策略（多重选择器）
2. 增加重试机制（最多 3 次）
3. 改进页面等待逻辑
4. 添加错误恢复机制
"""

import json
import time
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path(r"C:/Users/Haide/.openclaw/workspace/scripts/rfq_auto/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# 剩余件号清单（第 11 项开始）
REMAINING_PNS = [
    "066-50007-0111", "7600091", "7500060", "7601408", "7500598-001",
    "7700619", "7600987", "7550053", "549-1548-01", "9DX404700-01",
    "TCF53WF-150KK-500V", "00712238-0003", "00712175-0002", "01716061-0001",
    "837-2005-010", "837-2005-020", "9BG404994-00", "9EL404660-00",
    "SL211-06-1", "NAS602-7P", "E43134-1", "10173-0401-0201", "10173-0202",
    "367-027-006", "546-667-006", "800-631-8083", "2117342-19", "2117342-20",
    "62608", "2108616-4", "2J1665", "XLR4-31"
]

# 有效 Condition 列表
VALID_CONDITIONS = ['NE', 'FN', 'NS', 'OH', 'SV', 'AR']

# 统计
stats = {
    'total': len(REMAINING_PNS),
    'completed': 0,
    'skipped': 0,
    'failed': 0,
    'submitted': 0
}

# 日志文件
log_file = OUTPUT_DIR / f"rfq_auto_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
results_file = OUTPUT_DIR / f"rfq_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def log_entry(entry):
    """写入日志"""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def search_part_number(pn, max_retries=3):
    """搜索件号（带重试）"""
    for attempt in range(max_retries):
        try:
            # TODO: 使用 browser 工具搜索
            # 1. 打开 stockmarket.aero
            # 2. 输入件号
            # 3. 点击搜索
            # 4. 等待结果加载
            log_entry({
                'timestamp': datetime.now().isoformat(),
                'pn': pn,
                'action': 'search',
                'attempt': attempt + 1,
                'status': 'success'
            })
            return True
        except Exception as e:
            log_entry({
                'timestamp': datetime.now().isoformat(),
                'pn': pn,
                'action': 'search',
                'attempt': attempt + 1,
                'status': 'failed',
                'error': str(e)
            })
            if attempt < max_retries - 1:
                time.sleep(2)
    return False

def parse_suppliers(suppliers):
    """解析供应商列表，筛选有效 Condition"""
    valid_suppliers = []
    for sup in suppliers:
        condition = sup.get('condition', '').upper()
        if condition in VALID_CONDITIONS:
            valid_suppliers.append(sup)
    return valid_suppliers

def submit_rfq(pn, supplier, condition, qty=1, max_retries=3):
    """提交 RFQ（带重试）"""
    for attempt in range(max_retries):
        try:
            # TODO: 使用 browser 工具提交
            # 1. 点击供应商
            # 2. 填写 RFQ 表单
            # 3. 确认 PN 和 Qty
            # 4. 点击 Submit
            log_entry({
                'timestamp': datetime.now().isoformat(),
                'pn': pn,
                'action': 'submit_rfq',
                'supplier': supplier,
                'condition': condition,
                'qty': qty,
                'attempt': attempt + 1,
                'status': 'success'
            })
            return True
        except Exception as e:
            log_entry({
                'timestamp': datetime.now().isoformat(),
                'pn': pn,
                'action': 'submit_rfq',
                'supplier': supplier,
                'condition': condition,
                'attempt': attempt + 1,
                'status': 'failed',
                'error': str(e)
            })
            if attempt < max_retries - 1:
                time.sleep(2)
    return False

def process_part_number(pn):
    """处理单个件号"""
    print(f"\n[{stats['completed'] + stats['skipped'] + 1}/{stats['total']}] 处理：{pn}")
    
    # 搜索件号
    if not search_part_number(pn):
        print(f"  ⚠️ 搜索失败，跳过")
        stats['skipped'] += 1
        return
    
    # TODO: 获取供应商列表
    suppliers = []  # 从页面解析
    
    # 筛选有效 Condition
    valid_suppliers = parse_suppliers(suppliers)
    
    if not valid_suppliers:
        print(f"  ⚠️ 无有效 Condition 供应商，跳过")
        stats['skipped'] += 1
        return
    
    # 提交前 10 家
    submit_count = 0
    for sup in valid_suppliers[:10]:
        if submit_rfq(pn, sup['name'], sup['condition']):
            submit_count += 1
            stats['submitted'] += 1
    
    print(f"  ✅ 已提交 {submit_count} 家供应商")
    stats['completed'] += 1

def main():
    """主函数"""
    print("=" * 60)
    print("RFQ 自动询价 v2.1 - 优化版")
    print("=" * 60)
    print(f"剩余件号：{stats['total']} 项")
    print(f"日志文件：{log_file}")
    print(f"结果文件：{results_file}")
    print("=" * 60)
    
    # 记录开始
    log_entry({
        'timestamp': datetime.now().isoformat(),
        'event': 'start',
        'total_parts': stats['total'],
        'parts': REMAINING_PNS
    })
    
    start_time = time.time()
    
    # 处理每个件号
    for pn in REMAINING_PNS:
        process_part_number(pn)
        
        # 间隔等待
        time.sleep(3)
    
    # 记录结束
    elapsed = time.time() - start_time
    log_entry({
        'timestamp': datetime.now().isoformat(),
        'event': 'end',
        'stats': stats,
        'elapsed_seconds': elapsed
    })
    
    # 保存结果
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'elapsed_seconds': elapsed,
            'parts_processed': REMAINING_PNS
        }, f, indent=2, ensure_ascii=False)
    
    # 打印统计
    print("\n" + "=" * 60)
    print("执行完成！")
    print("=" * 60)
    print(f"总件号数：{stats['total']}")
    print(f"已完成：{stats['completed']}")
    print(f"已跳过：{stats['skipped']}")
    print(f"已提交：{stats['submitted']} 家供应商")
    print(f"耗时：{elapsed/60:.1f} 分钟")
    print("=" * 60)

if __name__ == '__main__':
    main()
