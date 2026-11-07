// Compact PDFForge mark — an orange document tile with a white "F" and a spark.
// Drawn inline so it stays crisp on the dark sidebar at any size.
export function BrandMark({ className }: { className?: string }) {
  return (
    <svg className={className} width={40} height={40} viewBox="0 0 40 40" aria-hidden="true">
      <defs>
        <linearGradient id="pf-mark" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f97a3c" />
          <stop offset="0.55" stopColor="#f75f22" />
          <stop offset="1" stopColor="#e64e12" />
        </linearGradient>
      </defs>
      {/* document tile with a folded top-right corner */}
      <path
        d="M9 5.5A3.5 3.5 0 0 1 12.5 2H25l7 7v22.5A3.5 3.5 0 0 1 28.5 35h-16A3.5 3.5 0 0 1 9 31.5z"
        fill="url(#pf-mark)"
      />
      <path d="M25 2v4.5A2.5 2.5 0 0 0 27.5 9H32z" fill="#fff" opacity="0.28" />
      {/* bold F */}
      <path
        d="M15.3 13.2h10.2v3.4h-6.4v3h5.5v3.3h-5.5v6.1h-3.8z"
        fill="#fff"
      />
      {/* spark */}
      <path
        d="M30 10.2l.8 2.1 2.1.8-2.1.8-.8 2.1-.8-2.1-2.1-.8 2.1-.8z"
        fill="#ffd9c2"
      />
    </svg>
  );
}
