# -*- coding: utf-8 -*-
"""
Blue Sky Technics 邮件需求提取脚本
直接连接 IMAP，提取邮件信息并导出 CSV
"""

import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime
import csv
import sys
from config import (
    IMAP_CONFIG,
    BLUE_SKY_REQUIREMENTS_FILE,
    OUTPUT_ENCODING,
    DEFAULT_OUTPUT_DIR
)

# 设置 stdout 为 utf-8
sys.stdout.reconfigure(encoding='utf-8')

# IMAP 配置（从 config 模块导入）
IMAP_SERVER = IMAP_CONFIG["server"]
IMAP_PORT = IMAP_CONFIG["port"]
USERNAME = "jianghaide@aeroedgeglobal.com"
AUTH_CODE = "arv9KztNY$JWaHx3"

# 输出文件路径（使用配置路径）
OUTPUT_FILE = BLUE_SKY_REQUIREMENTS_FILE

print("="*80)
print("=== Blue Sky Technics Email Extractor ===")
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Output Directory: {DEFAULT_OUTPUT_DIR}")
print("="*80)

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ""
    decoded = decode_header(s)
    return ''.join(
        part.decode(encoding or 'utf-8', errors='ignore') if isinstance(part, bytes) else part
        for part, encoding in decoded
    )

def extract_part_number(text):
    """从文本中提取零件号"""
    if not text:
        return ""
    patterns = [
        r'PN[:\s]*([A-Z0-9\-]+)',
        r'Part\s*(?:Number)?[:\s]*([A-Z0-9\-]+)',
        r'P/N[:\s]*([A-Z0-9\-]+)',
        r'#([A-Z0-9\-]+)',
        r'([A-Z]{2,}\d{3,}[-\d]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def extract_quantity(text):
    """从文本中提取数量"""
    if not text:
        return ""
    patterns = [
        r'Qty[:\s]*(\d+)',
        r'Quantity[:\s]*(\d+)',
        r'(\d+)\s*pcs?',
        r'(\d+)\s*units?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def extract_condition(text):
    """从文本中提取条件"""
    if not text:
        return ""
    conditions = ['SV', 'NS', 'NE', 'OH', 'AR', 'FN', 'AS']
    text_upper = text.upper()
    for cond in conditions:
        if re.search(rf'\b{cond}\b', text_upper):
            return cond
    return ""

def main():
    print("=== Blue Sky Technics Email Extractor ===")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect IMAP
    print("\n[1/5] Connecting to IMAP server...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, AUTH_CODE)
        print("[OK] Login successful")
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return
    
    # Select INBOX
    print("\n[2/5] Selecting INBOX...")
    mail.select("INBOX")
    
    # Search Blue Sky emails
    print("\n[3/5] Searching Blue Sky Technics emails...")
    search_criteria = '(FROM "blueskytechnics.com")'
    status, messages = mail.search(None, search_criteria)
    
    if status != "OK":
        print("[ERROR] Search failed")
        return
    
    email_ids = messages[0].split()
    print(f"[OK] Found {len(email_ids)} emails")
    
    if len(email_ids) == 0:
        print("No related emails found")
        return
    
    # Extract email info
    print("\n[4/5] Extracting email information...")
    emails_data = []
    
    for i, eid in enumerate(email_ids, 1):
        print(f"  Processing {i}/{len(email_ids)}...", end=" ")
        
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            print("Skip")
            continue
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Basic info
                subject = decode_mime_words(msg.get("Subject", ""))
                from_ = decode_mime_words(msg.get("From", ""))
                date_str = msg.get("Date", "")
                
                # Parse date
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = date_str
                
                # Extract body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))
                        if ctype == "text/plain" and "attachment" not in cdispo:
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            except:
                                pass
                            break
                else:
                    try:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
                
                # Limit body length
                body_short = body[:500] if body else ""
                full_text = f"{subject} {body_short}"
                
                # Extract key info
                part_number = extract_part_number(full_text)
                quantity = extract_quantity(full_text)
                condition = extract_condition(full_text)
                
                # Determine status
                status_text = "Pending"
                if "quote" in subject.lower() or "rfq" in subject.lower():
                    status_text = "RFQ"
                elif "re:" in subject.lower() or "reply" in subject.lower():
                    status_text = "Follow-up"
                
                emails_data.append({
                    "#": i,
                    "Date": formatted_date,
                    "From": from_,
                    "Subject": subject,
                    "PartNumber": part_number,
                    "Qty": quantity,
                    "Condition": condition,
                    "Status": status_text,
                    "Notes": ""
                })
                
                print("[OK]")
    
    # Export CSV (using config path)
    print("\n[5/5] Exporting to CSV...")
    output_file = OUTPUT_FILE
    
    if emails_data:
        fieldnames = ["#", "Date", "From", "Subject", "PartNumber", "Qty", "Condition", "Status", "Notes"]
        with open(output_file, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(emails_data)
        
        print(f"[OK] Exported to: {output_file}")
        print(f"[OK] Total: {len(emails_data)} emails")
        
        # Print summary
        print("\n=== Email Summary ===")
        for e in emails_data[:10]:
            pn = e['PartNumber'] or 'N/A'
            print(f"{e['Date']} | {e['From'][:50]:<50} | {pn:<20} | {e['Status']}")
        if len(emails_data) > 10:
            print(f"... and {len(emails_data) - 10} more emails")
        
        # Statistics
        print("\n=== Statistics ===")
        status_count = {}
        for e in emails_data:
            s = e['Status']
            status_count[s] = status_count.get(s, 0) + 1
        for s, c in status_count.items():
            print(f"  {s}: {c}")
    else:
        print("[ERROR] No data to export")
    
    # Close connection
    mail.close()
    mail.logout()
    
    print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=== Task Complete ===")

if __name__ == "__main__":
    main()
