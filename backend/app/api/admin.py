"""Password-protected admin dashboard showing anonymous usage metrics.

Guarded by HTTP Basic auth (ADMIN_USER / ADMIN_PASSWORD). If those aren't set the
whole thing is disabled and returns 404, so the endpoint doesn't even advertise itself.
The page is server-rendered HTML with inline CSS only — no scripts, no external assets.
"""
from __future__ import annotations

import html
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app import metrics
from app.config import settings

router = APIRouter()
_basic = HTTPBasic(auto_error=False)
_UNAUTHORIZED = {"WWW-Authenticate": "Basic"}


def require_admin(credentials: Optional[HTTPBasicCredentials] = Depends(_basic)) -> None:
    # Disabled unless both are configured — behave as if the route doesn't exist.
    if not (settings.admin_user and settings.admin_password):
        raise HTTPException(status_code=404, detail="Not Found")
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers=_UNAUTHORIZED)
    user_ok = secrets.compare_digest(credentials.username, settings.admin_user)
    pass_ok = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers=_UNAUTHORIZED)


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(_: None = Depends(require_admin)) -> HTMLResponse:
    return HTMLResponse(_render(metrics.summary()))


# --------------------------------------------------------------------------- rendering
def _pct(part: int, whole: int) -> int:
    return round(100 * part / whole) if whole else 0


def _bar(value: int, maximum: int, color: str) -> str:
    w = round(100 * value / maximum) if maximum else 0
    return f'<div class="bar"><span style="width:{w}%;background:{color}"></span></div>'


def _render(data: dict) -> str:
    totals = data["totals"]
    req = totals["requests"]
    ok = totals["successes"]
    fail = totals["failures"]
    per_tool = data["per_tool"]
    trend = data["daily_trend"]
    errors = data["recent_errors"]

    max_tool = max((t["requests"] or 0 for t in per_tool), default=0)
    max_day = max((d["requests"] for d in trend), default=0)

    # Per-tool rows
    rows = ""
    for t in per_tool:
        name = html.escape(t["tool"])
        r = t["requests"] or 0
        s = t["successes"] or 0
        f = t["failures"] or 0
        avg_ms = round((t["total_ms"] or 0) / r) if r else 0
        sr = _pct(s, r)
        sr_color = "#16a34a" if sr >= 90 else "#d97706" if sr >= 60 else "#dc2626"
        rows += f"""<tr>
          <td class="tool">{name}</td>
          <td class="num">{r}</td>
          <td class="barcell">{_bar(r, max_tool, "#f75f22")}</td>
          <td class="num" style="color:#16a34a">{s}</td>
          <td class="num" style="color:{'#dc2626' if f else '#9aa6a3'}">{f}</td>
          <td class="num" style="color:{sr_color};font-weight:700">{sr}%</td>
          <td class="num">{avg_ms} ms</td>
        </tr>"""
    if not rows:
        rows = '<tr><td colspan="7" class="empty">No usage recorded yet.</td></tr>'

    # 14-day trend bars
    trend_bars = ""
    for d in trend:
        h = round(100 * d["requests"] / max_day) if max_day else 0
        label = d["day"][5:]  # MM-DD
        trend_bars += (
            f'<div class="tcol" title="{html.escape(d["day"])}: {d["requests"]}">'
            f'<div class="tbar"><span style="height:{max(h,2)}%"></span></div>'
            f'<div class="tlabel">{html.escape(label)}</div>'
            f'<div class="tval">{d["requests"]}</div></div>'
        )

    # Recent errors
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

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>PDFForge — Admin</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:#0f2e2b; color:#e8f0ee; font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }}
  .wrap {{ max-width:980px; margin:0 auto; padding:28px 20px 60px; }}
  h1 {{ font-size:22px; margin:0; }} h1 span {{ color:#f97a3c; }}
  .sub {{ color:#a7c1ba; font-size:13px; margin-top:4px; }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.08em; color:#a7c1ba; margin:32px 0 12px; }}
  .cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:20px; }}
  .card {{ background:#163f3a; border:1px solid rgba(255,255,255,.08); border-radius:14px; padding:16px 18px; }}
  .card .k {{ color:#a7c1ba; font-size:12px; text-transform:uppercase; letter-spacing:.06em; }}
  .card .v {{ font-size:28px; font-weight:800; margin-top:4px; }}
  table {{ width:100%; border-collapse:collapse; background:#163f3a; border-radius:12px; overflow:hidden; }}
  th,td {{ text-align:left; padding:10px 12px; border-bottom:1px solid rgba(255,255,255,.06); font-size:14px; }}
  th {{ color:#a7c1ba; font-size:11px; text-transform:uppercase; letter-spacing:.05em; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.tool {{ font-weight:600; }}
  .barcell {{ width:34%; }}
  .bar {{ background:rgba(255,255,255,.08); border-radius:6px; height:9px; overflow:hidden; }}
  .bar span {{ display:block; height:100%; border-radius:6px; }}
  .empty {{ text-align:center; color:#a7c1ba; padding:22px; }}
  .tag {{ background:rgba(220,38,38,.18); color:#fca5a5; border-radius:999px; padding:2px 9px; font-size:12px; }}
  .when {{ color:#a7c1ba; font-size:12px; }}
  .trend {{ display:flex; gap:6px; align-items:flex-end; background:#163f3a; border-radius:12px; padding:16px; }}
  .tcol {{ flex:1; text-align:center; }}
  .tbar {{ height:90px; display:flex; align-items:flex-end; }}
  .tbar span {{ display:block; width:100%; background:#f75f22; border-radius:4px 4px 0 0; }}
  .tlabel {{ color:#a7c1ba; font-size:10px; margin-top:6px; }}
  .tval {{ font-size:11px; color:#e8f0ee; }}
  .foot {{ color:#6f8a84; font-size:12px; margin-top:34px; }}
  @media (max-width:640px) {{ .cards {{ grid-template-columns:1fr; }} .barcell {{ display:none; }} }}
</style></head><body><div class="wrap">
  <h1>PDF<span>Forge</span> &middot; Admin</h1>
  <div class="sub">Anonymous usage metrics — no IPs, file names, or contents. Auto-refreshes every 60s.</div>

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
