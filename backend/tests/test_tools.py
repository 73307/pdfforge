"""End-to-end tests for each tool endpoint (in-process processing)."""
import io
import zipfile

from pypdf import PdfReader


def _pdf_file(data, name="in.pdf"):
    return (name, data, "application/pdf")


def test_merge_two_pdfs(client, pdf):
    r = client.post(
        "/api/merge",
        files=[("files", _pdf_file(pdf(2))), ("files", _pdf_file(pdf(3)))],
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"
    assert len(PdfReader(io.BytesIO(r.content)).pages) == 5


def test_merge_needs_two_files(client, pdf):
    r = client.post("/api/merge", files=[("files", _pdf_file(pdf(1)))])
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_split_single_range_returns_pdf(client, pdf):
    r = client.post("/api/split", files={"file": _pdf_file(pdf(5))}, data={"ranges": "2-4"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(PdfReader(io.BytesIO(r.content)).pages) == 3


def test_split_multi_range_returns_zip(client, pdf):
    r = client.post("/api/split", files={"file": _pdf_file(pdf(5))}, data={"ranges": "1,3-4"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        assert len(zf.namelist()) == 2


def test_split_rejects_out_of_range(client, pdf):
    r = client.post("/api/split", files={"file": _pdf_file(pdf(2))}, data={"ranges": "1-9"})
    assert r.status_code == 422


def test_rotate(client, pdf):
    r = client.post(
        "/api/rotate", files={"file": _pdf_file(pdf(2))}, data={"angle": "90", "pages": ""}
    )
    assert r.status_code == 200
    assert r.content[:5] == b"%PDF-"


def test_rotate_bad_angle(client, pdf):
    r = client.post("/api/rotate", files={"file": _pdf_file(pdf(1))}, data={"angle": "45"})
    assert r.status_code == 422


def test_images_to_pdf(client, png):
    r = client.post(
        "/api/images-to-pdf",
        files=[("files", ("a.png", png("red"), "image/png")),
               ("files", ("b.png", png("blue"), "image/png"))],
        data={"page_size": "a4", "orientation": "auto"},
    )
    assert r.status_code == 200
    assert r.content[:5] == b"%PDF-"
    assert len(PdfReader(io.BytesIO(r.content)).pages) == 2


def test_pdf_to_images(client, pdf):
    r = client.post(
        "/api/pdf-to-images", files={"file": _pdf_file(pdf(2))}, data={"format": "png", "dpi": "100"}
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        assert len(zf.namelist()) == 2


def test_compress_returns_pdf(client, pdf):
    r = client.post("/api/compress", files={"file": _pdf_file(pdf(3))}, data={"level": "light"})
    assert r.status_code == 200
    assert r.content[:5] == b"%PDF-"
    assert "X-Reduced" in r.headers


def test_protect_encrypts(client, pdf):
    r = client.post(
        "/api/protect", files={"file": _pdf_file(pdf(1))}, data={"password": "secret123"}
    )
    assert r.status_code == 200
    reader = PdfReader(io.BytesIO(r.content))
    assert reader.is_encrypted


def test_protect_rejects_short_password(client, pdf):
    r = client.post("/api/protect", files={"file": _pdf_file(pdf(1))}, data={"password": "ab"})
    assert r.status_code == 422
