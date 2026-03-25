content = open(r'C:\Users\Haide\.openclaw\workspace\scripts\linkedin_save_posts.py','r',encoding='utf-8').read()
replacements = [
    ("f'linkedin_feed_{date_tag}_002'", "f'linkedin_feed_{date_tag}_019'"),
    ("f'linkedin_feed_{date_tag}_003'", "f'linkedin_feed_{date_tag}_020'"),
    ("f'linkedin_feed_{date_tag}_004'", "f'linkedin_feed_{date_tag}_021'"),
    ("f'linkedin_feed_{date_tag}_005'", "f'linkedin_feed_{date_tag}_022'"),
    ("f'linkedin_feed_{date_tag}_006'", "f'linkedin_feed_{date_tag}_023'"),
]
for old, new in replacements:
    content = content.replace(old, new)
open(r'C:\Users\Haide\.openclaw\workspace\scripts\linkedin_save_posts.py','w',encoding='utf-8').write(content)
print('Done')
