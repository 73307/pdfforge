import Link from "next/link";
import type { ToolDef } from "@/lib/tools";
import { ToolIcon } from "./icons";

export function ToolCard({ tool }: { tool: ToolDef }) {
  return (
    <Link
      href={`/${tool.slug}`}
      className="group rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-card transition hover:-translate-y-0.5 hover:border-brand-300"
    >
      <div className="mb-3 inline-flex rounded-xl bg-brand-50 p-2.5 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300">
        <ToolIcon name={tool.icon} className="h-6 w-6" />
      </div>
      <h3 className="font-semibold">{tool.name}</h3>
      <p className="mt-1 text-sm text-[var(--muted)]">{tool.tagline}</p>
      <span className="mt-3 inline-block text-sm font-medium text-brand-600 group-hover:underline dark:text-brand-400">
        Open tool →
      </span>
    </Link>
  );
}
