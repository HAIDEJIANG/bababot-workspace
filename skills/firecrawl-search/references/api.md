# Firecrawl API Reference

## Environment
Set your API key:
```bash
export FIRECRAWL_API_KEY=fc-xxxxxxxxxx
```

## API Endpoints

### Search
POST https://api.firecrawl.dev/v1/search

Request body:
```json
{
 "query": "search terms",
 "limit": 10,
 "lang": "en",
 "country": "us"
}

### Scrape
POST https://api.firecrawl.dev/v1/scrape

 "url": "https://example.com",
 "formats": ["markdown", "html", "screenshot"],
 "onlyMainContent": true,
 "includeTags": ["h1", "p", "article"],
 "excludeTags": ["nav", "footer", "aside"]

### Crawl
POST https://api.firecrawl.dev/v1/crawl

 "limit": 50,
 "excludePaths": ["/blog", "/admin"],
 "scrapeOptions": {
 "formats": ["markdown"],
 "onlyMainContent": true

Check status:
GET https://api.firecrawl.dev/v1/crawl/{job_id}

## Response Format
All responses follow this structure:
 "success": true,
 "data": { ... },
 "status": "completed"

## Rate Limits
- Search: Check your Firecrawl dashboard

## Pricing
See https://firecrawl.dev/pricing for current rates.