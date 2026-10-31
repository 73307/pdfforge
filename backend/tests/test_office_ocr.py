"""Excel->PDF and OCR tests.

Both depend on external binaries (LibreOffice / Tesseract) that may not be installed.
Tests accept either a real result (200) or the safe "unavailable" error (422), and always
check that validation and error-shaping are correct.
"""
import io
import zipfile

import fitz  # PyMuPDF


def make_fake_xlsx() -> bytes:
    """A minimal ZIP that looks like an .xlsx (has an xl/ entry) for validation."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<?xml version='1.0'?><Types/>")
        zf.writestr("xl/workbook.xml", "<workbook/>")
    return buf.getvalue()


def make_text_pdf_bytes(text: str = "Scanned-looking text for OCR") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=16)
    data = doc.tobytes()
    doc.close()
    return data


def test_excel_to_pdf_graceful(client):
    r = client.post(
        "/api/excel-to-pdf",
        files={
            "file": (
                "s.xlsx",
                make_fake_xlsx(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        assert r.content[:5] == b"%PDF-"
    else:
        assert r.json()["error"]["code"] == "processing_failed"


def test_excel_rejects_non_spreadsheet(client):
    r = client.post(
        "/api/excel-to-pdf",
        files={"file": ("s.xlsx", b"not a spreadsheet at all", "application/octet-stream")},
    )
    assert r.status_code == 415


def test_ocr_graceful(client):
    r = client.post(
        "/api/ocr-pdf",
        files={"file": ("in.pdf", make_text_pdf_bytes(), "application/pdf")},
        data={"output": "text", "lang": "eng"},
    )
    assert r.status_code in (200, 422)
    if r.status_code == 422:
        assert r.json()["error"]["code"] == "processing_failed"


def test_ocr_rejects_bad_output(client):
    r = client.post(
        "/api/ocr-pdf",
        files={"file": ("in.pdf", make_text_pdf_bytes(), "application/pdf")},
        data={"output": "xml"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_ocr_rejects_bad_lang(client):
    r = client.post(
        "/api/ocr-pdf",
        files={"file": ("in.pdf", make_text_pdf_bytes(), "application/pdf")},
        data={"output": "text", "lang": "en!;rm -rf"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
