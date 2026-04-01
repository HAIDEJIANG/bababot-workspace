import csv
from collections import Counter

f = open('C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv', 'r', encoding='utf-8')
r = csv.DictReader(f)
rows = list(r)

print(f"总记录: {len(rows)}")

# 统计公司/发布者
companies = Counter()
for x in rows:
    c = x.get('company', '') or x.get('author_name', '')
    if c and c != 'Unknown':
        companies[c[:40]] += 1

print(f"公司/发布者: {len(companies)} 家")
print("\n前 20 家活跃发布者:")
for c, n in companies.most_common(20):
    print(f"  {c}: {n} 条")

# 统计业务类型
types = Counter(x.get('business_type', '未知') for x in rows)
print("\n业务类型分布:")
for t, n in types.most_common(10):
    print(f"  {t}: {n} 条")

# 统计联系方式
contacts = [x for x in rows if x.get('contact_info')]
print(f"\n有联系方式: {len(contacts)} 条")

# 统计零件号
pn_count = sum(1 for x in rows if x.get('part_numbers'))
print(f"含零件号: {pn_count} 条")