#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blue Sky Technics 需求汇总脚本（最终版）
"""

import imaplib
import email
from email.header import decode_header
import csv
import re
import ssl

# IMAP 配置
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
PASSWORD = "arv9KztNY" + chr(36) + "JWaHx3"

# 搜索条件 - 使用确切的发件人
SEARCH_FROM = ["domas@blueskytechnics.com", "Domas @ Blue Sky Technics"]
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
    try:
        if not text:
            return ""
        patterns = [
            r'PN[:\s]*([A-Z0-9\-]+)',
            r'Part\s*Number[:\s]*([A-Z0-9\-]+)',
            r'P/N[:\s]*([A-Z0-9\-]+)',
            r'#([A-Z0-9\-]+)',
            r'Item[:\s]*([A-Z0-9\-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        general_pattern = r'\b([A-Z]{1,3}[0-9]{4,}(?:-[A-Z0-9]+)?)\b'
        match = re.search(general_pattern, text)
        if match:
            return match.group(1)
    except:
        pass
    return ""

def extract_quantity(text):
    try:
        if not text:
            return ""
        patterns = [r'Qty[:\s]*(\d+)', r'Quantity[:\s]*(\d+)', r'(\d+)\s*pcs?', r'数量[:\s]*(\d+)']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
    except:
        pass
    return ""

def extract_condition(text):
    try:
        if not text:
            return ""
        conditions = ['SV', 'NS', 'NE', 'OH', 'AR', 'FN', 'AS', 'US', 'RT', 'OV']
        text_upper = text.upper()
        for cond in conditions:
            if re.search(r'\b' + cond + r'\b', text_upper):
                return cond
    except:
        pass
    return ""

def extract_status(subject, body):
    try:
        text = (subject + " " + body).upper()
        if any(kw in text for kw in ['QUOTE', 'QUOTATION', '报价']):
            return "报价"
        elif any(kw in text for kw in ['OFFER', 'AVAILABLE', '有货', 'AVAILABLE']):
            return "有货"
        elif any(kw in text for kw in ['REQUEST', 'RFQ', '需求', '需要', 'LOOKING FOR', 'WANTED']):
            return "需求"
        elif any(kw in text for kw in ['ORDER', 'CONFIRM', '确认', 'PURCHASE']):
            return "订单"
        elif any(kw in text for kw in ['SOLD', '成交', 'SOLD']):
            return "成交"
    except:
        pass
    return "其他"

def get_email_body(msg):
    try:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                try:
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
                except:
                    continue
        else:
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors='ignore')
            except:
                pass
        return body[:500] if body else ""
    except:
        return ""

def main():
    print("=" * 60)
    print("Blue Sky Technics 需求汇总")
    print("=" * 60)
    
    results = []
    seen_subjects = set()
    
    print(f"\nConnecting to {IMAP_SERVER}:{IMAP_PORT}...")
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    
    try:
        print(f"Logging in as {USERNAME}...")
        mail.login(USERNAME, PASSWORD)
        
        print("Selecting INBOX...")
        mail.select("INBOX")
        
        print("Searching ALL emails...")
        status, messages = mail.search(None, "ALL")
        
        if status != "OK":
            print("Search failed!")
            return
        
        email_ids = messages[0].split()
        total = len(email_ids)
        print(f"Total emails in INBOX: {total}")
        print(f"Searching for Blue Sky Technics emails...")
        print()
        
        found_count = 0
        for idx, email_id in enumerate(email_ids):
            try:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Check sender
                from_raw = msg.get("From", "")
                from_decoded = decode_mime_words(from_raw)
                
                # Check exact match for Blue Sky Technics
                match = False
                if 'domas@blueskytechnics.com' in from_raw.lower() or 'blue sky technics' in from_decoded.lower():
                    match = True
                
                if not match:
                    continue
                
                # Extract date
                date_str = msg.get("Date", "")
                date_formatted = date_str
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                    if date_obj.year < 2025:
                        continue
                    date_formatted = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                
                # Extract subject
                subject = decode_mime_words(msg.get("Subject", ""))
                
                # Deduplicate
                if subject in seen_subjects:
                    continue
                seen_subjects.add(subject)
                
                # Get body
                body = get_email_body(msg)
                
                # Extract fields
                part_number = extract_part_number(subject + " " + body)
                quantity = extract_quantity(body)
                condition = extract_condition(body)
                status_val = extract_status(subject, body)
                
                results.append({
                    "日期": date_formatted,
                    "发件人": from_decoded,
                    "主题": subject,
                    "零件号": part_number,
                    "数量": quantity,
                    "条件": condition,
                    "状态": status_val,
                })
                
                found_count += 1
                print(f"[{found_count}] {date_formatted} | {subject[:60]}")
                
            except Exception as e:
                print(f"Error processing email: {e}")
                continue
        
        print(f"\n{'=' * 60}")
        print(f"Found {len(results)} Blue Sky Technics emails")
        
        # Save to CSV
        if results:
            fieldnames = ["日期", "发件人", "主题", "零件号", "数量", "条件", "状态"]
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Saved to: {OUTPUT_CSV}")
            
            # Display summary
            print(f"\n{'=' * 60}")
            print("Summary:")
            print(f"{'=' * 60}")
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
        
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass
        print("\nDisconnected.")

if __name__ == "__main__":
    main()
