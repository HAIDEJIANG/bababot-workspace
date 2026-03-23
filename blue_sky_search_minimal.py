#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blue Sky Technics 需求汇总（最小版）
- 只搜索最近 50 封邮件
- 找到就立即处理
"""

import imaplib
import email
from email.header import decode_header
import csv
import re
import ssl

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
PASSWORD = "arv9KztNY" + chr(36) + "JWaHx3"

OUTPUT_CSV = r"C:\Users\Haide\Desktop\Blue_Sky_Technics_需求汇总.csv"

def decode_mime_words(s):
    try:
        if not s:
            return ""
        decoded = []
        for part, encoding in decode_header(s):
            if isinstance(part, bytes):
                decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
            else:
                decoded.append(str(part))
        return ''.join(decoded)
    except:
        return str(s) if s else ""

def extract_part_number(text):
    if not text:
        return ""
    patterns = [r'PN[:\s]*([A-Z0-9\-]+)', r'P/N[:\s]*([A-Z0-9\-]+)', r'#([A-Z0-9\-]+)']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    general_pattern = r'\b([A-Z]{1,3}[0-9]{4,}(?:-[A-Z0-9]+)?)\b'
    match = re.search(general_pattern, text)
    if match:
        return match.group(1)
    return ""

def extract_quantity(text):
    if not text:
        return ""
    patterns = [r'Qty[:\s]*(\d+)', r'(\d+)\s*pcs?']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def extract_condition(text):
    if not text:
        return ""
    conditions = ['SV', 'NS', 'NE', 'OH', 'AR', 'FN', 'AS']
    text_upper = text.upper()
    for cond in conditions:
        if re.search(r'\b' + cond + r'\b', text_upper):
            return cond
    return ""

def get_email_body(msg):
    try:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition") or "")
                if "attachment" in content_disposition.lower():
                    continue
                if content_type == "text/plain":
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(charset, errors='ignore')
                        break
        else:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(charset, errors='ignore')
        return body[:500] if body else ""
    except:
        return ""

def main():
    print("Blue Sky Technics 需求汇总（最小版）")
    
    results = []
    
    print(f"Connecting to {IMAP_SERVER}...")
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    
    try:
        mail.login(USERNAME, PASSWORD)
        mail.select("INBOX")
        
        # Get all email IDs
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        # Only check the last 50 emails
        recent_ids = email_ids[-50:] if len(email_ids) > 50 else email_ids
        print(f"Checking last {len(recent_ids)} emails")
        
        for email_id in recent_ids:
            try:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                from_raw = msg.get("From", "").lower()
                
                # Check for Blue Sky Technics
                if 'domas@blueskytechnics.com' not in from_raw:
                    continue
                
                # Extract date
                date_str = msg.get("Date", "")
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                    if date_obj.year < 2025:
                        continue
                    date_formatted = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    date_formatted = date_str
                
                subject = decode_mime_words(msg.get("Subject", ""))
                body = get_email_body(msg)
                
                part_number = extract_part_number(subject + " " + body)
                quantity = extract_quantity(body)
                condition = extract_condition(body)
                
                # Determine status from subject/body
                text_upper = (subject + " " + body).upper()
                if any(kw in text_upper for kw in ['QUOTE', 'QUOTATION']):
                    status_val = "报价"
                elif any(kw in text_upper for kw in ['OFFER', 'AVAILABLE']):
                    status_val = "有货"
                elif any(kw in text_upper for kw in ['REQUEST', 'RFQ', '需求', '需要']):
                    status_val = "需求"
                else:
                    status_val = "其他"
                
                results.append({
                    "日期": date_formatted,
                    "发件人": decode_mime_words(msg.get("From", "")),
                    "主题": subject,
                    "零件号": part_number,
                    "数量": quantity,
                    "条件": condition,
                    "状态": status_val,
                })
                
                print(f"Found: {date_formatted} | {subject[:50]}")
                
            except Exception as e:
                continue
        
        print(f"\nTotal found: {len(results)}")
        
        if results:
            fieldnames = ["日期", "发件人", "主题", "零件号", "数量", "条件", "状态"]
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Saved to: {OUTPUT_CSV}")
            
            # Display results
            for i, r in enumerate(results, 1):
                print(f"\n{i}. {r['日期']}")
                print(f"   发件人: {r['发件人']}")
                print(f"   主题: {r['主题']}")
                print(f"   零件号: {r['零件号']}")
                print(f"   数量: {r['数量']}")
                print(f"   条件: {r['条件']}")
                print(f"   状态: {r['状态']}")
        else:
            print("No Blue Sky Technics emails found.")
        
    finally:
        mail.close()
        mail.logout()
        print("\nDone.")

if __name__ == "__main__":
    main()
