---
name: netpad
description: "Manage NetPad forms, submissions, users, and RBAC. Use when: (1) Creating forms with custom fields, (2) Submitting data to forms, (3) Querying form submissions, (4) Managing users/groups/roles (RBAC), (5) Installing NetPad apps from marketplace. Requires NETPAD_API_KEY for API, or `netpad login` for CLI."
metadata: {"clawdbot":{"emoji":"","requires":{"bins":["curl","jq","netpad"]},"install":[{"id":"cli","kind":"node","package":"@netpad/cli","bins":["netpad"],"label":"Install NetPad CLI (npm)"}],"author":{"name":"Michael Lynn","github":"mrlynn","website":"https://mlynn.org","linkedin":"https://linkedin.com/in/mlynn"}}}

# NetPad
Manage forms, submissions, users, and RBAC via CLI and REST API.

## Two Tools
`netpad` CLI, Install=`npm i -g @netpad/cli`, Purpose=RBAC, marketplace, packages
REST API, Install=curl + API key, Purpose=Forms, submissions, data

## Authentication
```bash
export NETPAD_API_KEY="np_live_xxx" # Production
export NETPAD_API_KEY="np_test_xxx" # Test (can submit to drafts)
```

All requests use Bearer token:
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
 "https://www.netpad.io/api/v1/..."

## Quick Reference
List projects, Endpoint=`/projects`, Method=GET
List forms, Endpoint=`/forms`, Method=GET
Create form, Endpoint=`/forms`, Method=POST
Get form, Endpoint=`/forms/{formId}`, Method=GET
Update/publish form, Endpoint=`/forms/{formId}`, Method=PATCH
Delete form, Endpoint=`/forms/{formId}`, Method=DELETE
List submissions, Endpoint=`/forms/{formId}/submissions`, Method=GET
Create submission, Endpoint=`/forms/{formId}/submissions`, Method=POST
Get submission, Endpoint=`/forms/{formId}/submissions/{id}`, Method=GET
Delete submission, Endpoint=`/forms/{formId}/submissions/{id}`, Method=DELETE

## Projects
Forms belong to projects. Get project ID before creating forms.

# List projects
"https://www.netpad.io/api/v1/projects" | jq '.data[] | {projectId, name}'

## Forms

### List Forms
"https://www.netpad.io/api/v1/forms?status=published&pageSize=50"

### Create Form
curl -X POST -H "Authorization: Bearer $NETPAD_API_KEY" \
 -H "Content-Type: application/json" \
 "https://www.netpad.io/api/v1/forms" \
 -d '{
 "name": "Contact Form",
 "description": "Simple contact form",
 "projectId": "proj_xxx",
 "fields": [
 {"path": "name", "label": "Name", "type": "text", "required": true},
 {"path": "email", "label": "Email", "type": "email", "required": true},
 {"path": "phone", "label": "Phone", "type": "phone"},
 {"path": "message", "label": "Message", "type": "textarea"}
 ]
 }'

### Get Form Details
"https://www.netpad.io/api/v1/forms/{formId}"

### Publish Form
curl -X PATCH -H "Authorization: Bearer $NETPAD_API_KEY" \
 "https://www.netpad.io/api/v1/forms/{formId}" \
 -d '{"status": "published"}'

### Update Form Fields
{"path": "name", "label": "Full Name", "type": "text", "required": true},
 {"path": "email", "label": "Email Address", "type": "email", "required": true},
 {"path": "company", "label": "Company", "type": "text"},
 {"path": "role", "label": "Role", "type": "select", "options": [
 {"value": "dev", "label": "Developer"},
 {"value": "pm", "label": "Product Manager"},
 {"value": "exec", "label": "Executive"}
 ]}

### Delete Form
curl -X DELETE -H "Authorization: Bearer $NETPAD_API_KEY" \

## Submissions

### Submit Data
"https://www.netpad.io/api/v1/forms/{formId}/submissions" \
 "data": {
 "name": "John Doe",
 "email": "john@example.com",
 "message": "Hello from the API!"
 }

# Recent submissions
"https://www.netpad.io/api/v1/forms/{formId}/submissions?pageSize=50"

# With date filter
"https://www.netpad.io/api/v1/forms/{formId}/submissions?startDate=2026-01-01T00:00:00Z"

# Sorted ascending
"https://www.netpad.io/api/v1/forms/{formId}/submissions?sortOrder=asc"

### Get Single Submission
"https://www.netpad.io/api/v1/forms/{formId}/submissions/{submissionId}"

## Field Types
`text`, Description=Single line text, Validation=minLength, maxLength, pattern
`email`, Description=Email address, Validation=Built-in validation
`phone`, Description=Phone number, Validation=Built-in validation
`number`, Description=Numeric input, Validation=min, max
`date`, Description=Date picker, Validation=-
`select`, Description=Dropdown, Validation=options: [{value, label}]
`checkbox`, Description=Boolean, Validation=-
`textarea`, Description=Multi-line text, Validation=minLength, maxLength
`file`, Description=File upload, Validation=-

### Field Schema
```json
{
 "path": "fieldName",
 "label": "Display Label",
 "type": "text",
 "required": true,
 "placeholder": "Hint text",
 "helpText": "Additional guidance",
 "options": [{"value": "a", "label": "Option A"}],
 "validation": {
 "minLength": 1,
 "maxLength": 500,
 "pattern": "^[A-Z].*",
 "min": 0,
 "max": 100

# 1. Create draft
RESULT=$(curl -s -X POST -H "Authorization: Bearer $NETPAD_API_KEY" \
 -d '{"name":"Survey","projectId":"proj_xxx","fields":[...]}')
FORM_ID=$(echo $RESULT | jq -r '.data.id')

# 2. Publish
"https://www.netpad.io/api/v1/forms/$FORM_ID" \
 -d '{"status":"published"}'

### Export All Submissions
"https://www.netpad.io/api/v1/forms/{formId}/submissions?pageSize=1000" \
 | jq '.data[].data'

### Bulk Submit
for row in $(cat data.json | jq -c '.[]'); do
 curl -s -X POST -H "Authorization: Bearer $NETPAD_API_KEY" \
 -d "{\"data\":$row}"
done

### Search Forms
"https://www.netpad.io/api/v1/forms?search=contact&status=published"

## Helper Script
Use `scripts/netpad.sh` for common operations:

# Make executable
chmod +x scripts/netpad.sh

# Usage
./scripts/netpad.sh projects list
./scripts/netpad.sh forms list published
./scripts/netpad.sh forms create "Contact Form" proj_xxx
./scripts/netpad.sh forms publish frm_xxx
./scripts/netpad.sh submissions list frm_xxx
./scripts/netpad.sh submissions create frm_xxx '{"name":"John","email":"john@example.com"}'
./scripts/netpad.sh submissions export frm_xxx > data.jsonl
./scripts/netpad.sh submissions count frm_xxx

## Rate Limits
- Requests/hour: 1,000

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Response Format

### Success
"success": true,
 "data": { ... },
 "pagination": {"total": 100, "page": 1, "pageSize": 20, "hasMore": true},
 "requestId": "uuid"

### Error
"success": false,
 "error": {
 "code": "VALIDATION_ERROR",
 "message": "Description",
 "details": {}
 },

# Required for REST API
export NETPAD_API_KEY="np_live_xxx"

# Optional (for local/staging)
export NETPAD_BASE_URL="https://staging.netpad.io/api/v1"

## NetPad CLI (@netpad/cli)
Install: `npm i -g @netpad/cli`

### Authentication
netpad login # Opens browser
netpad whoami # Check auth status
netpad logout # Clear credentials

# Search for apps
netpad search "helpdesk"

# Install an app
netpad install @netpad/helpdesk-app

# List installed
netpad list

# Create new app scaffold
netpad create-app my-app

# Submit to marketplace
netpad submit ./my-app

# List org members
netpad users list -o org_xxx

# Add user
netpad users add user@example.com -o org_xxx --role member

# Change role
netpad users update user@example.com -o org_xxx --role admin

# Remove user
netpad users remove user@example.com -o org_xxx

# List groups
netpad groups list -o org_xxx

# Create group
netpad groups create "Engineering" -o org_xxx

# Add user to group
netpad groups add-member grp_xxx user@example.com -o org_xxx

# Delete group
netpad groups delete grp_xxx -o org_xxx

# List roles (builtin + custom)
netpad roles list -o org_xxx

# Create custom role
netpad roles create "Reviewer" -o org_xxx --base viewer --description "Can review submissions"

# View role details
netpad roles get role_xxx -o org_xxx

# Delete custom role
netpad roles delete role_xxx -o org_xxx

# Assign role to user
netpad assign user user@example.com role_xxx -o org_xxx

# Assign role to group
netpad assign group grp_xxx role_xxx -o org_xxx

# Remove assignment
netpad unassign user user@example.com role_xxx -o org_xxx

# List all permissions
netpad permissions list -o org_xxx

# Check user's effective permissions
netpad permissions check user@example.com -o org_xxx

## References
- `references/api-endpoints.md` — Complete REST API endpoint docs
- `references/cli-commands.md` — Full CLI command reference

## Author
**Michael Lynn** — Principal Staff Developer Advocate at MongoDB

- Website: [mlynn.org](https://mlynn.org), GitHub: [@mrlynn](https://github.com/mrlynn), LinkedIn: [linkedin.com/in/mlynn](https://linkedin.com/in/mlynn)