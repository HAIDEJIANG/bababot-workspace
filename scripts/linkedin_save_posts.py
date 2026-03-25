import csv, os, datetime

csv_path = r'C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv'
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
batch_id = 'batch_' + datetime.datetime.now().strftime('%Y%m%d')
date_tag = datetime.datetime.now().strftime('%Y%m%d')

new_posts = [
    {
        'post_id': f'linkedin_feed_{date_tag}_018',
        'timestamp': now,
        'author_name': 'Shine Yang \u6768\u71d5\u8d85',
        'company': 'AeroFinance',
        'position': 'Editor & Senior Conference Producer',
        'content': 'We are happy to announce that Mr. WANG Tao, Deputy Manager, Materials Management Center, China Southern Technic has confirmed to speak at CAMMF 2026, where 400+ attendees from aircraft parts&materials management communities are expected to be present.',
        'business_type': '\u822a\u7a7a\u4f1a\u8bae/\u822a\u6750\u7ba1\u7406 - CAMMF 2026',
        'business_value_score': '8.0',
        'urgency': '',
        'has_contact': 'True',
        'contact_info': 'https://lnkd.in/ggpKivwA',
        'post_time': '2h',
        'reactions': '3',
        'comments': '0',
        'reposts': '0',
        'has_image': '1',
        'image_content': 'CAMMF 2026 event image',
        'source_url': 'https://www.linkedin.com/in/shine-yang-%E6%9D%A8%E7%87%95%E8%B6%85-15426418',
        'source_file': 'LinkedIn_Business_Posts_Master_Table.csv',
        'merge_timestamp': now,
        'batch_id': batch_id,
        'collected_at': now,
        '_source_file': '',
        'author_url': 'https://www.linkedin.com/in/shine-yang-%E6%9D%A8%E7%87%95%E8%B6%85-15426418',
        'posted_time': '2h',
        'content_summary': 'CAMMF 2026 speaker announcement - China Southern Technic materials management',
        'is_repost': '',
        'original_author': '',
        'category': 'Conference/Event',
        'aircraft_type': '',
        'author_title': 'Editor & Senior Conference Producer, AeroFinance',
        'content_type': 'image+text',
        'tags': '#CAMMF2026 #AircraftParts #MaterialsManagement',
        'author': 'Shine Yang \u6768\u71d5\u8d85',
        'likes': '3',
        'summary': 'CAMMF 2026 speaker from China Southern Technic confirmed, 400+ aircraft parts community attendees',
        'part_numbers': '',
        'condition': '',
        'quantity': '',
        'certification': '',
        'part_number': '',
        'status': 'active',
        'notes': ''
    },
    {
        'post_id': f'linkedin_feed_{date_tag}_019',
        'timestamp': now,
        'author_name': 'AVIAHEADS',
        'company': 'AVIAHEADS',
        'position': 'Company',
        'content': 'Aircraft redelivery preparation: Returning aircraft in 2026-2028? Gap assessment needed 9-15 months before. Part-CAMO platform in Estonia supports airworthiness, transitions, storage, redelivery via compliance control, technical oversight, records review. Contact commercial@aviaheads.com',
        'business_type': 'MRO/CAMO\u670d\u52a1 - \u98de\u673a\u9000\u79df\u51c6\u5907',
        'business_value_score': '7.0',
        'urgency': '',
        'has_contact': 'True',
        'contact_info': 'commercial@aviaheads.com',
        'post_time': '58m',
        'reactions': '2',
        'comments': '0',
        'reposts': '0',
        'has_image': '1',
        'image_content': '7-page document about aircraft redelivery',
        'source_url': 'https://www.linkedin.com/company/aviaheads/posts',
        'source_file': 'LinkedIn_Business_Posts_Master_Table.csv',
        'merge_timestamp': now,
        'batch_id': batch_id,
        'collected_at': now,
        '_source_file': '',
        'author_url': 'https://www.linkedin.com/company/aviaheads/posts',
        'posted_time': '58m',
        'content_summary': 'Aircraft lease return gap assessment service, Part-CAMO platform Estonia',
        'is_repost': '',
        'original_author': '',
        'category': 'MRO/CAMO Service',
        'aircraft_type': '',
        'author_title': 'Company - 2,574 followers',
        'content_type': 'document+text',
        'tags': '#TeamAVIAHEADS #AircraftRedelivery #CAMO',
        'author': 'AVIAHEADS',
        'likes': '2',
        'summary': 'Aircraft redelivery prep service: gap assessment, Part-CAMO, compliance for 2026-2028 returns',
        'part_numbers': '',
        'condition': '',
        'quantity': '',
        'certification': '',
        'part_number': '',
        'status': 'active',
        'notes': ''
    },
    {
        'post_id': f'linkedin_feed_{date_tag}_020',
        'timestamp': now,
        'author_name': 'BIRD AVIATION - MRO Part.145',
        'company': 'BIRD AVIATION',
        'position': 'Company',
        'content': '#Aircraft jacking and proper structural support - key role in maintaining accuracy and safety during maintenance. Take a closer look at our services: https://lnkd.in/er8FRiws #Aviation #MRO #AircraftMaintenance #Hangar #BirdAviation',
        'business_type': 'MRO\u670d\u52a1 - \u98de\u673a\u7ef4\u4fee(Part.145)',
        'business_value_score': '7.0',
        'urgency': '',
        'has_contact': 'True',
        'contact_info': 'https://lnkd.in/er8FRiws / www.birdaviation.com',
        'post_time': '23h',
        'reactions': '42',
        'comments': '0',
        'reposts': '1',
        'has_image': '1',
        'image_content': 'Aircraft jacking/maintenance image',
        'source_url': 'https://www.linkedin.com/company/bird-aviation-ltd-/posts',
        'source_file': 'LinkedIn_Business_Posts_Master_Table.csv',
        'merge_timestamp': now,
        'batch_id': batch_id,
        'collected_at': now,
        '_source_file': '',
        'author_url': 'https://www.linkedin.com/company/bird-aviation-ltd-/posts',
        'posted_time': '23h',
        'content_summary': 'Aircraft jacking & structural support MRO service promotion',
        'is_repost': '',
        'original_author': '',
        'category': 'MRO Service',
        'aircraft_type': '',
        'author_title': 'Company - 10,963 followers',
        'content_type': 'image+text',
        'tags': '#Aircraft #Aviation #MRO #AircraftMaintenance #Hangar #BirdAviation',
        'author': 'BIRD AVIATION',
        'likes': '42',
        'summary': 'MRO Part.145 aircraft jacking and maintenance services',
        'part_numbers': '',
        'condition': '',
        'quantity': '',
        'certification': 'Part.145',
        'part_number': '',
        'status': 'active',
        'notes': ''
    },
    {
        'post_id': f'linkedin_feed_{date_tag}_021',
        'timestamp': now,
        'author_name': 'Alpha Aircraft Systems',
        'company': 'Alpha Aircraft Systems',
        'position': 'Company',
        'content': 'Bronze Sponsor of Aviation Africa 2026. Over 30 years experience, globally trusted MRO provider specialising in APU systems and key aircraft components. FAA and EASA-approved. Aviation Africa: 9-10 September 2026, Sarit Expo Centre, Nairobi, Kenya.',
        'business_type': 'MRO\u670d\u52a1 - APU\u7cfb\u7edf, \u822a\u7a7a\u5c55\u4f1a\u8d5e\u52a9',
        'business_value_score': '8.0',
        'urgency': '',
        'has_contact': 'True',
        'contact_info': 'www.aviationafrica.aero',
        'post_time': '16h',
        'reactions': '4',
        'comments': '3',
        'reposts': '1',
        'has_image': '1',
        'image_content': 'Aviation Africa 2026 sponsorship image',
        'source_url': 'https://www.linkedin.com/company/alpha-aircraft-systems/posts',
        'source_file': 'LinkedIn_Business_Posts_Master_Table.csv',
        'merge_timestamp': now,
        'batch_id': batch_id,
        'collected_at': now,
        '_source_file': '',
        'author_url': 'https://www.linkedin.com/company/alpha-aircraft-systems/posts',
        'posted_time': '16h',
        'content_summary': 'APU MRO specialist sponsoring Aviation Africa 2026, FAA/EASA approved',
        'is_repost': 'True',
        'original_author': 'Aviation AFRICA Summit & Exhibition',
        'category': 'MRO/APU/Event',
        'aircraft_type': '',
        'author_title': 'Company - 672 followers',
        'content_type': 'image+text',
        'tags': '#avaf26 #aviation #mro #aircraft #apu #maintenance',
        'author': 'Alpha Aircraft Systems',
        'likes': '4',
        'summary': 'APU & aircraft component MRO, FAA/EASA, sponsoring Aviation Africa 2026 Nairobi',
        'part_numbers': '',
        'condition': '',
        'quantity': '',
        'certification': 'FAA, EASA',
        'part_number': '',
        'status': 'active',
        'notes': 'Reposted by Joseph Oyekanmi Isijola. Original: Aviation AFRICA Summit.'
    },
    {
        'post_id': f'linkedin_feed_{date_tag}_022',
        'timestamp': now,
        'author_name': 'AMP Aero Services',
        'company': 'AMP Aero Services / GA Telesis',
        'position': 'Company',
        'content': 'A GREAT tournament put on by GA Telesis. This is one that stays on our calendar year after year. Always well organized, well attended, and a great environment.',
        'business_type': '\u822a\u7a7a\u884c\u4e1a\u6d3b\u52a8/\u793e\u4ea4',
        'business_value_score': '5.0',
        'urgency': '',
        'has_contact': '',
        'contact_info': '',
        'post_time': '13h',
        'reactions': '55',
        'comments': '0',
        'reposts': '3',
        'has_image': '1',
        'image_content': 'GA Telesis event photo',
        'source_url': 'https://www.linkedin.com/company/ampaeroservices/posts',
        'source_file': 'LinkedIn_Business_Posts_Master_Table.csv',
        'merge_timestamp': now,
        'batch_id': batch_id,
        'collected_at': now,
        '_source_file': '',
        'author_url': 'https://www.linkedin.com/company/ampaeroservices/posts',
        'posted_time': '13h',
        'content_summary': 'AMP Aero Services at GA Telesis annual event',
        'is_repost': 'True',
        'original_author': 'GA Telesis reposted',
        'category': 'Industry Event/Networking',
        'aircraft_type': '',
        'author_title': 'Company - 6,009 followers',
        'content_type': 'image+text',
        'tags': '#GATelesis #AMPAero #AviationEvent',
        'author': 'AMP Aero Services',
        'likes': '55',
        'summary': 'AMP Aero at GA Telesis annual tournament, industry networking',
        'part_numbers': '',
        'condition': '',
        'quantity': '',
        'certification': '',
        'part_number': '',
        'status': 'active',
        'notes': 'Reposted by GA Telesis.'
    },
    {
        'post_id': f'linkedin_feed_{date_tag}_023',
        'timestamp': now,
        'author_name': 'Aberdair Aviation Group',
        'company': 'Aberdair Aviation Group / Eagle Copters',
        'position': 'Company',
        'content': 'Strategic partnership with Eagle Copters to deploy up to 5x Bell 412EP helicopters in Africa via AOC bases in Kenya and Ghana. First B412EPs to enter service within 3 months. Supporting passenger transport, medevac and utility contracts. Also providing B412 maintenance from Nanyuki, Kenya facility.',
        'business_type': '\u76f4\u5347\u673a\u8fd0\u8425/\u79df\u8d41 - Bell 412EP',
        'business_value_score': '7.0',
        'urgency': '',
        'has_contact': 'True',
        'contact_info': 'https://lnkd.in/eFn-iz3Q',
        'post_time': '1d',
        'reactions': '0',
        'comments': '0',
        'reposts': '0',
        'has_image': '1',
        'image_content': 'Bell 412EP helicopter partnership image',
        'source_url': 'https://www.linkedin.com/company/aberdair-aviation/posts',
        'source_file': 'LinkedIn_Business_Posts_Master_Table.csv',
        'merge_timestamp': now,
        'batch_id': batch_id,
        'collected_at': now,
        '_source_file': '',
        'author_url': 'https://www.linkedin.com/company/aberdair-aviation/posts',
        'posted_time': '1d',
        'content_summary': 'Aberdair + Eagle Copters: 5x Bell 412EP in Africa, maintenance in Kenya',
        'is_repost': '',
        'original_author': '',
        'category': 'Helicopter Operations/Partnership',
        'aircraft_type': 'Bell 412EP',
        'author_title': 'Company - 2,610 followers',
        'content_type': 'image+text',
        'tags': '#Bell412 #Helicopter #AfricaAviation #EagleCopters',
        'author': 'Aberdair Aviation Group',
        'likes': '0',
        'summary': '5x Bell 412EP deployment in Africa, Kenya/Ghana bases, MRO from Nanyuki',
        'part_numbers': '',
        'condition': '',
        'quantity': '5',
        'certification': '',
        'part_number': '',
        'status': 'active',
        'notes': 'Partnership with Eagle Copters. First aircraft within 3 months.'
    }
]

# Read existing
with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    existing_rows = list(reader)

# Check for existing IDs to avoid duplicates
existing_ids = set()
id_field = fieldnames[0]  # first field (may have BOM)
for row in existing_rows:
    if id_field in row and row[id_field]:
        existing_ids.add(row[id_field])

print(f'Existing rows: {len(existing_rows)}')
print(f'Existing IDs sample: {list(existing_ids)[:3]}')

# Map new posts to fieldnames
added = 0
for post in new_posts:
    pid = post['post_id']
    if pid in existing_ids:
        print(f'SKIP duplicate: {pid}')
        continue
    mapped = {}
    for fn in fieldnames:
        clean = fn.lstrip('\ufeff')
        if fn in post:
            mapped[fn] = post[fn]
        elif clean in post:
            mapped[fn] = post[clean]
        else:
            mapped[fn] = ''
    existing_rows.append(mapped)
    added += 1

# Write back
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in existing_rows:
        clean_row = {k: v for k, v in row.items() if k is not None}
        writer.writerow(clean_row)

print(f'Added: {added}')
print(f'Total rows: {len(existing_rows)}')
print('DONE')
