from cdp_client import CDPClient

c = CDPClient(port=9222)
t = c.find_linkedin_feed()
c.connect(t['id'])

info = c.get_page_info()
print(f'Page: {info}')

posts = c.extract_posts()
print(f'Posts: {len(posts)}')

for i, post in enumerate(posts[:5]):
    author = post.get('author', 'Unknown')[:30]
    text_len = len(post.get('text', ''))
    print(f'  [{i+1}] {author}... ({text_len} chars)')

c.disconnect()
