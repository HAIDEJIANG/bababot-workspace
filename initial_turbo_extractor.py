# -*- coding: utf-8 -*-
"""
Initial Aviation 和 Turbo Resources 邮件需求提取
"""

import imaplib
import email
from email.header import decode_header
import sys
import re
from datetime import datetime
import csv
from config import (
    IMAP_CONFIG,
    INITIAL_TURBO_ANALYSIS_FILE,
    OUTPUT_ENCODING,
    DEFAULT_OUTPUT_DIR
)

sys.stdout.reconfigure(encoding='utf-8')

# IMAP 配置（从 config 模块导入）
IMAP_SERVER = IMAP_CONFIG["server"]
IMAP_PORT = IMAP_CONFIG["port"]
USERNAME = "jianghaide@aeroedgeglobal.com"
AUTH_CODE = "arv9KztNY$JWaHx3"

# 输出文件路径（使用配置路径）
OUTPUT_FILE = INITIAL_TURBO_ANALYSIS_FILE

print("="*80)
print("=== Initial Aviation & Turbo Resources Email Extractor ===")
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Output Directory: {DEFAULT_OUTPUT_DIR}")
print("="*80)

def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return ''.join(
        part.decode(encoding or 'utf-8', errors='ignore') if isinstance(part, bytes) else part
        for part, encoding in decoded
    )

def extract_parts_from_body(body):
    """从邮件正文提取零件号"""
    parts = []
    lines = body.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            # Pattern: part_number followed by description
            match = re.match(r'^([A-Z0-9\-]+)\s+(.+)$', line, re.IGNORECASE)
            if match and len(match.group(1)) >= 5:
                pn = match.group(1)
                desc = match.group(2)
                # Filter out non-part lines
                if not any(kw in desc.lower() for kw in ['please', 'quote', 'part', 'number', 'description', 'hello', 'hi ', 'thanks', 'regards', 'best', 'subject']):
                    parts.append({'PN': pn, 'Desc': desc})
    return parts

print("=== Initial Aviation & Turbo Resources Email Extractor ===")
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(USERNAME, AUTH_CODE)
mail.select("INBOX")

# Search ALL
print("\nSearching ALL emails since 2026-01-01...")
status, messages = mail.search(None, '(SINCE "01-Jan-2026")')

if status != "OK":
    print("Search failed")
    exit()

email_ids = messages[0].split()
print(f"Found {len(email_ids)} total emails")

# Filter and extract
print("\nFiltering Initial Aviation and Turbo Resources emails...\n")

target_companies = ['initialaviation', 'initial aviation', 'turboresources', 'turbo resources']
emails_data = []

for i, eid in enumerate(email_ids, 1):
    status, msg_data = mail.fetch(eid, "(RFC822)")
    if status != "OK":
        continue
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            from_ = decode_mime_words(msg.get("From", ""))
            
            # Check if target company
            from_lower = from_.lower()
            is_target = any(company in from_lower for company in target_companies)
            
            if is_target:
                subject = decode_mime_words(msg.get("Subject", ""))
                date_str = msg.get("Date", "")
                
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
                
                # Extract parts
                parts = extract_parts_from_body(body)
                
                # Determine company
                company = "Initial Aviation" if "initialaviation" in from_lower else "Turbo Resources"
                
                print(f"{'='*80}")
                print(f"Date: {formatted_date}")
                print(f"From: {from_}")
                print(f"Company: {company}")
                print(f"Subject: {subject}")
                print(f"Parts found: {len(parts)}")
                if parts:
                    for pn in parts[:10]:
                        print(f"  {pn['PN']}: {pn['Desc'][:60]}")
                    if len(parts) > 10:
                        print(f"  ... and {len(parts) - 10} more")
                print()
                
                emails_data.append({
                    "Date": formatted_date,
                    "From": from_,
                    "Company": company,
                    "Subject": subject,
                    "Body": body[:2000],
                    "Parts": parts
                })

print(f"\nTotal emails found: {len(emails_data)}")

# Export CSV
print("\nExporting to CSV...")

all_parts = []
for e in emails_data:
    for part in e['Parts']:
        all_parts.append({
            "Date": e['Date'],
            "Company": e['Company'],
            "From": e['From'][:50],
            "Subject": e['Subject'][:50],
            "PartNumber": part['PN'],
            "Description": part['Desc']
        })

# Two output files (using config paths)
output_file_all = INITIAL_TURBO_ANALYSIS_FILE
output_file_summary = DEFAULT_OUTPUT_DIR / "Initial_Turbo_Summary.csv"

if all_parts:
    # Full analysis
    fieldnames = ["Date", "Company", "From", "Subject", "PartNumber", "Description"]
    with open(output_file_all, 'w', newline='', encoding=OUTPUT_ENCODING) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_parts)
    
    print(f"[OK] Exported {len(all_parts)} parts to: {output_file_all}")
    
    # Summary by company
    company_stats = {}
    for e in emails_data:
        c = e['Company']
        if c not in company_stats:
            company_stats[c] = {'emails': 0, 'parts': 0}
        company_stats[c]['emails'] += 1
        company_stats[c]['parts'] += len(e['Parts'])
    
    print("\n=== Summary ===")
    for company, stats in company_stats.items():
        print(f"{company}: {stats['emails']} emails, {stats['parts']} parts")
    
    # Print all parts
    print(f"\n=== All Parts ({len(all_parts)} total) ===")
    for p in all_parts[:50]:
        print(f"{p['Date']} | {p['Company']:<20} | {p['PartNumber']:<20} | {p['Description'][:40]}")
    if len(all_parts) > 50:
        print(f"... and {len(all_parts) - 50} more")
else:
    print("[WARN] No parts extracted")

mail.close()
mail.logout()

print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== Task Complete ===")
