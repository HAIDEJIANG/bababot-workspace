# -*- coding: utf-8 -*-
"""
Blue Sky Technics 邮件提取 - 使用 ALL 搜索后过滤
"""

import imaplib
import email
from email.header import decode_header
import sys
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

print("=== Blue Sky Technics Email Extractor ===")
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(USERNAME, AUTH_CODE)
mail.select("INBOX")

# Search ALL then filter
print("\n[1/3] Searching ALL emails since 2026-01-01...")
status, messages = mail.search(None, '(SINCE "01-Jan-2026")')

if status != "OK":
    print("[ERROR] Search failed")
    exit()

email_ids = messages[0].split()
print(f"[OK] Found {len(email_ids)} total emails")

# Filter for Blue Sky
print("\n[2/3] Filtering Blue Sky Technics emails...")
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
                print(f"  Found: {from_}")
                
                # Extract info
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
                
                body_short = body[:500] if body else ""
                full_text = f"{subject} {body_short}"
                
                # Extract part number
                part_number = ""
                import re
                patterns = [r'PN[:\s]*([A-Z0-9\-]+)', r'([A-Z]{2,}\d{3,}[-\d]*)']
                for pattern in patterns:
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        part_number = match.group(1)
                        break
                
                # Extract condition
                condition = ""
                for cond in ['SV', 'NS', 'NE', 'OH', 'AR']:
                    if re.search(rf'\b{cond}\b', full_text.upper()):
                        condition = cond
                        break
                
                # Determine status
                status_text = "Pending"
                if "quote" in subject.lower() or "rfq" in subject.lower():
                    status_text = "RFQ"
                elif "re:" in subject.lower():
                    status_text = "Follow-up"
                
                emails_data.append({
                    "#": len(emails_data) + 1,
                    "Date": formatted_date,
                    "From": from_,
                    "Subject": subject,
                    "PartNumber": part_number,
                    "Qty": "",
                    "Condition": condition,
                    "Status": status_text,
                    "Notes": ""
                })

print(f"\n[OK] Found {len(emails_data)} Blue Sky emails")

# Export CSV
print("\n[3/3] Exporting to CSV...")
output_file = r"C:\Users\Haide\Desktop\Blue_Sky_Technics_Requirements.csv"

if emails_data:
    fieldnames = ["#", "Date", "From", "Subject", "PartNumber", "Qty", "Condition", "Status", "Notes"]
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(emails_data)
    
    print(f"[OK] Exported to: {output_file}")
    
    # Print summary
    print("\n=== Email Summary ===")
    for e in emails_data:
        pn = e['PartNumber'] or 'N/A'
        cond = e['Condition'] or 'N/A'
        print(f"{e['Date']} | {e['Subject'][:60]:<60} | {pn:<20} | {cond:<6} | {e['Status']}")
    
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

mail.close()
mail.logout()

print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=== Task Complete ===")
