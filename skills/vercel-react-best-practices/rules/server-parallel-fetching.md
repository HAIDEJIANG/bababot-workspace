---
title: Parallel Data Fetching with Component Composition
impact: CRITICAL
impactDescription: eliminates server-side waterfalls
tags: server, rsc, parallel-fetching, composition

## Parallel Data Fetching with Component Composition
React Server Components execute sequentially within a tree. Restructure with composition to parallelize data fetching.

**Incorrect (Sidebar waits for Page's fetch to complete):**

```tsx
export default async function Page() {
 const header = await fetchHeader()
 return (
 <div>
 <div>{header}</div>
 <Sidebar />
 </div>
 )
}

async function Sidebar() {
 const items = await fetchSidebarItems()
 return <nav>{items.map(renderItem)}</nav>
```

**Correct (both fetch simultaneously):**

async function Header() {
 const data = await fetchHeader()
 return <div>{data}</div>

export default function Page() {
 <Header />

**Alternative with children prop:**

function Layout({ children }: { children: ReactNode }) {
 {children}

 <Layout>
 </Layout>