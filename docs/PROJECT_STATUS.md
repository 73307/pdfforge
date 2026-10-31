# PROJECT_STATUS

Living checklist. Updated at the end of each phase.

## Legend
✅ done · 🟡 partial · ⬜ not started

## Phases
- ✅ **Phase 0 — Requirements & decisions** — `docs/requirements.md`, `docs/DECISIONS.md`
- ✅ **Phase 1 — Environment & repo** — backend + frontend scaffolding, `.env.example`, health endpoint
- ✅ **Phase 2 — UI foundation** — homepage, tool directory, reusable `ToolLayout`, dropzone, states
- ✅ **Phase 3 — Merge PDF (end-to-end)** — upload+order → `/api/merge` → secure download → cleanup
- ✅ **Phase 4 — Core tools** — Split, Rotate, Images→PDF, PDF→Images
- ✅ **Phase 5 — Compress & Protect** — honest compression, AES password protection
- ✅ **Phase 6 — Reliability & security** — limits, validation, rate limit, timeouts, headers, cleanup (see `docs/SECURITY.md`)
- 🟡 **Phase 7 — Background jobs & storage** — not needed for size-limited sync MVP; design documented, deferred
- ✅ **Phase 8 — Advanced conversions** — PDF→Word (`pdf2docx`, editable, no extra install); Word→PDF & Excel→PDF (LibreOffice/`soffice`); OCR → searchable PDF or plain text (Tesseract). Each tool returns a safe "unavailable" message if its system binary isn't installed.
- 🟡 **Phase 9 — QA** — unit/integration tests included and run by **GitHub Actions CI** (`.github/workflows/ci.yml`: backend `pytest` + frontend type-check & build) on every push/PR; full a11y/perf/concurrency suite still pending
- ✅ **Phase 10 — Deployment** — slim `Dockerfile` + `Dockerfile.full` (LibreOffice+Tesseract), `docker-compose.yml` (local) + `docker-compose.prod.yml` (Caddy auto-HTTPS), **GitHub Actions CD** (`.github/workflows/deploy.yml`: tag `v*` → SSH deploy, dormant until configured), and a step-by-step `docs/DEPLOYMENT.md` (single-server + split-hosting).
- ✅ **Phase 11 — SEO & launch pages** — per-tool metadata, `sitemap.ts`, `robots.ts`, privacy/terms
- ⬜ **Phase 12 — Monetization** — deferred by design (do reliability first)

## Files changed (this build)
- Root: `README.md`, `.gitignore`, `.env.example`, `docker-compose.yml`
- `docs/`: `requirements.md`, `DECISIONS.md`, `SECURITY.md`, `PROJECT_STATUS.md`
- `backend/app/**` (config, core, security, validators, storage, services, api, main)
- `backend/tests/**`
- `frontend/app/**`, `frontend/components/**`, `frontend/lib/**`, config files

## Commands to run (macOS) — see README
Backend: `uvicorn app.main:app --reload --port 8000` · `pytest -q`
Frontend: `npm install && npm run dev`

## Test results (actually run on 2026-10-31, Python 3.9.6, macOS)
- **Backend unit/integration:** `pytest` → **30 passed** (health, security headers, validators,
  merge, split single/multi, rotate, images→pdf, pdf→images, compress, protect, body-size limit,
  disguised-file rejection, PDF→Word, Word→PDF & Excel→PDF graceful fallback, OCR graceful +
  bad-output/bad-lang rejection, non-Word/non-spreadsheet rejection).
- **Live smoke test** (server with default settings, i.e. real process-isolated workers):
  - `GET /health` → `{"status":"ok",...}`
  - Security headers present (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
    `Content-Security-Policy: default-src 'none'...`, `Referrer-Policy: no-referrer`).
  - `POST /api/merge` (2 + 3 page PDFs) → `200 application/pdf`, output had **5 pages**.
  - `POST /api/merge` with a disguised non-PDF → `415 unsupported_media_type` (safe message, no paths).
  - `POST /api/split` `ranges=1,3` → `200 application/zip`.
  - `POST /api/pdf-to-word` → `200` editable `.docx`; extracted text matched the source PDF.
  - `POST /api/word-to-pdf` (no LibreOffice here) → safe `422` "unavailable" message (no crash/leak).
  - `POST /api/excel-to-pdf` → `415` for non-spreadsheet; safe `422` "LibreOffice unavailable" for a valid file.
  - `POST /api/ocr-pdf` → safe `422` "Tesseract unavailable"; bad `output`/`lang` → `422 validation_error`.
  - Temp working dirs auto-deleted after each response (verified empty after completion).
- **Tools total:** 11 (merge, split, rotate, images→pdf, pdf→images, compress, protect, pdf→word, word→pdf, excel→pdf, ocr).
- **Frontend:** source complete and config JSON validated. Not run here because **Node.js is not
  installed on this machine** — run `npm install && npm run dev` after installing Node (see README).

## Known issues / limitations
- Compression can't shrink already-optimized or purely image PDFs much (reported honestly in UI).
- PDF↔Word is optional and depends on a LibreOffice install; fidelity varies.
- Rate limiting is in-memory (single process). Use Redis for multi-replica production.

## Next milestone
Phase 7 (async jobs) only if real traffic/large files demand it; otherwise Phase 12 after monetization review.
