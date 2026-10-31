# Deploying PDFForge to production

Two routes are documented:

- **Option 1 — One server + Docker Compose + Caddy (recommended).** Everything (frontend,
  backend with conversion/OCR tools, and automatic HTTPS) on a single VPS. Copy-paste friendly.
- **Option 2 — Split hosting.** Frontend on a static/Next host (Vercel/Netlify), backend on a
  container host (Fly.io / Render / Railway / your own box).

What you'll end up with (Option 1):

```
                 Internet (HTTPS)
                       │
                 ┌─────▼─────┐   :443   automatic Let's Encrypt certs
                 │   Caddy   │
                 └──┬─────┬──┘
     yourdomain.com │     │ api.yourdomain.com
            ┌───────▼┐   ┌▼────────┐
            │frontend│   │ backend │  (LibreOffice + Tesseract inside)
            │ :3000  │   │  :8000  │  temp files in RAM (tmpfs), auto-deleted
            └────────┘   └─────────┘
```

---

## Option 1 — One server with Docker Compose + Caddy

### Prerequisites
- A Linux server (a 2 vCPU / 4 GB VPS is a good start — LibreOffice needs RAM).
- A domain name you control.
- Docker + the Compose plugin installed on the server:
  ```bash
  curl -fsSL https://get.docker.com | sh
  ```

### 1. Point DNS at the server
Create two DNS records pointing at your server's public IP:
- `yourdomain.com`        → `A` (and `AAAA` if you have IPv6)
- `api.yourdomain.com`    → `A` (and `AAAA`)

Wait for them to resolve (`dig +short yourdomain.com`). Caddy needs this working to issue certs.

### 2. Get the code onto the server
```bash
git clone <your-repo-url> pdfforge && cd pdfforge
```
(or `scp`/`rsync` the `pdf-converter/` folder up). All commands below run from the folder that
contains `docker-compose.prod.yml`.

### 3. Configure the domain
```bash
echo "DOMAIN=yourdomain.com" > .env
```
That single variable drives the frontend's API URL, the backend's CORS allow-list, and Caddy's
certificate domains. No secrets are needed — PDFForge is stateless and has no database/keys.

### 4. Build & launch
```bash
docker compose -f docker-compose.prod.yml up -d --build
```
First build takes a while (it installs LibreOffice + Tesseract into the backend image). Watch logs:
```bash
docker compose -f docker-compose.prod.yml logs -f
```

### 5. Verify
```bash
curl -s https://api.yourdomain.com/health
```
Expected: `{"status":"ok", ...}`. Then open `https://yourdomain.com` in a browser and run a tool.
Confirm the conversion tools work inside the container:
```bash
docker compose -f docker-compose.prod.yml exec backend soffice --version
docker compose -f docker-compose.prod.yml exec backend tesseract --version
```

### 6. Updates & rollback
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```
Rollback = check out the previous commit/tag and run the same command. There's no database to
migrate. Keep the previous image tag if you want an instant revert.

---

## Option 2 — Split hosting

Good if you want a managed frontend and to scale the backend separately.

**Frontend (Vercel / Netlify / Cloudflare Pages):**
- Project root: `frontend/`
- Build: `npm run build`, output handled by the platform's Next.js support.
- Set env var `NEXT_PUBLIC_API_BASE_URL = https://api.yourdomain.com` (your backend's public URL).

**Backend (Fly.io / Render / Railway / a VPS):**
- Build from `backend/Dockerfile.full` (so LibreOffice + Tesseract are included).
- Set env vars:
  - `APP_ENV=production`
  - `CORS_ALLOW_ORIGINS=https://yourdomain.com` (your frontend's public origin — this is what
    allows the browser to call the API).
  - `DATA_DIR=/data` on a writable (ideally tmpfs/ephemeral) path.
- Expose port 8000 behind the platform's HTTPS/load balancer.
- Give it ≥ 1–2 GB RAM for LibreOffice.

The only wiring between the two: the frontend's `NEXT_PUBLIC_API_BASE_URL` must point at the
backend, and the backend's `CORS_ALLOW_ORIGINS` must list the frontend origin.

---

## Continuous integration & deployment (GitHub Actions)

Two workflows live in `.github/workflows/`:

- **`ci.yml`** — on every push to `main` and every PR: backend `pytest` + frontend type-check
  and production build. Your quality gate (and the first real compile of the frontend in CI).
- **`deploy.yml`** — on a version tag (`v*`) or manual run: SSHes to your server, checks out the
  tag, and runs `docker compose -f docker-compose.prod.yml up -d --build`. **Dormant until
  configured**, so it's safe to commit.

### One-time setup
1. Do the Option 1 steps on the server once (clone the repo at a path, create `.env` with
   `DOMAIN=...`, install Docker).
2. In GitHub → **Settings → Secrets and variables → Actions**:

   | Kind | Name | Value |
   |---|---|---|
   | Variable | `DEPLOY_SSH_HOST` | server IP / hostname |
   | Variable | `DEPLOY_SSH_USER` | SSH user (e.g. `deploy`) |
   | Variable | `DEPLOY_PATH` | path to the repo on the server |
   | Variable | `DEPLOY_SSH_PORT` | optional, defaults to 22 |
   | Secret | `DEPLOY_SSH_KEY` | a private SSH key whose public key is in the server's `~/.ssh/authorized_keys` |

### Release
```bash
git tag v1.0.0
git push origin v1.0.0
```
Actions rebuilds and restarts the stack on the server. Roll back by deploying an earlier tag.

> Optional (faster deploys on a small box): have CI build & push images to GHCR and pull them on
> the server instead of building the ~1.3 GB backend image there. Not required to start.

## Production security checklist

- [x] **HTTPS everywhere** — Caddy issues/renews certs automatically; HSTS is set.
- [x] **Secrets** — none required; never bake real secrets into images. If you later add any
      (e.g. S3), inject them as runtime env vars / a secret manager, not in the image.
- [x] **CORS locked** to your real frontend origin (`CORS_ALLOW_ORIGINS`).
- [x] **Edge body limit** — Caddy caps request bodies at 55 MB (app caps at 50 MB).
- [x] **Non-root containers**, `no-new-privileges`, and **tmpfs** for temp files (nothing
      touches disk; everything auto-deletes after each response).
- [x] **Resource caps** (`mem_limit`, `cpus`) so a heavy job can't starve the host.
- [x] **Rate limiting** on by default (per IP). For multiple backend replicas, move the limiter
      to Redis (see `docs/SECURITY.md`) so limits hold across instances.
- [ ] **Backups** — not needed; the service stores nothing. (Only Caddy's cert volume persists.)
- [ ] **Monitoring** — point your uptime monitor at `GET /health`; ship container logs to your
      log stack. Logs never contain file contents.

## Scaling notes
- The backend processes synchronously under a timeout. For high traffic or very large files,
  introduce the Phase 7 async queue (job id + Redis/Celery worker + object storage) so web
  requests don't wait. Until then, scale by running more backend replicas behind Caddy and
  moving rate-limit state to Redis.
- LibreOffice is the heaviest tool; give the backend enough RAM and CPU, or run a separate
  "conversions" backend with its own limits.

## Rough cost
A single small VPS (2 vCPU / 4 GB) is typically enough to start and runs ~a few dollars to
~$20–40/month depending on provider. The app itself has no per-file infrastructure cost beyond
CPU/RAM time (no storage, no database in the MVP).
