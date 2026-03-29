# API Reference
Complete function reference for all DataForSEO API modules.

## Table of Contents
- [Keywords Data API](#keywords-data-api) (4 functions)
- [Labs API](#labs-api) (9 functions)
- [SERP API](#serp-api) (6 functions)
- [Trends API](#trends-api) (6 functions)

---

## Keywords Data API
Import: `from api.keywords_data import ...`

### `get_search_volume(keywords, location_name, language_name, save)`
Get search volume, CPC, and competition data for keywords.

`keywords`, Type=`List[str]`, Default=required, Description=Keywords to analyze (max 700)
`location_name`, Type=`str`, Default="United States", Description=Target location
`language_name`, Type=`str`, Default="English", Description=Target language
`save`, Type=`bool`, Default=`True`, Description=Save results to JSON

**Returns:** Dict with search volume, CPC, and competition for each keyword.

### `get_keywords_for_site(target_domain, location_name, language_name, save)`
Get keywords associated with a specific domain.

| `target_domain` | `str` | required | Domain to analyze (e.g., "example.com") |

**Returns:** Dict with keywords relevant to the domain.

### `get_ad_traffic_by_keywords(keywords, location_name, language_name, bid, save)`
Estimate advertising traffic potential for keywords at a given CPC bid.

| `keywords` | `List[str]` | required | Keywords to analyze |
| `bid` | `float` | `2.0` | Maximum CPC bid for estimation |

**Returns:** Dict with traffic estimates for the given bid.

### `get_keywords_for_keywords(keywords, location_name, language_name, save)`
Get keyword expansion ideas from Google Ads Keyword Planner.

| `keywords` | `List[str]` | required | Seed keywords (max 20) |

**Returns:** Dict with expanded keyword ideas.

## Labs API
Import: `from api.labs import ...`

### `get_keyword_overview(keywords, location_name, language_name, include_serp_info, save)`
Comprehensive keyword data: search volume, CPC, competition, and search intent.

| `include_serp_info` | `bool` | `False` | Include SERP features data |

**Returns:** Dict with comprehensive keyword metrics.

### `get_keyword_suggestions(keyword, location_name, language_name, include_seed_keyword, include_serp_info, limit, save)`
Get long-tail keyword suggestions based on a seed keyword.

| `keyword` | `str` | required | Seed keyword (min 3 characters) |
| `include_seed_keyword` | `bool` | `True` | Include seed keyword metrics |
| `include_serp_info` | `bool` | `False` | Include SERP data per keyword |
| `limit` | `int` | `100` | Max results (max 1000) |

**Returns:** Dict with keyword suggestions and metrics.

### `get_keyword_ideas(keywords, location_name, language_name, include_serp_info, closely_variants, limit, save)`
Get keyword ideas from the same category as seed keywords. Goes beyond semantic similarity.

| `keywords` | `List[str]` | required | Seed keywords (max 200) |
| `include_serp_info` | `bool` | `False` | Include SERP data |
| `closely_variants` | `bool` | `False` | Phrase-match (True) vs broad-match (False) |
| `limit` | `int` | `700` | Max results (max 1000) |

**Returns:** Dict with keyword ideas and metrics.

### `get_related_keywords(keyword, location_name, language_name, depth, include_seed_keyword, include_serp_info, limit, save)`
Get keywords from Google's "searches related to" feature using depth-first search.

| `keyword` | `str` | required | Seed keyword |
| `depth` | `int` | `2` | Search depth 0-4 (4 = max ~4680 results) |

**Returns:** Dict with related keywords and metrics.

### `get_bulk_keyword_difficulty(keywords, location_name, language_name, save)`
Get keyword difficulty scores (0-100) indicating how hard it is to rank in the top 10.

| `keywords` | `List[str]` | required | Keywords to analyze (max 1000) |

**Returns:** Dict with difficulty scores for each keyword.

### `get_historical_search_volume(keywords, location_name, language_name, include_serp_info, save)`
Get monthly search volume data since 2019.

| `include_serp_info` | `bool` | `False` | Include SERP features |

**Returns:** Dict with historical search volume and monthly breakdowns.

### `get_search_intent(keywords, location_name, language_name, save)`
Classify keywords as informational, navigational, transactional, or commercial.

| `keywords` | `List[str]` | required | Keywords to classify (max 1000) |

**Returns:** Dict with intent classifications for each keyword.

### `get_domain_keywords(target_domain, location_name, language_name, limit, save)`
Get keywords that a domain ranks for in organic search.

| `limit` | `int` | `100` | Max results |

**Returns:** Dict with keywords the domain ranks for.

### `get_competitors(keywords, location_name, language_name, limit, save)`
Find domains that compete for the same keywords.

| `keywords` | `List[str]` | required | Keywords to find competitors for |
| `limit` | `int` | `20` | Max competitors to return |

**Returns:** Dict with competitor domains and their metrics.

## SERP API
Import: `from api.serp import ...`

### `get_google_serp(keyword, location_name, language_name, depth, device, save)`
Get Google organic search results for a keyword.

| `keyword` | `str` | required | Search query |
| `depth` | `int` | `100` | Number of results (max 700) |
| `device` | `str` | `"desktop"` | `"desktop"` or `"mobile"` |

**Returns:** Dict with SERP data including rankings, URLs, titles, and SERP features.

### `get_youtube_serp(keyword, location_name, language_name, depth, device, save)`
Get YouTube organic search results for a keyword.

| `keyword` | `str` | required | Search query (max 700 chars) |
| `depth` | `int` | `20` | Number of results (max 700, billed per 20) |

**Returns:** Dict with YouTube video rankings, titles, channels, views.

### `get_google_maps_serp(keyword, location_name, language_name, depth, save)`
Get Google Maps/Local search results.

| `keyword` | `str` | required | Search query (e.g., "restaurants near me") |
| `depth` | `int` | `20` | Number of results |

**Returns:** Dict with local business listings.

### `get_google_news_serp(keyword, location_name, language_name, depth, save)`
Get Google News search results.

| `depth` | `int` | `100` | Number of results |

**Returns:** Dict with news articles and rankings.

### `get_google_images_serp(keyword, location_name, language_name, depth, save)`
Get Google Images search results.

**Returns:** Dict with image results including URLs, titles, sources.

### `get_featured_snippet(keyword, location_name, language_name, save)`
Get Google SERP focused on featured snippets and SERP features. Returns top 10 results on desktop.

| `keyword` | `str` | required | Search query (ideally a question) |

**Returns:** Dict with SERP data including featured snippet details.

## Trends API
Import: `from api.trends import ...`

### `get_trends_explore(keywords, location_name, search_type, time_range, date_from, date_to, category_code, save)`
Get Google Trends data for keywords.

| `keywords` | `List[str]` | required | Keywords to compare (max 5) |
| `search_type` | `str` | `"web"` | `"web"`, `"news"`, `"youtube"`, `"images"`, `"froogle"` (shopping) |
| `time_range` | `str` | `"past_12_months"` | `"past_hour"`, `"past_4_hours"`, `"past_day"`, `"past_7_days"`, `"past_month"`, `"past_3_months"`, `"past_12_months"`, `"past_5_years"` |
| `date_from` | `str` | `None` | Custom start date (yyyy-mm-dd), overrides time_range |
| `date_to` | `str` | `None` | Custom end date (yyyy-mm-dd) |
| `category_code` | `int` | `None` | Google Trends category filter |

**Returns:** Dict with trend graphs, regional interest, related topics and queries.

### `get_youtube_trends(keywords, location_name, time_range, save)`
YouTube-specific trend data. Convenience wrapper for `get_trends_explore` with `search_type="youtube"`.

| `time_range` | `str` | `"past_12_months"` | Time range |

**Returns:** Dict with YouTube trend data.

### `get_news_trends(keywords, location_name, time_range, save)`
Google News trend data. Convenience wrapper for `get_trends_explore` with `search_type="news"`.

**Returns:** Dict with news trend data.

### `get_shopping_trends(keywords, location_name, time_range, save)`
Google Shopping trend data. Convenience wrapper for `get_trends_explore` with `search_type="froogle"`.

**Returns:** Dict with shopping/e-commerce trend data.

### `compare_keyword_trends(keywords, location_name, search_types, time_range, save)`
Compare keyword trends across multiple search platforms.

| `search_types` | `List[str]` | `["web", "youtube"]` | Platforms to compare |
| `save` | `bool` | `True` | Save individual results |

**Returns:** Dict with search_type keys and trend data values.

### `get_trending_now(location_name, save)`
Get currently trending searches in real-time.

**Returns:** Dict with currently trending searches.