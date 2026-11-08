"""Pure-ASGI middleware that stamps strict security headers on every response."""
from __future__ import annotations

from starlette.datastructures import MutableHeaders

from app.config import settings

# Strict policy for the JSON/file API: it should never load or render anything itself.
_STRICT_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"

# Swagger UI (/docs) pulls its assets from a CDN and fetches /openapi.json, so it needs a
# looser policy to render. These pages are development-only (disabled in production).
_DOCS_CSP = (
    "default-src 'none'; "
    "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "img-src 'self' data: https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none'; base-uri 'none'"
)

_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")

# The admin dashboard + login are self-contained HTML pages with inline CSS (no scripts,
# no external assets). Allow inline styles and same-origin form posts (the login form);
# everything else stays locked down.
_ADMIN_CSP = (
    "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
    "base-uri 'none'; frame-ancestors 'none'"
)

_BASE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


def _csp_for(path: str) -> str:
    if path.startswith("/admin"):
        return _ADMIN_CSP
    # Only relax for the docs pages, and only when they're enabled (non-production).
    if settings.app_env != "production" and path.startswith(_DOCS_PATHS):
        return _DOCS_CSP
    return _STRICT_CSP


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        csp = _csp_for(scope.get("path", ""))

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for key, value in _BASE_HEADERS.items():
                    headers[key] = value
                headers["Content-Security-Policy"] = csp
            await send(message)

        await self.app(scope, receive, send_wrapper)
