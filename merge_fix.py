import json
import os
from datetime import datetime

# 读取原始备份文件（33条帖子）
backup_path = os.path.expanduser("~/Desktop/real business post/LinkedIn_Business_Posts_ALL_20260224_235254.json")
with open(backup_path, "r", encoding="utf-8") as f:
    original_posts = json.load(f)

print(f"原始备份: {len(original_posts)} 条帖子")

# 读取新提取的文件（21条帖子）
new_path = os.path.expanduser("~/Desktop/real business post/linkedin_real_business_posts.json")
with open(new_path, "r", encoding="utf-8") as f:
    new_data = json.load(f)

print(f"新提取: {len(new_data['posts'])} 条帖子")

# 合并数据
existing_ids = {p["post_id"] for p in original_posts}
added_count = 0
for post in new_data["posts"]:
    if post["post_id"] not in existing_ids:
        original_posts.append(post)
        added_count += 1

print(f"新增: {added_count} 条帖子")

# 更新元数据
metadata = {
    "total_collected": len(original_posts),
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "source_files": ["LinkedIn_Business_Posts_ALL_20260224_235254.json", "linkedin_real_business_posts.json"]
}

# 保存合并后的文件
with open(new_path, "w", encoding="utf-8") as f:
    json.dump({"metadata": metadata, "posts": original_posts}, f, ensure_ascii=False, indent=2)

total = len(original_posts)
remaining = max(0, 100 - total)
print(f"总计: {total} 条工作帖子")
print(f"目标: 100 条")
print(f"还差: {remaining} 条")
print("✅ 数据已合并并保存")
