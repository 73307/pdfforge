"""Anonymous usage metrics.

Stores aggregate counters plus a rolling window of recent events — per tool: how many
requests, how many succeeded/failed, processing time, and byte sizes. From these it
derives richer (still fully anonymous) insights for the admin console: trends, time
percentiles, busiest hours, error breakdowns, recent jobs and data volume. It records
NO IP addresses, file names, file contents, or anything that could identify a user.

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

_MAX_EVENTS = 50_000  # rolling window kept for the deeper (percentile/hourly/jobs) stats
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
               ts INTEGER NOT NULL, err_code TEXT NOT NULL DEFAULT '', err_msg TEXT NOT NULL DEFAULT ''
           )"""
    )
    # Migrate older databases that predate the error-reason columns.
    cols = {r[1] for r in conn.execute("PRAGMA table_info(events)")}
    if "err_code" not in cols:
        conn.execute("ALTER TABLE events ADD COLUMN err_code TEXT NOT NULL DEFAULT ''")
    if "err_msg" not in cols:
        conn.execute("ALTER TABLE events ADD COLUMN err_msg TEXT NOT NULL DEFAULT ''")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts)")
    return conn


def record(tool: str, status: int, duration_ms: int, req_bytes: int, resp_bytes: int,
           err_code: str = "", err_msg: str = "") -> None:
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
                    "INSERT INTO events (tool, category, status, ms, req_bytes, resp_bytes, ts, err_code, err_msg) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    (tool, cat, status, duration_ms, req_bytes, resp_bytes, now,
                     "" if ok else err_code, "" if ok else err_msg),
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
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(values) - 1)
    return int(values[lo] + (values[hi] - values[lo]) * (k - lo))


def _empty_report(range_days: int) -> dict:
    return {
        "range_days": range_days,
        "totals": {"requests": 0, "successes": 0, "failures": 0, "bytes_in": 0, "bytes_out": 0,
                   "median_ms": 0, "p95_ms": 0, "prev_requests": 0, "prev_successes": 0, "prev_failures": 0},
        "daily": [], "per_tool": [], "hourly": [], "errors_by_category": [],
        "errors_by_reason": [], "recent_jobs": [], "recent_errors": [],
    }


def report(range_days: int = 7) -> dict:
    """Everything the admin console needs, scoped to the last `range_days` days."""
    today = date.today()
    start_day = (today - timedelta(days=range_days - 1)).isoformat()
    prev_start = (today - timedelta(days=2 * range_days - 1)).isoformat()
    start_ts = int(time.time()) - range_days * 86400

    try:
        conn = _connect()
        try:
            conn.row_factory = sqlite3.Row

            # per-tool counts within the range (from the daily rollup)
            per_tool_counts = {
                r["tool"]: dict(r)
                for r in conn.execute(
                    """SELECT tool, SUM(requests) requests, SUM(successes) successes,
                              SUM(failures) failures, SUM(req_bytes) req_bytes, SUM(resp_bytes) resp_bytes
                       FROM daily WHERE day >= ? GROUP BY tool""",
                    (start_day,),
                ).fetchall()
            }
            # per-day totals across all tools, within the range
            day_rows = {
                r["day"]: dict(r)
                for r in conn.execute(
                    """SELECT day, SUM(requests) requests, SUM(successes) successes,
                              SUM(failures) failures, SUM(total_ms) total_ms
                       FROM daily WHERE day >= ? GROUP BY day""",
                    (start_day,),
                ).fetchall()
            }
            # previous equal-length period (for deltas)
            prev = conn.execute(
                """SELECT SUM(requests) requests, SUM(successes) successes, SUM(failures) failures
                   FROM daily WHERE day >= ? AND day < ?""",
                (prev_start, start_day),
            ).fetchone()

            events = conn.execute(
                "SELECT tool, category, status, ms, req_bytes, resp_bytes, ts, err_code, err_msg "
                "FROM events WHERE ts >= ? ORDER BY ts",
                (start_ts,),
            ).fetchall()
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        log.warning("metrics report failed: %s", type(exc).__name__)
        return _empty_report(range_days)

    # --- totals + deltas ---
    totals = {"requests": 0, "successes": 0, "failures": 0, "bytes_in": 0, "bytes_out": 0}
    for t in per_tool_counts.values():
        totals["requests"] += t["requests"] or 0
        totals["successes"] += t["successes"] or 0
        totals["failures"] += t["failures"] or 0
        totals["bytes_in"] += t["req_bytes"] or 0
        totals["bytes_out"] += t["resp_bytes"] or 0
    totals["prev_requests"] = (prev["requests"] or 0) if prev else 0
    totals["prev_successes"] = (prev["successes"] or 0) if prev else 0
    totals["prev_failures"] = (prev["failures"] or 0) if prev else 0

    all_ms = sorted(e["ms"] for e in events)
    totals["median_ms"] = _pctile(all_ms, 0.50)
    totals["p95_ms"] = _pctile(all_ms, 0.95)

    # --- daily series (ordered, gap-filled) ---
    daily = []
    for i in range(range_days):
        d = (today - timedelta(days=range_days - 1 - i)).isoformat()
        row = day_rows.get(d, {})
        req = row.get("requests", 0) or 0
        succ = row.get("successes", 0) or 0
        daily.append({
            "day": d, "requests": req, "completed": succ,
            "failed": row.get("failures", 0) or 0,
            "avg_ms": round((row.get("total_ms", 0) or 0) / req) if req else 0,
        })

    # --- per-tool timing/sizes from events in range ---
    ms_by, in_by, out_by = {}, {}, {}
    hours = [0] * 24
    errors_by_cat = {}
    reasons: dict = {}  # human error message -> {count, tools, category}
    for e in events:
        ms_by.setdefault(e["tool"], []).append(e["ms"])
        in_by.setdefault(e["tool"], []).append(e["req_bytes"])
        out_by.setdefault(e["tool"], []).append(e["resp_bytes"])
        hours[datetime.fromtimestamp(e["ts"], timezone.utc).hour] += 1
        if e["category"] != "ok":
            errors_by_cat[e["category"]] = errors_by_cat.get(e["category"], 0) + 1
            key = (e["err_msg"] or "").strip() or e["category"]
            r = reasons.setdefault(key, {"reason": key, "count": 0, "tools": set(), "category": e["category"]})
            r["count"] += 1
            r["tools"].add(e["tool"])

    per_tool = []
    for tool, c in sorted(per_tool_counts.items(), key=lambda kv: kv[1]["requests"] or 0, reverse=True):
        ms = sorted(ms_by.get(tool, []))
        ins, outs = in_by.get(tool, []), out_by.get(tool, [])
        per_tool.append({
            "tool": tool, "requests": c["requests"] or 0, "successes": c["successes"] or 0,
            "failures": c["failures"] or 0, "p50_ms": _pctile(ms, 0.50), "p95_ms": _pctile(ms, 0.95),
            "avg_in": round(sum(ins) / len(ins)) if ins else 0,
            "avg_out": round(sum(outs) / len(outs)) if outs else 0,
        })

    # --- recent jobs + recent errors (from the tail of the event stream) ---
    recent_jobs, recent_errors = [], []
    for e in reversed(events):
        when = datetime.fromtimestamp(e["ts"], timezone.utc).isoformat(timespec="seconds")
        if len(recent_jobs) < 12:
            recent_jobs.append({
                "tool": e["tool"], "status": e["status"], "category": e["category"],
                "ms": e["ms"], "at": when,
            })
        if e["category"] != "ok" and len(recent_errors) < 25:
            recent_errors.append({
                "tool": e["tool"], "category": e["category"], "status": e["status"], "at": when,
                "reason": (e["err_msg"] or "").strip() or e["category"],
            })
        if len(recent_jobs) >= 12 and len(recent_errors) >= 25:
            break

    return {
        "range_days": range_days,
        "totals": totals,
        "daily": daily,
        "per_tool": per_tool,
        "hourly": [{"hour": h, "requests": hours[h]} for h in range(24)],
        "errors_by_category": sorted(
            [{"category": c, "count": n} for c, n in errors_by_cat.items()],
            key=lambda x: x["count"], reverse=True,
        ),
        "errors_by_reason": sorted(
            [{"reason": r["reason"], "count": r["count"], "category": r["category"],
              "tools": ", ".join(sorted(r["tools"]))} for r in reasons.values()],
            key=lambda x: x["count"], reverse=True,
        ),
        "recent_jobs": recent_jobs,
        "recent_errors": recent_errors,
    }
