#!/usr/bin/env python3
"""
DOMAS Email Processor
Search for DOMAS emails and extract equipment requirements
"""

import imaplib
import email
from email.header import decode_header
import re
import pandas as pd
from datetime import datetime
import os

# Email configuration
EMAIL_CONFIG = {
    'sale': {
        'imap_host': 'imaphz.qiye.163.com',
        'imap_port': 993,
        'user': 'sale@aeroedgeglobal.com',
        'password': 'A4D8%b3x6FHAH45d'
    },
    'jianghaide': {
        'imap_host': 'imaphz.qiye.163.com',
        'imap_port': 993,
        'user': 'jianghaide@aeroedgeglobal.com',
        'password': 'A4D8%b3x6FHAH45d'
    }
}

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
                decoded.append(part.decode('latin-1', errors='ignore'))
        else:
            decoded.append(part)
    return ''.join(decoded)

def get_email_body(msg):
    """Extract the body content from an email message"""
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
    return body

def extract_equipment_info(subject, body, from_email, date):
    """Extract equipment requirements from email content"""
    requirements = []
    
    # Combine subject and body for searching
    content = f"{subject}\n{body}"
    
    # Common patterns for part numbers (aviation industry)
    part_number_patterns = [
        r'\b([A-Z]{1,3}\d{4,6}[-]?\d{1,3}[A-Z]?)\b',  # e.g., CFM56-7B, V2500-A1
        r'\b(\d{6,8}[-]?\d{1,3})\b',  # e.g., 1152466-250
        r'\b([A-Z]{2,4}[-]?\d{4,6}[-]?\d{1,3})\b',  # e.g., PW4000-94
    ]
    
    # Pattern for quantity
    qty_patterns = [
        r'(?:QTY|Quantity|数量|件数)[:：\s]*(\d+)',
        r'(\d+)\s*(?:EA|PCS|Pieces|件|个|台)',
        r'require[:\s]+(\d+)\s+(?:units?|pieces?|sets?)',
    ]
    
    # Pattern for equipment name
    equipment_patterns = [
        r'(?:Equipment|Item|Part|Component|器材|设备|零件)[:：\s]*([A-Za-z0-9\s\-\(\)]+?)(?:\n|$)',
        r'(?:Description|描述)[:：\s]*([A-Za-z0-9\s\-\(\)]+?)(?:\n|$)',
    ]
    
    # Try to find part numbers
    part_numbers = []
    for pattern in part_number_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        part_numbers.extend(matches)
    
    # Try to find quantities
    quantities = []
    for pattern in qty_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        quantities.extend(matches)
    
    # Try to find equipment names
    equipment_names = []
    for pattern in equipment_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        equipment_names.extend([m.strip() for m in matches if len(m.strip()) > 3])
    
    # Create requirement entries
    if part_numbers or equipment_names:
        # If we found specific info
        for i, pn in enumerate(part_numbers[:3]):  # Limit to 3 per email
            req = {
                '日期': date,
                '发件人邮箱': from_email,
                '邮件主题': subject[:100],
                '器材名称': equipment_names[i] if i < len(equipment_names) else '未明确',
                '型号/件号 (Part Number)': pn,
                '数量': quantities[i] if i < len(quantities) else '未明确',
                '需求描述': content[:500].replace('\n', ' ').strip(),
                '优先级': '中等',
                '备注': ''
            }
            requirements.append(req)
        
        # If no part numbers but has equipment names
        if not part_numbers and equipment_names:
            for i, name in enumerate(equipment_names[:3]):
                req = {
                    '日期': date,
                    '发件人邮箱': from_email,
                    '邮件主题': subject[:100],
                    '器材名称': name,
                    '型号/件号 (Part Number)': '待确认',
                    '数量': quantities[i] if i < len(quantities) else '未明确',
                    '需求描述': content[:500].replace('\n', ' ').strip(),
                    '优先级': '中等',
                    '备注': ''
                }
                requirements.append(req)
    else:
        # General requirement entry for emails mentioning DOMAS
        if 'DOMAS' in content.upper():
            req = {
                '日期': date,
                '发件人邮箱': from_email,
                '邮件主题': subject[:100],
                '器材名称': '待分析',
                '型号/件号 (Part Number)': '待确认',
                '数量': '待确认',
                '需求描述': content[:500].replace('\n', ' ').strip(),
                '优先级': '中等',
                '备注': '需要人工审核'
            }
            requirements.append(req)
    
    return requirements if requirements else []

def search_domas_emails(email_config, account_name):
    """Search for DOMAS emails in an account"""
    print(f"\n{'='*60}")
    print(f"Processing account: {account_name} ({email_config['user']})")
    print('='*60)
    
    all_requirements = []
    
    try:
        # Connect to IMAP server
        print(f"Connecting to {email_config['imap_host']}:{email_config['imap_port']}...")
        mail = imaplib.IMAP4_SSL(email_config['imap_host'], email_config['imap_port'])
        
        # Login
        print(f"Logging in as {email_config['user']}...")
        mail.login(email_config['user'], email_config['password'])
        
        # Select inbox
        mail.select('INBOX')
        
        # Search for emails from DOMAS - try multiple search criteria
        print("Searching for emails from DOMAS...")
        
        # Try different search queries
        search_queries = [
            '(FROM "DOMAS")',
            '(SUBJECT "DOMAS")',
            '(BODY "DOMAS")',
            '(OR FROM "DOMAS" SUBJECT "DOMAS")',
            'ALL'  # Fallback: get all emails and filter manually
        ]
        
        messages = None
        for query in search_queries:
            status, messages = mail.search(None, query)
            if status == 'OK' and messages[0]:
                print(f"  Search query '{query}' found {len(messages[0].split()) emails")
                break
        
        if not messages or not messages[0]:
            print("  No messages found with any search query")
            mail.close()
            mail.logout()
            return []
        
        if status != 'OK':
            print(f"No messages found or search failed")
            mail.close()
            mail.logout()
            return []
        
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} emails")
        
        # Process each email
        for i, email_id in enumerate(email_ids[:50]):  # Limit to 50 emails per account
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Get email metadata
                        subject = decode_mime_words(msg.get('Subject', ''))
                        from_email = decode_mime_words(msg.get('From', ''))
                        date_str = msg.get('Date', '')
                        
                        # Parse date
                        try:
                            date_obj = email.utils.parsedate_to_datetime(date_str)
                            date = date_obj.strftime('%Y-%m-%d %H:%M')
                        except:
                            date = date_str[:20] if date_str else 'Unknown'
                        
                        # Get body
                        body = get_email_body(msg)
                        
                        print(f"  Processing email {i+1}/{min(len(email_ids), 50)}: {subject[:50]}...")
                        
                        # Extract requirements
                        reqs = extract_equipment_info(subject, body, from_email, date)
                        all_requirements.extend(reqs)
                        
            except Exception as e:
                print(f"    Error processing email: {e}")
                continue
        
        mail.close()
        mail.logout()
        print(f"Successfully processed {account_name}")
        
    except Exception as e:
        print(f"Error connecting to {account_name}: {e}")
    
    return all_requirements

def main():
    """Main function"""
    print("DOMAS Email Processor")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_requirements = []
    
    # Process each email account
    for account_name, config in EMAIL_CONFIG.items():
        reqs = search_domas_emails(config, account_name)
        all_requirements.extend(reqs)
        print(f"\nFound {len(reqs)} requirements from {account_name}")
    
    # Create DataFrame
    if all_requirements:
        df = pd.DataFrame(all_requirements)
        
        # Ensure output directory exists
        output_dir = 'C:/Users/Haide/Desktop/OPENCLAW'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to Excel
        output_file = os.path.join(output_dir, 'DOMAS_Requirements_Summary.xlsx')
        df.to_excel(output_file, index=False, sheet_name='DOMAS Requirements')
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total emails processed: {len(all_requirements)}")
        print(f"Total requirements extracted: {len(all_requirements)}")
        print(f"Output file: {output_file}")
        print(f"Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    else:
        print("\nNo DOMAS-related requirements found in either account.")
        # Create empty Excel with headers
        df = pd.DataFrame(columns=[
            '日期', '发件人邮箱', '邮件主题', '器材名称', 
            '型号/件号 (Part Number)', '数量', '需求描述', '优先级', '备注'
        ])
        
        output_dir = 'C:/Users/Haide/Desktop/OPENCLAW'
        os.makedirs(output_dir, exist_ok=True)
        output_file = 'C:/Users/Haide/Desktop/OPENCLAW/DOMAS_Requirements_Summary.xlsx'
        df.to_excel(output_file, index=False, sheet_name='DOMAS Requirements')
        print(f"Created empty summary file: {output_file}")

if __name__ == '__main__':
    main()
