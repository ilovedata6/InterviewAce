# InterviewAce v2 — Architecture Guide

## Clean Architecture Overview

InterviewAce v2 follows **Layered Clean Architecture** with clear dependency rules:

```
┌─────────────────────────────────────────────────┐
│                  Presentation                   │
│              (api/, schemas/)                    │
├─────────────────────────────────────────────────┤
│                    Domain                       │
│   (domain/entities/, interfaces/, exceptions)    │
├─────────────────────────────────────────────────┤
│                Infrastructure                   │
│  (infrastructure/persistence/, llm/, cache/,    │
│   tasks/)                                       │
└─────────────────────────────────────────────────┘
```

### Dependency Rule
Inner layers NEVER import from outer layers:
- **Domain** → depends on nothing (pure Python)
- **Infrastructure** → implements Domain interfaces
- **Presentation** → depends on Domain & Infrastructure

---

## Directory Structure

```
backend/app/
├── domain/                           # Layer 0 — Pure business logic
│   ├── entities/                     # Business objects (dataclasses)
│   │   ├── user.py                   # UserEntity
│   │   ├── resume.py                 # ResumeEntity
│   │   └── interview.py             # InterviewSessionEntity, InterviewQuestionEntity
│   ├── interfaces/                   # Ports (ABCs)
│   │   ├── repositories.py          # IUserRepository, IResumeRepository, IInterviewRepository
│   │   └── llm_provider.py          # ILLMProvider
│   ├── value_objects/                # Enums, constants
│   │   └── enums.py                 # ResumeStatus, FileType, UserRole (single source of truth)
│   └── exceptions.py                # Domain exception hierarchy
│
├── infrastructure/                   # Layer 1 — Framework adapters
│   ├── persistence/
│   │   ├── models/                   # SQLAlchemy ORM models (canonical location)
│   │   │   ├── base.py              # Base, TimestampMixin
│   │   │   ├── user.py              # User
│   │   │   ├── resume.py            # Resume
│   │   │   ├── interview.py         # InterviewSession, InterviewQuestion
│   │   │   └── security.py          # LoginAttempt, TokenBlacklist, etc.
│   │   └── repositories/            # Concrete repository implementations
│   │       ├── user_repository.py   # UserRepository(IUserRepository)
│   │       ├── resume_repository.py # ResumeRepository(IResumeRepository)
│   │       └── interview_repository.py # InterviewRepository(IInterviewRepository)
│   ├── llm/                          # LLM adapters
│   │   ├── openai_provider.py       # OpenAIProvider(ILLMProvider) — primary
│   │   ├── gemini_provider.py       # GeminiProvider(ILLMProvider) — fallback
│   │   └── factory.py               # LLMProviderWithFallback + get_llm_provider()
│   ├── cache/                        # Redis cache layer
│   │   └── redis_client.py          # Async Redis singleton, token blacklist, rate limit
│   └── tasks/                        # Background tasks (Celery)
│       ├── celery_app.py            # Celery config (Redis broker + backend)
│       ├── resume_tasks.py          # parse_resume_task (background LLM parsing)
│       └── maintenance.py           # prune_expired_tokens (hourly Celery Beat)
│
├── api/                              # Presentation layer
├── core/                             # Cross-cutting concerns
│   ├── config.py                     # Settings
│   ├── middleware.py                 # CORS, security headers, rate limiting
│   ├── security.py                   # JWT, password hashing
│   ├── logging_config.py            # structlog pipeline setup
│   └── exceptions.py                # Domain exception → HTTP mapping
├── db/                               # Database session management
├── models/                           # Backward-compatible re-exports → infrastructure
├── schemas/                          # Pydantic schemas (API DTOs)
├── services/                         # Service layer (orchestrators, parsers)
└── utils/                            # File handling, email utilities
```

---

## Domain Interfaces (Ports)

| Interface | Purpose | Concrete Implementation |
|---|---|---|
| `IUserRepository` | User CRUD persistence | `UserRepository` (SQLAlchemy) |
| `IResumeRepository` | Resume CRUD + queries | `ResumeRepository` (SQLAlchemy) |
| `IInterviewRepository` | Session & question persistence | `InterviewRepository` (SQLAlchemy) |
| `ILLMProvider` | Question generation, feedback, parsing | `OpenAIProvider` (primary), `GeminiProvider` (fallback) |

---

## Domain Exceptions

All domain exceptions extend `DomainException(message, code)`:

| Exception | HTTP Status | Use Case |
|---|---|---|
| `EntityNotFoundError` | 404 | User/resume/session not found |
| `AuthenticationError` | 401 | Bad credentials |
| `AuthorizationError` | 403 | Insufficient permissions |
| `TokenError` | 401 | Expired/invalid JWT |
| `DuplicateEntityError` | 409 | Email already registered |
| `ValidationError` | 422 | Business rule violation |
| `PasswordPolicyError` | 422 | Weak password |
| `FileValidationError` | 400 | Bad file type/size |
| `ResumeProcessingError` | 500 | Parsing failure |
| `LLMProviderError` | 503 | All providers down |
| `EmailDeliveryError` | 500 | SMTP failure |

Exception handlers are registered in `app/core/exceptions.py` and convert domain exceptions to JSON HTTP responses automatically.

---

## LLM Provider Architecture

InterviewAce uses a **Strategy + Composite** pattern for LLM integration:

```
┌──────────────────────────────────────────────┐
│           ILLMProvider (ABC)                 │
│  generate_questions() | generate_feedback()  │
│  generate_completion() | parse_resume()      │
└────────────┬──────────────┬──────────────────┘
             │              │
    ┌────────▼──┐    ┌──────▼────────┐
    │ OpenAI    │    │ Gemini        │
    │ Provider  │    │ Provider      │
    │ (primary) │    │ (fallback)    │
    └────────┬──┘    └──────┬────────┘
             │              │
        ┌────▼──────────────▼────┐
        │ LLMProviderWithFallback │
        │  try primary → fallback │
        └────────────────────────┘
```

### Configuration
| Setting | Default | Purpose |
|---|---|---|
| `LLM_PRIMARY_PROVIDER` | `openai` | Which provider to try first (`openai` or `gemini`) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-5.2-2025-12-11` | OpenAI model identifier |
| `GEMINI_API_KEY` | — | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model identifier |
| `LLM_TIMEOUT` | `60` | Request timeout in seconds (OpenAI) |
| `LLM_MAX_RETRIES` | `2` | Max retry attempts (OpenAI) |

### Key Differences
- **OpenAI**: Uses `response_format={"type": "json_object"}` for native JSON output — no post-processing needed.
- **Gemini**: Returns text that may include markdown code fences — cleaned via `_clean_gemini_json()`.
- **Fallback**: If the primary provider raises `LLMProviderError`, the composite transparently retries with the fallback provider.

### Usage
```python
from app.infrastructure.llm.factory import get_llm_provider

provider = get_llm_provider()  # returns LLMProviderWithFallback
questions = provider.generate_questions({"system_prompt": ..., "user_prompt": ...})
```

---

## Migration Notes

### Enum Relocation
`ResumeStatus` and `FileType` enums moved from `app/schemas/resume.py` to `app/domain/value_objects/enums.py`. The schemas module now **imports** from the domain layer (single source of truth). This fixes the previous model→schema layer violation.

### Model Relocation
ORM models moved from `app/models/` to `app/infrastructure/persistence/models/`. The old `app/models/` files are now **re-export wrappers** for backward compatibility. All existing imports (`from app.models.user import User`) continue to work.

### Alembic
`alembic/env.py` updated to import models from `app.infrastructure.persistence.models`. `alembic check` confirms no schema drift.
