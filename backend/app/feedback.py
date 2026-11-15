"""Anonymous user feedback — a star rating (1-5) and an optional message.

No accounts, no IPs, no emails — just the rating and whatever text the user chose to
type. Stored in a small SQLite file next to the metrics DB (same persistent location).
Recording is best-effort and never raises into a request.
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from datetime import datetime, timezone

from app.config import settings
from app.core.logging import get_logger

log = get_logger("feedback")
_lock = threading.Lock()


def _db_path() -> str:
    base = os.path.dirname(settings.metrics_db_path) or "."
    return os.path.join(base, "feedback.db")


def _connect() -> sqlite3.Connection:
    path = _db_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=3000")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS feedback (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               rating INTEGER NOT NULL,
               message TEXT NOT NULL DEFAULT '',
               tool TEXT NOT NULL DEFAULT '',
               ts INTEGER NOT NULL
           )"""
    )
    return conn


def record(rating: int, message: str = "", tool: str = "") -> None:
    """Store one feedback entry. Best-effort: never raises."""
    try:
        with _lock:
            conn = _connect()
            try:
                conn.execute(
                    "INSERT INTO feedback (rating, message, tool, ts) VALUES (?,?,?,?)",
                    (rating, message, tool, int(time.time())),
                )
                conn.commit()
            finally:
                conn.close()
    except Exception as exc:  # noqa: BLE001 — never break the request
        log.warning("feedback record failed: %s", type(exc).__name__)


def summary(limit: int = 40) -> dict:
    try:
        conn = _connect()
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute("SELECT rating, message, tool, ts FROM feedback ORDER BY id DESC").fetchall()
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        log.warning("feedback summary failed: %s", type(exc).__name__)
        return {"count": 0, "avg": 0.0, "dist": [0, 0, 0, 0, 0], "with_comment": 0, "recent": []}

    count = len(rows)
    avg = round(sum(r["rating"] for r in rows) / count, 2) if count else 0.0
    dist = [0, 0, 0, 0, 0]
    for r in rows:
        if 1 <= r["rating"] <= 5:
            dist[r["rating"] - 1] += 1
    recent = [
        {
            "rating": r["rating"],
            "message": (r["message"] or "").strip(),
            "tool": r["tool"] or "",
            "at": datetime.fromtimestamp(r["ts"], timezone.utc).isoformat(timespec="seconds"),
        }
        for r in rows[:limit]
    ]
    return {
        "count": count,
        "avg": avg,
        "dist": dist,  # dist[i] = number of i+1-star ratings
        "with_comment": sum(1 for r in rows if (r["message"] or "").strip()),
        "recent": recent,
    }
