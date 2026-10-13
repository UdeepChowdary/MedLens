"""MedLens FastAPI Application Entry Point."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import MedLensException, ErrorResponse
from app.core.logging import logger
from app.api.v1.api import api_router


def create_application() -> FastAPI:
    """Factory creating and configuring the primary FastAPI instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "MedLens verification-first medicine composition analysis engine. "
            "Deterministic extraction, normalization, and comparison."
        ),
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 1. CORS Configuration
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 2. Custom Exception Handlers
    @app.exception_handler(MedLensException)
    async def medlens_exception_handler(request: Request, exc: MedLensException) -> JSONResponse:
        logger.warning(f"Domain error [{exc.error_code}]: {exc.message}")
        error_payload = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Request validation error on {request.url.path}: {exc.errors()}")
        error_payload = ErrorResponse(
            error_code="ERR_REQUEST_VALIDATION_FAILED",
            message="Request body or query parameters failed schema validation.",
            details={"errors": exc.errors()},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_payload.model_dump(),
        )

    # 3. Mount API v1 router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
