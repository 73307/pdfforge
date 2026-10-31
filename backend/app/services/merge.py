"""Merge multiple PDFs in the given order into one. Runs in an isolated process."""
from __future__ import annotations

from pypdf import PdfReader, PdfWriter


def merge_pdfs(input_paths: list[str], output_path: str) -> dict:
    writer = PdfWriter()
    total = 0
    for path in input_paths:
        reader = PdfReader(path)
        if reader.is_encrypted:
            reader.decrypt("")
        for page in reader.pages:
            writer.add_page(page)
            total += 1
    with open(output_path, "wb") as fh:
        writer.write(fh)
    writer.close()
    return {"pages": total}
