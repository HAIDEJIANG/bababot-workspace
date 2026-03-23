#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFQ20260318-01 直接 Playwright 批量提交
绕过 openclaw browser 命令，直接使用 Playwright
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# 修复编码问题
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 42 个零件清单
PARTS = [
    ("S1820612-02", "1", "NE"),
    ("X-A1B", "1", "NE"),
    ("9BG407572-70", "1", "NE"),
    ("2LA006823-70", "1", "SV"),
    ("091595-01", "1", "NE"),
    ("091595-02", "1", "NE"),
    ("00712226-0002", "5", "NE"),
    ("00712226-0001", "1", "NE"),
    ("30090331-0502", "1", "NE"),
    ("30060173-0502", "1", "NE"),
]

def log_event(event_type, data):
    """记录事件到 JSONL"""
    log_file = OUTPUT_DIR / f"rfq_direct_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    entry = {
        "ts": datetime.now().isoformat(),
        "event": event_type,
        **data
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_file

def submit_rfq_direct(page, pn, qty, cond):
    """直接提交单个 RFQ"""
    try:
        # 1. 搜索零件
        print(f"[SEARCH] {pn}")
        # 修复选择器：使用 placeholder 而不是 name
        search_box = page.locator('input[placeholder*="Part Number"], input[placeholder*="Search"]').first
        search_box.fill(pn)
        # 点击 Go 按钮
        page.locator('input[value="Go"], button:has-text("Go")').first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 2. 展开所有行（关键步骤！）
        print(f"[EXPAND] Clicking Expand All...")
        try:
            # 尝试多种展开选择器
            expand_selectors = [
                'a:has-text("Expand All")',
                'a[href="#"]:has-text("Expand")',
                'link:has-text("Expand All")'
            ]
            for selector in expand_selectors:
                try:
                    expand_btn = page.locator(selector).first
                    if expand_btn.is_visible(timeout=3000):
                        expand_btn.click()
                        print(f"[OK] Expanded via: {selector}")
                        time.sleep(2)
                        break
                except:
                    continue
        except Exception as e:
            print(f"[INFO] No expand button or already expanded")
        
        # 3. 查找目标 Condition 的供应商
        print(f"[FIND] Looking for condition {cond}")
        
        # 获取所有行
        rows = page.locator("tr").all()
        target_row = None
        
        for row in rows:
            try:
                text = row.inner_text(timeout=2000)
                if pn.upper() in text.upper() and cond in text.upper():
                    # 检查是否有 Send 按钮
                    if "Send" in text:
                        target_row = row
                        print(f"[FOUND] {cond} row found")
                        break
            except:
                continue
        
        if not target_row:
            print(f"[SKIP] No {cond} supplier found for {pn}")
            return False, "No matching supplier"
        
        # 4. 点击 Send
        print(f"[CLICK] Send button")
        send_clicked = False
        
        # 尝试多种点击方式
        for attempt in range(3):
            try:
                send_btn = target_row.locator('a:has-text("Send")').first
                send_btn.wait_for(state='visible', timeout=5000)
                time.sleep(0.5)
                
                if attempt == 0:
                    # 尝试 1: 普通点击
                    send_btn.click()
                elif attempt == 1:
                    # 尝试 2: 强制点击
                    send_btn.click(force=True)
                else:
                    # 尝试 3: JavaScript 点击
                    send_btn.evaluate('el => el.click()')
                
                send_clicked = True
                print(f"[OK] Send clicked (attempt {attempt + 1})")
                break
            except Exception as e:
                print(f"[WARN] Attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        if not send_clicked:
            return False, "Could not click Send button"
        
        # 5. 等待并处理弹窗
        print(f"[WAIT] Waiting for RFQ form...")
        
        # 等待弹窗出现（多种可能）
        form_found = False
        for wait_time in [2, 3, 5]:
            time.sleep(wait_time)
            
            # 检查是否有数量输入框
            qty_selectors = [
                'input[type="number"]',
                'input[name*="qty" i]',
                'input[name*="quantity" i]',
                'input[id*="qty"]',
                'input[placeholder*="qty" i]',
            ]
            
            for selector in qty_selectors:
                try:
                    qty_inputs = page.locator(selector)
                    if qty_inputs.count() > 0:
                        print(f"[FOUND] Quantity input via: {selector}")
                        qty_inputs.first.fill(qty)
                        print(f"[OK] Quantity filled: {qty}")
                        form_found = True
                        break
                except:
                    continue
            
            if form_found:
                break
        
        if not form_found:
            # 尝试截图调试
            try:
                page.screenshot(path="outputs/debug_form.png")
                print(f"[DEBUG] Screenshot saved")
            except:
                pass
            return False, "RFQ form did not appear"
        
        time.sleep(2)
        
        # 6. 查找并提交
        print(f"[SUBMIT] Submitting RFQ...")
        try:
            submit_selectors = [
                'input[value*="Submit" i]',
                'button:has-text("Submit")',
                'input[type="submit"]',
                'button[type="submit"]',
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btns = page.locator(selector)
                    if submit_btns.count() > 0:
                        submit_btns.first.click()
                        time.sleep(2)
                        print(f"[OK] {pn} submitted")
                        return True, "Success"
                except:
                    continue
            
            return False, "Submit button not found"
        except Exception as e:
            return False, f"Submit failed: {e}"
            
    except Exception as e:
        print(f"[ERROR] {pn}: {e}")
        return False, str(e)

def main():
    print("="*60)
    print("RFQ20260318-01 批量提交 (直接 Playwright)")
    print("="*60)
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        # 登录 stockmarket.aero
        print("[LOGIN] Opening stockmarket.aero...")
        page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do", timeout=60000)
        time.sleep(3)
        
        # 检查登录状态
        content = page.content()
        if "sale@aeroedgeglobal.com" in content or "Welcome," in content:
            print("[OK] Already logged in")
        elif "Login" in content or "Sign In" in content:
            print("[INFO] Need to login...")
            page.goto("https://www.stockmarket.aero/StockMarket/LoadLogin.do")
            time.sleep(2)
            # 自动填充并登录
            try:
                page.fill('input[type="text"]', 'sale@aeroedgeglobal.com')
                page.fill('input[type="password"]', 'Aa138222')
                page.click('button:has-text("Submit")')
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                print("[OK] Logged in successfully")
            except Exception as e:
                print(f"[WARN] Auto login failed: {e}")
                print("[WAIT] Please login manually (60 seconds)...")
                for i in range(60):
                    time.sleep(1)
                    if "Welcome," in page.content():
                        print("[OK] Manual login detected")
                        break
        else:
            print("[INFO] Login status unknown, continuing...")
        
        # 处理每个零件
        for i, (pn, qty, cond) in enumerate(PARTS, 1):
            print(f"\n[{i}/{len(PARTS)}] Processing {pn}...")
            success, msg = submit_rfq_direct(page, pn, qty, cond)
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
                print("[WAIT] 5 seconds...")
                time.sleep(5)
        
        browser.close()
    
    # 保存报告
    report = {
        "rfq_id": "RFQ20260318-01",
        "total": len(PARTS),
        "success": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    }
    
    report_file = OUTPUT_DIR / "rfq20260318_01_direct_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total: {len(PARTS)}")
    print(f"Success: {report['success']}")
    print(f"Failed: {report['failed']}")
    print(f"Report: {report_file}")

if __name__ == "__main__":
    main()
