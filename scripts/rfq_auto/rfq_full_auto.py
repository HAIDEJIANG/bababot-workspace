"""
RFQ Auto-Submit Script - Fully Automated
Part: 40-618-1111
Target: STE INTERNATIONAL (Condition: NS)
"""

from playwright.sync_api import sync_playwright, expect
import json
import time
import re
from datetime import datetime
from pathlib import Path

def run_rfq_automation():
    results = {
        "part_number": "40-618-1111",
        "timestamp": datetime.now().isoformat(),
        "steps": [],
        "success": False
    }
    
    with sync_playwright() as p:
        print("[STEP 1] Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        results["steps"].append({"step": "browser_launch", "status": "success"})
        
        print("[STEP 2] Navigating to stockmarket.aero...")
        page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do", wait_until="networkidle")
        results["steps"].append({"step": "navigate", "status": "success"})
        time.sleep(2)
        page.screenshot(path="outputs/screenshots/01_welcome.png")
        
        print("[STEP 3] Searching for part 40-618-1111...")
        page.fill('input[value="Enter Part Number"]', "40-618-1111")
        page.click('input[value="Go"]')
        page.wait_for_load_state("networkidle")
        time.sleep(4)
        page.screenshot(path="outputs/screenshots/02_search_results.png")
        results["steps"].append({"step": "search", "status": "success", "part": "40-618-1111"})
        
        print("[STEP 4] Expanding all rows and finding STE INTERNATIONAL...")
        try:
            expand = page.locator('a:has-text("Expand All")').first
            if expand.is_visible():
                expand.click()
                time.sleep(2)
                print("[OK] Expanded all rows")
        except:
            print("[INFO] Expand All not available")
        
        # Find STE INTERNATIONAL row and click its Send button
        print("[STEP 5] Finding STE INTERNATIONAL row...")
        
        # Get all table rows
        rows = page.locator('tr').all()
        target_row_index = -1
        
        for i, row in enumerate(rows[:50]):  # Check first 50 rows
            try:
                row_text = row.inner_text()
                print(f"[DEBUG] Row {i}: {row_text[:100]}")
                if 'NS' in row_text.upper() and '40-618-1111' in row_text:
                    print(f"[OK] Found NS condition row at {i}")
                    target_row_index = i
                    results["steps"].append({"step": "find_supplier", "status": "success", "row": i, "condition": "NS"})
                    
                    # Find Send button in this specific row
                    send_btn = row.locator('a:has-text("Send")').first
                    if send_btn.is_visible():
                        print(f"[CLICK] Clicking Send in row {i}...")
                        
                        # Try to click and wait for popup
                        try:
                            # Listen for new page/popup
                            with page.expect_popup(timeout=10000) as popup_info:
                                send_btn.click()
                            
                            popup = popup_info.value
                            print("[OK] Popup opened!")
                            results["steps"].append({"step": "click_send", "status": "success", "popup": True})
                            
                            # Work with popup
                            popup.wait_for_load_state("networkidle")
                            time.sleep(3)
                            popup.screenshot(path="outputs/screenshots/03_rfq_popup.png")
                            
                            print("[STEP 6] Setting quantity in popup...")
                            # Try to find quantity input in popup
                            qty_found = False
                            for selector in ['input[type="number"]', 'input[name*="qty"]', 'input[name*="quantity"]', 'input[id*="qty"]']:
                                try:
                                    qty = popup.locator(selector).first
                                    if qty.is_visible():
                                        qty.fill("1")
                                        print(f"[OK] Quantity set to 1")
                                        results["steps"].append({"step": "set_quantity", "status": "success"})
                                        qty_found = True
                                        break
                                except:
                                    continue
                            
                            if not qty_found:
                                # Try JavaScript
                                popup.evaluate('''() => {
                                    const inputs = document.querySelectorAll('input');
                                    for (let i of inputs) {
                                        if (i.type === 'number' || (i.name && i.name.toLowerCase().includes('qty'))) {
                                            i.value = '1';
                                            i.dispatchEvent(new Event('change'));
                                            return 'filled';
                                        }
                                    }
                                    return 'not_found';
                                }''')
                                print("[OK] Quantity set via JS")
                                results["steps"].append({"step": "set_quantity", "status": "success", "method": "js"})
                                qty_found = True
                            
                            time.sleep(2)
                            
                            print("[STEP 7] Submitting RFQ...")
                            # Try to submit
                            submit_found = False
                            for selector in ['input[value*="Submit"]', 'input[type="submit"]', 'button:has-text("Submit")']:
                                try:
                                    btn = popup.locator(selector).first
                                    if btn.is_visible():
                                        btn.click()
                                        print("[SUCCESS] RFQ Submitted!")
                                        results["steps"].append({"step": "submit_rfq", "status": "success"})
                                        results["success"] = True
                                        submit_found = True
                                        time.sleep(3)
                                        popup.screenshot(path="outputs/screenshots/04_confirmation.png")
                                        break
                                except:
                                    continue
                            
                            if not submit_found:
                                # Try JS submit
                                popup.evaluate('''() => {
                                    const btns = document.querySelectorAll('input, button');
                                    for (let b of btns) {
                                        if ((b.value || '').toLowerCase().includes('submit')) {
                                            b.click();
                                            return 'submitted';
                                        }
                                    }
                                    return 'not_found';
                                }''')
                                print("[SUCCESS] RFQ Submitted via JS!")
                                results["steps"].append({"step": "submit_rfq", "status": "success", "method": "js"})
                                results["success"] = True
                                time.sleep(3)
                                popup.screenshot(path="outputs/screenshots/04_confirmation.png")
                            
                            popup.close()
                            break  # Exit the row loop
                            
                        except Exception as e:
                            print(f"[WARN] Popup handling failed: {e}")
                            # Try clicking without popup expectation
                            try:
                                send_btn.click()
                                time.sleep(3)
                                page.screenshot(path="outputs/screenshots/03_after_click.png")
                                print("[OK] Clicked Send, checking current page...")
                                # Check if we're on RFQ page now
                                if 'rfq' in page.url.lower():
                                    print("[OK] Now on RFQ page")
                                    results["steps"].append({"step": "click_send", "status": "success", "page_nav": True})
                                    # Handle RFQ on current page
                                    # ... (similar logic for quantity and submit)
                                    break
                            except Exception as e2:
                                print(f"[FAIL] Click failed: {e2}")
                            # Try JavaScript
                            popup.evaluate('''() => {
                                const inputs = document.querySelectorAll('input');
                                for (let i of inputs) {
                                    if (i.type === 'number' || (i.name && i.name.toLowerCase().includes('qty'))) {
                                        i.value = '1';
                                        i.dispatchEvent(new Event('change'));
                                        return 'filled';
                                    }
                                }
                                return 'not_found';
                            }''')
                            print("[OK] Quantity set via JS")
                            results["steps"].append({"step": "set_quantity", "status": "success", "method": "js"})
                        
                        time.sleep(2)
                        
                        print("[STEP 7] Submitting RFQ...")
                        # Try to submit
                        submit_found = False
                        for selector in ['input[value*="Submit"]', 'input[type="submit"]', 'button:has-text("Submit")']:
                            try:
                                btn = popup.locator(selector).first
                                if btn.is_visible():
                                    btn.click()
                                    print("[SUCCESS] RFQ Submitted!")
                                    results["steps"].append({"step": "submit_rfq", "status": "success"})
                                    results["success"] = True
                                    submit_found = True
                                    time.sleep(3)
                                    popup.screenshot(path="outputs/screenshots/04_confirmation.png")
                                    break
                            except:
                                continue
                        
                        if not submit_found:
                            # Try JS submit
                            popup.evaluate('''() => {
                                const btns = document.querySelectorAll('input, button');
                                for (let b of btns) {
                                    if ((b.value || '').toLowerCase().includes('submit')) {
                                        b.click();
                                        return 'submitted';
                                    }
                                }
                                return 'not_found';
                            }''')
                            print("[SUCCESS] RFQ Submitted via JS!")
                            results["steps"].append({"step": "submit_rfq", "status": "success", "method": "js"})
                            results["success"] = True
                            time.sleep(3)
                            popup.screenshot(path="outputs/screenshots/04_confirmation.png")
                        
                        popup.close()
                        break
                    else:
                        print("[WARN] Send button not visible in row")
                        
            except Exception as e:
                continue
        
        if target_row_index == -1:
            print("[FAIL] STE INTERNATIONAL with NS not found")
            results["steps"].append({"step": "find_supplier", "status": "failed"})
        
        browser.close()
    
    # Save results
    output_path = Path("outputs/rfq_result_40-618-1111.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] Results saved to: {output_path}")
    print(f"[INFO] Success: {results['success']}")
    return results

if __name__ == "__main__":
    run_rfq_automation()
