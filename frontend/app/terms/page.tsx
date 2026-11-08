import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "The terms that govern your use of PDFForge's free, private PDF and image tools.",
  alternates: { canonical: "/terms" },
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

export default function Terms() {
  return (
    <article className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <header>
        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--text)] sm:text-4xl">
          Terms of Service
        </h1>
        <p className="mt-2 text-sm text-[var(--muted)]">Last updated: {UPDATED}</p>
        <p className="mt-4 text-[var(--muted)]">
          These terms govern your use of PDFForge. By using the tools, you agree to them. If you
          don&apos;t agree, please don&apos;t use the service.
        </p>
      </header>

      <div className="mt-8 space-y-7">
        <Section id="service" title="1. The service">
          <p>
            PDFForge provides free, browser-based tools to merge, split, convert, compress, protect
            and edit PDF and image files. The service is offered on an &quot;as available&quot;
            basis; we may add, change, limit, or discontinue features at any time to keep it
            reliable and secure.
          </p>
        </Section>

        <Section id="acceptable" title="2. Acceptable use">
          <p>You agree to use PDFForge lawfully and responsibly. In particular, you must not:</p>
          <ul className="list-disc space-y-1 pl-5">
            <li>Upload or process files you don&apos;t own or have the right to use.</li>
            <li>Process illegal content, malware, or anything that infringes others&apos; rights.</li>
            <li>Attempt to bypass limits, probe, overload, disrupt, or reverse-engineer the service.</li>
            <li>Use automated means to abuse the tools beyond the published rate limits.</li>
          </ul>
        </Section>

        <Section id="content" title="3. Your content">
          <p>
            You keep all rights to the files you upload. We claim no ownership over them and do not
            use them for any purpose other than performing the operation you requested. Files are
            deleted immediately after processing, as described in our{" "}
            <Link href="/privacy" className="font-medium text-ink-600 underline hover:text-brand-600">
              Privacy Policy
            </Link>
            .
          </p>
        </Section>

        <Section id="warranty" title="4. No warranty">
          <p>
            The service is provided &quot;as is&quot; and &quot;as available&quot;, without
            warranties of any kind, express or implied. Conversion, compression and background-removal
            results vary by file, and we do not guarantee perfect fidelity, accuracy, or
            availability for every document.
          </p>
        </Section>

        <Section id="liability" title="5. Limitation of liability">
          <p>
            To the maximum extent permitted by law, PDFForge and its operators are not liable for any
            indirect, incidental, or consequential damages, or for any loss of data arising from your
            use of the service. Always keep your own copy of important files before processing them.
          </p>
        </Section>

        <Section id="ip" title="6. Intellectual property">
          <p>
            The PDFForge name, branding, interface, and code are the property of their owners and are
            protected by applicable laws. These terms grant you no rights to our trademarks or
            software beyond using the service as intended.
          </p>
        </Section>

        <Section id="age" title="7. Eligibility">
          <p>
            You must be old enough to form a binding agreement in your jurisdiction to use PDFForge.
            If you use it on behalf of an organisation, you confirm you&apos;re authorised to accept
            these terms for it.
          </p>
        </Section>

        <Section id="changes" title="8. Changes to these terms">
          <p>
            We may update these terms from time to time. We&apos;ll revise the &quot;last
            updated&quot; date above, and your continued use of the service means you accept the
            updated terms.
          </p>
        </Section>

        <Section id="law" title="9. Governing law">
          <p>
            These terms are governed by the laws of the operator&apos;s jurisdiction, without regard
            to conflict-of-law rules. Any disputes will be handled by the competent courts there.
          </p>
        </Section>

        <Section id="contact" title="10. Contact">
          <p>
            Questions about these terms? Reach us at{" "}
            <a href="mailto:support@pdfforge.example" className="font-medium text-ink-600 underline hover:text-brand-600">
              support@pdfforge.example
            </a>
            .
          </p>
        </Section>
      </div>
    </article>
  );
}
