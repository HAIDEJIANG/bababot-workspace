#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本 - 查看邮件原始发件人信息
"""

import imaplib
import email
from email.header import decode_header
import ssl

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
PASSWORD = "arv9KztNY$JWaHx3"

def decode_mime_words(s):
    if not s:
        return ""
    decoded = []
    for word, encoding in decode_header(s):
        if isinstance(word, bytes):
            try:
                decoded.append(word.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(word.decode('utf-8', errors='ignore'))
        else:
            decoded.append(word)
    return ''.join(decoded)

print("Connecting to IMAP...")
ssl_context = ssl.create_default_context()
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
mail.login(USERNAME, PASSWORD)
mail.select("INBOX")

print("Fetching all emails...")
status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()
print(f"Total emails: {len(email_ids)}")

# Get last 50 emails
recent_ids = email_ids[-50:] if len(email_ids) > 50 else email_ids

print("\nChecking last 50 emails for Blue Sky/Domas:")
found_count = 0
for i, email_id in enumerate(recent_ids, 1):
    try:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status == "OK":
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    raw_from = msg.get("From", "")
                    decoded_from = decode_mime_words(raw_from)
                    subject = decode_mime_words(msg.get("Subject", ""))
                    
                    # Check for Blue Sky or Domas
                    match = False
                    if "Blue" in decoded_from or "blue" in raw_from.lower():
                        match = True
                    if "Sky" in decoded_from or "sky" in raw_from.lower():
                        match = True
                    if "Domas" in decoded_from or "domas" in raw_from.lower():
                        match = True
                    if "bluesky" in raw_from.lower():
                        match = True
                    
                    if match:
                        found_count += 1
                        print(f"\n[FOUND #{found_count}]")
                        print(f"  Raw From: {repr(raw_from[:100])}")
                        print(f"  Decoded From: {decoded_from[:100]}")
                        print(f"  Subject: {subject[:80]}")
    except Exception as e:
        print(f"Error: {e}")

print(f"\nTotal found: {found_count}")

mail.close()
mail.logout()
print("\nDone!")
