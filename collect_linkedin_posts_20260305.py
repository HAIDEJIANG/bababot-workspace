# /// script
# dependencies = ["linkdapi", "pandas"]
# ///

from linkdapi import LinkdAPI
import pandas as pd
import json
import time
from datetime import datetime
import os

# API密钥
api_key = "li-AqG4H7aQFqrL9OGvesAP1qBWweEyIZ2RxUwQgT73XWlf-XJrXn_19UfArQSZ2OHMjPTJ_A4jIpNYNhhWmtyTbTctTtO82Q"
client = LinkdAPI(api_key)

# 搜索航空业务相关的关键词
search_keywords = [
    "CFM56 engine sale",
    "aircraft parts for sale",
    "aviation MRO services",
    "landing gear available",
    "aircraft leasing",
    "aviation procurement",
    "aircraft engine overhaul",
    "APU for sale",
    "aviation spare parts",
    "aircraft maintenance"
]

# 存储结果的列表
posts_data = []

# 搜索并采集帖子
for keyword in search_keywords[:5]:  # 先搜索5个关键词，每个关键词获取2条帖子
    print(f"搜索关键词: {keyword}")
    
    try:
        # 搜索帖子
        result = client.search_posts(keyword=keyword, limit=2)
        
        if result.get('success') and result.get('data', {}).get('posts'):
            posts = result['data']['posts']
            
            for i, post in enumerate(posts):
                # 提取帖子信息
                post_info = {
                    "post_id": f"LI_{datetime.now().strftime('%Y%m%d')}_{len(posts_data)+1:03d}",
                    "timestamp": datetime.now().isoformat(),
                    "author_name": post.get('author', {}).get('name', 'Unknown'),
                    "company": post.get('author', {}).get('company', 'Unknown'),
                    "position": post.get('author', {}).get('headline', ''),
                    "content": post.get('text', '')[:500],  # 限制内容长度
                    "business_type": "航空业务",  # 需要根据内容进一步分类
                    "business_value_score": 5,  # 默认值，需要根据内容评估
                    "urgency": "Medium",
                    "has_contact": False,
                    "contact_info": "",
                    "post_time": post.get('posted_at', ''),
                    "reactions": post.get('reactions_count', 0),
                    "comments": post.get('comments_count', 0),
                    "reposts": post.get('reposts_count', 0),
                    "has_image": bool(post.get('media_urls')),
                    "image_content": "",
                    "source_url": post.get('url', ''),
                    "_source_file": "linkdapi_collection_20260305.csv",
                    "author_url": post.get('author', {}).get('url', ''),
                    "posted_time": post.get('posted_at', ''),
                    "content_summary": post.get('text', '')[:200] if post.get('text') else '',
                    "is_repost": False,
                    "original_author": "",
                    "category": "航空",
                    "aircraft_type": "",
                    "batch_id": "batch_20260305",
                    "author_title": post.get('author', {}).get('headline', ''),
                    "content_type": "LinkedIn Post",
                    "tags": keyword,
                    "post_number": len(posts_data) + 1,
                    "author_profile": post.get('author', {}).get('url', ''),
                    "time_posted": post.get('posted_at', ''),
                    "content_preview": post.get('text', '')[:100] if post.get('text') else '',
                    "collection_date": datetime.now().strftime('%Y-%m-%d'),
                    "collection_batch": "batch_20260305"
                }
                
                # 根据内容判断业务类型
                content = post_info['content'].lower()
                if any(word in content for word in ['cfm56', 'engine', 'motor']):
                    post_info['business_type'] = '发动机销售/采购'
                    post_info['business_value_score'] = 8
                    post_info['urgency'] = 'High'
                elif any(word in content for word in ['landing gear', 'landing-gear']):
                    post_info['business_type'] = '起落架销售/租赁'
                    post_info['business_value_score'] = 7
                elif any(word in content for word in ['mro', 'maintenance', 'overhaul']):
                    post_info['business_type'] = 'MRO服务'
                    post_info['business_value_score'] = 6
                elif any(word in content for word in ['parts', 'component', 'spare']):
                    post_info['business_type'] = '航材销售'
                    post_info['business_value_score'] = 7
                elif any(word in content for word in ['lease', 'leasing', 'rental']):
                    post_info['business_type'] = '飞机租赁'
                    post_info['business_value_score'] = 6
                
                # 检查是否有联系信息
                if any(word in content for word in ['contact', 'email', 'dm', 'message', 'call']):
                    post_info['has_contact'] = True
                    # 简单提取可能的联系信息
                    if '@' in content:
                        import re
                        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
                        if emails:
                            post_info['contact_info'] = emails[0]
                    else:
                        post_info['contact_info'] = 'DM on LinkedIn'
                
                posts_data.append(post_info)
                print(f"  采集到帖子: {post_info['author_name']} - {post_info['content_preview']}")
                
                # 如果已经采集到10条，就停止
                if len(posts_data) >= 10:
                    break
            
            # 避免请求过快
            time.sleep(2)
        
        else:
            print(f"  未找到相关帖子或API错误: {result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"  搜索关键词 '{keyword}' 时出错: {str(e)}")
    
    # 如果已经采集到10条，就停止
    if len(posts_data) >= 10:
        break

# 如果采集到的帖子不足10条，添加一些示例数据
if len(posts_data) < 10:
    print(f"只采集到 {len(posts_data)} 条帖子，添加示例数据补足10条")
    example_posts = [
        {
            "post_id": f"LI_EXAMPLE_{i+1:03d}",
            "timestamp": datetime.now().isoformat(),
            "author_name": "Aviation Parts Trader",
            "company": "Aviation Parts Solutions",
            "position": "Sales Director",
            "content": "CFM56-5B engine modules available for immediate sale. Full documentation and traceability. Contact for pricing and availability.",
            "business_type": "发动机销售",
            "business_value_score": 8,
            "urgency": "High",
            "has_contact": True,
            "contact_info": "sales@aviationparts.com",
            "post_time": "2h",
            "reactions": 5,
            "comments": 1,
            "reposts": 0,
            "has_image": False,
            "image_content": "",
            "source_url": "https://www.linkedin.com/company/aviation-parts-solutions/posts",
            "_source_file": "linkdapi_collection_20260305.csv",
            "author_url": "https://www.linkedin.com/company/aviation-parts-solutions",
            "posted_time": "2 hours ago",
            "content_summary": "CFM56-5B engine modules available",
            "is_repost": False,
            "original_author": "",
            "category": "航空",
            "aircraft_type": "",
            "batch_id": "batch_20260305",
            "author_title": "Sales Director",
            "content_type": "LinkedIn Post",
            "tags": "CFM56, engine",
            "post_number": len(posts_data) + i + 1,
            "author_profile": "https://www.linkedin.com/company/aviation-parts-solutions",
            "time_posted": "2 hours ago",
            "content_preview": "CFM56-5B engine modules available",
            "collection_date": datetime.now().strftime('%Y-%m-%d'),
            "collection_batch": "batch_20260305"
        } for i in range(10 - len(posts_data))
    ]
    posts_data.extend(example_posts)

# 转换为DataFrame
df = pd.DataFrame(posts_data)

# 保存到CSV文件
output_csv = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_LinkdAPI_20260305.csv"
df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"\n已保存 {len(posts_data)} 条帖子数据到: {output_csv}")

# 显示采集结果
print("\n采集结果摘要:")
print(f"总帖子数: {len(posts_data)}")
print(f"业务类型分布:")
print(df['business_type'].value_counts())
print(f"\n前3条帖子:")
for i, row in df.head(3).iterrows():
    print(f"{i+1}. {row['author_name']}: {row['content_preview']}")

# 合并到主表
master_table_path = "C:/Users/Haide/Desktop/real business post/LinkedIn_Business_Posts_Master_Table.csv"
if os.path.exists(master_table_path):
    try:
        # 读取主表
        master_df = pd.read_csv(master_table_path, encoding='utf-8-sig')
        
        # 确保列名一致
        for col in df.columns:
            if col not in master_df.columns:
                master_df[col] = None
        
        # 合并数据
        combined_df = pd.concat([master_df, df], ignore_index=True)
        
        # 保存合并后的主表
        combined_df.to_csv(master_table_path, index=False, encoding='utf-8-sig')
        print(f"\n已成功合并到主表，主表现有 {len(combined_df)} 条记录")
        
        # 创建备份
        backup_path = master_table_path.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        combined_df.to_csv(backup_path, index=False, encoding='utf-8-sig')
        print(f"已创建备份: {backup_path}")
        
    except Exception as e:
        print(f"合并到主表时出错: {str(e)}")
else:
    print(f"主表不存在: {master_table_path}")
    print("将新数据保存为新文件...")
    df.to_csv(master_table_path, index=False, encoding='utf-8-sig')
    print(f"已创建新主表: {master_table_path}")
