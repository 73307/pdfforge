"use client";

import Link from "next/link";
import { TOOLS, CATEGORIES, TOOL_CATEGORY, type ToolDef } from "@/lib/tools";
import { useWorkspace, type CatKey } from "./SearchContext";
import { ToolIcon, ArrowRight, Help } from "@/components/icons";

const TABS: { id: CatKey; label: string }[] = [
  { id: "all", label: "All tools" },
  ...CATEGORIES.map((c) => ({ id: c.id as CatKey, label: c.label })),
];

function matches(tool: ToolDef, q: string): boolean {
  if (!q) return true;
  const hay = `${tool.name} ${tool.tagline} ${tool.description}`.toLowerCase();
  return q
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((term) => hay.includes(term));
}

function ToolRow({ tool }: { tool: ToolDef }) {
  return (
    <Link
      href={`/${tool.slug}`}
      className="group flex items-center gap-3.5 rounded-2xl border border-[var(--border)] bg-white px-4 py-3.5 transition hover:border-brand-300 hover:shadow-card"
    >
      <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-ink-50 text-ink-600 transition group-hover:bg-brand-50 group-hover:text-brand-600">
        <ToolIcon name={tool.icon} className="h-[22px] w-[22px]" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[15px] font-bold text-[var(--text)]">{tool.name}</span>
        <span className="block truncate text-sm text-[var(--muted)]">{tool.tagline}</span>
      </span>
      <ArrowRight className="h-4 w-4 shrink-0 text-[var(--muted)] transition group-hover:translate-x-0.5 group-hover:text-brand-600" />
    </Link>
  );
}

export function ToolFinder() {
  const { query, cat, setCat } = useWorkspace();
  // "home" shows every tool, same as "all".
  const activeTab: CatKey = cat === "home" ? "all" : cat;

  const list = TOOLS.filter((t) => (activeTab === "all" ? true : TOOL_CATEGORY[t.slug] === activeTab)).filter(
    (t) => matches(t, query),
  );

  return (
    <section id="find" className="scroll-mt-24">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-xl font-extrabold tracking-tight text-[var(--text)]">Find your tool</h2>
        <div className="flex flex-wrap gap-1 rounded-full border border-[var(--border)] bg-white p-1 shadow-sm">
          {TABS.map((tab) => {
            const active = tab.id === activeTab;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setCat(tab.id)}
                aria-pressed={active}
                className={`rounded-full px-3.5 py-1.5 text-sm font-semibold transition ${
                  active ? "bg-ink-700 text-white shadow-sm" : "text-[var(--muted)] hover:text-[var(--text)]"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {query && (
        <p className="mb-3 text-sm text-[var(--muted)]">
          {list.length} result{list.length === 1 ? "" : "s"} for “{query}”
        </p>
      )}

      {list.length > 0 ? (
        <div className="grid gap-3 md:grid-cols-2">
          {list.map((tool) => (
            <ToolRow key={tool.slug} tool={tool} />
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-[var(--border)] bg-white px-4 py-10 text-center text-sm text-[var(--muted)]">
          No tools match your search. Try “merge”, “compress” or “word”.
        </div>
      )}

      <Link
        href="#top"
        className="mt-3 flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-ink-50/60 px-4 py-3.5 transition hover:border-ink-200"
      >
        <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-ink-600">
          <Help className="h-5 w-5" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-[15px] font-bold text-[var(--text)]">Not sure which tool?</span>
          <span className="block text-sm text-[var(--muted)]">
            Add your file at the top — we’ll suggest the right ones.
          </span>
        </span>
        <span className="hidden shrink-0 items-center gap-1 text-sm font-semibold text-ink-600 sm:inline-flex">
          Start here
          <ArrowRight className="h-4 w-4" />
        </span>
      </Link>
    </section>
  );
}
