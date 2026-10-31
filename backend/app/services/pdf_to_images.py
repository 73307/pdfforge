"""Render PDF pages to images (PNG/JPEG) and package them as a ZIP.

DPI is clamped to a safe range to avoid rendering gigapixel images from a crafted PDF.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import fitz  # PyMuPDF


def pdf_to_images(input_path: str, output_path: str, fmt: str = "png", dpi: int = 150) -> dict:
    dpi = max(72, min(int(dpi), 200))
    fmt = "jpeg" if str(fmt).lower() in ("jpg", "jpeg") else "png"
    ext = "jpg" if fmt == "jpeg" else "png"

    doc = fitz.open(input_path)
    try:
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        workdir = Path(output_path).parent
        count = 0
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i in range(doc.page_count):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                if fmt == "jpeg":
                    data = pix.tobytes(output="jpeg", jpg_quality=85)
                else:
                    data = pix.tobytes(output="png")
                img_path = workdir / f"page_{i + 1:04d}.{ext}"
                img_path.write_bytes(data)
                zf.write(img_path, arcname=img_path.name)
                img_path.unlink(missing_ok=True)
                count += 1
        return {"pages": count, "format": ext}
    finally:
        doc.close()
