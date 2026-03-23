#!/usr/bin/env python3
"""
Check email folders and recent emails in sale account
"""

import imaplib
import email
from email.header import decode_header
import ssl

# Email configuration
EMAIL_CONFIG = {
    'imap_host': 'imaphz.qiye.163.com',
    'imap_port': 993,
    'user': 'sale@aeroedgeglobal.com',
    'password': 'A4D8%b3x6FHAH45d'
}

def decode_mime_words(s):
    if not s:
        return ''
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(part.decode('latin-1', errors='ignore'))
        else:
            decoded.append(part)
    return ''.join(decoded)

def main():
    print("Checking Email Folders and Recent Emails")
    print("="*60)
    
    # Connect
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['imap_host'], EMAIL_CONFIG['imap_port'], ssl_context=ssl_context)
    mail.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
    
    # List all folders
    print("\n=== Available Folders ===")
    status, folders = mail.list()
    if status == 'OK':
        for folder in folders[:20]:  # Show first 20
            print(f"  {folder}")
    
    # Check INBOX
    print("\n=== INBOX Recent Emails (Last 20) ===")
    mail.select('INBOX')
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        email_ids = messages[0].split()
        print(f"Total emails in INBOX: {len(email_ids)}")
        
        # Show last 20 emails
        for i, email_id in enumerate(reversed(email_ids[-20:])):
            status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                subject = decode_mime_words(msg.get('Subject', ''))
                from_email = decode_mime_words(msg.get('From', ''))
                date = msg.get('Date', '')[:30]
                print(f"  [{i+1}] From: {from_email[:60]}")
                print(f"      Subject: {subject[:80]}")
                print(f"      Date: {date}")
                print()
    
    # Check other common folders
    common_folders = ['Sent', 'SENT', 'Sent Messages', 'Drafts', 'Trash', 'Spam', 'Junk']
    
    for folder_name in common_folders:
        try:
            status, messages = mail.select(folder_name)
            if status == 'OK':
                status, messages = mail.search(None, '(OR FROM "DOMAS" SUBJECT "DOMAS")')
                if status == 'OK' and messages[0]:
                    count = len(messages[0].split())
                    print(f"\n=== Folder '{folder_name}': Found {count} DOMAS emails ===")
        except:
            pass
    
    mail.close()
    mail.logout()
    
    print("\nSearch completed!")

if __name__ == '__main__':
    main()
