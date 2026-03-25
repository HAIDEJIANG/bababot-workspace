import csv
import os
from datetime import datetime

csv_path = r'C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv'

# Read existing to check for duplicates
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    existing_rows = list(reader)

# Get existing post_ids to avoid duplicates
existing_ids = set(r.get('post_id', '') for r in existing_rows)

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
batch_id = f'batch_{datetime.now().strftime("%Y%m%d_%H%M")}'
today_str = datetime.now().strftime('%Y%m%d')

# New posts from feed scrape
new_posts = [
    {
        'post_id': f'linkedin_feed_{today_str}_001',
        'timestamp': '2026-03-25 02:00:00',
        'author_name': 'Julio Peláez V.',
        'company': 'JMS IMPEX',
        'position': 'President / CEO',
        'content': 'CFM56-7B26 – Fresh Shop Visit | Ready to Deliver. 8,775 Cycles. Freshly repaired. Backed by StandardAero warranty (4,000 FH / 12 months). Engine stand included. Well-positioned unit for operators requiring immediate availability. Only direct buyers or mandates will be entertained. Full documentation available against verifiable LOI. Email: julio.pelaez.villalobos@gmail.com WhatsApp: +502 3209 6692',
        'business_type': '发动机销售 - CFM56-7B26',
        'business_value_score': '9.0',
        'urgency': '高',
        'has_contact': 'True',
        'contact_info': 'julio.pelaez.villalobos@gmail.com / WhatsApp: +502 3209 6692',
        'source_url': 'https://www.linkedin.com/in/jmsimpex',
        'author_url': 'https://www.linkedin.com/in/jmsimpex',
        'content_type': 'image+text',
        'tags': '#CFM56 #Engine #AircraftEngine',
        'category': '发动机交易',
        'part_number': 'CFM56-7B26',
        'condition': 'Fresh Shop Visit',
    },
    {
        'post_id': f'linkedin_feed_{today_str}_002',
        'timestamp': '2026-03-25 01:00:00',
        'author_name': "Turbo Resources Int'l",
        'company': "Turbo Resources Int'l",
        'position': 'Company',
        'content': 'Looking to source a quality aircraft component? Part Number: SJ30361. Description: Inlet Cowl. Platform: Airbus A330. Condition: Overhauled (OH) 2 year warranty. Tag Date: 05/2024. Trace: 129 trace. Asking: $195,000. Contact: Adam@TurboResources.com',
        'business_type': '航材销售 - A330 Inlet Cowl',
        'business_value_score': '8.5',
        'urgency': '中',
        'has_contact': 'True',
        'contact_info': 'Adam@TurboResources.com',
        'source_url': 'https://www.linkedin.com/company/turboresources/posts',
        'author_url': 'https://www.linkedin.com/company/turboresources/posts',
        'content_type': 'image+text',
        'tags': '#Aviation #AircraftParts #A330 #MRO #Aerospace',
        'category': '航材交易',
        'part_number': 'SJ30361',
        'condition': 'Overhauled (OH)',
    },
    {
        'post_id': f'linkedin_feed_{today_str}_003',
        'timestamp': '2026-03-24 20:00:00',
        'author_name': 'FlyX Avia',
        'company': 'FlyX Avia',
        'position': 'Aviation Consultant & Support Services',
        'content': 'ACMI Requirement – B737 Freighter (Kenya Operation). Seeking B737F on ACMI lease for cargo operations based in Kenya. Aircraft Requirements: Type: B737 Freighter (2012 or newer), Payload: 21-23 Metric Tons, Utilization: 200 Block Hours per month, Start: Immediate. Email: ops@flyxavia.com',
        'business_type': '飞机租赁 - B737F ACMI',
        'business_value_score': '8.0',
        'urgency': '高',
        'has_contact': 'True',
        'contact_info': 'ops@flyxavia.com',
        'source_url': 'https://www.linkedin.com/in/flyx-avia-70aa4928a',
        'author_url': 'https://www.linkedin.com/in/flyx-avia-70aa4928a',
        'content_type': 'text',
        'tags': '#ACMI #B737F #CargoAviation #Freighter #AircraftLease',
        'category': '飞机租赁',
        'aircraft_type': 'B737F',
        'condition': 'ACMI Lease',
    },
    {
        'post_id': f'linkedin_feed_{today_str}_004',
        'timestamp': '2026-03-25 01:00:00',
        'author_name': 'Sergei Chereshnev',
        'company': 'Buyers and Sellers of Aircraft Spare Parts (Group)',
        'position': '2nd',
        'content': 'Aircraft Parts Available – Ireland. Engine – Trent 700: 91E676-04 RH Upper Pivoting Door (Repaired, EASA F1/FAA), 91E900-04 RH Lower Pivoting Door (Repaired, EASA F1/FAA). Engine – PW4000: 56A631 Blades Sets – LPC 1st Stage 19 sets (Inspected/Tested, FAA/EASA), 51G533-001 CASE (OH), 314T4010-10A Inlet Cowl (PW4056, AR). Avionics – A319-A340: 066-01212-0102 Transponder TRA-100B 4 EA (NS, EASA F1). All parts available in Ireland.',
        'business_type': '航材销售 - Trent700/PW4000/Avionics',
        'business_value_score': '9.0',
        'urgency': '中',
        'has_contact': 'False',
        'contact_info': '',
        'source_url': 'https://www.linkedin.com/groups/3926957',
        'author_url': '',
        'content_type': 'image+text',
        'tags': '#Aviation #MRO #AircraftParts #Trent700 #PW4000 #Avionics',
        'category': '航材交易',
        'part_number': '91E676-04, 91E900-04, 56A631, 51G533-001, 314T4010-10A, 066-01212-0102',
        'condition': 'Repaired/OH/AR/NS',
    },
    {
        'post_id': f'linkedin_feed_{today_str}_005',
        'timestamp': '2026-03-24 20:00:00',
        'author_name': 'KHLAIF Almanaseer',
        'company': 'Aerolinke Aviation',
        'position': 'Aviation & Aerospace Professional',
        'content': 'Seeking to acquire an Airbus A320 airframe for non-airworthy use. Interest in aircraft retired from active service or in end-of-life transition, maintaining basic onboard functionality (power systems, lighting, cabin seating). Airworthiness not required, landing gear condition not a limiting factor. Contact: Ceo@aerolinke.com, WhatsApp: 00962781328866, Www.aerolinke.com',
        'business_type': '飞机采购 - A320 Airframe (非适航)',
        'business_value_score': '7.0',
        'urgency': '中',
        'has_contact': 'True',
        'contact_info': 'Ceo@aerolinke.com / WhatsApp: 00962781328866',
        'source_url': 'https://www.linkedin.com/in/khlaif-almanaseer-4545b671',
        'author_url': 'https://www.linkedin.com/in/khlaif-almanaseer-4545b671',
        'content_type': 'text+link',
        'tags': '#A320 #AircraftSale #Aviation',
        'category': '飞机采购',
        'aircraft_type': 'A320',
        'condition': 'Non-airworthy',
    },
    {
        'post_id': f'linkedin_feed_{today_str}_006',
        'timestamp': '2026-03-24 23:00:00',
        'author_name': 'Aero Asset',
        'company': 'Aero Asset',
        'position': 'Company',
        'content': 'New to Market – Airbus H135 SN2317. Contact Monica Mazzei for more details. Specs: https://lnkd.in/gt4trXC6',
        'business_type': '直升机销售 - Airbus H135',
        'business_value_score': '7.5',
        'urgency': '中',
        'has_contact': 'True',
        'contact_info': 'Monica Mazzei (via LinkedIn)',
        'source_url': 'https://www.linkedin.com/company/aeroasset/posts',
        'author_url': 'https://www.linkedin.com/company/aeroasset/posts',
        'content_type': 'image+text',
        'tags': '#Airbus #H135 #Helicopters #AircraftSales #Aviation',
        'category': '直升机交易',
        'aircraft_type': 'H135',
        'condition': 'Available',
    },
    {
        'post_id': f'linkedin_feed_{today_str}_007',
        'timestamp': '2026-03-25 01:00:00',
        'author_name': 'Nathan Minami',
        'company': 'Barnes Aerospace (prev. Hanwha Aerospace USA)',
        'position': 'President, Americas',
        'content': 'Super excited to be joining Barnes Aerospace as President, Americas. Previously VP/GM at Hanwha Aerospace USA. Focus on A&D customers with safety, quality, delivery and cost efficiency, supporting global security and commercial aviation growth.',
        'business_type': '行业人事动态 - MRO/OEM高管',
        'business_value_score': '6.0',
        'urgency': '低',
        'has_contact': 'False',
        'contact_info': '',
        'source_url': 'https://www.linkedin.com/in/nathanminami',
        'author_url': 'https://www.linkedin.com/in/nathanminami',
        'content_type': 'text',
        'tags': '#Aerospace #MRO #OEM #Leadership',
        'category': '行业动态',
    },
]

# Add common fields and filter duplicates
added = 0
for post in new_posts:
    if post['post_id'] in existing_ids:
        print(f"SKIP (duplicate): {post['post_id']}")
        continue
    
    # Fill missing fields with empty string
    for fn in fieldnames:
        if fn not in post:
            post[fn] = ''
    
    post['collected_at'] = now
    post['batch_id'] = batch_id
    post['merge_timestamp'] = now
    
    existing_rows.append(post)
    added += 1
    print(f"ADDED: {post['post_id']} - {post['author_name']} - {post['business_type']}")

# Write back
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(existing_rows)

print(f"\nTotal: {len(existing_rows)} records (+{added} new)")
