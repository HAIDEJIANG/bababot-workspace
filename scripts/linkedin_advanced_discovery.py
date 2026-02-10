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
import time
import sys

# API Configuration
# LinkdAPI KEY from TOOLS.md
API_KEY = "li-AqG4H7aQFqrL9OGvesAP1qBWweEyIZ2RxUwQgT73XWlf-XJrXn_19UfArQSZ2OHMjPTJ_A4jIpNYNhhWmtyTbTctTtO82Q"

# Expanded Categories to cover all aviation assets
CATEGORIES = {
    "Aircraft": ["Airbus A320", "Airbus A321", "Airbus A319", "Boeing 737", "A330", "B777", "ERJ", "CRJ", "aircraft for sale", "aircraft wanted"],
    "Engines": ["CFM56-7B", "CFM56-5B", "LEAP-1A", "LEAP-1B", "GE90", "Trent 700", "V2500", "PW4000", "engine sale", "engine availability"],
    "Landing Gear": ["Landing Gear", "L/G availability", "LG", "shipset", "737 Landing Gear", "A320 Landing Gear"],
    "APU": ["GTCP131-9A", "GTCP131-9B", "GTCP331-350", "GTCP331-500", "APU sale", "APU wanted"],
    "Aviation Material": ["Aviation parts", "Airframe parts", "avionics", "rotable", "consignment", "surplus inventory"],
    "MRO Services": ["component repair", "engine repair", "engine overhaul", "aircraft maintenance", "heavy maintenance", "C-check", "D-check", "base maintenance", "line maintenance"]
}

# High-intent modifiers including "PN" and "PART NUMBER"
INTENT_MODIFIERS = [
    "for sale", "available now", "wanted", "looking for", 
    "RFQ", "procurement", "PN", "PART NUMBER", "teardown", "package for sale"
]

def run_search():
    client = LinkdAPI(API_KEY)
    all_leads = []
    consecutive_failures = 0
    MAX_FAILURES = 3
    
    print(f"[{datetime.now()}] Starting Advanced LinkedIn Aviation Discovery...")
    
    for category, keywords in CATEGORIES.items():
        print(f"\n--- Category: {category} ---")
        for kw in keywords:
            for mod in INTENT_MODIFIERS:
                query = f"\"{kw}\" {mod}"
                print(f"Searching for: {query}")
                try:
                    # Using sort_by='date' for newest leads
                    result = client.search_posts(keyword=query, sort_by='date')
                    
                    if result.get('success'):
                        consecutive_failures = 0 # Reset counter on success
                        posts = result.get('data', {}).get('posts', [])
                        for post in posts[:3]:
                            lead = {
                                "category": category,
                                "keyword": kw,
                                "modifier": mod,
                                "author": post.get('authorName', 'Unknown'),
                                "company": post.get('authorCompany', 'N/A'),
                                "content": post.get('body', ''),
                                "url": post.get('url', 'N/A'),
                                "time": post.get('postedAt', 'Recent')
                            }
                            if not any(l['url'] == lead['url'] for l in all_leads):
                                all_leads.append(lead)
                                print(f"  [+] New Lead found from {lead['author']}")
                    else:
                        print(f"  [!] API returned success=False for {query}")
                        consecutive_failures += 1
                        
                except Exception as e:
                    print(f"  [!] Error searching {query}: {e}")
                    consecutive_failures += 1
                
                # Check for termination condition (Three-strike rule)
                if consecutive_failures >= MAX_FAILURES:
                    print(f"\n[CRITICAL] LinkdAPI is unavailable (3 consecutive failures). Terminating task.")
                    print(f"FOUND_LEADS_START\n{json.dumps(all_leads, indent=2)}\nFOUND_LEADS_END")
                    sys.exit(1)
                
                time.sleep(1) # Rate limit mitigation

    print(f"\nFOUND_LEADS_START")
    print(json.dumps(all_leads, indent=2))
    print("FOUND_LEADS_END")

if __name__ == "__main__":
    run_search()
