# -*- coding: utf-8 -*-
"""
列出所有发件人，查找 Blue Sky 相关邮箱
"""

import imaplib
import email
from email.header import decode_header
import sys
from datetime import datetime

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

print("=== Listing All Senders (2026-01-01 to now) ===")
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(USERNAME, AUTH_CODE)
mail.select("INBOX")

# Search all emails since 2026-01-01
print("\nSearching all emails since 2026-01-01...")
status, messages = mail.search(None, '(SINCE "01-Jan-2026")')

if status != "OK":
    print("Search failed")
    exit()

email_ids = messages[0].split()
print(f"Found {len(email_ids)} emails")

# Collect unique senders
senders = {}
print("\nProcessing emails...")

for i, eid in enumerate(email_ids[:200], 1):  # Limit to 200
    status, msg_data = mail.fetch(eid, "(RFC822)")
    if status != "OK":
        continue
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            from_ = decode_mime_words(msg.get("From", ""))
            
            if from_ not in senders:
                senders[from_] = 0
            senders[from_] += 1

# Sort by count
sorted_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)

print("\n=== Top Senders ===")
for i, (sender, count) in enumerate(sorted_senders[:30], 1):
    marker = " ***" if "blue" in sender.lower() or "sky" in sender.lower() or "domas" in sender.lower() else ""
    print(f"{i:3}. [{count:3}] {sender}{marker}")

mail.close()
mail.logout()

print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
