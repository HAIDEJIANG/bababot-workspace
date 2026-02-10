# /// script
# dependencies = ["linkdapi"]
# ///
from linkdapi import LinkdAPI
import time
import json

api_key = "li-AqG4H7aQFqrL9OGvesAP1qBWweEyIZ2RxUwQgT73XWlf-XJrXn_19UfArQSZ2OHMjPTJ_A4jIpNYNhhWmtyTbTctTtO82Q"
client = LinkdAPI(api_key)

targets = [
    {"name": "Nick Chambers", "id": "nick-chambers-10ab4628"},
    {"name": "Connor Jacobs", "id": "connor-jacobs-b59435160"},
]

# Specific search for the others
search_queries = [
    "Megan McClure VSE Aviation",
    "Brian Jones Sky Air Supply",
]

results = []

for target in targets:
    print(f"Fetching full profile for {target['name']}...")
    res = client.get_full_profile(username=target['id'])
    if res.get('success'):
        results.append(res['data'])
    else:
        print(f"Failed for {target['name']}: {res.get('message')}")
    time.sleep(10)

for query in search_queries:
    print(f"Searching for {query}...")
    res = client.search_people(keyword=query)
    if res.get('success') and res.get('data', {}).get('people'):
        person = res['data']['people'][0]
        username = person.get('username') or person.get('public_id')
        if not username and person.get('url'):
            username = person['url'].split('/in/')[-1].strip('/')
        
        if username:
            print(f"Found {query} -> {username}. Fetching profile...")
            time.sleep(10)
            prof = client.get_full_profile(username=username)
            if prof.get('success'):
                results.append(prof['data'])
    time.sleep(10)

with open("final_linkedin_results.json", "w") as f:
    json.dump(results, f, indent=2)
