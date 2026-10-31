"""Content-based file validation. Extensions and client filenames are NOT trusted.

Each file is checked by magic bytes AND by actually parsing it with the real library
(pypdf / Pillow). Anything that is not a genuine, well-formed PDF or JPG/PNG — within
the configured page/pixel limits — is rejected with a safe message.
"""
from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.core.errors import UnsupportedMediaError, ValidationAppError

_PDF_MAGIC = b"%PDF-"
_JPEG_MAGIC = b"\xff\xd8\xff"
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sniff(head: bytes) -> str | None:
    if head.startswith(_PDF_MAGIC):
        return "pdf"
    if head.startswith(_JPEG_MAGIC):
        return "jpeg"
    if head.startswith(_PNG_MAGIC):
        return "png"
    return None


def detect_file_type(path: Path) -> str | None:
    with open(path, "rb") as fh:
        return sniff(fh.read(16))


def ensure_pdf(path: Path) -> int:
    """Validate a real, readable PDF. Returns the page count."""
    if detect_file_type(path) != "pdf":
        raise UnsupportedMediaError("Only PDF files are accepted here.")

    from pypdf import PdfReader

    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            # Accept only if it opens with an empty password; otherwise ask the user
            # to remove the password first. We never attempt to crack it.
            try:
                if reader.decrypt("") == 0:
                    raise ValidationAppError(
                        "This PDF is password-protected. Remove the password first."
                    )
            except ValidationAppError:
                raise
            except Exception:
                raise ValidationAppError(
                    "This PDF is password-protected. Remove the password first."
                )
        pages = len(reader.pages)
    except ValidationAppError:
        raise
    except Exception:
        raise ValidationAppError("The PDF appears to be corrupted or unreadable.")

    if pages < 1:
        raise ValidationAppError("The PDF has no readable pages.")
    if pages > settings.max_pdf_pages:
        raise ValidationAppError(
            f"The PDF has too many pages (limit is {settings.max_pdf_pages})."
        )
    return pages


def ensure_image(path: Path) -> tuple[int, int]:
    """Validate a real JPG/PNG within the pixel limit. Returns (width, height)."""
    kind = detect_file_type(path)
    if kind not in ("jpeg", "png"):
        raise UnsupportedMediaError("Only JPG and PNG images are accepted here.")

    from PIL import Image

    # Pillow raises DecompressionBombError past this threshold on open.
    Image.MAX_IMAGE_PIXELS = settings.max_image_pixels

    try:
        with Image.open(path) as im:
            im.verify()  # structural check (invalidates the object)
        with Image.open(path) as im:
            width, height = im.size
    except ValidationAppError:
        raise
    except Exception:
        raise ValidationAppError("The image is corrupted or unreadable.")

    if width * height > settings.max_image_pixels:
        raise ValidationAppError("The image resolution is too large.")
    return width, height


_ZIP_MAGIC = b"PK\x03\x04"
_OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def ensure_word(path: Path) -> str:
    """Validate a Word document. Returns 'docx' or 'doc'.

    .docx is a ZIP whose entries live under 'word/'. .doc is an OLE compound file.
    """
    with open(path, "rb") as fh:
        head = fh.read(8)

    if head.startswith(_ZIP_MAGIC):
        import zipfile

        try:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
        except Exception:
            raise ValidationAppError("The Word file is corrupted or unreadable.")
        if not any(n.startswith("word/") for n in names):
            raise UnsupportedMediaError("Only Word documents (.docx) are accepted here.")
        return "docx"

    if head.startswith(_OLE_MAGIC):
        return "doc"

    raise UnsupportedMediaError("Only Word documents (.doc/.docx) are accepted here.")


def ensure_spreadsheet(path: Path) -> str:
    """Validate an Excel spreadsheet. Returns 'xlsx' or 'xls'."""
    with open(path, "rb") as fh:
        head = fh.read(8)

    if head.startswith(_ZIP_MAGIC):
        import zipfile

        try:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
        except Exception:
            raise ValidationAppError("The spreadsheet is corrupted or unreadable.")
        if not any(n.startswith("xl/") for n in names):
            raise UnsupportedMediaError("Only Excel spreadsheets (.xlsx) are accepted here.")
        return "xlsx"

    if head.startswith(_OLE_MAGIC):
        return "xls"

    raise UnsupportedMediaError("Only Excel spreadsheets (.xls/.xlsx) are accepted here.")
