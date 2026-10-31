// Per-tool accent colours. Full literal class strings so Tailwind keeps them.

export interface ToolColor {
  chipBg: string;
  chipText: string;
  bar: string;
  hoverBorder: string;
}

export const TOOL_COLORS: Record<string, ToolColor> = {
  "merge-pdf": { chipBg: "bg-violet-100", chipText: "text-violet-600", bar: "bg-violet-500", hoverBorder: "hover:border-violet-300" },
  "split-pdf": { chipBg: "bg-sky-100", chipText: "text-sky-600", bar: "bg-sky-500", hoverBorder: "hover:border-sky-300" },
  "rotate-pdf": { chipBg: "bg-amber-100", chipText: "text-amber-600", bar: "bg-amber-500", hoverBorder: "hover:border-amber-300" },
  "images-to-pdf": { chipBg: "bg-emerald-100", chipText: "text-emerald-600", bar: "bg-emerald-500", hoverBorder: "hover:border-emerald-300" },
  "pdf-to-images": { chipBg: "bg-rose-100", chipText: "text-rose-600", bar: "bg-rose-500", hoverBorder: "hover:border-rose-300" },
  "compress-pdf": { chipBg: "bg-cyan-100", chipText: "text-cyan-600", bar: "bg-cyan-500", hoverBorder: "hover:border-cyan-300" },
  "protect-pdf": { chipBg: "bg-indigo-100", chipText: "text-indigo-600", bar: "bg-indigo-500", hoverBorder: "hover:border-indigo-300" },
  "pdf-to-word": { chipBg: "bg-blue-100", chipText: "text-blue-600", bar: "bg-blue-500", hoverBorder: "hover:border-blue-300" },
  "word-to-pdf": { chipBg: "bg-fuchsia-100", chipText: "text-fuchsia-600", bar: "bg-fuchsia-500", hoverBorder: "hover:border-fuchsia-300" },
  "excel-to-pdf": { chipBg: "bg-green-100", chipText: "text-green-600", bar: "bg-green-500", hoverBorder: "hover:border-green-300" },
  "ocr-pdf": { chipBg: "bg-orange-100", chipText: "text-orange-600", bar: "bg-orange-500", hoverBorder: "hover:border-orange-300" },
};

export const DEFAULT_COLOR: ToolColor = {
  chipBg: "bg-violet-100",
  chipText: "text-violet-600",
  bar: "bg-violet-500",
  hoverBorder: "hover:border-violet-300",
};

export function toolColor(slug: string): ToolColor {
  return TOOL_COLORS[slug] ?? DEFAULT_COLOR;
}
