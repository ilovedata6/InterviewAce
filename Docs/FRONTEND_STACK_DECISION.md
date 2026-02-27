# Frontend Stack Decision — InterviewAce

> **Date:** 2025-02-27  
> **Decision:** Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui  
> **Status:** Accepted

---

## 1. Candidates Evaluated

| Criteria | Vue.js 3 (Nuxt) | React (Vite SPA) | Next.js 14 (App Router) |
|----------|-----------------|-------------------|------------------------|
| **Learning Curve** | Low-Medium | Medium | Medium (but most structured) |
| **Ecosystem Size** | Good | Largest | Largest (React superset) |
| **Community / AI Help** | Good | Best | Best |
| **SSR / SEO** | Nuxt 3 — yes | Manual (no built-in) | Built-in, zero config |
| **File-based Routing** | Nuxt 3 — yes | No (manual react-router) | Yes, built-in |
| **Auth Middleware** | Nuxt middleware | Manual guards | Built-in middleware.ts |
| **API Proxy (BFF)** | Nuxt server routes | No built-in | API Routes / Server Actions |
| **UI Component Library** | PrimeVue, Vuetify | shadcn/ui, MUI, Ant | shadcn/ui, MUI, Ant |
| **Deployment** | Vercel / Netlify | Any static host | Vercel (best-in-class) |
| **Job Market** | Smaller | Largest | Part of React — largest |
| **TypeScript Support** | Excellent | Excellent | Excellent |

---

## 2. Why Next.js Wins for InterviewAce

### 2.1 Developer Experience for a Backend Engineer

You have zero frontend experience. Next.js offers the **most guardrails**:

- **File-based routing**: Create `app/dashboard/page.tsx` → you have the `/dashboard` route. No router configuration needed.
- **Layouts**: Shared UI (navbar, sidebar) is defined once in `layout.tsx` files. Nested layouts compose automatically.
- **Server Components** (default): Write React components that render on the server — no `useEffect`/`useState` needed for data fetching. Just `async function` + `fetch()`.
- **TypeScript first**: Full type safety from API responses to UI components. Catches bugs at compile time, not at runtime.

### 2.2 Architecture Fit

InterviewAce has **two distinct UX patterns** that Next.js handles perfectly:

| Page Type | Rendering Strategy | Why |
|-----------|-------------------|-----|
| Landing, Login, Register | **SSR** (Server-Side Rendered) | SEO, fast first paint, no auth needed |
| Dashboard, Resume List | **SSR + Client hydration** | Needs auth, but initial content can be server-rendered |
| Interview Session (live Q&A) | **CSR** (Client-Side Rendered) | Real-time interaction, WebSocket-like polling, heavy state |
| Admin Panel | **CSR** | Protected, no SEO needed, dynamic tables |

Next.js App Router lets you mix these **per page** without any extra configuration.

### 2.3 Auth Integration with FastAPI

```
Browser → Next.js Middleware (checks JWT in cookie) → Allow/Redirect
Browser → Next.js API Route → Attach JWT → FastAPI Backend
```

- **middleware.ts**: Runs before every request. Checks auth cookie, redirects unauthenticated users.
- **API Routes (BFF)**: Frontend calls `/api/interview/start` on Next.js → Next.js server calls `http://fastapi:8000/api/v1/interview/start` with the JWT. This keeps the FastAPI URL and tokens off the client entirely.

### 2.4 UI Library: shadcn/ui

Instead of a heavy component library, **shadcn/ui** gives you:

- Copy-paste components (Button, Card, Dialog, Table, Form, etc.) into your project
- Built on **Radix UI** (accessible primitives) + **Tailwind CSS** (utility-first styling)
- Fully customizable — you own the code, no version lock-in
- Matches the clean, professional look needed for an interview prep tool
- Most popular React UI approach in 2024-2025

### 2.5 Ecosystem Advantages

| Need | Next.js/React Solution |
|------|----------------------|
| Forms + Validation | `react-hook-form` + `zod` (same validation lib can mirror your Pydantic schemas) |
| State Management | `zustand` (tiny, simple) or React Context (built-in) |
| Data Fetching/Caching | `@tanstack/react-query` (auto-retry, caching, optimistic updates) |
| Charts (Dashboard) | `recharts` or `nivo` |
| PDF Viewer (Resume) | `react-pdf` |
| Rich Text / Markdown | `react-markdown` |
| File Upload | `react-dropzone` |
| Toast Notifications | `sonner` (works great with shadcn/ui) |
| Icons | `lucide-react` (included with shadcn/ui) |

---

## 3. Why NOT Vue.js

Vue.js is excellent and arguably easier to learn in isolation. However:

1. **Smaller ecosystem** — Fewer component libraries, fewer tutorials, fewer StackOverflow answers
2. **Less AI assistance** — LLMs (ChatGPT, Copilot) have significantly more React/Next.js training data
3. **Nuxt 3 is powerful but newer** — Less battle-tested than Next.js 14 for production apps
4. **Job market** — If this project goes on your portfolio, React/Next.js skills are more marketable

## 4. Why NOT Plain React (Vite SPA)

1. **No routing built-in** — You'd need to install and configure `react-router-dom` manually
2. **No SSR** — Landing page won't be SEO-friendly without extra work
3. **No API proxy** — JWT tokens would need to be in `localStorage` (XSS vulnerability) or you'd need to build a separate BFF server
4. **No middleware** — Auth route protection requires manual React guards
5. **More decisions** — Every architectural choice is on you. Next.js makes sensible defaults.

---

## 5. Final Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Next.js 14 (App Router) | SSR + CSR hybrid, file routing, middleware, API routes |
| **Language** | TypeScript 5 | Type safety, IntelliSense, compile-time error catching |
| **Styling** | Tailwind CSS 3 | Utility-first CSS, no separate CSS files needed |
| **UI Components** | shadcn/ui | Pre-built accessible components (Button, Card, Table, Dialog, Form...) |
| **Forms** | react-hook-form + zod | Form state + schema validation (mirrors Pydantic) |
| **Data Fetching** | @tanstack/react-query | Caching, auto-refetch, loading/error states |
| **State Management** | zustand | Lightweight global state (auth, interview session) |
| **Charts** | recharts | Dashboard analytics visualization |
| **Icons** | lucide-react | Consistent icon set |
| **Notifications** | sonner | Toast notifications |
| **Auth Storage** | httpOnly cookies | Secure JWT storage (not localStorage) |
| **Linting** | ESLint + Prettier | Code consistency (auto-configured by Next.js) |
| **Testing** | Vitest + React Testing Library | Unit + component tests |
| **E2E Testing** | Playwright | End-to-end browser testing |
| **Package Manager** | pnpm | Fast, disk-efficient |
| **Deployment** | Vercel (free tier) or Docker | Zero-config deploy or self-host |

---

## 6. Expected Learning Path

As someone with zero frontend knowledge, here's the recommended learning order:

1. **TypeScript basics** (2-3 hours) — types, interfaces, generics
2. **React fundamentals** (4-6 hours) — components, props, state, hooks (`useState`, `useEffect`)
3. **Next.js App Router** (3-4 hours) — file routing, layouts, server vs client components
4. **Tailwind CSS** (1-2 hours) — utility classes, responsive design
5. **shadcn/ui** (1 hour) — installing and using components

**Total ramp-up: ~12-16 hours** before you can be productive.

> **Recommended resource:** The official Next.js tutorial at https://nextjs.org/learn (free, interactive, covers everything above)
