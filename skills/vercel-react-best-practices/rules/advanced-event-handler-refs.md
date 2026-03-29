---
title: Store Event Handlers in Refs
impact: LOW
impactDescription: stable subscriptions
tags: advanced, hooks, refs, event-handlers, optimization

## Store Event Handlers in Refs
Store callbacks in refs when used in effects that shouldn't re-subscribe on callback changes.

**Incorrect (re-subscribes on every render):**

```tsx
function useWindowEvent(event: string, handler: () => void) {
 useEffect(() => {
 window.addEventListener(event, handler)
 return () => window.removeEventListener(event, handler)
 }, [event, handler])
}
```

**Correct (stable subscription):**

 const handlerRef = useRef(handler)
 handlerRef.current = handler
 }, [handler])

 const listener = () => handlerRef.current()
 window.addEventListener(event, listener)
 return () => window.removeEventListener(event, listener)
 }, [event])

**Alternative: use `useEffectEvent` if you're on latest React:**

import { useEffectEvent } from 'react'

 const onEvent = useEffectEvent(handler)

 window.addEventListener(event, onEvent)
 return () => window.removeEventListener(event, onEvent)

`useEffectEvent` provides a cleaner API for the same pattern: it creates a stable function reference that always calls the latest version of the handler.