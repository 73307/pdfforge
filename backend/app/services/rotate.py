"""Rotate all pages or a selected set of pages by a multiple of 90 degrees."""
from __future__ import annotations

from pypdf import PdfReader, PdfWriter


def rotate_pdf(input_path: str, output_path: str, angle: int, pages: list[int] | None) -> dict:
    reader = PdfReader(input_path)
    if reader.is_encrypted:
        reader.decrypt("")

    writer = PdfWriter()
    target = set(pages) if pages else None
    rotated = 0
    for index, page in enumerate(reader.pages, 1):
        if target is None or index in target:
            page.rotate(angle)  # clockwise, angle must be a multiple of 90
            rotated += 1
        writer.add_page(page)

    with open(output_path, "wb") as fh:
        writer.write(fh)
    writer.close()
    return {"rotated": rotated}
