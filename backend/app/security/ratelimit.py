"""In-memory sliding-window rate limiter, exposed as a FastAPI dependency.

NOTE: in-memory state is per-process. For multi-replica production, back this with
Redis so limits hold across instances. Behind a proxy, trust the first hop of
X-Forwarded-For only if you control that proxy.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import Request

from app.config import settings
from app.core.errors import RateLimitError


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            dq = self._hits[key]
            cutoff = now - self.window
            while dq and dq[0] <= cutoff:
                dq.popleft()
            if len(dq) >= self.limit:
                return False
            dq.append(now)
            return True


_limiter = SlidingWindowRateLimiter(
    settings.rate_limit_requests, settings.rate_limit_window_seconds
)


def _client_key(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit(request: Request) -> None:
    if not _limiter.allow(_client_key(request)):
        raise RateLimitError("Too many requests. Please slow down and try again shortly.")
