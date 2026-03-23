import csv, json, sys
from pathlib import Path

if len(sys.argv) < 3:
    print('Usage: append_csv_row.py <csv_path> <row_json>')
    sys.exit(2)

path = Path(sys.argv[1])
row = json.loads(sys.argv[2])

with path.open('r', newline='', encoding='utf-8') as f:
    header = next(csv.reader(f))

with path.open('a', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=header)
    w.writerow(row)

print('appended')
