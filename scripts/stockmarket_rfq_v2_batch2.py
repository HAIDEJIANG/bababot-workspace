#!/usr/bin/env python3
"""
StockMarket.aero RFQ 自动化脚本 v2 - Batch 2 (PN 44-53)
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
    pn = re.sub(r'[（(].*?[）)]', '', raw_pn)
    pn = pn.strip().split(' ')[0].split('\t')[0]
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

# PN 44-53 (待执行)
PARTS_LIST = [
    (44, "00871-2125-0250", "new", 1),
    (45, "40-647-577-03", "new", 1),
    (46, "40-657-5102", "new", 1),
    (47, "40-656-5043", "new", 1),
    (48, "7517832-4", "new", 1),
    (49, "438006002", "new", 1),
    (50, "CS203-04", "new", 1),
    (51, "8-99511-23", "new", 1),
    (52, "8-995-02", "sv", 1),
    (53, "2233000-816-1", "new", 1),  # 客户要求全新件，无全新件库存则跳过
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
        if cond_type == "new":
            primary_conds = NEW_CONDITIONS
            fallback_conds = None
        else:
            primary_conds = SV_CONDITIONS
            fallback_conds = NEW_CONDITIONS
        
        r = self._retry_get(f"{BASE_URL}/SearchAction.do", params={
            "theAction": "expandAll", "partNumber": pn, "partial": "false"
        })
        soup = BeautifulSoup(r.text, "html.parser")
        
        for h3 in soup.find_all("h3"):
            if "0" in h3.get_text() and "results" in h3.get_text():
                return [], "no_stock"

        all_entries = []
        current_vendor = None
        rows = soup.find_all("tr")
        
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            
            for i, cell in enumerate(cells):
                if cell.get_text(strip=True) == pn and i > 0 and len(cells) >= 3:
                    vendor_text = cells[0].get_text(strip=True)
                    for cert in ["This vendor has been", "European Commission", "Lists Alternates", "View Images", "This vendor is displaying"]:
                        idx = vendor_text.find(cert)
                        if idx > 0:
                            vendor_text = vendor_text[:idx].strip()
                    current_vendor = vendor_text
                    break
            
            if len(cells) == 7:
                pn_text = cells[0].get_text(strip=True)
                cond = cells[3].get_text(strip=True).upper()
                
                if pn_text == pn and cond not in EXCLUDED_CONDITIONS:
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
        
        primary = [e for e in all_entries if e["condition"] in primary_conds]
        
        if primary:
            return primary, "ok"
        
        if fallback_conds:
            fallback = [e for e in all_entries if e["condition"] in fallback_conds]
            if fallback:
                return fallback, "fallback"
        
        return [], "no_match"

    def send_rfq(self, entry, pn, qty):
        idMap = "{sysStmKey=%s, searchKey=%s, rowId=%s}" % (
            entry["sysStmKey"], entry["searchKey"], entry["rowId"]
        )
        
        r = self._retry_get(f"{BASE_URL}/LoadItemDetailAction.do", params={
            "actiontype": "rfq", "idMap": idMap
        })
        
        if r.status_code != 200:
            return False, "form_load_failed"
        
        soup = BeautifulSoup(r.text, "html.parser")
        rfq_form = soup.find("form", id="rfqForm")
        if not rfq_form:
            return False, "no_rfq_form"
        
        form_data = {}
        for inp in rfq_form.find_all("input"):
            name = inp.get("name")
            if name:
                form_data[name] = inp.get("value", "")
        
        form_data["refNumber"] = RFQ_REFERENCE
        form_data["quanitity"] = str(qty)
        form_data["priority"] = "ROUTINE"
        form_data["headerNotes"] = RFQ_COMMENTS
        
        r2 = self._retry_post(f"{BASE_URL}/RFQConfirmAction.do", data=form_data)
        
        if r2.status_code == 200 and "sent successfully" in r2.text.lower():
            return True, "sent"
        elif r2.status_code == 200 and "RFQ Sent" in r2.text:
            return True, "sent"
        else:
            soup2 = BeautifulSoup(r2.text, "html.parser")
            title = soup2.find("title")
            title_text = title.get_text() if title else ""
            if "RFQ Sent" in title_text or "sent" in r2.text.lower():
                return True, "sent"
            return False, "submit_failed: " + title_text[:50]

    def process_part(self, idx, pn, cond_type, qty):
        clean_pn_val = clean_pn(pn)
        if clean_pn_val != pn:
            print("\n[PN %d] %s -> %s | %s | x%d" % (idx, pn, clean_pn_val, "New" if cond_type == "new" else "SV", qty))
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
        
        seen = set()
        unique = []
        for e in entries:
            if e["vendor"] not in seen:
                seen.add(e["vendor"])
                unique.append(e)
        
        to_send = unique[:10]
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
                time.sleep(1.5)
            except Exception as ex:
                print(" ERROR: %s" % str(ex)[:50])
                time.sleep(2)
        
        self.results.append((idx, pn, "sent", sent_count, "; ".join(sent_list)))
        print("  == %d/%d RFQ sent" % (sent_count, len(to_send)))

    def run(self):
        from datetime import datetime
        print("=" * 60)
        print("StockMarket.aero RFQ Auto v2 - Batch 2 (PN 44-53)")
        print("RFQ: %s" % RFQ_REFERENCE)
        print("Time: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)
        
        if not self.login():
            print("Login failed")
            return
        
        for idx, pn, cond_type, qty in PARTS_LIST:
            self.process_part(idx, pn, cond_type, qty)
            time.sleep(2)
        
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
        
        log_path = os.path.join(os.path.dirname(__file__), "..", "rfq_auto_results_batch2.csv")
        with open(log_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["PN#", "Part Number", "Status", "RFQ Count", "Vendors"])
            for row in self.results:
                w.writerow(row)
        print("\nResults saved: %s" % log_path)


if __name__ == "__main__":
    bot = StockMarketRFQ()
    bot.run()
