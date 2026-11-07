"""Remove the background from an image.

Uses rembg (a U^2-Net ONNX segmentation model) to compute the foreground mask and
returns a PNG — transparent by default, or composited onto a solid colour. The model
file is downloaded once and then cached on disk (~/.u2net), so later runs are fast.
Runs inside the isolated worker with a hard timeout.
"""
from __future__ import annotations

from app.core.errors import ProcessingError

# Default model: good general-purpose quality. Cached after first download.
_MODEL = "u2net"


def rembg_available() -> bool:
    try:
        import rembg  # noqa: F401

        return True
    except Exception:
        return False


def remove_background(input_path: str, output_path: str, background: str = "transparent") -> dict:
    try:
        from rembg import new_session, remove
    except Exception as exc:  # pragma: no cover - import guard
        raise ProcessingError(
            "Background removal is unavailable: the model library isn't installed."
        ) from exc

    from PIL import Image

    with Image.open(input_path) as im:
        source = im.convert("RGBA")

    session = new_session(_MODEL)
    cutout = remove(source, session=session)  # RGBA image with the background made transparent

    if background in ("white", "black"):
        fill = (255, 255, 255, 255) if background == "white" else (0, 0, 0, 255)
        canvas = Image.new("RGBA", cutout.size, fill)
        canvas.paste(cutout, (0, 0), cutout)
        cutout = canvas.convert("RGB")

    cutout.save(output_path, format="PNG")
    return {"background": background}
