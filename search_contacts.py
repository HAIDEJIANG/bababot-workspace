# /// script
# dependencies = [
#     "linkdapi",
# ]
# ///

from linkdapi import LinkdAPI
import os
import json

api_key = "li-AqG4H7aQFqrL9OGvesAP1qBWweEyIZ2RxUwQgT73XWlf-XJrXn_19UfArQSZ2OHMjPTJ_A4jIpNYNhhWmtyTbTctTtO82Q"
client = LinkdAPI(api_key)

contacts = [
    {"name": "Nick Chambers", "company": "STS Component Solutions"},
    {"name": "Megan McClure", "company": "VSE Aviation"},
    {"name": "Brian Jones", "company": "Sky Air Supply"},
    {"name": "Greg Macleod", "company": "STS Engine Services"},
    {"name": "Connor Jacobs", "company": "Jacaero"},
]

results = []

import time

for contact in contacts:
    print(f"Searching for {contact['name']} at {contact['company']}...")
    try:
        search_result = client.search_people(keyword=f"{contact['name']} {contact['company']}")
        
        # print(f"Search Result for {contact['name']}: {json.dumps(search_result, indent=2)}")

        if search_result.get('success') and search_result.get('data', {}).get('people'):
            people = search_result['data']['people']
            person = people[0]
            
            # Extract username from URL if not present
            username = person.get('username') or person.get('public_id')
            if not username and person.get('url'):
                username = person['url'].split('/in/')[-1].strip('/')
            
            urn = person.get('urn')
            print(f"Found person: {person.get('fullName')} with identifier: {username or urn}")
            
            time.sleep(2) # Avoid rate limit
            
            print(f"Fetching full profile...")
            profile = client.get_full_profile(username=username, urn=urn)
            if profile.get('success'):
                results.append(profile['data'])
            else:
                print(f"Failed to fetch profile: {profile.get('message')}")
        else:
            print(f"Search failed or no results for {contact['name']}")
    except Exception as e:
        print(f"Error searching for {contact['name']}: {e}")
    
    time.sleep(5) # Wait 5 seconds between contacts

with open("linkedin_results.json", "w") as f:
    json.dump(results, f, indent=2)
