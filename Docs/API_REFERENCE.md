# API Reference

Base URL: `http://localhost:8000/api/v1`

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## Authentication `/auth`

### `POST /auth/register`
Register a new user.

**Request Body**
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "Str0ng@Pass"
}
```

**Response `201`**
```json
{
  "id": "uuid",
  "email": "jane@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_email_verified": false
}
```

---

### `POST /auth/login`
Authenticate and obtain tokens.

**Request Body** (`application/x-www-form-urlencoded`)
```
username=jane@example.com&password=Str0ng@Pass
```

**Response `200`**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

---

### `POST /auth/refresh`
Exchange a refresh token for a new access token.

**Request Body**
```json
{ "refresh_token": "<jwt>" }
```

**Response `200`**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

### `POST /auth/logout`
🔒 Protected. Blacklists the current access token.

**Response `200`**
```json
{ "message": "Successfully logged out" }
```

---

### `GET /auth/me`
🔒 Protected. Returns the current user's profile.

**Response `200`**
```json
{
  "id": "uuid",
  "email": "jane@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_email_verified": true
}
```

---

### `POST /auth/verify-email`
Submit the email verification token received by email.

**Request Body**
```json
{ "token": "<verification_token>" }
```

**Response `200`**
```json
{ "message": "Email verified successfully" }
```

---

### `POST /auth/resend-verification`
Resend the verification email.

**Request Body**
```json
{ "email": "jane@example.com" }
```

---

### `POST /auth/reset-password/request`
Trigger a password-reset email.

**Request Body**
```json
{ "email": "jane@example.com" }
```

---

### `POST /auth/reset-password/confirm`
Set a new password using the reset token.

**Request Body**
```json
{
  "token": "<reset_token>",
  "new_password": "NewStr0ng@Pass"
}
```

---

### `POST /auth/change-password`
🔒 Protected. Change password while authenticated.

**Request Body**
```json
{
  "current_password": "OldStr0ng@Pass",
  "new_password": "NewStr0ng@Pass"
}
```

---

## Resume `/resume`

### `POST /resume/`
🔒 Protected. Upload and analyze a resume.

**Request** `multipart/form-data`
```
file: <PDF or DOCX, max 10 MB>
```

**Response `201`**
```json
{
  "id": "uuid",
  "file_name": "<uuid>.pdf",
  "status": "analyzed",
  "file_size": 204800,
  "message": "Resume uploaded and parsed successfully.",
  "file_type": "pdf"
}
```

---

### `GET /resume/`
🔒 Protected. List all resumes for the current user.

**Response `200`** — array of resume objects

---

### `GET /resume/{resume_id}`
🔒 Protected. Get a single resume by ID.

---

### `DELETE /resume/{resume_id}`
🔒 Protected. Delete a resume.

---

### `GET /resume/{resume_id}/analysis`
🔒 Protected. Get the full AI-parsed analysis JSON for a resume.

**Response `200`**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "inferred_role": "Backend Engineer",
  "years_of_experience": 4.5,
  "experience": [...],
  "education": [...],
  "confidence_score": 0.93
}
```

---

### `GET /resume/{resume_id}/version`
🔒 Protected. Get version history for a resume.

---

### `POST /resume/{resume_id}/share`
🔒 Protected. Generate or toggle a public share token.

---

### `GET /resume/shared/{share_token}`
Public. View a shared resume by token (no auth required).

---

### `GET /resume/{resume_id}/export`
🔒 Protected. Export resume data.

---

## Interview `/interview`

### `POST /interview/`
🔒 Protected. Start a new interview session using the user's latest resume.

**Request Body**
```json
{ "resume_id": "uuid" }
```

**Response `200`**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "resume_id": "uuid",
  "started_at": "2026-02-22T10:00:00Z",
  "completed_at": null,
  "final_score": null,
  "feedback_summary": null
}
```
> Generates 12–15 questions (5 technical, 3 behavioural, 5–4 project-based) on creation.

---

### `GET /interview/{session_id}`
🔒 Protected. Get session details.

---

### `GET /interview/{session_id}/next`
🔒 Protected. Get the next unanswered question.

**Response `200`**
```json
{
  "question_id": "uuid",
  "question_text": "Explain how you optimized the database queries in Project X."
}
```

---

### `POST /interview/{session_id}/answer`
🔒 Protected. Submit an answer to the current question.

**Request Body**
```json
{
  "answer_text": "I used index optimization and query caching..."
}
```

**Response `200`** — Question with evaluation score and feedback comment

---

### `POST /interview/{session_id}/complete`
🔒 Protected. Mark the session complete and request the final summary.

**Response `200`**
```json
{
  "session_id": "uuid",
  "final_score": 7.4,
  "feedback_summary": "Strong technical depth but behavioural answers need more STAR structure.",
  "question_feedback": [...]
}
```

---

### `GET /interview/{session_id}/summary`
🔒 Protected. Retrieve the summary for a completed session.

---

### `GET /interview/history`
🔒 Protected. List all interview sessions for the current user.

**Response `200`** — array of `InterviewSession` objects

---

## Error Responses

| Status | Meaning |
|---|---|
| `400` | Bad request / validation error |
| `401` | Missing or invalid token |
| `403` | Forbidden (e.g. not your resource) |
| `404` | Resource not found |
| `422` | Pydantic validation failure |
| `429` | Rate limit exceeded (100 req/min per IP) |
| `500` | Internal server error (LLM failure, DB error, etc.) |
