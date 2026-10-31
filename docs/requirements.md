# Phase 0 — Requirements & Acceptance Criteria

## Product name (placeholder)
**PDFForge** — original branding. Not affiliated with or imitating iLovePDF or any
other brand. Replace the logo/colors freely.

## Target users
Anyone who needs quick, private, browser-based PDF edits without installing software
or creating an account. No login required for the MVP.

## MVP tools (build order)
1. Merge PDF
2. Split PDF (page ranges / extract pages)
3. Rotate PDF
4. JPG/PNG → PDF
5. PDF → JPG/PNG
6. Compress PDF (honest results)
7. Protect PDF (password / AES encryption)
8. *(Later phase)* PDF ↔ Word / Office conversions

## Key decisions (defaults — change in `.env`)
| Decision | Default |
|---|---|
| First release requires login? | **No** |
| Payment in MVP? | **No** |
| Max total request size | 50 MB |
| Max single file size | 25 MB |
| Max files per request | 20 |
| Max PDF pages processed | 500 |
| Temp-file retention | 15 minutes, then auto-deleted |
| Download link lifetime | 15 minutes |
| Rate limit | 30 requests / 60s per IP |

## Supported input formats
- PDF (`application/pdf`, verified by content, not extension)
- Images: JPEG, PNG (verified by magic bytes)

## Non-goals (MVP)
- Accounts, billing, ads, analytics
- Cloud storage / databases
- Perfect-fidelity Office conversions

## Acceptance criteria (Definition of Done per tool)
- Works with at least one valid test file.
- Invalid / malformed / oversized / wrong-type input returns a **safe, clear** error
  (no stack trace, no server paths).
- Temp files are removed on success **and** failure.
- The result is streamed directly in the response (no path-based download endpoint),
  so there is no traversal surface; temp files are gone right after the response.
- Automated test(s) exist and actually pass.
- `PROJECT_STATUS.md` updated; known limitations documented.
