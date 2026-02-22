"""
Centralized exception-to-HTTP mapping.

Registers FastAPI exception handlers that convert domain exceptions
into proper JSON error responses, keeping the domain layer free of
framework imports.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainException,
    DuplicateEntityError,
    EntityNotFoundError,
    FileValidationError,
    LLMProviderError,
    PasswordPolicyError,
    ResumeProcessingError,
    TokenError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register domain-exception handlers on the FastAPI app."""

    @app.exception_handler(EntityNotFoundError)
    async def _not_found(request: Request, exc: EntityNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(AuthenticationError)
    async def _authn(request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(AuthorizationError)
    async def _authz(request: Request, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(TokenError)
    async def _token(request: Request, exc: TokenError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(DuplicateEntityError)
    async def _duplicate(request: Request, exc: DuplicateEntityError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(ValidationError)
    async def _validation(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(PasswordPolicyError)
    async def _password(request: Request, exc: PasswordPolicyError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(FileValidationError)
    async def _file(request: Request, exc: FileValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(ResumeProcessingError)
    async def _resume(request: Request, exc: ResumeProcessingError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(LLMProviderError)
    async def _llm(request: Request, exc: LLMProviderError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": exc.message, "code": exc.code})

    # Catch-all for any other domain exception not explicitly handled
    @app.exception_handler(DomainException)
    async def _domain_generic(request: Request, exc: DomainException) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": exc.message, "code": exc.code})
