---
title: useLatest for Stable Callback Refs
impact: LOW
impactDescription: prevents effect re-runs
tags: advanced, hooks, useLatest, refs, optimization

## useLatest for Stable Callback Refs
Access latest values in callbacks without adding them to dependency arrays. Prevents effect re-runs while avoiding stale closures.

**Implementation:**

```typescript
function useLatest<T>(value: T) {
 const ref = useRef(value)
 useEffect(() => {
 ref.current = value
 }, [value])
 return ref
}
```

**Incorrect (effect re-runs on every callback change):**

```tsx
function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
 const [query, setQuery] = useState('')

 const timeout = setTimeout(() => onSearch(query), 300)
 return () => clearTimeout(timeout)
 }, [query, onSearch])

**Correct (stable effect, fresh callback):**

 const onSearchRef = useLatest(onSearch)

 const timeout = setTimeout(() => onSearchRef.current(query), 300)
 }, [query])