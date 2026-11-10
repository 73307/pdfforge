/** @type {import('next').NextConfig} */

const isProd = process.env.NODE_ENV === "production";

// Allow XHR/fetch to the backend API origin (and the HMR socket in dev).
let apiOrigin = "";
try {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    apiOrigin = new URL(process.env.NEXT_PUBLIC_API_BASE_URL).origin;
  }
} catch {
  apiOrigin = "";
}

const connectSrc = ["'self'", apiOrigin, isProd ? "" : "ws: http://localhost:* http://127.0.0.1:*"]
  .filter(Boolean)
  .join(" ");

// A Content-Security-Policy that works with Next.js. Scripts/styles need 'unsafe-inline'
// because Next injects inline bootstrap; everything else is locked down. Dev also needs
// 'unsafe-eval' for React Fast Refresh.
const csp = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${isProd ? "" : " 'unsafe-eval'"}`,
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
  "font-src 'self' https://fonts.gstatic.com data:",
  "img-src 'self' data: blob:",
  `connect-src ${connectSrc}`,
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
  // The result page previews PDFs in an <iframe> that points at an in-memory blob URL.
  "frame-src 'self' blob:",
  "worker-src 'self' blob:",
  "manifest-src 'self'",
  ...(isProd ? ["upgrade-insecure-requests"] : []),
].join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: csp },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-DNS-Prefetch-Control", value: "off" },
  { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
  {
    key: "Permissions-Policy",
    value: "geolocation=(), microphone=(), camera=(), payment=(), usb=(), interest-cohort=()",
  },
  // HSTS is honoured only over HTTPS; harmless over http during local dev.
  ...(isProd
    ? [{ key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" }]
    : []),
];

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Hide the Next.js dev-mode "N" indicator (dev only; never shows in production).
  devIndicators: false,
  // Serve our (small, local) images directly and skip the Next image optimizer, which
  // removes the /_next/image endpoint and its known DoS attack surface on self-hosted apps.
  images: { unoptimized: true },
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
