import * as React from "react";

type SvgProps = React.SVGProps<SVGSVGElement>;

function Svg(props: SvgProps) {
  return (
    <svg
      width={24}
      height={24}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    />
  );
}

export function Logo({ className }: { className?: string }) {
  return (
    <svg className={className} width={30} height={30} viewBox="0 0 32 32" aria-hidden="true">
      <defs>
        <linearGradient id="pf-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#6366f1" />
          <stop offset="1" stopColor="#4338ca" />
        </linearGradient>
      </defs>
      <rect x="4" y="2" width="20" height="26" rx="4" fill="url(#pf-g)" />
      <rect x="8" y="6" width="20" height="26" rx="4" fill="#a5b4fc" opacity="0.35" />
      <path d="M14 13l4 4-4 4" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </svg>
  );
}

const PATHS: Record<string, React.ReactNode> = {
  merge: (
    <>
      <rect x="3" y="4" width="8" height="11" rx="1.5" />
      <rect x="13" y="9" width="8" height="11" rx="1.5" />
      <path d="M11 9h2" />
    </>
  ),
  split: (
    <>
      <rect x="4" y="3" width="12" height="16" rx="1.5" />
      <path d="M9 3v16" strokeDasharray="2 2" />
      <path d="M18 8l3 3-3 3" />
    </>
  ),
  rotate: (
    <>
      <path d="M21 12a9 9 0 1 1-2.64-6.36" />
      <path d="M21 3v4h-4" />
    </>
  ),
  image: (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="8.5" cy="9" r="1.5" />
      <path d="M21 16l-5-5L5 20" />
    </>
  ),
  fileImage: (
    <>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5" />
      <circle cx="10" cy="13" r="1.2" />
      <path d="M8 18l3-3 2 2 2-2 2 3" />
    </>
  ),
  compress: (
    <>
      <path d="M9 3H5a2 2 0 0 0-2 2v4M15 3h4a2 2 0 0 1 2 2v4M9 21H5a2 2 0 0 1-2-2v-4M15 21h4a2 2 0 0 0 2-2v-4" />
      <path d="M8 12h8" />
    </>
  ),
  lock: (
    <>
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
      <circle cx="12" cy="15.5" r="1.2" />
    </>
  ),
  word: (
    <>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5" />
      <path d="M8.5 12l1.2 5 1.3-3.5L12.3 17l1.2-5" />
    </>
  ),
  excel: (
    <>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5" />
      <path d="M9 12l4 5M13 12l-4 5" />
    </>
  ),
  ocr: (
    <>
      <path d="M4 8V6a2 2 0 0 1 2-2h2M16 4h2a2 2 0 0 1 2 2v2M20 16v2a2 2 0 0 1-2 2h-2M8 20H6a2 2 0 0 1-2-2v-2" />
      <path d="M8 10h8M8 13h8M8 16h5" />
    </>
  ),
};

export function ToolIcon({ name, className }: { name: string; className?: string }) {
  return <Svg className={className}>{PATHS[name] ?? PATHS.merge}</Svg>;
}

export const Upload = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M12 15V3M7 8l5-5 5 5" />
    <path d="M5 21h14a0 0 0 0 0 0 0" />
    <path d="M5 15v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />
  </Svg>
);

export const Download = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M12 3v12M7 10l5 5 5-5" />
    <path d="M5 15v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />
  </Svg>
);

export const Trash = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M4 7h16M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2m-9 0 1 13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l1-13" />
  </Svg>
);

export const ArrowUp = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M12 19V5M6 11l6-6 6 6" />
  </Svg>
);

export const ArrowDown = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M12 5v14M6 13l6 6 6-6" />
  </Svg>
);

export const Shield = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z" />
    <path d="M9 12l2 2 4-4" />
  </Svg>
);

export const Check = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M20 6L9 17l-5-5" />
  </Svg>
);

export const Alert = (p: SvgProps) => (
  <Svg {...p}>
    <path d="M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
  </Svg>
);

export const Spinner = ({ className }: { className?: string }) => (
  <svg
    className={`animate-spin ${className ?? ""}`}
    width={20}
    height={20}
    viewBox="0 0 24 24"
    fill="none"
    aria-hidden="true"
  >
    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="3" opacity="0.25" />
    <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
  </svg>
);
