"""
RFQ Auto-Submit Script using Playwright - Simplified Version
Part: 40-618-1111
Target: STE INTERNATIONAL (Condition: NS)
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
        print("[STEP 1] Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        results["steps"].append({"step": "browser_launch", "status": "success"})
        
        print("[STEP 2] Navigating to stockmarket.aero...")
        page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do", wait_until="networkidle")
        results["steps"].append({"step": "navigate", "status": "success"})
        
        time.sleep(3)
        page.screenshot(path="outputs/screenshots/01_welcome.png")
        
        print("[STEP 3] Searching for part 40-618-1111...")
        page.fill('input[value="Enter Part Number"]', "40-618-1111")
        page.click('input[value="Go"]')
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        page.screenshot(path="outputs/screenshots/02_search_results.png")
        results["steps"].append({"step": "search", "status": "success", "part": "40-618-1111"})
        
        print("[STEP 4] Finding STE INTERNATIONAL with NS condition...")
        
        # Try to click Expand All first to show all details
        print("[INFO] Attempting to expand all rows...")
        try:
            expand_link = page.locator('a:has-text("Expand All"), a:has-text("expand")').first
            if expand_link.is_visible():
                expand_link.click()
                print("[OK] Expanded all rows")
                time.sleep(2)
            else:
                print("[INFO] Expand All not found or already expanded")
        except Exception as e:
            print(f"[WARN] Expand failed: {e}")
        
        page_content = page.content().upper()
        
        if "STE INTERNATIONAL" in page_content and "NS" in page_content:
            print("[OK] Found STE INTERNATIONAL with NS condition")
            results["steps"].append({"step": "find_supplier", "status": "success", "supplier": "STE INTERNATIONAL", "condition": "NS"})
            
            # Click first Send button (simplified approach)
            print("[STEP 5] Clicking Send RFQ...")
            try:
                # Find Send link and scroll into view
                send_link = page.locator('a:has-text("Send")').first
                send_link.scroll_into_view_if_needed()
                time.sleep(1)
                # Use JavaScript to click (more reliable)
                page.evaluate('element => element.click()', send_link.element_handle())
                print("[OK] Send button clicked")
                results["steps"].append({"step": "click_send", "status": "success"})
                
                # Wait for popup/dialog to appear
                print("[INFO] Waiting for RFQ form popup...")
                time.sleep(3)
                
                # Handle popup - Playwright may need to wait for dialog
                try:
                    # Wait for any dialog/popup
                    page.wait_for_selector('div[role="dialog"], .modal, .popup, iframe', timeout=5000)
                    print("[OK] Popup detected")
                except:
                    print("[INFO] No standard popup, checking page content...")
                
                # Take screenshot
                page.screenshot(path="outputs/screenshots/03_rfq_form.png")
                
                # Debug: Get all element info
                print("[DEBUG] Scanning page for form elements...")
                debug_info = page.evaluate('''() => {
                    const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
                        type: i.type,
                        name: i.name,
                        id: i.id,
                        class: i.className,
                        value: i.value,
                        placeholder: i.placeholder
                    })).filter(i => i.type || i.name || i.id);
                    
                    const allButtons = Array.from(document.querySelectorAll('button, input[type="submit"], a'));
                    const submitButtons = allButtons.filter(b => {
                        const text = (b.textContent || b.value || '').toLowerCase();
                        return text.includes('submit') || text.includes('send');
                    }).map(b => ({
                        tag: b.tagName,
                        text: b.textContent?.trim().substring(0, 50),
                        value: b.value,
                        type: b.type,
                        href: b.href
                    }));
                    
                    const dialogs = Array.from(document.querySelectorAll('div[role="dialog"], .modal, .popup')).map(d => d.id || d.className);
                    
                    return { inputs: inputs.slice(0, 20), buttons: submitButtons.slice(0, 20), dialogs };
                }''')
                
                print(f"[DEBUG] Found {len(debug_info['inputs'])} inputs, {len(debug_info['buttons'])} buttons, {len(debug_info['dialogs'])} dialogs")
                if debug_info['inputs']:
                    print(f"[DEBUG] Sample inputs: {debug_info['inputs'][:3]}")
                if debug_info['buttons']:
                    print(f"[DEBUG] Sample buttons: {debug_info['buttons'][:3]}")
                
                # Save debug info
                with open('outputs/debug_form_info.json', 'w', encoding='utf-8') as f:
                    json.dump(debug_info, f, indent=2, ensure_ascii=False)
                print("[INFO] Debug info saved to outputs/debug_form_info.json")
                
                # Check current URL
                current_url = page.url
                print(f"[INFO] Current URL: {current_url}")
                
                # Look for RFQ form in main page
                page_content = page.content().lower()
                if "rfq" in page_content or "quantity" in page_content:
                    print("[OK] RFQ form detected in main page")
                else:
                    print("[INFO] Checking for iframes...")
                    # Check for iframes
                    frames = page.frames
                    print(f"[DATA] Found {len(frames)} frames")
                    for i, frame in enumerate(frames):
                        try:
                            frame_content = frame.content().lower()
                            if "quantity" in frame_content or "rfq" in frame_content:
                                print(f"[OK] RFQ form found in frame {i}")
                                page = frame  # Switch to this frame
                                break
                        except:
                            continue
                
                time.sleep(2)
                
                # Set quantity to 1
                print("[STEP 6] Setting quantity to 1...")
                qty_set = False
                # Try many different selectors
                qty_selectors = [
                    'input[type="number"]',
                    'input[name*="qty" i]',
                    'input[name*="quantity" i]',
                    'input[id*="qty" i]',
                    'input[id*="quantity" i]',
                    'input[placeholder*="qty" i]',
                    'input[placeholder*="quantity" i]',
                    'input[name="qty"]',
                    'input[name="quantity"]',
                    'input[class*="qty"]',
                    'input[class*="quantity"]',
                    'input[data-testid*="qty"]',
                    '//input[contains(@name, "qty")]',
                    '//input[contains(@id, "qty")]',
                    '//input[contains(@class, "qty")]',
                ]
                
                for selector in qty_selectors:
                    try:
                        if selector.startswith('//'):
                            qty_input = page.locator(f'xpath={selector}').first
                        else:
                            qty_input = page.locator(selector).first
                        
                        if qty_input.is_visible():
                            qty_input.fill("1")
                            print(f"[OK] Quantity set using: {selector[:50]}")
                            results["steps"].append({"step": "set_quantity", "status": "success", "value": "1", "selector": selector[:50]})
                            qty_set = True
                            break
                    except Exception as e:
                        continue
                
                if not qty_set:
                    print("[WARN] Quantity input not found, trying JavaScript...")
                    # Try JavaScript to find and fill quantity
                    try:
                        result = page.evaluate('''() => {
                            const inputs = document.querySelectorAll('input');
                            for (let input of inputs) {
                                if (input.type === 'number' || 
                                    (input.name && input.name.toLowerCase().includes('qty')) ||
                                    (input.id && input.id.toLowerCase().includes('qty'))) {
                                    input.value = '1';
                                    input.dispatchEvent(new Event('input', { bubbles: true }));
                                    input.dispatchEvent(new Event('change', { bubbles: true }));
                                    return 'filled:' + input.name;
                                }
                            }
                            return 'not_found';
                        }''')
                        if result.startswith('filled'):
                            print(f"[OK] Quantity set via JavaScript: {result}")
                            results["steps"].append({"step": "set_quantity", "status": "success", "value": "1", "method": "javascript"})
                            qty_set = True
                    except Exception as e:
                        print(f"[WARN] JavaScript fill failed: {e}")
                
                if not qty_set:
                    results["steps"].append({"step": "set_quantity", "status": "failed", "error": "No input found"})
                
                time.sleep(2)
                page.screenshot(path="outputs/screenshots/03b_after_quantity.png")
                
                # Submit RFQ
                print("[STEP 7] Submitting RFQ...")
                submit_success = False
                submit_selectors = [
                    'input[value*="Submit" i]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Submit RFQ")',
                    'a:has-text("Submit")',
                    'input[value="Submit"]',
                    'input[name*="submit" i]',
                    'button[type="submit"]',
                    '//input[contains(@value, "Submit")]',
                    '//button[contains(text(), "Submit")]',
                    '//a[contains(text(), "Submit")]',
                ]
                
                for selector in submit_selectors:
                    try:
                        if selector.startswith('//'):
                            submit_btn = page.locator(f'xpath={selector}').first
                        else:
                            submit_btn = page.locator(selector).first
                        
                        if submit_btn.is_visible():
                            submit_btn.scroll_into_view_if_needed()
                            time.sleep(1)
                            submit_btn.click()
                            print(f"[SUCCESS] RFQ submitted using: {selector[:50]}")
                            results["steps"].append({"step": "submit_rfq", "status": "success", "selector": selector[:50]})
                            results["success"] = True
                            submit_success = True
                            time.sleep(3)
                            page.screenshot(path="outputs/screenshots/04_confirmation.png")
                            break
                    except Exception as e:
                        continue
                
                if not submit_success:
                    print("[WARN] Submit button not found, trying JavaScript...")
                    try:
                        result = page.evaluate('''() => {
                            const buttons = document.querySelectorAll('input, button, a');
                            for (let btn of buttons) {
                                const text = (btn.value || btn.textContent || '').toLowerCase();
                                if (text.includes('submit')) {
                                    btn.click();
                                    return 'clicked:' + text;
                                }
                            }
                            return 'not_found';
                        }''')
                        if result.startswith('clicked'):
                            print(f"[SUCCESS] RFQ submitted via JavaScript: {result}")
                            results["steps"].append({"step": "submit_rfq", "status": "success", "method": "javascript"})
                            results["success"] = True
                            submit_success = True
                            time.sleep(3)
                            page.screenshot(path="outputs/screenshots/04_confirmation.png")
                    except Exception as e:
                        print(f"[FAIL] JavaScript submit failed: {e}")
                
                if not submit_success:
                    results["steps"].append({"step": "submit_rfq", "status": "failed", "error": "No button found"})
                    
            except Exception as e:
                print(f"[FAIL] Click Send failed: {str(e)}")
                results["steps"].append({"step": "click_send", "status": "failed", "error": str(e)})
        else:
            print("[FAIL] STE INTERNATIONAL with NS not found")
            results["steps"].append({"step": "find_supplier", "status": "failed", "error": "Supplier not found"})
        
        try:
            browser.close()
        except:
            pass
        
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
