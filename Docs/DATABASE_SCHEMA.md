# Database Schema

**Engine:** PostgreSQL  
**ORM:** SQLAlchemy 2.0 (synchronous)  
**Migration tool:** None — `Base.metadata.create_all()` only *(see [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md))*

All tables inherit `created_at` and `updated_at` timestamp columns from `TimestampMixin`.

---

## Tables

### `users`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK, default `uuid4` |
| `full_name` | VARCHAR | NOT NULL |
| `email` | VARCHAR | UNIQUE, NOT NULL |
| `hashed_password` | VARCHAR | NOT NULL |
| `is_active` | BOOLEAN | default `true` |
| `is_email_verified` | BOOLEAN | default `false` |
| `created_at` | TIMESTAMP | auto |
| `updated_at` | TIMESTAMP | auto |

---

### `resumes`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → `users.id` |
| `title` | VARCHAR(100) | NOT NULL |
| `description` | TEXT | nullable |
| `file_path` | VARCHAR | NOT NULL |
| `file_name` | VARCHAR(255) | NOT NULL |
| `file_size` | INTEGER | NOT NULL |
| `file_type` | ENUM(pdf, docx) | NOT NULL |
| `inferred_role` | VARCHAR(100) | nullable |
| `status` | ENUM(pending, analyzed, failed) | default `pending` |
| `analysis` | JSON | nullable — full Gemini output |
| `version` | INTEGER | NOT NULL, default `1` |
| `years_of_experience` | INTEGER | nullable |
| `skills` | JSON | nullable — list of strings |
| `parent_version_id` | UUID | FK → `resumes.id` (self-ref) |
| `is_public` | BOOLEAN | default `false` |
| `share_token` | VARCHAR(64) | UNIQUE, nullable |
| `confidence_score` | FLOAT | nullable |
| `processing_time` | FLOAT | nullable |
| `created_at` | TIMESTAMP | auto |
| `updated_at` | TIMESTAMP | auto |

---

### `interview_sessions`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → `users.id` |
| `resume_id` | UUID | FK → `resumes.id` |
| `started_at` | DATETIME | NOT NULL |
| `completed_at` | DATETIME | nullable |
| `final_score` | FLOAT | nullable |
| `feedback_summary` | TEXT | nullable |
| `created_at` | TIMESTAMP | auto |
| `updated_at` | TIMESTAMP | auto |

---

### `interview_questions`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `session_id` | UUID | FK → `interview_sessions.id` |
| `question_text` | TEXT | NOT NULL |
| `answer_text` | TEXT | nullable |
| `evaluation_score` | FLOAT | nullable |
| `feedback_comment` | TEXT | nullable |
| `created_at` | TIMESTAMP | auto |
| `updated_at` | TIMESTAMP | auto |

---

### `login_attempts`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → `users.id` |
| `ip_address` | VARCHAR(45) | NOT NULL (IPv6 safe) |
| `success` | BOOLEAN | default `false` |
| `locked_until` | DATETIME(tz) | nullable |
| `created_at` | TIMESTAMP | auto (server_default) |

---

### `token_blacklist`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `token_id` | VARCHAR(36) | UNIQUE, NOT NULL |
| `user_id` | UUID | FK → `users.id` |
| `expires_at` | DATETIME(tz) | NOT NULL |
| `reason` | VARCHAR(255) | nullable |
| `created_at` | TIMESTAMP | auto |

> ⚠️ No pruning mechanism — grows indefinitely. See [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md#13-token-blacklist-grows-without-pruning).

---

### `user_sessions`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → `users.id` |
| `session_id` | VARCHAR(36) | UNIQUE |
| `ip_address` | VARCHAR(45) | NOT NULL |
| `user_agent` | VARCHAR(255) | nullable |
| `session_data` | VARCHAR(1000) | nullable (JSON string) |
| `last_activity` | DATETIME(tz) | auto |
| `is_active` | BOOLEAN | default `true` |
| `created_at` | TIMESTAMP | auto |

---

### `password_history`
| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → `users.id` |
| `password_hash` | VARCHAR(255) | NOT NULL |
| `is_active` | BOOLEAN | default `true` |
| `created_at` | TIMESTAMP | auto |

> Keeps last 5 entries per user. New passwords are checked against all active entries.

---

### `password_reset_tokens`
| Column | Type | Constraints |
|---|---|---|
| `token` | VARCHAR | PK (UUID string) |
| `user_id` | UUID | FK → `users.id` |
| `expires_at` | DATETIME | NOT NULL (15-minute TTL) |
| `used` | BOOLEAN | default `false` |
| `created_at` | DATETIME | default `now()` |

---

## Entity Relationships

```
users ─────┬──── resumes (one-to-many)
           │       └──── interview_sessions (one-to-many)
           │                └──── interview_questions (one-to-many)
           │
           ├──── login_attempts (one-to-many)
           ├──── token_blacklist (one-to-many)
           ├──── user_sessions (one-to-many)
           ├──── password_history (one-to-many)
           └──── password_reset_tokens (one-to-many)

resumes ───┬──── resumes (self-ref parent_version_id, for versioning)
           └──── interview_sessions (one-to-many)
```

---

## Notes

- All primary keys are **UUID v4** (not auto-increment integers). This avoids enumeration attacks and is safe for distributed inserts.
- The `analysis` column on `resumes` stores the **full raw JSON** returned by Gemini. This makes querying individual fields (skills, experience entries) less efficient than normalized tables but keeps the schema simple and flexible.
- `user_sessions.session_data` is a JSON blob stored as a VARCHAR string — not a proper `JSONB` column. Consider switching to `JSONB` in PostgreSQL for query support.
- There is no soft-delete pattern — records are hard-deleted.
