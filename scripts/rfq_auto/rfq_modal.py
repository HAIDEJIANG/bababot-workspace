#!/usr/bin/env python3
"""
RFQ automation with proper modal/dialog handling
"""

from playwright.sync_api import sync_playwright
import time
import json

PART_NUMBER = "S1820612-02"
QUANTITY = "1"

def run_with_modal():
    print(f"[START] RFQ for {PART_NUMBER}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()
        
        try:
            # Navigate
            print("[1] Navigating...")
            page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do")
            time.sleep(3)
            
            # Check login
            if "Login" in page.content() or "Sign In" in page.content():
                print("[WARN] Not logged in. Waiting for manual login...")
                for i in range(60):
                    time.sleep(1)
                    if "Welcome" in page.content() or "Logout" in page.content():
                        print("[OK] Logged in!")
                        break
            else:
                print("[OK] Already logged in")
            
            # Search
            print(f"[2] Searching {PART_NUMBER}...")
            page.fill('input[value="Enter Part Number"]', PART_NUMBER)
            page.click('input[value="Go"]')
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Expand
            print("[3] Expanding...")
            try:
                page.click('a:has-text("Expand All")')
                time.sleep(3)
            except:
                pass
            
            # Find NE row
            print("[4] Finding best condition...")
            rows = page.locator('tr').all()
            target_row = -1
            
            for i, row in enumerate(rows):
                text = row.inner_text()
                if PART_NUMBER in text and 'NE' in text.upper():
                    target_row = i
                    print(f"[FOUND] NE at row {i}")
                    break
            
            if target_row < 0:
                print("[FAIL] NE not found")
                return False
            
            # Click Send
            print("[5] Clicking Send...")
            send_btn = rows[target_row].locator('a:has-text("Send")').first
            send_btn.click()
            
            # Wait for modal to appear
            print("[6] Waiting for modal...")
            time.sleep(5)  # Longer wait
            
            # Take screenshot
            page.screenshot(path=f"outputs/{PART_NUMBER}_modal.png")
            print("[SCREENSHOT] Saved modal screenshot")
            
            # Debug: Get all visible elements
            debug = page.evaluate('''() => {
                const all = document.querySelectorAll('input, button, a');
                const visible = [];
                for (let el of all) {
                    if (el.offsetParent !== null) {
                        visible.push({
                            tag: el.tagName,
                            type: el.type || '',
                            value: (el.value || '').substring(0, 20),
                            text: (el.textContent || '').substring(0, 30).trim()
                        });
                    }
                }
                return visible;
            }''')
            print(f"[DEBUG] Found {len(debug)} visible elements")
            for i, el in enumerate(debug):
                print(f"[DEBUG] {i}: {el['tag']} type={el['type']} value={el['value']} text={el['text']}")
            
            # Find Submit RFQ button anywhere on page
            print("[7] Looking for Submit RFQ button...")
            
            # Check for Respond button first (may need to click it)
            respond_btns = page.locator('button:has-text("Respond")').all()
            if respond_btns:
                print(f"[INFO] Found {len(respond_btns)} Respond button(s)")
                respond_btns[0].click()
                print("[CLICK] Clicked Respond")
                time.sleep(3)
                page.screenshot(path=f"outputs/{PART_NUMBER}_after_respond.png")
                print("[SCREENSHOT] Saved after_respond")
            
            # Now look for Submit
            selectors = [
                'input[value*="Submit"]',
                'input[value="Submit RFQ"]',
                'button:has-text("Submit")',
                'button:has-text("Submit RFQ")',
                'input[type="submit"]',
                'a:has-text("Submit")'
            ]
            
            submitted = False
            for sel in selectors:
                try:
                    btns = page.locator(sel).all()
                    print(f"[DEBUG] {sel}: {len(btns)} found")
                    for btn in btns:
                        if btn.is_visible():
                            val = btn.get_attribute('value') or btn.inner_text()
                            print(f"[CLICK] Clicking: {val}")
                            btn.click()
                            submitted = True
                            break
                    if submitted:
                        break
                except Exception as e:
                    print(f"[DEBUG] {sel} error: {e}")
            
            if submitted:
                print("[SUCCESS] RFQ submitted!")
                time.sleep(3)
                page.screenshot(path=f"outputs/{PART_NUMBER}_done.png")
                
                # Verify
                print("[8] Verifying...")
                page.goto("https://www.stockmarket.aero/StockMarket/LoadPastRFQ.do?offerType=made")
                time.sleep(3)
                page.screenshot(path=f"outputs/{PART_NUMBER}_history.png")
                
                if PART_NUMBER in page.content():
                    print(f"[VERIFIED] {PART_NUMBER} in RFQ history!")
                else:
                    print(f"[WARN] {PART_NUMBER} not found in history")
                
                return True
            else:
                print("[FAIL] Submit button not found")
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            page.screenshot(path=f"outputs/{PART_NUMBER}_error.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    result = run_with_modal()
    print(f"\n[RESULT] {result}")