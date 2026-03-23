#!/usr/bin/env python3
"""
Comprehensive search for DOMAS in all folders
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

def get_email_body(msg):
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body += payload.decode(charset, errors='ignore')
                except:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='ignore')
        except:
            pass
    return body[:500]  # First 500 chars only

def main():
    print("Comprehensive DOMAS Search in sale@aeroedgeglobal.com")
    print("="*60)
    
    # Connect
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['imap_host'], EMAIL_CONFIG['imap_port'], ssl_context=ssl_context)
    mail.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
    
    # List all folders
    print("\n=== Checking All Folders ===")
    status, folders = mail.list()
    
    domas_results = []
    
    if status == 'OK':
        # Decode folder names
        folder_list = []
        for f in folders:
            # Parse folder name from IMAP response
            parts = f.split(b'"')
            if len(parts) >= 3:
                folder_name = parts[-2].decode('utf-8', errors='ignore') if isinstance(parts[-2], bytes) else parts[-2]
            else:
                folder_name = f.decode('utf-8', errors='ignore')
            folder_list.append(folder_name)
        
        print(f"Found {len(folder_list)} folders: {folder_list}")
        
        # Search each folder
        for folder_name in folder_list:
            try:
                mail.select(folder_name)
                
                # Search for DOMAS in subject
                status, messages = mail.search(None, '(SUBJECT "DOMAS")')
                if status == 'OK' and messages[0]:
                    count = len(messages[0].split())
                    print(f"\n  Folder '{folder_name}': {count} emails with 'DOMAS' in SUBJECT")
                    
                    # Get details
                    for email_id in messages[0].split()[:5]:
                        status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
                        if status == 'OK':
                            msg = email.message_from_bytes(msg_data[0][1])
                            subject = decode_mime_words(msg.get('Subject', ''))
                            from_email = decode_mime_words(msg.get('From', ''))
                            date = msg.get('Date', '')[:30]
                            domas_results.append({
                                'folder': folder_name,
                                'subject': subject,
                                'from': from_email,
                                'date': date
                            })
                            print(f"    - From: {from_email}, Subject: {subject[:60]}")
                
                # Search for DOMAS in from
                status, messages = mail.search(None, '(FROM "DOMAS")')
                if status == 'OK' and messages[0]:
                    count = len(messages[0].split())
                    print(f"\n  Folder '{folder_name}': {count} emails with 'DOMAS' in FROM")
                
                # Search for DOMAS in body
                status, messages = mail.search(None, '(BODY "DOMAS")')
                if status == 'OK' and messages[0]:
                    count = len(messages[0].split())
                    print(f"\n  Folder '{folder_name}': {count} emails with 'DOMAS' in BODY")
                
            except Exception as e:
                print(f"  Error checking folder '{folder_name}': {e}")
    
    mail.logout()
    
    print("\n" + "="*60)
    print("SEARCH RESULTS SUMMARY")
    print("="*60)
    if domas_results:
        print(f"Found {len(domas_results)} DOMAS-related emails:")
        for r in domas_results:
            print(f"  Folder: {r['folder']}")
            print(f"  From: {r['from']}")
            print(f"  Subject: {r['subject']}")
            print(f"  Date: {r['date']}")
            print()
    else:
        print("No emails containing 'DOMAS' found in any folder.")
    
    print("\nSearch completed!")

if __name__ == '__main__':
    main()
