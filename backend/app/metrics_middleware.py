"""ASGI middleware that records one aggregate metric per API call.

It captures the tool name (from the path), the response status, how long it took, and the
request/response byte sizes. For FAILED requests it also keeps the backend's own error
code + generic message (e.g. "LibreOffice is not installed") so the admin can see WHY a
tool failed — nothing about the file itself or the caller.
"""
from __future__ import annotations

import json
import time

from app import metrics
from app.config import settings

_PREFIX = "/api/"


class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if scope["type"] != "http" or not settings.metrics_enabled or not path.startswith(_PREFIX):
            await self.app(scope, receive, send)
            return

        tool = path[len(_PREFIX):].strip("/") or "unknown"

        req_bytes = 0
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    req_bytes = int(value)
                except ValueError:
                    req_bytes = 0
                break

        start = time.perf_counter()
        state = {"status": 500, "resp_bytes": 0, "err": b""}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                state["status"] = message["status"]
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    state["resp_bytes"] += len(body)
                    # Only error responses have a small JSON body worth keeping; success
                    # bodies are the (binary) result file and are never buffered.
                    if state["status"] >= 400 and len(state["err"]) < 2048:
                        state["err"] += body[:2048]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            err_code, err_msg = "", ""
            if state["status"] >= 400 and state["err"]:
                try:
                    err = json.loads(state["err"].decode("utf-8", "replace")).get("error", {})
                    err_code = str(err.get("code", ""))[:40]
                    err_msg = str(err.get("message", ""))[:200]
                except Exception:
                    pass
            metrics.record(tool, state["status"], duration_ms, req_bytes, state["resp_bytes"], err_code, err_msg)
