# -*- coding: utf-8 -*-
"""验证 LinkedIn 数据质量"""
import csv

filepath = r'C:\Users\Haide\Desktop\real business post\LinkedIn_Business_Posts_Master_Table.csv'

with open(filepath, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
    categories = {}
    business_types = {}
    business_values = {}
    
    for row in rows:
        cat = row.get('category', '').strip()
        bt = row.get('business_type', '').strip()
        bv = row.get('business_value', '').strip()
        
        categories[cat] = categories.get(cat, 0) + 1
        business_types[bt] = business_types.get(bt, 0) + 1
        business_values[bv] = business_values.get(bv, 0) + 1
    
    print(f'Total rows: {len(rows)}')
    print(f'\nCategory distribution:')
    for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f'  {k if k else "(empty)"}: {v}')
    
    print(f'\nBusiness Type distribution:')
    for k, v in sorted(business_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f'  {k if k else "(empty)"}: {v}')
    
    print(f'\nBusiness Value distribution:')
    for k, v in sorted(business_values.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f'  {k if k else "(empty)"}: {v}')