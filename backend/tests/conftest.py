"""Test configuration. Env must be set BEFORE importing the app (settings are cached)."""
from __future__ import annotations

import io
import os
import tempfile

# Deterministic, fast tests: run operations in-process and use an isolated data dir.
os.environ.setdefault("PROCESS_ISOLATION", "false")
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="pdfforge-test-"))
os.environ.setdefault("RATE_LIMIT_REQUESTS", "100000")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402
from pypdf import PdfWriter  # noqa: E402

from app.main import app  # noqa: E402


def make_pdf_bytes(pages: int = 1) -> bytes:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def make_png_bytes(color: str = "red", size: tuple[int, int] = (64, 64)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return buf.getvalue()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def pdf():
    return make_pdf_bytes


@pytest.fixture
def png():
    return make_png_bytes
