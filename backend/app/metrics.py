"""Anonymous usage metrics.

Stores aggregate counters plus a rolling window of recent events — per tool: how many
requests, how many succeeded/failed, processing time, and byte sizes. From these it
derives deeper (still fully anonymous) insights: time percentiles, busiest hours, error
breakdowns and data volume. It records NO IP addresses, file names, file contents, or
anything that could identify a user; it exists purely to show which tools are used and
where they fail, so the product can be improved.

Backed by a small SQLite file so the numbers survive restarts and are shared across
worker processes. Recording is best-effort and never raises into a request.
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from datetime import date, datetime, timedelta, timezone

from app.config import settings
from app.core.logging import get_logger

log = get_logger("metrics")

_MAX_EVENTS = 50_000  # rolling window kept for the deeper (percentile/hourly) stats
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
               tool TEXT NOT NULL, day TEXT NOT NULL,
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
        """CREATE TABLE IF NOT EXISTS events (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               tool TEXT NOT NULL, category TEXT NOT NULL, status INTEGER NOT NULL,
               ms INTEGER NOT NULL, req_bytes INTEGER NOT NULL, resp_bytes INTEGER NOT NULL,
               ts INTEGER NOT NULL
           )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts)")
    return conn


def record(tool: str, status: int, duration_ms: int, req_bytes: int, resp_bytes: int) -> None:
    """Record one tool invocation. Best-effort: never raises."""
    if not settings.metrics_enabled:
        return
    ok = 200 <= status < 300
    cat = _category(status)
    now = int(time.time())
    try:
        with _lock:
            conn = _connect()
            try:
                conn.execute(
                    """INSERT INTO daily (tool, day, requests, successes, failures, total_ms, req_bytes, resp_bytes)
                       VALUES (?, ?, 1, ?, ?, ?, ?, ?)
                       ON CONFLICT(tool, day) DO UPDATE SET
                           requests = requests + 1,
                           successes = successes + ?, failures = failures + ?,
                           total_ms = total_ms + ?, req_bytes = req_bytes + ?, resp_bytes = resp_bytes + ?""",
                    (tool, _today(), 1 if ok else 0, 0 if ok else 1, duration_ms, req_bytes, resp_bytes,
                     1 if ok else 0, 0 if ok else 1, duration_ms, req_bytes, resp_bytes),
                )
                conn.execute(
                    "INSERT INTO events (tool, category, status, ms, req_bytes, resp_bytes, ts) VALUES (?,?,?,?,?,?,?)",
                    (tool, cat, status, duration_ms, req_bytes, resp_bytes, now),
                )
                conn.execute(
                    "DELETE FROM events WHERE id <= (SELECT MAX(id) FROM events) - ?", (_MAX_EVENTS,)
                )
                conn.commit()
            finally:
                conn.close()
    except Exception as exc:  # noqa: BLE001 — metrics must never break a request
        log.warning("metrics record failed: %s", type(exc).__name__)


def _pctile(values: list[int], p: float) -> int:
    """Nearest-rank-ish percentile with linear interpolation. values must be sorted."""
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(values) - 1)
    return int(values[lo] + (values[hi] - values[lo]) * (k - lo))


def summary(days: int = 30) -> dict:
    """Aggregate + deeper view for the admin dashboard."""
    empty = {
        "totals": {"requests": 0, "successes": 0, "failures": 0, "bytes_in": 0, "bytes_out": 0},
        "per_tool": [], "daily_trend": [], "hourly": [], "errors_by_category": [], "recent_errors": [],
    }
    try:
        conn = _connect()
        try:
            conn.row_factory = sqlite3.Row

            # --- lifetime per-tool counts + totals (from daily) ---
            lifetime = {
                r["tool"]: dict(r)
                for r in conn.execute(
                    """SELECT tool, SUM(requests) requests, SUM(successes) successes,
                              SUM(failures) failures, SUM(req_bytes) req_bytes, SUM(resp_bytes) resp_bytes
                       FROM daily GROUP BY tool"""
                ).fetchall()
            }
            totals = {"requests": 0, "successes": 0, "failures": 0, "bytes_in": 0, "bytes_out": 0}
            for t in lifetime.values():
                totals["requests"] += t["requests"] or 0
                totals["successes"] += t["successes"] or 0
                totals["failures"] += t["failures"] or 0
                totals["bytes_in"] += t["req_bytes"] or 0
                totals["bytes_out"] += t["resp_bytes"] or 0

            # --- daily trend ---
            start = (date.today() - timedelta(days=days - 1)).isoformat()
            by_day = {
                r["day"]: r["requests"]
                for r in conn.execute(
                    "SELECT day, SUM(requests) requests FROM daily WHERE day >= ? GROUP BY day", (start,)
                ).fetchall()
            }
            daily_trend = [
                {"day": (date.today() - timedelta(days=days - 1 - i)).isoformat()}
                for i in range(days)
            ]
            for d in daily_trend:
                d["requests"] = by_day.get(d["day"], 0)

            # --- pull recent events once; derive percentiles / sizes / hours / errors ---
            events = conn.execute(
                "SELECT tool, category, status, ms, req_bytes, resp_bytes, ts FROM events"
            ).fetchall()
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        log.warning("metrics summary failed: %s", type(exc).__name__)
        return empty

    # Per-tool timing (percentiles) + average sizes, from the recent event window.
    ms_by_tool: dict[str, list[int]] = {}
    in_by_tool: dict[str, list[int]] = {}
    out_by_tool: dict[str, list[int]] = {}
    hours = [0] * 24
    errors_by_cat: dict[str, int] = {}
    recent_errors: list[dict] = []
    week_ago = int(time.time()) - 7 * 86400

    for e in events:
        ms_by_tool.setdefault(e["tool"], []).append(e["ms"])
        in_by_tool.setdefault(e["tool"], []).append(e["req_bytes"])
        out_by_tool.setdefault(e["tool"], []).append(e["resp_bytes"])
        if e["ts"] >= week_ago:
            hours[datetime.fromtimestamp(e["ts"], timezone.utc).hour] += 1
        if e["category"] != "ok":
            errors_by_cat[e["category"]] = errors_by_cat.get(e["category"], 0) + 1

    for e in reversed(events):
        if e["category"] != "ok" and len(recent_errors) < 25:
            recent_errors.append({
                "tool": e["tool"], "category": e["category"], "status": e["status"],
                "at": datetime.fromtimestamp(e["ts"], timezone.utc).isoformat(timespec="seconds"),
            })

    per_tool = []
    for tool, lt in sorted(lifetime.items(), key=lambda kv: kv[1]["requests"] or 0, reverse=True):
        ms = sorted(ms_by_tool.get(tool, []))
        ins = in_by_tool.get(tool, [])
        outs = out_by_tool.get(tool, [])
        per_tool.append({
            "tool": tool,
            "requests": lt["requests"] or 0,
            "successes": lt["successes"] or 0,
            "failures": lt["failures"] or 0,
            "p50_ms": _pctile(ms, 0.50),
            "p95_ms": _pctile(ms, 0.95),
            "avg_in": round(sum(ins) / len(ins)) if ins else 0,
            "avg_out": round(sum(outs) / len(outs)) if outs else 0,
        })

    return {
        "totals": totals,
        "per_tool": per_tool,
        "daily_trend": daily_trend,
        "hourly": [{"hour": h, "requests": hours[h]} for h in range(24)],
        "errors_by_category": sorted(
            [{"category": c, "count": n} for c, n in errors_by_cat.items()],
            key=lambda x: x["count"], reverse=True,
        ),
        "recent_errors": recent_errors,
    }
