# Frontend Implementation Planner — InterviewAce

> **Purpose:** One feature per phase. Each phase = one or more atomic commits. Complete one phase fully before starting the next.  
> **Status Legend:** ⬜ Not Started · 🟡 In Progress · ✅ Done  
> **Estimated Total:** ~15 phases across 6-8 weeks (part-time)

---

## Phase F0 — Project Scaffold & Tooling
> *Goal: Bootable Next.js app with Tailwind, shadcn/ui, ESLint, and basic folder structure.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F0.1 | Run `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir` | `feat(fe): scaffold next.js app` | ✅ |
| F0.2 | Install pnpm, remove npm lockfile, configure `.npmrc` | `chore(fe): switch to pnpm` | ✅ |
| F0.3 | Initialize shadcn/ui: `npx shadcn-ui@latest init` (New York theme, zinc palette) | `feat(fe): initialize shadcn/ui` | ✅ |
| F0.4 | Install core dependencies: `zustand`, `@tanstack/react-query`, `react-hook-form`, `zod`, `sonner`, `lucide-react` | `chore(fe): install core dependencies` | ✅ |
| F0.5 | Create folder structure: `components/`, `lib/`, `hooks/`, `stores/`, `types/` | `chore(fe): create directory scaffold` | ✅ |
| F0.6 | Create `.env.local` with `BACKEND_URL=http://localhost:8000/api/v1` and `NEXT_PUBLIC_APP_NAME=InterviewAce` | `chore(fe): add environment variables` | ✅ |
| F0.7 | Configure `next.config.ts` — enable `output: "standalone"` for Docker | `chore(fe): configure next.config.ts` | ✅ |
| F0.8 | Add ESLint + Prettier config (extends `next/core-web-vitals`, `next/typescript`) | `chore(fe): configure eslint + prettier` | ✅ |

**Checkpoint:** `pnpm dev` boots to a "Hello InterviewAce" page. No errors.

---

## Phase F1 — Design System & Shared Components
> *Goal: Install all needed shadcn/ui components and create the app shell layout.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F1.1 | Install shadcn/ui components: `button`, `card`, `input`, `form`, `label`, `table`, `dialog`, `dropdown-menu`, `badge`, `skeleton`, `tabs`, `progress`, `separator`, `avatar`, `sheet` | `feat(fe): add shadcn/ui components` | ✅ |
| F1.2 | Install `sonner` toast component via shadcn/ui | `feat(fe): add toast notifications` | ✅ |
| F1.3 | Create `lib/utils.ts` — `cn()` helper (merge Tailwind classes) | `feat(fe): add utility helpers` | ✅ |
| F1.4 | Create `components/layout/app-sidebar.tsx` — sidebar nav with links: Dashboard, Resumes, Interviews, Profile | `feat(fe): create app sidebar` | ✅ |
| F1.5 | Create `components/layout/app-navbar.tsx` — top bar with user avatar dropdown (Profile, Logout) | `feat(fe): create app navbar` | ✅ |
| F1.6 | Create `app/(app)/layout.tsx` — authenticated app shell (sidebar + navbar + children) | `feat(fe): create authenticated layout` | ✅ |
| F1.7 | Create `components/layout/auth-layout.tsx` — centered card layout for login/register pages | `feat(fe): create auth layout` | ✅ |
| F1.8 | Create global `loading.tsx` and `error.tsx` | `feat(fe): add loading skeleton and error boundary` | ✅ |
| F1.9 | Define color scheme / CSS variables in `globals.css` (professional dark/light theme) | `style(fe): define color scheme` | ✅ |

**Checkpoint:** App shell renders with sidebar, navbar. Links don't go anywhere yet. Responsive on mobile.

---

## Phase F2 — TypeScript Types & API Client
> *Goal: Create typed API layer that mirrors FastAPI schemas. All frontend data contracts defined here.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F2.1 | Create `types/auth.ts` — `User`, `LoginRequest`, `RegisterRequest`, `TokenResponse`, `PasswordResetRequest`, `PasswordChangeRequest` | `feat(fe): define auth types` | ✅ |
| F2.2 | Create `types/resume.ts` — `Resume`, `ResumeAnalysis`, `ResumeVersion`, `ResumeUploadResponse`, `ExportFormat` | `feat(fe): define resume types` | ✅ |
| F2.3 | Create `types/interview.ts` — `InterviewSession`, `Question`, `Answer`, `InterviewSummary`, `InterviewConfig` | `feat(fe): define interview types` | ✅ |
| F2.4 | Create `types/common.ts` — `PaginatedResponse<T>`, `ApiError`, `ApiResponse<T>` | `feat(fe): define common types` | ✅ |
| F2.5 | Create `lib/api-client.ts` — typed fetch wrapper (`get`, `post`, `put`, `delete`, `upload`) with error handling | `feat(fe): create api client` | ✅ |
| F2.6 | Create `lib/validations/auth.ts` — Zod schemas: `loginSchema`, `registerSchema`, `forgotPasswordSchema`, `resetPasswordSchema`, `changePasswordSchema` | `feat(fe): add auth validation schemas` | ✅ |
| F2.7 | Create `lib/validations/resume.ts` — Zod schemas: `uploadSchema`, `exportSchema` | `feat(fe): add resume validation schemas` | ✅ |
| F2.8 | Create `lib/validations/interview.ts` — Zod schemas: `interviewConfigSchema`, `answerSchema` | `feat(fe): add interview validation schemas` | ✅ |

**Checkpoint:** All types compile. Zod schemas match FastAPI Pydantic models. apiClient is tested manually.

---

## Phase F3 — BFF Proxy Layer (Next.js API Routes)
> *Goal: All FastAPI endpoints accessible via same-origin Next.js API routes. JWT handled in cookies.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F3.1 | Create BFF helper: `lib/bff.ts` — utility to read cookie, call FastAPI, handle token refresh | `feat(fe): create bff proxy utility` | ✅ |
| F3.2 | Create `app/api/auth/login/route.ts` — login, set httpOnly cookies, return user | `feat(fe): BFF login route` | ✅ |
| F3.3 | Create `app/api/auth/register/route.ts` — register, return user | `feat(fe): BFF register route` | ✅ |
| F3.4 | Create `app/api/auth/logout/route.ts` — call FastAPI logout, clear cookies | `feat(fe): BFF logout route` | ✅ |
| F3.5 | Create `app/api/auth/refresh/route.ts` — refresh token, update cookies | `feat(fe): BFF token refresh route` | ✅ |
| F3.6 | Create `app/api/auth/me/route.ts` — proxy GET /auth/me | `feat(fe): BFF me route` | ✅ |
| F3.7 | Create remaining auth routes: verify-email, forgot-password, reset-password, change-password | `feat(fe): BFF remaining auth routes` | ✅ |
| F3.8 | Create `app/api/resumes/route.ts` — GET list + POST upload (multipart) | `feat(fe): BFF resume list/upload routes` | ✅ |
| F3.9 | Create `app/api/resumes/[id]/route.ts` — GET detail, DELETE | `feat(fe): BFF resume detail routes` | ✅ |
| F3.10 | Create resume sub-routes: analysis, versions, share, export | `feat(fe): BFF resume sub-routes` | ✅ |
| F3.11 | Create `app/api/interviews/start/route.ts` — POST start | `feat(fe): BFF interview start route` | ✅ |
| F3.12 | Create interview session routes: GET session, next-question, answer, complete, summary | `feat(fe): BFF interview session routes` | ✅ |
| F3.13 | Create `app/api/interviews/history/route.ts` — GET history | `feat(fe): BFF interview history route` | ✅ |
| F3.14 | Create admin routes: users, stats | `feat(fe): BFF admin routes` | ✅ |

**Checkpoint:** All FastAPI endpoints are reachable via `/api/*`. JWT is never exposed to the browser.

---

## Phase F4 — Authentication Middleware & Auth Store
> *Goal: Auth guard protecting all /app routes. Login state persisted across navigations.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F4.1 | Create `middleware.ts` — check `access_token` cookie, redirect unauthenticated users to /login, redirect authenticated users away from /login | `feat(fe): add auth middleware` | ✅ |
| F4.2 | Create `stores/auth-store.ts` — zustand store: user, isAuthenticated, login(), logout(), fetchUser() | `feat(fe): create auth store` | ✅ |
| F4.3 | Create `hooks/use-auth.ts` — wrapper hook exposing auth store + React Query for /me | `feat(fe): create auth hook` | ✅ |
| F4.4 | Create auth provider in root layout — fetch user on mount, populate store | `feat(fe): add auth provider to root layout` | ✅ |
| F4.5 | Create admin role guard — redirect non-admin from /admin/* routes | `feat(fe): add admin role guard` | ✅ |

**Checkpoint:** Unauthenticated → redirected to /login. Authenticated → allowed into /dashboard. Admin routes protected.

---

## Phase F5 — Landing Page
> *Goal: Public landing page at "/" with hero, features, CTA to register/login.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F5.1 | Create `app/page.tsx` — hero section: headline, subheadline, CTA buttons (Get Started, Login) | `feat(fe): create landing page hero` | ✅ |
| F5.2 | Add features section — 3 cards: AI Interviews, Resume Analysis, Progress Tracking | `feat(fe): landing page features section` | ✅ |
| F5.3 | Add footer with links | `feat(fe): landing page footer` | ✅ |
| F5.4 | Make fully responsive (mobile/tablet/desktop) | `style(fe): responsive landing page` | ✅ |

**Checkpoint:** Landing page renders at `/`. Looks professional. Links go to /login and /register.

---

## Phase F6 — Auth Pages (Login, Register, Password Reset)
> *Goal: Fully functional auth flow — register, verify email, login, forgot/reset password.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F6.1 | Create `components/auth/login-form.tsx` — email + password + "Forgot password?" link. Uses react-hook-form + zod | `feat(fe): create login form` | ✅ |
| F6.2 | Create `app/(auth)/login/page.tsx` — renders login form in auth layout + handles submit → BFF → redirect to /dashboard | `feat(fe): create login page` | ✅ |
| F6.3 | Create `components/auth/register-form.tsx` — name + email + password + confirm password | `feat(fe): create register form` | ✅ |
| F6.4 | Create `app/(auth)/register/page.tsx` — register + success message ("Check your email") | `feat(fe): create register page` | ✅ |
| F6.5 | Create `app/(auth)/verify-email/page.tsx` — reads token from URL, calls verify, shows success/failure | `feat(fe): create email verification page` | ✅ |
| F6.6 | Create `app/(auth)/forgot-password/page.tsx` — email input, "Reset link sent" message | `feat(fe): create forgot password page` | ✅ |
| F6.7 | Create `app/(auth)/reset-password/page.tsx` — new password + confirm, reads token from URL | `feat(fe): create reset password page` | ✅ |
| F6.8 | Wire up toast notifications for all auth actions (success, errors) | `feat(fe): add auth toast notifications` | ✅ |
| F6.9 | Add form validation error display (inline under each field) | `style(fe): inline form validation errors` | ✅ |

**Checkpoint:** Full auth flow works end-to-end. User can register → verify email → login → see dashboard.

---

## Phase F7 — Dashboard Page
> *Goal: Authenticated landing page showing user stats, recent activity, and quick actions.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F7.1 | Create `components/dashboard/stats-cards.tsx` — 4 cards: Total Interviews, Average Score, Resumes Uploaded, Last Activity | `feat(fe): dashboard stats cards` | ✅ |
| F7.2 | Create `components/dashboard/quick-actions.tsx` — "Start Interview" + "Upload Resume" buttons | `feat(fe): dashboard quick actions` | ✅ |
| F7.3 | Create `components/dashboard/recent-activity.tsx` — list of recent interviews + resume uploads | `feat(fe): dashboard recent activity` | ✅ |
| F7.4 | Create `app/(app)/dashboard/page.tsx` — compose dashboard components, fetch data via React Query | `feat(fe): create dashboard page` | ✅ |
| F7.5 | Add loading skeletons for each dashboard section | `style(fe): dashboard loading skeletons` | ✅ |

**Checkpoint:** Dashboard shows real data from API. Stats update after interviews/uploads.

---

## Phase F8 — Resume Module (Upload, List, Detail, Analysis)
> *Goal: Full resume CRUD with file upload, analysis display, and version history.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F8.1 | Create `hooks/use-resumes.ts` — React Query hooks: useResumes, useResume, useUploadResume, useDeleteResume | `feat(fe): create resume hooks` | ✅ |
| F8.2 | Create `components/resume/resume-card.tsx` — card showing filename, date, status badge (pending/analyzed/failed) | `feat(fe): create resume card component` | ✅ |
| F8.3 | Create `app/(app)/resumes/page.tsx` — grid of resume cards + "Upload" button | `feat(fe): create resume list page` | ✅ |
| F8.4 | Create `components/resume/resume-upload-zone.tsx` — drag-and-drop with react-dropzone, file type/size validation | `feat(fe): create resume upload component` | ✅ |
| F8.5 | Create `app/(app)/resumes/upload/page.tsx` — upload page with progress indicator | `feat(fe): create resume upload page` | ✅ |
| F8.6 | Create `components/resume/resume-analysis.tsx` — structured display: skills, experience, education, summary | `feat(fe): create resume analysis display` | ✅ |
| F8.7 | Create `app/(app)/resumes/[id]/page.tsx` — resume detail: file info + analysis + versions + actions (delete, export, share) | `feat(fe): create resume detail page` | ✅ |
| F8.8 | Create `components/resume/resume-versions.tsx` — version timeline showing upload dates and changes | `feat(fe): create version history component` | ✅ |
| F8.9 | Add polling for resume analysis status (pending → analyzed) | `feat(fe): poll resume analysis status` | ✅ |
| F8.10 | Add delete confirmation dialog | `feat(fe): resume delete confirmation` | ✅ |

**Checkpoint:** Can upload PDF/DOCX, see it in list, view analysis results, browse versions, delete.

---

## Phase F9 — Interview Module (Configure, Live Q&A, Summary)
> *Goal: Full interview flow — configure, answer questions one by one, see summary.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F9.1 | Create `stores/interview-store.ts` — zustand store: session state machine (configuring → loading → answering → submitting → feedback → completing → summary) | `feat(fe): create interview state store` | ✅ |
| F9.2 | Create `hooks/use-interview.ts` — React Query + zustand integration for interview flow | `feat(fe): create interview hooks` | ✅ |
| F9.3 | Create `components/interview/interview-config.tsx` — form: select resume, question count, difficulty (from Tier 1 improvements) | `feat(fe): create interview config form` | ✅ |
| F9.4 | Create `app/(app)/interviews/start/page.tsx` — config page → "Start" button → POST /start → redirect to session | `feat(fe): create interview start page` | ✅ |
| F9.5 | Create `components/interview/question-display.tsx` — shows current question text, question number (e.g., "Question 3 of 10") | `feat(fe): create question display component` | ✅ |
| F9.6 | Create `components/interview/answer-input.tsx` — textarea with character count, timer, "Submit Answer" button | `feat(fe): create answer input component` | ✅ |
| F9.7 | Create `components/interview/progress-bar.tsx` — visual progress through questions | `feat(fe): create interview progress bar` | ✅ |
| F9.8 | Create `app/(app)/interviews/[sessionId]/page.tsx` — live interview page: question → answer → next question loop | `feat(fe): create live interview page` | ✅ |
| F9.9 | Create `components/interview/interview-summary.tsx` — final score, feedback, per-question breakdown | `feat(fe): create interview summary component` | ✅ |
| F9.10 | Create `components/interview/score-breakdown.tsx` — visual score display (bar chart or radar) | `feat(fe): create score breakdown chart` | ✅ |
| F9.11 | Create `app/(app)/interviews/[sessionId]/summary/page.tsx` — summary page | `feat(fe): create interview summary page` | ✅ |
| F9.12 | Create `components/interview/interview-history-table.tsx` — sortable table: date, resume used, score, status | `feat(fe): create interview history table` | ✅ |
| F9.13 | Create `app/(app)/interviews/page.tsx` — interview history list | `feat(fe): create interview history page` | ✅ |

**Checkpoint:** Full interview flow works: configure → start → answer questions → see summary. History shows past interviews.

---

## Phase F10 — Profile & Settings
> *Goal: User can view profile, change password, manage account.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F10.1 | Create `app/(app)/profile/page.tsx` — shows user info (name, email, join date, email verified status) | `feat(fe): create profile page` | ⬜ |
| F10.2 | Add change password form (current password + new password + confirm) | `feat(fe): add change password form` | ⬜ |
| F10.3 | Add resend verification email button (if not verified) | `feat(fe): add resend verification button` | ⬜ |

**Checkpoint:** User can view profile, change password.

---

## Phase F11 — Admin Panel
> *Goal: Admin users can manage users and view system stats.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F11.1 | Create `app/(app)/admin/layout.tsx` — admin guard, admin sidebar links | `feat(fe): create admin layout` | ✅ |
| F11.2 | Create `components/admin/user-table.tsx` — sortable, paginated user list: name, email, status, role, actions | `feat(fe): create admin user table` | ✅ |
| F11.3 | Create `app/(app)/admin/users/page.tsx` — user management: activate/deactivate, view details | `feat(fe): create admin users page` | ✅ |
| F11.4 | Create `app/(app)/admin/stats/page.tsx` — system stats: total users, total interviews, active sessions | `feat(fe): create admin stats page` | ✅ |

**Checkpoint:** Admin can list users, toggle active status, view system stats.

---

## Phase F12 — Charts & Analytics (Dashboard Enhancement)
> *Goal: Add visual analytics to the dashboard.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F12.1 | Install `recharts` | `chore(fe): install recharts` | ✅ |
| F12.2 | Create `components/dashboard/score-trend-chart.tsx` — line chart showing interview scores over time | `feat(fe): add score trend chart` | ✅ |
| F12.3 | Add skill radar chart — showing strengths/weaknesses from interview feedback | `feat(fe): add skill radar chart` | ✅ |
| F12.4 | Add interview frequency chart — interviews per week/month | `feat(fe): add interview frequency chart` | ✅ |

**Checkpoint:** Dashboard has 3 visual charts showing meaningful analytics.

---

## Phase F13 — Testing
> *Goal: Test coverage for critical flows.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F13.1 | Set up Vitest + React Testing Library | `chore(fe): configure vitest` | ✅ |
| F13.2 | Unit tests for auth store (login, logout, token refresh) | `test(fe): auth store unit tests` | ✅ |
| F13.3 | Unit tests for interview store (state machine transitions) | `test(fe): interview store unit tests` | ✅ |
| F13.4 | Component tests for login form, register form | `test(fe): auth form component tests` | ✅ |
| F13.5 | Component tests for interview config, answer input | `test(fe): interview component tests` | ✅ |
| F13.6 | Set up Playwright for E2E tests | `chore(fe): configure playwright` | ✅ |
| F13.7 | E2E test: register → verify → login → dashboard | `test(fe): auth e2e test` | ✅ |
| F13.8 | E2E test: upload resume → view analysis | `test(fe): resume e2e test` | ✅ |
| F13.9 | E2E test: start interview → answer → summary | `test(fe): interview e2e test` | ✅ |

**Checkpoint:** Core flows have test coverage. CI can run frontend tests.

---

## Phase F14 — CI/CD & Deployment
> *Goal: Frontend builds in CI, deployable to Vercel or Docker.*

| # | Task | Commit Message | Status |
|---|------|---------------|--------|
| F14.1 | Add frontend to GitHub Actions CI: `pnpm lint`, `pnpm build`, `pnpm test` | `ci(fe): add frontend to CI pipeline` | ✅ |
| F14.2 | Create `frontend/Dockerfile` — multi-stage build (deps → build → production) | `chore(fe): add Dockerfile` | ✅ |
| F14.3 | Update root `docker-compose.yml` — add frontend service | `chore: add frontend to docker-compose` | ✅ |
| F14.4 | Create Vercel deployment config (`vercel.json`) as alternative to Docker | `chore(fe): add vercel config` | ✅ |
| F14.5 | Set up environment variable documentation for deployment | `docs(fe): deployment environment variables` | ✅ |

**Checkpoint:** Frontend builds in CI. Deployable via Docker or Vercel.

---

## Progress Tracker

| Phase | Name | Tasks | Status |
|-------|------|-------|--------|
| F0 | Project Scaffold & Tooling | 8 | ✅ |
| F1 | Design System & Shared Components | 9 | ✅ |
| F2 | TypeScript Types & API Client | 8 | ✅ |
| F3 | BFF Proxy Layer | 14 | ✅ |
| F4 | Auth Middleware & Store | 5 | ✅ |
| F5 | Landing Page | 4 | ✅ |
| F6 | Auth Pages | 9 | ✅ |
| F7 | Dashboard Page | 5 | ✅ |
| F8 | Resume Module | 10 | ✅ |
| F9 | Interview Module | 13 | ✅ |
| F10 | Profile & Settings | 3 | ✅ |
| F11 | Admin Panel | 4 | ✅ |
| F12 | Charts & Analytics | 4 | ✅ |
| F13 | Testing | 9 | ✅ |
| F14 | CI/CD & Deployment | 5 | ✅ |
| **TOTAL** | | **110** | |

---

## Execution Rules

1. **One phase at a time.** Do not start F3 before F2 is ✅.
2. **Each task = one commit.** Follow the commit messages exactly.
3. **Test after each phase.** Run `pnpm dev` and manually verify the checkpoint.
4. **No extra features.** If something isn't in the planner, add it as a new phase first.
5. **Update this file** after completing each task. Change ⬜ → ✅.
6. **Dependencies flow downward:**
   ```
   F0 (scaffold)
   ├── F1 (design system)
   │   └── F5 (landing page)
   ├── F2 (types + api client)
   │   └── F3 (BFF proxy)
   │       └── F4 (auth middleware)
   │           ├── F6 (auth pages)
   │           │   └── F7 (dashboard)
   │           │       ├── F8 (resume module)
   │           │       ├── F9 (interview module)
   │           │       ├── F10 (profile)
   │           │       └── F11 (admin panel)
   │           │           └── F12 (charts)
   │           └── F13 (testing) — can start alongside F7+
   └── F14 (CI/CD) — can start alongside F1+
   ```
