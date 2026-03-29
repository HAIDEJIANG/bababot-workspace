# Example MCP Calls for Job Search
This file contains example MCP tool calls and their expected outputs.

## Basic Search

### Request
```json
{
 "tool": "scrape_jobs_tool",
 "params": {
 "search_term": "software engineer",
 "location": "San Francisco, CA",
 "results_wanted": 10,
 "site_name": ["indeed", "linkedin"]
 }
```

### Response
"jobs": [
 "title": "Software Engineer",
 "company": "TechCorp Inc.",
 "company_url": "https://techcorp.com",
 "job_url": "https://indeed.com/viewjob?jk=abc123",
 "location": {
 "city": "San Francisco",
 "state": "CA",
 "country": "USA"
 },
 "is_remote": false,
 "description": "We are looking for a talented Software Engineer to join our team...",
 "job_type": "fulltime",
 "salary": {
 "min_amount": 120000,
 "max_amount": 180000,
 "interval": "yearly",
 "currency": "USD"
 "date_posted": "2024-01-28"
 "title": "Senior Software Engineer",
 "company": "StartupXYZ",
 "job_url": "https://linkedin.com/jobs/view/123456789",
 "is_remote": true,
 "description": "Join our growing team as a Senior Software Engineer...",
 "job_level": "Senior",
 "date_posted": "2024-01-27"
 ],
 "total_found": 10

---

## Remote Jobs Search
"search_term": "Python developer",
 "location": "Remote",
 "site_name": ["indeed", "zip_recruiter"],
 "results_wanted": 20

## Recent Data Science Jobs
"search_term": "data scientist",
 "location": "Boston, MA",
 "hours_old": 48,
 "site_name": ["linkedin", "glassdoor", "indeed"],
 "linkedin_fetch_description": true

## Entry-Level with Easy Apply
"search_term": "junior developer",
 "location": "New York, NY",
 "easy_apply": true,
 "results_wanted": 30

## International Search (Germany)
"search_term": "software developer",
 "location": "Berlin",
 "country_indeed": "germany",
 "site_name": ["indeed"],
 "results_wanted": 15

## Helper Tools

### Get Supported Sites
"tool": "get_supported_sites",
 "params": {}

### Get Supported Countries
"tool": "get_supported_countries",

### Get Job Search Tips
"tool": "get_job_search_tips",