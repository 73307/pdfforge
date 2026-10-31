"""Temp storage with random names, traversal-proof cleanup, and a retention sweeper.

Design: each request gets its own random working directory under DATA_DIR/work/.
Uploads are saved there under server-generated random names (the client's filename
is never used for a path). The processed result is streamed back directly and the
whole working directory is deleted immediately after the response. A background
sweeper removes any directory older than the retention window (covers crashes).
"""
from __future__ import annotations

import shutil
import threading
import time
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.core.errors import PayloadTooLargeError
from app.core.logging import get_logger

log = get_logger("storage")
_CHUNK = 1024 * 1024  # 1 MB


class Storage:
    def __init__(self, base: str, retention_seconds: int):
        self.base = Path(base).resolve()
        self.work_root = self.base / "work"
        self.retention = retention_seconds
        self.work_root.mkdir(parents=True, exist_ok=True)

    def new_workdir(self) -> Path:
        d = self.work_root / uuid.uuid4().hex
        d.mkdir(parents=False, exist_ok=False)
        return d

    def random_name(self, suffix: str = "") -> str:
        if suffix and not suffix.startswith("."):
            suffix = "." + suffix
        return uuid.uuid4().hex + suffix

    async def save_upload(self, upload: UploadFile, dest: Path, max_bytes: int) -> int:
        """Stream an upload to disk, enforcing a hard byte cap as we go."""
        size = 0
        with open(dest, "wb") as fh:
            while True:
                chunk = await upload.read(_CHUNK)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    fh.close()
                    dest.unlink(missing_ok=True)
                    raise PayloadTooLargeError("A file exceeds the maximum allowed size.")
                fh.write(chunk)
        return size

    def is_inside(self, path: Path) -> bool:
        """True only if `path` resolves to somewhere inside the work root."""
        try:
            rp = Path(path).resolve()
        except OSError:
            return False
        return rp == self.work_root or self.work_root in rp.parents

    def cleanup(self, workdir: Path) -> None:
        if self.is_inside(workdir):
            shutil.rmtree(workdir, ignore_errors=True)

    def sweep(self) -> int:
        now = time.time()
        removed = 0
        if not self.work_root.exists():
            return 0
        for child in list(self.work_root.iterdir()):
            try:
                if now - child.stat().st_mtime > self.retention:
                    shutil.rmtree(child, ignore_errors=True)
                    removed += 1
            except FileNotFoundError:
                pass
        return removed


storage = Storage(settings.data_dir, settings.retention_seconds)


def start_sweeper(interval: int | None = None) -> threading.Thread:
    interval = interval or max(60, settings.retention_seconds // 2)

    def loop() -> None:
        while True:
            time.sleep(interval)
            try:
                n = storage.sweep()
                if n:
                    log.info("sweeper removed %d expired working dir(s)", n)
            except Exception:  # noqa: BLE001
                log.warning("sweeper pass failed")

    t = threading.Thread(target=loop, daemon=True, name="temp-sweeper")
    t.start()
    return t
