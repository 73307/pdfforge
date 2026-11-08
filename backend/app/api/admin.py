"""Password-protected admin dashboard showing anonymous usage metrics.

Access is gated by a small custom login form (not the browser's HTTP Basic popup).
A valid login sets a signed, HttpOnly session cookie — the only cookie this app uses,
and only for the admin, never for visitors. If ADMIN_USER/ADMIN_PASSWORD aren't set the
whole thing is disabled and returns 404.

The pages are server-rendered HTML with inline CSS only — no scripts, no external assets.
"""
from __future__ import annotations

import hashlib
import hmac
import html
import secrets
import time

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import metrics
from app.config import settings
from app.security.ratelimit import rate_limit

router = APIRouter()

_COOKIE = "pdfforge_admin"
_TTL = 8 * 60 * 60  # 8 hours


# --------------------------------------------------------------------------- auth
def _enabled() -> bool:
    return bool(settings.admin_user and settings.admin_password)


def _key() -> bytes:
    return hashlib.sha256(("pdfforge-admin-session::" + settings.admin_password).encode()).digest()


def _make_token() -> str:
    expiry = str(int(time.time()) + _TTL)
    sig = hmac.new(_key(), expiry.encode(), hashlib.sha256).hexdigest()
    return f"{expiry}:{sig}"


def _valid_token(token: str | None) -> bool:
    if not token or ":" not in token:
        return False
    expiry, sig = token.split(":", 1)
    if not expiry.isdigit() or int(expiry) < time.time():
        return False
    expected = hmac.new(_key(), expiry.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


def _authed(request: Request) -> bool:
    return _valid_token(request.cookies.get(_COOKIE))


def _set_cookie(response) -> None:
    response.set_cookie(
        _COOKIE,
        _make_token(),
        max_age=_TTL,
        httponly=True,
        samesite="strict",
        secure=settings.app_env == "production",
        path="/admin",
    )


# --------------------------------------------------------------------------- routes
@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request) -> HTMLResponse:
    if not _enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not _authed(request):
        return HTMLResponse(_login_page())
    return HTMLResponse(_dashboard(metrics.summary()))


@router.post("/admin/login", response_class=HTMLResponse, dependencies=[Depends(rate_limit)])
def admin_login(user: str = Form(""), password: str = Form("")):
    if not _enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    user_ok = hmac.compare_digest(user, settings.admin_user)
    pass_ok = hmac.compare_digest(password, settings.admin_password)
    if not (user_ok and pass_ok):
        return HTMLResponse(_login_page(error="Wrong username or password."), status_code=401)
    resp = RedirectResponse(url="/admin", status_code=303)
    _set_cookie(resp)
    return resp


@router.get("/admin/logout")
def admin_logout():
    resp = RedirectResponse(url="/admin", status_code=303)
    resp.delete_cookie(_COOKIE, path="/admin")
    return resp


# --------------------------------------------------------------------------- pages
_HEAD = """<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PDFForge — Admin</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:#0f2e2b; color:#e8f0ee; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }}
  a {{ color:#f97a3c; }}
  .wrap {{ max-width:980px; margin:0 auto; padding:28px 20px 60px; }}
  h1 {{ font-size:22px; margin:0; }} h1 span {{ color:#f97a3c; }}
  .brand {{ font-size:22px; font-weight:800; }} .brand span {{ color:#f97a3c; }}
  {extra}
</style></head><body>"""

_LOGIN_CSS = """
  .login { min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }
  .box { width:100%; max-width:360px; background:#163f3a; border:1px solid rgba(255,255,255,.08);
         border-radius:18px; padding:28px; }
  .box .brand { text-align:center; }
  .box h2 { font-size:15px; color:#a7c1ba; text-align:center; margin:6px 0 20px; font-weight:500; }
  label { display:block; font-size:13px; color:#a7c1ba; margin:14px 0 6px; }
  input { width:100%; padding:11px 13px; border-radius:11px; border:1px solid rgba(255,255,255,.14);
          background:#0f2e2b; color:#e8f0ee; font-size:15px; }
  input:focus { outline:2px solid #f75f22; outline-offset:1px; }
  button { width:100%; margin-top:22px; padding:12px; border:0; border-radius:999px; cursor:pointer;
           background:#e64e12; color:#fff; font-size:15px; font-weight:700; }
  button:hover { background:#bf3d0f; }
  .err { background:rgba(220,38,38,.16); color:#fca5a5; border-radius:10px; padding:9px 12px;
         font-size:13px; margin-top:14px; text-align:center; }
  .note { color:#6f8a84; font-size:12px; text-align:center; margin-top:16px; }
"""


def _login_page(error: str = "") -> str:
    err_html = f'<div class="err">{html.escape(error)}</div>' if error else ""
    head = _HEAD.format(extra=_LOGIN_CSS)
    return f"""{head}<div class="login"><form class="box" method="post" action="/admin/login">
      <div class="brand">PDF<span>Forge</span></div>
      <h2>Admin sign in</h2>
      <label for="u">Username</label>
      <input id="u" name="user" autocomplete="username" autofocus>
      <label for="p">Password</label>
      <input id="p" name="password" type="password" autocomplete="current-password">
      {err_html}
      <button type="submit">Sign in</button>
      <div class="note">Usage metrics · authorized access only</div>
    </form></div></body></html>"""


# --------------------------------------------------------------------------- dashboard
_DASH_CSS = """
  .top { display:flex; align-items:center; justify-content:space-between; gap:12px; }
  .sub { color:#a7c1ba; font-size:13px; margin-top:4px; }
  .logout { font-size:13px; color:#a7c1ba; text-decoration:none; border:1px solid rgba(255,255,255,.14);
            padding:7px 14px; border-radius:999px; white-space:nowrap; }
  .logout:hover { color:#fff; border-color:rgba(255,255,255,.3); }
  h2 { font-size:15px; text-transform:uppercase; letter-spacing:.08em; color:#a7c1ba; margin:32px 0 12px; }
  .cards { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:20px; }
  .card { background:#163f3a; border:1px solid rgba(255,255,255,.08); border-radius:14px; padding:16px 18px; }
  .card .k { color:#a7c1ba; font-size:12px; text-transform:uppercase; letter-spacing:.06em; }
  .card .v { font-size:28px; font-weight:800; margin-top:4px; }
  table { width:100%; border-collapse:collapse; background:#163f3a; border-radius:12px; overflow:hidden; }
  th,td { text-align:left; padding:10px 12px; border-bottom:1px solid rgba(255,255,255,.06); font-size:14px; }
  th { color:#a7c1ba; font-size:11px; text-transform:uppercase; letter-spacing:.05em; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; }
  td.tool { font-weight:600; }
  .barcell { width:34%; }
  .bar { background:rgba(255,255,255,.08); border-radius:6px; height:9px; overflow:hidden; }
  .bar span { display:block; height:100%; border-radius:6px; }
  .empty { text-align:center; color:#a7c1ba; padding:22px; }
  .tag { background:rgba(220,38,38,.18); color:#fca5a5; border-radius:999px; padding:2px 9px; font-size:12px; }
  .when { color:#a7c1ba; font-size:12px; }
  .trend { display:flex; gap:6px; align-items:flex-end; background:#163f3a; border-radius:12px; padding:16px; }
  .tcol { flex:1; text-align:center; }
  .tbar { height:90px; display:flex; align-items:flex-end; }
  .tbar span { display:block; width:100%; background:#f75f22; border-radius:4px 4px 0 0; }
  .tlabel { color:#a7c1ba; font-size:10px; margin-top:6px; }
  .tval { font-size:11px; color:#e8f0ee; }
  .foot { color:#6f8a84; font-size:12px; margin-top:34px; }
  @media (max-width:640px) { .cards { grid-template-columns:1fr; } .barcell { display:none; } }
"""


def _pct(part: int, whole: int) -> int:
    return round(100 * part / whole) if whole else 0


def _bar(value: int, maximum: int, color: str) -> str:
    w = round(100 * value / maximum) if maximum else 0
    return f'<div class="bar"><span style="width:{w}%;background:{color}"></span></div>'


def _dashboard(data: dict) -> str:
    totals = data["totals"]
    req, ok, fail = totals["requests"], totals["successes"], totals["failures"]
    per_tool, trend, errors = data["per_tool"], data["daily_trend"], data["recent_errors"]
    max_tool = max((t["requests"] or 0 for t in per_tool), default=0)
    max_day = max((d["requests"] for d in trend), default=0)

    rows = ""
    for t in per_tool:
        r = t["requests"] or 0
        s = t["successes"] or 0
        f = t["failures"] or 0
        avg_ms = round((t["total_ms"] or 0) / r) if r else 0
        sr = _pct(s, r)
        sr_color = "#16a34a" if sr >= 90 else "#d97706" if sr >= 60 else "#dc2626"
        rows += f"""<tr>
          <td class="tool">{html.escape(t["tool"])}</td>
          <td class="num">{r}</td>
          <td class="barcell">{_bar(r, max_tool, "#f75f22")}</td>
          <td class="num" style="color:#16a34a">{s}</td>
          <td class="num" style="color:{'#dc2626' if f else '#9aa6a3'}">{f}</td>
          <td class="num" style="color:{sr_color};font-weight:700">{sr}%</td>
          <td class="num">{avg_ms} ms</td>
        </tr>"""
    if not rows:
        rows = '<tr><td colspan="7" class="empty">No usage recorded yet.</td></tr>'

    trend_bars = ""
    for d in trend:
        h = round(100 * d["requests"] / max_day) if max_day else 0
        trend_bars += (
            f'<div class="tcol" title="{html.escape(d["day"])}: {d["requests"]}">'
            f'<div class="tbar"><span style="height:{max(h,2)}%"></span></div>'
            f'<div class="tlabel">{html.escape(d["day"][5:])}</div>'
            f'<div class="tval">{d["requests"]}</div></div>'
        )

    err_rows = ""
    for e in errors:
        err_rows += (
            f'<tr><td class="tool">{html.escape(e["tool"])}</td>'
            f'<td><span class="tag">{html.escape(e["category"])}</span></td>'
            f'<td class="num">{e["status"]}</td>'
            f'<td class="when">{html.escape(e["at"].replace("T", " ").replace("+00:00", " UTC"))}</td></tr>'
        )
    if not err_rows:
        err_rows = '<tr><td colspan="4" class="empty">No errors recorded. 🎉</td></tr>'

    overall_sr = _pct(ok, req)
    sr_color = "#16a34a" if overall_sr >= 90 else "#d97706" if overall_sr >= 60 else "#dc2626"
    head = _HEAD.format(extra=_DASH_CSS)

    return f"""{head}<div class="wrap">
  <div class="top">
    <div>
      <h1>PDF<span>Forge</span> &middot; Admin</h1>
      <div class="sub">Anonymous usage metrics — no IPs, file names, or contents.</div>
    </div>
    <a class="logout" href="/admin/logout">Sign out</a>
  </div>

  <div class="cards">
    <div class="card"><div class="k">Total requests</div><div class="v">{req}</div></div>
    <div class="card"><div class="k">Success rate</div><div class="v" style="color:{sr_color}">{overall_sr}%</div></div>
    <div class="card"><div class="k">Failures</div><div class="v" style="color:{'#dc2626' if fail else '#e8f0ee'}">{fail}</div></div>
  </div>

  <h2>Requests — last {len(trend)} days</h2>
  <div class="trend">{trend_bars}</div>

  <h2>Tools</h2>
  <table>
    <tr><th>Tool</th><th class="num">Uses</th><th></th><th class="num">OK</th><th class="num">Fail</th><th class="num">Success</th><th class="num">Avg time</th></tr>
    {rows}
  </table>

  <h2>Recent errors</h2>
  <table>
    <tr><th>Tool</th><th>Type</th><th class="num">Status</th><th>When</th></tr>
    {err_rows}
  </table>

  <div class="foot">PDFForge admin · metrics are aggregate counts only, stored server-side.</div>
</div></body></html>"""
