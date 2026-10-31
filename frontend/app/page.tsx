import { TOOLS } from "@/lib/tools";
import { ToolCard } from "@/components/ToolCard";
import { Shield, Trash, Spinner } from "@/components/icons";

const FEATURES = [
  {
    icon: <Shield className="h-5 w-5" />,
    title: "Secure by design",
    body: "Content is validated, processing is sandboxed and time-limited, and no server paths or errors leak out.",
  },
  {
    icon: <Trash className="h-5 w-5" />,
    title: "Nothing is kept",
    body: "Your file and its result are deleted the moment the download is sent. No account, no history.",
  },
  {
    icon: <Spinner className="h-5 w-5" />,
    title: "Honest results",
    body: "Real progress, clear errors, and we tell you when something (like compression) can't be improved.",
  },
];

export default function Home() {
  return (
    <>
      <section className="mx-auto max-w-6xl px-4 pb-10 pt-14 text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-xs font-medium text-[var(--muted)]">
          <Shield className="h-3.5 w-3.5 text-brand-600" />
          Private · No login · Auto-deleted
        </span>
        <h1 className="mx-auto mt-5 max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl">
          Every PDF tool you need, <span className="text-brand-600 dark:text-brand-400">in one place</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-[var(--muted)]">
          Merge, split, rotate, convert, compress and protect PDFs in seconds — all in your
          browser, with security built in from the ground up.
        </p>
        <div className="mt-7 flex justify-center gap-3">
          <a
            href="#tools"
            className="rounded-xl bg-brand-600 px-5 py-2.5 font-medium text-white hover:bg-brand-700"
          >
            Browse tools
          </a>
          <a
            href="/privacy"
            className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-5 py-2.5 font-medium hover:border-brand-300"
          >
            How we protect your files
          </a>
        </div>
      </section>

      <section id="tools" className="mx-auto max-w-6xl scroll-mt-20 px-4">
        <h2 className="mb-4 text-xl font-semibold">All tools</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {TOOLS.map((tool) => (
            <ToolCard key={tool.slug} tool={tool} />
          ))}
        </div>
      </section>

      <section className="mx-auto mt-14 max-w-6xl px-4">
        <div className="grid gap-4 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 sm:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="flex gap-3">
              <div className="mt-0.5 text-brand-600 dark:text-brand-400">{f.icon}</div>
              <div>
                <h3 className="font-semibold">{f.title}</h3>
                <p className="mt-1 text-sm text-[var(--muted)]">{f.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
