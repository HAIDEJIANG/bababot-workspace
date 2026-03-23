import csv
from pathlib import Path

path = Path('outputs/LinkedIn_Business_Posts_新增_20260226_1146.csv')
row = {
    'source_url': 'https://www.linkedin.com/feed/update/urn:li:activity:7432569802474409984/',
    'author_name': 'Hamza Satti',
    'company': 'American Aeronex',
    'post_time': '4 hours ago',
    'category': 'Aircraft acquisition (ATR72-600)',
    'summary': 'WTB ATR 72-600 passenger aircraft (2015–2018 YOM); requests technical details, cycles/hours, maintenance status, and pricing.',
    'request_type': 'WTB',
    'request_details': 'Seeking ATR 72-600 (2015–2018 YOM), airworthy/ready, complete records, immediate delivery; submit tech details + price; contact hamza@americanaeronex.com',
}

with path.open('r', newline='', encoding='utf-8') as f:
    header = next(csv.reader(f))

with path.open('a', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=header)
    w.writerow(row)

print('appended')
