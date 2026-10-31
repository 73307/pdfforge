import pytest

from app.core.errors import UnsupportedMediaError, ValidationAppError
from app.validators.files import ensure_image, ensure_pdf
from tests.conftest import make_pdf_bytes, make_png_bytes


def test_ensure_pdf_accepts_valid(tmp_path):
    p = tmp_path / "a.bin"
    p.write_bytes(make_pdf_bytes(3))
    assert ensure_pdf(p) == 3


def test_ensure_pdf_rejects_non_pdf(tmp_path):
    p = tmp_path / "fake.bin"
    p.write_bytes(b"this is clearly not a pdf")
    with pytest.raises(UnsupportedMediaError):
        ensure_pdf(p)


def test_ensure_pdf_rejects_corrupt_pdf(tmp_path):
    p = tmp_path / "corrupt.bin"
    p.write_bytes(b"%PDF-1.7\nbut the rest is garbage and not a real pdf")
    with pytest.raises(ValidationAppError):
        ensure_pdf(p)


def test_ensure_image_accepts_png(tmp_path):
    p = tmp_path / "img.bin"
    p.write_bytes(make_png_bytes())
    w, h = ensure_image(p)
    assert (w, h) == (64, 64)


def test_ensure_image_rejects_non_image(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"nope")
    with pytest.raises(UnsupportedMediaError):
        ensure_image(p)
