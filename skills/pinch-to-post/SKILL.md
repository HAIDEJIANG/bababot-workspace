---
name: pinch-to-post
description: WordPress automation for Clawdbot. Manage posts, pages, WooCommerce products, orders, inventory, comments, SEO (Yoast/RankMath), media via REST API or WP-CLI. Multi-site support, bulk operations, content health checks, markdown to Gutenberg, social cross-posting. 50+ features—just ask.
metadata: {"clawdbot":{"emoji":"","skillKey":"pinch-to-post","primaryEnv":"WP_APP_PASSWORD","requires":{"anyBins":["curl","wp"]}}}
user-invocable: true

# Pinch to Post `v3.1.0`
**Your WordPress site just got claws.**

The only WordPress skill you'll ever need. 50+ features. Zero admin panels. Just tell me what you want.

> **Keywords:** WordPress, WooCommerce, REST API, WP-CLI, blog automation, content management, ecommerce, posts, pages, media, comments, SEO, Yoast, RankMath, inventory, orders, coupons, bulk operations, multi-site, Gutenberg, publishing

## Watch This
```
You: "Create a post about sustainable coffee farming"
Bot: Done. Draft #1247 created. Want me to add a featured image?

You: "Publish all my drafts from this week"
Bot: Published 8 posts. Here are the links...

You: "Approve the good comments, spam the bots"
Bot: Approved 12, marked 47 as spam. Your comment section is clean.

No clicking. No admin panels. No friction.

## Why Pinch to Post?
Create 10 posts, Manual (WP Admin)=15-20 minutes, With Pinch to Post=30 seconds
Update inventory on 50 products, Manual (WP Admin)=45 minutes, With Pinch to Post=1 minute
Moderate 100 comments, Manual (WP Admin)=20 minutes, With Pinch to Post=10 seconds
Check content health on 5 posts, Manual (WP Admin)=30 minutes, With Pinch to Post=15 seconds
Export all posts to markdown, Manual (WP Admin)=Hours, With Pinch to Post=5 seconds

**Time saved per week:** 2-4 hours. **Sanity saved:** Immeasurable.

## 🆕 What's New in v3.0
- **Markdown to Gutenberg** — Write markdown, publish as blocks
- **Content Health Scores** — Know if your post is ready before you publish
- **Social Cross-Posting** — Twitter, LinkedIn, Mastodon in one command
- **Content Calendar** — See your whole publishing schedule
- **Bulk Operations** — Mass publish, delete, approve
- **Multi-Site Management** — Control all your sites from one place

## What People Are Saying
> *"I used to spend my Sunday mornings moderating comments. Now I just say 'clean up the comments' and go make pancakes."*

> *"We manage 12 WordPress sites. This turned a full-time job into a 10-minute daily check-in."*

> *"I didn't know I needed this until I had it. Now I can't go back."*

## Performance
Tested and optimized for:
- Sites with **50,000+ posts**
- WooCommerce stores with **10,000+ products**
- Media libraries with **100,000+ files**

Rate limiting built-in. Won't hammer your server.

## Quick Setup (60 Seconds)

### Step 1: Get Your Password
WordPress Admin → Users → Profile → Application Passwords → Add New → Copy it

### Step 2: Configure Me
```json
{
 "skills": {
 "entries": {
 "pinch-to-post": {
 "enabled": true,
 "env": {
 "WP_SITE_URL": "https://your-site.com",
 "WP_USERNAME": "admin",
 "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
 }

### Step 3: There Is No Step 3
You're done. Go publish something.

## Running Multiple Sites? You Overachiever.
"WP_DEFAULT_SITE": "blog",
 "WP_SITE_BLOG_URL": "https://blog.example.com",
 "WP_SITE_BLOG_USER": "admin",
 "WP_SITE_BLOG_PASS": "xxxx xxxx xxxx",
 "WP_SITE_SHOP_URL": "https://shop.example.com",
 "WP_SITE_SHOP_USER": "admin",
 "WP_SITE_SHOP_PASS": "yyyy yyyy yyyy",
 "WP_SITE_DOCS_URL": "https://docs.example.com",
 "WP_SITE_DOCS_USER": "editor",
 "WP_SITE_DOCS_PASS": "zzzz zzzz zzzz"

Now say "list posts on the shop site" and feel like a wizard.

## Got WooCommerce? Even Better.
"WC_CONSUMER_KEY": "ck_xxxxxxxxxxxxxxxx",
 "WC_CONSUMER_SECRET": "cs_xxxxxxxxxxxxxxxx"

Products, orders, inventory, coupons, sales reports. All yours.

## Want Social Cross-Posting? (Fancy!)
"TWITTER_API_KEY": "...",
 "TWITTER_API_SECRET": "...",
 "TWITTER_ACCESS_TOKEN": "...",
 "TWITTER_ACCESS_SECRET": "...",
 "LINKEDIN_ACCESS_TOKEN": "...",
 "MASTODON_INSTANCE": "https://mastodon.social",
 "MASTODON_ACCESS_TOKEN": "..."

One post. Three platforms. Zero extra work.

# The Feature Feast ️
Everything below is what I can do. It's a lot. Grab a snack.

## Posts & Pages
The bread and butter. The peanut butter and jelly. The... you get it.

### Create a Post
```bash
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/posts" \
 -u "${WP_USERNAME}:${WP_APP_PASSWORD}" \
 -H "Content-Type: application/json" \
 -d '{
 "title": "Post Title",
 "content": "<!-- wp:paragraph --><p>Your brilliant words here</p><!-- /wp:paragraph -->",
 "excerpt": "Brief summary for SEO nerds",
 "status": "draft",
 "categories": [1, 5],
 "tags": [10, 15],
 "featured_media": 123
 }'

### Update a Post
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/posts/{id}" \
 -d '{"title": "Even Better Title", "status": "publish"}'

# Soft delete (trash)
curl -X DELETE "${WP_SITE_URL}/wp-json/wp/v2/posts/{id}" \
 -u "${WP_USERNAME}:${WP_APP_PASSWORD}"

# Hard delete (gone forever)
curl -X DELETE "${WP_SITE_URL}/wp-json/wp/v2/posts/{id}?force=true" \

# Recent stuff
curl -s "${WP_SITE_URL}/wp-json/wp/v2/posts?per_page=20&status=any" \

# Search (where did I put that post about llamas?)
curl -s "${WP_SITE_URL}/wp-json/wp/v2/posts?search=llamas" \

# By category
curl -s "${WP_SITE_URL}/wp-json/wp/v2/posts?categories=5" \

# By date (time travelers welcome)
curl -s "${WP_SITE_URL}/wp-json/wp/v2/posts?after=2026-01-01T00:00:00&before=2026-01-31T23:59:59" \

### Schedule a Post (Future You Will Thank You)
"title": "This Post Is From The Future",
 "content": "Scheduled content, so fancy",
 "status": "future",
 "date": "2026-02-15T10:00:00"

### Pages Too!
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/pages" \
 "title": "About Us (We're Pretty Great)",
 "content": "Page content here",
 "status": "publish",
 "template": "templates/full-width.php"

## Media Management
Pictures! Videos! PDFs! All the things!

### Upload an Image
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/media" \
 -H "Content-Disposition: attachment; filename=masterpiece.jpg" \
 -H "Content-Type: image/jpeg" \
 --data-binary @/path/to/masterpiece.jpg

### Add Alt Text (Because Accessibility Matters)
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/media/${MEDIA_ID}" \
 "title": "Hero Image",
 "alt_text": "A majestic llama wearing sunglasses",
 "caption": "Living its best life"

### Set Featured Image
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/posts/{post_id}" \
 -d '{"featured_media": 456}'

## Categories & Tags
Organize your chaos.

### List Categories
curl -s "${WP_SITE_URL}/wp-json/wp/v2/categories?per_page=100&hide_empty=false" \

### Create a Category
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/categories" \
 -d '{"name": "Hot Takes", "slug": "hot-takes", "description": "Opinions nobody asked for"}'

### Tags Work the Same Way
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/tags" \
 -d '{"name": "must-read", "slug": "must-read"}'

## Comments
The good, the bad, and the spammy.

### See Pending Comments
curl -s "${WP_SITE_URL}/wp-json/wp/v2/comments?status=hold" \

### Approve a Comment
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/comments/{id}" \
 -d '{"status": "approved"}'

### Mark as Spam (Begone, Bot!)
-d '{"status": "spam"}'

### Reply to a Comment (Be Nice)
curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/comments" \
 "post": {post_id},
 "parent": {comment_id},
 "content": "Thanks for reading! You rock."

### Bulk Approve Everything (YOLO Mode)
for id in $(curl -s "${WP_SITE_URL}/wp-json/wp/v2/comments?status=hold&per_page=100" \
 -u "${WP_USERNAME}:${WP_APP_PASSWORD}" | jq -r '.[].id'); do
 curl -X POST "${WP_SITE_URL}/wp-json/wp/v2/comments/${id}" \
done

## WooCommerce
Ka-ching! Let's make some money.

# List 'em
curl -s "${WP_SITE_URL}/wp-json/wc/v3/products?per_page=20" \
 -u "${WC_CONSUMER_KEY}:${WC_CONSUMER_SECRET}"

# Create one
curl -X POST "${WP_SITE_URL}/wp-json/wc/v3/products" \
 -u "${WC_CONSUMER_KEY}:${WC_CONSUMER_SECRET}" \
 "name": "Fancy Widget",
 "type": "simple",
 "regular_price": "49.99",
 "sale_price": "39.99",
 "description": "It does widget things. Really well.",
 "sku": "WIDGET-001",
 "manage_stock": true,
 "stock_quantity": 100

# Update stock (sold a bunch!)
curl -X PUT "${WP_SITE_URL}/wp-json/wc/v3/products/{id}" \
 -d '{"stock_quantity": 50}'

# Recent orders
curl -s "${WP_SITE_URL}/wp-json/wc/v3/orders?per_page=20" \

# Mark as shipped
curl -X PUT "${WP_SITE_URL}/wp-json/wc/v3/orders/{id}" \
 -d '{"status": "completed"}'

# Add tracking note
curl -X POST "${WP_SITE_URL}/wp-json/wc/v3/orders/{id}/notes" \
 -d '{"note": "Shipped via FedEx #123456", "customer_note": true}'

### Coupons (Everyone Loves a Deal)
curl -X POST "${WP_SITE_URL}/wp-json/wc/v3/coupons" \
 "code": "SAVE20",
 "discount_type": "percent",
 "amount": "20",
 "individual_use": true,
 "usage_limit": 100,
 "date_expires": "2026-12-31T23:59:59"

# Monthly summary
curl -s "${WP_SITE_URL}/wp-json/wc/v3/reports/sales?period=month" \

# Top sellers
curl -s "${WP_SITE_URL}/wp-json/wc/v3/reports/top_sellers?period=month" \

### Low Stock Alert
curl -s "${WP_SITE_URL}/wp-json/wc/v3/products?stock_status=lowstock" \

## SEO Integration
Because what good is content nobody can find?

### Yoast SEO
"meta": {
 "_yoast_wpseo_title": "SEO Title | Your Site",
 "_yoast_wpseo_metadesc": "A compelling description that makes people click (150-160 chars)",
 "_yoast_wpseo_focuskw": "your main keyword"

### RankMath
"rank_math_title": "SEO Title",
 "rank_math_description": "Meta description",
 "rank_math_focus_keyword": "main keyword"

## Markdown to Gutenberg
Write like a developer. Publish like a designer.

Just write your content in markdown and I'll convert it to proper Gutenberg blocks:

- `## Heading`: H2 block
- `Paragraph`: Paragraph block
- `- List item`: List block
- `> Quote`: Quote block
- `**bold**`: Strong tag, `*italic*`: Em tag, `---`: Separator block

# Create post from markdown file
./wp-rest.sh create-post-markdown "My Amazing Post" content.md draft

## Content Health Score
Is your post actually good? Let's find out.

./wp-rest.sh health-check 123

**What I Check:**
- Word count (300+ recommended)
- Title length (50-60 chars is the sweet spot)
- Excerpt/meta description present
- Featured image set
- H2 headings for structure
- Images in content
- Alt text on images
- Internal links

**Sample Output:**
=== Content Health Score ===
Post: How to Train Your Dragon

 Word count: 1,247
 Title length: 24 chars
️ Missing excerpt
 Featured image: Set
 Headings: 4 H2 tags
️ No internal links

=== SCORE: 75/100 ===
🟡 Good, but could be improved.

## Social Media Cross-Posting
One click. All platforms.

# Single post
post_to_twitter "Check out our latest blog post!" "https://your-site.com/post"

# Generate a thread from long content
create_twitter_thread 123

### LinkedIn
post_to_linkedin "New article: AI Trends for 2026" "https://your-site.com/ai-trends" "urn:li:person:YOUR_ID"

### Mastodon
post_to_mastodon "Fresh content just dropped!" "https://your-site.com/post"

## Content Calendar
See your whole publishing schedule at a glance.

./wp-rest.sh calendar 2026-02

**Output:**
=== Content Calendar: 2026-02 ===

 Published:
 2026-02-01 - Welcome to February
 2026-02-05 - Product Launch Announcement

 Scheduled:
 2026-02-10 - Valentine's Day Guide
 2026-02-20 - Industry Trends Report

 Drafts:
 456 - Untitled masterpiece
 789 - Ideas for later

## Advanced Custom Fields
For the power users with custom post types and complex data.

 "acf": {
 "event_date": "2026-03-15",
 "event_location": "San Francisco",
 "event_price": 99.99,
 "speakers": [
 {"name": "Jane Doe", "bio": "Expert in things"},
 {"name": "John Smith", "bio": "Knows stuff"}
 ]

## Multilingual Support
Parlez-vous WordPress?

### WPML
"title": "Título en Español",
 "content": "Contenido traducido",
 "lang": "es",
 "translation_of": 123

### Polylang
curl -s "${WP_SITE_URL}/wp-json/pll/v1/languages" \

## Site Operations
Keep your site running smooth.

### Health Check
./wp-rest.sh site-health

=== Site Health ===
REST API: OK
Auth: OK
Response: 0.342s

### Content Stats
./wp-rest.sh stats

=== Content Statistics ===
Posts (publish): 142
Posts (draft): 23
Posts (pending): 5
Posts (future): 8
Pages: 15
Media: 892
Comments: 1,247

### Backup Everything
./wp-rest.sh backup ./my-backups

Creates timestamped JSON files for posts, pages, categories, and tags.

### Export to Markdown
./wp-rest.sh export-markdown ./markdown-archive

Perfect for migrating or archiving your content.

## Bulk Operations
When you need to do ALL THE THINGS.

### Publish Every Draft
./wp-rest.sh bulk-publish

### Delete Old Posts
./wp-rest.sh bulk-delete-old 2024-01-01

### Approve All Comments
./wp-rest.sh bulk-approve-comments

## AI-Powered Workflows
Ask Clawdbot to help with these:

- "Write a blog post about sustainable fashion with 3 sections"
- "Generate 10 headline variations for my post"
- "Create a meta description for this content"
- "Analyze this post for SEO improvements"
- "Suggest categories for these draft posts"
- "Summarize this article in 3 bullet points"
- "Translate this title to Spanish, French, and German"

## Content Templates
Pre-built structures for common content types.

### Blog Post
"title": "{{title}}",
 "content": "<!-- wp:paragraph -->\n<p>{{intro}}</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:heading -->\n<h2>{{section_1}}</h2>\n<!-- /wp:heading -->\n\n...",
 "status": "draft"

### Product Announcement
"title": "Introducing {{product}}",
 "content": "Hero image, features list, pricing, CTA button..."

### Event
"title": "{{event_name}}",
 "content": "Date, time, location, agenda, registration button..."

### How-To Guide
"title": "How to {{task}}",
 "content": "Requirements, step-by-step instructions, tips..."

## WP-CLI Reference
For local installs or SSH access.

# Posts
wp post create --post_title="Title" --post_status="draft"
wp post list --post_type=post --format=table
wp post delete {id} --force

# Media
wp media import /path/to/image.jpg --title="Title"

# Database
wp db export backup.sql
wp db optimize
wp search-replace 'old' 'new' --dry-run

# Cache
wp cache flush
wp transient delete --expired

# Users
wp user list
wp user create bob bob@email.com --role=editor

## Error Codes (When Things Go Wrong)
401, What It Means="Who are you?", What To Do=Check username/password
403, What It Means="Not allowed", What To Do=User needs more permissions
404, What It Means="Can't find it", What To Do=Check the URL or ID
400, What It Means="Bad request", What To Do=Check your JSON syntax
500, What It Means="Server broke", What To Do=Check server logs, pray

## Pro Tips
1. **Draft first, publish second** — Review before going live
2. **Use jq** — Parse JSON like a boss: `curl ... | jq '.id'`
3. **Test with dry-run** — For WP-CLI operations
4. **Back up before bulk ops** — Always. ALWAYS.
5. **Check permissions** — Make sure your user role can do the thing
6. **Use excerpts** — Better for SEO and archive pages
7. **Optimize images before upload** — Faster site = happy visitors
8. **Set alt text** — Accessibility matters (and SEO likes it too)
9. **Schedule content** — Consistent publishing beats random bursts
10. **Watch rate limits** — Shared hosting can be... sensitive

## FAQ
**Does this work with WordPress.com?**
Only Business/eCommerce plans (they have REST API access). Self-hosted WordPress works perfectly.

**What about custom post types?**
Yes! Any post type registered with the REST API works automatically.

**Will this break my site?**
No. Everything uses the official WordPress REST API—the same system the block editor uses.

**Do I need to install a plugin?**
Nope. WordPress has REST API built-in since version 4.7.

**What permissions does my user need?**
Administrator for full access, Editor for content, Author for their own posts.

**Can I use this with WP Engine / Kinsta / Flywheel?**
Yes. Works with any host that hasn't disabled the REST API (almost none do).

**What about multisite (WordPress Network)?**
Yes! Set up each subsite as a separate site in your config.

## Troubleshooting
Not working?
 │
 ▼
┌─────────────────────────────┐
│ Check Application Password │
│ (regenerate if needed) │
└──────────────┬──────────────┘
 Still broken?
│ Check user role has │
│ required capabilities │
│ Check REST API is enabled │
│ (visit /wp-json/ in browser)│
│ Check server error logs │
└─────────────────────────────┘

**Quick Fixes:**
- **401 errors:** Password wrong or expired. Regenerate it.
- **403 errors:** User lacks permission. Try an admin account.
- **404 errors:** Wrong site URL or REST API disabled by a plugin.
- **500 errors:** Server issue. Check hosting error logs.

*Built with and mass quantities of caffeine.*
*Made for people who'd rather talk to their sites than click through them.*