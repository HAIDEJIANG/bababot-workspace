import pandas as pd

file_path = r'C:\Users\Haide\Desktop\LINKEDIN\LINKEDIN Connections_bababot_style_FINAL.csv'
df = pd.read_csv(file_path, encoding='utf-8')

landing_gear_keywords = ['landing gear', '起落架', 'landing-gear', 'landinggear']
mask = df.astype(str).apply(lambda x: x.str.contains('|'.join(landing_gear_keywords), case=False, na=False)).any(axis=1)
landing_gear_contacts = df[mask]

print("="*60)
print("A320 LANDING GEAR - POTENTIAL BUYERS")
print("="*60)
print(f"\nTotal contacts in database: {len(df)}")
print(f"Landing gear related contacts found: {len(landing_gear_contacts)}")
print()

for idx, row in landing_gear_contacts.iterrows():
    print(f"--- Contact {idx+1} ---")
    print(f"Name: {row.get('Name', 'N/A')}")
    print(f"Title: {row.get('Title', 'N/A')}")
    print(f"Company: {row.get('Company', 'N/A')}")
    print(f"Industry: {row.get('Industry', 'N/A')}")
    
    notes = row.get('Notes', '')
    if pd.notna(notes) and str(notes).strip():
        print(f"Notes: {str(notes)[:150]}...")
    print()

print("="*60)
print("Recommendation: Prioritize companies with 'Landing Gear' in name")
print("="*60)
