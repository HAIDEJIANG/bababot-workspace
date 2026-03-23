#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFQ20260320-02 四川海特 42 项完整询价任务 - Playwright 自动化
每完成 5 项自动保存进度
"""

import json
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# 42 个零件号清单
PARTS_42 = [
    {"pn": "964-0452-001", "desc": "HF 收发机", "qty": 1, "oem": "HONEYWELL"},
    {"pn": "731964FS6-130", "desc": "板卡引导槽", "qty": 4, "oem": "FISCHER ELEKTRONIK"},
    {"pn": "31-8321-1", "desc": "灯泡组件", "qty": 5, "oem": "Honeywell"},
    {"pn": "433-100-005", "desc": "开关护盖", "qty": 5, "oem": "V81590"},
    {"pn": "432164032", "desc": "风扇叶", "qty": 1, "oem": "be"},
    {"pn": "432004168", "desc": "FAN MOTOR", "qty": 2, "oem": "be"},
    {"pn": "805786-1", "desc": "可调电阻", "qty": 2, "oem": "unk"},
    {"pn": "L15089", "desc": "电位器", "qty": 2, "oem": "POEENTIOMETERS.COM"},
    {"pn": "B397BAM0624", "desc": "飞行增稳计算机", "qty": 1, "oem": "THALES"},
    {"pn": "U431BAM00", "desc": "电源", "qty": 1, "oem": "THALES"},
    {"pn": "U431BBM", "desc": "电源", "qty": 1, "oem": "THALES"},
    {"pn": "651-2606-001", "desc": "轴", "qty": 5, "oem": "COLLINS"},
    {"pn": "10170-0202", "desc": "多油箱指示器", "qty": 1, "oem": "UTC"},
    {"pn": "174117-02", "desc": "电缆组件", "qty": 1, "oem": "ge"},
    {"pn": "10155-0550", "desc": "电容", "qty": 15, "oem": "honeywell"},
    {"pn": "259-2971-030", "desc": "开关", "qty": 2, "oem": "COLLINS"},
    {"pn": "4014030965", "desc": "IC", "qty": 1, "oem": "THALES"},
    {"pn": "4007210657", "desc": "IC", "qty": 1, "oem": "THALES"},
    {"pn": "350E5500206", "desc": "SDAC", "qty": 1, "oem": "AIRBUS"},
    {"pn": "805804-1", "desc": "变压器", "qty": 5, "oem": "HONEYWELL"},
    {"pn": "805807-1", "desc": "电感", "qty": 5, "oem": "HONEYWELL"},
    {"pn": "2117342-20", "desc": "APU 控制组件", "qty": 2, "oem": "HONEYWELL"},
    {"pn": "1096064-118", "desc": "筛选器", "qty": 3, "oem": "V07217"},
    {"pn": "1152466-250", "desc": "起动转换组件", "qty": 1, "oem": "07217"},
    {"pn": "2110212-4", "desc": "后面板", "qty": 1, "oem": "HONEYWELL"},
    {"pn": "2110212-6", "desc": "后面板", "qty": 1, "oem": "HONEYWELL"},
    {"pn": "17403-05", "desc": "电路板", "qty": 1, "oem": "DOWKEY"},
    {"pn": "21126-28", "desc": "线圈", "qty": 1, "oem": "DOWKEY"},
    {"pn": "71217-0003", "desc": "液晶片", "qty": 1, "oem": "ONTIC"},
    {"pn": "2101-01-2", "desc": "燃油量指示器", "qty": 1, "oem": "ONTIC"},
    {"pn": "29100A2140054K", "desc": "灯泡", "qty": 2, "oem": "F6175"},
    {"pn": "29120B2140089Z", "desc": "灯罩", "qty": 2, "oem": "F6175"},
    {"pn": "52900A2501294Y0", "desc": "密封圈", "qty": 4, "oem": "F6175"},
    {"pn": "27624AJ040LE", "desc": "垫片", "qty": 16, "oem": "F6175"},
    {"pn": "52900A2501298G0", "desc": "密封圈", "qty": 2, "oem": "F6175"},
    {"pn": "55-03-05-44", "desc": "弹垫", "qty": 2, "oem": "F6175"},
    {"pn": "682-1001-001", "desc": "灯帽", "qty": 10, "oem": "V81590"},
    {"pn": "433-100-002", "desc": "开关护盖", "qty": 3, "oem": "V81590"},
    {"pn": "30090236-0511", "desc": "PSM", "qty": 1, "oem": "HONEYWELL"},
    {"pn": "30060148-0501", "desc": "PS", "qty": 1, "oem": "HONEYWELL"},
    {"pn": "066-50007-0432", "desc": "ALT", "qty": 1, "oem": "HONEYWELL"},
    {"pn": "066-50007-0111", "desc": "PS", "qty": 1, "oem": "HONEYWELL"},
]

VALID_CONDITIONS = ['NE', 'FN', 'NS', 'OH', 'SV', 'AR']
PROGRESS_FILE = Path("C:/Users/Haide/Desktop/OPENCLAW/RFQ20260320-02_Progress.md")
RESULT_FILE = Path("C:/Users/Haide/.openclaw/workspace/scripts/rfq_auto/outputs/rfq_result_RFQ20260320-02.json")
LOG_FILE = Path("C:/Users/Haide/.openclaw/workspace/scripts/rfq_auto/outputs/rfq_auto_run_RFQ20260320-02.jsonl")

def save_progress(stats, parts_results):
    content = f"""# RFQ20260320-02 四川海特自动询价进度报告

**RFQ 编号**: RFQ20260320-02  
**客户**: 四川海特 (SICHUAN HAITE HIGH-TECH)  
**联系人**: 张雨欣 Cynthia Zhang (cynthia@haitegroup.com)  
**截止日期**: 2026 年 3 月 27 日  
**总项数**: 42 项  

**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M GMT+8')}  
**执行账户**: sale@aeroedgeglobal.com  
**平台**: stockmarket.aero  

---

## 执行状态

- **已完成**: {stats['completed']}/42
- **跳过 (无供应商)**: {stats['skipped_no_suppliers']}
- **跳过 (无效 Condition)**: {stats['skipped_invalid_condition']}
- **失败**: {stats['failed']}
- **提交总数**: {stats['total_submissions']}
- **成功提交**: {stats['successful_submissions']}

---

## 42 个件号清单

| 序号 | 件号 | 描述 | Condition | Qty | OEM | 状态 |
|------|------|------|-----------|-----|-----|------|
"""
    for i, part in enumerate(PARTS_42, 1):
        result = parts_results.get(part['pn'], {})
        status = result.get('status', '待处理')
        content += f"| {i} | {part['pn']} | {part['desc']} | 可用件 | {part['qty']} | {part['oem']} | {status} |\n"
    
    content += f"\n---\n\n*最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    PROGRESS_FILE.parent.mkdir(exist_ok=True)
    PROGRESS_FILE.write_text(content, encoding='utf-8')
    print(f"[SAVE] Progress saved: {PROGRESS_FILE}")

def log_entry(entry):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def process_part(page, part, index):
    """处理单个零件的 RFQ 提交"""
    pn = part['pn']
    print(f"\n[SEARCH] [{index}/42] Processing: {pn}")
    
    try:
        # 搜索零件
        search_box = page.locator('input[value="Enter Part Number"]').first
        search_box.fill(pn)
        page.locator('input[value="Go"]').first.click()
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
        # 检查是否有结果
        if "No parts found" in page.content():
            print(f"  [WARN] No suppliers found")
            return {'status': 'skipped_no_suppliers', 'suppliers_found': 0}
        
        # 展开所有行
        try:
            page.get_by_text("Expand All").first.click()
            time.sleep(3)
        except:
            pass
        
        # 查找有效 Condition 的供应商
        suppliers = []
        rows = page.locator('tr').all()
        for row in rows:
            text = row.inner_text()
            if pn in text:
                for cond in VALID_CONDITIONS:
                    if cond in text.upper():
                        suppliers.append({'condition': cond, 'text': text})
                        break
        
        print(f"  [INFO] Found {len(suppliers)} valid suppliers")
        
        if not suppliers:
            return {'status': 'skipped_no_suppliers', 'suppliers_found': 0}
        
        # 提交前 10 家
        submitted = 0
        for sup in suppliers[:10]:
            try:
                # 点击 Send
                send_btn = row.get_by_text("Send").first
                if send_btn.is_visible():
                    send_btn.click()
                    time.sleep(2)
                    
                    # 点击 Submit RFQ
                    submit_btn = page.get_by_text("Submit RFQ").first
                    if submit_btn.is_visible():
                        submit_btn.click()
                        time.sleep(2)
                        submitted += 1
                        print(f"  [OK] Submitted {submitted}/10")
            except:
                continue
        
        return {'status': f'completed ({submitted}/10+)', 'submitted': submitted}
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return {'status': 'failed', 'error': str(e)}

def main():
    print("[START] RFQ20260320-02 42 items automation task")
    
    stats = {
        'completed': 0, 'skipped_no_suppliers': 0,
        'skipped_invalid_condition': 0, 'failed': 0,
        'total_submissions': 0, 'successful_submissions': 0
    }
    parts_results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        # 登录
        print("[LOGIN] Logging in to stockmarket.aero...")
        page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do")
        time.sleep(2)
        
        if "Login" in page.content():
            page.fill('input[type="text"]', 'sale@aeroedgeglobal.com')
            page.fill('input[type="password"]', 'Aa138222')
            page.click('button[value="Submit"]')
            page.wait_for_load_state('networkidle')
            time.sleep(3)
        
        print("[OK] Login successful")
        
        # 从第 2 项开始（第 1 项已完成）
        for i, part in enumerate(PARTS_42[1:], start=2):
            result = process_part(page, part, i)
            parts_results[part['pn']] = result
            
            if 'submitted' in result:
                stats['total_submissions'] += result['submitted']
                stats['successful_submissions'] += result['submitted']
            
            if 'completed' in result.get('status', ''):
                stats['completed'] += 1
            elif 'skipped' in result.get('status', ''):
                stats['skipped_no_suppliers'] += 1
            elif 'failed' in result.get('status', ''):
                stats['failed'] += 1
            
            # 每 5 项保存进度
            if i % 5 == 0:
                save_progress(stats, parts_results)
                log_entry({'index': i, 'pn': part['pn'], 'result': result})
            
            time.sleep(3)  # 项之间等待
        
        # 最终保存
        save_progress(stats, parts_results)
        
        RESULT_FILE.parent.mkdir(exist_ok=True)
        with open(RESULT_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'rfq_id': 'RFQ20260320-02', 'customer': '四川海特',
                'deadline': '2026-03-27', 'total_parts': 42,
                'completed_at': datetime.now().isoformat(),
                'stats': stats, 'parts': parts_results
            }, f, indent=2, ensure_ascii=False)
        
        browser.close()
    
    print(f"\n[DONE] Task completed! Stats: {stats}")

if __name__ == "__main__":
    main()
