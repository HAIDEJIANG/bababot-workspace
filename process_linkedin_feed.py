import json, csv, os, re
from datetime import datetime

def extract_posts_from_snapshot():
    """Extract posts from the LinkedIn snapshot data"""
    posts = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    batch_id = datetime.now().strftime('linkedin_batch_%Y%m%d_%H%M%S')
    
    # Post 3: Dragon Aviation Capital - ACIA Aero Leasing ATR delivery
    posts.append({
        'batch_id': f"{batch_id}_001",
        'timestamp': timestamp,
        'author': 'Dragon Aviation Capital (Singapore) Pte. Ltd.',
        'author_title': 'Aviation Capital Company',
        'content_type': 'repost',
        'summary': 'ACIA Aero Leasing announced delivery of third ATR 72-600 passenger aircraft on lease to PNG Air, Papua New Guinea. Partnership for fleet expansion with ATR72-600s providing efficiency for regional connectivity.',
        'tags': '飞机租赁,ATR72,交付',
        'business_value_score': '8',
        'urgency': '中',
        'has_contact': 'False',
        'contact_info': '',
        'post_time': '2h',
        'likes': '1',
        'comments': '0',
        'reposts': '0',
        'is_repost': 'True',
        'original_author': 'Emerald Media / ACIA Aero Leasing',
        'source_url': 'https://www.linkedin.com/feed/update/urn:li:activity:7432846134294876160/'
    })
    
    # Post 4: MEBAA - Aircraft Leasing & Finance course
    posts.append({
        'batch_id': f"{batch_id}_002",
        'timestamp': timestamp,
        'author': 'The Middle East and North Africa Business Aviation Association (MEBAA)',
        'author_title': 'Business Aviation Association',
        'content_type': 'course_promotion',
        'summary': 'Aircraft Leasing & Finance course promotion. Covers leasing structures, major lessors, aviation finance regulations, funding sources, airline credit risk, investment strategies, lease vs buy decisions.',
        'tags': '航空金融,租赁,培训',
        'business_value_score': '6',
        'urgency': '低',
        'has_contact': 'True',
        'contact_info': 'https://aim.edu.pk/AL',
        'post_time': '5h',
        'likes': '0',
        'comments': '0',
        'reposts': '0',
        'is_repost': 'False',
        'original_author': 'Dr. Wali Mughni',
        'source_url': 'https://www.linkedin.com/groups/2013235?q=highlightedFeedForGroups&highlightedUpdateUrn=urn%3Ali%3AgroupPost%3A2013235-7433104534320795649'
    })
    
    # Post 5: Abhi Krishna - Aircraft parts sales
    posts.append({
        'batch_id': f"{batch_id}_003",
        'timestamp': timestamp,
        'author': 'Abhi Krishna',
        'author_title': 'Aircrafts parts/consumables sales | Technical publication Team lead',
        'content_type': 'inventory_sales',
        'summary': 'New inventory available: B727 parts, PW engines for sale. Contact sales@aviano.in for details.',
        'tags': '航材,发动机销售,B727,PW',
        'business_value_score': '9',
        'urgency': '高',
        'has_contact': 'True',
        'contact_info': 'sales@aviano.in',
        'post_time': '9h',
        'likes': '4',
        'comments': '0',
        'reposts': '2',
        'is_repost': 'False',
        'original_author': 'Abhi Krishna',
        'source_url': 'https://www.linkedin.com/in/abhi-krishna-b73418243?miniProfileUrn=urn%3Ali%3Afsd_profile%3AACoAADxlbYcBZ3QXgLNHUsXsHGTt0N9GsziUUpY'
    })
    
    return posts

def write_batch_files(posts, output_dir):
    """Write posts to CSV, JSON, and MD files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # File paths
    csv_path = os.path.join(output_dir, f'LinkedIn_Business_Posts_新增_{timestamp}_batch_script.csv')
    json_path = os.path.join(output_dir, f'LinkedIn_Business_Posts_新增_{timestamp}_batch_script.json')
    md_path = os.path.join(output_dir, f'LinkedIn_Business_Posts_新增_{timestamp}_batch_script.md')
    
    # CSV fieldnames matching master table structure
    fieldnames = ['batch_id', 'timestamp', 'author', 'author_title', 'content_type', 
                  'summary', 'tags', 'business_value_score', 'urgency', 'has_contact',
                  'contact_info', 'post_time', 'likes', 'comments', 'reposts',
                  'is_repost', 'original_author', 'source_url']
    
    # Write CSV
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    
    # Write JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'collection_date': date_str,
            'batch_timestamp': timestamp,
            'total_posts': len(posts),
            'posts': posts
        }, f, ensure_ascii=False, indent=2)
    
    # Write Markdown report
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# LinkedIn Aviation Business Posts Report\n\n")
        f.write(f"**Collection Date:** {date_str}\n\n")
        f.write(f"**Batch ID:** {timestamp}\n\n")
        f.write(f"**Total Posts:** {len(posts)}\n\n")
        f.write("---\n\n")
        
        for i, post in enumerate(posts, 1):
            f.write(f"## Post {i}: {post['content_type']}\n\n")
            f.write(f"**Author:** {post['author']} ({post['author_title']})\n\n")
            f.write(f"**Tags:** {post['tags']}\n\n")
            f.write(f"**Business Value:** {post['business_value_score']}/10 | **Urgency:** {post['urgency']}\n\n")
            f.write(f"**Posted:** {post['post_time']} | **Engagement:** {post['likes']} likes, {post['comments']} comments, {post['reposts']} reposts\n\n")
            f.write(f"**Summary:** {post['summary']}\n\n")
            if post['has_contact'] == 'True':
                f.write(f"**Contact:** {post['contact_info']}\n\n")
            f.write(f"**Source:** [{post['source_url']}]({post['source_url']})\n\n")
            if post['is_repost'] == 'True':
                f.write(f"*Repost from: {post['original_author']}*\n\n")
            f.write("---\n\n")
    
    return csv_path, json_path, md_path

def update_master_table(new_posts, master_path):
    """Update master CSV with new posts, avoiding duplicates"""
    
    # CSV fieldnames matching master table structure
    fieldnames = ['batch_id', 'timestamp', 'author', 'author_title', 'content_type', 
                  'summary', 'tags', 'business_value_score', 'urgency', 'has_contact',
                  'contact_info', 'post_time', 'likes', 'comments', 'reposts',
                  'is_repost', 'original_author', 'source_url']
    
    # Read existing URLs to check for duplicates
    existing_urls = set()
    file_exists = os.path.exists(master_path)
    
    if file_exists:
        try:
            with open(master_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get('source_url', '')
                    if url:
                        existing_urls.add(url)
        except Exception as e:
            print(f"Warning: Could not read master file: {e}")
    
    # Filter new posts (avoid duplicates by source_url)
    unique_new_posts = [p for p in new_posts if p['source_url'] not in existing_urls]
    
    # Append to master file
    if file_exists and len(unique_new_posts) > 0:
        with open(master_path, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(unique_new_posts)
    elif len(unique_new_posts) > 0:
        # Create new file
        with open(master_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_new_posts)
    
    # Count total
    total_count = len(existing_urls) + len(unique_new_posts)
    
    return len(unique_new_posts), total_count

if __name__ == '__main__':
    # Output directory
    output_dir = r'C:\Users\Haide\Desktop\real business post'
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract posts
    posts = extract_posts_from_snapshot()
    
    # Write batch files
    csv_path, json_path, md_path = write_batch_files(posts, output_dir)
    
    # Update master table
    master_path = os.path.join(output_dir, 'LinkedIn_Business_Posts_Master_Table.csv')
    new_count, total_count = update_master_table(posts, master_path)
    
    # Print results
    print(f"[OK] Batch complete!")
    print(f"[*] New posts added: {new_count}")
    print(f"[*] Total posts in master: {total_count}")
    print(f"\n[Files] Output files:")
    print(f"   CSV: {csv_path}")
    print(f"   JSON: {json_path}")
    print(f"   MD: {md_path}")
    print(f"   Master: {master_path}")
