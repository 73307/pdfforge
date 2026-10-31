"""HTTP API for the PDF tools.

Every endpoint follows the same hardened flow:
  rate limit -> size-capped streaming save -> content validation ->
  isolated + timed processing -> direct stream of the result -> guaranteed cleanup.
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.core.errors import ProcessingError, ValidationAppError
from app.core.pages import parse_pages, parse_ranges
from app.core.runner import run_isolated
from app.security.ratelimit import rate_limit
from app.services.compress import compress_pdf
from app.services.images_to_pdf import images_to_pdf
from app.services.merge import merge_pdfs
from app.services.pdf_to_images import pdf_to_images
from app.services.protect import protect_pdf
from app.services.ocr import ocr_pdf, tesseract_available
from app.services.rotate import rotate_pdf
from app.services.split import split_pdf
from app.services.word import office_to_pdf, pdf_to_word
from app.storage.temp import storage
from app.validators.files import ensure_image, ensure_pdf, ensure_spreadsheet, ensure_word

router = APIRouter(prefix="/api", dependencies=[Depends(rate_limit)])

PDF = "application/pdf"
ZIP = "application/zip"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


# --------------------------------------------------------------------------- helpers
def _stream(path: Path, media_type: str, filename: str, workdir: Path) -> FileResponse:
    """Stream a result file, then delete the whole working dir in the background."""
    return FileResponse(
        path=str(path),
        media_type=media_type,
        filename=filename,
        background=BackgroundTask(storage.cleanup, workdir),
    )


async def _save_pdfs(files: list[UploadFile], workdir: Path, minimum: int) -> list[str]:
    if len(files) < minimum:
        raise ValidationAppError(
            f"Please upload at least {minimum} PDF file{'s' if minimum > 1 else ''}."
        )
    if len(files) > settings.max_files_per_request:
        raise ValidationAppError(f"Too many files (limit is {settings.max_files_per_request}).")
    paths: list[str] = []
    for upload in files:
        dest = workdir / storage.random_name(".upload")
        await storage.save_upload(upload, dest, settings.max_file_bytes)
        ensure_pdf(dest)
        paths.append(str(dest))
    return paths


async def _save_images(files: list[UploadFile], workdir: Path) -> list[str]:
    if not files:
        raise ValidationAppError("Please upload at least one image.")
    if len(files) > settings.max_files_per_request:
        raise ValidationAppError(f"Too many files (limit is {settings.max_files_per_request}).")
    paths: list[str] = []
    for upload in files:
        dest = workdir / storage.random_name(".upload")
        await storage.save_upload(upload, dest, settings.max_file_bytes)
        ensure_image(dest)
        paths.append(str(dest))
    return paths


# --------------------------------------------------------------------------- endpoints
@router.post("/merge")
async def merge(files: list[UploadFile] = File(...)):
    workdir = storage.new_workdir()
    try:
        paths = await _save_pdfs(files, workdir, minimum=2)
        out = workdir / "merged.pdf"
        run_isolated(merge_pdfs, paths, str(out), timeout=settings.op_timeout_seconds)
        return _stream(out, PDF, "merged.pdf", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/split")
async def split(file: UploadFile = File(...), ranges: str = Form(...)):
    workdir = storage.new_workdir()
    try:
        [path] = await _save_pdfs([file], workdir, minimum=1)
        pages = ensure_pdf(Path(path))
        parsed = parse_ranges(ranges, pages)
        zipped = len(parsed) > 1
        out = workdir / ("split.zip" if zipped else "split.pdf")
        run_isolated(split_pdf, path, str(out), parsed, timeout=settings.op_timeout_seconds)
        return _stream(out, ZIP if zipped else PDF, out.name, workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/rotate")
async def rotate(
    file: UploadFile = File(...),
    angle: int = Form(...),
    pages: str = Form(""),
):
    if angle % 360 not in (90, 180, 270):
        raise ValidationAppError("Angle must be 90, 180, or 270 degrees.")
    workdir = storage.new_workdir()
    try:
        [path] = await _save_pdfs([file], workdir, minimum=1)
        total = ensure_pdf(Path(path))
        page_list = parse_pages(pages, total) if pages.strip() else None
        out = workdir / "rotated.pdf"
        run_isolated(
            rotate_pdf, path, str(out), angle % 360, page_list,
            timeout=settings.op_timeout_seconds,
        )
        return _stream(out, PDF, "rotated.pdf", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/images-to-pdf")
async def images_to_pdf_endpoint(
    files: list[UploadFile] = File(...),
    page_size: str = Form("fit"),
    orientation: str = Form("auto"),
):
    if page_size not in ("fit", "a4"):
        raise ValidationAppError("page_size must be 'fit' or 'a4'.")
    if orientation not in ("auto", "portrait", "landscape"):
        raise ValidationAppError("orientation must be 'auto', 'portrait', or 'landscape'.")
    workdir = storage.new_workdir()
    try:
        paths = await _save_images(files, workdir)
        out = workdir / "images.pdf"
        run_isolated(
            images_to_pdf, paths, str(out), page_size, orientation,
            timeout=settings.op_timeout_seconds,
        )
        return _stream(out, PDF, "images.pdf", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/pdf-to-images")
async def pdf_to_images_endpoint(
    file: UploadFile = File(...),
    format: str = Form("png"),
    dpi: int = Form(150),
):
    if format.lower() not in ("png", "jpg", "jpeg"):
        raise ValidationAppError("format must be 'png' or 'jpeg'.")
    workdir = storage.new_workdir()
    try:
        [path] = await _save_pdfs([file], workdir, minimum=1)
        ensure_pdf(Path(path))
        out = workdir / "pages.zip"
        run_isolated(
            pdf_to_images, path, str(out), format.lower(), dpi,
            timeout=settings.op_timeout_seconds,
        )
        return _stream(out, ZIP, "pages.zip", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/compress")
async def compress(file: UploadFile = File(...), level: str = Form("light")):
    if level not in ("light", "strong"):
        raise ValidationAppError("level must be 'light' or 'strong'.")
    workdir = storage.new_workdir()
    try:
        [path] = await _save_pdfs([file], workdir, minimum=1)
        ensure_pdf(Path(path))
        out = workdir / "compressed.pdf"
        result = run_isolated(
            compress_pdf, path, str(out), level, timeout=settings.op_timeout_seconds
        )
        headers = {
            "X-Original-Bytes": str(result.get("original_bytes", "")),
            "X-Compressed-Bytes": str(result.get("compressed_bytes", "")),
            "X-Reduced": "1" if result.get("reduced") else "0",
        }
        response = _stream(out, PDF, "compressed.pdf", workdir)
        response.headers.update(headers)
        return response
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/protect")
async def protect(file: UploadFile = File(...), password: str = Form(...)):
    if not (4 <= len(password) <= 128):
        raise ValidationAppError("Password must be between 4 and 128 characters.")
    workdir = storage.new_workdir()
    try:
        [path] = await _save_pdfs([file], workdir, minimum=1)
        ensure_pdf(Path(path))
        out = workdir / "protected.pdf"
        run_isolated(protect_pdf, path, str(out), password, timeout=settings.op_timeout_seconds)
        return _stream(out, PDF, "protected.pdf", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/pdf-to-word")
async def pdf_to_word_endpoint(file: UploadFile = File(...)):
    workdir = storage.new_workdir()
    try:
        [path] = await _save_pdfs([file], workdir, minimum=1)
        ensure_pdf(Path(path))
        out = workdir / "converted.docx"
        run_isolated(pdf_to_word, path, str(out), timeout=settings.office_timeout_seconds)
        return _stream(out, DOCX, "converted.docx", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/word-to-pdf")
async def word_to_pdf_endpoint(file: UploadFile = File(...)):
    workdir = storage.new_workdir()
    try:
        dest = workdir / storage.random_name(".upload")
        await storage.save_upload(file, dest, settings.max_file_bytes)
        ensure_word(dest)
        out = workdir / "converted.pdf"
        # LibreOffice is a blocking subprocess; run it off the event loop.
        await run_in_threadpool(office_to_pdf, str(dest), str(out), str(workdir))
        return _stream(out, PDF, "converted.pdf", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/excel-to-pdf")
async def excel_to_pdf_endpoint(file: UploadFile = File(...)):
    workdir = storage.new_workdir()
    try:
        dest = workdir / storage.random_name(".upload")
        await storage.save_upload(file, dest, settings.max_file_bytes)
        ensure_spreadsheet(dest)
        out = workdir / "converted.pdf"
        await run_in_threadpool(office_to_pdf, str(dest), str(out), str(workdir))
        return _stream(out, PDF, "converted.pdf", workdir)
    except Exception:
        storage.cleanup(workdir)
        raise


@router.post("/ocr-pdf")
async def ocr_endpoint(
    file: UploadFile = File(...),
    output: str = Form("pdf"),
    lang: str = Form("eng"),
):
    if output not in ("pdf", "text"):
        raise ValidationAppError("output must be 'pdf' or 'text'.")
    if not re.fullmatch(r"[a-z]{3}(\+[a-z]{3})*", lang):
        raise ValidationAppError("Invalid language code (use e.g. 'eng' or 'eng+hin').")
    # Pre-check here so the clear message reaches the user (the isolated worker
    # intentionally hides its internal error text).
    if not tesseract_available():
        raise ProcessingError("OCR is unavailable: Tesseract is not installed on the server.")
    workdir = storage.new_workdir()
    try:
        [path] = await _save_pdfs([file], workdir, minimum=1)
        ensure_pdf(Path(path))
        if output == "text":
            out = workdir / "ocr.txt"
            media, name = "text/plain; charset=utf-8", "ocr.txt"
        else:
            out = workdir / "ocr.pdf"
            media, name = PDF, "searchable.pdf"
        run_isolated(ocr_pdf, path, str(out), output, lang, timeout=settings.office_timeout_seconds)
        return _stream(out, media, name, workdir)
    except Exception:
        storage.cleanup(workdir)
        raise
