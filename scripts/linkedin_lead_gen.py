# /// script
# dependencies = [
#     "linkdapi",
#     "rich",
# ]
# ///

from linkdapi import LinkdAPI
import os
import json
from datetime import datetime

# API Configuration
API_KEY = "li-AqG4H7aQFqrL9OGvesAP1qBWweEyIZ2RxUwQgT73XWlf-XJrXn_19UfArQSZ2OHMjPTJ_A4jIpNYNhhWmtyTbTctTtO82Q"
KEYWORDS = [
    # General Overview
    "Aircraft", "Engine", "Spare parts", "Aviation components",
    # Engines
    "CFM56", "LEAP", "GE90", "GEnx", "Trent", "V2500", "PW1000G", "CF34", "CF6", "GTF",
    # Aircraft
    "A320", "A330", "A350", "B737", "B777", "B787", "A220", "E190",
    # Components & Categories
    "Landing Gear", "APU", "NLG", "MLG", "GTCP", "Avionics", "Engine Parts", "Aircraft Parts",
    "Aviation Material", "Consumables", "Rotables", "Aircraft Tear-down"
]
MODIFIERS = ["sale", "wanted", "available", "sourcing", "RFQ", "stock"]
BUSINESS_TOKENS = ["PN", "Part Number", "S/N", "Serial Number", "Condition", "Price", "USD", "Contact", "@", "WhatsApp", "Email", "Looking for", "In stock"]
EXCLUDE_TOKENS = ["news", "announces", "press release", "summit", "conference", "celebrating", "congratulations", "happy to announce", "hiring", "recruiting", "job", "career", "vacancy", "position", "join our team", "apply now"]

def is_business_lead(content):
    content_lower = content.lower()
    # Check for exclusion
    if any(token in content_lower for token in EXCLUDE_TOKENS):
        return False
    # Check for business intent indicators
    if any(token.lower() in content_lower for token in BUSINESS_TOKENS):
        return True
    return False

def run_search():
    client = LinkdAPI(API_KEY)
    all_leads = []
    
    print(f"[{datetime.now()}] Starting LinkedIn lead generation (Business Only Mode)...")
    
    for kw in KEYWORDS:
        for mod in MODIFIERS:
            query = f"{kw} {mod}"
            print(f"Searching for: {query}")
            try:
                result = client.search_posts(keyword=query)
                
                if result.get('success') and result.get('data', {}).get('posts'):
                    posts = result['data']['posts']
                    for post in posts[:10]: 
                        body = post.get('body', '')
                        if is_business_lead(body):
                            lead = {
                                "keyword": kw,
                                "modifier": mod,
                                "author": post.get('authorName', 'Unknown'),
                                "content": body,
                                "url": post.get('url', 'N/A'),
                                "time": post.get('postedAt', 'Recent')
                            }
                            if not any(l['url'] == lead['url'] for l in all_leads):
                                all_leads.append(lead)
                        else:
                            print(f"Skipping non-business content: {body[:50]}...")
            except Exception as e:
                print(f"Error searching {query}: {e}")

    # Output results for bababot to read
    print(f"\nFOUND_LEADS_START")
    print(json.dumps(all_leads, indent=2))
    print("FOUND_LEADS_END")

if __name__ == "__main__":
    run_search()
