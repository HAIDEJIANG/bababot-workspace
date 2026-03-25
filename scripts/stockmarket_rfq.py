#!/usr/bin/env python3
"""
StockMarket.aero RFQ 自动化脚本 v3 (统一版)
用法:
  python stockmarket_rfq.py parts.csv                     # 从 CSV 读取零件清单
  python stockmarket_rfq.py parts.csv --ref RFQ20260401   # 指定 RFQ 参考号
  python stockmarket_rfq.py parts.csv --start 5 --end 20  # 只跑第 5-20 行
  python stockmarket_rfq.py parts.csv --max-vendors 20    # 每个 PN 最多发 20 家（默认 20）
  python stockmarket_rfq.py parts.csv --dry-run            # 只搜索不发送

CSV 格式 (UTF-8, 首行为表头):
  序号,件号,条件,数量
  1,2117388-12,sv,1
  2,183-1524-020,new,10

条件: new = 全新件(FN/NE/NS), sv = 可用件(OH/RP/SV/TESTED/INSPECTED)
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import sys
import re
import argparse
import urllib3
from datetime import datetime

urllib3.disable_warnings()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# ===== 配置 =====
BASE_URL = "https://www.stockmarket.aero/StockMarket"
USERNAME = "sale@aeroedgeglobal.com"
PASSWORD = "Aa138222"
DEFAULT_RFQ_REF = "RFQ" + datetime.now().strftime("%Y%m%d")
RFQ_COMMENTS = "Please quote in USD. Delivery time unit required (e.g., 1D/2W/3M/4Y). Validity period must be specified. Thank you."

NEW_CONDITIONS = {"FN", "NE", "NS"}
SV_CONDITIONS = {"OH", "RP", "SV", "TESTED", "INSPECTED"}
EXCLUDED_CONDITIONS = {"AR", "DIST", "EXCHANGE", "RQST", "REQUEST"}


def clean_pn(raw_pn):
    """清洗 PN，去除括号、中文、空格后的描述信息"""
    pn = re.sub(r'[（(].*?[）)]', '', raw_pn)
    pn = pn.strip().split(' ')[0].split('\t')[0]
    pn = re.sub(r'[^A-Za-z0-9.\-]', '', pn)
    return pn


def load_parts_from_csv(csv_path):
    """从 CSV 文件加载零件清单"""
    parts = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)  # 跳过表头
        for row in reader:
            if len(row) < 4:
                continue
            idx = int(row[0].strip())
            pn = row[1].strip()
            cond = row[2].strip().lower()
            qty = int(row[3].strip())
            if pn and cond in ('new', 'sv'):
                parts.append((idx, pn, cond, qty))
    return parts


class StockMarketRFQ:
    def __init__(self, rfq_ref, max_vendors=20, dry_run=False):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        self.rfq_ref = rfq_ref
        self.max_vendors = max_vendors
        self.dry_run = dry_run
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
        """Search PN, expand all, extract sysStmKey for matching conditions"""
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
                    for cert in ["This vendor has been", "European Commission", "Lists Alternates",
                                 "View Images", "This vendor is displaying"]:
                        idx_pos = vendor_text.find(cert)
                        if idx_pos > 0:
                            vendor_text = vendor_text[:idx_pos].strip()
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
        """Send RFQ for a specific stock entry"""
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

        form_data["refNumber"] = self.rfq_ref
        form_data["quanitity"] = str(qty)  # StockMarket 的拼写错误
        form_data["priority"] = "ROUTINE"
        form_data["headerNotes"] = RFQ_COMMENTS

        r2 = self._retry_post(f"{BASE_URL}/RFQConfirmAction.do", data=form_data)

        if r2.status_code == 200:
            text_lower = r2.text.lower()
            if "sent successfully" in text_lower or "rfq sent" in text_lower:
                return True, "sent"
            soup2 = BeautifulSoup(r2.text, "html.parser")
            title = soup2.find("title")
            title_text = title.get_text() if title else ""
            if "RFQ Sent" in title_text or "sent" in text_lower:
                return True, "sent"
            return False, "submit_failed: " + title_text[:50]
        return False, "http_%d" % r2.status_code

    def process_part(self, idx, pn, cond_type, qty):
        clean = clean_pn(pn)
        label = "New" if cond_type == "new" else "SV"
        if clean != pn:
            print("\n[PN %d] %s → %s | %s | x%d" % (idx, pn, clean, label, qty))
        else:
            print("\n[PN %d] %s | %s | x%d" % (idx, pn, label, qty))

        try:
            entries, status = self.search_and_get_rfq_keys(clean, cond_type, qty)
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

        # 去重 (同一供应商只发一次)
        seen = set()
        unique = []
        for e in entries:
            if e["vendor"] not in seen:
                seen.add(e["vendor"])
                unique.append(e)

        to_send = unique[:self.max_vendors]
        sent_count = 0
        sent_list = []

        if self.dry_run:
            print("  [DRY RUN] Would send to %d vendors:" % len(to_send))
            for e in to_send:
                print("    - %s (%s)" % (e["vendor"][:50], e["condition"]))
            self.results.append((idx, pn, "dry_run", len(to_send), "; ".join(e["vendor"] for e in to_send)))
            return

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

    def run(self, parts_list):
        print("=" * 60)
        print("StockMarket.aero RFQ Auto v3")
        print("RFQ Ref: %s" % self.rfq_ref)
        print("Max vendors/PN: %d" % self.max_vendors)
        print("Parts: %d" % len(parts_list))
        print("Mode: %s" % ("DRY RUN" if self.dry_run else "LIVE"))
        print("Time: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)

        if not self.dry_run:
            if not self.login():
                print("Login failed")
                return

        for idx, pn, cond_type, qty in parts_list:
            self.process_part(idx, pn, cond_type, qty)
            time.sleep(2)

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        total = len(self.results)
        sent = sum(1 for r in self.results if r[2] in ("sent", "dry_run"))
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

        # Save CSV log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "rfq_auto_results_%s.csv" % timestamp)
        with open(log_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["PN#", "Part Number", "Status", "RFQ Count", "Vendors"])
            for row in self.results:
                w.writerow(row)
        print("\nResults saved: %s" % log_path)


def main():
    parser = argparse.ArgumentParser(description="StockMarket.aero RFQ 自动化")
    parser.add_argument("csv_file", help="零件清单 CSV 文件路径")
    parser.add_argument("--ref", default=DEFAULT_RFQ_REF, help="RFQ 参考号 (默认: RFQ+日期)")
    parser.add_argument("--start", type=int, default=None, help="起始行号 (按 CSV 中的序号列)")
    parser.add_argument("--end", type=int, default=None, help="结束行号 (按 CSV 中的序号列)")
    parser.add_argument("--max-vendors", type=int, default=20, help="每 PN 最多发送供应商数 (默认: 20)")
    parser.add_argument("--dry-run", action="store_true", help="只搜索不发送")
    args = parser.parse_args()

    # 加载零件
    parts = load_parts_from_csv(args.csv_file)
    print("Loaded %d parts from %s" % (len(parts), args.csv_file))

    # 按范围过滤
    if args.start is not None or args.end is not None:
        start = args.start or 0
        end = args.end or 99999
        parts = [(idx, pn, cond, qty) for idx, pn, cond, qty in parts if start <= idx <= end]
        print("Filtered to %d parts (range %d-%d)" % (len(parts), start, end))

    if not parts:
        print("No parts to process!")
        return

    bot = StockMarketRFQ(rfq_ref=args.ref, max_vendors=args.max_vendors, dry_run=args.dry_run)
    bot.run(parts)


if __name__ == "__main__":
    main()
