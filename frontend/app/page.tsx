import Link from "next/link";
import { getTool, POPULAR_SLUGS } from "@/lib/tools";
import { ToolIcon, ArrowRight } from "@/components/icons";
import { QuickStart } from "@/components/workspace/QuickStart";
import { ToolFinder } from "@/components/workspace/ToolFinder";

const POPULAR_TINT: Record<string, { wrap: string; chip: string }> = {
  "merge-pdf": { wrap: "bg-emerald-50 hover:border-emerald-300", chip: "bg-emerald-100 text-emerald-700" },
  "compress-pdf": { wrap: "bg-sky-50 hover:border-sky-300", chip: "bg-sky-100 text-sky-700" },
  "pdf-to-word": { wrap: "bg-brand-50 hover:border-brand-300", chip: "bg-brand-100 text-brand-700" },
};

function PopularCard({ slug }: { slug: string }) {
  const tool = getTool(slug);
  if (!tool) return null;
  const tint = POPULAR_TINT[slug] ?? POPULAR_TINT["merge-pdf"];
  return (
    <Link
      href={`/${tool.slug}`}
      className={`group flex items-center gap-4 rounded-2xl border border-transparent p-5 transition hover:shadow-card ${tint.wrap}`}
    >
      <span className={`inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${tint.chip}`}>
        <ToolIcon name={tool.icon} className="h-6 w-6" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-[15px] font-bold text-[var(--text)]">{tool.name}</span>
        <span className="block truncate text-sm text-[var(--muted)]">{tool.tagline}</span>
      </span>
      <ArrowRight className="h-5 w-5 shrink-0 text-[var(--muted)] transition group-hover:translate-x-0.5 group-hover:text-[var(--text)]" />
    </Link>
  );
}

export default function Home() {
  return (
    <div id="top" className="mx-auto max-w-6xl space-y-9 px-4 py-7 sm:px-6 lg:px-8">
      <header>
        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--text)] sm:text-[34px]">
          What would you like to do?
        </h1>
        <p className="mt-1.5 text-[var(--muted)]">Simple tools for your everyday PDF tasks.</p>
      </header>

      <QuickStart />

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-extrabold tracking-tight text-[var(--text)]">Popular tools</h2>
          <Link
            href="/?cat=all#find"
            className="inline-flex items-center gap-1 text-sm font-semibold text-ink-600 hover:text-brand-600"
          >
            View all tools
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {POPULAR_SLUGS.map((slug) => (
            <PopularCard key={slug} slug={slug} />
          ))}
        </div>
      </section>

      <ToolFinder />
    </div>
  );
}
