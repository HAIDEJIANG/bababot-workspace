# NetPad API v1 - Complete Endpoint Reference
Base URL: `https://www.netpad.io/api/v1`

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer np_live_xxx

Live, Format=`np_live_xxx`, Usage=Production forms (published only)
Test, Format=`np_test_xxx`, Usage=Testing (can submit to drafts)

---

## Projects
GET, Endpoint=`/projects`, Description=List all projects

### Response: List Projects
```json
{
 "success": true,
 "data": [
 "projectId": "proj_xxx",
 "name": "Project Name",
 "slug": "project-name",
 "description": "Project description",
 "organizationId": "org_xxx",
 "createdAt": "2026-01-01T00:00:00.000Z"
 }
 ],
 "requestId": "uuid"

## Forms
| GET | `/forms` | List all forms |
| POST | `/forms` | Create form |
| GET | `/forms/{formId}` | Get form details |
| PATCH | `/forms/{formId}` | Update form |
| DELETE | `/forms/{formId}` | Delete form |

### Query Parameters: List Forms
page, Type=int, Default=1, Description=Page number
pageSize, Type=int, Default=20, Description=Items per page (max 100)
status, Type=string, Default=-, Description=Filter: `draft` or `published`
search, Type=string, Default=-, Description=Search name/description

### Request: Create Form
"name": "Form Name",
 "description": "Optional description",
 "slug": "url-friendly-slug",
 "fields": [
 "path": "fieldName",
 "label": "Display Label",
 "type": "text",
 "required": true,
 "placeholder": "Hint text",
 "helpText": "Additional guidance",
 "validation": {
 "minLength": 1,
 "maxLength": 500
 ]

### Request: Update Form
"name": "Updated Name",
 "description": "Updated description",
 "status": "published",
 "fields": [...]

### Response: Form Detail
"data": {
 "id": "frm_xxx",
 "slug": "contact-form",
 "name": "Contact Form",
 "description": "A simple contact form",
 "responseCount": 42,
 "fields": [...],
 "settings": {
 "submitButtonText": "Submit",
 "successMessage": "Thank you!",
 "redirectUrl": null
 },
 "createdAt": "2026-01-01T00:00:00.000Z",
 "updatedAt": "2026-01-15T00:00:00.000Z",
 "publishedAt": "2026-01-02T00:00:00.000Z"

## Submissions
| GET | `/forms/{formId}/submissions` | List submissions |
| POST | `/forms/{formId}/submissions` | Create submission |
| GET | `/forms/{formId}/submissions/{submissionId}` | Get submission |
| DELETE | `/forms/{formId}/submissions/{submissionId}` | Delete submission |

### Query Parameters: List Submissions
| startDate | datetime | - | Filter after date |
| endDate | datetime | - | Filter before date |
| sortBy | string | submittedAt | Sort field |
| sortOrder | string | desc | `asc` or `desc` |

### Request: Create Submission
"name": "John Doe",
 "email": "john@example.com",
 "message": "Hello!"
 "metadata": {
 "referrer": "https://example.com",
 "customFields": {
 "campaign": "winter2026"

### Response: Submission Detail
"id": "sub_xxx",
 "formId": "frm_xxx",
 "submittedAt": "2026-01-15T12:00:00.000Z",
 "ipAddress": "192.168.1.1",
 "userAgent": "Mozilla/5.0...",
 "referrer": "https://example.com"

## System
| GET | `/health` | Health check |

### Response: Health Check
"status": "healthy",
 "timestamp": "2026-01-15T12:00:00.000Z",
 "version": "1.0.0",
 "services": {
 "api": {"status": "up", "responseTime": 5},
 "database": {"status": "up", "responseTime": 12}

## Field Types
`text`, HTML Equivalent=`<input type="text">`, Validation Options=minLength, maxLength, pattern
`email`, HTML Equivalent=`<input type="email">`, Validation Options=Built-in email format
`phone`, HTML Equivalent=`<input type="tel">`, Validation Options=Built-in phone format
`number`, HTML Equivalent=`<input type="number">`, Validation Options=min, max
`date`, HTML Equivalent=`<input type="date">`, Validation Options=-
`select`, HTML Equivalent=`<select>`, Validation Options=options array
`checkbox`, HTML Equivalent=`<input type="checkbox">`, Validation Options=-
`textarea`, HTML Equivalent=`<textarea>`, Validation Options=minLength, maxLength
`file`, HTML Equivalent=`<input type="file">`, Validation Options=-

### Field Options (for select)
"path": "country",
 "label": "Country",
 "type": "select",
 "options": [
 {"value": "us", "label": "United States"},
 {"value": "ca", "label": "Canada"},
 {"value": "uk", "label": "United Kingdom"}

### Field Validation
"path": "age",
 "label": "Age",
 "type": "number",
 "min": 18,
 "max": 120

 "path": "zipcode",
 "label": "ZIP Code",
 "pattern": "^\\d{5}(-\\d{4})?$"

## Error Codes
`INVALID_API_KEY`, HTTP Status=401, Description=Missing or invalid API key
`FORBIDDEN`, HTTP Status=403, Description=No access to resource
`NOT_FOUND`, HTTP Status=404, Description=Resource doesn't exist
`VALIDATION_ERROR`, HTTP Status=400, Description=Invalid request body
`DUPLICATE_SLUG`, HTTP Status=409, Description=Slug already in use
`RATE_LIMIT_EXCEEDED`, HTTP Status=429, Description=Too many requests
`FORM_NOT_PUBLISHED`, HTTP Status=400, Description=Form is draft (use test key)

### Error Response Format
"success": false,
 "error": {
 "code": "VALIDATION_ERROR",
 "message": "Human-readable description",
 "details": {
 "field": "email",
 "reason": "Invalid email format"

## Rate Limits
- Requests per hour: 1,000

### Rate Limit Headers
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704067200
Retry-After: 3600

## Pagination
All list endpoints support pagination:

 "data": [...],
 "pagination": {
 "total": 100,
 "page": 1,
 "pageSize": 20,
 "totalPages": 5,
 "hasMore": true

To iterate all pages:

```bash
page=1
while true; do
 result=$(curl -s -H "Authorization: Bearer $NETPAD_API_KEY" \
 "https://www.netpad.io/api/v1/forms/$FORM_ID/submissions?page=$page&pageSize=100")

 echo "$result" | jq -r '.data[]'

 hasMore=$(echo "$result" | jq -r '.pagination.hasMore')
 [[ "$hasMore" != "true" ]] && break
 ((page++))
done