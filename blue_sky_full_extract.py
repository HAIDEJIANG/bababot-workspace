# -*- coding: utf-8 -*-
"""
重新读取 Blue Sky Technics 邮件全文，提取所有零件号
"""

import imaplib
import email
from email.header import decode_header
import sys
import re
from datetime import datetime
import csv

sys.stdout.reconfigure(encoding='utf-8')

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
AUTH_CODE = "arv9KztNY$JWaHx3"

def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return ''.join(
        part.decode(encoding or 'utf-8', errors='ignore') if isinstance(part, bytes) else part
        for part, encoding in decoded
    )

print("=== Blue Sky Technics - Full Email Content Extraction ===")
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(USERNAME, AUTH_CODE)
mail.select("INBOX")

# Search ALL then filter
print("\nSearching ALL emails since 2026-01-01...")
status, messages = mail.search(None, '(SINCE "01-Jan-2026")')

if status != "OK":
    print("Search failed")
    exit()

email_ids = messages[0].split()
print(f"Found {len(email_ids)} total emails")

# Filter for Blue Sky and extract FULL content
print("\nFiltering Blue Sky Technics emails...\n")
emails_data = []

for i, eid in enumerate(email_ids, 1):
    status, msg_data = mail.fetch(eid, "(RFC822)")
    if status != "OK":
        continue
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            from_ = decode_mime_words(msg.get("From", ""))
            
            # Check if from Blue Sky
            if "blueskytechnics" in from_.lower() or "blue sky" in from_.lower():
                subject = decode_mime_words(msg.get("Subject", ""))
                date_str = msg.get("Date", "")
                
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = date_str
                
                # Extract FULL body
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
                
                print(f"{'='*80}")
                print(f"Date: {formatted_date}")
                print(f"From: {from_}")
                print(f"Subject: {subject}")
                print(f"{'='*80}")
                print(f"\n{body[:3000]}\n")  # Print first 3000 chars
                
                # Extract part numbers line by line
                part_numbers = []
                lines = body.split('\n')
                for line in lines:
                    # Look for part number patterns
                    line = line.strip()
                    if line:
                        # Pattern: part_number followed by description
                        match = re.match(r'^([A-Z0-9\-]+)\s+(.+)$', line, re.IGNORECASE)
                        if match and len(match.group(1)) >= 5:
                            pn = match.group(1)
                            desc = match.group(2)
                            if not any(kw in desc.lower() for kw in ['please', 'quote', 'part', 'number', 'description', 'hello', 'hi ', 'thanks', 'regards']):
                                part_numbers.append({'PN': pn, 'Desc': desc})
                
                if part_numbers:
                    print(f"\n*** EXTRACTED {len(part_numbers)} PART NUMBERS ***")
                    for pn in part_numbers[:30]:
                        print(f"  {pn['PN']}: {pn['Desc'][:60]}")
                    if len(part_numbers) > 30:
                        print(f"  ... and {len(part_numbers) - 30} more")
                    print()
                
                emails_data.append({
                    "Date": formatted_date,
                    "From": from_,
                    "Subject": subject,
                    "Body": body[:2000],
                    "PartCount": len(part_numbers)
                })

print(f"\nTotal Blue Sky emails: {len(emails_data)}")

# Export detailed CSV
print("\nExporting to CSV...")
output_file = r"C:\Users\Haide\Desktop\Blue_Sky_Full_Analysis.csv"

all_parts = []
for e in emails_data:
    body = e['Body']
    lines = body.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            match = re.match(r'^([A-Z0-9\-]+)\s+(.+)$', line, re.IGNORECASE)
            if match and len(match.group(1)) >= 5:
                pn = match.group(1)
                desc = match.group(2)
                if not any(kw in desc.lower() for kw in ['please', 'quote', 'part', 'number', 'description', 'hello', 'hi ', 'thanks', 'regards']):
                    all_parts.append({
                        "Date": e['Date'],
                        "Subject": e['Subject'][:50],
                        "PartNumber": pn,
                        "Description": desc
                    })

if all_parts:
    fieldnames = ["Date", "Subject", "PartNumber", "Description"]
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_parts)
    
    print(f"[OK] Exported {len(all_parts)} parts to: {output_file}")
else:
    print("[WARN] No parts extracted")

mail.close()
mail.logout()

print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== Task Complete ===")
