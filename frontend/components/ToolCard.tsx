import Link from "next/link";
import type { ToolDef } from "@/lib/tools";
import { ToolIcon } from "./icons";
import { toolColor } from "./toolColors";

export function ToolCard({ tool }: { tool: ToolDef }) {
  const c = toolColor(tool.slug);
  return (
    <Link
      href={`/${tool.slug}`}
      className={`group relative overflow-hidden rounded-3xl border border-[var(--border)] bg-white p-5 shadow-card transition duration-200 hover:-translate-y-1 hover:shadow-glow ${c.hoverBorder}`}
    >
      <span className={`absolute inset-x-0 top-0 h-1.5 ${c.bar}`} />
      <div className={`mb-3 mt-1 inline-flex rounded-2xl ${c.chipBg} ${c.chipText} p-3`}>
        <ToolIcon name={tool.icon} className="h-6 w-6" />
      </div>
      <h3 className="text-[15px] font-bold text-slate-900">{tool.name}</h3>
      <p className="mt-1 text-sm text-slate-500">{tool.tagline}</p>
      <span className={`mt-3 inline-flex items-center gap-1 text-sm font-semibold ${c.chipText}`}>
        Open
        <span className="transition group-hover:translate-x-0.5">→</span>
      </span>
    </Link>
  );
}
