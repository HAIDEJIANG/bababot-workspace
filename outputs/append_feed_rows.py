import csv, json, sys
from pathlib import Path

# Usage: python append_feed_rows.py <csv_path> <rows_json_path>

csv_path = Path(sys.argv[1])
rows_path = Path(sys.argv[2])
rows = json.loads(rows_path.read_text(encoding='utf-8'))

with csv_path.open('r', newline='', encoding='utf-8') as f:
    header = next(csv.reader(f))

existing_ids = set()
with csv_path.open('r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r.get('activity_id'):
            existing_ids.add(r['activity_id'])

added = 0
with csv_path.open('a', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=header)
    for r in rows:
        aid = str(r.get('activity_id') or '').strip()
        if not aid or aid in existing_ids:
            continue
        # normalize
        out = {k: (r.get(k, '') if r.get(k, '') is not None else '') for k in header}
        w.writerow(out)
        existing_ids.add(aid)
        added += 1

print(f'added={added}')
