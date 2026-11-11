"""Admin console — a multi-section operations dashboard built on real, anonymous metrics.

Access is gated by a small custom login form (not the browser's HTTP Basic popup). A
valid login sets a signed, HttpOnly session cookie — the only cookie this app uses, and
only for the admin, never for visitors. If ADMIN_USER/ADMIN_PASSWORD aren't set the
whole thing is disabled and returns 404.

Every number here is derived from aggregate counts + a capped recent-event window: no
IPs, file names, contents, or per-user tracking. There is no visitor/traffic-source or
job-queue data because this app stores none of that — nothing shown here is faked.

Pages are server-rendered HTML with inline CSS/SVG only — no scripts, no external assets.
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import html
import io
import secrets
import time
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse

from app import metrics, system_status
from app.config import settings
from app.security.ratelimit import rate_limit

router = APIRouter()

_COOKIE = "pdfforge_admin"
_TTL = 8 * 60 * 60
_RANGES = (7, 30, 90)


# --------------------------------------------------------------------------- auth
def _enabled() -> bool:
    return bool(settings.admin_user and settings.admin_password)


def _key() -> bytes:
    return hashlib.sha256(("pdfforge-admin-session::" + settings.admin_password).encode()).digest()


def _make_token() -> str:
    expiry = str(int(time.time()) + _TTL)
    return f"{expiry}:{hmac.new(_key(), expiry.encode(), hashlib.sha256).hexdigest()}"


def _valid_token(token: Optional[str]) -> bool:
    if not token or ":" not in token:
        return False
    expiry, sig = token.split(":", 1)
    if not expiry.isdigit() or int(expiry) < time.time():
        return False
    return hmac.compare_digest(sig, hmac.new(_key(), expiry.encode(), hashlib.sha256).hexdigest())


def _authed(request: Request) -> bool:
    return _valid_token(request.cookies.get(_COOKIE))


def _set_cookie(response) -> None:
    response.set_cookie(
        _COOKIE, _make_token(), max_age=_TTL, httponly=True, samesite="strict",
        secure=settings.app_env == "production", path="/admin",
    )


def _range(request: Request) -> int:
    try:
        r = int(request.query_params.get("range", "7"))
    except ValueError:
        r = 7
    return r if r in _RANGES else 7


def _guard(request: Request):
    """Return None if the request is an authenticated admin, else an HTMLResponse to send."""
    if not _enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not _authed(request):
        return HTMLResponse(_login_page())
    return None


# --------------------------------------------------------------------------- routes
@router.get("/admin", response_class=HTMLResponse)
def admin_overview(request: Request):
    blocked = _guard(request)
    if blocked:
        return blocked
    rng = _range(request)
    return HTMLResponse(_shell("overview", "Overview", rng, _page_overview(metrics.report(rng), system_status.status(), rng)))


@router.get("/admin/tools", response_class=HTMLResponse)
def admin_tools(request: Request):
    blocked = _guard(request)
    if blocked:
        return blocked
    rng = _range(request)
    return HTMLResponse(_shell("tools", "Tool performance", rng, _page_tools(metrics.report(rng))))


@router.get("/admin/errors", response_class=HTMLResponse)
def admin_errors(request: Request):
    blocked = _guard(request)
    if blocked:
        return blocked
    rng = _range(request)
    return HTMLResponse(_shell("errors", "Errors & alerts", rng, _page_errors(metrics.report(rng))))


@router.get("/admin/system", response_class=HTMLResponse)
def admin_system(request: Request):
    blocked = _guard(request)
    if blocked:
        return blocked
    rng = _range(request)
    return HTMLResponse(_shell("system", "System", rng, _page_system(system_status.status())))


@router.get("/admin/export.csv", response_class=PlainTextResponse)
def admin_export(request: Request):
    blocked = _guard(request)
    if blocked:
        raise HTTPException(status_code=401, detail="Sign in first")
    rep = metrics.report(_range(request))
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["tool", "requests", "successes", "failures", "success_rate_%", "p50_ms", "p95_ms", "avg_in_bytes", "avg_out_bytes"])
    for t in rep["per_tool"]:
        sr = round(100 * t["successes"] / t["requests"]) if t["requests"] else 0
        w.writerow([t["tool"], t["requests"], t["successes"], t["failures"], sr, t["p50_ms"], t["p95_ms"], t["avg_in"], t["avg_out"]])
    return PlainTextResponse(
        buf.getvalue(), media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="pdfforge-tools.csv"'},
    )


@router.post("/admin/login", response_class=HTMLResponse, dependencies=[Depends(rate_limit)])
def admin_login(user: str = Form(""), password: str = Form("")):
    if not _enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not (hmac.compare_digest(user, settings.admin_user) and hmac.compare_digest(password, settings.admin_password)):
        return HTMLResponse(_login_page(error="Wrong username or password."), status_code=401)
    resp = RedirectResponse(url="/admin", status_code=303)
    _set_cookie(resp)
    return resp


@router.get("/admin/logout")
def admin_logout():
    resp = RedirectResponse(url="/admin", status_code=303)
    resp.delete_cookie(_COOKIE, path="/admin")
    return resp


# --------------------------------------------------------------------------- format helpers
def _pct(part: int, whole: int) -> int:
    return round(100 * part / whole) if whole else 0


def _bytes(n: int) -> str:
    v = float(n or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if v < 1024 or unit == "TB":
            return f"{v:.0f} {unit}" if unit == "B" else f"{v:.1f} {unit}"
        v /= 1024
    return f"{v:.1f} TB"


def _ms(n: int) -> str:
    return f"{n / 1000:.1f} s" if n and n >= 1000 else f"{n or 0} ms"


def _uptime(s: int) -> str:
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m = s // 60
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


def _delta_html(cur: int, prev: int) -> str:
    if not prev:
        return '<span class="d flat">— no prior data</span>'
    pct = (cur - prev) / prev * 100
    up = pct >= 0
    arrow = "▲" if up else "▼"
    cls = "up" if up else "down"
    return f'<span class="d {cls}">{arrow} {abs(pct):.1f}% vs previous</span>'


# --------------------------------------------------------------------------- SVG
def _spark(values: list[int], color: str) -> str:
    if not values:
        values = [0]
    n = len(values)
    mx = max(values) or 1
    w, h = 120.0, 34.0
    pts = []
    for i, v in enumerate(values):
        x = (w * i / (n - 1)) if n > 1 else 0
        y = h - 3 - (h - 6) * (v / mx)
        pts.append(f"{x:.1f},{y:.1f}")
    line = " ".join(pts)
    area = f"0,{h} " + line + f" {w},{h}"
    return (
        f'<svg class="spark" viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="none">'
        f'<polygon points="{area}" fill="{color}" opacity="0.12"/>'
        f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def _area_chart(daily: list[dict]) -> str:
    if not daily:
        daily = [{"day": "", "completed": 0, "failed": 0}]
    n = len(daily)
    W, H, pt, pb = 680.0, 230.0, 12.0, 26.0
    mx = max([max(d["completed"], d["failed"]) for d in daily] + [1])

    def X(i):
        return (W * i / (n - 1)) if n > 1 else 0

    def Y(v):
        return pt + (H - pt - pb) * (1 - v / mx)

    comp = " ".join(f"{X(i):.1f},{Y(d['completed']):.1f}" for i, d in enumerate(daily))
    fail = " ".join(f"{X(i):.1f},{Y(d['failed']):.1f}" for i, d in enumerate(daily))
    area = f"0,{Y(0):.1f} " + comp + f" {W:.1f},{Y(0):.1f}"
    grid = "".join(
        f'<line x1="0" y1="{pt + (H - pt - pb) * g / 2:.1f}" x2="{W}" y2="{pt + (H - pt - pb) * g / 2:.1f}" '
        f'stroke="#e4ebe9" stroke-width="1"/>' for g in range(3)
    )
    step = max(1, n // 7)
    labels = "".join(
        f'<text x="{X(i):.1f}" y="{H - 6:.1f}" fill="#8aa39d" font-size="10" '
        f'text-anchor="middle">{html.escape(daily[i]["day"][5:])}</text>'
        for i in range(0, n, step)
    )
    return (
        f'<svg class="area" viewBox="0 0 {W:.0f} {H:.0f}">'
        '<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#15a46a" stop-opacity="0.28"/>'
        '<stop offset="1" stop-color="#15a46a" stop-opacity="0"/></linearGradient></defs>'
        f"{grid}"
        f'<polygon points="{area}" fill="url(#ag)"/>'
        f'<polyline points="{comp}" fill="none" stroke="#15a46a" stroke-width="2.5" stroke-linejoin="round"/>'
        f'<polyline points="{fail}" fill="none" stroke="#f05a28" stroke-width="2" stroke-linejoin="round"/>'
        f"{labels}</svg>"
    )


def _bar(value: int, maximum: int, color: str) -> str:
    w = round(100 * value / maximum) if maximum else 0
    return f'<div class="bar"><span style="width:{w}%;background:{color}"></span></div>'


def _status_badge(status: int) -> str:
    if 200 <= status < 300:
        return '<span class="badge ok">✓ Completed</span>'
    if status == 429:
        return '<span class="badge warn">⏳ Throttled</span>'
    return f'<span class="badge fail">✕ Failed · {status}</span>'


# --------------------------------------------------------------------------- alerts
def _alerts(rep: dict, sysd: dict) -> list[dict]:
    out = []
    for t in rep["per_tool"]:
        if t["requests"] >= 5:
            sr = _pct(t["successes"], t["requests"])
            if sr < 80:
                out.append({"lvl": "warn", "title": f"{t['tool']} is failing often",
                            "body": f"Only {sr}% success over {t['requests']} jobs. Check the inputs or the converter."})
            if t["p95_ms"] >= 10000:
                out.append({"lvl": "warn", "title": f"{t['tool']} is slow",
                            "body": f"95th-percentile time is {_ms(t['p95_ms'])}. Consider more worker capacity."})
    st = sysd["storage"]
    if st["total"] and st["used"] / st["total"] > 0.8:
        out.append({"lvl": "warn", "title": "Temporary storage is nearly full",
                    "body": f"{_bytes(st['used'])} of {_bytes(st['total'])} used."})
    for name, ok in sysd["converters"].items():
        if not ok:
            out.append({"lvl": "info", "title": f"{name} is not installed",
                        "body": "The tools that depend on it will return a clear error until it's set up."})
    return out[:3]


# --------------------------------------------------------------------------- pages
def _page_overview(rep: dict, sysd: dict, rng: int) -> str:
    tot = rep["totals"]
    daily = rep["daily"]
    req, ok, fail = tot["requests"], tot["successes"], tot["failures"]
    sr = _pct(ok, req)

    s_req = [d["requests"] for d in daily]
    s_ok = [d["completed"] for d in daily]
    s_fail = [d["failed"] for d in daily]
    s_rate = [_pct(d["completed"], d["requests"]) for d in daily]
    s_ms = [d["avg_ms"] for d in daily]

    def card(icon, label, value, delta, spark, accent):
        return f"""<div class="stat">
          <div class="st-h"><span class="st-ic" style="background:{accent}1a;color:{accent}">{icon}</span>
            <span class="st-l">{label}</span></div>
          <div class="st-v">{value}</div>{delta}
          <div class="st-s">{spark}</div></div>"""

    cards = (
        card("⇄", "Jobs run", f"{req:,}", _delta_html(req, tot["prev_requests"]), _spark(s_req, "#15a46a"), "#15a46a")
        + card("✓", "Completed", f"{ok:,}", _delta_html(ok, tot["prev_successes"]), _spark(s_ok, "#15a46a"), "#15a46a")
        + card("◎", "Success rate", f"{sr}%", f'<span class="d flat">{ok:,} ok · {fail:,} failed</span>', _spark(s_rate, "#2a9d8f"), "#2a9d8f")
        + card("⏱", "Median time", _ms(tot["median_ms"]), f'<span class="d flat">p95 {_ms(tot["p95_ms"])}</span>', _spark(s_ms, "#e8a33d"), "#e8a33d")
        + card("⚠", "Failed jobs", f"{fail:,}", _delta_html(fail, tot["prev_failures"]), _spark(s_fail, "#f05a28"), "#f05a28")
    )

    # tool performance (top 6)
    max_jobs = max([t["requests"] for t in rep["per_tool"]] + [1])
    tp = ""
    for t in rep["per_tool"][:6]:
        tsr = _pct(t["successes"], t["requests"])
        tp += f"""<div class="tp-row"><span class="tp-n">{html.escape(t['tool'])}</span>
          <span class="tp-bar">{_bar(t['requests'], max_jobs, '#15a46a')}</span>
          <span class="tp-j">{t['requests']:,}</span>
          <span class="tp-s">{tsr}%</span></div>"""
    if not tp:
        tp = '<div class="muted pad">No tool usage yet.</div>'

    # recent jobs
    jobs = ""
    for j in rep["recent_jobs"]:
        jobs += f"""<tr><td class="tool">{html.escape(j['tool'])}</td>
          <td>{_status_badge(j['status'])}</td><td class="num">{_ms(j['ms'])}</td>
          <td class="when">{html.escape(j['at'][11:19])} UTC</td></tr>"""
    if not jobs:
        jobs = '<tr><td colspan="4" class="empty">No jobs recorded yet.</td></tr>'

    # system health
    conv = "".join(
        f'<div class="sh-row"><span>{html.escape(n)}</span>'
        f'<span class="{"ok" if ok_ else "bad"}">{"● Available" if ok_ else "○ Not installed"}</span></div>'
        for n, ok_ in sysd["converters"].items()
    )
    st = sysd["storage"]
    st_pct = round(100 * st["used"] / st["total"]) if st["total"] else 0
    data_total = tot["bytes_in"] + tot["bytes_out"]

    # alerts
    alerts = _alerts(rep, sysd)
    banner = ""
    if alerts:
        a = alerts[0]
        banner = f"""<div class="banner {a['lvl']}"><span class="b-ic">⚠</span>
          <span><b>{html.escape(a['title'])}.</b> {html.escape(a['body'])}</span>
          <a href="/admin/errors?range={rng}">View details →</a></div>"""

    return f"""{banner}
    <div class="stats">{cards}</div>
    <div class="grid2">
      <div class="panel">
        <div class="p-h"><h3>Processing activity</h3>
          <span class="legend"><i class="dot g"></i>Completed <i class="dot o"></i>Failed</span></div>
        {_area_chart(daily)}
      </div>
      <div class="panel">
        <div class="p-h"><h3>Tool performance</h3><a href="/admin/tools?range={rng}">All tools →</a></div>
        <div class="tp-head"><span>Tool</span><span></span><span>Jobs</span><span>OK%</span></div>
        {tp}
      </div>
    </div>
    <div class="grid2">
      <div class="panel">
        <div class="p-h"><h3>Recent jobs</h3><a href="/admin/errors?range={rng}">Error log →</a></div>
        <table class="jobs"><tr><th>Tool</th><th>Status</th><th class="num">Duration</th><th>Time</th></tr>{jobs}</table>
        <div class="muted small pad">Job metadata only — no file names or contents are stored.</div>
      </div>
      <div class="side-col">
        <div class="panel">
          <div class="p-h"><h3>System health</h3></div>
          <div class="sh-row"><span>API</span><span class="ok">● Operational</span></div>
          {conv}
          <div class="sh-row"><span>Uptime</span><span class="muted">{_uptime(sysd['uptime_s'])}</span></div>
          <div class="sh-store">
            <div class="sh-row"><span>Temp storage</span><span class="muted">{_bytes(st['used'])} of {_bytes(st['total'])}</span></div>
            <div class="bar"><span style="width:{max(st_pct,1)}%;background:#15a46a"></span></div>
          </div>
        </div>
        <div class="panel">
          <div class="p-h"><h3>Data processed</h3></div>
          <div class="st-v">{_bytes(data_total)}</div>
          <div class="muted small">{_bytes(tot['bytes_in'])} in · {_bytes(tot['bytes_out'])} out · last {rng} days</div>
        </div>
      </div>
    </div>"""


def _page_tools(rep: dict) -> str:
    max_jobs = max([t["requests"] for t in rep["per_tool"]] + [1])
    rows = ""
    for t in rep["per_tool"]:
        sr = _pct(t["successes"], t["requests"])
        c = "#16a34a" if sr >= 90 else "#d97706" if sr >= 60 else "#dc2626"
        rows += f"""<tr><td class="tool">{html.escape(t['tool'])}</td>
          <td class="num">{t['requests']:,}</td>
          <td class="barcell">{_bar(t['requests'], max_jobs, '#15a46a')}</td>
          <td class="num" style="color:{c};font-weight:700">{sr}%</td>
          <td class="num" style="color:#16a34a">{t['successes']:,}</td>
          <td class="num" style="color:{'#dc2626' if t['failures'] else '#9aa6a3'}">{t['failures']:,}</td>
          <td class="num">{_ms(t['p50_ms'])}</td><td class="num">{_ms(t['p95_ms'])}</td>
          <td class="num">{_bytes(t['avg_in'])}</td><td class="num">{_bytes(t['avg_out'])}</td></tr>"""
    if not rows:
        rows = '<tr><td colspan="10" class="empty">No tool usage yet.</td></tr>'
    hourly = rep["hourly"]
    maxh = max([h["requests"] for h in hourly] + [1])
    bars = ""
    for h in hourly:
        pct = max(round(100 * h["requests"] / maxh), 2)
        label = f'{h["hour"]:02d}' if h["hour"] % 3 == 0 else ""
        bars += (
            f'<div class="tcol" title="{h["hour"]:02d}:00 UTC: {h["requests"]}">'
            f'<div class="tbar"><span style="height:{pct}%"></span></div>'
            f'<div class="hlabel">{label}</div></div>'
        )
    return f"""<div class="panel">
      <div class="p-h"><h3>Tool performance</h3><a href="/admin/export.csv?range={rep['range_days']}">Export CSV ↓</a></div>
      <table class="full"><tr><th>Tool</th><th class="num">Jobs</th><th></th><th class="num">Success</th>
        <th class="num">OK</th><th class="num">Fail</th><th class="num">Median</th><th class="num">p95</th>
        <th class="num">Avg in</th><th class="num">Avg out</th></tr>{rows}</table>
    </div>
    <div class="panel"><div class="p-h"><h3>Busiest hours (UTC)</h3></div><div class="trend">{bars}</div></div>"""


def _page_errors(rep: dict) -> str:
    alerts = _alerts(rep, system_status.status())
    al = ""
    for a in alerts:
        al += f'<div class="banner {a["lvl"]}"><span class="b-ic">⚠</span><span><b>{html.escape(a["title"])}.</b> {html.escape(a["body"])}</span></div>'
    if not al:
        al = '<div class="banner ok"><span class="b-ic">✓</span><span><b>All clear.</b> No active alerts.</span></div>'

    # Why errors happen — grouped by the exact message users receive (the actionable view)
    reasons = rep["errors_by_reason"]
    max_r = max([r["count"] for r in reasons] + [1])
    rrows = ""
    for r in reasons:
        rrows += (f'<tr><td class="reason">{html.escape(r["reason"])}</td>'
                  f'<td class="when">{html.escape(r["tools"])}</td>'
                  f'<td class="barcell">{_bar(r["count"], max_r, "#dc2626")}</td>'
                  f'<td class="num">{r["count"]}</td></tr>')
    if not rrows:
        rrows = '<tr><td colspan="4" class="empty">No errors recorded. 🎉</td></tr>'

    max_ec = max([c["count"] for c in rep["errors_by_category"]] + [1])
    ecat = ""
    for c in rep["errors_by_category"]:
        ecat += f'<tr><td class="tool">{html.escape(c["category"])}</td><td class="barcell">{_bar(c["count"], max_ec, "#dc2626")}</td><td class="num">{c["count"]}</td></tr>'
    if not ecat:
        ecat = '<tr><td colspan="3" class="empty">No errors. 🎉</td></tr>'

    er = ""
    for e in rep["recent_errors"]:
        er += (f'<tr><td class="tool">{html.escape(e["tool"])}</td>'
               f'<td class="reason">{html.escape(e.get("reason", e["category"]))}</td>'
               f'<td class="num">{e["status"]}</td>'
               f'<td class="when">{html.escape(e["at"].replace("T", " ").replace("+00:00", " UTC"))}</td></tr>')
    if not er:
        er = '<tr><td colspan="4" class="empty">No errors recorded. 🎉</td></tr>'

    return f"""{al}
    <div class="panel">
      <div class="p-h"><h3>Why errors happen</h3><span class="muted small">the exact message users get — grouped so you can fix the cause</span></div>
      <table><tr><th>Reason</th><th>Tool(s)</th><th></th><th class="num">Count</th></tr>{rrows}</table>
    </div>
    <div class="grid2">
      <div class="panel"><div class="p-h"><h3>Error categories</h3></div>
        <table><tr><th>Type</th><th></th><th class="num">Count</th></tr>{ecat}</table></div>
      <div class="panel"><div class="p-h"><h3>Recent errors</h3></div>
        <table class="jobs"><tr><th>Tool</th><th>Reason</th><th class="num">Status</th><th>When</th></tr>{er}</table></div>
    </div>"""


def _page_system(sysd: dict) -> str:
    conv = "".join(
        f'<div class="sh-row"><span>{html.escape(n)}</span>'
        f'<span class="{"ok" if ok_ else "bad"}">{"● Available" if ok_ else "○ Not installed"}</span></div>'
        for n, ok_ in sysd["converters"].items()
    )
    st = sysd["storage"]
    st_pct = round(100 * st["used"] / st["total"]) if st["total"] else 0
    cfg = [
        ("Environment", settings.app_env),
        ("Max upload", _bytes(settings.max_upload_bytes)),
        ("Max per file", _bytes(settings.max_file_bytes)),
        ("Max PDF pages", f"{settings.max_pdf_pages:,}"),
        ("Rate limit", f"{settings.rate_limit_requests} / {settings.rate_limit_window_seconds}s per IP"),
        ("Op timeout", f"{settings.op_timeout_seconds}s"),
        ("Office timeout", f"{settings.office_timeout_seconds}s"),
    ]
    cfg_rows = "".join(f'<div class="sh-row"><span>{html.escape(k)}</span><span class="muted">{html.escape(str(v))}</span></div>' for k, v in cfg)
    return f"""<div class="grid2">
      <div class="panel"><div class="p-h"><h3>Health</h3></div>
        <div class="sh-row"><span>API</span><span class="ok">● Operational</span></div>
        <div class="sh-row"><span>Uptime</span><span class="muted">{_uptime(sysd['uptime_s'])}</span></div>
        {conv}
        <div class="sh-store"><div class="sh-row"><span>Temp storage</span>
          <span class="muted">{_bytes(st['used'])} of {_bytes(st['total'])}</span></div>
          <div class="bar"><span style="width:{max(st_pct,1)}%;background:#15a46a"></span></div></div>
      </div>
      <div class="panel"><div class="p-h"><h3>Configuration &amp; limits</h3></div>{cfg_rows}</div>
    </div>"""


# --------------------------------------------------------------------------- shell + login
def _nav(active: str, rng: int) -> str:
    items = [("overview", "Overview", "/admin"), ("tools", "Tool performance", "/admin/tools"),
             ("errors", "Errors & alerts", "/admin/errors"), ("system", "System", "/admin/system")]
    out = ""
    for key, label, href in items:
        cls = "nav-i active" if key == active else "nav-i"
        out += f'<a class="{cls}" href="{href}?range={rng}">{html.escape(label)}</a>'
    return out


def _range_selector(active: str, rng: int) -> str:
    base = {"overview": "/admin", "tools": "/admin/tools", "errors": "/admin/errors", "system": "/admin/system"}[active]
    out = ""
    for r in _RANGES:
        cls = "rg active" if r == rng else "rg"
        out += f'<a class="{cls}" href="{base}?range={r}">{r}d</a>'
    return out


def _shell(active: str, crumb: str, rng: int, body: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head>"
        "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>PDFForge — Admin</title><style>" + _CSS + "</style></head><body>"
        + f"""<div class="app">
      <aside class="side">
        <div class="brand">PDF<span>Forge</span><em>Admin</em></div>
        <div class="nav-sec">Monitor</div>
        {_nav(active, rng)}
        <div class="side-foot">
          <a class="nav-i" href="/" target="_blank">↗ Visit website</a>
          <a class="nav-i" href="/admin/logout">⏻ Sign out</a>
        </div>
      </aside>
      <main class="main">
        <header class="topbar">
          <div class="crumb"><span class="muted">Admin</span> <span class="sep">/</span> <b>{html.escape(crumb)}</b></div>
          <div class="ranges">{_range_selector(active, rng)}</div>
        </header>
        <div class="content"><h1>{html.escape(crumb)}</h1>
          <p class="lede">Real, anonymous usage &amp; health — no visitor tracking, no personal data.</p>
          {body}
        </div>
      </main></div></body></html>"""
    )


_LOGIN_CSS = """
  body { margin:0; background:#0f2e2b; color:#e8f0ee; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }
  .login { min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }
  .box { width:100%; max-width:360px; background:#163f3a; border:1px solid rgba(255,255,255,.08); border-radius:18px; padding:28px; }
  .brand { text-align:center; font-size:22px; font-weight:800; } .brand span { color:#f97a3c; }
  h2 { font-size:15px; color:#a7c1ba; text-align:center; margin:6px 0 20px; font-weight:500; }
  label { display:block; font-size:13px; color:#a7c1ba; margin:14px 0 6px; }
  input { width:100%; padding:11px 13px; border-radius:11px; border:1px solid rgba(255,255,255,.14); background:#0f2e2b; color:#e8f0ee; font-size:15px; box-sizing:border-box; }
  input:focus { outline:2px solid #f75f22; outline-offset:1px; }
  button { width:100%; margin-top:22px; padding:12px; border:0; border-radius:999px; cursor:pointer; background:#e64e12; color:#fff; font-size:15px; font-weight:700; }
  button:hover { background:#bf3d0f; }
  .err { background:rgba(220,38,38,.16); color:#fca5a5; border-radius:10px; padding:9px 12px; font-size:13px; margin-top:14px; text-align:center; }
  .note { color:#6f8a84; font-size:12px; text-align:center; margin-top:16px; }
"""


def _login_page(error: str = "") -> str:
    err = f'<div class="err">{html.escape(error)}</div>' if error else ""
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>PDFForge — Admin</title><style>" + _LOGIN_CSS + "</style></head><body>"
        f"""<div class="login"><form class="box" method="post" action="/admin/login">
          <div class="brand">PDF<span>Forge</span></div>
          <h2>Admin sign in</h2>
          <label for="u">Username</label>
          <input id="u" name="user" autocomplete="username" autofocus>
          <label for="p">Password</label>
          <input id="p" name="password" type="password" autocomplete="current-password">
          {err}
          <button type="submit">Sign in</button>
          <div class="note">Usage metrics · authorized access only</div>
        </form></div></body></html>"""
    )


_CSS = """
  * { box-sizing:border-box; }
  body { margin:0; background:#f4f7f7; color:#0f1f1d; font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif; }
  a { color:#107a52; text-decoration:none; } a:hover { text-decoration:underline; }
  .app { display:flex; min-height:100vh; }
  .side { width:240px; flex-shrink:0; background:#0f2e2b; color:#bcd6d0; padding:18px 14px; display:flex; flex-direction:column; }
  .brand { font-size:19px; font-weight:800; color:#fff; padding:4px 8px 2px; } .brand span { color:#f97a3c; }
  .brand em { font-style:normal; font-size:10px; font-weight:700; letter-spacing:.1em; background:#1d514a; color:#cfe6e0; border-radius:6px; padding:2px 6px; margin-left:8px; vertical-align:middle; }
  .nav-sec { font-size:10px; text-transform:uppercase; letter-spacing:.14em; color:#6f8a84; margin:22px 8px 8px; }
  .nav-i { display:block; padding:9px 12px; border-radius:10px; color:#bcd6d0; font-weight:500; margin-bottom:2px; }
  .nav-i:hover { background:#163f3a; color:#fff; text-decoration:none; }
  .nav-i.active { background:#1d514a; color:#fff; box-shadow:inset 3px 0 0 #f75f22; }
  .side-foot { margin-top:auto; border-top:1px solid rgba(255,255,255,.08); padding-top:10px; }
  .main { flex:1; min-width:0; display:flex; flex-direction:column; }
  .topbar { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:14px 26px; border-bottom:1px solid #e4ebe9; background:#fff; }
  .crumb .sep { color:#c3cecb; margin:0 4px; }
  .ranges { display:flex; gap:4px; background:#eef3f2; border-radius:999px; padding:3px; }
  .rg { padding:5px 12px; border-radius:999px; color:#5b6b68; font-weight:600; font-size:13px; }
  .rg.active { background:#fff; color:#0f1f1d; box-shadow:0 1px 2px rgba(0,0,0,.08); }
  .content { padding:24px 26px 50px; max-width:1200px; width:100%; }
  h1 { font-size:26px; margin:0; letter-spacing:-.01em; }
  .lede { color:#5b6b68; margin:4px 0 20px; }
  .muted { color:#5b6b68; } .small { font-size:12px; } .pad { padding:10px 2px; }
  .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; }
  .stat { background:#fff; border:1px solid #e4ebe9; border-radius:16px; padding:15px 16px; }
  .st-h { display:flex; align-items:center; gap:8px; }
  .st-ic { width:30px; height:30px; border-radius:9px; display:inline-flex; align-items:center; justify-content:center; font-size:15px; }
  .st-l { color:#5b6b68; font-size:13px; font-weight:600; }
  .st-v { font-size:28px; font-weight:800; margin:8px 0 2px; letter-spacing:-.02em; }
  .d { font-size:12px; font-weight:600; } .d.up { color:#16a34a; } .d.down { color:#dc2626; } .d.flat { color:#8aa39d; }
  .st-s { margin-top:8px; height:34px; }
  .spark { width:100%; height:34px; display:block; }
  .grid2 { display:grid; grid-template-columns:1.4fr 1fr; gap:14px; margin-top:14px; }
  .side-col { display:flex; flex-direction:column; gap:14px; }
  .panel { background:#fff; border:1px solid #e4ebe9; border-radius:16px; padding:16px 18px; }
  .p-h { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
  .p-h h3 { margin:0; font-size:15px; } .p-h a { font-size:13px; font-weight:600; }
  .legend { font-size:12px; color:#5b6b68; } .dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin:0 4px 0 10px; }
  .dot.g { background:#15a46a; } .dot.o { background:#f05a28; }
  .area { width:100%; height:auto; display:block; }
  .bar { background:#eef3f2; border-radius:6px; height:8px; overflow:hidden; }
  .bar span { display:block; height:100%; border-radius:6px; }
  table { width:100%; border-collapse:collapse; }
  th,td { text-align:left; padding:9px 8px; border-bottom:1px solid #eef3f2; font-size:13px; }
  th { color:#8aa39d; font-size:11px; text-transform:uppercase; letter-spacing:.04em; font-weight:700; }
  td.num,th.num { text-align:right; font-variant-numeric:tabular-nums; }
  td.tool { font-weight:600; } td.when { color:#8aa39d; font-size:12px; }
  td.reason { font-weight:500; max-width:420px; }
  .empty { text-align:center; color:#8aa39d; padding:20px; }
  .badge { font-size:12px; font-weight:600; border-radius:999px; padding:2px 9px; }
  .badge.ok { background:#e5f5ec; color:#15834f; } .badge.fail { background:#fdeceb; color:#c23b28; } .badge.warn { background:#fdf2e3; color:#b4720c; }
  .tag { background:#fdeceb; color:#c23b28; border-radius:999px; padding:2px 9px; font-size:12px; }
  .tp-head,.tp-row { display:grid; grid-template-columns:1.3fr 1.1fr auto auto; gap:10px; align-items:center; }
  .tp-head { font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:#8aa39d; font-weight:700; padding-bottom:8px; border-bottom:1px solid #eef3f2; }
  .tp-row { padding:9px 0; border-bottom:1px solid #eef3f2; } .tp-n { font-weight:600; }
  .tp-j { text-align:right; font-variant-numeric:tabular-nums; } .tp-s { text-align:right; color:#15834f; font-weight:700; width:44px; }
  .barcell { width:26%; }
  .sh-row { display:flex; justify-content:space-between; padding:9px 0; border-bottom:1px solid #eef3f2; }
  .sh-row .ok { color:#15a46a; font-weight:600; } .sh-row .bad { color:#d97706; font-weight:600; }
  .sh-store { margin-top:6px; }
  .banner { display:flex; align-items:center; gap:12px; background:#fdf2e3; border:1px solid #f6dcae; color:#8a5a08; border-radius:14px; padding:12px 16px; margin-bottom:16px; }
  .banner.info { background:#eef4fb; border-color:#cfe0f3; color:#2c5a8a; }
  .banner.ok { background:#e9f6ef; border-color:#bfe3cd; color:#15834f; }
  .banner .b-ic { font-size:16px; } .banner a { margin-left:auto; font-weight:700; white-space:nowrap; }
  .trend { display:flex; gap:5px; align-items:flex-end; }
  .tcol { flex:1; text-align:center; } .tbar { height:84px; display:flex; align-items:flex-end; }
  .tbar span { display:block; width:100%; background:#15a46a; border-radius:4px 4px 0 0; } .hlabel { color:#8aa39d; font-size:9px; margin-top:4px; }
  .jobs td.tool { font-weight:600; }
  @media (max-width:860px) { .side { display:none; } .grid2 { grid-template-columns:1fr; } }
"""
