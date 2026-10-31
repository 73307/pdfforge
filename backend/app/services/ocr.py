"""OCR a PDF (including scanned/image-only PDFs).

Two outputs:
  - "pdf":  a *searchable* PDF — same pages, with an invisible selectable text layer.
  - "text": the extracted plain text (.txt).

Uses Tesseract (via pytesseract) + PyMuPDF for rendering. The Tesseract binary must be
installed on the host (brew install tesseract). Runs in the isolated worker with a hard
timeout; if OCR isn't available we return a clear, safe message.
"""
from __future__ import annotations

import io
import shutil

import fitz  # PyMuPDF

from app.core.errors import ProcessingError


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def ocr_pdf(input_path: str, output_path: str, output: str = "pdf", lang: str = "eng", dpi: int = 200) -> dict:
    if not tesseract_available():
        raise ProcessingError("OCR is unavailable: Tesseract is not installed on the server.")

    import pytesseract
    from PIL import Image

    dpi = max(150, min(int(dpi), 300))
    doc = fitz.open(input_path)
    try:
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        if output == "text":
            chunks: list[str] = []
            for i in range(doc.page_count):
                pix = doc.load_page(i).get_pixmap(matrix=matrix, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes(output="png")))
                chunks.append(pytesseract.image_to_string(img, lang=lang))
            with open(output_path, "w", encoding="utf-8") as fh:
                fh.write("\n\n".join(chunks))
            return {"pages": doc.page_count, "output": "text"}

        # Searchable PDF: Tesseract renders each page image + an invisible text layer;
        # we stitch the per-page PDFs together.
        from pypdf import PdfReader, PdfWriter

        writer = PdfWriter()
        for i in range(doc.page_count):
            pix = doc.load_page(i).get_pixmap(matrix=matrix, alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes(output="png")))
            page_pdf = pytesseract.image_to_pdf_or_hocr(img, extension="pdf", lang=lang)
            for page in PdfReader(io.BytesIO(page_pdf)).pages:
                writer.add_page(page)
        with open(output_path, "wb") as fh:
            writer.write(fh)
        writer.close()
        return {"pages": doc.page_count, "output": "pdf"}
    finally:
        doc.close()
