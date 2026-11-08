# PDFForge — Go-Live Security Checklist

A practical checklist for deploying PDFForge to production securely. Work top to bottom;
the 🔴 items are required before you expose the site to the public internet.

> **On "data theft":** PDFForge is **stateless** — no user accounts, no database, and uploaded
> files are processed in an isolated worker and deleted immediately (in production they live on
> a RAM-backed `tmpfs`, never the disk). There is essentially **no stored user data to steal**.
> The real production risks are **denial-of-service (DoS)** and **running outdated dependencies**,
> not data exfiltration. The items below are ordered with that in mind.

---

## ✅ Already handled (no action needed)

These are built into the app and the production Docker/Caddy setup:

- [x] **HTTPS everywhere** with automatic certificates + **HSTS** (Caddy / Let's Encrypt)
- [x] **Containers run as a non-root user** (backend `appuser`, frontend `node`)
- [x] **Sandboxed file processing** — each operation runs in an isolated child process with a hard timeout
- [x] **Upload limits** — per-file size, total request size, PDF page count, and image pixel caps
- [x] **Content validation** — files checked by magic bytes + real parsing, not by extension
- [x] **`tmpfs` temp storage** — processed files never touch disk and are wiped on container restart
- [x] **Restricted CORS** — API only accepts the real frontend origin (`https://DOMAIN`)
- [x] **Strict security headers + CSP** on both frontend and backend
- [x] **Safe error handling** — no stack traces or internal details leak to clients
- [x] **API docs hidden in production** (`/docs`, `/openapi.json` disabled when `APP_ENV=production`)
- [x] **Resource limits** (`mem_limit`, `cpus`) + `no-new-privileges` on containers
- [x] **Edge body-size guard** at Caddy (55 MB) + gzip/zstd + HTTP/3
- [x] **No secrets committed** to the repository (`.env` is gitignored)
- [x] **Rate limiting trusts the proxy correctly** (`TRUST_FORWARDED_FOR=true` in prod compose)

---

## 🔴 Required before going live

- [ ] **Set your domain.** Create a `.env` next to `docker-compose.prod.yml`:
      `echo "DOMAIN=yourdomain.com" > .env`
- [ ] **Point DNS** `yourdomain.com` **and** `api.yourdomain.com` (A/AAAA records) at the server's IP.
- [ ] **Open ports 80 and 443** (TCP + UDP for 443) on the server/firewall so Caddy can get certs and serve HTTPS.
- [ ] **Deploy with the full backend image** (includes LibreOffice + Tesseract):
      `docker compose -f docker-compose.prod.yml up -d --build`
- [ ] **Confirm `APP_ENV=production`** is in effect → visit `https://api.yourdomain.com/docs` and verify it is **404** (docs disabled).
- [ ] **Never commit your production `.env`** (it's already gitignored — keep it that way).
- [ ] **Verify HTTPS + headers** after launch: `curl -sI https://yourdomain.com | grep -i strict-transport-security` should show HSTS.

## 🟡 Strongly recommended

- [ ] **Put a CDN/WAF in front** (e.g. Cloudflare) — biggest practical win against DDoS/bots. Enable "Under Attack" mode if targeted.
- [ ] **Upgrade Next.js** to a patched release to clear the remaining advisories. This is a breaking migration (Next 15 makes `params`/`searchParams` async), so do it on a branch with full testing.
- [ ] **Stronger rate limiting.** The in-memory limiter is per-worker (the backend runs 2 workers) and per-instance, so the real limit is looser than configured and won't hold across replicas. For strict/scaled limits, use **Caddy's `rate_limit`** or a **Redis-backed** limiter.
- [ ] **Error + uptime monitoring** (e.g. Sentry for errors, UptimeRobot/BetterStack for availability).
- [ ] **Finish the legal pages** — replace `support@pdfforge.example` with a real contact, fill in the governing-law jurisdiction, and have a lawyer review for your market (GDPR/CCPA, etc.).

## 🔵 Ongoing

- [ ] Run `npm audit` (frontend) and review Python deps periodically; patch promptly.
- [ ] Keep base images updated (`caddy`, `python:slim`, `node:alpine`) and rebuild.
- [ ] Add server-level abuse handling (e.g. `fail2ban`) and log review.
- [ ] Get a professional **penetration test** before serious scale or handling sensitive documents.

---

## Quick deploy reference

```bash
# 1. Set your domain
echo "DOMAIN=yourdomain.com" > .env

# 2. Point DNS: yourdomain.com + api.yourdomain.com -> server IP

# 3. Build & run the full production stack (frontend + backend + Caddy auto-HTTPS)
docker compose -f docker-compose.prod.yml up -d --build

# 4. Check logs
docker compose -f docker-compose.prod.yml logs -f
```

Frontend → `https://yourdomain.com` · API → `https://api.yourdomain.com`

_Last reviewed: 8 November 2026._
