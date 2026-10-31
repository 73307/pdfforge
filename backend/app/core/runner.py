"""Run a CPU-bound PDF operation under a hard timeout in an isolated process.

Why a separate process: pypdf / PyMuPDF do heavy work inside C extensions that an
in-process signal/thread timeout cannot reliably interrupt. A child process can be
force-killed if it runs too long, protecting the web tier from hangs and runaway
memory. Output files are written to disk by the child; only a small, picklable
result dict crosses back through the queue.
"""
from __future__ import annotations

import multiprocessing as mp
from typing import Any, Callable

from app.config import settings
from app.core.errors import ProcessingError, TimeoutAppError
from app.core.logging import get_logger

log = get_logger("runner")

# "spawn" is the default and only safe start method on macOS; be explicit so behaviour
# is identical on Linux containers too.
_CTX = mp.get_context("spawn")


def _worker(func: Callable[..., Any], args: tuple, kwargs: dict, q) -> None:
    try:
        result = func(*args, **kwargs)
        q.put(("ok", result))
    except Exception as exc:  # noqa: BLE001 — convert to a short, safe string
        q.put(("err", f"{type(exc).__name__}: {exc}"))


def run_isolated(func: Callable[..., Any], *args, timeout: float | None = None, **kwargs) -> Any:
    timeout = timeout or settings.op_timeout_seconds

    # In tests (or when explicitly disabled) run in-process for speed/determinism.
    if not settings.process_isolation:
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            log.warning("operation failed (in-process): %s", type(exc).__name__)
            raise ProcessingError("The file could not be processed.") from exc

    q = _CTX.Queue()
    proc = _CTX.Process(target=_worker, args=(func, args, kwargs, q), daemon=True)
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
        log.warning("operation exceeded %ss timeout and was killed", timeout)
        raise TimeoutAppError("Processing took too long and was stopped.")

    try:
        status, payload = q.get(timeout=10)
    except Exception:  # noqa: BLE001
        log.warning("operation produced no result (exit code %s)", proc.exitcode)
        raise ProcessingError("Processing failed to produce a result.")

    if status == "ok":
        return payload

    log.warning("operation error: %s", payload)
    raise ProcessingError("The file could not be processed.")
