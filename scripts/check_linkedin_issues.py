# -*- coding: utf-8 -*-
"""检查 LinkedIn 数据的具体问题"""

import csv

with open(r'C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    
    bad_category = []
    bad_businesstype = []
    bad_sourceurl = []
    
    for i, row in enumerate(reader):
        cat = row.get('category', '').lower().strip()
        bt = row.get('business_type', '').lower().strip()
        url = row.get('source_url', '')
        
        valid_cats = ['engine', 'aircraft', 'landing_gear', 'mro', 'parts', 'helicopter', 'service', 'training', 'other', '']
        valid_bts = ['supply', 'demand', 'service', 'news', 'education', 'other', '']
        
        if len(bad_category) < 5 and cat and cat not in valid_cats:
            bad_category.append((i+2, cat, row.get('author', '')[:20]))
        
        if len(bad_businesstype) < 5 and bt and bt not in valid_bts:
            bad_businesstype.append((i+2, bt, row.get('author', '')[:20]))
        
        if len(bad_sourceurl) < 5 and (not url or not (url.startswith('http') or url.startswith('www'))):
            bad_sourceurl.append((i+2, url[:50] if url else '(empty)', row.get('author', '')[:20]))
    
    print('=== Category issues (first 5):')
    for line, cat, author in bad_category:
        print(f'  Line {line}: category="{cat}", author="{author}"')
    
    print('\n=== Business Type issues (first 5):')
    for line, bt, author in bad_businesstype:
        print(f'  Line {line}: business_type="{bt}", author="{author}"')
    
    print('\n=== Source URL issues (first 5):')
    for line, url, author in bad_sourceurl:
        print(f'  Line {line}: source_url="{url}", author="{author}"')