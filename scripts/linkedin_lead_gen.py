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
KEYWORDS = ["CFM56-7B", "LEAP engine", "GE90 engine"]
MODIFIERS = ["sale", "wanted", "available", "sourcing"]

def run_search():
    client = LinkdAPI(API_KEY)
    all_leads = []
    
    print(f"[{datetime.now()}] Starting LinkedIn lead generation...")
    
    for kw in KEYWORDS:
        for mod in MODIFIERS:
            query = f"{kw} {mod}"
            print(f"Searching for: {query}")
            try:
                # Search for posts from the last 24 hours (if supported) or just top results
                result = client.search_posts(keyword=query)
                
                if result.get('success') and result.get('data', {}).get('posts'):
                    posts = result['data']['posts']
                    for post in posts[:5]: # Top 5 per sub-query
                        lead = {
                            "keyword": kw,
                            "modifier": mod,
                            "author": post.get('authorName', 'Unknown'),
                            "content": post.get('body', ''),
                            "url": post.get('url', 'N/A'),
                            "time": post.get('postedAt', 'Recent')
                        }
                        # Deduplicate by URL
                        if not any(l['url'] == lead['url'] for l in all_leads):
                            all_leads.append(lead)
            except Exception as e:
                print(f"Error searching {query}: {e}")

    # Output results for bababot to read
    print(f"\nFOUND_LEADS_START")
    print(json.dumps(all_leads, indent=2))
    print("FOUND_LEADS_END")

if __name__ == "__main__":
    run_search()
