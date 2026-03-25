#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取 jianghaide@aeroedgeglobal.com 邮箱收件箱
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

def main():
    print("=" * 70)
    print("jianghaide@aeroedgeglobal.com - Inbox Check")
    print("Time: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    print("\n[1] Connecting...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDR, EMAIL_PASS)
        print("  OK - Logged in")
    except Exception as e:
        print("  FAIL: %s" % str(e))
        return

    mail.select("INBOX")

    # Get recent emails
    since = "20-Mar-2026"
    print("\n[2] Searching since %s..." % since)
    status, msgs = mail.search(None, '(SINCE %s)' % since)
    if status != "OK":
        print("  Search failed")
        mail.logout()
        return

    msg_ids = msgs[0].split()
    print("  Found %d emails" % len(msg_ids))

    print("\n[3] Latest emails:")
    print("-" * 100)
    print("%-4s %-25s %-50s %s" % ("No", "From", "Subject", "Date"))
    print("-" * 100)

    for idx, mid in enumerate(msg_ids[-30:], 1):  # Last 30
        try:
            st, data = mail.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
            if st != "OK":
                continue
            msg = email.message_from_bytes(data[0][1])
            subject = decode_mime(msg.get("Subject", ""))
            from_addr = decode_mime(msg.get("From", ""))
            date_str = decode_mime(msg.get("Date", ""))

            # Shorten from
            from_short = from_addr.split('<')[0].strip()[:25] if '<' in from_addr else from_addr[:25]
            # Shorten date
            date_short = date_str[:20] if date_str else ""

            print("%-4d %-25s %-50s %s" % (idx, from_short, subject[:50], date_short))
        except:
            continue

    print("-" * 100)
    mail.logout()
    print("\nDone.")

if __name__ == "__main__":
    main()
