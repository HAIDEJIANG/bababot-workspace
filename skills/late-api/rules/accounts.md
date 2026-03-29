# Accounts API

## Endpoints
`GET`, Endpoint=`/v1/accounts`, Description=List accounts
`PUT`, Endpoint=`/v1/accounts/{accountId}`, Description=Update account
`DELETE`, Endpoint=`/v1/accounts/{accountId}`, Description=Disconnect account
`GET`, Endpoint=`/v1/accounts/health`, Description=Check all accounts health
`GET`, Endpoint=`/v1/accounts/{accountId}/health`, Description=Check specific account health
`GET`, Endpoint=`/v1/accounts/follower-stats`, Description=Get follower statistics

## Platform-Specific Account Endpoints
| `PUT` | `/v1/accounts/{accountId}/facebook-page` | Update selected Facebook page |
| `GET` | `/v1/accounts/{accountId}/gmb-reviews` | Get Google Business reviews |
| `GET` | `/v1/accounts/{accountId}/linkedin-organizations` | List LinkedIn organizations |
| `PUT` | `/v1/accounts/{accountId}/linkedin-organization` | Switch personal/organization mode |
| `GET` | `/v1/accounts/{accountId}/linkedin-mentions` | Get LinkedIn mentions |
| `GET` | `/v1/accounts/{accountId}/linkedin-aggregate-analytics` | Get LinkedIn analytics |
| `GET` | `/v1/accounts/{accountId}/linkedin-post-analytics` | Get LinkedIn post analytics |
| `GET` | `/v1/accounts/{accountId}/pinterest-boards` | List Pinterest boards |
| `PUT` | `/v1/accounts/{accountId}/pinterest-boards` | Set default Pinterest board |
| `GET` | `/v1/accounts/{accountId}/reddit-subreddits` | List user's subreddits |
| `PUT` | `/v1/accounts/{accountId}/reddit-subreddits` | Set default subreddit |

## List Accounts
```bash
curl "https://getlate.dev/api/v1/accounts?profileId=PROFILE_ID" \
 -H "Authorization: Bearer YOUR_API_KEY"
```

## Account Health Check
curl "https://getlate.dev/api/v1/accounts/health" \

Response indicates if tokens are valid or need reconnection.

## Account Groups
| `GET` | `/v1/account-groups` | List account groups |
| `POST` | `/v1/account-groups` | Create account group |
| `PUT` | `/v1/account-groups/{groupId}` | Update account group |
| `DELETE` | `/v1/account-groups/{groupId}` | Delete account group |

Account groups let you organize accounts for bulk posting operations.