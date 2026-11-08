import type { Metadata } from "next";
import Link from "next/link";
import { Shield } from "@/components/icons";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description:
    "PDFForge processes your documents without collecting personal data: files are handled in isolation and deleted immediately, with no accounts and no tracking cookies.",
  alternates: { canonical: "/privacy" },
};

const UPDATED = "8 November 2026";

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-24">
      <h2 className="text-lg font-bold tracking-tight text-[var(--text)]">{title}</h2>
      <div className="mt-2 space-y-2 text-[var(--muted)]">{children}</div>
    </section>
  );
}

export default function Privacy() {
  return (
    <article className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <header>
        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--text)] sm:text-4xl">
          Privacy Policy
        </h1>
        <p className="mt-2 text-sm text-[var(--muted)]">Last updated: {UPDATED}</p>
        <p className="mt-4 text-[var(--muted)]">
          PDFForge is built to process your documents without collecting or keeping personal data.
          This policy explains, in plain language, exactly what happens to the files you upload and
          what limited information we handle to keep the service running.
        </p>
      </header>

      {/* TL;DR */}
      <div className="mt-6 rounded-2xl border border-[var(--border)] bg-white p-5 shadow-card">
        <div className="mb-2 flex items-center gap-2 font-bold text-[var(--text)]">
          <Shield className="h-5 w-5 text-ink-600" />
          The short version
        </div>
        <ul className="list-disc space-y-1 pl-5 text-sm text-[var(--muted)]">
          <li>No account, no sign-up, and no history of what you process.</li>
          <li>Your files are processed on our own servers and deleted the moment you get the result.</li>
          <li>We don&apos;t use tracking cookies, analytics, or advertising of any kind.</li>
          <li>Passwords you set for encryption are used in memory only — never logged or stored.</li>
        </ul>
      </div>

      <div className="mt-8 space-y-7">
        <Section id="files" title="1. The files you upload">
          <p>
            Files are used only to perform the operation you asked for. Each upload is written to a
            temporary, per-request location with a random name, processed in an isolated worker with
            a strict time limit, streamed back to your browser, and then deleted immediately. A
            background sweeper removes anything left behind (for example, after an interrupted
            request) within minutes.
          </p>
          <p>
            All conversions run on our own infrastructure. Your files are <strong>not</strong> sent
            to any third-party AI, cloud, or &quot;online&quot; conversion service. We do not read,
            index, analyse, or retain the contents of your documents beyond the processing needed to
            produce your result.
          </p>
        </Section>

        <Section id="collect" title="2. Information we collect">
          <p>
            We don&apos;t ask for your name, email, or any account details. To keep the service
            reliable and to prevent abuse, our servers keep short-lived operational logs that may
            include your IP address, a timestamp, which tool was called, the response status, the
            error type (if any), and request/response sizes.
          </p>
          <p>
            These logs <strong>never</strong> contain your file contents, file names, or the
            passwords you enter. IP addresses are retained only briefly for rate-limiting and
            security, then discarded.
          </p>
        </Section>

        <Section id="cookies" title="3. Cookies &amp; tracking">
          <p>
            PDFForge does not use cookies for tracking, and does not use analytics, advertising
            pixels, fingerprinting, or any third-party trackers. We don&apos;t build a profile of
            you, and we don&apos;t sell or share data for marketing.
          </p>
          <p>
            Because we set no advertising or analytics cookies, there is no cookie-consent banner to
            click through. Any browser storage we might use is strictly functional (for example,
            remembering a UI preference on your device) and is never used to identify or track you.
          </p>
        </Section>

        <Section id="passwords" title="4. Passwords &amp; encryption">
          <p>
            When you use <strong>Protect PDF</strong>, the password you type is used only to encrypt
            that file during the request. It is held in memory for the duration of processing and is
            never written to disk, logged, or stored. We cannot recover it for you, so keep it safe.
          </p>
        </Section>

        <Section id="security" title="5. How we protect the service">
          <p>
            We apply defence-in-depth: uploads are validated by their actual content (not just their
            extension), processed in sandboxed worker processes with hard size and time limits,
            served over HTTPS with strict security headers and a Content-Security-Policy, and
            protected by per-client rate limiting. No system is perfectly secure, but we design to
            fail safely and to keep your data exposure to the absolute minimum.
          </p>
        </Section>

        <Section id="children" title="6. Children">
          <p>
            PDFForge is a general-purpose utility and is not directed at children. We do not
            knowingly collect personal information from children, and because we require no account,
            we do not knowingly hold any.
          </p>
        </Section>

        <Section id="rights" title="7. Your choices and rights">
          <p>
            Since we don&apos;t create accounts or keep your files, there is very little personal
            data for us to hold, correct, or delete. Depending on where you live (for example, under
            the GDPR or CCPA), you may have rights regarding any personal data a service holds about
            you. If you have a request or question, contact us using the details below.
          </p>
        </Section>

        <Section id="providers" title="8. Service providers">
          <p>
            We rely on infrastructure providers (such as hosting and content delivery) to operate
            the service. These providers process requests only to deliver PDFForge to you and are
            not permitted to use your data for their own purposes. We do not sell your data.
          </p>
        </Section>

        <Section id="changes" title="9. Changes to this policy">
          <p>
            If we change how the service handles data, we&apos;ll update this page and revise the
            &quot;last updated&quot; date above. Significant changes will be highlighted here.
          </p>
        </Section>

        <Section id="contact" title="10. Contact">
          <p>
            Questions about privacy? Reach us at{" "}
            <a href="mailto:support@pdfforge.example" className="font-medium text-ink-600 underline hover:text-brand-600">
              support@pdfforge.example
            </a>
            .
          </p>
        </Section>
      </div>

      <p className="mt-10 border-t border-[var(--border)] pt-5 text-sm text-[var(--muted)]">
        See also our{" "}
        <Link href="/terms" className="font-medium text-ink-600 underline hover:text-brand-600">
          Terms of Service
        </Link>
        .
      </p>
    </article>
  );
}
