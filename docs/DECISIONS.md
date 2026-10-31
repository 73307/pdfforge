# Architecture Decisions (ADR log)

## ADR-001: Stack
- **Frontend:** Next.js App Router + TypeScript + Tailwind. SSR tool pages give good
  SEO; client components handle uploads.
- **Backend:** FastAPI (async, typed, great file-upload support).
- **PDF libs:** `pypdf` for structural ops (merge/split/rotate/encrypt),
  `PyMuPDF (fitz)` for rendering and image→PDF, `Pillow` for image validation.
- **Why split FE/BE:** processing is CPU/memory heavy and must be isolated from the
  web tier so limits (timeout, memory) can be applied independently.

## ADR-002: No DB / queue in MVP
Local temp storage + background cleanup is enough for synchronous, size-limited ops.
PostgreSQL + Redis/Celery are deferred to Phase 7 and only added when job duration or
traffic demands async processing.

## ADR-003: Security model — trust nothing from the client
- Validate **file content** (magic bytes + library parse), never the extension or
  the client-supplied filename.
- Storage filenames are server-generated random tokens.
- Downloads go through a token → absolute-path map; the resolved path is re-checked to
  be inside the data dir (defense against traversal) before streaming.
- Every response (success or error) triggers temp cleanup; a sweeper removes anything
  older than the retention window.
- Errors return a generic JSON body + a request id; details are logged server-side
  **without** file contents.
- Strict security headers + locked-down CORS + in-memory per-IP rate limiting.

## ADR-004: Honest UX
No fake progress bars. Indeterminate spinners for in-flight work; real byte sizes and
page counts where known. Conversion limitations stated in the UI.

## ADR-005: Licensing flag
PyMuPDF/MuPDF is AGPL; LibreOffice is MPL/LGPL. Before any commercial deployment,
review and, if needed, obtain a commercial MuPDF license. Documented in README.
