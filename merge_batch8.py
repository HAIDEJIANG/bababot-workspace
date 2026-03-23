import csv

existing_content = set()

try:
    with open('outputs/aviation_linkedin_master_20250301.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
            existing_content.add(key)
except:
    pass

new_records = []
try:
    with open('outputs/aviation_linkedin_new_batch8.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row.get('author_name','')}_{row.get('post_content','')[:100]}"
            if key not in existing_content:
                new_records.append(row)
                existing_content.add(key)
except Exception as e:
    print(f'Error: {e}')

if new_records:
    with open('outputs/aviation_linkedin_master_20250301.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in new_records:
            writer.writerow([
                row['timestamp'], row['author_name'], row['author_title'],
                row['author_company'], row['post_content'], row['hashtags'],
                row['source_url'], row['post_type'], row['collected_at']
            ])
    print(f'Added: {len(new_records)}')
else:
    print('Duplicate or error')

print(f'Total: {len(existing_content)}')
