"""Anonymous usage metrics.

Stores aggregate counters only — per tool, per day: how many requests, how many
succeeded/failed, total processing time and bytes. Plus a short ring of recent error
categories. It records NO IP addresses, file names, file contents, or anything that
could identify a user; it exists purely to show which tools are used and where they
fail, so the product can be improved.

Backed by a small SQLite file so the numbers survive restarts and are shared across
worker processes. Recording is best-effort and never raises into a request.
"""
from __future__ import annotations

import os
import sqlite3
import threading
from datetime import date, datetime, timedelta, timezone

from app.config import settings
from app.core.logging import get_logger

log = get_logger("metrics")

_MAX_RECENT_ERRORS = 200
_lock = threading.Lock()


def _today() -> str:
    return date.today().isoformat()


def _category(status: int) -> str:
    if 200 <= status < 300:
        return "ok"
    if status == 413:
        return "too_large"
    if status == 415:
        return "unsupported_type"
    if status == 422:
        return "invalid_input"
    if status == 429:
        return "rate_limited"
    if status >= 500:
        return "server_error"
    return "client_error"


def _connect() -> sqlite3.Connection:
    path = settings.metrics_db_path
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=3000")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS daily (
               tool TEXT NOT NULL,
               day TEXT NOT NULL,
               requests INTEGER NOT NULL DEFAULT 0,
               successes INTEGER NOT NULL DEFAULT 0,
               failures INTEGER NOT NULL DEFAULT 0,
               total_ms INTEGER NOT NULL DEFAULT 0,
               req_bytes INTEGER NOT NULL DEFAULT 0,
               resp_bytes INTEGER NOT NULL DEFAULT 0,
               PRIMARY KEY (tool, day)
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS errors (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               tool TEXT NOT NULL,
               category TEXT NOT NULL,
               status INTEGER NOT NULL,
               at TEXT NOT NULL
           )"""
    )
    return conn


def record(tool: str, status: int, duration_ms: int, req_bytes: int, resp_bytes: int) -> None:
    """Record one tool invocation. Best-effort: never raises."""
    if not settings.metrics_enabled:
        return
    ok = 200 <= status < 300
    cat = _category(status)
    try:
        with _lock:
            conn = _connect()
            try:
                conn.execute(
                    """INSERT INTO daily (tool, day, requests, successes, failures, total_ms, req_bytes, resp_bytes)
                       VALUES (?, ?, 1, ?, ?, ?, ?, ?)
                       ON CONFLICT(tool, day) DO UPDATE SET
                           requests = requests + 1,
                           successes = successes + ?,
                           failures = failures + ?,
                           total_ms = total_ms + ?,
                           req_bytes = req_bytes + ?,
                           resp_bytes = resp_bytes + ?""",
                    (
                        tool, _today(), 1 if ok else 0, 0 if ok else 1, duration_ms, req_bytes, resp_bytes,
                        1 if ok else 0, 0 if ok else 1, duration_ms, req_bytes, resp_bytes,
                    ),
                )
                if not ok:
                    conn.execute(
                        "INSERT INTO errors (tool, category, status, at) VALUES (?, ?, ?, ?)",
                        (tool, cat, status, datetime.now(timezone.utc).isoformat(timespec="seconds")),
                    )
                    conn.execute(
                        "DELETE FROM errors WHERE id < (SELECT MAX(id) FROM errors) - ?",
                        (_MAX_RECENT_ERRORS,),
                    )
                conn.commit()
            finally:
                conn.close()
    except Exception as exc:  # noqa: BLE001 — metrics must never break a request
        log.warning("metrics record failed: %s", type(exc).__name__)


def summary(days: int = 14) -> dict:
    """Aggregate view for the admin dashboard."""
    try:
        conn = _connect()
        try:
            conn.row_factory = sqlite3.Row
            per_tool = [
                dict(r)
                for r in conn.execute(
                    """SELECT tool,
                              SUM(requests)  AS requests,
                              SUM(successes) AS successes,
                              SUM(failures)  AS failures,
                              SUM(total_ms)  AS total_ms,
                              SUM(req_bytes) AS req_bytes,
                              MAX(day)       AS last_day
                       FROM daily GROUP BY tool ORDER BY requests DESC"""
                ).fetchall()
            ]
            totals = {"requests": 0, "successes": 0, "failures": 0}
            for t in per_tool:
                totals["requests"] += t["requests"] or 0
                totals["successes"] += t["successes"] or 0
                totals["failures"] += t["failures"] or 0

            start = (date.today() - timedelta(days=days - 1)).isoformat()
            by_day = {
                r["day"]: r["requests"]
                for r in conn.execute(
                    "SELECT day, SUM(requests) AS requests FROM daily WHERE day >= ? GROUP BY day",
                    (start,),
                ).fetchall()
            }
            daily_trend = []
            for i in range(days):
                d = (date.today() - timedelta(days=days - 1 - i)).isoformat()
                daily_trend.append({"day": d, "requests": by_day.get(d, 0)})

            recent_errors = [
                dict(r)
                for r in conn.execute(
                    "SELECT tool, category, status, at FROM errors ORDER BY id DESC LIMIT 25"
                ).fetchall()
            ]
            return {
                "totals": totals,
                "per_tool": per_tool,
                "daily_trend": daily_trend,
                "recent_errors": recent_errors,
            }
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        log.warning("metrics summary failed: %s", type(exc).__name__)
        return {"totals": {"requests": 0, "successes": 0, "failures": 0}, "per_tool": [], "daily_trend": [], "recent_errors": []}
