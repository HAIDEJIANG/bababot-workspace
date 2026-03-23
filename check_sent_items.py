#!/usr/bin/env python3
"""
Check sent emails to/from DOMAS
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
    print("Checking Sent Items for DOMAS")
    print("="*60)
    
    # Connect
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['imap_host'], EMAIL_CONFIG['imap_port'], ssl_context=ssl_context)
    mail.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
    
    # Try to access sent folder (163 uses encoded folder names)
    sent_folders = ['&XfJT0ZAB-', 'Sent', 'SENT', 'Sent Items', 'Sent Messages']
    
    for folder in sent_folders:
        try:
            status, messages = mail.select(folder)
            if status == 'OK':
                print(f"\n=== Found Sent Folder: {folder} ===")
                
                # Search for DOMAS in sent items
                status, messages = mail.search(None, '(OR TO "DOMAS" SUBJECT "DOMAS")')
                if status == 'OK' and messages[0]:
                    email_ids = messages[0].split()
                    print(f"Found {len(email_ids)} emails related to DOMAS")
                    
                    # Show details
                    for email_id in email_ids[:10]:
                        status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
                        if status == 'OK':
                            msg = email.message_from_bytes(msg_data[0][1])
                            subject = decode_mime_words(msg.get('Subject', ''))
                            to_email = decode_mime_words(msg.get('To', ''))
                            date = msg.get('Date', '')[:30]
                            print(f"  To: {to_email[:60]}")
                            print(f"  Subject: {subject[:80]}")
                            print(f"  Date: {date}")
                            print()
                else:
                    print("No DOMAS-related emails in sent folder")
                
                # Show recent sent emails
                print("\nRecent sent emails (last 10):")
                status, messages = mail.search(None, 'ALL')
                if status == 'OK':
                    email_ids = messages[0].split()
                    for email_id in reversed(email_ids[-10:]):
                        status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
                        if status == 'OK':
                            msg = email.message_from_bytes(msg_data[0][1])
                            subject = decode_mime_words(msg.get('Subject', ''))
                            to_email = decode_mime_words(msg.get('To', ''))
                            date = msg.get('Date', '')[:30]
                            print(f"  To: {to_email[:50]}, Subject: {subject[:60]}")
                break
        except Exception as e:
            print(f"Error accessing folder '{folder}': {e}")
    
    mail.logout()
    print("\nSearch completed!")

if __name__ == '__main__':
    main()
