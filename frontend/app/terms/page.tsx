import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms",
  description: "Terms of use for PDFForge.",
  alternates: { canonical: "/terms" },
};

export default function Terms() {
  return (
    <article className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-3xl font-bold">Terms of use</h1>
      <p className="mt-2 text-sm text-[var(--muted)]">
        Starter terms — replace with reviewed legal text before any commercial launch.
      </p>

      <div className="mt-6 space-y-5 text-[var(--muted)]">
        <section>
          <h2 className="text-lg font-semibold text-[var(--text)]">Acceptable use</h2>
          <p className="mt-1">
            Use the tools only on files you have the right to process. Don&apos;t upload illegal
            content, malware, or attempt to disrupt or probe the service.
          </p>
        </section>
        <section>
          <h2 className="text-lg font-semibold text-[var(--text)]">No warranty</h2>
          <p className="mt-1">
            The service is provided &quot;as is&quot;. PDF conversion and compression results can
            vary by file; we don&apos;t guarantee perfect fidelity for every document.
          </p>
        </section>
        <section>
          <h2 className="text-lg font-semibold text-[var(--text)]">Limits</h2>
          <p className="mt-1">
            File size, page count, and request rate are limited to keep the service reliable for
            everyone.
          </p>
        </section>
      </div>
    </article>
  );
}
