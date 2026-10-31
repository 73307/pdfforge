"""Compress a PDF. Honest by design: if we can't make it smaller, we keep the original.

- "light": lossless rewrite — garbage-collect unused objects, deflate streams/fonts,
  de-duplicate. Safe, keeps full quality.
- "strong": the above plus downsampling/re-encoding embedded images (lossy). Best effort;
  any image that can't be improved is left untouched.
"""
from __future__ import annotations

import io
import os
import shutil

import fitz  # PyMuPDF


def _downsample_images(doc: "fitz.Document", max_side: int = 1600, jpg_quality: int = 60) -> None:
    from PIL import Image

    seen: set[int] = set()
    for page in doc:
        try:
            images = page.get_images(full=True)
        except Exception:
            continue
        for img in images:
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                extracted = doc.extract_image(xref)
                pil = Image.open(io.BytesIO(extracted["image"])).convert("RGB")
                w, h = pil.size
                scale = min(1.0, max_side / max(w, h))
                if scale < 1.0:
                    pil = pil.resize(
                        (max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS
                    )
                buf = io.BytesIO()
                pil.save(buf, format="JPEG", quality=jpg_quality, optimize=True)
                new_bytes = buf.getvalue()
                if len(new_bytes) < len(extracted["image"]):
                    page.replace_image(xref, stream=new_bytes)
            except Exception:
                # Any unsupported image / older API -> skip it, keep going.
                continue


def compress_pdf(input_path: str, output_path: str, level: str = "light") -> dict:
    original = os.path.getsize(input_path)

    doc = fitz.open(input_path)
    try:
        if level == "strong":
            _downsample_images(doc)
        doc.save(
            output_path,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            clean=True,
        )
    finally:
        doc.close()

    compressed = os.path.getsize(output_path)
    if compressed >= original:
        shutil.copyfile(input_path, output_path)  # nothing gained; return the original
        return {"original_bytes": original, "compressed_bytes": original, "reduced": False}
    return {"original_bytes": original, "compressed_bytes": compressed, "reduced": True}
