"""User-safe error types.

Every error that reaches the client is one of these: it carries a *generic*,
non-sensitive message and an HTTP status. Internal details (tracebacks, library
messages, file paths) are logged server-side only — never returned.
"""
from __future__ import annotations


class AppError(Exception):
    status_code: int = 400
    code: str = "bad_request"

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class ValidationAppError(AppError):
    status_code = 422
    code = "validation_error"


class UnsupportedMediaError(AppError):
    status_code = 415
    code = "unsupported_media_type"


class PayloadTooLargeError(AppError):
    status_code = 413
    code = "payload_too_large"


class RateLimitError(AppError):
    status_code = 429
    code = "rate_limited"


class TimeoutAppError(AppError):
    status_code = 504
    code = "processing_timeout"


class ProcessingError(AppError):
    status_code = 422
    code = "processing_failed"


class NotFoundAppError(AppError):
    status_code = 404
    code = "not_found"
