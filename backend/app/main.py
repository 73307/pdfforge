"""PDFForge FastAPI application: middleware stack, safe error handlers, routes."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.routes import router
from app.config import settings
from app.core.errors import AppError
from app.core.logging import configure_logging, get_logger
from app.security.headers import SecurityHeadersMiddleware
from app.security.limits import MaxBodySizeMiddleware
from app.storage.temp import start_sweeper

log = get_logger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.app_debug)
    start_sweeper()
    log.info("PDFForge %s starting (env=%s)", __version__, settings.app_env)
    yield


app = FastAPI(
    title="PDFForge API",
    version=__version__,
    lifespan=lifespan,
    # Hide schema docs in production to reduce surface; keep them in development.
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.app_env != "production" else None,
)

# Middleware: last added is outermost. SecurityHeaders must wrap everything.
app.add_middleware(MaxBodySizeMiddleware, max_bytes=settings.max_upload_bytes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    expose_headers=[
        "Content-Disposition",
        "X-Original-Bytes",
        "X-Compressed-Bytes",
        "X-Reduced",
    ],
    max_age=600,
)
app.add_middleware(SecurityHeadersMiddleware)


# --------------------------------------------------------------------------- errors
@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
async def handle_validation(_: Request, __: RequestValidationError) -> JSONResponse:
    # Do not echo the raw validation structure back to the client.
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "Invalid or missing fields."}},
    )


@app.exception_handler(Exception)
async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
    request_id = uuid.uuid4().hex
    log.exception("unhandled error request_id=%s type=%s", request_id, type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Something went wrong while processing your request.",
                "request_id": request_id,
            }
        },
    )


# --------------------------------------------------------------------------- routes
@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": "PDFForge", "version": __version__, "env": settings.app_env}


app.include_router(router)
