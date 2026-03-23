#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch RFQ emails from Haite Group (cynthia@haitegroup.com) via Gmail IMAP
"""

import imaplib
import email
from email.header import decode_header
import json
import ssl
from datetime import datetime
import os

# Gmail IMAP configuration
IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993
IMAP_USER = 'jianghaide@gmail.com'
IMAP_PASS = 'Aa138222'

def decode_mime_words(s):
    """Decode MIME encoded words in email headers"""
    if not s:
        return ''
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(part.decode('utf-8', errors='ignore'))
        else:
            decoded.append(part)
    return ''.join(decoded)

def get_email_body(msg):
    """Extract text body from email message"""
    body = ''
    
    if msg.is_multipart():
        # Prefer plain text part
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition') or '')
            
            # Skip attachments
            if 'attachment' in content_disposition.lower():
                continue
            
            if content_type == 'text/plain':
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(charset, errors='ignore')
                        break
                except:
                    pass
        
        # If no plain text, try HTML
        if not body:
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode(charset, errors='ignore')
                            break
                    except:
                        pass
    else:
        # Not multipart
        try:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(charset, errors='ignore')
        except:
            body = msg.get_payload()
    
    return body

def parse_rfq_content(text):
    """Parse RFQ email content to extract part numbers, quantities, and conditions"""
    parts = []
    
    # Common patterns in RFQ emails
    lines = text.split('\n')
    
    # Try to find table-like structures or lists
    current_part = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for part number patterns (alphanumeric with dashes)
        # Examples: 123456-789, ABC-123-XYZ, etc.
        
        # Try to detect part info in various formats
        # Format 1: PN: XXX, QTY: YYY, COND: ZZZ
        if 'PN' in line.upper() or 'P/N' in line.upper() or 'PART' in line.upper():
            # Extract part number
            import re
            pn_match = re.search(r'(?:PN|P/N|Part\s*(?:Number|#)?|件号)[:\s]*([A-Z0-9\-]+)', line, re.IGNORECASE)
            qty_match = re.search(r'(?:QTY|Qty|Quantity|数量)[:\s]*(\d+)', line, re.IGNORECASE)
            cond_match = re.search(r'(?:COND|Condition|条件)[:\s]*([A-Z]+)', line, re.IGNORECASE)
            
            if pn_match:
                if current_part and 'pn' in current_part:
                    parts.append(current_part)
                current_part = {
                    'pn': pn_match.group(1).upper(),
                    'qty': qty_match.group(1) if qty_match else '',
                    'cond': cond_match.group(1).upper() if cond_match else ''
                }
        
        # Format 2: Table row with tabs or multiple spaces
        elif '\t' in line or '   ' in line:
            tokens = [t.strip() for t in line.split() if t.strip()]
            if len(tokens) >= 2:
                # First token might be PN, second might be qty
                potential_pn = tokens[0]
                if re.match(r'^[A-Z0-9\-]+$', potential_pn, re.IGNORECASE) and len(potential_pn) >= 5:
                    if current_part and 'pn' in current_part:
                        parts.append(current_part)
                    current_part = {
                        'pn': potential_pn.upper(),
                        'qty': tokens[1] if len(tokens) > 1 and tokens[1].isdigit() else '',
                        'cond': ''
                    }
                    # Look for condition in remaining tokens
                    for token in tokens[2:]:
                        if token.upper() in ['SV', 'NE', 'OH', 'AR', 'FN', 'AS', 'RT']:
                            current_part['cond'] = token.upper()
                            break
    
    # Add last part if exists
    if current_part and 'pn' in current_part:
        parts.append(current_part)
    
    # If no structured data found, try to find all potential part numbers in text
    if not parts:
        import re
        # Match common part number patterns
        pn_pattern = r'\b([A-Z]?[0-9]{5,}-[A-Z0-9\-]+|[A-Z]{2,}[0-9]{3,}-[0-9]+)\b'
        matches = re.findall(pn_pattern, text.upper())
        for pn in matches[:20]:  # Limit to 20
            parts.append({'pn': pn, 'qty': '', 'cond': ''})
    
    return parts

def main():
    print('=' * 60)
    print('Gmail RFQ Email Fetcher')
    print('=' * 60)
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        print(f'\nConnecting to {IMAP_HOST}:{IMAP_PORT}...')
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, ssl_context=ssl_context)
        
        print('Authenticating...')
        mail.login(IMAP_USER, IMAP_PASS)
        print('✓ Authentication successful')
        
        print('Selecting INBOX...')
        mail.select('INBOX')
        print('✓ INBOX selected')
        
        # Search for emails from cynthia@haitegroup.com
        print('\nSearching for emails from cynthia@haitegroup.com...')
        status, messages = mail.search(None, '(FROM "cynthia@haitegroup.com")')
        
        if status != 'OK':
            print('✗ Search failed')
            return
        
        email_ids = messages[0].split()
        print(f'✓ Found {len(email_ids)} email(s)')
        
        if not email_ids:
            print('No emails found from cynthia@haitegroup.com')
            return
        
        # Get the latest 10 emails
        latest_ids = email_ids[-10:]
        
        emails_data = []
        
        print(f'\nFetching {len(latest_ids)} latest email(s)...\n')
        
        for email_id in latest_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Get headers
                    subject = decode_mime_words(msg.get('Subject', ''))
                    from_addr = decode_mime_words(msg.get('From', ''))
                    date_str = msg.get('Date', '')
                    
                    # Parse date
                    try:
                        date_obj = email.utils.parsedate_to_datetime(date_str)
                        date_formatted = date_obj.isoformat()
                    except:
                        date_formatted = date_str
                    
                    # Get body
                    body = get_email_body(msg)
                    
                    emails_data.append({
                        'id': email_id.decode(),
                        'subject': subject,
                        'from': from_addr,
                        'date': date_formatted,
                        'body': body
                    })
                    
                    print(f'  [{len(emails_data)}] Subject: {subject}')
                    print(f'      Date: {date_formatted}')
                    print(f'      From: {from_addr}')
                    print()
        
        # Sort by date (newest first)
        emails_data.sort(key=lambda x: x['date'], reverse=True)
        
        print('=' * 60)
        print('SUMMARY')
        print('=' * 60)
        print(f'\nTotal emails found: {len(emails_data)}')
        
        if emails_data:
            latest = emails_data[0]
            print(f'\nLatest email:')
            print(f'  Subject: {latest["subject"]}')
            print(f'  Date: {latest["date"]}')
            print(f'  From: {latest["from"]}')
            
            # Parse RFQ content
            print('\n' + '=' * 60)
            print('RFQ CONTENT ANALYSIS')
            print('=' * 60)
            
            parts = parse_rfq_content(latest['body'])
            
            if parts:
                print(f'\nFound {len(parts)} part(s):')
                for i, part in enumerate(parts, 1):
                    print(f'  {i}. PN: {part["pn"]}, QTY: {part["qty"] or "N/A"}, COND: {part["cond"] or "N/A"}')
            else:
                print('\nNo structured part data found in email body.')
                print('\nEmail body preview (first 500 chars):')
                print(latest['body'][:500])
            
            # Create output JSON
            output = {
                'email_subject': latest['subject'],
                'email_date': latest['date'],
                'sender': latest['from'],
                'parts': parts,
                'all_emails': [
                    {
                        'subject': e['subject'],
                        'date': e['date'],
                        'from': e['from']
                    }
                    for e in emails_data
                ]
            }
            
            # Save to file
            output_path = 'C:/Users/Haide/Desktop/haite_rfq_requirements.json'
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f'\n✓ Saved to: {output_path}')
            
            # Also save full raw data
            raw_output = {
                'latest_email': latest,
                'all_emails': emails_data
            }
            raw_path = 'C:/Users/Haide/Desktop/haite_rfq_raw.json'
            with open(raw_path, 'w', encoding='utf-8') as f:
                json.dump(raw_output, f, ensure_ascii=False, indent=2)
            print(f'✓ Saved raw data to: {raw_path}')
        
        mail.logout()
        print('\n✓ Done')
        
    except imaplib.IMAP4.error as e:
        print(f'✗ IMAP error: {e}')
        print('\nPossible solutions:')
        print('1. Gmail may require an App Password instead of regular password')
        print('2. Check if IMAP access is enabled in Gmail settings')
        print('3. Verify username and password are correct')
    except Exception as e:
        print(f'✗ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
