"""Security behaviours: disguised files, oversized bodies, safe error bodies."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.security.limits import MaxBodySizeMiddleware


def test_disguised_non_pdf_is_rejected(client):
    r = client.post(
        "/api/merge",
        files=[("files", ("a.pdf", b"not really a pdf", "application/pdf")),
               ("files", ("b.pdf", b"still not a pdf", "application/pdf"))],
    )
    assert r.status_code == 415
    body = r.json()
    assert body["error"]["code"] == "unsupported_media_type"
    # No internals leaked.
    assert "traceback" not in r.text.lower()
    assert "/" not in body["error"]["message"]  # no server paths


def test_error_responses_still_have_security_headers(client):
    r = client.post("/api/merge", files=[("files", ("a.pdf", b"x", "application/pdf"))])
    assert r.status_code == 422
    assert r.headers.get("X-Frame-Options") == "DENY"


def test_body_size_limit_middleware():
    app = FastAPI()
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=10)

    @app.post("/x")
    async def x():  # pragma: no cover - should never run for oversize body
        return {"ok": True}

    c = TestClient(app)
    r = c.post("/x", content=b"x" * 100)
    assert r.status_code == 413
    assert r.json()["error"]["code"] == "payload_too_large"
