#!/usr/bin/env python3
"""
RFQ 自动提交最终版 - 连接到现有浏览器会话
- 三个零件号：10037-0770, 1152466-250, 129666-3
- Condition 过滤：NE > FN > NS > OH > SV > AR
- 每 PN 最多提交前 10 家有效供应商
"""

from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
from pathlib import Path

# 配置
TARGET_PNS = [
    {"pn": "10037-0770", "desc": "Fuel Load Preselect Indicator"},
    {"pn": "1152466-250", "desc": "APU Start Converter Unit"},
    {"pn": "129666-3", "desc": "Precooler Control Valve Sensor"},
]

VALID_CONDITIONS = ["NE", "FN", "NS", "OH", "SV", "AR"]
CONDITION_PRIORITY = {c: i for i, c in enumerate(VALID_CONDITIONS)}

OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULT_FILE = OUTPUT_DIR / f"rfq_result_{RUN_ID}.json"
LOG_FILE = OUTPUT_DIR / f"rfq_auto_run_{RUN_ID}.jsonl"


def log(event: str, **kwargs):
    """写入日志"""
    entry = {
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "event": event,
        **kwargs
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[LOG] {event}: {kwargs}")


def extract_condition_from_row(row_text: str) -> str:
    """从行文本中提取 Condition"""
    text_upper = row_text.upper()
    for cond in VALID_CONDITIONS:
        if f" {cond} " in text_upper or f" {cond}\n" in text_upper or text_upper.startswith(cond):
            return cond
    return None


def parse_suppliers_from_page(page, pn: str) -> list:
    """从搜索结果页解析供应商列表"""
    suppliers = []
    
    # 获取所有表格行
    rows = page.locator('tr').all()
    
    for idx, row in enumerate(rows):
        try:
            text = row.inner_text()
            
            # 检查是否包含零件号
            if pn not in text:
                continue
            
            # 提取供应商信息
            vendor = None
            location = None
            qty = None
            condition = None
            
            # 尝试解析单元格
            cells = row.locator('td').all()
            for cell in cells:
                cell_text = cell.inner_text().strip()
                if not cell_text:
                    continue
                
                # 供应商名称通常在第一列
                if vendor is None and len(cell_text) > 3:
                    vendor = cell_text.split('\n')[0].strip()
                
                # 查找位置信息
                if 'United' in cell_text or 'Kingdom' in cell_text or 'Canada' in cell_text or 'AZ,' in cell_text or 'CA,' in cell_text:
                    location = cell_text
                
                # 查找数量
                if 'RQST' in cell_text.upper() or cell_text.isdigit():
                    qty = cell_text
                
                # 查找 Condition
                for cond in VALID_CONDITIONS:
                    if cond in cell_text.upper():
                        condition = cond
                        break
            
            # 如果 Condition 不在单元格中，从整行文本提取
            if condition is None:
                condition = extract_condition_from_row(text)
            
            if vendor:
                suppliers.append({
                    "vendor": vendor,
                    "location": location or "Unknown",
                    "qty": qty or "RQST",
                    "condition": condition,
                    "row_index": idx
                })
        except Exception as e:
            print(f"解析行 {idx} 失败：{e}")
    
    return suppliers


def select_top_suppliers(suppliers: list, max_count: int = 10) -> list:
    """按优先级选择供应商"""
    # 过滤有效 Condition
    valid_suppliers = [s for s in suppliers if s.get("condition") in VALID_CONDITIONS]
    
    # 按优先级排序
    valid_suppliers.sort(key=lambda s: (
        CONDITION_PRIORITY.get(s["condition"], 999),
        s["vendor"].lower()
    ))
    
    # 去重（同一供应商只保留最高优先级）
    seen_vendors = set()
    unique_suppliers = []
    for s in valid_suppliers:
        vendor_key = s["vendor"].upper()
        if vendor_key not in seen_vendors:
            seen_vendors.add(vendor_key)
            unique_suppliers.append(s)
    
    return unique_suppliers[:max_count]


def submit_rfq_for_supplier(page, supplier: dict, pn: str, part_desc: str) -> dict:
    """为单个供应商提交 RFQ"""
    result = {
        "vendor": supplier["vendor"],
        "condition": supplier["condition"],
        "status": "pending",
        "error": None
    }
    
    try:
        # 点击供应商行（展开详情）
        rows = page.locator('tr').all()
        if supplier["row_index"] < len(rows):
            row = rows[supplier["row_index"]]
            
            # 查找并点击 "Send" 按钮
            try:
                send_btn = row.locator('a:has-text("Send"), input[value="Send"]').first
                if send_btn.is_visible():
                    send_btn.click()
                    time.sleep(3)
                else:
                    # 尝试点击行本身
                    row.click()
                    time.sleep(3)
            except Exception as e:
                print(f"点击 Send 失败：{e}")
                row.click()
                time.sleep(3)
        
        # 等待模态框出现
        time.sleep(5)
        
        # 填写 RFQ 表单
        try:
            # 查找数量输入框
            qty_input = page.locator('input[name*="qty"], input[placeholder*="Qty"], input[value*="1"]').first
            if qty_input.is_visible():
                qty_input.fill("1")
        except:
            pass
        
        # 查找并点击 "Submit RFQ" 按钮
        submit_clicked = False
        
        # 尝试多种选择器
        selectors = [
            'input[value="Submit RFQ"]',
            'button:has-text("Submit RFQ")',
            'input[type="submit"]',
            'button[type="submit"]',
        ]
        
        for selector in selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    submit_clicked = True
                    print(f"点击了提交按钮：{selector}")
                    break
            except:
                continue
        
        if not submit_clicked:
            # 尝试通过角色查找
            try:
                btn = page.get_by_role('button', name='Submit RFQ')
                if btn.is_visible():
                    btn.click()
                    submit_clicked = True
            except:
                pass
        
        if submit_clicked:
            time.sleep(3)
            result["status"] = "submitted"
            print(f"成功提交：{supplier['vendor']}")
        else:
            result["status"] = "failed"
            result["error"] = "Submit button not found"
            print(f"提交失败：找不到提交按钮")
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"提交异常：{e}")
    
    return result


def process_part_number(page, pn_info: dict) -> dict:
    """处理单个零件号的 RFQ 提交"""
    pn = pn_info["pn"]
    desc = pn_info["desc"]
    
    log("pn_start", pn=pn, desc=desc)
    
    result = {
        "pn": pn,
        "description": desc,
        "suppliers_found": 0,
        "suppliers_valid": 0,
        "submissions": []
    }
    
    try:
        # 搜索零件号
        log("search_start", pn=pn)
        
        # 清空搜索框
        search_box = page.locator('input[value="Enter Part Number"]').first
        search_box.fill("")
        time.sleep(1)
        
        # 输入零件号
        search_box.fill(pn)
        time.sleep(1)
        
        # 点击 Go
        go_btn = page.locator('input[value="Go"]').first
        go_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        log("search_complete", pn=pn)
        
        # 展开所有行
        try:
            expand_btn = page.locator('a:has-text("Expand All"), a:has-text("expand")').first
            if expand_btn.is_visible():
                expand_btn.click()
                time.sleep(3)
                log("expanded_all_rows")
        except:
            log("expand_not_found")
        
        # 解析供应商
        suppliers = parse_suppliers_from_page(page, pn)
        result["suppliers_found"] = len(suppliers)
        log("suppliers_parsed", count=len(suppliers))
        
        # 选择前 10 家有效供应商
        top_suppliers = select_top_suppliers(suppliers, max_count=10)
        result["suppliers_valid"] = len(top_suppliers)
        log("top_suppliers_selected", count=len(top_suppliers), suppliers=[s["vendor"] for s in top_suppliers])
        
        # 为每家供应商提交 RFQ
        for supplier in top_suppliers:
            log("submit_start", vendor=supplier["vendor"], condition=supplier["condition"])
            submission_result = submit_rfq_for_supplier(page, supplier, pn, desc)
            result["submissions"].append(submission_result)
            log("submit_complete", vendor=supplier["vendor"], status=submission_result["status"])
            
            # 等待一下，避免太快
            time.sleep(2)
        
        # 截图保存
        try:
            screenshot_path = OUTPUT_DIR / f"{pn}_{RUN_ID}.png"
            page.screenshot(path=str(screenshot_path))
            log("screenshot_saved", path=str(screenshot_path))
        except Exception as e:
            log("screenshot_failed", error=str(e))
        
    except Exception as e:
        log("pn_error", pn=pn, error=str(e))
        result["error"] = str(e)
    
    log("pn_complete", pn=pn, submissions=len(result["submissions"]))
    return result


def main():
    """主函数"""
    log("run_start", run_id=RUN_ID, target_pns=[p["pn"] for p in TARGET_PNS])
    
    all_results = {
        "run_id": RUN_ID,
        "start_time": datetime.now().isoformat(),
        "target_pns": TARGET_PNS,
        "results": []
    }
    
    try:
        with sync_playwright() as p:
            # 连接到现有浏览器（CDP 端口 18800）
            log("browser_connect", cdp_url="http://127.0.0.1:18800")
            
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
            
            # 使用现有标签页或创建新标签页
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                pages = context.pages
                if pages:
                    page = pages[0]
                    log("using_existing_page", url=page.url)
                else:
                    page = context.new_page()
            else:
                context = browser.new_context()
                page = context.new_page()
            
            # 导航到 stockmarket.aero（如果不在该页面）
            if "stockmarket.aero" not in page.url:
                log("navigating", url="https://www.stockmarket.aero/StockMarket/Welcome.do")
                page.goto("https://www.stockmarket.aero/StockMarket/Welcome.do")
                page.wait_for_load_state("networkidle")
                time.sleep(3)
            
            log("browser_ready", url=page.url)
            
            # 处理每个零件号
            for pn_info in TARGET_PNS:
                result = process_part_number(page, pn_info)
                all_results["results"].append(result)
            
            browser.close()
            
    except Exception as e:
        log("run_error", error=str(e))
        all_results["error"] = str(e)
    
    # 保存结果
    all_results["end_time"] = datetime.now().isoformat()
    
    # 计算统计
    total_submissions = sum(len(r.get("submissions", [])) for r in all_results["results"])
    successful = sum(1 for r in all_results["results"] for s in r.get("submissions", []) if s.get("status") == "submitted")
    failed = sum(1 for r in all_results["results"] for s in r.get("submissions", []) if s.get("status") == "failed")
    unique_vendors = set()
    for r in all_results["results"]:
        for s in r.get("submissions", []):
            unique_vendors.add(s.get("vendor"))
    
    all_results["summary"] = {
        "total_submissions": total_submissions,
        "successful": successful,
        "failed": failed,
        "unique_vendors_covered": len(unique_vendors)
    }
    
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    log("run_complete", 
        total=total_submissions, 
        success=successful, 
        failed=failed,
        vendors=len(unique_vendors),
        result_file=str(RESULT_FILE),
        log_file=str(LOG_FILE)
    )
    
    print(f"\n{'='*60}")
    print(f"RFQ 自动提交完成")
    print(f"提交总数：{total_submissions}")
    print(f"成功：{successful}")
    print(f"失败：{failed}")
    print(f"覆盖供应商数：{len(unique_vendors)}")
    print(f"结果文件：{RESULT_FILE}")
    print(f"日志文件：{LOG_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
