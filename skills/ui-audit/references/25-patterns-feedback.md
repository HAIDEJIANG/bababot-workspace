# Patterns: System Feedback
Patterns for communicating system status and action outcomes to users.

---

## What is System Feedback?
Communication from the system that keeps users informed about what's happening. Based on Nielsen's first heuristic: "Visibility of system status."

**Core principle:** Users should never wonder what's happening. The system should always speak.

## Progress Indicators
**What:** Visual communication of ongoing processes.

### Types
- **Determinate**: Duration known (upload 45%, step 2/4)
- **Indeterminate**: Duration unknown (spinner, loading bar)
- **Skeleton screens**: Loading structured content
- **Background indicator**: Process running but not blocking

### Timing Guidelines
- < 100ms: None needed
- 100ms - 1s: Simple spinner
- 1s - 10s: Progress indicator with context
- 10s+: Background process with notification

### Implementation Guidelines
**DO:**
- Show progress immediately on action
- Use determinate when possible (more reassuring)
- Include text explaining what's happening
- Allow cancellation for long processes
- Celebrate completion (subtle success state)

**DON'T:**
- Leave users staring at nothing
- Use spinners for > 10 seconds
- Show fake progress
- Block unnecessarily (show skeleton, load in background)
- Forget edge cases (slow connections, failures)

### Skeleton Screens
Best practices:
- Match layout of loading content
- Animate subtly (pulse or shimmer)
- Show as soon as structure is known
- Replace with content progressively
- Don't make more complex than the content

## Notifications & Alerts
**What:** System messages about events, status changes, or required attention.

### Types by Urgency
**Toast**, Persistence=Auto-dismiss (3-5s), Attention Level=Low, informational
**Banner**, Persistence=Persistent until dismissed, Attention Level=Medium, action needed
**Alert/Modal**, Persistence=Blocks interaction, Attention Level=High, immediate action
**Inline**, Persistence=Contextual, persistent, Attention Level=Medium, related to specific element

### Notification Anatomy
```
[Icon] [Title] (optional)
[Message explaining what happened]
[Action button] [Dismiss]

### Implementation Guidelines (Toasts)
- Brief, clear message
- Auto-dismiss (3-5 seconds typical)
- Allow manual dismiss
- Stack if multiple
- Position consistently (top-right or bottom-right common)

- Use for errors requiring action
- Auto-dismiss critical information
- Cover important content
- Show too many simultaneously
- Require immediate reading

### Implementation Guidelines (Banners)
- Span full width (usually top of page)
- Clear close/dismiss button
- Explain what and why
- Include action if applicable
- Use semantic colors (red=error, yellow=warning, blue=info)

- Stack multiple banners
- Use for non-critical info
- Make hard to dismiss
- Show vague messages

## Validation Feedback
**What:** Communicating input validity to users.

### Validation Timing
- **Real-time**: Format validation (email, phone)
- **On blur**: Field completion check
- **On submit**: Final validation
- **Debounced**: Async validation (username availability)

### Validation States
Empty → Neutral (no validation shown)
Typing → Neutral or real-time hints
Valid → Success indicator (green check)
Invalid → Error state (red, message)

### Error Message Guidelines
- Explain what's wrong specifically
- Explain how to fix it
- Place near the field
- Use plain language
- Persist until fixed

- Use generic messages ("Invalid input")
- Blame the user ("You entered wrong value")
- Use technical jargon
- Place far from the field
- Show all errors at once without field highlighting

### Examples
- "Invalid email": "Enter a valid email address (e.g., name@example.com)"
- "Required field": "Email is required"
- "Password error": "Password must be at least 8 characters"
- "Error": "This username is already taken. Try another."

## Success Feedback
**What:** Confirming successful completion of actions.

| Type | Use Case |
| **Inline** | Form field valid, item added |
| **Toast** | Action completed successfully |
| **Success page** | Major workflow complete |
| **Animation** | Delightful confirmation |

### Success Message Guidelines
- Confirm what was accomplished
- Indicate next steps if applicable
- Be brief but clear
- Match tone to significance
- Celebrate appropriately

- Over-celebrate minor actions
- Be vague about what succeeded
- Require action to dismiss (usually)
- Miss the success feedback entirely

Minor: (checkmark appears)
Standard: "Changes saved"
Significant: "Your order is confirmed! Check your email for details."
Major: [Success page with next steps]

## Contextual Help
**What:** In-context guidance and explanation.

| **Tooltips** | Icon/term explanations |
| **Inline hints** | Form field guidance |
| **Helper text** | Persistent guidance below inputs |
| **Info icons** | "What's this?" explanations |
| **Empty states** | Guidance when no content |

- Explain *why*, not just *what*
- Keep contextual (near related element)
- Make optional (not blocking)
- Provide examples when helpful

- Over-explain obvious things
- Use tooltips for critical info
- Write novels in helper text
- Hide essential instructions
- Require reading help to complete task

### Help Text Examples
**Form fields:**
Label: Password
Input: ********
Helper: At least 8 characters with one number and symbol.

**Feature explanation:**
[i] What are workspaces?
→ Workspaces let you organize projects into separate
 areas. Each workspace has its own members and settings.

## Empty States
**What:** Feedback when there's no content to display.

### Empty State Anatomy
[Illustration/Icon] (optional)
[Title explaining the state]
[Description of what goes here and why it's empty]
[CTA to add content or take action]

**First use**, Cause=New user, no data, Response=Guide to create first item
**No results**, Cause=Search/filter with no matches, Response=Suggest adjustments
**Cleared**, Cause=User deleted content, Response=Confirm empty, offer restore
**Error**, Cause=Failed to load, Response=Explain and offer retry

- Explain why it's empty
- Provide clear action to fix
- Match tone to context
- Design for the state (don't ignore it)
- Use as opportunity to educate

- Leave completely blank
- Just say "No results"
- Make user feel they did something wrong
- Offer irrelevant actions
- Use generic illustration for every state

## Feedback Timing Matrix
Button click, Immediate=Visual state change, Short Delay=-, Background=-
Form submit, Immediate=Disable + spinner, Short Delay=Success/error toast, Background=-
Save, Immediate=Inline "saving...", Short Delay="Saved" confirmation, Background=-
Upload, Immediate=Progress bar, Short Delay=Completion toast, Background=Status in UI
Long process, Immediate=Initiated message, Short Delay=-, Background=Notification when done

## Feedback Audit
- Loading states defined:, Success feedback clear:, Error states helpful:, Validation timing appropriate:, Empty states designed:
- Help available in context:
- Progress visible for long actions: