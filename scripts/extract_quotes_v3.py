#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 sale@aeroedgeglobal.com 提取 RFQ 报价邮件
使用 IMAP + 授权码
"""

import imaplib
import email
from email.header import decode_header
import re
import os
import json
import csv
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IMAP_SERVER = "imap.qiye.163.com"
IMAP_PORT = 993
EMAIL_ADDR = "sale@aeroedgeglobal.com"
EMAIL_PASS = "A4D8%b3x6FHAH45d"  # IMAP authorization code

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def decode_mime(val):
    if not val:
        return ""
    parts = decode_header(val)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            except:
                result.append(part.decode('utf-8', errors='replace'))
        else:
            result.append(str(part))
    return " ".join(result)

def get_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                try:
                    payload = part.get_payload(decode=True)
                    cs = part.get_content_charset() or 'utf-8'
                    body += payload.decode(cs, errors='replace')
                except:
                    pass
            elif ct == "text/html" and "attachment" not in cd and not body:
                try:
                    payload = part.get_payload(decode=True)
                    cs = part.get_content_charset() or 'utf-8'
                    html = payload.decode(cs, errors='replace')
                    body += re.sub(r'<[^>]+>', ' ', html)
                    body = re.sub(r'\s+', ' ', body).strip()
                except:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            cs = msg.get_content_charset() or 'utf-8'
            body = payload.decode(cs, errors='replace')
        except:
            pass
    return body[:5000]

def get_attachments(msg):
    atts = []
    if msg.is_multipart():
        for part in msg.walk():
            cd = str(part.get("Content-Disposition", ""))
            if "attachment" in cd:
                fn = part.get_filename()
                if fn:
                    fn = decode_mime(fn)
                    sz = len(part.get_payload(decode=True) or b"")
                    atts.append({"filename": fn, "size": sz, "type": part.get_content_type()})
    return atts

def extract_email_addr(from_str):
    m = re.search(r'<([^>]+)>', from_str)
    return m.group(1) if m else from_str.strip()

def extract_sender_name(from_str):
    m = re.match(r'^"?([^"<]+)"?\s*<', from_str)
    return m.group(1).strip() if m else from_str.split('@')[0]

def extract_pn(text):
    patterns = [
        r'(?:P/?N|Part\s*(?:Number|No\.?))[:\s]*([A-Z0-9][\w\-\.]{3,})',
        r'Partnumber[:\s]*([A-Z0-9][\w\-\.]{3,})',
        r'\b(\d{5,}-\d{1,}(?:-\d+)?)\b',
        r'\b([A-Z]{2,}\d{4,}-\d+)\b',
    ]
    for p in patterns:
        m = re.findall(p, text, re.IGNORECASE)
        if m:
            return m[0]
    return ""

def extract_prices(text):
    prices = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', text)
    if not prices:
        prices = re.findall(r'USD\s*([\d,]+(?:\.\d{2})?)', text, re.IGNORECASE)
    return prices

def extract_condition(text):
    conds = re.findall(r'\b(FN|NE|NS|OH|SV|RP|NEW|OVERHAULED|SERVICEABLE|TESTED|INSPECTED|AR)\b', text, re.IGNORECASE)
    return conds[0].upper() if conds else ""

def extract_leadtime(text):
    m = re.search(r'\b(\d+)\s*(day|week|month|business day|working day|BD|WD)\b', text, re.IGNORECASE)
    if m:
        return m.group(0)
    if re.search(r'\bSTOCK\b', text, re.IGNORECASE):
        return "STOCK"
    if re.search(r'\bIMMEDIATE\b', text, re.IGNORECASE):
        return "IMMEDIATE"
    return ""

def extract_qty(text):
    m = re.search(r'\b(\d+)\s*(EA|PCS|pieces|units|each)\b', text, re.IGNORECASE)
    return m.group(0) if m else ""

def extract_location(text):
    locs = re.findall(r'\b(USA|US|UK|Netherlands|NL|Singapore|SG|China|CN|Germany|DE|France|FR|Canada|CA|FL|TX|NY|OH|IA|NJ|CT)\b', text, re.IGNORECASE)
    return locs[0] if locs else ""

def main():
    print("=" * 70)
    print("RFQ20260324-02 Quote Extraction via IMAP")
    print("Account: %s" % EMAIL_ADDR)
    print("Time: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    print("\n[1] Connecting...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDR, EMAIL_PASS)
        print("  OK - Logged in")
    except Exception as e:
        print("  FAIL: %s" % str(e))
        return

    mail.select("INBOX")

    since = "24-Mar-2026"
    print("\n[2] Searching since %s..." % since)
    status, msgs = mail.search(None, '(SINCE %s)' % since)
    if status != "OK":
        print("  Search failed")
        mail.logout()
        return

    msg_ids = msgs[0].split()
    print("  Found %d emails" % len(msg_ids))

    print("\n[3] Extracting quotes...")
    quotes = []
    skip_kw = ["confirmation for", "this message was sent to"]

    for idx, mid in enumerate(msg_ids):
        try:
            st, data = mail.fetch(mid, "(RFC822)")
            if st != "OK":
                continue
            msg = email.message_from_bytes(data[0][1])

            subject = decode_mime(msg.get("Subject", ""))
            from_addr = decode_mime(msg.get("From", ""))
            date_str = decode_mime(msg.get("Date", ""))

            subj_lower = subject.lower()
            # Skip StockMarket confirmations
            if any(k in subj_lower for k in skip_kw):
                continue

            # Only process quote/RFQ related
            rfq_kw = ["quote", "rfq", "pricing", "offer", "price", "aeroedge", "part number", "quotation"]
            if not any(k in subj_lower for k in rfq_kw):
                from_lower = from_addr.lower()
                if not any(k in from_lower for k in ["textquote", "stockmarket"]):
                    continue

            body = get_body(msg)
            atts = get_attachments(msg)
            combined = subject + " " + body

            pn = extract_pn(combined)
            # Try to get PN from subject specifically
            pn_subj = re.search(r'Part Number[:\s]*([A-Z0-9][\w\-\.]+)', subject, re.IGNORECASE)
            if pn_subj:
                pn = pn_subj.group(1)
            pn_subj2 = re.search(r'P/N[:\s]*([A-Z0-9][\w\-\.]+)', subject, re.IGNORECASE)
            if pn_subj2:
                pn = pn_subj2.group(1)

            prices = extract_prices(combined)
            cond = extract_condition(combined)
            lt = extract_leadtime(combined)
            qty = extract_qty(combined)
            loc = extract_location(combined)

            sender_email = extract_email_addr(from_addr)
            sender_name = extract_sender_name(from_addr)

            q = {
                "supplier": sender_name,
                "contact": sender_name,
                "email": sender_email,
                "pn": pn,
                "price_usd": prices[0] if prices else "",
                "qty": qty,
                "condition": cond,
                "lead_time": lt,
                "location": loc,
                "subject": subject[:120],
                "date": date_str,
                "attachments": [a["filename"] for a in atts],
                "body_preview": body[:300],
            }
            quotes.append(q)

            att_str = " +%d att" % len(atts) if atts else ""
            price_str = " $%s" % prices[0] if prices else ""
            print("  #%d %s | %s | %s%s%s" % (
                len(quotes), sender_name[:25], pn or "?", cond or "?", price_str, att_str))

        except Exception as e:
            continue

    mail.logout()

    print("\n" + "=" * 70)
    print("SUMMARY: %d quote emails extracted" % len(quotes))
    print("=" * 70)

    if not quotes:
        print("No quotes found")
        return

    # Save JSON
    jpath = os.path.join(OUTPUT_DIR, "rfq_quotes_full.json")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=2, ensure_ascii=False)
    print("\nJSON: %s" % jpath)

    # Save CSV
    cpath = os.path.join(OUTPUT_DIR, "rfq_quotes_full.csv")
    with open(cpath, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["No", "Supplier", "Contact", "Email", "PN", "Price_USD", "Qty", "Condition", "Lead_Time", "Location", "Subject", "Date", "Attachments"])
        for i, q in enumerate(quotes, 1):
            w.writerow([i, q["supplier"], q["contact"], q["email"], q["pn"],
                        q["price_usd"], q["qty"], q["condition"], q["lead_time"],
                        q["location"], q["subject"], q["date"],
                        "; ".join(q["attachments"])])
    print("CSV: %s" % cpath)

    # Print table
    print("\n" + "-" * 120)
    print("%-4s %-30s %-18s %-12s %-8s %-10s %-10s" % ("No", "Supplier", "PN", "Price", "Cond", "Lead", "Location"))
    print("-" * 120)
    for i, q in enumerate(quotes, 1):
        print("%-4d %-30s %-18s %-12s %-8s %-10s %-10s" % (
            i, q["supplier"][:30], q["pn"][:18],
            ("$"+q["price_usd"]) if q["price_usd"] else "-",
            q["condition"] or "-", q["lead_time"][:10] or "-", q["location"] or "-"))
    print("-" * 120)

if __name__ == "__main__":
    main()
