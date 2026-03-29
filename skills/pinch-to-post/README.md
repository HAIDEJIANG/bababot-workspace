# Pinch to Post `v3.1.0`
**Your WordPress site just got claws.**

> **Keywords:** WordPress, WooCommerce, REST API, WP-CLI, blog automation, content management, ecommerce, posts, pages, media, comments, SEO, Yoast, RankMath, inventory, orders, coupons, bulk operations, multi-site, Gutenberg

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://clawdhub.com/skills/pinch-to-post)
[![Features](https://img.shields.io/badge/features-50+-green.svg)](#features)
[![Sites Tested](https://img.shields.io/badge/tested%20on-50k%2B%20posts-orange.svg)](#performance)

## See It In Action
```
You: "Create a post about sustainable coffee farming"
Bot: Done. Draft #1247 created. Want me to add a featured image?

You: "Publish all my drafts from this week"
Bot: Published 8 posts. Here are the links...

You: "What's low on stock in my store?"
Bot: 3 products under 10 units: Blue Widget (4), Red Gadget (7), Green Thing (2)

You: "Approve the good comments, spam the bots"
Bot: Approved 12, marked 47 as spam. Your comment section is clean.

**That's it.** No clicking. No admin panels. No friction.

## Why Pinch to Post?
Create 10 posts, Manual (WP Admin)=15-20 minutes, With Pinch to Post=30 seconds
Update inventory on 50 products, Manual (WP Admin)=45 minutes, With Pinch to Post=1 minute
Moderate 100 comments, Manual (WP Admin)=20 minutes, With Pinch to Post=10 seconds
Check content health on 5 posts, Manual (WP Admin)=30 minutes, With Pinch to Post=15 seconds
Export all posts to markdown, Manual (WP Admin)=Hours (with plugins), With Pinch to Post=5 seconds
Backup posts, pages, taxonomies, Manual (WP Admin)=Plugin + waiting, With Pinch to Post=Instant

**Time saved per week:** 2-4 hours
**Sanity saved:** Immeasurable

## 🆕 What's New in v3.0
- **Markdown to Gutenberg** — Write markdown, publish as blocks
- **Content Health Scores** — Know if your post is ready before you publish
- **Social Cross-Posting** — Twitter, LinkedIn, Mastodon in one command
- **Content Calendar** — See your whole publishing schedule
- **Bulk Operations** — Mass publish, delete, approve
- **Multi-Site Management** — Control all your WordPress sites from one place
- **WooCommerce Deep Integration** — Products, orders, coupons, reports

## What People Are Saying
> *"I used to spend my Sunday mornings moderating comments. Now I just say 'clean up the comments' and go make pancakes."*
> — Someone who likes pancakes

> *"We manage 12 WordPress sites. This turned a full-time job into a 10-minute daily check-in."*
> — Agency owner, probably

> *"I didn't know I needed this until I had it. Now I can't go back."*
> — Every user, eventually

## Quick Start (60 Seconds)

### Step 1: Get Your Password
WordPress Admin → Users → Profile → Application Passwords → Add New → Copy it

### Step 2: Configure
```json
{
 "skills": {
 "entries": {
 "pinch-to-post": {
 "enabled": true,
 "env": {
 "WP_SITE_URL": "https://your-site.com",
 "WP_USERNAME": "admin",
 "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx"
 }

### Step 3: There Is No Step 3
You're done. Say "create a test post" and watch the magic.

## Features
**Content Management**
- Posts, pages, media, revisions
- Categories, tags, custom taxonomies
- Markdown to Gutenberg conversion
- Content health scoring
- Scheduling and bulk operations

**WooCommerce**
- Products, variations, inventory, Orders, customers, notes, Coupons and discounts
- Sales reports and analytics

**Multi-Site**
- Manage unlimited WordPress sites
- Switch between sites mid-conversation
- Consistent commands across all sites

**SEO**
- Yoast SEO integration
- RankMath integration
- All in One SEO integration

**Comments**
- List, approve, spam, delete
- Reply to comments
- Bulk moderation

**Operations**
- Site health checks, Content statistics, Backup and export, Search and replace

## Performance
Tested and optimized for:
- Sites with **50,000+ posts**
- WooCommerce stores with **10,000+ products**
- Media libraries with **100,000+ files**
- Multi-site networks with **20+ sites**

Rate limiting built-in. Won't hammer your server.

## FAQ
**Does this work with WordPress.com?**
Only WordPress.com Business/eCommerce plans (they have REST API access). Self-hosted WordPress works perfectly.

**What about custom post types?**
Yes! Any post type registered with the REST API works out of the box.

**Will this break my site?**
No. Everything uses the official WordPress REST API—the same system the block editor uses. If your site works, this works.

**Do I need to install a plugin?**
Nope. WordPress has REST API built-in since version 4.7. Just generate an Application Password and you're set.

**What permissions does my user need?**
Administrator for full access, Editor for content management, Author for their own posts only.

**Is my password stored securely?**
Your Application Password stays in your local Clawdbot config. It's never sent anywhere except your own WordPress site.

**Can I use this with WP Engine / Kinsta / Flywheel?**
Yes. Works with any WordPress host that hasn't disabled the REST API (almost none do).

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
│ (hosting panel or wp-content│
│ /debug.log) │
└─────────────────────────────┘

**Common fixes:**
- **401 errors:** Password wrong or expired. Regenerate it.
- **403 errors:** User lacks permission. Try an admin account.
- **404 errors:** Wrong site URL or REST API disabled.
- **500 errors:** Server issue. Check hosting error logs.

## Install
```bash
clawdhub install pinch-to-post

Or tell Clawdbot: *"install the pinch-to-post skill"*

## Full Documentation
See the complete feature reference in the [SKILL.md](./SKILL.md) file.

## Links
- [ClawdHub](https://clawdhub.com/skills/pinch-to-post), [Clawdbot Docs](https://docs.clawd.bot/tools/skills), [WordPress REST API](https://developer.wordpress.org/rest-api/), [WooCommerce REST API](https://woocommerce.github.io/woocommerce-rest-api-docs/)

*Built with and mass quantities of caffeine.*
*Made for people who'd rather talk to their sites than click through them.*