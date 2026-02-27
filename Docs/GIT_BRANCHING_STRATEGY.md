# Git Branching Strategy — InterviewAce

> **Recommendation:** Feature branch workflow  
> **Do NOT develop on `main` directly.**

---

## 1. Branch Structure

```
main                    ← Production-ready code. Always clean. Protected.
 │
 ├── develop            ← Integration branch. All features merge here first.
 │    │
 │    ├── feature/frontend-scaffold     (Phase F0)
 │    ├── feature/frontend-design       (Phase F1)
 │    ├── feature/frontend-api-layer    (Phases F2 + F3)
 │    ├── feature/frontend-auth         (Phases F4 + F6)
 │    ├── feature/frontend-dashboard    (Phases F5 + F7)
 │    ├── feature/frontend-resume       (Phase F8)
 │    ├── feature/frontend-interview    (Phase F9)
 │    ├── feature/frontend-admin        (Phases F10 + F11 + F12)
 │    ├── feature/frontend-testing      (Phase F13)
 │    └── feature/frontend-cicd         (Phase F14)
 │
 └── hotfix/*           ← Urgent backend fixes that can't wait for develop
```

---

## 2. Why NOT Develop on Main?

| Approach | Risk | Professional? |
|----------|------|--------------|
| **Direct on main** | Broken commits block all deployments. No rollback safety. | ❌ No |
| **Single feature branch** | One giant PR. Hard to review. Hard to revert pieces. | ⚠️ Acceptable for solo |
| **Feature branches → develop → main** | Clean history. Reviewable PRs. Revertable. | ✅ Industry standard |

Since you're a solo developer, you could simplify to **feature branches → main** (skip `develop`). But using `develop` gives you:

- A safe integration branch to test combinations before promoting to main
- Main always stays deployable (important once you have CI/CD)
- Practice for team workflows you'll encounter professionally

---

## 3. Workflow Commands

### Initial Setup (One-Time)

```bash
# Create and push develop branch
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop
```

### Starting a New Feature

```bash
# Always branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/frontend-scaffold
```

### Working on a Feature

```bash
# Make changes, commit frequently
git add .
git commit -m "feat(fe): scaffold next.js app"

# Push to remote
git push -u origin feature/frontend-scaffold
```

### Merging a Completed Feature

```bash
# Update develop first
git checkout develop
git pull origin develop

# Merge feature branch
git merge feature/frontend-scaffold

# Push develop
git push origin develop

# Delete feature branch (cleanup)
git branch -d feature/frontend-scaffold
git push origin --delete feature/frontend-scaffold
```

### Promoting to Main (After a Phase Group is Stable)

```bash
# Only when develop is tested and stable
git checkout main
git pull origin main
git merge develop
git push origin main
git tag -a v2.0.0-alpha -m "Frontend scaffold + auth"
git push origin --tags
```

---

## 4. Commit Message Convention

Follow **Conventional Commits** (same as your backend):

```
<type>(<scope>): <description>

Types:
  feat     — New feature
  fix      — Bug fix
  chore    — Build/tooling changes
  style    — CSS / formatting (no logic change)
  refactor — Code change that doesn't add feature or fix bug
  test     — Adding/updating tests
  docs     — Documentation only
  ci       — CI/CD pipeline changes

Scope:
  fe       — Frontend changes
  be       — Backend changes
  (empty)  — Affects both or root-level
```

**Examples:**
```
feat(fe): create login page with form validation
fix(fe): handle 401 redirect loop in middleware
chore(fe): install recharts dependency
style(fe): responsive sidebar on mobile
test(fe): add auth store unit tests
ci(fe): add frontend build to GitHub Actions
docs(fe): update FRONTEND_PLANNER.md progress
```

---

## 5. When to Create Tags

| Tag Pattern | When | Example |
|------------|------|---------|
| `v1.x.x` | Backend-only releases (current) | `v1.0.0` |
| `v2.0.0-alpha` | First frontend milestone (auth works) | After Phase F6 |
| `v2.0.0-beta` | All features implemented | After Phase F12 |
| `v2.0.0-rc.1` | Testing complete, pre-launch | After Phase F13 |
| `v2.0.0` | Production-ready full-stack release | After Phase F14 |

---

## 6. .gitignore Additions for Frontend

Add to root `.gitignore`:

```gitignore
# Frontend
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.env.local
frontend/.env*.local
frontend/.vercel
frontend/coverage/
frontend/playwright-report/
frontend/test-results/
```

---

## 7. Recommended Branch Protection Rules (GitHub)

### `main` branch:
- ✅ Require pull request before merging
- ✅ Require status checks to pass (CI: lint + build + test)
- ✅ Require linear history (squash merge or rebase)
- ❌ Allow force pushes (never)

### `develop` branch:
- ✅ Require status checks to pass
- ⬜ Pull request optional (for solo dev, direct merge is fine)

---

## 8. Quick-Start Checklist

- [ ] Create `develop` branch from `main`
- [ ] Push `develop` to remote
- [ ] Set up branch protection on `main` (GitHub → Settings → Branches)
- [ ] Create first feature branch: `feature/frontend-scaffold`
- [ ] Start Phase F0
