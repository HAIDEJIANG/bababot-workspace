#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取 Abraham Siria 邮件 - 全量搜索后过滤
"""

import imaplib
import email
from email.header import decode_header
import sys
import re

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
    print("Abraham Siria - Full Scan")
    print("=" * 70)

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ADDR, EMAIL_PASS)
    print("Logged in OK")

    mail.select("INBOX")

    # Get all recent emails and filter locally
    since = "25-Dec-2025"
    status, msgs = mail.search(None, '(SINCE %s)' % since)
    if status != "OK":
        print("Search failed")
        mail.logout()
        return

    msg_ids = msgs[0].split()
    print("Total emails since %s: %d" % (since, len(msg_ids)))
    print("Scanning for Abraham Siria...")

    found = 0
    for mid in msg_ids:
        try:
            st, data = mail.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
            if st != "OK":
                continue
            msg = email.message_from_bytes(data[0][1])
            from_addr = decode_mime(msg.get("From", "")).lower()

            if "abraham" in from_addr or "siria" in from_addr:
                subject = decode_mime(msg.get("Subject", ""))
                date_str = decode_mime(msg.get("Date", ""))

                # Fetch full body
                st2, data2 = mail.fetch(mid, "(RFC822)")
                if st2 == "OK":
                    full_msg = email.message_from_bytes(data2[0][1])
                    body = get_body(full_msg)
                else:
                    body = ""

                found += 1
                print("\n--- Email #%d ---" % found)
                print("From: %s" % from_addr)
                print("Date: %s" % date_str)
                print("Subject: %s" % subject)
                print("Body:\n%s" % body[:2000])
                print("---")
        except:
            continue

    mail.logout()
    print("\n\nTotal Abraham Siria emails: %d" % found)

if __name__ == "__main__":
    main()
