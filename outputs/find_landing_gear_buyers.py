import pandas as pd
import sys

# Set encoding for output
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

file_path = r'C:\Users\Haide\Desktop\LINKEDIN\LINKEDIN Connections_bababot_style_FINAL.csv'
df = pd.read_csv(file_path, encoding='utf-8')

landing_gear_keywords = ['landing gear', '起落架', 'landing-gear', 'landinggear']

search_columns = ['First Name', 'Last Name', 'Position', 'Company', 'Business_Focus', 'Notes_Bababot']
search_columns = [c for c in search_columns if c in df.columns]

mask = df[search_columns].astype(str).apply(
    lambda x: x.str.contains('|'.join(landing_gear_keywords), case=False, na=False)
).any(axis=1)

landing_gear_contacts = df[mask].copy()

# Create report
report_lines = []
report_lines.append("="*70)
report_lines.append("A320 LANDING GEAR SALES - POTENTIAL BUYERS FROM LINKEDIN")
report_lines.append("="*70)
report_lines.append(f"\nTotal contacts in database: {len(df)}")
report_lines.append(f"Landing gear related contacts found: {len(landing_gear_contacts)}\n")

priority_companies = ['Landing Gear Leasing', 'Landing Gear Support', 'REVIMA', 'APOC Aviation']

for idx, row in landing_gear_contacts.iterrows():
    company = str(row.get('Company', 'N/A'))
    is_priority = any(p.lower() in company.lower() for p in priority_companies)
    
    first_name = str(row.get('First Name', ''))
    last_name = str(row.get('Last Name', ''))
    full_name = f"{first_name} {last_name}".strip()
    
    report_lines.append(f"{'[PRIORITY]' if is_priority else '[STANDARD]'} Contact #{idx+1}")
    report_lines.append(f"  Name: {full_name}")
    report_lines.append(f"  Title: {row.get('Position', 'N/A')}")
    report_lines.append(f"  Company: {company}")
    
    url = row.get('URL', '')
    if pd.notna(url) and str(url).strip():
        report_lines.append(f"  LinkedIn: {url}")
    
    connected_on = row.get('Connected On', '')
    if pd.notna(connected_on):
        report_lines.append(f"  Connected: {connected_on}")
    
    report_lines.append("")

report_lines.append("="*70)
report_lines.append("PRIORITY RECOMMENDATIONS:")
report_lines.append("1. [TOP] Landing Gear Leasing, LLC - Specialist in landing gear leasing")
report_lines.append("2. [TOP] Landing Gear Support Services - Landing gear support specialist")
report_lines.append("3. [HIGH] REVIMA - French MRO, known for landing gear overhaul")
report_lines.append("4. [HIGH] APOC Aviation - Aviation solutions & parts trading")
report_lines.append("5. [MEDIUM] Source One Spares - Spare parts & components trading")
report_lines.append("6. [MEDIUM] Executive Jet Support - Business aviation support")
report_lines.append("7. [LOW] Air Canada - Airline (direct contact for fleet needs)")
report_lines.append("8. [LOW] Head Aero - Aviation company")
report_lines.append("="*70)

# Print to console
for line in report_lines:
    print(line)

# Save to file
output_text = r'outputs/A320_Landing_Gear_Buyers_Report.txt'
with open(output_text, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

# Save CSV
output_csv = r'outputs/A320_Landing_Gear_Buyers.csv'
landing_gear_contacts.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"\nReport saved to: {output_text}")
print(f"CSV saved to: {output_csv}")
