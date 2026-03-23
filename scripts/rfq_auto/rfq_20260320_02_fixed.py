#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFQ20260320-02 四川海特 42 项询价脚本 - 修复版
修复问题：
1. 更新零件清单为 RFQ20260320-02
2. 增强错误处理
3. 添加调试截图
4. 优化选择器
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# 修复编码问题
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path(r"C:/Users/Haide/Desktop/OPENCLAW")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# RFQ20260320-02 42 个零件清单（从第 2 项开始，第 1 项已完成）
PARTS = [
    # 格式：(件号，数量，Condition)
    ("731964FS6-130", "4", "NE"),  # 第 2 项
    ("31-8321-1", "5", "NE"),  # 第 3 项
    ("433-100-005", "5", "NE"),  # 第 4 项
    ("432164032", "1", "NE"),  # 第 5 项
    ("432004168", "2", "NE"),  # 第 6 项
    ("805786-1", "2", "NE"),  # 第 7 项
    ("L15089", "2", "NE"),  # 第 8 项
    ("B397BAM0624", "1", "AR"),  # 第 9 项 - 可用件
    ("U431BAM00", "1", "NE"),  # 第 10 项
    ("U431BBM", "1", "NE"),  # 第 11 项
    ("651-2606-001", "5", "NE"),  # 第 12 项
    ("10170-0202", "1", "AR"),  # 第 13 项 - 可用件
    ("174117-02", "1", "NE"),  # 第 14 项
    ("10155-0550", "15", "NE"),  # 第 15 项
    ("259-2971-030", "2", "NE"),  # 第 16 项
    ("4014030965", "1", "NE"),  # 第 17 项
    ("4007210657", "1", "NE"),  # 第 18 项
    ("350E5500206", "1", "AR"),  # 第 19 项 - 可用件
    ("805804-1", "5", "NE"),  # 第 20 项
    ("805807-1", "5", "NE"),  # 第 21 项
    ("2117342-20", "2", "AR"),  # 第 22 项 - 可用件
    ("1096064-118", "3", "NE"),  # 第 23 项
    ("1152466-250", "1", "AR"),  # 第 24 项 - 可用件
    ("2110212-4", "1", "NE"),  # 第 25 项
    ("2110212-6", "1", "NE"),  # 第 26 项
    ("17403-05", "1", "NE"),  # 第 27 项
    ("21126-28", "1", "NE"),  # 第 28 项
    ("71217-0003", "1", "NE"),  # 第 29 项
    ("2101-01-2", "1", "AR"),  # 第 30 项 - 可用件
    ("29100A2140054K", "2", "NE"),  # 第 31 项
    ("29120B2140089Z", "2", "NE"),  # 第 32 项
    ("52900A2501294Y0", "4", "NE"),  # 第 33 项
    ("27624AJ040LE", "16", "NE"),  # 第 34 项
    ("52900A2501298G0", "2", "NE"),  # 第 35 项
    ("55-03-05-44", "2", "NE"),  # 第 36 项
    ("682-1001-001", "10", "NE"),  # 第 37 项
    ("433-100-002", "3", "NE"),  # 第 38 项
    ("30090236-0511", "1", "NE"),  # 第 39 项
    ("30060148-0501", "1", "NE"),  # 第 40 项
    ("066-50007-0432", "1", "AR"),  # 第 41 项 - 可用件
    ("066-50007-0111", "1", "AR"),  # 第 42 项 - 可用件
]

def log_event(event_type, data, log_file):
    """记录事件到 JSONL"""
    entry = {
        "ts": datetime.now().isoformat(),
        "event": event_type,
        **data
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def submit_rfq(page, pn, qty, cond, log_file):
    """提交单个 RFQ"""
    try:
        print(f"\n[SEARCH] {pn} (Qty:{qty}, Cond:{cond})")
        log_event("search_start", {"pn": pn, "qty": qty, "cond": cond}, log_file)
        
        # 1. 搜索零件 - 使用更精确的选择器
        search_box = page.locator('input[placeholder*="Part"], input[name*="part"], #partNumberInput').first
        if not search_box.is_visible(timeout=5000):
            # 备用选择器
            search_box = page.locator('input[type="text"]').first
        search_box.fill(pn)
        time.sleep(1)
        
        # 点击 Go/Search 按钮
        page.locator('input[value="Go"], input[type="submit"], button:has-text("Search")').first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 2. 点击 Expand All
        print(f"[EXPAND] Expanding all rows...")
        try:
            expand_btn = page.locator('a:has-text("Expand"), button:has-text("Expand")').first
            if expand_btn.is_visible(timeout=3000):
                expand_btn.click()
                time.sleep(2)
                print(f"[OK] Expanded")
        except Exception as e:
            print(f"[INFO] No expand button or already expanded: {e}")
        
        # 3. 查找目标 Condition 的供应商
        print(f"[FIND] Looking for {cond} condition...")
        rows = page.locator("tr").all()
        target_row = None
        
        for idx, row in enumerate(rows):
            try:
                text = row.inner_text(timeout=2000)
                # 检查是否包含件号和 Condition
                if pn.replace("-", "") in text.replace("-", "") and cond.upper() in text.upper():
                    # 检查是否有 Send 按钮
                    if "Send" in text or "send" in text.lower():
                        target_row = row
                        print(f"[FOUND] Row {idx}: {cond} condition found")
                        break
            except:
                continue
        
        if not target_row:
            print(f"[SKIP] No {cond} supplier found")
            log_event("search_failed", {"pn": pn, "reason": "No matching supplier"}, log_file)
            return False, "No matching supplier"
        
        # 4. 点击 Send
        print(f"[CLICK] Clicking Send button...")
        send_clicked = False
        
        for attempt in range(3):
            try:
                send_btn = target_row.locator('a:has-text("Send"), button:has-text("Send")').first
                send_btn.wait_for(state='visible', timeout=5000)
                time.sleep(0.5)
                
                if attempt == 0:
                    send_btn.click()
                elif attempt == 1:
                    send_btn.click(force=True)
                else:
                    page.evaluate('(el) => el.click()', send_btn)
                
                send_clicked = True
                print(f"[OK] Send clicked (attempt {attempt + 1})")
                break
            except Exception as e:
                print(f"[WARN] Attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        if not send_clicked:
            log_event("click_failed", {"pn": pn, "reason": "Could not click Send"}, log_file)
            return False, "Could not click Send"
        
        # 5. 等待弹窗并填写数量
        print(f"[WAIT] Waiting for RFQ form...")
        form_found = False
        
        # 尝试多种等待策略
        for attempt in range(5):
            wait_time = 3 + attempt * 2  # 3, 5, 7, 9, 11 秒
            time.sleep(wait_time)
            
            # 策略 1: 查找数量输入框
            qty_inputs = page.locator('input[type="number"], input[name*="qty" i], input[name*="quantity" i], input[placeholder*="Qty"]')
            if qty_inputs.count() > 0:
                try:
                    qty_inputs.first.fill(qty)
                    print(f"[OK] Quantity filled: {qty}")
                    form_found = True
                    break
                except Exception as e:
                    print(f"[WARN] Could not fill quantity: {e}")
            
            # 策略 2: 检查是否有弹窗（dialog/modal）
            try:
                dialogs = page.locator('dialog, .modal, .popup, [role="dialog"]')
                if dialogs.count() > 0:
                    print(f"[FOUND] Dialog detected")
                    # 在弹窗内查找数量输入框
                    qty_in_dialog = dialogs.first.locator('input[type="number"], input[name*="qty" i]')
                    if qty_in_dialog.count() > 0:
                        qty_in_dialog.first.fill(qty)
                        print(f"[OK] Quantity filled in dialog: {qty}")
                        form_found = True
                        break
            except:
                pass
            
            # 策略 3: 检查整个页面内容
            try:
                content = page.content()
                if "Qty" in content or "Quantity" in content or "quantity" in content:
                    print(f"[FOUND] Quantity field found in page content")
                    # 尝试所有可能的输入框
                    all_inputs = page.locator('input')
                    for i in range(all_inputs.count()):
                        try:
                            input_el = all_inputs.nth(i)
                            placeholder = input_el.get_attribute('placeholder') or ''
                            name = input_el.get_attribute('name') or ''
                            if 'qty' in placeholder.lower() or 'qty' in name.lower() or 'quantity' in placeholder.lower() or 'quantity' in name.lower():
                                input_el.fill(qty)
                                print(f"[OK] Quantity filled via input[{i}]: {qty}")
                                form_found = True
                                break
                        except:
                            continue
                    if form_found:
                        break
            except:
                pass
        
        if not form_found:
            # 截图调试
            try:
                screenshot_path = OUTPUT_DIR / f"debug_form_{pn.replace('-', '_')}_attempt{attempt+1}.png"
                page.screenshot(path=str(screenshot_path))
                print(f"[DEBUG] Screenshot saved: {screenshot_path}")
                
                # 保存页面 HTML
                html_path = OUTPUT_DIR / f"debug_form_{pn.replace('-', '_')}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(page.content())
                print(f"[DEBUG] HTML saved: {html_path}")
            except Exception as e:
                print(f"[WARN] Could not save debug info: {e}")
            
            log_event("form_failed", {"pn": pn, "reason": "Form did not appear after multiple attempts"}, log_file)
            return False, "RFQ form did not appear"
        
        time.sleep(2)
        
        # 6. 提交表单
        print(f"[SUBMIT] Submitting...")
        try:
            submit_btns = page.locator('input[value*="Submit" i], button:has-text("Submit"), input[type="submit"]')
            if submit_btns.count() > 0:
                submit_btns.first.click()
                time.sleep(3)
                print(f"[OK] {pn} submitted successfully!")
                log_event("submit_success", {"pn": pn}, log_file)
                return True, "Success"
        except Exception as e:
            log_event("submit_failed", {"pn": pn, "reason": str(e)}, log_file)
            return False, f"Submit failed: {e}"
            
    except Exception as e:
        print(f"[ERROR] {pn}: {e}")
        log_event("error", {"pn": pn, "error": str(e)}, log_file)
        return False, str(e)

def main():
    print("="*60)
    print("RFQ20260320-02 四川海特 42 项询价脚本 - 修复版")
    print("="*60)
    
    log_file = OUTPUT_DIR / f"rfq_auto_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    results = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=200, timeout=60000)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(30000)
            page.set_default_navigation_timeout(30000)
        
        # 登录
        print("[LOGIN] Opening stockmarket.aero...")
        page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do", timeout=60000)
        time.sleep(3)
        
        # 检查登录状态
        content = page.content()
        if "sale@aeroedgeglobal.com" in content or "Welcome" in content:
            print("[OK] Already logged in")
            log_event("login_success", {"method": "auto"}, log_file)
        elif "Login" in content or "Sign In" in content:
            print("[INFO] Need to login...")
            page.goto("https://www.stockmarket.aero/StockMarket/LoadLogin.do")
            time.sleep(2)
            try:
                page.fill('input[type="text"]', 'sale@aeroedgeglobal.com')
                page.fill('input[type="password"]', 'Aa138222')
                page.click('button:has-text("Submit")')
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                print("[OK] Logged in successfully")
                log_event("login_success", {"method": "auto"}, log_file)
            except Exception as e:
                print(f"[WARN] Auto login failed: {e}")
                log_event("login_failed", {"reason": str(e)}, log_file)
                print("[WAIT] Please login manually (60 seconds)...")
                for i in range(60):
                    time.sleep(1)
                    if "Welcome" in page.content():
                        print("[OK] Manual login detected")
                        log_event("login_success", {"method": "manual"}, log_file)
                        break
        else:
            print("[INFO] Login status unknown, continuing...")
            log_event("login_unknown", {}, log_file)
        
        # 处理每个零件
        for i, (pn, qty, cond) in enumerate(PARTS, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(PARTS)}] Processing {pn}...")
            print(f"{'='*60}")
            
            success, msg = submit_rfq(page, pn, qty, cond, log_file)
            results.append({
                "index": i,
                "pn": pn,
                "qty": qty,
                "condition": cond,
                "success": success,
                "message": msg,
                "timestamp": datetime.now().isoformat()
            })
            
            # 零件间等待
            if i < len(PARTS):
                print(f"\n[WAIT] 5 seconds before next item...")
                time.sleep(5)
        
        browser.close()
    
    except Exception as e:
        print(f"[FATAL] Script crashed: {e}")
        log_event("fatal_error", {"error": str(e)}, log_file)
        # 保存当前进度
        if results:
            print(f"[INFO] Saving partial results...")
    
    # 保存报告（即使崩溃也保存）
    report = {
        "rfq_id": "RFQ20260320-02",
        "customer": "四川海特",
        "total": len(PARTS),
        "success": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results,
        "completed_at": datetime.now().isoformat()
    }
    
    report_file = OUTPUT_DIR / f"rfq20260320_02_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 更新进度文件
    progress_file = OUTPUT_DIR / "RFQ20260320-02_Progress.md"
    with open(progress_file, "w", encoding="utf-8") as f:
        f.write(f"# RFQ20260320-02 进度报告\n\n")
        f.write(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 执行状态\n\n")
        f.write(f"- **总项数**: {len(PARTS)}\n")
        f.write(f"- **已完成**: {report['success']}\n")
        f.write(f"- **失败**: {report['failed']}\n\n")
        f.write(f"## 详细结果\n\n")
        f.write(f"| 序号 | 件号 | 数量 | Condition | 状态 | 消息 |\n")
        f.write(f"|------|------|------|-----------|------|------|\n")
        for r in results:
            status = "✅" if r["success"] else "❌"
            f.write(f"| {r['index']} | {r['pn']} | {r['qty']} | {r['condition']} | {status} | {r['message']} |\n")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {len(PARTS)}")
    print(f"Success: {report['success']}")
    print(f"Failed: {report['failed']}")
    print(f"Report: {report_file}")
    print(f"Progress: {progress_file}")

if __name__ == "__main__":
    main()
