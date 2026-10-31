"""Split / extract pages. One range -> a single PDF; many ranges -> a ZIP of PDFs."""
from __future__ import annotations

import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def _write_range(reader: PdfReader, start: int, end: int, out_path: Path) -> None:
    writer = PdfWriter()
    for i in range(start - 1, end):  # ranges are 1-based inclusive
        writer.add_page(reader.pages[i])
    with open(out_path, "wb") as fh:
        writer.write(fh)
    writer.close()


def split_pdf(input_path: str, output_path: str, ranges: list[tuple[int, int]]) -> dict:
    reader = PdfReader(input_path)
    if reader.is_encrypted:
        reader.decrypt("")

    out = Path(output_path)
    if len(ranges) == 1:
        start, end = ranges[0]
        _write_range(reader, start, end, out)
        return {"files": 1, "zipped": False}

    workdir = out.parent
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, (start, end) in enumerate(ranges, 1):
            part = workdir / f"part_{idx:03d}_pages_{start}-{end}.pdf"
            _write_range(reader, start, end, part)
            zf.write(part, arcname=part.name)
            part.unlink(missing_ok=True)
    return {"files": len(ranges), "zipped": True}
