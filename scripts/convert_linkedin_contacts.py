import csv

input_file = r"C:\Users\Haide\Desktop\OPENCLAW\LINKEDIN\LINKEDIN Connections_with_analysis_FINAL.csv"
output_file = r"C:\Users\Haide\Desktop\LINKEDIN\all_contacts_current.csv"

contacts = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        contact = {
            'contact_id': row.get('URL', ''),
            'name': f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
            'profile_url': row.get('URL', ''),
            'company': row.get('Company', ''),
            'title': row.get('Position', ''),
            'location': '',
            'industry': 'Aviation',
            'connections': '500+'
        }
        contacts.append(contact)

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['contact_id', 'name', 'profile_url', 'company', 'title', 'location', 'industry', 'connections'])
    writer.writeheader()
    writer.writerows(contacts)

print(f"转换完成：共 {len(contacts)} 位联系人")
print(f"输出文件：{output_file}")
