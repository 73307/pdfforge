import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy",
  description: "How PDFForge handles your files: validated, processed in isolation, and deleted immediately.",
  alternates: { canonical: "/privacy" },
};

export default function Privacy() {
  return (
    <article className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-3xl font-bold">Privacy policy</h1>
      <p className="mt-2 text-sm text-[var(--muted)]">
        This is a starter policy. Review it with a professional before any commercial launch.
      </p>

      <div className="mt-6 space-y-5 text-[var(--text)]">
        <section>
          <h2 className="text-lg font-semibold">What we do with your files</h2>
          <p className="mt-1 text-[var(--muted)]">
            Files you upload are used only to perform the operation you requested. They are written
            to a temporary, per-request location with a random name, processed in an isolated
            worker, streamed back to you, and then deleted immediately. A background sweeper removes
            anything left behind within minutes.
          </p>
        </section>
        <section>
          <h2 className="text-lg font-semibold">What we don&apos;t do</h2>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-[var(--muted)]">
            <li>We don&apos;t require an account and don&apos;t keep a history of your files.</li>
            <li>We don&apos;t read or store the contents of your files beyond processing.</li>
            <li>We don&apos;t sell data. Passwords you enter for encryption are never logged.</li>
          </ul>
        </section>
        <section>
          <h2 className="text-lg font-semibold">Logs</h2>
          <p className="mt-1 text-[var(--muted)]">
            Operational logs may record request metadata (time, status, error type) for reliability
            and abuse prevention. They never contain your file contents.
          </p>
        </section>
        <section>
          <h2 className="text-lg font-semibold">Contact</h2>
          <p className="mt-1 text-[var(--muted)]">
            Questions? Replace this with your real support contact before launch.
          </p>
        </section>
      </div>
    </article>
  );
}
