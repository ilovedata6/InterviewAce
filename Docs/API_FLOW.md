# InterviewAce — API Flow & Integration Guide

> **Version:** 2.0.0 | **Base URL:** `/api/v1` | **Auth:** Bearer JWT (HS256)

This document describes the complete API surface, request/response contracts, and recommended integration flows for InterviewAce.

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Global Configuration](#2-global-configuration)
3. [Authentication Flows](#3-authentication-flows)
4. [Resume Flows](#4-resume-flows)
5. [Interview Flows](#5-interview-flows)
6. [Health & Task Endpoints](#6-health--task-endpoints)
7. [Full API Reference](#7-full-api-reference)
8. [Error Handling](#8-error-handling)
9. [Rate Limiting](#9-rate-limiting)
10. [Sequence Diagrams](#10-sequence-diagrams)

---

## 1. Quick Start

The typical first-time user journey:

```
Register → Verify Email → Login → Upload Resume → Start Interview → Answer Questions → Complete → View Summary
```

**Minimum steps to conduct an interview:**

```bash
# 1. Register
POST /api/v1/auth/register  { "email": "...", "full_name": "...", "password": "..." }

# 2. Verify email (use token from email)
POST /api/v1/auth/verify-email  { "token": "<verification_token>" }

# 3. Login
POST /api/v1/auth/login  (form-data: username=email, password=...)
# → { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }

# 4. Upload resume (use access_token for all subsequent requests)
POST /api/v1/resume/upload/  (multipart: file=resume.pdf)
# → 202 { "id": "...", "status": "pending", "task_id": "..." }

# 5. Wait for resume processing (poll task)
GET /api/v1/tasks/<task_id>
# → { "status": "SUCCESS" }

# 6. Start interview
POST /api/v1/interview/start
# → { "id": "<session_id>", ... }

# 7. Get first question
GET /api/v1/interview/<session_id>/next
# → { "question_id": "...", "question_text": "..." }

# 8. Answer question (repeat 7-8 until 204 No Content)
POST /api/v1/interview/<session_id>/<question_id>/answer  { "answer_text": "..." }

# 9. Complete interview
POST /api/v1/interview/<session_id>/complete
# → { "final_score": 8.5, "feedback_summary": "...", "question_feedback": [...] }
```

---

## 2. Global Configuration

| Setting | Value |
|---|---|
| Access token expiry | **15 minutes** |
| Refresh token expiry | **7 days** |
| Max upload size | **10 MB** |
| Allowed file types | `pdf`, `docx` |
| Password policy | min 8 chars, must include uppercase + lowercase + digit + special char |
| Global rate limit | **100 requests/minute** |
| Max sessions per user | **5** |
| Session timeout | **30 minutes** |

---

## 3. Authentication Flows

### 3.1 Registration + Email Verification

```
┌──────────┐                              ┌──────────┐                    ┌──────────┐
│  Client   │                              │  Server   │                    │  Email   │
└────┬─────┘                              └────┬─────┘                    └────┬─────┘
     │                                         │                               │
     │  POST /auth/register                    │                               │
     │  { email, full_name, password }         │                               │
     │────────────────────────────────────────►│                               │
     │                                         │  Send verification email      │
     │                                         │──────────────────────────────►│
     │  200 { message: "Verification sent" }   │                               │
     │◄────────────────────────────────────────│                               │
     │                                         │                               │
     │  (User clicks link in email)            │                               │
     │                                         │                               │
     │  POST /auth/verify-email                │                               │
     │  { token: "<from_email>" }              │                               │
     │────────────────────────────────────────►│                               │
     │  200 { message: "Email verified" }      │                               │
     │◄────────────────────────────────────────│                               │
```

**Request — Register:**
```json
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "MyStr0ng!Pass"
}
```

**Response — 200:**
```json
{ "message": "Verification email sent. Please check your inbox." }
```

**Possible errors:**
| Status | Reason |
|--------|--------|
| `400` | Email already registered |
| `422` | Missing/invalid fields |
| `429` | Rate limit exceeded (10/min) |

---

**Request — Verify Email:**
```json
POST /api/v1/auth/verify-email
Content-Type: application/json

{ "token": "abc123-verification-token" }
```

**If verification token expired, resend it:**
```json
POST /api/v1/auth/resend-verification
Content-Type: application/json

{ "email": "user@example.com" }
```

> **Security note:** This always returns 200 regardless of whether the email exists, preventing user enumeration.

---

### 3.2 Login + Token Management

```
┌──────────┐                              ┌──────────┐
│  Client   │                              │  Server   │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │  POST /auth/login                       │
     │  (form: username, password)             │
     │────────────────────────────────────────►│
     │  200 { access_token, refresh_token }    │
     │◄────────────────────────────────────────│
     │                                         │
     │  GET /auth/me                           │
     │  Authorization: Bearer <access_token>   │
     │────────────────────────────────────────►│
     │  200 { id, email, full_name, ... }      │
     │◄────────────────────────────────────────│
     │                                         │
     │  ── (access token nearing expiry) ──    │
     │                                         │
     │  POST /auth/refresh                     │
     │  Authorization: Bearer <refresh_token>  │
     │────────────────────────────────────────►│
     │  200 { new_access_token, new_refresh }  │
     │◄────────────────────────────────────────│
     │                                         │
     │  POST /auth/logout                      │
     │  Authorization: Bearer <access_token>   │
     │────────────────────────────────────────►│
     │  200 { message: "Logged out" }          │
     │◄────────────────────────────────────────│
```

**Request — Login:**
```
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=MyStr0ng!Pass
```

> **Important:** Login uses **form data** (OAuth2 spec), not JSON. The `username` field accepts the user's email address.

**Response — 200:**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

**Possible errors:**
| Status | Reason |
|--------|--------|
| `401` | Incorrect email/password, or account locked |
| `403` | Email not yet verified |
| `429` | Rate limit exceeded (5/min) |

---

**Token Refresh:**
```
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```
Returns a new token pair (both access and refresh tokens are rotated).

**Logout:**
```
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```
Revokes the current session and tokens.

---

### 3.3 Password Reset (Forgot Password)

```
┌──────────┐                              ┌──────────┐                    ┌──────────┐
│  Client   │                              │  Server   │                    │  Email   │
└────┬─────┘                              └────┬─────┘                    └────┬─────┘
     │                                         │                               │
     │  POST /auth/reset-password-request      │                               │
     │  { email }                              │                               │
     │────────────────────────────────────────►│──────────────────────────────►│
     │  200 { message }                        │   Reset token email           │
     │◄────────────────────────────────────────│                               │
     │                                         │                               │
     │  POST /auth/reset-password-confirm      │                               │
     │  { token, new_password }                │                               │
     │────────────────────────────────────────►│                               │
     │  200 { message: "Password reset" }      │                               │
     │◄────────────────────────────────────────│                               │
```

**Request:**
```json
POST /api/v1/auth/reset-password-request
{ "email": "user@example.com" }
```

**Confirm with token from email:**
```json
POST /api/v1/auth/reset-password-confirm
{ "token": "reset-token-from-email", "new_password": "NewStr0ng!Pass" }
```

---

### 3.4 Change Password (While Logged In)

```json
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{ "old_password": "MyStr0ng!Pass", "new_password": "NewStr0ng!Pass" }
```

**Possible errors:**
| Status | Reason |
|--------|--------|
| `400` | Old password incorrect, or new password same as old |
| `401` | Not authenticated |

---

## 4. Resume Flows

### 4.1 Upload + Processing

```
┌──────────┐                              ┌──────────┐                    ┌──────────┐
│  Client   │                              │  Server   │                    │   LLM    │
└────┬─────┘                              └────┬─────┘                    └────┬─────┘
     │                                         │                               │
     │  POST /resume/upload/                   │                               │
     │  multipart: file=resume.pdf             │                               │
     │────────────────────────────────────────►│                               │
     │  202 { id, status:"pending", task_id }  │                               │
     │◄────────────────────────────────────────│                               │
     │                                         │  Background: parse resume     │
     │                                         │──────────────────────────────►│
     │  GET /tasks/<task_id>                   │                               │
     │────────────────────────────────────────►│                               │
     │  200 { status: "PENDING" }              │                               │
     │◄────────────────────────────────────────│◄──────────────────────────────│
     │                                         │   Analysis result             │
     │  GET /tasks/<task_id>  (poll again)     │                               │
     │────────────────────────────────────────►│                               │
     │  200 { status: "SUCCESS", result }      │                               │
     │◄────────────────────────────────────────│                               │
     │                                         │                               │
     │  GET /resume/<resume_id>                │                               │
     │────────────────────────────────────────►│                               │
     │  200 { full resume with analysis }      │                               │
     │◄────────────────────────────────────────│                               │
```

**Upload Request:**
```
POST /api/v1/resume/upload/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file=@resume.pdf
```

**Response — 202 Accepted:**
```json
{
  "id": "a1b2c3d4-...",
  "file_name": "resume.pdf",
  "status": "pending",
  "message": "Resume uploaded successfully. Processing started.",
  "file_size": 245760,
  "file_type": "application/pdf",
  "task_id": "celery-task-id-123"
}
```

**Constraints:**
- Max file size: 10 MB
- Allowed types: `pdf`, `docx`
- Rate limit: 10 uploads/minute

**Processing States:**
| Status | Meaning |
|--------|---------|
| `pending` | Uploaded, queued for parsing |
| `processing` | LLM is analyzing the resume |
| `analyzed` | Parsing complete — skills, experience extracted |
| `error` | Parsing failed |

---

### 4.2 List & Search Resumes

```
GET /api/v1/resume/?skip=0&limit=10&status=analyzed&search=python
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset (≥ 0) |
| `limit` | int | `10` | Page size (1–100) |
| `status` | string | — | Filter: `pending`, `processing`, `analyzed`, `error` |
| `search` | string | — | Full-text search on title/description |

**Response — 200:**
```json
{
  "items": [
    {
      "id": "a1b2c3d4-...",
      "title": "resume.pdf",
      "status": "analyzed",
      "skills": ["Python", "FastAPI", "PostgreSQL"],
      "inferred_role": "Backend Developer",
      "years_of_experience": 5.0,
      "created_at": "2025-01-15T10:30:00Z",
      ...
    }
  ],
  "total": 3,
  "skip": 0,
  "limit": 10,
  "has_more": false
}
```

---

### 4.3 Get / Update / Delete Resume

**Get single resume:**
```
GET /api/v1/resume/<resume_id>
Authorization: Bearer <access_token>
```

**Update metadata:**
```json
PUT /api/v1/resume/<resume_id>
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Senior Backend Resume",
  "description": "Updated for 2025 applications",
  "tags": ["backend", "python", "senior"]
}
```
All fields are optional. Only provided fields are updated.

**Delete resume:**
```
DELETE /api/v1/resume/<resume_id>
Authorization: Bearer <access_token>
→ 204 No Content
```

---

## 5. Interview Flows

### 5.1 Complete Interview Flow

```
┌──────────┐                              ┌──────────┐                    ┌──────────┐
│  Client   │                              │  Server   │                    │   LLM    │
└────┬─────┘                              └────┬─────┘                    └────┬─────┘
     │                                         │                               │
     │  POST /interview/start                  │                               │
     │────────────────────────────────────────►│  Generate questions from      │
     │                                         │  user's latest resume         │
     │                                         │──────────────────────────────►│
     │                                         │◄──────────────────────────────│
     │  200 { session_id, resume_id, ... }     │  12-15 questions              │
     │◄────────────────────────────────────────│                               │
     │                                         │                               │
     │  ┌─── Question Loop ────────────────┐   │                               │
     │  │                                  │   │                               │
     │  │  GET /interview/{sid}/next       │   │                               │
     │  │─────────────────────────────────►│   │                               │
     │  │  200 { question_id, text }       │   │                               │
     │  │◄─────────────────────────────────│   │                               │
     │  │                                  │   │                               │
     │  │  POST /interview/{sid}/{qid}/    │   │                               │
     │  │       answer                     │   │                               │
     │  │  { answer_text }                 │   │                               │
     │  │─────────────────────────────────►│   │                               │
     │  │  200 { next question }           │   │                               │
     │  │  or 204 (no more questions)      │   │                               │
     │  │◄─────────────────────────────────│   │                               │
     │  │                                  │   │                               │
     │  └──── Repeat until 204 ────────────┘   │                               │
     │                                         │                               │
     │  POST /interview/{sid}/complete         │  Evaluate all answers,        │
     │────────────────────────────────────────►│  generate scores & feedback   │
     │                                         │──────────────────────────────►│
     │                                         │◄──────────────────────────────│
     │  200 { final_score, feedback, ... }     │                               │
     │◄────────────────────────────────────────│                               │
     │                                         │                               │
     │  GET /interview/{sid}/summary           │                               │
     │────────────────────────────────────────►│                               │
     │  200 { detailed AI summary }            │                               │
     │◄────────────────────────────────────────│                               │
```

**Prerequisites:** User must have at least one uploaded resume (status: `analyzed`).

---

### 5.2 Start Interview

```
POST /api/v1/interview/start
Authorization: Bearer <access_token>
```

No request body needed — the server automatically picks the user's most recent resume.

**Response — 200:**
```json
{
  "id": "session-uuid-...",
  "user_id": "user-uuid-...",
  "resume_id": "resume-uuid-...",
  "started_at": "2025-01-15T10:30:00Z",
  "completed_at": null,
  "final_score": null,
  "feedback_summary": null
}
```

**Possible errors:**
| Status | Reason |
|--------|--------|
| `404` | No resume found — upload one first |
| `500` | Question generation failed (LLM error) |

---

### 5.3 Get Next Question

```
GET /api/v1/interview/<session_id>/next
Authorization: Bearer <access_token>
```

**Response — 200:**
```json
{
  "question_id": "question-uuid-...",
  "question_text": "Explain how you would design a RESTful API for a microservices architecture."
}
```

**Response — 204:** No Content (all questions have been answered — ready to complete)

---

### 5.4 Submit Answer

```json
POST /api/v1/interview/<session_id>/<question_id>/answer
Authorization: Bearer <access_token>
Content-Type: application/json

{ "answer_text": "I would start by identifying bounded contexts..." }
```

**Response — 200:** Returns the next question (same schema as 5.3)
**Response — 204:** No more questions — proceed to complete

> **Tip:** The answer endpoint returns the next question directly, so you can skip the separate `GET /next` call after each answer.

---

### 5.5 Complete Interview

```
POST /api/v1/interview/<session_id>/complete
Authorization: Bearer <access_token>
```

**Response — 200:**
```json
{
  "session_id": "session-uuid-...",
  "final_score": 8.5,
  "feedback_summary": "Strong technical knowledge with room for improvement in system design...",
  "question_feedback": [
    {
      "question_id": "q1-uuid",
      "evaluation_score": 9.0,
      "feedback_comment": "Excellent understanding of RESTful principles..."
    },
    {
      "question_id": "q2-uuid",
      "evaluation_score": 7.5,
      "feedback_comment": "Good answer but could include more specifics..."
    }
  ]
}
```

---

### 5.6 View Session Details & History

**Get a specific session:**
```
GET /api/v1/interview/<session_id>
Authorization: Bearer <access_token>
```

**Get detailed AI summary:**
```
GET /api/v1/interview/<session_id>/summary
Authorization: Bearer <access_token>
```

**List all past interviews (paginated):**
```
GET /api/v1/interview/history?skip=0&limit=10
Authorization: Bearer <access_token>
```

**Response — 200:**
```json
{
  "items": [
    {
      "id": "session-uuid-...",
      "resume_id": "resume-uuid-...",
      "started_at": "2025-01-15T10:30:00Z",
      "completed_at": "2025-01-15T11:00:00Z",
      "final_score": 8.5,
      "feedback_summary": "..."
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 10,
  "has_more": false
}
```

---

## 6. Health & Task Endpoints

### Health Check (no auth, no `/api/v1` prefix)

```
GET /health    → { "status": "healthy" }
GET /ready     → { "status": "ready", "checks": { "database": "ok", "redis": "ok" } }
```

### Task Status Polling

```
GET /api/v1/tasks/<task_id>
```

**Response:**
```json
{
  "task_id": "celery-task-id-123",
  "status": "SUCCESS",
  "result": { ... },
  "error": null
}
```

**Task states:** `PENDING` → `STARTED` → `SUCCESS` | `FAILURE` | `RETRY` | `REVOKED`

---

## 7. Full API Reference

### Auth Endpoints — `/api/v1/auth`

| # | Method | Path | Auth | Rate Limit | Description |
|---|--------|------|------|------------|-------------|
| 1 | `POST` | `/auth/register` | No | 10/min | Register a new account |
| 2 | `POST` | `/auth/login` | No | 5/min | Login (returns token pair) |
| 3 | `GET` | `/auth/me` | **Yes** | — | Get current user profile |
| 4 | `POST` | `/auth/logout` | **Yes** | — | Logout (revoke session) |
| 5 | `POST` | `/auth/refresh` | **Yes**¹ | — | Refresh token pair |
| 6 | `POST` | `/auth/change-password` | **Yes** | — | Change password |
| 7 | `POST` | `/auth/verify-email` | No | — | Verify email with token |
| 8 | `POST` | `/auth/resend-verification` | No | — | Resend verification email |
| 9 | `POST` | `/auth/reset-password-request` | No | 3/min | Request password reset |
| 10 | `POST` | `/auth/reset-password-confirm` | No | — | Confirm password reset |

¹ Send the **refresh token** (not access token) in the Authorization header.

### Interview Endpoints — `/api/v1/interview`

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 11 | `POST` | `/interview/start` | **Yes** | Start new interview session |
| 12 | `GET` | `/interview/{session_id}/next` | **Yes** | Get next unanswered question |
| 13 | `POST` | `/interview/{session_id}/{question_id}/answer` | **Yes** | Submit answer to question |
| 14 | `POST` | `/interview/{session_id}/complete` | **Yes** | Complete and get evaluation |
| 15 | `GET` | `/interview/{session_id}` | **Yes** | Get session details |
| 16 | `GET` | `/interview/history` | **Yes** | List past interviews |
| 17 | `GET` | `/interview/{session_id}/summary` | **Yes** | Get AI-generated summary |

### Resume Endpoints — `/api/v1/resume`

| # | Method | Path | Auth | Rate Limit | Description |
|---|--------|------|------|------------|-------------|
| 18 | `POST` | `/resume/upload/` | **Yes** | 10/min | Upload resume file |
| 19 | `GET` | `/resume/` | **Yes** | — | List resumes (paginated) |
| 20 | `GET` | `/resume/{resume_id}` | **Yes** | — | Get resume details |
| 21 | `PUT` | `/resume/{resume_id}` | **Yes** | — | Update resume metadata |
| 22 | `DELETE` | `/resume/{resume_id}` | **Yes** | — | Delete resume |

### Utility Endpoints

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 23 | `GET` | `/health` | No | Liveness probe |
| 24 | `GET` | `/ready` | No | Readiness probe (DB + Redis) |
| 25 | `GET` | `/tasks/{task_id}` | No | Poll background task status |

---

## 8. Error Handling

All errors follow a consistent JSON structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | Success | Standard success response |
| `202` | Accepted | Resume upload (processing starts in background) |
| `204` | No Content | Successful delete, or no more interview questions |
| `400` | Bad Request | Validation errors, duplicate email, wrong password |
| `401` | Unauthorized | Missing/expired/invalid token |
| `403` | Forbidden | Email not verified (login) |
| `404` | Not Found | Resource doesn't exist or belongs to another user |
| `422` | Unprocessable | JSON schema validation error (missing required fields) |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Server Error | Internal error (LLM failure, DB error) |

**Security behavior:**
- Resources belonging to other users return `404` (not `403`) to prevent enumeration
- Password reset and resend-verification always return `200` regardless of email existence
- JWTs are validated on every authenticated request; expired tokens return `401`

---

## 9. Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /auth/register` | 10 requests | 1 minute |
| `POST /auth/login` | 5 requests | 1 minute |
| `POST /auth/reset-password-request` | 3 requests | 1 minute |
| `POST /resume/upload/` | 10 requests | 1 minute |
| All other endpoints | 100 requests | 1 minute |

When rate limited, the server responds with:
```
HTTP 429 Too Many Requests
Retry-After: <seconds>
```

---

## 10. Sequence Diagrams

### Full User Journey

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTERVIEWACE — FULL USER FLOW                       │
└─────────────────────────────────────────────────────────────────────────────┘

PHASE 1: ACCOUNT SETUP
═══════════════════════

  ┌─────────────┐                    ┌─────────────┐
  │   CLIENT    │                    │   SERVER    │
  └──────┬──────┘                    └──────┬──────┘
         │  1. POST /auth/register          │
         │  { email, name, password }       │
         │─────────────────────────────────►│ ──► Send verification email
         │  200 "Verification sent"         │
         │◄─────────────────────────────────│
         │                                  │
         │  2. POST /auth/verify-email      │
         │  { token from email }            │
         │─────────────────────────────────►│ ──► Mark user as verified
         │  200 "Email verified"            │
         │◄─────────────────────────────────│
         │                                  │
         │  3. POST /auth/login             │
         │  (form: username, password)      │
         │─────────────────────────────────►│ ──► Create session
         │  200 { access_token,             │
         │        refresh_token }           │
         │◄─────────────────────────────────│
         │                                  │

PHASE 2: RESUME UPLOAD
══════════════════════

         │  4. POST /resume/upload/         │
         │  (file: resume.pdf)              │
         │─────────────────────────────────►│ ──► Queue background parsing
         │  202 { id, task_id,              │
         │        status: "pending" }       │
         │◄─────────────────────────────────│
         │                                  │
         │  5. GET /tasks/{task_id}         │
         │  (poll every 2-3 seconds)        │
         │─────────────────────────────────►│
         │  200 { status: "SUCCESS" }       │
         │◄─────────────────────────────────│
         │                                  │

PHASE 3: INTERVIEW
═════════════════

         │  6. POST /interview/start        │
         │─────────────────────────────────►│ ──► LLM generates 12-15 Qs
         │  200 { session_id }              │     from resume content
         │◄─────────────────────────────────│
         │                                  │
         │  7. GET /interview/{sid}/next    │
         │─────────────────────────────────►│
         │  200 { question_id, text }       │
         │◄─────────────────────────────────│
         │                                  │
         │  8. POST /interview/{sid}/{qid}/ │
         │     answer { answer_text }       │
         │─────────────────────────────────►│
         │  200 { next_question }           │
         │  or 204 (no more questions)      │
         │◄─────────────────────────────────│
         │                                  │
         │     ↑ Repeat steps 7-8 ↑         │
         │                                  │
         │  9. POST /interview/{sid}/       │
         │     complete                     │
         │─────────────────────────────────►│ ──► LLM evaluates answers
         │  200 { final_score: 8.5,         │
         │    feedback_summary,             │
         │    question_feedback[] }         │
         │◄─────────────────────────────────│
         │                                  │

PHASE 4: REVIEW & HISTORY
═════════════════════════

         │  10. GET /interview/{sid}/       │
         │      summary                     │
         │─────────────────────────────────►│
         │  200 { detailed AI summary }     │
         │◄─────────────────────────────────│
         │                                  │
         │  11. GET /interview/history      │
         │      ?skip=0&limit=10            │
         │─────────────────────────────────►│
         │  200 { items[], total }          │
         │◄─────────────────────────────────│

TOKEN MAINTENANCE (throughout all phases):
══════════════════════════════════════════

         │  POST /auth/refresh              │
         │  Bearer <refresh_token>          │
         │─────────────────────────────────►│
         │  200 { new tokens }              │
         │◄─────────────────────────────────│
```

### Token Refresh Strategy

```
Timeline:
─────────────────────────────────────────────────────────────────►

  Login          Refresh          Refresh          Logout
   │               │                │                │
   ▼               ▼                ▼                ▼
   ├──── 15m ─────►├──── 15m ─────►├──── 15m ─────►│
   │  Access Token  │  Access Token  │  Access Token  │
   │                │                │                │
   ├────────────── 7d ──────────────────────────────►│
   │           Refresh Token                          │

Recommended: Refresh the access token when ~80% of its lifetime
has elapsed (around the 12-minute mark).
```

---

## Appendix: Request/Response Schema Reference

### UserCreate (Register)
```json
{
  "email": "string (valid email)",
  "full_name": "string",
  "password": "string (min 8, upper+lower+digit+special)"
}
```

### Token (Login/Refresh Response)
```json
{
  "access_token": "string (JWT)",
  "refresh_token": "string (JWT)",
  "token_type": "bearer"
}
```

### UserResponse (Me)
```json
{
  "id": "uuid",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### ResumeResponse
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "resume.pdf",
  "description": null,
  "tags": [],
  "file_path": "uploads/abc123.pdf",
  "file_name": "resume.pdf",
  "file_size": 245760,
  "file_type": "application/pdf",
  "status": "analyzed",
  "inferred_role": "Backend Developer",
  "years_of_experience": 5.0,
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "analysis": { "experience": [...], "education": [...] },
  "version": 1,
  "parent_version_id": null,
  "is_public": false,
  "share_token": null
}
```

### ResumeUpdate
```json
{
  "title": "string (1-100 chars, optional)",
  "description": "string (max 500 chars, optional)",
  "tags": ["string (max 10 items, optional)"]
}
```

### InterviewSessionInDB
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "resume_id": "uuid",
  "started_at": "2025-01-15T10:30:00Z",
  "completed_at": null,
  "final_score": null,
  "feedback_summary": null
}
```

### QuestionOut
```json
{
  "question_id": "uuid",
  "question_text": "Explain your experience with..."
}
```

### AnswerIn
```json
{
  "answer_text": "string"
}
```

### SummaryOut
```json
{
  "session_id": "uuid",
  "final_score": 8.5,
  "feedback_summary": "Overall assessment...",
  "question_feedback": [
    {
      "question_id": "uuid",
      "evaluation_score": 9.0,
      "feedback_comment": "Excellent..."
    }
  ]
}
```

### PaginatedResponse
```json
{
  "items": [],
  "total": 0,
  "skip": 0,
  "limit": 10,
  "has_more": false
}
```
