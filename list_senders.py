#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出收件箱中的所有发件人
"""

import imaplib
import email
from email.header import decode_header
import ssl

IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993
USERNAME = "jianghaide@aeroedgeglobal.com"
PASSWORD = "arv9KztNY" + chr(36) + "JWaHx3"

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

def main():
    print("Connecting...")
    ssl_context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
    
    try:
        print("Logging in...")
        mail.login(USERNAME, PASSWORD)
        
        print("Selecting INBOX...")
        mail.select("INBOX")
        
        print("Searching ALL...")
        status, messages = mail.search(None, "ALL")
        
        if status != "OK":
            print("Search failed!")
            return
        
        email_ids = messages[0].split()
        print(f"Total: {len(email_ids)} emails\n")
        
        # Collect all senders
        senders = {}
        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                from_raw = msg.get("From", "")
                from_decoded = decode_mime_words(from_raw)
                
                # Extract email address
                import re
                email_match = re.search(r'<([^>]+)>', from_decoded)
                email_addr = email_match.group(1) if email_match else from_decoded
                
                if email_addr not in senders:
                    senders[email_addr] = from_decoded
                
            except Exception as e:
                continue
        
        # Print unique senders
        print(f"Unique senders: {len(senders)}\n")
        for addr, name in sorted(senders.items()):
            print(f"  {name} <{addr}>")
        
        # Search for Blue Sky or Domas
        print("\n" + "=" * 60)
        print("Searching for 'Blue Sky' or 'Domas'...")
        print("=" * 60)
        found = False
        for addr, name in senders.items():
            if 'blue' in name.lower() or 'sky' in name.lower() or 'domas' in name.lower() or 'blue' in addr.lower() or 'sky' in addr.lower() or 'domas' in addr.lower():
                print(f"  FOUND: {name} <{addr}>")
                found = True
        
        if not found:
            print("  No matching senders found!")
        
    finally:
        mail.close()
        mail.logout()
        print("\nDone.")

if __name__ == "__main__":
    main()
