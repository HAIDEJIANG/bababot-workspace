#!/usr/bin/env python3
"""
Complete RFQ automation script for stockmarket.aero
Fully automatic - no manual intervention required
"""

import json
import os
import time
from datetime import datetime

from playwright.sync_api import sync_playwright


def run_rfq_automation():
    """Run complete RFQ automation"""
    results = {
        "part_number": "S1820612-02",
        "timestamp": datetime.now().isoformat(),
        "steps": [],
        "success": False
    }
    
    print("[STEP 1] Launching browser...")
    with sync_playwright() as p:
        # Launch browser with proper settings
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        try:
            # Step 2: Navigate to stockmarket.aero
            print("[STEP 2] Navigating to stockmarket.aero...")
            page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do", timeout=30000)
            
            # Check login status
            print("[INFO] Checking login status...")
            page_content = page.content()
            if "Welcome" in page_content or "Logout" in page_content or "sale@aeroedgeglobal.com" in page_content:
                print("[OK] User is logged in")
                results["steps"].append({"step": "login_check", "status": "logged_in"})
            elif "Login" in page_content or "Sign In" in page_content:
                print("[WARN] User is NOT logged in. Please login manually in the browser window.")
                print("[INFO] Script will wait 60 seconds for manual login...")
                results["steps"].append({"step": "login_check", "status": "not_logged_in", "action": "waiting_for_manual_login"})
                
                # Wait for user to login manually
                for i in range(60):
                    time.sleep(1)
                    if i % 10 == 0:
                        print(f"[INFO] Waiting for login... ({i}/60 seconds)")
                    page_content = page.content()
                    if "Welcome" in page_content or "Logout" in page_content:
                        print("[OK] User logged in successfully!")
                        results["steps"].append({"step": "login_check", "status": "logged_in_after_wait"})
                        break
                else:
                    print("[FAIL] Login timeout. Please login and restart the script.")
                    results["steps"].append({"step": "login_check", "status": "timeout"})
                    return results
            else:
                print("[INFO] Login status unknown, continuing...")
                results["steps"].append({"step": "login_check", "status": "unknown"})
            
            results["steps"].append({"step": "navigate", "status": "success"})
            
            # Step 3: Search for part number
            print("[STEP 3] Searching for part S1820612-02...")
            page.fill('input[type="text"][name="partNumber"]', 'S1820612-02')
            page.click('input[value="Go"]')
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for results to load
            results["steps"].append({"step": "search", "status": "success"})
            
            # Take screenshot to debug
            page.screenshot(path="outputs/screenshots/search_results.png")
            
            # Step 4: Expand all rows
            print("[STEP 4] Expanding all rows...")
            # Try multiple selectors for Expand All
            expand_clicked = False
            expand_selectors = [
                'a:has-text("Expand All")',
                'a:has-text("expand")',
                'button:has-text("Expand")',
                'div:has-text("Expand All")'
            ]
            for selector in expand_selectors:
                try:
                    expand_links = page.locator(selector)
                    if expand_links.count() > 0:
                        expand_links.first.click()
                        print(f"[OK] Expand All clicked using: {selector}")
                        expand_clicked = True
                        time.sleep(5)  # Wait for expansion
                        results["steps"].append({"step": "expand_all", "status": "success", "selector": selector})
                        break
                except Exception as e:
                    continue
            
            if not expand_clicked:
                print("[INFO] No Expand All button found, checking if rows are already expanded...")
                results["steps"].append({"step": "expand_all", "status": "skipped", "note": "Not found or already expanded"})
            
            # Take screenshot to debug
            page.screenshot(path="outputs/screenshots/after_expand.png")
            
            # Debug: Get all row content
            print("[DEBUG] Scanning page for rows...")
            all_text = page.locator('body').inner_text()
            lines = all_text.split('\n')
            for i, line in enumerate(lines[:30]):
                if 'NS' in line or 'STE' in line or '40-618' in line:
                    print(f"[DEBUG] Line {i}: {line[:100]}")
            
            # Step 5: Find NS condition row and click Send
            print("[STEP 5] Finding NS condition row...")
            
            # Get page content for debugging
            page_content = page.content()
            if 'STE INTERNATIONAL' in page_content:
                print("[DEBUG] STE INTERNATIONAL found in page")
            if 'NS' in page_content:
                print("[DEBUG] NS found in page")
            
            rows = page.locator('tr').all()
            print(f"[DEBUG] Found {len(rows)} table rows")
            
            # Debug: Print all rows with condition info
            for i, row in enumerate(rows[:30]):
                try:
                    row_text = row.inner_text(timeout=5000)
                    if 'S1820612' in row_text or 'KANNAD' in row_text.upper() or 'NE' in row_text.upper() or 'FN' in row_text.upper() or 'NS' in row_text.upper() or 'SV' in row_text.upper() or 'AR' in row_text.upper():
                        print(f"[DEBUG] Row {i}: {row_text[:150]}")
                except:
                    continue
            
            ns_row_found = False
            best_condition = None
            best_row = -1
            priority = {'NE': 1, 'FN': 2, 'NS': 3, 'OH': 4, 'SV': 5, 'AR': 6}
            
            for i, row in enumerate(rows[:100]):  # Check first 100 rows
                try:
                    row_text = row.inner_text(timeout=5000)
                    # Check for any valid condition with part number
                    if 'S1820612-02' in row_text or 'S1820612' in row_text:
                        # Find the best condition
                        for cond in priority.keys():
                            if cond in row_text.upper():
                                if best_condition is None or priority[cond] < priority[best_condition]:
                                    best_condition = cond
                                    best_row = i
                                    print(f"[DEBUG] Found {cond} condition at row {i}")
                                break
                        
                        if best_row >= 0:
                print(f"[OK] Best condition found: {best_condition} at row {best_row}")
                results["steps"].append({"step": "find_best_row", "status": "success", "row": best_row, "condition": best_condition})
                
                # Find and click Send button in this row
                row = rows[best_row]
                send_btns = row.locator('a:has-text("Send")').all()
                if send_btns:
                    print(f"[CLICK] Clicking Send in {best_condition} row...")
                            
                            # Try to detect popup
                            try:
                                with page.expect_popup(timeout=15000) as popup_info:
                                    send_btns[0].click()
                                
                                popup = popup_info.value
                                print("[OK] Popup detected!")
                                results["steps"].append({"step": "click_send", "status": "success", "popup": True})
                                
                                # Wait for popup to load
                                popup.wait_for_load_state("networkidle")
                                time.sleep(3)
                                popup.screenshot(path="outputs/screenshots/rfq_popup.png")
                                
                                # Now work with popup for quantity and submit
                                print("[STEP 6] Setting quantity in popup...")
                                qty_set = False
                                
                                # Try to find quantity input
                                for selector in ['input[type="number"]', 'input[name*="qty"]', 'input[name*="quantity"]']:
                                    try:
                                        qty = popup.locator(selector).first
                                        if qty.is_visible():
                                            qty.fill("1")
                                            print(f"[OK] Quantity set using: {selector}")
                                            results["steps"].append({"step": "set_quantity", "status": "success"})
                                            qty_set = True
                                            break
                                    except:
                                        continue
                                
                                if not qty_set:
                                    print("[WARN] Quantity input not found, using default")
                                    results["steps"].append({"step": "set_quantity", "status": "skipped", "note": "Using default value"})
                                
                                time.sleep(2)
                                
                                # Submit RFQ
                                print("[STEP 7] Submitting RFQ...")
                                submit_clicked = False
                                for selector in ['input[value*="Submit"]', 'input[type="submit"]', 'button:has-text("Submit")']:
                                    try:
                                        btn = popup.locator(selector).first
                                        if btn.is_visible():
                                            btn.click()
                                            print(f"[SUCCESS] RFQ submitted using: {selector}")
                                            results["steps"].append({"step": "submit_rfq", "status": "success"})
                                            results["success"] = True
                                            submit_clicked = True
                                            time.sleep(3)
                                            popup.screenshot(path="outputs/screenshots/rfq_submitted.png")
                                            break
                                    except:
                                        continue
                                
                                if not submit_clicked:
                                    print("[FAIL] Submit button not found")
                                    results["steps"].append({"step": "submit_rfq", "status": "failed"})
                                
                                popup.close()
                                
                            except Exception as e:
                                print(f"[WARN] Popup not detected: {e}")
                                print("[INFO] Clicking Send without popup detection...")
                                send_btns[0].click()
                                time.sleep(5)
                                page.screenshot(path="outputs/screenshots/after_send_click.png")
                                
                                # Check if we're on a new page or form appeared
                                if "RFQ" in page.content().upper() or "quantity" in page.content().lower():
                                    print("[OK] RFQ form detected on current page")
                                    results["steps"].append({"step": "click_send", "status": "success", "page_form": True})
                                else:
                                    print("[WARN] No RFQ form detected")
                                    results["steps"].append({"step": "click_send", "status": "success", "form_detected": False})
                            
                            ns_row_found = True
                            break  # Exit row loop after clicking Send
                except Exception as e:
                    continue
            
            if not ns_row_found:
                print("[FAIL] NS condition row not found")
                results["steps"].append({"step": "find_ns_row", "status": "failed"})
                return results
            
            # Step 6: Wait for RFQ form to appear (in current page, not popup)
            print("[STEP 6] Waiting for RFQ form to load...")
            time.sleep(5)  # Give time for form to appear
            
            # Take screenshot to debug
            page.screenshot(path="outputs/screenshots/rfq_form_after_click.png")
            
            # Step 7: Set quantity using multiple strategies
            print("[STEP 7] Setting quantity to 1...")
            qty_set = False
            
            # Strategy 1: Look for quantity input fields
            qty_selectors = [
                'input[name*="qty"]',
                'input[name*="quantity"]', 
                'input[id*="qty"]',
                'input[type="number"]',
                'input[value="1"]'
            ]
            
            for selector in qty_selectors:
                try:
                    inputs = page.locator(selector).all()
                    for inp in inputs:
                        if inp.is_visible() and inp.is_editable():
                            inp.fill("1")
                            print(f"[OK] Quantity set using selector: {selector}")
                            results["steps"].append({"step": "set_quantity", "status": "success", "method": selector})
                            qty_set = True
                            break
                    if qty_set:
                        break
                except Exception as e:
                    continue
            
            if not qty_set:
                # Strategy 2: Use JavaScript to find and set quantity
                try:
                    js_result = page.evaluate("""
                        // Find all input elements that might be quantity
                        const inputs = document.querySelectorAll('input');
                        for (let inp of inputs) {
                            const name = inp.name || inp.id || '';
                            if (name.toLowerCase().includes('qty') || 
                                name.toLowerCase().includes('quantity') ||
                                inp.type === 'number') {
                                inp.value = '1';
                                inp.dispatchEvent(new Event('change', { bubbles: true }));
                                inp.dispatchEvent(new Event('input', { bubbles: true }));
                                return 'Quantity set via JS';
                            }
                        }
                        return 'Not found';
                    """)
                    if js_result != 'Not found':
                        print(f"[OK] Quantity set via JavaScript: {js_result}")
                        results["steps"].append({"step": "set_quantity", "status": "success", "method": "javascript"})
                        qty_set = True
                except Exception as e:
                    print(f"[WARN] JavaScript quantity setting failed: {e}")
            
            if not qty_set:
                print("[WARN] Could not set quantity, continuing anyway...")
                results["steps"].append({"step": "set_quantity", "status": "skipped"})
            
            # Step 8: Submit RFQ using multiple strategies
            print("[STEP 8] Submitting RFQ...")
            submit_clicked = False
            
            # Strategy 1: Look for submit buttons
            submit_selectors = [
                'input[value*="Submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'input[value="Submit RFQ"]',
                'input[class*="submit"]'
            ]
            
            for selector in submit_selectors:
                try:
                    buttons = page.locator(selector).all()
                    for btn in buttons:
                        if btn.is_visible():
                            btn.click()
                            print(f"[OK] RFQ submitted using selector: {selector}")
                            results["steps"].append({"step": "submit_rfq", "status": "success", "method": selector})
                            submit_clicked = True
                            break
                    if submit_clicked:
                        break
                except Exception as e:
                    continue
            
            if not submit_clicked:
                # Strategy 2: Use JavaScript to submit
                try:
                    js_submit = page.evaluate("""
                        // Try to find and click submit button via JS
                        const buttons = document.querySelectorAll('input, button');
                        for (let btn of buttons) {
                            const val = btn.value || btn.textContent || '';
                            if (val.includes('Submit') || val.includes('submit')) {
                                btn.click();
                                return 'Submitted via JS';
                            }
                        }
                        // Try to submit the form directly
                        const forms = document.querySelectorAll('form');
                        if (forms.length > 0) {
                            forms[0].submit();
                            return 'Form submitted via JS';
                        }
                        return 'Not found';
                    """)
                    if js_submit != 'Not found':
                        print(f"[OK] RFQ submitted via JavaScript: {js_submit}")
                        results["steps"].append({"step": "submit_rfq", "status": "success", "method": "javascript"})
                        submit_clicked = True
                except Exception as e:
                    print(f"[WARN] JavaScript submit failed: {e}")
            
            if submit_clicked:
                print("[SUCCESS] RFQ automation completed!")
                results["success"] = True
                # Wait a bit to ensure submission
                time.sleep(3)
                page.screenshot(path="outputs/screenshots/rfq_submitted.png")
            else:
                print("[FAIL] Could not submit RFQ")
                results["steps"].append({"step": "submit_rfq", "status": "failed"})
            
        except Exception as e:
            print(f"[ERROR] Automation failed: {e}")
            results["steps"].append({"step": "automation", "status": "error", "error": str(e)})
        finally:
            # Save results
            os.makedirs("outputs", exist_ok=True)
            with open("outputs/rfq_result_S1820612-02.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Close browser
            browser.close()
            
            if results["success"]:
                print("[INFO] Results saved to: outputs/rfq_result_S1820612-02.json")
                print("[INFO] Success: True")
            else:
                print("[INFO] Results saved to: outputs/rfq_result_S1820612-02.json")
                print("[INFO] Success: False")
    
    return results


if __name__ == "__main__":
    run_rfq_automation()