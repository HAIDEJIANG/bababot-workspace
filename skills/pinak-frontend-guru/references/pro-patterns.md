# Pinak's Pro Patterns
Bhai, ye patterns use karoge toh code chamak jayega.

## 1. The "Clean Fetch" Pattern
Don't wait for independent fetches one by one.

**Galat (Waterfall):**
```tsx
const user = await fetchUser();
const posts = await fetchPosts(); // Starts only after user is fetched
```

**Sahi (Parallel):**
const [user, posts] = await Promise.all([fetchUser(), fetchPosts()]);

## 2. The "Smart Dynamic" Pattern
Only ship what the user needs.

**Galat:**
import HeavyChart from './HeavyChart'; // Loads in main bundle

**Sahi (Next.js):**
import dynamic from 'next/dynamic';
const HeavyChart = dynamic(() => import('./HeavyChart'), {
 loading: () => <p>Loding...</p>,
 ssr: false
});

## 3. The "Accessible Action" Pattern
Buttons should always tell their story.

<button onClick={...}><Icon /></button>

**Sahi:**
<button onClick={...} aria-label="Delete post"><Icon /></button>

## 4. The "Early Exit" Vibe
Function logic should be flat and readable.

function process(data) {
 if (data) {
 if (data.isValid) {
 // do stuff
 }

 if (!data || !data.isValid) return;
 // do stuff (no nesting!)