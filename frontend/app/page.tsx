import { getTool, TOOLS } from "@/lib/tools";
import { ToolCard } from "@/components/ToolCard";
import { ToolIcon, Upload, Shield, Trash, Spinner } from "@/components/icons";
import { toolColor } from "@/components/toolColors";

const CATEGORIES = [
  { label: "Organize", slugs: ["merge-pdf", "split-pdf", "rotate-pdf"] },
  {
    label: "Convert",
    slugs: ["images-to-pdf", "pdf-to-images", "pdf-to-word", "word-to-pdf", "excel-to-pdf", "ocr-pdf"],
  },
  { label: "Optimize & secure", slugs: ["compress-pdf", "protect-pdf"] },
];

const FEATURES = [
  {
    icon: <Shield className="h-5 w-5" />,
    title: "Secure by design",
    body: "Content is validated, processing is sandboxed and time-limited, and nothing internal leaks out.",
    tint: "bg-violet-100 text-violet-600",
  },
  {
    icon: <Trash className="h-5 w-5" />,
    title: "Nothing is kept",
    body: "Your file and its result are deleted the moment the download is sent. No account, no history.",
    tint: "bg-rose-100 text-rose-600",
  },
  {
    icon: <Spinner className="h-5 w-5" />,
    title: "Honest results",
    body: "Real progress, clear errors, and we tell you when something (like compression) can't improve.",
    tint: "bg-emerald-100 text-emerald-600",
  },
];

function FloatingBadge({ slug, className }: { slug: string; className?: string }) {
  const tool = getTool(slug);
  const c = toolColor(slug);
  if (!tool) return null;
  return (
    <div className={`absolute ${className} rounded-2xl border border-[var(--border)] bg-white p-2.5 shadow-card`}>
      <span className={`inline-flex rounded-xl ${c.chipBg} ${c.chipText} p-2`}>
        <ToolIcon name={tool.icon} className="h-5 w-5" />
      </span>
    </div>
  );
}

function HeroVisual() {
  const rows: [string, string, string][] = [
    ["report.pdf", "2.1 MB", "bg-violet-500"],
    ["invoice.pdf", "0.8 MB", "bg-sky-500"],
  ];
  return (
    <div className="relative mx-auto hidden w-full max-w-sm lg:block">
      <div className="rotate-2 rounded-3xl border border-[var(--border)] bg-white p-5 shadow-glow">
        <div className="flex items-center justify-between">
          <span className="text-sm font-bold text-slate-900">Merge PDF</span>
          <span className="rounded-full bg-violet-100 px-2 py-0.5 text-xs font-semibold text-violet-600">
            2 files
          </span>
        </div>
        <div className="mt-3 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-violet-200 bg-violet-50/60 py-6 text-center">
          <span className="inline-flex rounded-full bg-violet-100 p-2.5 text-violet-600">
            <Upload className="h-5 w-5" />
          </span>
          <p className="mt-2 text-sm font-semibold text-slate-700">Drop your PDF here</p>
          <p className="text-xs text-slate-400">or click to choose</p>
        </div>
        <div className="mt-3 space-y-2">
          {rows.map(([name, size, dot]) => (
            <div
              key={name}
              className="flex items-center gap-2 rounded-xl border border-[var(--border)] px-3 py-2"
            >
              <span className={`h-2 w-2 rounded-full ${dot}`} />
              <span className="flex-1 truncate text-sm text-slate-700">{name}</span>
              <span className="text-xs text-slate-400">{size}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 w-full rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 py-2.5 text-center text-sm font-semibold text-white shadow-md">
          Merge PDF →
        </div>
      </div>

      <FloatingBadge slug="rotate-pdf" className="-left-7 top-8 -rotate-6" />
      <FloatingBadge slug="protect-pdf" className="-right-6 top-24 rotate-6" />
      <FloatingBadge slug="images-to-pdf" className="-left-5 bottom-10 rotate-3" />
    </div>
  );
}

export default function Home() {
  return (
    <>
      {/* Hero — asymmetric */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-24 left-[8%] h-72 w-72 rounded-full bg-violet-300/50 blur-3xl" />
          <div className="absolute top-0 right-[10%] h-72 w-72 rounded-full bg-fuchsia-300/40 blur-3xl" />
          <div className="absolute top-40 left-1/3 h-56 w-56 rounded-full bg-amber-200/40 blur-3xl" />
        </div>

        <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 pb-12 pt-16 lg:grid-cols-2">
          <div className="text-center lg:text-left">
            <span className="inline-flex items-center gap-2 rounded-full border border-violet-200 bg-white/70 px-3.5 py-1.5 text-xs font-semibold text-violet-700 shadow-sm backdrop-blur">
              <Shield className="h-3.5 w-3.5" />
              Private · No login · Auto-deleted
            </span>
            <h1 className="mt-6 text-5xl font-extrabold leading-[1.03] tracking-tight text-slate-900 sm:text-6xl">
              Fix any PDF in{" "}
              <span className="bg-gradient-to-r from-violet-600 via-fuchsia-500 to-orange-400 bg-clip-text text-transparent">
                seconds.
              </span>
            </h1>
            <p className="mx-auto mt-5 max-w-md text-lg text-slate-600 lg:mx-0">
              Merge, split, convert, compress and protect — right in your browser. No uploads kept,
              no account, no clutter.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3 lg:justify-start">
              <a
                href="#tools"
                className="rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 px-6 py-3 font-semibold text-white shadow-md transition hover:shadow-glow"
              >
                Browse tools
              </a>
              <a
                href="/privacy"
                className="rounded-full border border-[var(--border)] bg-white px-6 py-3 font-semibold text-slate-700 transition hover:border-violet-300 hover:text-violet-700"
              >
                How we protect files
              </a>
            </div>
            <div className="mt-6 flex flex-wrap justify-center gap-x-5 gap-y-1 text-sm text-slate-400 lg:justify-start">
              <span>✦ {TOOLS.length} free tools</span>
              <span>✦ No sign-up</span>
              <span>✦ Files auto-deleted</span>
            </div>
          </div>

          <HeroVisual />
        </div>
      </section>

      {/* Tools grouped by category */}
      <section id="tools" className="mx-auto max-w-6xl scroll-mt-20 px-4 pt-4">
        {CATEGORIES.map((cat) => (
          <div key={cat.label} className="mb-12">
            <div className="mb-4 flex items-center gap-4">
              <h2 className="text-lg font-extrabold tracking-tight text-slate-900">{cat.label}</h2>
              <span className="h-px flex-1 bg-[var(--border)]" />
              <span className="text-xs font-medium text-slate-400">{cat.slugs.length} tools</span>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {cat.slugs.map((slug) => {
                const tool = getTool(slug);
                return tool ? <ToolCard key={slug} tool={tool} /> : null;
              })}
            </div>
          </div>
        ))}
      </section>

      {/* Why */}
      <section className="mx-auto max-w-6xl px-4">
        <div className="grid gap-5 rounded-3xl border border-[var(--border)] bg-gradient-to-br from-violet-50 via-white to-fuchsia-50 p-7 sm:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="flex gap-3">
              <div
                className={`mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${f.tint}`}
              >
                {f.icon}
              </div>
              <div>
                <h3 className="font-bold text-slate-900">{f.title}</h3>
                <p className="mt-1 text-sm text-slate-600">{f.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
