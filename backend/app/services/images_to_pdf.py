"""Convert JPG/PNG images into a single PDF (one image per page)."""
from __future__ import annotations

from PIL import Image

_A4_72DPI = (595, 842)  # points == pixels at 72 dpi


def images_to_pdf(
    input_paths: list[str],
    output_path: str,
    page_size: str = "fit",
    orientation: str = "auto",
) -> dict:
    pages: list[Image.Image] = []
    for path in input_paths:
        with Image.open(path) as raw:
            img = raw.convert("RGB")

        if page_size == "a4":
            pw, ph = _A4_72DPI
            landscape = orientation == "landscape" or (
                orientation == "auto" and img.width > img.height
            )
            if landscape:
                pw, ph = ph, pw
            canvas = Image.new("RGB", (pw, ph), "white")
            scale = min(pw / img.width, ph / img.height)
            nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
            resized = img.resize((nw, nh), Image.LANCZOS)
            canvas.paste(resized, ((pw - nw) // 2, (ph - nh) // 2))
            pages.append(canvas)
        else:  # "fit": the page equals the image
            pages.append(img)

    first, rest = pages[0], pages[1:]
    first.save(output_path, "PDF", save_all=True, append_images=rest)
    return {"pages": len(pages)}
