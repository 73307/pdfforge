"""Reject oversized requests as early as possible (by Content-Length)."""
from __future__ import annotations

from starlette.responses import JSONResponse


class MaxBodySizeMiddleware:
    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            for name, value in scope.get("headers", []):
                if name == b"content-length":
                    try:
                        declared = int(value)
                    except ValueError:
                        break
                    if declared > self.max_bytes:
                        response = JSONResponse(
                            {
                                "error": {
                                    "code": "payload_too_large",
                                    "message": "Upload exceeds the maximum allowed size.",
                                }
                            },
                            status_code=413,
                        )
                        await response(scope, receive, send)
                        return
                    break
        await self.app(scope, receive, send)
