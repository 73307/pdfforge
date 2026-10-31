import { TOOLS } from "@/lib/tools";
import { ToolCard } from "@/components/ToolCard";
import { Shield, Trash, Spinner } from "@/components/icons";

const FEATURES = [
  {
    icon: <Shield className="h-5 w-5" />,
    title: "Secure by design",
    body: "Content is validated, processing is sandboxed and time-limited, and no server paths or errors leak out.",
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
    body: "Real progress, clear errors, and we tell you when something (like compression) can't be improved.",
    tint: "bg-emerald-100 text-emerald-600",
  },
];

export default function Home() {
  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-24 left-[15%] h-72 w-72 rounded-full bg-violet-300/50 blur-3xl" />
          <div className="absolute -top-10 right-[12%] h-72 w-72 rounded-full bg-fuchsia-300/50 blur-3xl" />
          <div className="absolute top-20 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-sky-200/50 blur-3xl" />
        </div>

        <div className="mx-auto max-w-6xl px-4 pb-10 pt-16 text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-violet-200 bg-white/70 px-3.5 py-1.5 text-xs font-semibold text-violet-700 shadow-sm backdrop-blur">
            <Shield className="h-3.5 w-3.5" />
            Private · No login · Auto-deleted
          </span>
          <h1 className="mx-auto mt-6 max-w-3xl text-5xl font-extrabold leading-[1.05] tracking-tight text-slate-900 sm:text-6xl">
            Every PDF tool,
            <br />
            <span className="bg-gradient-to-r from-violet-600 via-fuchsia-500 to-orange-400 bg-clip-text text-transparent">
              bright and simple.
            </span>
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-lg text-slate-600">
            Merge, split, rotate, convert, compress and protect PDFs in seconds — right in your
            browser, with security built in.
          </p>
          <div className="mt-8 flex justify-center gap-3">
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
        </div>
      </section>

      {/* Tools */}
      <section id="tools" className="mx-auto max-w-6xl scroll-mt-20 px-4">
        <div className="mb-5 flex items-end justify-between">
          <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">All tools</h2>
          <span className="text-sm font-medium text-slate-400">{TOOLS.length} tools · free</span>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {TOOLS.map((tool) => (
            <ToolCard key={tool.slug} tool={tool} />
          ))}
        </div>
      </section>

      {/* Why */}
      <section className="mx-auto mt-16 max-w-6xl px-4">
        <div className="grid gap-5 rounded-3xl border border-[var(--border)] bg-gradient-to-br from-violet-50 to-white p-7 sm:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="flex gap-3">
              <div className={`mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${f.tint}`}>
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
