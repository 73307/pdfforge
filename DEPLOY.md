# PDFForge — Deploy with your own domain (step by step)

This guide takes you from nothing to a live, HTTPS website with all 11 tools working,
using a cheap server (VPS) + your own domain. Total time: ~30–45 minutes.
The repo is already configured for this (Docker + Caddy auto-HTTPS).

**What you'll need**
- A domain (~₹700–900 / year)
- A small VPS with **at least 2 GB RAM** (4 GB recommended; the backend bundles LibreOffice + OCR)
- ~₹400–800 / month for the server

---

## Step 1 — Buy a domain

1. Go to a registrar — **Namecheap** (easy) or **Cloudflare Registrar** (cheapest, great DNS).
2. Search a name (e.g. `pdfforge.in`, `mypdftools.com`) and buy it.
3. Keep that tab open — you'll add DNS records in Step 3.

## Step 2 — Create a server (VPS)

Use any provider. Beginner-friendly: **DigitalOcean**. Cheapest: **Hetzner**.

1. Create an account and a new server ("Droplet" on DigitalOcean / "Server" on Hetzner).
2. Choose:
   - **Image/OS:** Ubuntu 24.04 LTS
   - **Size:** at least **2 GB RAM** (DigitalOcean "2 GB / 1 CPU"; Hetzner "CX22 = 4 GB" is great value)
   - **Auth:** set a root password (or add an SSH key if you know how)
3. After it's created, copy the server's **public IP address** (e.g. `203.0.113.45`).

## Step 3 — Point your domain at the server (DNS)

In your registrar's (or Cloudflare's) DNS settings, add two **A records**:

| Type | Name  | Value (your server IP) |
|------|-------|------------------------|
| A    | `@`   | `203.0.113.45`         |
| A    | `api` | `203.0.113.45`         |

- `@` = your root domain (`yourdomain.com`)
- `api` = the API subdomain (`api.yourdomain.com`)

> ⚠️ If you use **Cloudflare**, set these two records to **DNS only (grey cloud)** for now.
> We'll turn on the orange proxy in Step 8, after HTTPS certificates are issued.

DNS can take a few minutes (sometimes up to an hour) to update.

## Step 4 — Connect to the server (SSH)

On your Mac, open Terminal and run (replace with your IP):

```bash
ssh root@203.0.113.45
```

Type `yes` the first time, then the root password. You're now on the server.

## Step 5 — Install Docker

On the server, run:

```bash
curl -fsSL https://get.docker.com | sh
```

Verify:

```bash
docker --version && docker compose version
```

## Step 6 — Open the firewall

```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw --force enable
```

> If your provider has its **own cloud firewall** (DigitalOcean/Hetzner panel), also allow
> ports **22, 80, 443** there.

## Step 7 — Deploy PDFForge

On the server:

```bash
git clone https://github.com/73307/pdfforge.git
cd pdfforge
echo "DOMAIN=yourdomain.com" > .env     # <-- your real domain, no https://
docker compose -f docker-compose.prod.yml up -d --build
```

The first build downloads LibreOffice/Tesseract and takes **~5–10 minutes**. Caddy then
automatically fetches HTTPS certificates for `yourdomain.com` and `api.yourdomain.com`.

Watch the logs until it settles:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

(Press `Ctrl+C` to stop watching — the app keeps running.)

## Step 8 — Check it's live

In your browser:
- `https://yourdomain.com` → your PDFForge site 🎉
- `https://api.yourdomain.com/health` → `{"status":"ok", ...}`
- `https://api.yourdomain.com/docs` → **404** (docs are correctly hidden in production)

If HTTPS doesn't work at first, it's almost always DNS not pointed yet or port 80/443 closed
— see Troubleshooting below.

## Step 9 — (Recommended) Put Cloudflare in front

For free DDoS/bot protection:
1. Add your domain to a free **Cloudflare** account and switch your domain's nameservers to Cloudflare's.
2. Keep the `@` and `api` A records; **first** leave them grey-cloud until Step 8 passes.
3. Then set them to **orange cloud (Proxied)** and set SSL/TLS mode to **Full (strict)**.
4. Turn on "Always Use HTTPS" and a basic rate-limiting/bot rule.

---

## Updating the app later

When you push new changes to GitHub, update the live site with:

```bash
cd pdfforge
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

- **Site won't load / no HTTPS:** DNS not pointed yet (check the A records), or ports 80/443
  closed (check `ufw status` and the provider's cloud firewall). Caddy retries certs automatically.
- **Caddy cert errors in logs:** make sure both `yourdomain.com` and `api.yourdomain.com` resolve
  to the server IP (`dig yourdomain.com +short`) and that Cloudflare proxy is **grey** during first issuance.
- **Backend container restarting / out of memory:** your server has too little RAM — resize to ≥ 2 GB
  (4 GB if you use Word/Excel conversions a lot).
- **Word→PDF / Excel→PDF / OCR fail:** you're on the slim backend. The prod compose already uses
  `Dockerfile.full` (LibreOffice + Tesseract) — rebuild with `--build`.

## Before you call it "launched"

Work through [`GO_LIVE.md`](GO_LIVE.md) — real contact email in the legal pages, monitoring,
and the recommended Next.js upgrade.

_Last updated: 8 November 2026._
