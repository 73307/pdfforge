"""PDF <-> Word conversion tests.

PDF -> Word always works (pure Python). Word -> PDF needs LibreOffice, so that test
accepts either a real conversion (200) or the safe "unavailable" error (422).
"""
import io

import fitz  # PyMuPDF
from docx import Document


def make_text_pdf_bytes(text: str = "Hello PDFForge editable text", pages: int = 1) -> bytes:
    doc = fitz.open()
    for _ in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=14)
    data = doc.tobytes()
    doc.close()
    return data


def make_docx_bytes(text: str = "Hello from Word") -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_pdf_to_word_produces_editable_docx(client):
    r = client.post(
        "/api/pdf-to-word",
        files={"file": ("in.pdf", make_text_pdf_bytes(), "application/pdf")},
    )
    assert r.status_code == 200
    assert r.content[:4] == b"PK\x03\x04"  # .docx is a zip container
    doc = Document(io.BytesIO(r.content))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "PDFForge" in text


def test_word_to_pdf_graceful_without_libreoffice(client):
    r = client.post(
        "/api/word-to-pdf",
        files={
            "file": (
                "in.docx",
                make_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        assert r.content[:5] == b"%PDF-"
    else:
        assert r.json()["error"]["code"] == "processing_failed"


def test_word_to_pdf_rejects_non_word(client):
    r = client.post(
        "/api/word-to-pdf",
        files={"file": ("x.docx", b"definitely not a word file", "application/octet-stream")},
    )
    assert r.status_code == 415
