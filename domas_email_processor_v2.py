#!/usr/bin/env python3
"""
DOMAS Email Processor v2
Search for DOMAS emails and extract equipment requirements
Enhanced version with better search and error handling
"""

import imaplib
import email
from email.header import decode_header
import re
import pandas as pd
from datetime import datetime
import os
import ssl

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
            # Also check text/html parts
            elif content_type == 'text/html' and 'attachment' not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        # Simple HTML tag removal
                        html_text = payload.decode(charset, errors='ignore')
                        clean_text = re.sub(r'<[^>]+>', ' ', html_text)
                        body += clean_text
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
    content_upper = content.upper()
    
    # Check if this is DOMAS-related
    is_domas_related = 'DOMAS' in content_upper or 'DOMAS' in from_email.upper()
    
    if not is_domas_related:
        return []
    
    # Common patterns for part numbers (aviation industry)
    part_number_patterns = [
        r'\b([A-Z]{1,4}\d{4,7}[-]?\d{1,4}[A-Z]?)\b',  # e.g., CFM567B, V2500A1
        r'\b(\d{6,8}[-]\d{1,4})\b',  # e.g., 1152466-250
        r'\b([A-Z]{2,4}[-]?\d{4,6}[-]?\d{1,3})\b',  # e.g., PW4000-94
        r'\b([A-Z]\d{4,6}[A-Z]?)\b',  # e.g., A320, B737
    ]
    
    # Pattern for quantity
    qty_patterns = [
        r'(?:QTY|Quantity|数量 | 件数)[:：\s]*(\d+)',
        r'(\d+)\s*(?:EA|PCS|Pieces|件 | 个 | 台|SET|SETS)',
        r'require[:\s]+(\d+)\s+(?:units?|pieces?|sets?)',
        r'need[:\s]+(\d+)\s+(?:units?|pieces?|sets?)',
    ]
    
    # Pattern for equipment name/description
    equipment_patterns = [
        r'(?:Equipment|Item|Part|Component|Material|器材 | 设备 | 零件 | 航材)[:：\s]*([^\n]+?)(?:\n|$)',
        r'(?:Description|描述 | 名称)[:：\s]*([^\n]+?)(?:\n|$)',
        r'(?:Product|产品)[:：\s]*([^\n]+?)(?:\n|$)',
    ]
    
    # Pattern for priority
    priority_patterns = [
        r'(?:Priority|优先级 | 紧急程度)[:：\s]*(高 | 中 | 低|Urgent|Normal|Low|High|AOG|RUSH)',
        r'\b(AOG|URGENT|RUSH|PRIORITY)\b',
    ]
    
    # Try to find part numbers
    part_numbers = []
    for pattern in part_number_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        part_numbers.extend(matches)
    # Remove duplicates while preserving order
    part_numbers = list(dict.fromkeys(part_numbers))
    
    # Try to find quantities
    quantities = []
    for pattern in qty_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        quantities.extend(matches)
    
    # Try to find equipment names
    equipment_names = []
    for pattern in equipment_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        equipment_names.extend([m.strip() for m in matches if len(m.strip()) > 2 and len(m.strip()) < 200])
    
    # Try to find priority
    priority = '中等'
    for pattern in priority_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            priority_match = matches[0].upper()
            if 'AOG' in priority_match or 'URGENT' in priority_match or 'RUSH' in priority_match or '高' in priority_match:
                priority = '高'
            elif 'LOW' in priority_match or '低' in priority_match:
                priority = '低'
            break
    
    # Create requirement entries
    if part_numbers or equipment_names:
        # If we found specific info
        max_entries = max(len(part_numbers), len(equipment_names), 1)
        
        for i in range(min(max_entries, 5)):  # Limit to 5 per email
            pn = part_numbers[i] if i < len(part_numbers) else '待确认'
            name = equipment_names[i] if i < len(equipment_names) else '待确认'
            qty = quantities[i] if i < len(quantities) else '待确认'
            
            # Clean up the description
            desc = content[:800].replace('\n', ' ').replace('\r', ' ').strip()
            # Remove multiple spaces
            desc = re.sub(r'\s+', ' ', desc)
            
            req = {
                '日期': date,
                '发件人邮箱': from_email,
                '邮件主题': subject[:150],
                '器材名称': name,
                '型号/件号 (Part Number)': pn,
                '数量': qty,
                '需求描述': desc,
                '优先级': priority,
                '备注': ''
            }
            requirements.append(req)
    else:
        # General requirement entry for DOMAS emails without specific part info
        desc = content[:800].replace('\n', ' ').replace('\r', ' ').strip()
        desc = re.sub(r'\s+', ' ', desc)
        
        req = {
            '日期': date,
            '发件人邮箱': from_email,
            '邮件主题': subject[:150],
            '器材名称': '待分析',
            '型号/件号 (Part Number)': '待确认',
            '数量': '待确认',
            '需求描述': desc,
            '优先级': priority,
            '备注': '需要人工审核 - DOMAS 相关邮件'
        }
        requirements.append(req)
    
    return requirements

def search_domas_emails(email_config, account_name):
    """Search for DOMAS emails in an account"""
    print(f"\n{'='*60}")
    print(f"Processing account: {account_name} ({email_config['user']})")
    print('='*60)
    
    all_requirements = []
    total_emails_checked = 0
    domas_emails_found = 0
    
    try:
        # Connect to IMAP server with SSL
        print(f"Connecting to {email_config['imap_host']}:{email_config['imap_port']}...")
        
        # Create SSL context that doesn't verify certificates (for enterprise email)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        mail = imaplib.IMAP4_SSL(email_config['imap_host'], email_config['imap_port'], ssl_context=ssl_context)
        
        # Login
        print(f"Logging in as {email_config['user']}...")
        mail.login(email_config['user'], email_config['password'])
        
        # Select inbox
        mail.select('INBOX')
        
        # Search for ALL emails and filter manually
        print("Searching all emails (will filter for DOMAS)...")
        status, messages = mail.search(None, 'ALL')
        
        if status != 'OK':
            print(f"Search failed")
            mail.close()
            mail.logout()
            return []
        
        email_ids = messages[0].split()
        total_emails_checked = len(email_ids)
        print(f"Total emails in inbox: {total_emails_checked}")
        
        # Process each email (limit to most recent 200)
        emails_to_process = min(len(email_ids), 200)
        
        for i, email_id in enumerate(reversed(email_ids[:emails_to_process])):
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
                        
                        # Check if DOMAS-related before processing
                        if 'DOMAS' not in from_email.upper() and 'DOMAS' not in subject.upper():
                            # Still need to check body, but skip if not promising
                            pass
                        
                        # Parse date
                        try:
                            date_obj = email.utils.parsedate_to_datetime(date_str)
                            date = date_obj.strftime('%Y-%m-%d %H:%M')
                        except:
                            date = date_str[:20] if date_str else 'Unknown'
                        
                        # Get body
                        body = get_email_body(msg)
                        
                        # Check if DOMAS-related
                        if 'DOMAS' in from_email.upper() or 'DOMAS' in subject.upper() or 'DOMAS' in body.upper():
                            domas_emails_found += 1
                            print(f"  [{domas_emails_found}] DOMAS email: {subject[:60]}... (From: {from_email[:50]})")
                            
                            # Extract requirements
                            reqs = extract_equipment_info(subject, body, from_email, date)
                            all_requirements.extend(reqs)
                        
            except Exception as e:
                print(f"    Error processing email: {e}")
                continue
        
        mail.close()
        mail.logout()
        print(f"\nSuccessfully processed {account_name}")
        print(f"  Total emails checked: {total_emails_checked}")
        print(f"  DOMAS-related emails: {domas_emails_found}")
        print(f"  Requirements extracted: {len(all_requirements)}")
        
    except Exception as e:
        print(f"Error connecting to {account_name}: {e}")
        import traceback
        traceback.print_exc()
    
    return all_requirements

def main():
    """Main function"""
    print("DOMAS Email Processor v2")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_requirements = []
    stats = {}
    
    # Process each email account
    for account_name, config in EMAIL_CONFIG.items():
        reqs = search_domas_emails(config, account_name)
        all_requirements.extend(reqs)
        stats[account_name] = len(reqs)
        print(f"\nFound {len(reqs)} requirements from {account_name}")
    
    # Create DataFrame
    output_dir = 'C:/Users/Haide/Desktop/OPENCLAW'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'DOMAS_Requirements_Summary.xlsx')
    
    if all_requirements:
        df = pd.DataFrame(all_requirements)
        
        # Save to Excel
        df.to_excel(output_file, index=False, sheet_name='DOMAS Requirements')
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total DOMAS emails processed: {sum(stats.values())}")
        print(f"Total requirements extracted: {len(all_requirements)}")
        print(f"Output file: {output_file}")
        print(f"Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Print breakdown by account
        print("\nBreakdown by account:")
        for account, count in stats.items():
            print(f"  {account}: {count} requirements")
        
    else:
        print("\nNo DOMAS-related requirements found in either account.")
        # Create empty Excel with headers
        df = pd.DataFrame(columns=[
            '日期', '发件人邮箱', '邮件主题', '器材名称', 
            '型号/件号 (Part Number)', '数量', '需求描述', '优先级', '备注'
        ])
        df.to_excel(output_file, index=False, sheet_name='DOMAS Requirements')
        print(f"Created empty summary file: {output_file}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
