"""
LinkedIn Group Post Collector - Arab Aviation Update
"""

import csv
import os
from datetime import datetime

OUTPUT_FILE = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"

# New post from Arab Aviation group
NEW_POSTS = [
    {
        "post_id": "aa_etienne_a320_supply_20260317",
        "post_date": "2026-03-16",
        "author": "Etienne MANSOUR",
        "author_title": "Sales Director at Go Airparts",
        "company": "Go Airparts",
        "category": "aircraft",
        "business_type": "supply",
        "business_value": "high",
        "content": "Airbus A320. YOM 2011. 7400 & 9800CR on V2500 engines. Fresh C check. Airframe cycles 35K. LeadTime 2 months (C check). Feel free to contact us on Sales@goairparts.com",
        "content_summary": "Selling Airbus A320, YOM 2011, 7400/9800CR on V2500, fresh C check, 35K cycles",
        "contact_info": "Sales@goairparts.com",
        "source_url": "https://www.linkedin.com/groups/4118652/",
        "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "verified": True,
        "notes": "Pinned admin post in Arab Aviation group (35,262 members)"
    }
]

def save_to_csv(posts, file_path):
    fieldnames = [
        "post_id", "post_date", "author", "author_title", "company",
        "category", "business_type", "business_value",
        "content", "content_summary", "contact_info",
        "source_url", "collection_date", "verified", "notes"
    ]
    
    file_exists = os.path.exists(file_path)
    
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for post in posts:
            writer.writerow(post)
    
    print(f"Saved {len(posts)} posts to {file_path}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    save_to_csv(NEW_POSTS, OUTPUT_FILE)
    print(f"Total new posts: {len(NEW_POSTS)}")
