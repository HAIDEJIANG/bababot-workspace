"""
LinkedIn Group Post Collector - Data Update
Collects aviation business posts from LinkedIn groups and saves to CSV
"""

import csv
import os
from datetime import datetime

# Output file path
OUTPUT_FILE = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"

# New posts collected from browser session (2026-03-17)
NEW_POSTS = [
    {
        "post_id": "atc_ezzine_a320_demand_20260317",
        "post_date": "2026-03-15",
        "author": "Ezzine Atef",
        "author_title": "Senior Aviation Business Development Consultant Aircraft & Engine Sales",
        "company": "",
        "category": "aircraft",
        "business_type": "demand",
        "business_value": "high",
        "content": "Looking for 2 × Airbus A320ceo. Engine: CFM56 preferred / IAE V2500 acceptable. YOM: 2016+. Condition: Airworthy. Budget: ~ $30M. Buyer position: POF • KYC • Exclusive Mandate. All on hand. Please contact via DM if available.",
        "content_summary": "Looking for 2 Airbus A320ceo aircraft, 2016+, airworthy, budget ~$30M",
        "contact_info": "DM on LinkedIn",
        "source_url": "https://www.linkedin.com/groups/2205442/",
        "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "verified": True,
        "notes": "Pinned post in Aviation Trading Circle group (126,239 members)"
    },
    {
        "post_id": "basp_pascal_cfm56_demand_20260317",
        "post_date": "2026-03-14",
        "author": "Pascal Picard",
        "author_title": "EASA Part-66 Cat B1.1 - Boeing 737NG/BBJ - Airbus A340 | Founder & CEO chez AVIDEX Expert & Value",
        "company": "AVIDEX Expert & Value",
        "category": "engine",
        "business_type": "demand",
        "business_value": "high",
        "content": "Dear network, ‼️ ENGINES REQUIREMENT‼️ I currently have a request from one of my client who is looking to source 2 CFM56-7B27/B3 engines, ideally with approximately CR : 2000 / 1500. Please drop me a message. contact@avidex.aero",
        "content_summary": "Looking to source 2 CFM56-7B27/B3 engines, CR ~2000/1500",
        "contact_info": "contact@avidex.aero",
        "source_url": "https://www.linkedin.com/groups/3926957/",
        "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "verified": True,
        "notes": "Buyers and Sellers of Aircraft Spare Parts group (6,885 members)"
    },
    {
        "post_id": "basp_flye_b737_supply_20260317",
        "post_date": "2026-03-11",
        "author": "Mariolise (Lisa) Williams",
        "author_title": "Founder & Managing Director @ FLYE Aviation PTY LTD | Aircraft Sales, Leasing, Charters",
        "company": "FLYE Aviation PTY LTD",
        "category": "aircraft",
        "business_type": "supply",
        "business_value": "high",
        "content": "✈️ FLYE Aviation is pleased to present select Boeing 737-300 opportunities currently available for qualified operators. Available Inventory: • B737-300 Passenger Aircraft ×2 • B737-300 Freighter Aircraft ×2. Aircraft are available for immediate commercial discussions with qualified buyers. Further technical specifications, maintenance status, and commercial terms will be provided upon receipt of buyer qualification. Serious inquiries only. No Chains! 📩 Contact: sales@flyeaviation.co.za; mariolise@flyeaviation.co.za",
        "content_summary": "Selling B737-300 aircraft: 2 passenger + 2 freighter units available",
        "contact_info": "sales@flyeaviation.co.za; mariolise@flyeaviation.co.za",
        "source_url": "https://www.linkedin.com/groups/3926957/",
        "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "verified": True,
        "notes": "Buyers and Sellers of Aircraft Spare Parts group (6,885 members)"
    }
]

def save_to_csv(posts, file_path):
    """Save posts to CSV file, appending if exists"""
    fieldnames = [
        "post_id", "post_date", "author", "author_title", "company",
        "category", "business_type", "business_value",
        "content", "content_summary", "contact_info",
        "source_url", "collection_date", "verified", "notes"
    ]
    
    # Check if file exists
    file_exists = os.path.exists(file_path)
    
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for post in posts:
            writer.writerow(post)
    
    print(f"Saved {len(posts)} posts to {file_path}")

if __name__ == "__main__":
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save collected posts
    save_to_csv(NEW_POSTS, OUTPUT_FILE)
    
    print("\n=== Collection Summary ===")
    print(f"Total new posts collected: {len(NEW_POSTS)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("\nPosts collected:")
    for post in NEW_POSTS:
        print(f"  - {post['post_id']}: {post['author']} - {post['business_type']} {post['category']} ({post['business_value']})")
    
    print("\n=== Target Groups Status ===")
    groups_visited = [
        "Aviation Trading Circle (2205442) - ✓ Visited",
        "Buyers and Sellers of Aircraft Spare Parts (3926957) - ✓ Visited",
        "Arab Aviation (4118652) - ⏳ Pending",
        "Aircraft Parts & Engine Traders (13059127) - ⏳ Pending",
        "AIRCRAFT & ENGINE TRADERS PLATFORM (3319971) - ⏳ Pending",
        "Aircraft Engine Exchange (3699087) - ⏳ Pending",
        "Wet Lease & ACMI (9275338) - ⏳ Pending"
    ]
    for g in groups_visited:
        print(f"  {g}")
