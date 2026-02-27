# Frontend Architecture — InterviewAce

> **Framework:** Next.js 14 (App Router) + TypeScript  
> **Pattern:** Feature-based modular architecture with BFF (Backend-for-Frontend) proxy layer

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Next.js Client (React)               │  │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │  │
│  │  │  Pages   │  │Components│  │  State (zustand)│  │  │
│  │  │ (Routes) │  │ (UI Kit) │  │  + React Query │  │  │
│  │  └────┬─────┘  └──────────┘  └───────┬───────┘   │  │
│  │       │                              │            │  │
│  │       └──────────┬───────────────────┘            │  │
│  │                  │ fetch("/api/...")               │  │
│  └──────────────────┼────────────────────────────────┘  │
│                     │                                    │
├─────────────────────┼────────────────────────────────────┤
│          Next.js Server (Node.js)                        │
│  ┌──────────────────┼────────────────────────────────┐  │
│  │          API Routes (BFF Layer)                    │  │
│  │  ┌───────────────┼──────────────────────────┐     │  │
│  │  │  middleware.ts │ (Auth check on every req)│     │  │
│  │  ├───────────────┼──────────────────────────┤     │  │
│  │  │  /api/auth/*   → proxy → FastAPI /auth/* │     │  │
│  │  │  /api/resume/* → proxy → FastAPI /resume/*│    │  │
│  │  │  /api/interview/* → proxy → FastAPI /*   │     │  │
│  │  │  /api/admin/*  → proxy → FastAPI /admin/* │    │  │
│  │  └──────────────────────────────────────────┘     │  │
│  │  Attaches JWT from httpOnly cookie to each        │  │
│  │  upstream request. Client NEVER sees raw JWT.     │  │
│  └───────────────────────────────────────────────────┘  │
│                     │                                    │
├─────────────────────┼────────────────────────────────────┤
│                     ▼                                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │         FastAPI Backend (Python)                   │  │
│  │         http://localhost:8000/api/v1               │  │
│  │  ┌──────────┐  ┌──────┐  ┌───────┐  ┌─────────┐ │  │
│  │  │PostgreSQL│  │Redis │  │Celery │  │LLM APIs │ │  │
│  │  └──────────┘  └──────┘  └───────┘  └─────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure

```
frontend/
├── .env.local                    # NEXT_PUBLIC_* vars + BACKEND_URL (server-only)
├── .eslintrc.json
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── pnpm-lock.yaml
│
├── public/                       # Static assets (logo, favicon, OG images)
│   ├── logo.svg
│   ├── favicon.ico
│   └── og-image.png
│
├── src/
│   ├── app/                      # Next.js App Router (file-based routing)
│   │   ├── layout.tsx            # Root layout (html, body, global providers)
│   │   ├── page.tsx              # Landing page (/)
│   │   ├── loading.tsx           # Global loading skeleton
│   │   ├── error.tsx             # Global error boundary
│   │   ├── not-found.tsx         # 404 page
│   │   │
│   │   ├── (auth)/               # Route group: auth pages (no layout nesting)
│   │   │   ├── login/
│   │   │   │   └── page.tsx      # /login
│   │   │   ├── register/
│   │   │   │   └── page.tsx      # /register
│   │   │   ├── verify-email/
│   │   │   │   └── page.tsx      # /verify-email?token=...
│   │   │   ├── forgot-password/
│   │   │   │   └── page.tsx      # /forgot-password
│   │   │   └── reset-password/
│   │   │       └── page.tsx      # /reset-password?token=...
│   │   │
│   │   ├── (app)/                # Route group: authenticated app pages
│   │   │   ├── layout.tsx        # App shell (sidebar + navbar + auth guard)
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx      # /dashboard — overview, stats, quick actions
│   │   │   ├── resumes/
│   │   │   │   ├── page.tsx      # /resumes — list all resumes
│   │   │   │   ├── upload/
│   │   │   │   │   └── page.tsx  # /resumes/upload — upload new resume
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx  # /resumes/:id — resume detail + analysis
│   │   │   │       └── export/
│   │   │   │           └── page.tsx  # /resumes/:id/export
│   │   │   ├── interviews/
│   │   │   │   ├── page.tsx      # /interviews — interview history
│   │   │   │   ├── start/
│   │   │   │   │   └── page.tsx  # /interviews/start — configure + start
│   │   │   │   └── [sessionId]/
│   │   │   │       ├── page.tsx  # /interviews/:sessionId — live Q&A
│   │   │   │       └── summary/
│   │   │   │           └── page.tsx  # /interviews/:sessionId/summary
│   │   │   ├── profile/
│   │   │   │   └── page.tsx      # /profile — user settings, change password
│   │   │   └── admin/            # Admin-only section
│   │   │       ├── layout.tsx    # Admin guard (checks role)
│   │   │       ├── users/
│   │   │       │   └── page.tsx  # /admin/users — user management
│   │   │       └── stats/
│   │   │           └── page.tsx  # /admin/stats — system statistics
│   │   │
│   │   └── api/                  # Next.js API Routes (BFF proxy)
│   │       ├── auth/
│   │       │   ├── login/route.ts
│   │       │   ├── register/route.ts
│   │       │   ├── logout/route.ts
│   │       │   ├── refresh/route.ts
│   │       │   ├── me/route.ts
│   │       │   ├── verify-email/route.ts
│   │       │   ├── forgot-password/route.ts
│   │       │   ├── reset-password/route.ts
│   │       │   └── change-password/route.ts
│   │       ├── resumes/
│   │       │   ├── route.ts            # GET list, POST upload
│   │       │   └── [id]/
│   │       │       ├── route.ts        # GET detail, DELETE
│   │       │       ├── analysis/route.ts
│   │       │       ├── versions/route.ts
│   │       │       ├── share/route.ts
│   │       │       └── export/route.ts
│   │       ├── interviews/
│   │       │   ├── start/route.ts
│   │       │   ├── [sessionId]/
│   │       │   │   ├── route.ts        # GET session
│   │       │   │   ├── next-question/route.ts
│   │       │   │   ├── answer/route.ts
│   │       │   │   ├── complete/route.ts
│   │       │   │   └── summary/route.ts
│   │       │   └── history/route.ts
│   │       └── admin/
│   │           ├── users/route.ts
│   │           └── stats/route.ts
│   │
│   ├── components/               # Shared components
│   │   ├── ui/                   # shadcn/ui components (auto-generated)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── form.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── skeleton.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── progress.tsx
│   │   │   └── ... (added as needed)
│   │   ├── layout/
│   │   │   ├── app-sidebar.tsx   # Main sidebar navigation
│   │   │   ├── app-navbar.tsx    # Top navbar (user menu, notifications)
│   │   │   ├── footer.tsx        # Landing page footer
│   │   │   └── auth-layout.tsx   # Centered card layout for auth pages
│   │   ├── auth/
│   │   │   ├── login-form.tsx
│   │   │   ├── register-form.tsx
│   │   │   ├── forgot-password-form.tsx
│   │   │   └── reset-password-form.tsx
│   │   ├── dashboard/
│   │   │   ├── stats-cards.tsx         # Quick stat cards (total interviews, avg score)
│   │   │   ├── recent-activity.tsx     # Recent interviews/uploads
│   │   │   ├── score-trend-chart.tsx   # Line chart of interview scores over time
│   │   │   └── quick-actions.tsx       # Start interview, Upload resume buttons
│   │   ├── resume/
│   │   │   ├── resume-card.tsx         # Resume list item card
│   │   │   ├── resume-upload-zone.tsx  # Drag-and-drop upload area
│   │   │   ├── resume-analysis.tsx     # Parsed analysis display (skills, experience)
│   │   │   ├── resume-versions.tsx     # Version history timeline
│   │   │   └── resume-export-dialog.tsx
│   │   ├── interview/
│   │   │   ├── interview-config.tsx    # Pre-start configuration form
│   │   │   ├── question-display.tsx    # Current question card
│   │   │   ├── answer-input.tsx        # Text area with char count + timer
│   │   │   ├── progress-bar.tsx        # Questions answered: 3/10
│   │   │   ├── interview-summary.tsx   # Final results display
│   │   │   ├── score-breakdown.tsx     # Radar/bar chart of category scores
│   │   │   └── interview-history-table.tsx
│   │   └── admin/
│   │       ├── user-table.tsx
│   │       └── system-stats.tsx
│   │
│   ├── lib/                      # Shared utilities and configuration
│   │   ├── api-client.ts         # Typed fetch wrapper for BFF API routes
│   │   ├── auth.ts               # Auth helpers (getSession, isAuthenticated)
│   │   ├── utils.ts              # General utilities (cn(), formatDate, etc.)
│   │   ├── constants.ts          # App-wide constants (routes, config)
│   │   └── validations/          # Zod schemas (mirror Pydantic models)
│   │       ├── auth.ts           # LoginSchema, RegisterSchema, etc.
│   │       ├── resume.ts         # UploadSchema, ExportSchema, etc.
│   │       └── interview.ts      # InterviewConfigSchema, AnswerSchema, etc.
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── use-auth.ts           # Auth state hook (wraps zustand store)
│   │   ├── use-interview.ts      # Interview session hook (state machine)
│   │   ├── use-resumes.ts        # Resume CRUD hooks (wraps React Query)
│   │   └── use-media-query.ts    # Responsive breakpoint hook
│   │
│   ├── stores/                   # Zustand global state stores
│   │   ├── auth-store.ts         # User session, tokens, login/logout actions
│   │   └── interview-store.ts    # Active interview session state
│   │
│   ├── types/                    # TypeScript type definitions
│   │   ├── api.ts                # API response types (matches FastAPI schemas)
│   │   ├── auth.ts               # User, Token, Session types
│   │   ├── resume.ts             # Resume, Analysis, Version types
│   │   ├── interview.ts          # InterviewSession, Question, Answer types
│   │   └── common.ts             # Pagination, Error, ApiResponse generics
│   │
│   ├── styles/
│   │   └── globals.css           # Tailwind directives + custom CSS variables
│   │
│   └── middleware.ts             # Next.js middleware (auth redirect logic)
│
└── tests/
    ├── unit/                     # Vitest unit tests
    │   ├── components/
    │   └── hooks/
    ├── integration/              # Component integration tests
    └── e2e/                      # Playwright E2E tests
        ├── auth.spec.ts
        ├── resume.spec.ts
        └── interview.spec.ts
```

---

## 3. Authentication Flow

### 3.1 Login Flow

```
1. User submits email + password on /login page
2. Client calls POST /api/auth/login (Next.js API route)
3. Next.js API route:
   a. Forwards credentials to FastAPI POST /api/v1/auth/login
   b. Receives { access_token, refresh_token }
   c. Sets TWO httpOnly cookies:
      - "access_token" (httpOnly, secure, sameSite=strict, path=/, maxAge=30min)
      - "refresh_token" (httpOnly, secure, sameSite=strict, path=/api/auth/refresh, maxAge=7d)
   d. Returns { user } to client (NO tokens exposed)
4. Client stores user info in zustand auth-store
5. middleware.ts allows access to (app)/* routes
```

### 3.2 Request Flow (Authenticated)

```
1. Client calls GET /api/resumes (Next.js API route)
2. Next.js API route:
   a. Reads access_token from httpOnly cookie
   b. Forwards request to FastAPI with Authorization: Bearer <token>
   c. If 401 → tries refresh flow → retries original request
   d. If refresh fails → clears cookies → returns 401
3. Client receives data or 401 (triggers logout + redirect)
```

### 3.3 middleware.ts Logic

```typescript
// Simplified middleware logic
const publicPaths = ["/", "/login", "/register", "/verify-email", 
                     "/forgot-password", "/reset-password"];

export function middleware(request: NextRequest) {
  const token = request.cookies.get("access_token");
  const { pathname } = request.nextUrl;

  // Public pages → allow
  if (publicPaths.some(p => pathname.startsWith(p))) return NextResponse.next();

  // No token → redirect to login
  if (!token) return NextResponse.redirect(new URL("/login", request.url));

  // Admin routes → check role claim in JWT
  if (pathname.startsWith("/admin")) {
    const payload = decodeJWT(token.value); // decode only, verification happens server-side
    if (payload.role !== "admin") return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}
```

---

## 4. Data Fetching Strategy

### 4.1 React Query for Client-Side Data

```typescript
// Example: hooks/use-resumes.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export function useResumes() {
  return useQuery({
    queryKey: ["resumes"],
    queryFn: () => apiClient.get("/api/resumes"),
    staleTime: 5 * 60 * 1000,  // Cache for 5 minutes
  });
}

export function useDeleteResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/resumes/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["resumes"] }),
  });
}
```

### 4.2 Server Components for Initial Data

```typescript
// Example: app/(app)/dashboard/page.tsx (Server Component)
import { cookies } from "next/headers";

async function getDashboardStats() {
  const token = cookies().get("access_token")?.value;
  const res = await fetch(`${process.env.BACKEND_URL}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    next: { revalidate: 60 },  // Cache for 60 seconds
  });
  return res.json();
}

export default async function DashboardPage() {
  const stats = await getDashboardStats();
  return <DashboardClient initialData={stats} />;
}
```

---

## 5. State Management Architecture

```
┌─────────────────────────────────────────────┐
│                  State Layers                │
├─────────────────────────────────────────────┤
│                                             │
│  1. SERVER STATE (React Query)              │
│     - Resumes list, detail, analysis        │
│     - Interview history, summary            │
│     - User profile data                     │
│     - Admin user list                       │
│     → Auto-cached, auto-refetched           │
│                                             │
│  2. GLOBAL CLIENT STATE (Zustand)           │
│     - Auth state (user, isAuthenticated)    │
│     - Active interview session              │
│     - UI preferences (sidebar open/closed)  │
│     → Persistent across page navigations    │
│                                             │
│  3. LOCAL COMPONENT STATE (useState)        │
│     - Form inputs                           │
│     - Modal open/closed                     │
│     - Dropdown selections                   │
│     - Animation states                      │
│     → Ephemeral, component-scoped           │
│                                             │
│  4. URL STATE (Next.js searchParams)        │
│     - Pagination (?page=2)                  │
│     - Filters (?status=analyzed)            │
│     - Sort order (?sort=date)               │
│     → Shareable, bookmarkable               │
│                                             │
└─────────────────────────────────────────────┘
```

**Rule of thumb:** If data comes from the API → React Query. If it's app-wide UI state → Zustand. If it's local to one component → `useState`. If it should survive a page reload → URL params.

---

## 6. Interview Session — State Machine

The live interview is the most complex UI. It follows a finite state machine:

```
    ┌──────────┐
    │CONFIGURING│  User sets: resume, question count, difficulty
    └─────┬────┘
          │ "Start Interview"
          ▼
    ┌──────────┐
    │ LOADING  │  POST /api/interviews/start
    └─────┬────┘
          │ session created
          ▼
    ┌──────────┐
    │ANSWERING │◄────────────────────┐
    │          │  Show question       │
    │          │  User types answer   │
    │          │  Timer counting      │
    └─────┬────┘                     │
          │ "Submit Answer"          │
          ▼                          │
    ┌──────────┐                     │
    │SUBMITTING│  POST /answer       │
    └─────┬────┘                     │
          │ saved                    │
          ▼                          │
    ┌──────────┐    more questions   │
    │ FEEDBACK │─────────────────────┘
    │(optional)│  Show per-Q feedback
    └─────┬────┘
          │ last question
          ▼
    ┌──────────┐
    │COMPLETING│  POST /complete
    └─────┬────┘
          │
          ▼
    ┌──────────┐
    │ SUMMARY  │  GET /summary → display results
    └──────────┘
```

This state machine is managed in `stores/interview-store.ts` using Zustand.

---

## 7. API Client Design

```typescript
// lib/api-client.ts — Typed fetch wrapper

type ApiResponse<T> = {
  data: T;
  status: number;
};

type ApiError = {
  detail: string;
  status: number;
};

class ApiClient {
  private baseUrl = "";  // Calls Next.js API routes (same origin)

  async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(path, window.location.origin);
    if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    
    const res = await fetch(url.toString());
    if (!res.ok) throw await this.handleError(res);
    return res.json();
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw await this.handleError(res);
    return res.json();
  }

  async upload<T>(path: string, formData: FormData): Promise<T> {
    const res = await fetch(path, { method: "POST", body: formData });
    if (!res.ok) throw await this.handleError(res);
    return res.json();
  }

  // ... delete, patch, etc.

  private async handleError(res: Response): Promise<ApiError> {
    const body = await res.json().catch(() => ({ detail: "Unknown error" }));
    return { detail: body.detail || "Something went wrong", status: res.status };
  }
}

export const apiClient = new ApiClient();
```

---

## 8. Error Handling Strategy

```
┌─────────────────────────────────────────┐
│         Error Handling Layers           │
├─────────────────────────────────────────┤
│                                         │
│  1. FORM VALIDATION (Zod)              │
│     → Inline field errors               │
│     → Prevents bad requests             │
│                                         │
│  2. API ERROR (React Query onError)    │
│     → Toast notification                │
│     → 401 → auto-logout + redirect     │
│     → 403 → "Forbidden" message        │
│     → 422 → map to form errors         │
│     → 429 → "Rate limited, wait X sec" │
│     → 500 → "Something went wrong"     │
│                                         │
│  3. PAGE ERROR (error.tsx)             │
│     → Full-page error boundary          │
│     → "Retry" button                   │
│     → Log to console (later: Sentry)   │
│                                         │
│  4. NOT FOUND (not-found.tsx)          │
│     → Friendly 404 page                │
│     → "Go to Dashboard" link           │
│                                         │
└─────────────────────────────────────────┘
```

---

## 9. Responsive Design Approach

| Breakpoint | Target | Layout |
|-----------|--------|--------|
| < 640px (sm) | Mobile | Single column, bottom nav, collapsible sidebar |
| 640-1024px (md) | Tablet | Two columns, collapsible sidebar |
| > 1024px (lg) | Desktop | Full sidebar + content area |

Tailwind makes this trivial:
```html
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

**Mobile-first:** All styles are mobile by default. `md:` and `lg:` prefixes add desktop enhancements.

---

## 10. Performance Considerations

| Technique | Where | Why |
|-----------|-------|-----|
| **Server Components** | Dashboard, Resume list, History | Less JavaScript shipped to client |
| **React Query caching** | All API data | Avoid redundant network requests |
| **Image optimization** | `next/image` for any images | Lazy loading, WebP conversion |
| **Code splitting** | Automatic per-route | Only load JS for current page |
| **Skeleton loading** | `loading.tsx` per route | Instant perceived performance |
| **Debounced search** | Admin user search, resume filter | Reduce API calls while typing |
| **Virtualized lists** | Long interview history | Only render visible rows |
