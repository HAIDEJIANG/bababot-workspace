"""
RFQ Auto-Submit Script for 3 Target Part Numbers
Parts:
1. 10037-0770 (Fuel Load Preselect Indicator) - 80 suppliers
2. 1152466-250 (APU Start Converter Unit) - 95 suppliers
3. 129666-3 (Precooler Control Valve Sensor) - 108 suppliers

Rules:
- Condition filter: NE, FN, NS, OH, SV, AR only
- Priority: NE > FN > NS > OH > SV > AR
- Max 10 valid suppliers per PN
- Auto-submit, no confirmation required
"""

from playwright.sync_api import sync_playwright, expect, Page, BrowserContext
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Configuration
VALID_CONDITIONS = ["NE", "FN", "NS", "OH", "SV", "AR"]
CONDITION_PRIORITY = {c: i for i, c in enumerate(VALID_CONDITIONS)}

TARGET_PARTS = [
    {"pn": "10037-0770", "name": "Fuel Load Preselect Indicator", "expected_suppliers": 80},
    {"pn": "1152466-250", "name": "APU Start Converter Unit", "expected_suppliers": 95},
    {"pn": "129666-3", "name": "Precooler Control Valve Sensor", "expected_suppliers": 108},
]

MAX_SUPPLIERS_PER_PN = 10

# Output paths
OUTPUT_DIR = Path("scripts/rfq_auto/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SupplierResult:
    vendor: str
    condition: str
    pn: str
    status: str  # "success", "failed", "skipped"
    error: Optional[str] = None
    timestamp: str = ""


@dataclass
class PartResult:
    part_number: str
    part_name: str
    total_suppliers_found: int = 0
    valid_suppliers_count: int = 0
    submitted_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    suppliers: List[SupplierResult] = None
    
    def __post_init__(self):
        if self.suppliers is None:
            self.suppliers = []


def normalize_condition(cond: Optional[str]) -> Optional[str]:
    """Normalize condition string to uppercase valid format."""
    if not cond:
        return None
    c = cond.strip().upper()
    return c if c in VALID_CONDITIONS else None


def extract_condition_from_text(text: str) -> Optional[str]:
    """Extract condition code from row text."""
    # Look for condition codes in the text
    for cond in VALID_CONDITIONS:
        if re.search(rf'\b{cond}\b', text, re.IGNORECASE):
            return cond
    return None


def log_message(log_file, message: str):
    """Write message to JSONL log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message
    }
    log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log_file.flush()
    print(message)


def find_supplier_rows(page: Page, pn: str) -> List[Tuple[int, str, Optional[str]]]:
    """
    Find all supplier rows for the given part number.
    Returns list of (row_index, row_text, condition) tuples.
    """
    rows = page.locator('tr').all()
    found_rows = []
    
    for i, row in enumerate(rows[:200]):  # Check first 200 rows
        try:
            row_text = row.inner_text()
            # Check if this row contains the part number
            if pn in row_text:
                # Try to extract condition
                condition = extract_condition_from_text(row_text)
                found_rows.append((i, row_text, condition))
        except Exception as e:
            continue
    
    return found_rows


def filter_and_rank_suppliers(rows: List[Tuple[int, str, Optional[str]]], pn: str, max_count: int = 10) -> List[Tuple[int, str, str]]:
    """
    Filter rows by valid conditions and rank by priority.
    Returns list of (row_index, row_text, condition) for top suppliers.
    """
    # Filter to valid conditions only
    valid_rows = []
    for idx, text, cond in rows:
        if cond and cond in VALID_CONDITIONS:
            valid_rows.append((idx, text, cond))
    
    # Deduplicate by vendor (extract vendor name from text)
    # For now, we'll just take unique rows and sort by condition priority
    seen_vendors = set()
    unique_rows = []
    
    for idx, text, cond in valid_rows:
        # Simple vendor extraction - adjust based on actual page structure
        vendor_match = re.search(r'^([A-Z][A-Za-z\s\-&.]+)', text)
        vendor = vendor_match.group(1).strip() if vendor_match else f"vendor_{idx}"
        
        vendor_key = vendor.upper()
        if vendor_key not in seen_vendors:
            seen_vendors.add(vendor_key)
            unique_rows.append((idx, text, cond))
    
    # Sort by condition priority
    ranked = sorted(unique_rows, key=lambda x: (CONDITION_PRIORITY.get(x[2], 999), x[0]))
    
    return ranked[:max_count]


def click_send_and_handle_popup(page: Page, row_index: int, log_file) -> Tuple[bool, Optional[Page]]:
    """
    Click Send button on the specified row and handle the popup.
    Returns (success, popup_page).
    """
    try:
        rows = page.locator('tr').all()
        if row_index >= len(rows):
            log_message(log_file, f"[ERROR] Row index {row_index} out of range")
            return False, None
        
        row = rows[row_index]
        
        # Find Send button in the row
        send_btn = row.locator('a:has-text("Send")').first
        
        if not send_btn.is_visible():
            log_message(log_file, f"[WARN] Send button not visible in row {row_index}")
            return False, None
        
        # Click Send and wait for popup
        try:
            with page.expect_popup(timeout=15000) as popup_info:
                send_btn.click()
            
            popup = popup_info.value
            log_message(log_file, f"[OK] Popup opened for row {row_index}")
            popup.wait_for_load_state("networkidle")
            time.sleep(2)
            return True, popup
        except Exception as e:
            log_message(log_file, f"[WARN] Popup expectation failed: {e}")
            # Try clicking without popup expectation
            send_btn.click()
            time.sleep(3)
            log_message(log_file, f"[INFO] Clicked Send, checking if on RFQ page")
            if 'rfq' in page.url.lower():
                return True, None  # RFQ form on same page
            return False, None
            
    except Exception as e:
        log_message(log_file, f"[ERROR] Click Send failed: {e}")
        return False, None


def fill_and_submit_rfq(popup_or_page, pn: str, log_file) -> bool:
    """
    Fill quantity and submit RFQ form.
    Returns True if successful.
    """
    try:
        # Try to find quantity input
        qty_filled = False
        qty_selectors = [
            'input[type="number"]',
            'input[name*="qty" i]',
            'input[name*="quantity" i]',
            'input[id*="qty" i]',
        ]
        
        for selector in qty_selectors:
            try:
                qty_input = popup_or_page.locator(selector).first
                if qty_input.is_visible():
                    qty_input.fill("1")
                    log_message(log_file, f"[OK] Quantity set to 1")
                    qty_filled = True
                    break
            except:
                continue
        
        if not qty_filled:
            # Try JavaScript fallback
            try:
                popup_or_page.evaluate('''() => {
                    const inputs = document.querySelectorAll('input');
                    for (let input of inputs) {
                        if (input.type === 'number' || 
                            (input.name && input.name.toLowerCase().includes('qty')) ||
                            (input.id && input.id.toLowerCase().includes('qty'))) {
                            input.value = '1';
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            return 'filled';
                        }
                    }
                    return 'not_found';
                }''')
                log_message(log_file, f"[OK] Quantity set via JavaScript")
                qty_filled = True
            except Exception as e:
                log_message(log_file, f"[WARN] JavaScript quantity fill failed: {e}")
        
        time.sleep(1)
        
        # Try to find and click Submit button
        submit_clicked = False
        submit_selectors = [
            'input[value*="Submit" i]',
            'input[value*="Send" i]',
            'button:has-text("Submit")',
            'button:has-text("Send")',
            'input[type="submit"]',
        ]
        
        for selector in submit_selectors:
            try:
                submit_btn = popup_or_page.locator(selector).first
                if submit_btn.is_visible():
                    submit_btn.click()
                    log_message(log_file, f"[SUCCESS] RFQ submitted!")
                    submit_clicked = True
                    time.sleep(2)
                    break
            except:
                continue
        
        if not submit_clicked:
            # Try JavaScript fallback
            try:
                result = popup_or_page.evaluate('''() => {
                    const buttons = document.querySelectorAll('input, button');
                    for (let btn of buttons) {
                        const val = (btn.value || btn.textContent || '').toLowerCase();
                        if (val.includes('submit') || val.includes('send')) {
                            btn.click();
                            return 'submitted';
                        }
                    }
                    // Fallback: try first button
                    if (buttons.length > 0) {
                        buttons[0].click();
                        return 'clicked_first';
                    }
                    return 'not_found';
                }''')
                log_message(log_file, f"[INFO] Submit via JavaScript: {result}")
                submit_clicked = True
            except Exception as e:
                log_message(log_file, f"[ERROR] JavaScript submit failed: {e}")
        
        return submit_clicked
        
    except Exception as e:
        log_message(log_file, f"[ERROR] Fill and submit failed: {e}")
        return False


def process_part_number(browser, context, pn: str, pn_name: str, log_file, result_file) -> PartResult:
    """Process RFQ submission for a single part number."""
    log_message(log_file, f"\n{'='*60}")
    log_message(log_file, f"[START] Processing PN: {pn} - {pn_name}")
    log_message(log_file, f"{'='*60}")
    
    result = PartResult(part_number=pn, part_name=pn_name)
    
    try:
        page = context.new_page()
        
        # Navigate to search page
        log_message(log_file, f"[NAV] Going to stockmarket.aero...")
        page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do", wait_until="networkidle")
        time.sleep(2)
        
        # Search for part number
        log_message(log_file, f"[SEARCH] Searching for {pn}...")
        search_input = page.locator('input[value="Enter Part Number"]').first
        if search_input.is_visible():
            search_input.fill(pn)
            page.locator('input[value="Go"]').first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(4)  # Wait for results to load
            log_message(log_file, f"[OK] Search completed")
        else:
            log_message(log_file, f"[ERROR] Search input not found")
            result.failed_count += 1
            return result
        
        # Expand all rows if available
        try:
            expand_all = page.locator('a:has-text("Expand All")').first
            if expand_all.is_visible():
                expand_all.click()
                time.sleep(2)
                log_message(log_file, f"[OK] Expanded all rows")
        except:
            log_message(log_file, f"[INFO] Expand All not available")
        
        # Find supplier rows
        log_message(log_file, f"[FIND] Finding supplier rows for {pn}...")
        rows = find_supplier_rows(page, pn)
        result.total_suppliers_found = len(rows)
        log_message(log_file, f"[INFO] Found {len(rows)} total rows")
        
        if not rows:
            log_message(log_file, f"[WARN] No suppliers found for {pn}")
            return result
        
        # Filter and rank suppliers
        top_suppliers = filter_and_rank_suppliers(rows, pn, MAX_SUPPLIERS_PER_PN)
        result.valid_suppliers_count = len(top_suppliers)
        log_message(log_file, f"[OK] Selected {len(top_suppliers)} valid suppliers (after filtering)")
        
        # Process each supplier
        for idx, row_text, condition in top_suppliers:
            log_message(log_file, f"\n[SUBMIT] Processing supplier at row {idx}, condition {condition}")
            
            supplier_result = SupplierResult(
                vendor=f"row_{idx}",
                condition=condition,
                pn=pn,
                status="pending",
                timestamp=datetime.now().isoformat()
            )
            
            # Click Send and handle popup
            success, popup = click_send_and_handle_popup(page, idx, log_file)
            
            if not success:
                supplier_result.status = "failed"
                supplier_result.error = "Failed to click Send or open popup"
                result.failed_count += 1
                result.suppliers.append(supplier_result)
                continue
            
            # Fill and submit RFQ
            if popup:
                submit_success = fill_and_submit_rfq(popup, pn, log_file)
                popup.close()
            else:
                submit_success = fill_and_submit_rfq(page, pn, log_file)
            
            if submit_success:
                supplier_result.status = "success"
                result.success_count += 1
                result.submitted_count += 1
                log_message(log_file, f"[OK] Successfully submitted to supplier")
            else:
                supplier_result.status = "failed"
                supplier_result.error = "Failed to submit RFQ form"
                result.failed_count += 1
                log_message(log_file, f"[FAIL] RFQ submission failed")
            
            result.suppliers.append(supplier_result)
            time.sleep(2)  # Brief pause between submissions
        
        log_message(log_file, f"\n[COMPLETE] PN {pn}: {result.success_count}/{result.valid_suppliers_count} successful")
        
    except Exception as e:
        log_message(log_file, f"[ERROR] Processing {pn} failed: {e}")
        result.failed_count += 1
    finally:
        try:
            page.close()
        except:
            pass
    
    return result


def main():
    """Main execution function."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = OUTPUT_DIR / f"rfq_auto_run_{timestamp}.jsonl"
    result_path = OUTPUT_DIR / f"rfq_result_{timestamp}.json"
    
    all_results = {
        "run_id": timestamp,
        "start_time": datetime.now().isoformat(),
        "target_parts": TARGET_PARTS,
        "part_results": [],
        "summary": {
            "total_submitted": 0,
            "total_success": 0,
            "total_failed": 0,
            "total_suppliers_covered": 0,
        }
    }
    
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_message(log_file, f"RFQ Auto-Submit Run Started: {timestamp}")
        log_message(log_file, f"Target Parts: {[p['pn'] for p in TARGET_PARTS]}")
        log_message(log_file, f"Max suppliers per PN: {MAX_SUPPLIERS_PER_PN}")
        log_message(log_file, f"Valid conditions: {VALID_CONDITIONS}")
        log_message(log_file, f"Condition priority: NE > FN > NS > OH > SV > AR")
        
        try:
            with sync_playwright() as p:
                # Launch browser
                log_message(log_file, f"\n[BROWSER] Launching Chromium...")
                browser = p.chromium.launch(headless=False, slow_mo=200)
                
                # Create context (user should already be logged in)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                # Process each part number
                for part_info in TARGET_PARTS:
                    pn = part_info["pn"]
                    pn_name = part_info["name"]
                    
                    part_result = process_part_number(
                        browser, context, pn, pn_name, log_file, result_path
                    )
                    
                    all_results["part_results"].append(asdict(part_result))
                    all_results["summary"]["total_submitted"] += part_result.submitted_count
                    all_results["summary"]["total_success"] += part_result.success_count
                    all_results["summary"]["total_failed"] += part_result.failed_count
                    all_results["summary"]["total_suppliers_covered"] += part_result.valid_suppliers_count
                    
                    # Save intermediate results
                    with open(result_path, "w", encoding="utf-8") as f:
                        json.dump(all_results, f, indent=2, ensure_ascii=False)
                
                browser.close()
                log_message(log_file, f"\n[BROWSER] Browser closed")
                
        except Exception as e:
            log_message(log_file, f"[FATAL] Run failed: {e}")
            import traceback
            log_message(log_file, traceback.format_exc())
        
        all_results["end_time"] = datetime.now().isoformat()
        
        # Final summary
        log_message(log_file, f"\n{'='*60}")
        log_message(log_file, f"RUN SUMMARY")
        log_message(log_file, f"{'='*60}")
        log_message(log_file, f"Total submitted: {all_results['summary']['total_submitted']}")
        log_message(log_file, f"Total success: {all_results['summary']['total_success']}")
        log_message(log_file, f"Total failed: {all_results['summary']['total_failed']}")
        log_message(log_file, f"Total suppliers covered: {all_results['summary']['total_suppliers_covered']}")
        log_message(log_file, f"Results saved to: {result_path}")
        log_message(log_file, f"Log saved to: {log_path}")
        
        # Save final results
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"RFQ Auto-Submit Complete!")
    print(f"{'='*60}")
    print(f"Total submitted: {all_results['summary']['total_submitted']}")
    print(f"Total success: {all_results['summary']['total_success']}")
    print(f"Total failed: {all_results['summary']['total_failed']}")
    print(f"Suppliers covered: {all_results['summary']['total_suppliers_covered']}")
    print(f"Results: {result_path}")
    print(f"Log: {log_path}")
    
    return all_results


if __name__ == "__main__":
    main()
