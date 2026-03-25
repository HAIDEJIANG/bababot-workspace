#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取 Abraham Siria 最近3个月的所有邮件内容
"""

import imaplib
import email
from email.header import decode_header
import sys
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
EMAIL_ADDR = "jianghaide@aeroedgeglobal.com"
EMAIL_PASS = "arv9KztNY$JWaHx3"

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
    return body[:3000]

def main():
    print("=" * 70)
    print("Abraham Siria - Email Extraction (Last 3 months)")
    print("=" * 70)

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ADDR, EMAIL_PASS)
    print("Logged in OK")

    mail.select("INBOX")

    # Search last 3 months
    since = "25-Dec-2025"
    print("Searching since %s..." % since)

    # Search by FROM containing abraham or siria
    status, msgs = mail.search(None, '(SINCE %s FROM "abraham")' % since)
    msg_ids_1 = msgs[0].split() if status == "OK" else []

    status2, msgs2 = mail.search(None, '(SINCE %s FROM "siria")' % since)
    msg_ids_2 = msgs2[0].split() if status2 == "OK" else []

    # Combine and deduplicate
    all_ids = list(set(msg_ids_1 + msg_ids_2))
    all_ids.sort(key=lambda x: int(x))
    print("Found %d emails from Abraham Siria" % len(all_ids))

    print("\n" + "=" * 70)
    for idx, mid in enumerate(all_ids, 1):
        try:
            st, data = mail.fetch(mid, "(RFC822)")
            if st != "OK":
                continue
            msg = email.message_from_bytes(data[0][1])
            subject = decode_mime(msg.get("Subject", ""))
            from_addr = decode_mime(msg.get("From", ""))
            date_str = decode_mime(msg.get("Date", ""))
            body = get_body(msg)

            print("\n--- Email #%d ---" % idx)
            print("From: %s" % from_addr)
            print("Date: %s" % date_str)
            print("Subject: %s" % subject)
            print("Body:")
            print(body[:1500])
            print("---")
        except Exception as e:
            print("Error reading email %s: %s" % (mid, str(e)[:50]))

    mail.logout()
    print("\nDone.")

if __name__ == "__main__":
    main()
