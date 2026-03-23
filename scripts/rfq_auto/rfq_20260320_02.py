#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFQ20260320-02 四川海特 42 项询价任务 - 自动执行脚本
基于 runner_v3_stable.py 优化

核心要求：
1. 42 项必须全部完成
2. 每项提交前 10 家有效供应商（Condition: NE, FN, NS, OH, SV, AR）
3. 每完成 5 项自动保存进度
4. 使用成熟脚本执行
"""

import json
import time
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

OUTPUT_DIR = Path(r"C:/Users/Haide/.openclaw/workspace/scripts/rfq_auto/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

PROGRESS_FILE = Path(r"C:/Users/Haide/Desktop/OPENCLAW/RFQ20260320-02_Progress.md")
Path(r"C:/Users/Haide/Desktop/OPENCLAW").mkdir(exist_ok=True)

# 42 个件号清单
PARTS_LIST = [
    {"pn": "964-0452-001", "desc": "HF 收发机", "condition": "可用件", "qty": 1, "mfr": "HONEYWELL", "status": "已提交 1 家"},
    {"pn": "731964FS6-130", "desc": "板卡引导槽", "condition": "全新件", "qty": 4, "mfr": "FISCHER ELEKTRONIK", "status": "待处理"},
    {"pn": "31-8321-1", "desc": "灯泡组件", "condition": "全新件", "qty": 5, "mfr": "Honeywell", "status": "待处理"},
    {"pn": "433-100-005", "desc": "开关护盖", "condition": "全新件", "qty": 5, "mfr": "V81590", "status": "待处理"},
    {"pn": "432164032", "desc": "风扇叶", "condition": "全新件", "qty": 1, "mfr": "be", "status": "待处理"},
    {"pn": "432004168", "desc": "FAN MOTOR", "condition": "全新件", "qty": 2, "mfr": "be", "status": "待处理"},
    {"pn": "805786-1", "desc": "可调电阻", "condition": "全新件", "qty": 2, "mfr": "unk", "status": "待处理"},
    {"pn": "L15089", "desc": "电位器", "condition": "全新件", "qty": 2, "mfr": "POEENTIOMETERS.COM", "status": "待处理"},
    {"pn": "B397BAM0624", "desc": "飞行增稳计算机", "condition": "可用件", "qty": 1, "mfr": "THALES", "status": "待处理"},
    {"pn": "U431BAM00", "desc": "电源", "condition": "全新件", "qty": 1, "mfr": "THALES", "status": "待处理"},
    {"pn": "U431BBM", "desc": "电源", "condition": "全新件", "qty": 1, "mfr": "THALES", "status": "待处理"},
    {"pn": "651-2606-001", "desc": "轴", "condition": "全新件", "qty": 5, "mfr": "COLLINS", "status": "待处理"},
    {"pn": "10170-0202", "desc": "多油箱指示器", "condition": "可用件", "qty": 1, "mfr": "UTC", "status": "待处理"},
    {"pn": "174117-02", "desc": "电缆组件", "condition": "全新件", "qty": 1, "mfr": "ge", "status": "待处理"},
    {"pn": "10155-0550", "desc": "电容", "condition": "全新件", "qty": 15, "mfr": "honeywell", "status": "待处理"},
    {"pn": "259-2971-030", "desc": "开关", "condition": "全新件", "qty": 2, "mfr": "COLLINS", "status": "待处理"},
    {"pn": "4014030965", "desc": "IC", "condition": "全新件", "qty": 1, "mfr": "THALES", "status": "待处理"},
    {"pn": "4007210657", "desc": "IC", "condition": "全新件", "qty": 1, "mfr": "THALES", "status": "待处理"},
    {"pn": "350E5500206", "desc": "SDAC", "condition": "可用件", "qty": 1, "mfr": "AIRBUS", "status": "待处理"},
    {"pn": "805804-1", "desc": "变压器", "condition": "全新件", "qty": 5, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "805807-1", "desc": "电感", "condition": "全新件", "qty": 5, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "2117342-20", "desc": "APU 控制组件", "condition": "可用件", "qty": 2, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "1096064-118", "desc": "筛选器", "condition": "全新件", "qty": 3, "mfr": "V07217", "status": "待处理"},
    {"pn": "1152466-250", "desc": "起动转换组件", "condition": "可用件", "qty": 1, "mfr": "07217", "status": "待处理"},
    {"pn": "2110212-4", "desc": "后面板", "condition": "全新件", "qty": 1, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "2110212-6", "desc": "后面板", "condition": "全新件", "qty": 1, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "17403-05", "desc": "电路板", "condition": "全新件", "qty": 1, "mfr": "DOWKEY", "status": "待处理"},
    {"pn": "21126-28", "desc": "线圈", "condition": "全新件", "qty": 1, "mfr": "DOWKEY", "status": "待处理"},
    {"pn": "71217-0003", "desc": "液晶片", "condition": "全新件", "qty": 1, "mfr": "ONTIC", "status": "待处理"},
    {"pn": "2101-01-2", "desc": "燃油量指示器", "condition": "可用件", "qty": 1, "mfr": "ONTIC", "status": "待处理"},
    {"pn": "29100A2140054K", "desc": "灯泡", "condition": "全新件", "qty": 2, "mfr": "F6175", "status": "待处理"},
    {"pn": "29120B2140089Z", "desc": "灯罩", "condition": "全新件", "qty": 2, "mfr": "F6175", "status": "待处理"},
    {"pn": "52900A2501294Y0", "desc": "密封圈", "condition": "全新件", "qty": 4, "mfr": "F6175", "status": "待处理"},
    {"pn": "27624AJ040LE", "desc": "垫片", "condition": "全新件", "qty": 16, "mfr": "F6175", "status": "待处理"},
    {"pn": "52900A2501298G0", "desc": "密封圈", "condition": "全新件", "qty": 2, "mfr": "F6175", "status": "待处理"},
    {"pn": "55-03-05-44", "desc": "弹垫", "condition": "全新件", "qty": 2, "mfr": "F6175", "status": "待处理"},
    {"pn": "682-1001-001", "desc": "灯帽", "condition": "全新件", "qty": 10, "mfr": "V81590", "status": "待处理"},
    {"pn": "433-100-002", "desc": "开关护盖", "condition": "全新件", "qty": 3, "mfr": "V81590", "status": "待处理"},
    {"pn": "30090236-0511", "desc": "PSM", "condition": "全新件", "qty": 1, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "30060148-0501", "desc": "PS", "condition": "全新件", "qty": 1, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "066-50007-0432", "desc": "ALT", "condition": "可用件", "qty": 1, "mfr": "HONEYWELL", "status": "待处理"},
    {"pn": "066-50007-0111", "desc": "PS", "condition": "可用件", "qty": 1, "mfr": "HONEYWELL", "status": "待处理"},
]

# 有效 Condition 列表
VALID_CONDITIONS = ['NE', 'FN', 'NS', 'OH', 'SV', 'AR']
CONDITION_PRIORITY = {'NE': 1, 'FN': 2, 'NS': 3, 'OH': 4, 'SV': 5, 'AR': 6}

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 3
PAGE_LOAD_TIMEOUT = 30
ITEM_DELAY = 3  # 每项之间等待 3 秒

# 统计
stats = {
    'total': len(PARTS_LIST),
    'completed': 0,
    'skipped_no_suppliers': 0,
    'skipped_invalid_condition': 0,
    'failed': 0,
    'submitted': 0,
    'results': []
}

# 日志文件
run_id = "RFQ20260320-02"
log_file = OUTPUT_DIR / f"rfq_auto_run_{run_id}.jsonl"
results_file = OUTPUT_DIR / f"rfq_result_{run_id}.json"
state_file = OUTPUT_DIR / f"rfq_state_{run_id}.json"

# ==================== 日志函数 ====================

def log_entry(entry):
    """写入日志"""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False, indent=None) + '\n')

def save_state():
    """保存进度状态"""
    state = {
        'timestamp': datetime.now().isoformat(),
        'run_id': run_id,
        'stats': {
            'total': stats['total'],
            'completed': stats['completed'],
            'skipped_no_suppliers': stats['skipped_no_suppliers'],
            'skipped_invalid_condition': stats['skipped_invalid_condition'],
            'failed': stats['failed'],
            'submitted': stats['submitted']
        },
        'last_completed_index': stats['completed'] + stats['skipped_no_suppliers'] + stats['skipped_invalid_condition'] + stats['failed']
    }
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def save_progress_markdown():
    """保存进度报告（Markdown 格式）"""
    completed_parts = [r for r in stats['results'] if r.get('status') in ['completed', 'skipped', 'failed']]
    
    content = f"""# RFQ20260320-02 四川海特询价进度报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**运行 ID**: {run_id}

## 总体统计
- 总件号数：{stats['total']}
- 已完成：{stats['completed']}
- 已跳过：{stats['skipped_no_suppliers'] + stats['skipped_invalid_condition']}
  - 无供应商：{stats['skipped_no_suppliers']}
  - 无效 Condition: {stats['skipped_invalid_condition']}
- 已失败：{stats['failed']}
- 已提交供应商：{stats['submitted']} 家

## 处理详情

| 序号 | 件号 | 描述 | 条件 | 数量 | 制造商 | 状态 | 提交数 |
|------|------|------|------|------|--------|------|--------|
"""
    
    for i, part in enumerate(PARTS_LIST):
        result = next((r for r in stats['results'] if r['pn'] == part['pn']), None)
        if result:
            status_icon = {'completed': '✅', 'skipped': '⚠️', 'failed': '❌', 'pending': '⏳'}.get(result.get('status', 'pending'), '⏳')
            submitted = result.get('submitted_count', 0)
        else:
            status_icon = '⏳'
            submitted = 0
        
        content += f"| {i+1} | {part['pn']} | {part['desc']} | {part['condition']} | {part['qty']} | {part['mfr']} | {status_icon} | {submitted} |\n"
    
    content += f"""
## 最近活动
{json.dumps(stats['results'][-10:] if len(stats['results']) > 10 else stats['results'], ensure_ascii=False, indent=2)}

---
*每 5 项自动更新 | 下次更新：完成第 {((stats['completed'] + stats['skipped_no_suppliers'] + stats['skipped_invalid_condition'] + stats['failed']) // 5 + 1) * 5} 项*
"""
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def save_results():
    """保存最终结果"""
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'run_id': run_id,
            'stats': stats,
            'parts_processed': PARTS_LIST
        }, f, indent=2, ensure_ascii=False)

# ==================== 浏览器操作函数 ====================

def browser_command(cmd, args=None, max_retries=MAX_RETRIES):
    """
    执行浏览器命令（带重试机制）
    注意：此函数需要与 OpenClaw browser 工具集成
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # TODO: 实际执行时需要调用 browser 工具
            # 这里使用占位符，实际执行时替换
            log_entry({
                'timestamp': datetime.now().isoformat(),
                'action': cmd,
                'attempt': attempt + 1,
                'status': 'success'
            })
            
            return {'status': 'success', 'attempt': attempt + 1}
            
        except Exception as e:
            last_error = str(e)
            log_entry({
                'timestamp': datetime.now().isoformat(),
                'action': cmd,
                'attempt': attempt + 1,
                'status': 'failed',
                'error': last_error
            })
            
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    
    return {'status': 'failed', 'error': last_error, 'attempts': max_retries}

def wait_for_page_load(timeout=PAGE_LOAD_TIMEOUT):
    """智能等待页面加载完成"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)
    return True

# ==================== 业务逻辑函数 ====================

def search_part_number(pn, qty=1):
    """
    搜索件号并获取供应商列表
    
    Args:
        pn: 件号
        qty: 数量
    
    Returns:
        list: 供应商列表，或 None（搜索失败）
    """
    print(f"  🔍 搜索：{pn}")
    
    # 步骤 1: 打开 stockmarket.aero
    result = browser_command('open', {
        'url': 'https://www.stockmarket.aero/StockMarket/Welcome.do',
        'loadState': 'networkidle',
        'timeoutMs': 30000
    })
    
    if result.get('status') != 'success':
        print(f"    ❌ 打开网站失败")
        return None
    
    # 步骤 2: 输入件号并搜索
    # TODO: 实现具体的浏览器操作
    
    # 步骤 3: 解析供应商列表
    suppliers = parse_suppliers_from_snapshot(pn)
    
    return suppliers

def parse_suppliers_from_snapshot(pn):
    """从页面快照解析供应商列表"""
    # TODO: 实际实现需要从浏览器快照解析
    # 这里返回示例数据
    suppliers = []
    
    log_entry({
        'timestamp': datetime.now().isoformat(),
        'action': 'parse_suppliers',
        'pn': pn,
        'count': len(suppliers)
    })
    
    return suppliers

def filter_valid_suppliers(suppliers):
    """筛选有效 Condition 的供应商"""
    valid = []
    for sup in suppliers:
        cond = sup.get('condition', '').upper()
        if cond in VALID_CONDITIONS:
            valid.append(sup)
        else:
            log_entry({
                'timestamp': datetime.now().isoformat(),
                'action': 'filter_supplier',
                'supplier': sup.get('name'),
                'condition': cond,
                'status': 'skipped_invalid_condition'
            })
    
    # 按优先级排序
    valid.sort(key=lambda x: CONDITION_PRIORITY.get(x.get('condition', '').upper(), 99))
    
    return valid

def submit_rfq(pn, supplier, condition, qty=1):
    """提交 RFQ"""
    print(f"    📤 提交 RFQ 至 {supplier} ({condition})")
    
    # TODO: 实现具体的 RFQ 提交流程
    
    result = browser_command('submit_rfq', {
        'pn': pn,
        'supplier': supplier,
        'condition': condition,
        'qty': qty
    })
    
    if result.get('status') == 'success':
        stats['submitted'] += 1
        print(f"    ✅ 提交成功")
        return True
    else:
        print(f"    ❌ 提交失败：{result.get('error')}")
        return False

def process_part_number(part_info):
    """处理单个件号"""
    pn = part_info['pn']
    qty = part_info['qty']
    desc = part_info['desc']
    
    index = stats['completed'] + stats['skipped_no_suppliers'] + stats['skipped_invalid_condition'] + stats['failed']
    print(f"\n[{index + 1}/{stats['total']}] 处理：{pn} ({desc})")
    
    result_record = {
        'pn': pn,
        'desc': desc,
        'qty': qty,
        'mfr': part_info.get('mfr', ''),
        'status': 'pending',
        'submitted_count': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    # 步骤 1: 搜索件号
    suppliers = search_part_number(pn, qty)
    
    if suppliers is None:
        print(f"  ⚠️ 搜索失败，跳过")
        result_record['status'] = 'failed'
        result_record['reason'] = 'search_failed'
        stats['failed'] += 1
        stats['results'].append(result_record)
        save_state()
        return 'failed'
    
    if not suppliers:
        print(f"  ⚠️ 无供应商，跳过")
        result_record['status'] = 'skipped'
        result_record['reason'] = 'no_suppliers'
        stats['skipped_no_suppliers'] += 1
        stats['results'].append(result_record)
        save_state()
        return 'skipped'
    
    # 步骤 2: 筛选有效 Condition
    valid_suppliers = filter_valid_suppliers(suppliers)
    
    if not valid_suppliers:
        print(f"  ⚠️ 无有效 Condition 供应商，跳过")
        result_record['status'] = 'skipped'
        result_record['reason'] = 'invalid_condition'
        stats['skipped_invalid_condition'] += 1
        stats['results'].append(result_record)
        save_state()
        return 'skipped'
    
    # 步骤 3: 提交前 10 家
    submit_count = 0
    for sup in valid_suppliers[:10]:
        if submit_rfq(pn, sup['name'], sup['condition'], qty):
            submit_count += 1
    
    print(f"  ✅ 已提交 {submit_count}/{len(valid_suppliers[:10])} 家供应商")
    result_record['status'] = 'completed'
    result_record['submitted_count'] = submit_count
    result_record['total_valid'] = len(valid_suppliers)
    stats['completed'] += 1
    stats['results'].append(result_record)
    save_state()
    
    return 'completed'

# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 70)
    print("RFQ20260320-02 四川海特 42 项询价任务")
    print("=" * 70)
    print(f"运行 ID: {run_id}")
    print(f"总件号数：{stats['total']} 项")
    print(f"日志文件：{log_file}")
    print(f"结果文件：{results_file}")
    print(f"进度文件：{PROGRESS_FILE}")
    print("=" * 70)
    
    # 记录开始
    log_entry({
        'timestamp': datetime.now().isoformat(),
        'event': 'start',
        'total_parts': stats['total'],
        'parts': [p['pn'] for p in PARTS_LIST],
        'version': '3.0-stable'
    })
    
    start_time = time.time()
    
    # 处理每个件号
    for i, part in enumerate(PARTS_LIST):
        process_part_number(part)
        
        # 每项之间等待
        if i < len(PARTS_LIST) - 1:
            print(f"  ⏳ 等待 {ITEM_DELAY} 秒...")
            time.sleep(ITEM_DELAY)
        
        # 每完成 5 项保存进度
        current_index = stats['completed'] + stats['skipped_no_suppliers'] + stats['skipped_invalid_condition'] + stats['failed']
        if current_index % 5 == 0:
            print(f"\n📝 保存进度报告（已完成 {current_index} 项）...")
            save_progress_markdown()
    
    # 记录结束
    elapsed = time.time() - start_time
    log_entry({
        'timestamp': datetime.now().isoformat(),
        'event': 'end',
        'stats': stats,
        'elapsed_seconds': elapsed
    })
    
    # 保存最终结果和进度
    save_results()
    save_progress_markdown()
    
    # 打印统计
    print("\n" + "=" * 70)
    print("✅ 执行完成！")
    print("=" * 70)
    print(f"总件号数：{stats['total']}")
    print(f"已完成：{stats['completed']}")
    print(f"已跳过：{stats['skipped_no_suppliers'] + stats['skipped_invalid_condition']}")
    print(f"  - 无供应商：{stats['skipped_no_suppliers']}")
    print(f"  - 无效 Condition: {stats['skipped_invalid_condition']}")
    print(f"已失败：{stats['failed']}")
    print(f"已提交：{stats['submitted']} 家供应商")
    print(f"耗时：{elapsed/60:.1f} 分钟")
    print("=" * 70)
    print(f"\n📁 输出文件:")
    print(f"  进度报告：{PROGRESS_FILE}")
    print(f"  日志：{log_file}")
    print(f"  结果：{results_file}")
    print(f"  状态：{state_file}")
    print("=" * 70)

if __name__ == '__main__':
    main()
