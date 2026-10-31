# PDFForge — Online PDF Tools Platform

PDFForge is a privacy-first, security-hardened online PDF toolkit (merge, split,
rotate, image↔PDF, compress, protect, PDF↔Word, Excel→PDF, OCR). It is **original
software** — inspired by the *category* of tools like iLovePDF, but with its own
branding, UI and code.

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS
- **Backend:** Python + FastAPI + pypdf + PyMuPDF
- **Security:** content-based file validation, server-side random filenames,
  path-traversal-proof downloads, per-op timeouts, rate limiting, strict security
  headers, automatic temp-file cleanup, and no leaking of server paths/stack traces.

> No system is literally "100% unbreakable", but this project applies defense-in-depth
> so that the common attacks against file-upload apps (malicious files, path traversal,
> oversized/zip-bomb inputs, resource exhaustion, info leaks) are blocked. See
> [`docs/SECURITY.md`](docs/SECURITY.md).

---

## Quick start (macOS)

### 1. Backend (FastAPI)

```bash
cd pdf-converter/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp ../.env.example .env            # edit values if you like
uvicorn app.main:app --reload --port 8000
```

Check it:

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok", ...}`

Run backend tests:

```bash
cd pdf-converter/backend
source .venv/bin/activate
pytest -q
```

### 2. Frontend (Next.js)

```bash
cd pdf-converter/frontend
npm install
cp .env.local.example .env.local   # points the UI at http://localhost:8000
npm run dev
```

Open http://localhost:3000

### 3. Everything with Docker (optional)

```bash
cd pdf-converter
cp .env.example .env
docker compose up --build
```

Frontend → http://localhost:3000 · Backend → http://localhost:8000

---

## Project layout

```
pdf-converter/
├── backend/      FastAPI app, PDF services, validators, security, tests
├── frontend/     Next.js UI, tool pages, components
├── docs/         requirements, decisions, security, project status
├── docker-compose.yml
└── .env.example
```

See [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for the phase-by-phase checklist.

## Optional system tools (for conversion/OCR)

Most tools (and **PDF→Word**, via `pdf2docx`) work out of the box. Three tools shell out to
a system binary and show a clear "unavailable" message if it's missing — install these to
enable them:

```bash
brew install --cask libreoffice
```

```bash
brew install tesseract
```

- **Word→PDF** and **Excel→PDF** need **LibreOffice** (`soffice`).
- **OCR PDF** needs **Tesseract** (extra languages: install the matching language packs).

## Honest limitations

- Compression may not shrink every PDF (already-optimized or image-only files); you get the original back if so.
- PDF→Word is editable for digital PDFs but won't perfectly preserve complex layouts, fonts, or tables; scanned/image-only PDFs need OCR (not included).
- Word→PDF (LibreOffice) is high-fidelity but still not pixel-perfect for every document.
- "Protect" adds real AES encryption; it never removes or bypasses passwords.

## License & branding

Use original branding and copy. Review the license of every dependency
(pypdf, PyMuPDF/MuPDF, LibreOffice) before any **commercial** deployment —
MuPDF in particular is AGPL and may require a commercial license.
