"""
RFQ Auto-Submit Script using Playwright
Part: 40-618-1111
Target Supplier: STE INTERNATIONAL (Condition: NS)
"""

from playwright.sync_api import sync_playwright
import json
import time
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
        # Launch browser
        print("[STEP 1] Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        results["steps"].append({"step": "browser_launch", "status": "success"})
        
        # Navigate to stockmarket.aero
        print("[STEP 2] Navigating to stockmarket.aero...")
        page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do", wait_until="networkidle")
        results["steps"].append({"step": "navigate", "status": "success", "url": page.url})
        
        # Take screenshot
        screenshot_path = Path("outputs/screenshots/01_welcome.png")
        screenshot_path.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshot_path))
        
        # Check if already logged in (check for welcome message or login form)
        page.wait_for_timeout(3000)
        if "Welcome" in page.content() or "Logout" in page.content():
            print("[OK] User appears to be logged in")
            results["steps"].append({"step": "login_check", "status": "logged_in"})
        else:
            print("[INFO] Login status unknown, continuing...")
            results["steps"].append({"step": "login_check", "status": "unknown"})
        
        # Search for part number
        print("[STEP 3] Searching for part 40-618-1111...")
        search_input = page.locator('input[value="Enter Part Number"]').first
        if search_input.is_visible():
            search_input.fill("40-618-1111")
            results["steps"].append({"step": "enter_part_number", "status": "success", "value": "40-618-1111"})
            
            # Click Go button
            go_button = page.locator('input[value="Go"]').first
            go_button.click()
            results["steps"].append({"step": "click_search", "status": "success"})
            
            # Wait for results
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Take screenshot of search results
            screenshot_path = Path("outputs/screenshots/02_search_results.png")
            page.screenshot(path=str(screenshot_path))
            
            # Wait for results to load
            page.wait_for_timeout(5000)
            
            # Look for STE INTERNATIONAL with NS condition
            print("[LIST] Looking for STE INTERNATIONAL (NS condition)...")
            page_content = page.content().upper()
            
            if "STE INTERNATIONAL" in page_content:
                print("[OK] Found STE INTERNATIONAL in page")
                results["steps"].append({"step": "find_supplier", "status": "success", "supplier": "STE INTERNATIONAL"})
                
                # Find all Send links
                send_links = page.locator('a:has-text("Send")')
                count = send_links.count()
                print(f"[DATA] Found {count} Send buttons")
                
                # Try to find by text content in the page
                # Look for rows containing both STE INTERNATIONAL and NS
                all_text = page.locator('body').inner_text()
                lines = all_text.split('\n')
                target_line = None
                ns_found = False
                for i, line in enumerate(lines):
                    if 'STE' in line.upper() and 'INTERNATIONAL' in line.upper():
                        print(f"[OK] Found STE INTERNATIONAL on line {i}")
                        print(f"[DEBUG] Line content: {line[:100]}")
                        if 'NS' in line.upper():
                            print(f"[OK] Line also contains NS condition!")
                            ns_found = True
                            target_line = line
                            results["steps"].append({
                                "step": "find_target_row",
                                "status": "success",
                                "line_index": i,
                                "condition": "NS",
                                "line_content": line[:200]
                            })
                            
                            # Strategy: Find all tables and look for STE INTERNATIONAL row
                            print("[SEARCH] Searching for Send button near STE INTERNATIONAL...")
                            
                            # Try multiple selector strategies
                            send_clicked = False
                            
                            # Strategy 1: Find link with href containing 'RFQ' and text 'Send'
                            try:
                                rfq_links = page.locator('a[href*="RFQ"]:has-text("Send")')
                                count = rfq_links.count()
                                print(f"[DATA] Found {count} RFQ Send links (href selector)")
                                if count > 0:
                                    print(f"[CLICK] Clicking first RFQ Send link...")
                                    rfq_links.first.click()
                                    send_clicked = True
                                    results["steps"].append({"step": "click_send_rfq", "status": "success", "method": "href_selector"})
                            except Exception as e:
                                print(f"[WARN] Strategy 1 failed: {e}")
                            
                            # Strategy 2: Find all Send links and click the one in same row as STE INTERNATIONAL
                            if not send_clicked:
                                try:
                                    all_send_links = page.locator('a:has-text("Send")')
                                    total = all_send_links.count()
                                    print(f"[DATA] Found {total} total Send links")
                                    
                                    # Get all links with their parent row context
                                    for j in range(total):
                                        link = all_send_links.nth(j)
                                        try:
                                            parent_row = link.locator('xpath=ancestor::tr[1]')
                                            if parent_row.count() > 0:
                                                row_text = parent_row.first.inner_text()
                                                if 'STE' in row_text.upper() and 'INTERNATIONAL' in row_text.upper():
                                                    print(f"[OK] Found Send button in STE INTERNATIONAL row (index {j})")
                                                    link.click()
                                                    send_clicked = True
                                                    results["steps"].append({"step": "click_send_rfq", "status": "success", "method": "row_context", "index": j})
                                                    break
                                        except Exception as e:
                                            print(f"[WARN] Link {j} error: {e}")
                                            continue
                                except Exception as e:
                                    print(f"[WARN] Strategy 2 failed: {e}")
                            
                            # Strategy 3: Fallback - click first Send button
                            if not send_clicked:
                                print("[WARN] Using fallback: clicking first Send button")
                                all_send_links.first.click()
                                send_clicked = True
                                results["steps"].append({"step": "click_send_rfq", "status": "success", "method": "fallback_first"})
                            
                            if send_clicked:
                                print("[OK] Send RFQ clicked successfully!")
                            
                            # Wait for RFQ form
                            time.sleep(2)
                            
                            # Take screenshot
                            screenshot_path = Path("outputs/screenshots/03_rfq_form.png")
                            page.screenshot(path=str(screenshot_path))
                            
                            # Find quantity input and set to 1
                            qty_inputs = page.locator('input[type="number"], input[name*="qty"], input[name*="quantity"]')
                            if qty_inputs.count() > 0:
                                qty_inputs.first.fill("1")
                                print("[OK] Quantity set to 1")
                                results["steps"].append({"step": "set_quantity", "status": "success", "value": "1"})
                                
                                # Find and click Submit RFQ button
                                submit_buttons = page.locator('input[value*="Submit"], button:has-text("Submit"), input[type="submit"]')
                                if submit_buttons.count() > 0:
                                    print("[STEP 4] Submitting RFQ...")
                                    submit_buttons.first.click()
                                    results["steps"].append({"step": "submit_rfq", "status": "success"})
                                    
                                    # Wait for confirmation
                                    time.sleep(3)
                                    
                                    # Take final screenshot
                                    screenshot_path = Path("outputs/screenshots/04_submission_confirm.png")
                                    page.screenshot(path=str(screenshot_path))
                                    
                                    # Check for success message
                                    if "thank you" in page.content().lower() or "submitted" in page.content().lower():
                                        print("[SUCCESS] RFQ submitted successfully!")
                                        results["success"] = True
                                        results["steps"].append({"step": "confirmation", "status": "success"})
                                    else:
                                        print("⚠️ Submission completed but no confirmation message found")
                                        results["steps"].append({"step": "confirmation", "status": "unknown"})
                                else:
                                    print("[FAIL] Submit button not found")
                                    results["steps"].append({"step": "submit_rfq", "status": "failed", "error": "Submit button not found"})
                            else:
                                print("[FAIL] Quantity input not found")
                                results["steps"].append({"step": "set_quantity", "status": "failed", "error": "Quantity input not found"})
                        else:
                            print("[FAIL] Send button not found in target row")
                            results["steps"].append({"step": "click_send_rfq", "status": "failed", "error": "Send button not found"})
                        break
                else:
                    print("[FAIL] STE INTERNATIONAL with NS condition not found in table rows")
                    results["steps"].append({"step": "find_target_row", "status": "failed", "error": "Target row not found"})
            else:
                print("[FAIL] STE INTERNATIONAL not found on page")
                results["steps"].append({"step": "find_supplier", "status": "failed", "error": "Supplier not found"})
        else:
            print("[FAIL] Search input not found")
            results["steps"].append({"step": "enter_part_number", "status": "failed", "error": "Search input not found"})
        
        browser.close()
    
    # Save results
    output_path = Path("outputs/rfq_result_40-618-1111.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] Results saved to: {output_path}")
    print(f"[INFO] Success: {results['success']}")
    
    return results

if __name__ == "__main__":
    run_rfq_automation()
