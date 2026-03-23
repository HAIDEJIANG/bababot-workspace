import json
import os
from datetime import datetime

# 读取原始备份文件
backup_path = os.path.expanduser("~/Desktop/real business post/LinkedIn_Business_Posts_ALL_20260224_235254.json")
with open(backup_path, "r", encoding="utf-8") as f:
    original_posts = json.load(f)

print(f"原始备份: {len(original_posts)} 条")

# 读取新提取的文件
new_path = os.path.expanduser("~/Desktop/real business post/linkedin_real_business_posts.json")
with open(new_path, "r", encoding="utf-8") as f:
    new_data = json.load(f)

print(f"新提取: {len(new_data['posts'])} 条")

# 合并
existing_ids = {p["post_id"] for p in original_posts}
added = 0
for post in new_data["posts"]:
    if post["post_id"] not in existing_ids:
        original_posts.append(post)
        added += 1

print(f"新增: {added} 条")

# 保存
metadata = {
    "total_collected": len(original_posts),
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

with open(new_path, "w", encoding="utf-8") as f:
    json.dump({"metadata": metadata, "posts": original_posts}, f, ensure_ascii=False, indent=2)

total = len(original_posts)
remaining = max(0, 100 - total)
print(f"总计: {total} 条")
print(f"目标: 100 条")
print("完成")
