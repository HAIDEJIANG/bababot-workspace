#!/usr/bin/env python3
"""
StockMarket.aero RFQ 自动化脚本 v2
搜索 + 条件筛选 + 自动提交 RFQ
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import sys
import re
import urllib3
urllib3.disable_warnings()

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def clean_pn(raw_pn):
    """清洗 PN，去除括号、中文、空格后的描述信息"""
    # 去除括号及其中文内容: 2233000-816-1（可用件）→ 2233000-816-1
    pn = re.sub(r'[（(].*?[）)]', '', raw_pn)
    # 去除空格后的内容（空格后通常是名称/描述）: 49-170-11 Amdt:ABC → 49-170-11
    pn = pn.strip().split(' ')[0].split('\t')[0]
    # 只保留字母、数字、连字符、点
    pn = re.sub(r'[^A-Za-z0-9.\-]', '', pn)
    return pn

# ===== 配置 =====
BASE_URL = "https://www.stockmarket.aero/StockMarket"
USERNAME = "sale@aeroedgeglobal.com"
PASSWORD = "Aa138222"
RFQ_REFERENCE = "RFQ20260324-02"
RFQ_COMMENTS = "Please quote in USD. Delivery time unit required (e.g., 1D/2W/3M/4Y). Validity period must be specified. Thank you."

NEW_CONDITIONS = {"FN", "NE", "NS"}
SV_CONDITIONS = {"OH", "RP", "SV", "TESTED", "INSPECTED"}
EXCLUDED_CONDITIONS = {"AR", "DIST", "EXCHANGE", "RQST", "REQUEST"}

PARTS_LIST = [
    (18, "2117388-12", "sv", 1),
    (19, "183-1524-020", "new", 10),
    (20, "DNN3551B", "new", 1),
    (21, "966-3138-001", "new", 10),
    (22, "98-0976", "new", 1),
    (23, "2156-604A", "sv", 1),
    (24, "98-1122", "new", 2),
    (25, "7743-00361-04", "new", 1),
    (26, "49-170-11", "sv", 1),
    (27, "2G916-1039", "new", 1),
    (28, "2G916-2501", "new", 1),
    (29, "42-767191", "new", 1),
    (30, "814462-1", "new", 3),
    (31, "433-673-1004-4061", "new", 1),
    (32, "433-673-1004-4060", "new", 1),
    (33, "433-673-1004-4062", "new", 1),
    (34, "TS30176", "new", 5),
    (35, "0248001981", "new", 20),
    (36, "IDT74FCT162646CTPV", "new", 20),
    (37, "RDX-7708CRW", "sv", 1),
    (38, "RDX-7708BRW", "sv", 1),
    (39, "5DV411474-10", "new", 5),
    (40, "H150AK26", "new", 1),
    (41, "822-0990-002", "sv", 1),
    (42, "822-0990-003", "sv", 1),
]


class StockMarketRFQ:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        self.results = []
        self.total_sent = 0

    def _retry_get(self, url, params=None, retries=3):
        for i in range(retries):
            try:
                r = self.session.get(url, params=params, timeout=45)
                return r
            except Exception as e:
                if i < retries - 1:
                    time.sleep(3)
                else:
                    raise e

    def _retry_post(self, url, data=None, retries=3):
        for i in range(retries):
            try:
                r = self.session.post(url, data=data, timeout=45, allow_redirects=True)
                return r
            except Exception as e:
                if i < retries - 1:
                    time.sleep(3)
                else:
                    raise e

    def login(self):
        print("[LOGIN] %s..." % USERNAME)
        r = self._retry_get(f"{BASE_URL}/LoadLogin.do")
        soup = BeautifulSoup(r.text, "html.parser")
        form = soup.find("form")
        action = form.get("action") if form else "/StockMarket/LoginAction.do"
        data = {"username": USERNAME, "password": PASSWORD, "rememberMe": "on", "group1": "signIn"}
        r2 = self._retry_post("https://www.stockmarket.aero" + action, data=data)
        if USERNAME in r2.text:
            print("  [OK] Logged in")
            return True
        print("  [FAIL]")
        return False

    def search_and_get_rfq_keys(self, pn, cond_type, qty):
        """Search PN, expand all, extract sysStmKey for matching conditions, then send RFQ"""
        # 条件匹配规则:
        # 全新件需求 → 只匹配 NE/FN/NS，无库存不可用可用件替代
        # 可用件需求 → 先匹配 OH/RP/SV/TESTED/INSPECTED，如无库存可退而求其次匹配全新件 NE/FN/NS
        if cond_type == "new":
            primary_conds = NEW_CONDITIONS
            fallback_conds = None  # 全新件需求不可降级
        else:
            primary_conds = SV_CONDITIONS
            fallback_conds = NEW_CONDITIONS  # 可用件需求可升级到全新件
        
        # Search with expand all
        r = self._retry_get(f"{BASE_URL}/SearchAction.do", params={
            "theAction": "expandAll", "partNumber": pn, "partial": "false"
        })
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Check no results
        for h3 in soup.find_all("h3"):
            if "0" in h3.get_text() and "results" in h3.get_text():
                return [], "no_stock"

        # Find all Send RFQ links with their sysStmKey and condition
        all_entries = []
        current_vendor = None
        rows = soup.find_all("tr")
        
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            
            # Vendor name row (has PN in one cell)
            for i, cell in enumerate(cells):
                if cell.get_text(strip=True) == pn and i > 0 and len(cells) >= 3:
                    vendor_text = cells[0].get_text(strip=True)
                    for cert in ["This vendor has been", "European Commission", "Lists Alternates", "View Images", "This vendor is displaying"]:
                        idx = vendor_text.find(cert)
                        if idx > 0:
                            vendor_text = vendor_text[:idx].strip()
                    current_vendor = vendor_text
                    break
            
            # Stock detail row (7 cells: PN | Desc | Qty | Cond | Send RFQ | Buy Now | Place PO)
            if len(cells) == 7:
                pn_text = cells[0].get_text(strip=True)
                cond = cells[3].get_text(strip=True).upper()
                
                if pn_text == pn and cond not in EXCLUDED_CONDITIONS:
                    # Extract sysStmKey from Send RFQ onclick
                    send_link = cells[4].find("a", onclick=True)
                    if send_link:
                        onclick = send_link.get("onclick", "")
                        match = re.search(r"sysStmKey=(\d+),\s*searchKey=(\d+),\s*rowId=(\d+)", onclick)
                        if match:
                            all_entries.append({
                                "vendor": current_vendor or "Unknown",
                                "condition": cond,
                                "qty": cells[2].get_text(strip=True),
                                "sysStmKey": match.group(1),
                                "searchKey": match.group(2),
                                "rowId": match.group(3),
                            })
        
        if not all_entries:
            all_send_links = soup.find_all("a", onclick=lambda x: x and "showitemdetailpopup" in x)
            if all_send_links:
                return [], "no_match"
            return [], "no_stock"
        
        # 先筛选主条件
        primary = [e for e in all_entries if e["condition"] in primary_conds]
        
        if primary:
            return primary, "ok"
        
        # 主条件无匹配，尝试降级/升级
        if fallback_conds:
            fallback = [e for e in all_entries if e["condition"] in fallback_conds]
            if fallback:
                return fallback, "fallback"  # 可用件需求降级到全新件
        
        return [], "no_match"

    def send_rfq(self, entry, pn, qty):
        """Send RFQ for a specific stock entry"""
        idMap = "{sysStmKey=%s, searchKey=%s, rowId=%s}" % (
            entry["sysStmKey"], entry["searchKey"], entry["rowId"]
        )
        
        # Step 1: Load the RFQ form
        r = self._retry_get(f"{BASE_URL}/LoadItemDetailAction.do", params={
            "actiontype": "rfq", "idMap": idMap
        })
        
        if r.status_code != 200:
            return False, "form_load_failed"
        
        soup = BeautifulSoup(r.text, "html.parser")
        rfq_form = soup.find("form", id="rfqForm")
        if not rfq_form:
            return False, "no_rfq_form"
        
        # Step 2: Extract hidden fields
        form_data = {}
        for inp in rfq_form.find_all("input"):
            name = inp.get("name")
            if name:
                form_data[name] = inp.get("value", "")
        
        # Step 3: Fill in RFQ details
        form_data["refNumber"] = RFQ_REFERENCE
        form_data["quanitity"] = str(qty)  # Note: typo in StockMarket's form
        form_data["priority"] = "ROUTINE"
        form_data["headerNotes"] = RFQ_COMMENTS
        
        # Step 4: Submit RFQ
        r2 = self._retry_post(f"{BASE_URL}/RFQConfirmAction.do", data=form_data)
        
        if r2.status_code == 200 and "sent successfully" in r2.text.lower():
            return True, "sent"
        elif r2.status_code == 200 and "RFQ Sent" in r2.text:
            return True, "sent"
        else:
            # Check response
            soup2 = BeautifulSoup(r2.text, "html.parser")
            title = soup2.find("title")
            title_text = title.get_text() if title else ""
            if "RFQ Sent" in title_text or "sent" in r2.text.lower():
                return True, "sent"
            return False, "submit_failed: " + title_text[:50]

    def process_part(self, idx, pn, cond_type, qty):
        # 清洗 PN
        clean_pn_val = clean_pn(pn)
        if clean_pn_val != pn:
            print("\n[PN %d] %s → %s | %s | x%d" % (idx, pn, clean_pn_val, "New" if cond_type == "new" else "SV", qty))
        else:
            print("\n[PN %d] %s | %s | x%d" % (idx, pn, "New" if cond_type == "new" else "SV", qty))
        
        try:
            entries, status = self.search_and_get_rfq_keys(clean_pn_val, cond_type, qty)
        except Exception as e:
            print("  ERROR: %s" % str(e)[:80])
            self.results.append((idx, pn, "error", 0, str(e)[:50]))
            return
        
        if status == "no_stock":
            print("  -- No stock")
            self.results.append((idx, pn, "no_stock", 0, ""))
            return
        
        if status == "no_match":
            print("  -- No matching condition")
            self.results.append((idx, pn, "no_match", 0, ""))
            return
        
        if status == "fallback":
            print("  -- SV requested but none found, using NE/FN/NS fallback")
        
        # Deduplicate by vendor
        seen = set()
        unique = []
        for e in entries:
            if e["vendor"] not in seen:
                seen.add(e["vendor"])
                unique.append(e)
        
        # Send RFQ to top 20
        to_send = unique[:20]
        sent_count = 0
        sent_list = []
        
        for e in to_send:
            print("  -> %s (%s) ..." % (e["vendor"][:40], e["condition"]), end="")
            try:
                ok, msg = self.send_rfq(e, pn, qty)
                if ok:
                    print(" SENT")
                    sent_count += 1
                    sent_list.append("%s(%s)" % (e["vendor"], e["condition"]))
                    self.total_sent += 1
                else:
                    print(" FAIL: %s" % msg)
                time.sleep(1.5)  # Rate limit
            except Exception as ex:
                print(" ERROR: %s" % str(ex)[:50])
                time.sleep(2)
        
        self.results.append((idx, pn, "sent", sent_count, "; ".join(sent_list)))
        print("  == %d/%d RFQ sent" % (sent_count, len(to_send)))

    def run(self):
        from datetime import datetime
        print("=" * 60)
        print("StockMarket.aero RFQ Auto v2 - Search + Submit")
        print("RFQ: %s" % RFQ_REFERENCE)
        print("Time: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)
        
        if not self.login():
            print("Login failed")
            return
        
        for idx, pn, cond_type, qty in PARTS_LIST:
            self.process_part(idx, pn, cond_type, qty)
            time.sleep(2)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        total = len(self.results)
        sent = sum(1 for r in self.results if r[2] == "sent")
        no_stock = sum(1 for r in self.results if r[2] == "no_stock")
        no_match = sum(1 for r in self.results if r[2] == "no_match")
        errors = sum(1 for r in self.results if r[2] == "error")
        print("Total PN: %d" % total)
        print("Sent RFQ: %d PN (%d total RFQs)" % (sent, self.total_sent))
        print("No stock: %d" % no_stock)
        print("No match: %d" % no_match)
        print("Errors: %d" % errors)
        
        print("\nDetails:")
        for idx, pn, status, count, vendors in self.results:
            print("  PN %d: %s | %s | %d sent | %s" % (idx, pn, status, count, vendors[:80]))
        
        # Save CSV
        log_path = os.path.join(os.path.dirname(__file__), "..", "rfq_auto_results.csv")
        with open(log_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["PN#", "Part Number", "Status", "RFQ Count", "Vendors"])
            for row in self.results:
                w.writerow(row)
        print("\nResults saved: %s" % log_path)


if __name__ == "__main__":
    bot = StockMarketRFQ()
    bot.run()
