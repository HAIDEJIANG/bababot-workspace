import pandas as pd
import sys

# Fix encoding
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

df = pd.read_csv(r'outputs/A320_Landing_Gear_Buyers.csv', encoding='utf-8-sig')

output_lines = []
output_lines.append('='*70)
output_lines.append('EMAIL ADDRESS CHECK FOR A320 LANDING GEAR BUYERS')
output_lines.append('='*70)

email_found = False

for idx, row in df.iterrows():
    first_name = str(row.get('First Name', ''))
    last_name = str(row.get('Last Name', ''))
    name = f"{first_name} {last_name}".strip()
    company = str(row.get('Company', 'N/A'))
    position = str(row.get('Position', 'N/A'))
    url = str(row.get('URL', ''))
    
    # Check for email
    email = None
    if 'Email Address' in df.columns:
        email_val = row.get('Email Address', '')
        if pd.notna(email_val) and str(email_val).strip() and str(email_val).lower() != 'nan':
            email = str(email_val).strip()
    
    output_lines.append(f"\n{name}")
    output_lines.append(f"  Company: {company}")
    output_lines.append(f"  Position: {position}")
    output_lines.append(f"  LinkedIn: {url}")
    
    if email:
        output_lines.append(f"  Email: {email}")
        email_found = True
    else:
        output_lines.append(f"  Email: [Not available in LinkedIn export]")

output_lines.append('\n' + '='*70)
if not email_found:
    output_lines.append("NOTE: No email addresses found in the LinkedIn export.")
    output_lines.append("LinkedIn privacy settings typically prevent email export.")
    output_lines.append("")
    output_lines.append("ALTERNATIVE WAYS TO CONTACT:")
    output_lines.append("1. Send LinkedIn InMail/Message directly via LinkedIn")
    output_lines.append("2. Visit company website to find contact information")
    output_lines.append("3. Call company main line and ask for the person")
output_lines.append('='*70)

# Print to console
for line in output_lines:
    print(line)

# Save to file
with open('outputs/A320_Landing_Gear_Buyers_Emails.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("\nReport saved to: outputs/A320_Landing_Gear_Buyers_Emails.txt")
