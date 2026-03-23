#!/usr/bin/env python3
"""
RFQ automation - Direct Submit after Send (NO Respond click)
"""

from playwright.sync_api import sync_playwright
import time

PART_NUMBER = "S1820612-02"

def run_rfq():
    print(f"[START] RFQ for {PART_NUMBER}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        try:
            # Navigate
            print("[1] Loading...")
            page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do")
            time.sleep(3)
            
            # Wait for login if needed
            if "Login" in page.content():
                print("[INFO] Waiting for login...")
                for i in range(60):
                    time.sleep(1)
                    if "Welcome" in page.content() or "Logout" in page.content():
                        break
            
            # Search
            print(f"[2] Search {PART_NUMBER}...")
            page.fill('input[value="Enter Part Number"]', PART_NUMBER)
            page.click('input[value="Go"]')
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Expand
            print("[3] Expand...")
            try:
                page.click('a:has-text("Expand All")')
                time.sleep(3)
            except:
                pass
            
            # Find NE row and click Send
            print("[4] Find NE condition...")
            rows = page.locator('tr').all()
            for i, row in enumerate(rows):
                if PART_NUMBER in row.inner_text() and 'NE' in row.inner_text().upper():
                    print(f"[FOUND] NE at row {i}")
                    row.locator('a:has-text("Send")').first.click()
                    print("[5] Clicked Send")
                    break
            
            # Wait for modal - CRITICAL STEP
            print("[6] Waiting for modal popup...")
            time.sleep(8)  # Longer wait for modal
            
            # Screenshot
            page.screenshot(path=f"outputs/{PART_NUMBER}_after_send.png")
            print("[SCREENSHOT] Saved")
            
            # Debug all visible elements
            elements = page.evaluate('''() => {
                const all = document.querySelectorAll('input, button, a, div');
                const list = [];
                for (let el of all) {
                    if (el.offsetParent !== null && el.offsetWidth > 0 && el.offsetHeight > 0) {
                        const text = (el.textContent || '').trim().substring(0, 50);
                        const value = (el.value || '').substring(0, 30);
                        if (text || value) {
                            list.push({tag: el.tagName, text, value, type: el.type || ''});
                        }
                    }
                }
                return list;
            }''')
            print(f"[DEBUG] Visible elements: {len(elements)}")
            for i, el in enumerate(elements):
                print(f"[{i}] {el['tag']} text='{el['text'][:40]}' value='{el['value']}'")
            
            # Find and click Submit RFQ - DO NOT CLICK RESPOND
            print("[7] Looking for Submit RFQ...")
            
            # Try specific selectors for Submit RFQ button
            try:
                # Look for button with Submit RFQ text
                btn = page.get_by_role('button', name='Submit RFQ')
                if btn.is_visible():
                    print("[CLICK] Clicking Submit RFQ button")
                    btn.click()
                    time.sleep(5)
                    page.screenshot(path=f"outputs/{PART_NUMBER}_submitted.png")
                    print("[SUCCESS] Done!")
                    return True
            except:
                pass
            
            # Try input with Submit value
            try:
                btn = page.locator('input[value="Submit RFQ"]').first
                if btn.is_visible():
                    print("[CLICK] Clicking Submit RFQ input")
                    btn.click()
                    time.sleep(5)
                    page.screenshot(path=f"outputs/{PART_NUMBER}_submitted.png")
                    print("[SUCCESS] Done!")
                    return True
            except:
                pass
            
            # Try any submit button
            try:
                btns = page.locator('button[type="submit"], input[type="submit"]').all()
                print(f"[DEBUG] Submit buttons: {len(btns)}")
                if btns:
                    btns[0].click()
                    print("[CLICK] Clicked submit")
                    time.sleep(5)
                    page.screenshot(path=f"outputs/{PART_NUMBER}_submitted.png")
                    return True
            except:
                pass
            
            print("[FAIL] Submit RFQ button not found")
            return False
            
        except Exception as e:
            print(f"[ERROR] {e}")
            page.screenshot(path=f"outputs/{PART_NUMBER}_error.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    run_rfq()