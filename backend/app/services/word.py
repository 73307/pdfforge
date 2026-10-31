"""PDF <-> Word conversions.

- PDF -> Word (.docx): uses `pdf2docx`, which produces genuinely editable Word output
  for text-based PDFs. No external tools required. Runs in the isolated worker.
- Word/Office -> PDF: shells out to LibreOffice (`soffice`) in headless mode. LibreOffice
  must be installed on the host/container. Each run gets its own isolated profile dir,
  a minimal environment, no shell, and a hard subprocess timeout.

Fidelity note: conversions are best-effort. Complex layouts, fonts, tables, and scanned
(image-only) PDFs may not round-trip perfectly. This is surfaced to users in the UI.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from app.config import settings
from app.core.errors import ProcessingError, TimeoutAppError


# --------------------------------------------------------------------------- PDF -> Word
def pdf_to_word(input_path: str, output_path: str) -> dict:
    from pdf2docx import Converter

    converter = Converter(input_path)
    try:
        converter.convert(output_path)  # converts the whole document
    finally:
        converter.close()
    if not Path(output_path).exists() or Path(output_path).stat().st_size == 0:
        raise ProcessingError("The PDF could not be converted to Word.")
    return {"converted": True}


# --------------------------------------------------------------------------- Word -> PDF
_SOFFICE_CANDIDATES = [
    "soffice",
    "libreoffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
]


def find_soffice() -> str | None:
    for candidate in _SOFFICE_CANDIDATES:
        if candidate.startswith("/"):
            if Path(candidate).exists():
                return candidate
        else:
            found = shutil.which(candidate)
            if found:
                return found
    return None


def office_to_pdf(input_path: str, output_path: str, workdir: str) -> dict:
    soffice = find_soffice()
    if not soffice:
        raise ProcessingError(
            "This conversion is unavailable: LibreOffice is not installed on the server."
        )

    wd = Path(workdir)
    profile = wd / "lo_profile"  # isolated per-request profile => safe parallel runs

    cmd = [
        soffice,
        f"-env:UserInstallation=file://{profile}",
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--nodefault",
        "--nofirststartwizard",
        "--convert-to",
        "pdf",
        "--outdir",
        str(wd),
        str(input_path),
    ]

    # Minimal environment: writable HOME in the sandbox, keep PATH for library lookup.
    env = {"HOME": str(wd), "PATH": os.environ.get("PATH", "/usr/bin:/bin")}

    try:
        subprocess.run(
            cmd,
            timeout=settings.office_timeout_seconds,
            capture_output=True,
            check=True,
            env=env,
        )
    except subprocess.TimeoutExpired:
        raise TimeoutAppError("Conversion took too long and was stopped.")
    except subprocess.CalledProcessError:
        raise ProcessingError("The document could not be converted.")
    except FileNotFoundError:
        raise ProcessingError(
            "This conversion is unavailable: LibreOffice is not installed on the server."
        )

    produced = wd / (Path(input_path).stem + ".pdf")
    if not produced.exists():
        raise ProcessingError("The document could not be converted.")
    if produced.resolve() != Path(output_path).resolve():
        shutil.move(str(produced), str(output_path))
    return {"converted": True}
