---
title: Early Return from Functions
impact: LOW-MEDIUM
impactDescription: avoids unnecessary computation
tags: javascript, functions, optimization, early-return

## Early Return from Functions
Return early when result is determined to skip unnecessary processing.

**Incorrect (processes all items even after finding answer):**

```typescript
function validateUsers(users: User[]) {
 let hasError = false
 let errorMessage = ''

 for (const user of users) {
 if (!user.email) {
 hasError = true
 errorMessage = 'Email required'
 }
 if (!user.name) {
 errorMessage = 'Name required'
 // Continues checking all users even after error found

 return hasError ? { valid: false, error: errorMessage } : { valid: true }
```

**Correct (returns immediately on first error):**

 return { valid: false, error: 'Email required' }
 return { valid: false, error: 'Name required' }

 return { valid: true }