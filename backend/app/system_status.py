"""Live system-health snapshot for the admin console (all real, no fake data)."""
from __future__ import annotations

import os
import shutil
import time

from app.config import settings
from app.services.background import rembg_available
from app.services.ocr import tesseract_available

_START = time.time()

_SOFFICE_PATHS = (
    "soffice",
    "libreoffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
)


def _soffice_available() -> bool:
    for c in _SOFFICE_PATHS:
        if os.path.isabs(c):
            if os.path.exists(c):
                return True
        elif shutil.which(c):
            return True
    return False


def _dir_size(path: str) -> int:
    total = 0
    try:
        for root, _dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    except OSError:
        pass
    return total


def status() -> dict:
    data_dir = settings.data_dir
    used = _dir_size(data_dir)
    try:
        total = shutil.disk_usage(data_dir if os.path.exists(data_dir) else ".").total
    except OSError:
        total = 0
    return {
        "api": "operational",
        "uptime_s": int(time.time() - _START),
        "converters": {
            "LibreOffice": _soffice_available(),
            "Tesseract OCR": tesseract_available(),
            "Background remover": rembg_available(),
        },
        "storage": {"used": used, "total": total},
    }
