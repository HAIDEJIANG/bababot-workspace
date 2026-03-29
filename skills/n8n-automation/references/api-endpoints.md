# n8n REST API — Endpoint Reference
Base URL: `{instance}/api/v1`
Auth: Header `X-N8N-API-KEY: {key}`

## Workflows
GET, Endpoint=`/workflows`, Description=List all workflows. Filter: `?active=true\, false`, `?tags=tag1,tag2`
GET, Endpoint=`/workflows/{id}`, Description=Get workflow by ID (includes nodes, connections)
POST, Endpoint=`/workflows`, Description=Create workflow from JSON body
PATCH, Endpoint=`/workflows/{id}`, Description=Update workflow (name, nodes, active status)
DELETE, Endpoint=`/workflows/{id}`, Description=Delete workflow
POST, Endpoint=`/workflows/{id}/activate`, Description=Activate workflow
POST, Endpoint=`/workflows/{id}/deactivate`, Description=Deactivate workflow
POST, Endpoint=`/workflows/{id}/transfer`, Description=Transfer workflow ownership (enterprise)

## Executions
| GET | `/executions` | List executions. Filter: `?status=error\|success\|waiting`, `?workflowId={id}`, `?limit=N` |
| GET | `/executions/{id}` | Get execution details (node data, errors, timing) |
| DELETE | `/executions/{id}` | Delete execution record |

## Credentials
| GET | `/credentials` | List all credentials (names/types only, no secrets) |
| POST | `/credentials` | Create credential |
| DELETE | `/credentials/{id}` | Delete credential |

## Tags
| GET | `/tags` | List all tags |
| POST | `/tags` | Create tag |
| PATCH | `/tags/{id}` | Update tag |
| DELETE | `/tags/{id}` | Delete tag |

## Users (admin)
| GET | `/users` | List users |
| GET | `/users/{id}` | Get user details |

## Webhooks (no auth needed)
- Production: `{instance}/webhook/{path}`
- Test: `{instance}/webhook-test/{path}`

## Pagination
All list endpoints support:
- `?limit=N` — Results per page (default 10, max 250)
- `?cursor=xxx` — Cursor for next page (returned in response)

## Response Format
```json
{
 "data": [...],
 "nextCursor": "string | null"
}
```

## Error Codes
- 401: Invalid or missing API key
- 404: Resource not found
- 429: Rate limit exceeded
- 500: Internal server error