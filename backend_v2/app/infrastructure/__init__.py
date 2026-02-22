"""
Infrastructure Layer — InterviewAce Clean Architecture.

This layer contains concrete implementations of domain interfaces:
- persistence/   SQLAlchemy ORM models + repository implementations
- llm/           LLM provider adapters (OpenAI, Gemini)
- storage/       File storage adapters (local, S3)
- email/         Email delivery adapters (SMTP)
"""
