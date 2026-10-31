# Security model — "hard to break" by design

No application is literally 100% unbreakable, but PDFForge applies **defense in depth**
so the realistic attacks against a file-upload tool are blocked at multiple layers.

## Threats considered & mitigations

| Threat | Mitigation |
|---|---|
| Malicious file disguised by extension | Content sniffing (magic bytes) **and** a real parse by pypdf/Pillow before processing. Extension & client filename are ignored for logic. |
| Path traversal via filename (`../../etc/passwd`) | Client filenames are never used for storage or paths. Storage names are random tokens inside a per-request random working dir. The result is **streamed directly** as the HTTP response (there is no download-by-path endpoint to attack); the suggested download filename is server-generated and header-sanitized. |
| Oversized uploads / DoS | Hard request-body cap (middleware), per-file cap, max files per request, max PDF pages, max image pixels. Reads are capped while streaming. |
| Decompression / zip bombs, huge renders | Page-count and pixel-count limits; render DPI bounded; per-op wall-clock timeout. |
| Resource exhaustion / long jobs | Each operation runs under a timeout; the worker process is killed if exceeded. |
| Information leakage | Global exception handler returns a generic message + request id. No stack traces, no server paths, no library internals reach the client. Logs never store file bytes. |
| Cross-site abuse | CORS limited to the configured frontend origin; strict security headers (CSP, X-Frame-Options=DENY, X-Content-Type-Options=nosniff, Referrer-Policy, Permissions-Policy). |
| Brute force / spam | In-memory sliding-window rate limit per client IP (swap for Redis in production). |
| Data retention / privacy | The per-request working dir (inputs + output) is deleted immediately after the response via a background task; a sweeper removes any orphaned dir older than the retention window. Nothing persists between requests. |
| Password tooling misuse | Protect only **adds** AES encryption. No unlock/bypass feature is provided. |

## Hardening checklist (Phase 6)
- [x] Request body size middleware
- [x] Per-file + per-request limits
- [x] Magic-byte + parse validation
- [x] Random server-side filenames
- [x] Direct-stream results (no download-by-path endpoint) + immediate temp cleanup
- [x] Per-operation timeout (separate process)
- [x] Rate limiting per IP
- [x] Security headers middleware
- [x] Locked-down CORS
- [x] Generic error responses + request id
- [x] Automatic cleanup (success/failure) + retention sweeper
- [x] Logging without file contents
- [ ] *(Production)* WAF / CDN, object storage with private ACLs, secret manager, HTTPS/HSTS at the edge

## Production notes
- Terminate TLS at the edge and enable HSTS.
- Put the backend behind a reverse proxy that also enforces body-size limits.
- Replace in-memory rate limiting with Redis so limits hold across replicas.
- Run the processing worker as a low-privilege user in a container with a read-only
  root filesystem and a tmpfs for the data dir; set CPU/memory cgroup limits.
