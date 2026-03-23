import pandas as pd
from datetime import datetime
import re

def extract_part_numbers_improved(text, subject):
    """Improved extraction focused on aviation part numbers"""
    all_text = text + " " + subject
    
    # Better patterns for aviation part numbers
    # Common formats: XXXX-XXXXX-XX, XXXXX-XX, XXX-XXXXX-XXX, 1-XXX-XXXX-XX, etc.
    patterns = [
        r'\b\d-\d{4}-\d{3}-\d{4}\b',  # 1-002-0102-2090
        r'\b\d-\d{5}-\d{3}\b',  # 1-002-0102
        r'\b\d{5}-\d{4}\b',  # 50000-0000 or 30-2506-3 (5 chars, hyphen, then rest)
        r'\b\d{2,}-\d{3,}-\d{1,}\b',  # XXX-XXX-XXX
        r'\b\d{4,}-\d{2,}\b',  # XXXXX-XX
        r'\b[A-Z]{1,2}\d{4,}-\d{2,}\b',  # A12345-67
    ]
    
    part_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        part_numbers.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_part_numbers = []
    for item in part_numbers:
        if item not in seen:
            seen.add(item)
            unique_part_numbers.append(item)
    
    # Filter out phone numbers and other false positives
    filtered_part_numbers = []
    for pn in unique_part_numbers:
        # Skip phone-like patterns
        if re.match(r'.*\d{3}-\d{3}-\d{4}.*', pn):  # Phone format
            continue
        # Skip if it's just a phone number component
        if pn == '961-3600':
            continue
        # Skip common words that might match
        if pn.lower() in ['thank', 'you', 'abraham', 'siria', 'please', 'quote']:
            continue
        # Must contain at least one digit
        if not re.search(r'\d', pn):
            continue
        # Must have a reasonable length for a part number
        if len(pn) < 4 or len(pn) > 25:
            continue
        
        filtered_part_numbers.append(pn)
    
    return filtered_part_numbers

def extract_part_number_from_subject(subject):
    """Extract part number specifically from email subject"""
    if not subject:
        return []
    
    # Pattern for part numbers in subject lines (often followed by "Please quote")
    patterns = [
        r'Please quote\s+([\d-]+[A-Za-z]?-\d+)',
        r'quote\s+([\d-]+[A-Za-z]?-\d+)',
        r'RFQ\s+([\d-]+)',
        r'inquiry\s+([\d-]+)',
    ]
    
    part_numbers = []
    for pattern in patterns:
        match = re.search(pattern, subject, re.IGNORECASE)
        if match:
            pn = match.group(1)
            if pn not in part_numbers:
                part_numbers.append(pn)
    
    return part_numbers

def extract_description_from_html(html_text, part_number):
    """Extract description from HTML table structure"""
    if not html_text or not part_number:
        return ""
    
    # Look for table cells containing the part number and description
    # Pattern: <td>part_number</td><td>description</td>
    pattern = rf'<td[^>]*>\s*{re.escape(part_number)}\s*</td>\s*<td[^>]*>([^<]+)</td>'
    match = re.search(pattern, html_text, re.IGNORECASE | re.DOTALL)
    
    if match:
        description = match.group(1).strip()
        # Clean up the description
        description = re.sub(r'\s+', ' ', description)
        return description
    
    return ""

def extract_table_data(text):
    """Extract structured table data from plain text emails"""
    parts = []
    
    # Look for patterns like: "Part Number Description Quantity Cond"
    if "Part Number" in text and "Description" in text:
        lines = text.split('\n')
        in_table = False
        for line in lines:
            if "Part Number" in line and "Description" in line:
                in_table = True
                continue
            if in_table and line.strip():
                # Try to parse the line as table data
                parts_match = re.match(r'^([0-9A-Za-z\-]+)\s+([^\d]+)(\d+)?\s*(\w+)?\s*$', line.strip())
                if parts_match:
                    part_num = parts_match.group(1).strip()
                    description = parts_match.group(2).strip()
                    qty = parts_match.group(3) or ""
                    condition = parts_match.group(4) or ""
                    
                    # Must be a valid part number with digits and hyphens
                    if part_num and len(part_num) > 3 and re.search(r'\d', part_num):
                        parts.append({
                            'part_number': part_num,
                            'description': description,
                            'quantity': qty,
                            'condition': condition
                        })
                elif line.strip():
                    # Alternative parsing for different table format
                    items = re.split(r'\s{2,}', line.strip())
                    if len(items) >= 2 and len(items[0]) > 3 and re.search(r'\d', items[0]):
                        part_num = items[0].strip()
                        description = items[1].strip() if len(items) > 1 else ""
                        qty = items[2].strip() if len(items) > 2 else ""
                        condition = items[3].strip() if len(items) > 3 else ""
                        
                        parts.append({
                            'part_number': part_num,
                            'description': description,
                            'quantity': qty,
                            'condition': condition
                        })
    
    return parts

def process_improved_data():
    # Email data
    email_data = [
      {
        "uid": 1720708294,
        "from": "\"Abraham Siria\" <AbrahamSiria@TurboResources.com>",
        "to": "jianghaide@aeroedgeglobal.com",
        "subject": "Request for Quote",
        "date": "2026-02-27T12:16:05.000Z",
        "text": "From: Turbo Resources Int's\n2615 N. Arizona Ave\nChandler, AZ  85225\nPhone: (480) 961-3600\nhttps://www.TurboResources.com\n\nPlease use this link to quote pricing for the following parts. https://www.TurboResources.com/quoteform.asp?ID=ADM202602270516054208626439\nIf they are no longer available from AeroEdge Global Aviation Services Co. Lt use this link. https://www.TurboResources.com/quoteform.asp?ID=ADM202602270516054208626439&nq=1\n\n\nPart Number          Description          Quantity  Cond\n30-2506-3            ANTICOLLISION LIGHT ASSY Any       \nThank you,\nAbraham Siria\n(480) 961-3600\n\nTo be removed from this mailing list, please visit our website at https://www.TurboResources.com/privacy.asp?address=jianghaide@aeroedgeglobal.com\n\n",
        "html": "<html><head><title>Turbo Resources E-mail</title>\n<style type=\"text/css\">\nbody { font-family: sans-serif; color: #5c5c5c; font-size: 16px; margin: 0px; padding:20px }\ntable { border-collapse:collapse; border:1px solid #cdcccb; background:#ebebea }\nth { background:#63b5e5; color:white; font-weight: normal; }\ntd, th { padding: 7px; font-size: 16px; border:1px solid #63b5e5; font-size: 14px; }\n#messageHeader, #messageBody, #messageFooter { border:1px solid #cdcccb; font-size: 16px; padding: 25px; }\n#messageBody { line-height: 24px; }\n#messageFooter { font-size: 12px; }\na { color: #ea1d2c; }\na:hover { color:#960000; }\n</style></head><body style=\"font-family: sans-serif; color: #5c5c5c; font-size: 16px; margin: 0px; padding: 20px;\">\n<table id=\"message\" style=\"border-collapse: collapse; border: 1px solid #cdcccb; background: #ebebea;\"><tr style=\"height:45px;\"><td id=\"messageHeader\" style=\"padding: 25px; font-size: 16px; border: 1px solid #cdcccb;\"><img id=\"companyLogo\" src=\"http://www.TurboResources.com/images/turbo-logo-email.png\" height=\"45\"></td></tr><tr><td id=\"messageBody\" valign=\"top\" style=\"padding: 25px; font-size: 16px; border: 1px solid #cdcccb; line-height: 24px;\">\nPlease <a href=\"https://www.TurboResources.com/quoteform.asp?ID=ADM202602270516054208626439\">click here to quote pricing</a> for the following parts.<br />\nIf they are no longer available from AeroEdge Global Aviation Services Co. Lt, <a href=\"https://www.TurboResources.com/quoteform.asp?ID=ADM202602270516054208626439&nq=1\">click here to \"no quote\"</a>.\n<br /><br />\n<table border=1 cellpadding=1 cellspacing=1><tr><th nowrap align=center>Part Number</th><th nowrap align=center>Description</th><th nowrap align=center>Quantity</th><th nowrap align=center>Condition</th></tr>\n<tr><td nowrap align=left>30-2506-3</td><td nowrap align=left>ANTICOLLISION LIGHT ASSY</td><td nowrap align=right>Any</td><td nowrap align=center>Any</td></tr>\n</table>\n<br />Thank you,<br />\nAbraham Siria<br />\n(480) 961-3600<br />\n<br /><font face=Tahoma size=2>To be removed from this mailing list, please visit our website at <a href=\"https://www.TurboResources.com/privacy.asp?address=jianghaide@aeroedgeglobal.com\">https://www.TurboResources.com/privacy.asp?address=jianghaide@aeroedgeglobal.com</a></font><br />\n</td></tr><tr><td id=\"messageFooter\" align=\"center\" style=\"padding: 25px; font-size: 12px; border: 1px solid #cdcccb;\">www.TurboResources.com &bull; phone: +1 480 961 3600 </td></tr></table></body></html>\n",
        "snippet": "From: Turbo Resources Int's\n2615 N. Arizona Ave\nChandler, AZ  85225\nPhone: (480) 961-3600\nhttps://www.TurboResources.com\n\nPlease use this link to quote pricing for the following parts. https://www.Tur",
        "attachments": [],
        "flags": ["\\Recent"]
      },
      {
        "uid": 1720708293,
        "from": "\"Abraham Siria\" <AbrahamSiria@TurboResources.com>",
        "to": "jianghaide@aeroedgeglobal.com",
        "subject": "Please quote 1-002-0102-2090",
        "date": "2026-02-27T09:48:55.000Z",
        "text": "\n\nAbraham Siria\nBusiness Development & Sales Director - Africa\nMain: (480) 961-3600\nMobile:+254712964510\nhttp://www.TurboResources.com<http://www.turboresources.com/>\nAbrahamSiria@TurboResources.com<mailto:AbrahamSiria@TurboResources.com>\n\n[http://www.turboresources.com/images/turbo-logo-email-40-years.png]\n\n\n\n\n\n\n",
        "html": "<html xmlns:v=\"urn:schemas-microsoft-com:vml\" xmlns:o=\"urn:schemas-microsoft-com:office:office\" xmlns:w=\"urn:schemas-microsoft-com:office:word\" xmlns:m=\"http://schemas.microsoft.com/office/2004/12/omml\" xmlns=\"http://www.w3.org/TR/REC-html40\">\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=us-ascii\">\n<meta name=\"Generator\" content=\"Microsoft Word 15 (filtered medium)\">\n<!--[if !mso]><style>v\\\\:* {behavior:url(#default#VML);}\no\\\\:* {behavior:url(#default#VML);}\nw\\\\:* {behavior:url(#default#VML);}\n.shape {behavior:url(#default#VML);}\n</style><![endif]--><style><!--\n/* Font Definitions */\n@font-face\n\t{font-family:\"Cambria Math\";\n\tpanose-1:2 4 5 3 5 4 6 3 2 4;}\n@font-face\n\t{font-family:Aptos;}\n/* Style Definitions */\np.MsoNormal, li.MsoNormal, div.MsoNormal\n\t{margin:0in;\n\tfont-size:12.0pt;\n\tfont-family:\"Aptos\",sans-serif;\n\tmso-ligatures:standardcontextual;}\nspan.EmailStyle17\n\t{mso-style-type:personal-compose;\n\tfont-family:\"Aptos\",sans-serif;\n\tcolor:windowtext;}\n.MsoChpDefault\n\t{mso-style-type:export-only;}\n@page WordSection1\n\t{size:8.5in 11.0in;\n\tmargin:1.0in 1.0in 1.0in 1.0in;}\ndiv.WordSection1\n\t{page:WordSection1;}\n--></style>\n</head>\n<body lang=\"EN-US\" link=\"#467886\" vlink=\"#96607D\" style=\"word-wrap:break-word\">\n<div class=\"WordSection1\">\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<table class=\"MsoNormalTable\" border=\"0\" cellspacing=\"3\" cellpadding=\"0\">\n<tbody>\n<tr>\n<td style=\"padding:.75pt .75pt .75pt .75pt\">\n<div style=\"margin-left:5.25pt;margin-top:5.25pt;margin-right:5.25pt;margin-bottom:5.25pt;xline-height:110%\">\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><b><u><span style=\"font-size:10.5pt;font-family:&quot;Arial&quot;,sans-serif;color:black\">Abraham Siria<o:p></o:p></span></u></b></p>\n<div style=\"margin-top:3.0pt\">\n<p class=\"MsoNormal\" align=\"right\" style=\"mso-margin-top-alt:5.25pt;margin-right:15.75pt;margin-bottom:5.25pt;margin-left:46.5pt;text-align:right\">\n<span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Business Development & Sales Director - Africa<o:p></o:p></span></p>\n</div>\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Main: (480) 961-3600<o:p></o:p></span></p>\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Mobile:+254712964510<br>\n<a href=\"http://www.turboresources.com/\"><span style=\"color:#5A5A5A\">http://www.TurboResources.com</span></a><br>\n<a href=\"mailto:AbrahamSiria@TurboResources.com\"><span style=\"color:#5A5A5A\">AbrahamSiria@TurboResources.com</span></a><o:p></o:p></span></p>\n</div>\n</td>\n<td width=\"1\" style=\"width:.75pt;border:none;border-right:solid black 1.0pt;padding:.75pt .75pt .75pt .75pt\">\n<p class=\"MsoNormal\">&nbsp;<o:p></o:p></p>\n</td>\n<td style=\"padding:.75pt .75pt .75pt .75pt\">\n<div style=\"margin-left:5.25pt;margin-top:5.25pt;margin-right:5.25pt;margin-bottom:5.25pt\">\n<p class=\"MsoNormal\"><img border=\"0\" width=\"340\" height=\"68\" style=\"width:3.5416in;height:.7083in\" id=\"_x0000_i1025\" src=\"http://www.turboresources.com/images/turbo-logo-email-40-years.png\"><o:p></o:p></p>\n</div>\n</td>\n</tr>\n</tbody>\n</table>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><span style=\"mso-ligatures:none\"><o:p>&nbsp;</o:p></span></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><span style=\"mso-ligatures:none\"><o:p>&nbsp;</o:p></span></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n</div>\n</body>\n</html>\n",
        "snippet": "\n\nAbraham Siria\nBusiness Development & Sales Director - Africa\nMain: (480) 961-3600\nMobile:+254712964510\nhttp://www.TurboResources.com<http://www.turboresources.com/>\nAbrahamSiria@TurboResources.com<m",
        "attachments": [],
        "flags": ["\\Recent"]
      },
      {
        "uid": 1720708292,
        "from": "\"Abraham Siria\" <AbrahamSiria@TurboResources.com>",
        "to": "jianghaide@aeroedgeglobal.com",
        "subject": "Please quote 20220-0101",
        "date": "2026-02-27T09:48:39.000Z",
        "text": "\n\nAbraham Siria\nBusiness Development & Sales Director - Africa\nMain: (480) 961-3600\nMobile:+254712964510\nhttp://www.TurboResources.com<http://www.turboresources.com/>\nAbrahamSiria@TurboResources.com<mailto:AbrahamSiria@TurboResources.com>\n\n[http://www.turboresources.com/images/turbo-logo-email-40-years.png]\n\n\n\n\n\n\n",
        "html": "<html xmlns:v=\"urn:schemas-microsoft-com:vml\" xmlns:o=\"urn:schemas-microsoft-com:office:office\" xmlns:w=\"urn:schemas-microsoft-com:office:word\" xmlns:m=\"http://schemas.microsoft.com/office/2004/12/omml\" xmlns=\"http://www.w3.org/TR/REC-html40\">\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=us-ascii\">\n<meta name=\"Generator\" content=\"Microsoft Word 15 (filtered medium)\">\n<!--[if !mso]><style>v\\\\:* {behavior:url(#default#VML);}\no\\\\:* {behavior:url(#default#VML);}\nw\\\\:* {behavior:url(#default#VML);}\n.shape {behavior:url(#default#VML);}\n</style><![endif]--><style><!--\n/* Font Definitions */\n@font-face\n\t{font-family:\"Cambria Math\";\n\tpanose-1:2 4 5 3 5 4 6 3 2 4;}\n@font-face\n\t{font-family:Aptos;}\n/* Style Definitions */\np.MsoNormal, li.MsoNormal, div.MsoNormal\n\t{margin:0in;\n\tfont-size:12.0pt;\n\tfont-family:\"Aptos\",sans-serif;\n\tmso-ligatures:standardcontextual;}\nspan.EmailStyle17\n\t{mso-style-type:personal-compose;\n\tfont-family:\"Aptos\",sans-serif;\n\tcolor:windowtext;}\n.MsoChpDefault\n\t{mso-style-type:export-only;}\n@page WordSection1\n\t{size:8.5in 11.0in;\n\tmargin:1.0in 1.0in 1.0in 1.0in;}\ndiv.WordSection1\n\t{page:WordSection1;}\n--></style>\n</head>\n<body lang=\"EN-US\" link=\"#467886\" vlink=\"#96607D\" style=\"word-wrap:break-word\">\n<div class=\"WordSection1\">\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<table class=\"MsoNormalTable\" border=\"0\" cellspacing=\"3\" cellpadding=\"0\">\n<tbody>\n<tr>\n<td style=\"padding:.75pt .75pt .75pt .75pt\">\n<div style=\"margin-left:5.25pt;margin-top:5.25pt;margin-right:5.25pt;margin-bottom:5.25pt;xline-height:110%\">\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><b><u><span style=\"font-size:10.5pt;font-family:&quot;Arial&quot;,sans-serif;color:black\">Abraham Siria<o:p></o:p></span></u></b></p>\n<div style=\"margin-top:3.0pt\">\n<p class=\"MsoNormal\" align=\"right\" style=\"mso-margin-top-alt:5.25pt;margin-right:15.75pt;margin-bottom:5.25pt;margin-left:46.5pt;text-align:right\">\n<span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Business Development & Sales Director - Africa<o:p></o:p></span></p>\n</div>\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Main: (480) 961-3600<o:p></o:p></span></p>\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Mobile:+254712964510<br>\n<a href=\"http://www.turboresources.com/\"><span style=\"color:#5A5A5A\">http://www.TurboResources.com</span></a><br>\n<a href=\"mailto:AbrahamSiria@TurboResources.com\"><span style=\"color:#5A5A5A\">AbrahamSiria@TurboResources.com</span></a><o:p></o:p></span></p>\n</div>\n</td>\n<td width=\"1\" style=\"width:.75pt;border:none;border-right:solid black 1.0pt;padding:.75pt .75pt .75pt .75pt\">\n<p class=\"MsoNormal\">&nbsp;<o:p></o:p></p>\n</td>\n<td style=\"padding:.75pt .75pt .75pt .75pt\">\n<div style=\"margin-left:5.25pt;margin-top:5.25pt;margin-right:5.25pt;margin-bottom:5.25pt\">\n<p class=\"MsoNormal\"><img border=\"0\" width=\"340\" height=\"68\" style=\"width:3.5416in;height:.7083in\" id=\"_x0000_i1025\" src=\"http://www.turboresources.com/images/turbo-logo-email-40-years.png\"><o:p></o:p></p>\n</div>\n</td>\n</tr>\n</tbody>\n</table>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><span style=\"mso-ligatures:none\"><o:p>&nbsp;</o:p></span></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><span style=\"mso-ligatures:none\"><o:p>&nbsp;</o:p></span></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n</div>\n</body>\n</html>\n",
        "snippet": "\n\nAbraham Siria\nBusiness Development & Sales Director - Africa\nMain: (480) 961-3600\nMobile:+254712964510\nhttp://www.TurboResources.com<http://www.turboresources.com/>\nAbrahamSiria@TurboResources.com<m",
        "attachments": [],
        "flags": ["\\Recent"]
      },
      {
        "uid": 1720708291,
        "from": "\"Abraham Siria\" <AbrahamSiria@TurboResources.com>",
        "to": "jianghaide@aeroedgeglobal.com",
        "subject": "Please quote 5000-1-01A-2396",
        "date": "2026-02-27T09:48:29.000Z",
        "text": "\n\nAbraham Siria\nBusiness Development & Sales Director - Africa\nMain: (480) 961-3600\nMobile:+254712964510\nhttp://www.TurboResources.com<http://www.turboresources.com/>\nAbrahamSiria@TurboResources.com<mailto:AbrahamSiria@TurboResources.com>\n\n[http://www.turboresources.com/images/turbo-logo-email-40-years.png]\n\n\n\n\n\n\n",
        "html": "<html xmlns:v=\"urn:schemas-microsoft-com:vml\" xmlns:o=\"urn:schemas-microsoft-com:office:office\" xmlns:w=\"urn:schemas-microsoft-com:office:word\" xmlns:m=\"http://schemas.microsoft.com/office/2004/12/omml\" xmlns=\"http://www.w3.org/TR/REC-html40\">\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=us-ascii\">\n<meta name=\"Generator\" content=\"Microsoft Word 15 (filtered medium)\">\n<!--[if !mso]><style>v\\\\:* {behavior:url(#default#VML);}\no\\\\:* {behavior:url(#default#VML);}\nw\\\\:* {behavior:url(#default#VML);}\n.shape {behavior:url(#default#VML);}\n</style><![endif]--><style><!--\n/* Font Definitions */\n@font-face\n\t{font-family:\"Cambria Math\";\n\tpanose-1:2 4 5 3 5 4 6 3 2 4;}\n@font-face\n\t{font-family:Aptos;}\n/* Style Definitions */\np.MsoNormal, li.MsoNormal, div.MsoNormal\n\t{margin:0in;\n\tfont-size:12.0pt;\n\tfont-family:\"Aptos\",sans-serif;\n\tmso-ligatures:standardcontextual;}\nspan.EmailStyle17\n\t{mso-style-type:personal-compose;\n\tfont-family:\"Aptos\",sans-serif;\n\tcolor:windowtext;}\n.MsoChpDefault\n\t{mso-style-type:export-only;}\n@page WordSection1\n\t{size:8.5in 11.0in;\n\tmargin:1.0in 1.0in 1.0in 1.0in;}\ndiv.WordSection1\n\t{page:WordSection1;}\n--></style>\n</head>\n<body lang=\"EN-US\" link=\"#467886\" vlink=\"#96607D\" style=\"word-wrap:break-word\">\n<div class=\"WordSection1\">\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<table class=\"MsoNormalTable\" border=\"0\" cellspacing=\"3\" cellpadding=\"0\">\n<tbody>\n<tr>\n<td style=\"padding:.75pt .75pt .75pt .75pt\">\n<div style=\"margin-left:5.25pt;margin-top:5.25pt;margin-right:5.25pt;margin-bottom:5.25pt;xline-height:110%\">\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><b><u><span style=\"font-size:10.5pt;font-family:&quot;Arial&quot;,sans-serif;color:black\">Abraham Siria<o:p></o:p></span></u></b></p>\n<div style=\"margin-top:3.0pt\">\n<p class=\"MsoNormal\" align=\"right\" style=\"mso-margin-top-alt:5.25pt;margin-right:15.75pt;margin-bottom:5.25pt;margin-left:46.5pt;text-align:right\">\n<span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Business Development & Sales Director - Africa<o:p></o:p></span></p>\n</div>\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Main: (480) 961-3600<o:p></o:p></span></p>\n<p class=\"MsoNormal\" align=\"right\" style=\"text-align:right\"><span style=\"font-size:9.5pt;font-family:&quot;Arial&quot;,sans-serif;color:#5A5A5A\">Mobile:+254712964510<br>\n<a href=\"http://www.turboresources.com/\"><span style=\"color:#5A5A5A\">http://www.TurboResources.com</span></a><br>\n<a href=\"mailto:AbrahamSiria@TurboResources.com\"><span style=\"color:#5A5A5A\">AbrahamSiria@TurboResources.com</span></a><o:p></o:p></span></p>\n</div>\n</td>\n<td width=\"1\" style=\"width:.75pt;border:none;border-right:solid black 1.0pt;padding:.75pt .75pt .75pt .75pt\">\n<p class=\"MsoNormal\">&nbsp;<o:p></o:p></p>\n</td>\n<td style=\"padding:.75pt .75pt .75pt .75pt\">\n<div style=\"margin-left:5.25pt;margin-top:5.25pt;margin-right:5.25pt;margin-bottom:5.25pt\">\n<p class=\"MsoNormal\"><img border=\"0\" width=\"340\" height=\"68\" style=\"width:3.5416in;height:.7083in\" id=\"_x0000_i1025\" src=\"http://www.turboresources.com/images/turbo-logo-email-40-years.png\"><o:p></o:p></p>\n</div>\n</td>\n</tr>\n</tbody>\n</table>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><span style=\"mso-ligatures:none\"><o:p>&nbsp;</o:p></span></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><span style=\"mso-ligatures:none\"><o:p>&nbsp;</o:p></span></p>\n<p class=\"MsoNormal\" style=\"mso-margin-top-alt:auto;mso-margin-bottom-alt:auto\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n<p class=\"MsoNormal\"><o:p>&nbsp;</o:p></p>\n</div>\n</body>\n</html>\n",
        "snippet": "\n\nAbraham Siria\nBusiness Development & Sales Director - Africa\nMain: (480) 961-3600\nMobile:+254712964510\nhttp://www.TurboResources.com<http://www.turboresources.com/>\nAbrahamSiria@TurboResources.com<m",
        "attachments": [],
        "flags": ["\\Recent"]
      }
    ]
    
    # Prepare the dataframe
    rows = []
    count = 1
    
    for email in email_data:
        date_str = email.get("date", "")
        subject = email.get("subject", "")
        text = email.get("text", "")
        html = email.get("html", "")
        uid = email.get("uid", "")
        
        # Parse date
        if date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            formatted_date = ""
        
        # Extract part numbers from subject first
        subject_part_numbers = extract_part_number_from_subject(subject)
        
        # Extract table data if present
        table_parts = extract_table_data(text)
        
        # If we found structured table data, use it
        if table_parts:
            for part_data in table_parts:
                part_num = part_data['part_number']
                description = part_data['description']
                qty = part_data['quantity']
                condition = part_data['condition']
                
                row = {
                    "序号": count,
                    "邮件日期": formatted_date,
                    "邮件主题": subject,
                    "件号 (Part Number)": part_num,
                    "描述 (Description)": description,
                    "数量 (Quantity)": qty,
                    "Condition (NE/SV/OH 等)": condition,
                    "目标价格 (Target Price)": "",
                    "交期要求 (Delivery)": "",
                    "备注": "",
                    "原始邮件 ID": uid
                }
                rows.append(row)
                count += 1
        
        # If we found part numbers in subject but not in table
        elif subject_part_numbers:
            for part_num in subject_part_numbers:
                row = {
                    "序号": count,
                    "邮件日期": formatted_date,
                    "邮件主题": subject,
                    "件号 (Part Number)": part_num,
                    "描述 (Description)": "",
                    "数量 (Quantity)": "",
                    "Condition (NE/SV/OH 等)": "",
                    "目标价格 (Target Price)": "",
                    "交期要求 (Delivery)": "",
                    "备注": "Part number from subject line only",
                    "原始邮件 ID": uid
                }
                rows.append(row)
                count += 1
        
        # Try improved extraction from content
        else:
            improved_part_numbers = extract_part_numbers_improved(text, subject)
            
            if improved_part_numbers:
                for part_num in improved_part_numbers:
                    description = extract_description_from_html(html, part_num)
                    
                    row = {
                        "序号": count,
                        "邮件日期": formatted_date,
                        "邮件主题": subject,
                        "件号 (Part Number)": part_num,
                        "描述 (Description)": description,
                        "数量 (Quantity)": "",
                        "Condition (NE/SV/OH 等)": "",
                        "目标价格 (Target Price)": "",
                        "交期要求 (Delivery)": "",
                        "备注": "Extracted from email content",
                        "原始邮件 ID": uid
                    }
                    rows.append(row)
                    count += 1
            
            else:
                # No part numbers found
                row = {
                    "序号": count,
                    "邮件日期": formatted_date,
                    "邮件主题": subject,
                    "件号 (Part Number)": "",
                    "描述 (Description)": "",
                    "数量 (Quantity)": "",
                    "Condition (NE/SV/OH 等)": "",
                    "目标价格 (Target Price)": "",
                    "交期要求 (Delivery)": "",
                    "备注": "No part numbers found in this email",
                    "原始邮件 ID": uid
                }
                rows.append(row)
                count += 1
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Save to Excel
    output_file = "C:/Users/Haide/Desktop/OPENCLAW/TurboResources_Requirements_2026.xlsx"
    
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    df.to_excel(output_file, index=False)
    print(f"Excel file saved to: {output_file}")
    print(f"Total emails processed: {len(email_data)}")
    print(f"Total part numbers extracted: {len([row for row in rows if row['件号 (Part Number)']])}")
    
    return df

if __name__ == "__main__":
    df = process_improved_data()
    print("\nExtracted Data:")
    print(df[['序号', '邮件日期', '邮件主题', '件号 (Part Number)', '描述 (Description)', '数量 (Quantity)', 'Condition (NE/SV/OH 等)']].to_string(index=False))