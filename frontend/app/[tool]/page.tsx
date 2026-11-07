import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTool, TOOLS } from "@/lib/tools";
import { ToolRunner } from "@/components/ToolRunner";
import { ToolIcon, ArrowRight } from "@/components/icons";

export function generateStaticParams() {
  return TOOLS.map((t) => ({ tool: t.slug }));
}

export function generateMetadata({ params }: { params: { tool: string } }): Metadata {
  const tool = getTool(params.tool);
  if (!tool) return { title: "Tool not found" };
  return {
    title: tool.name,
    description: tool.description,
    alternates: { canonical: `/${tool.slug}` },
    openGraph: {
      title: `${tool.name} · PDFForge`,
      description: tool.description,
      type: "website",
    },
  };
}

export default function ToolPage({ params }: { params: { tool: string } }) {
  const tool = getTool(params.tool);
  if (!tool) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: `${tool.name} — PDFForge`,
    applicationCategory: "Utility",
    operatingSystem: "Any",
    description: tool.description,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        href="/#find"
        className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-[var(--muted)] transition hover:text-brand-600"
      >
        <ArrowRight className="h-4 w-4 rotate-180" />
        All tools
      </Link>

      <div className="mb-4 inline-flex rounded-2xl bg-ink-50 p-3 text-ink-600">
        <ToolIcon name={tool.icon} className="h-7 w-7" />
      </div>
      <h1 className="text-3xl font-extrabold tracking-tight text-[var(--text)] sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-2 max-w-2xl text-[var(--muted)]">{tool.description}</p>

      <div className="mt-6">
        <ToolRunner tool={tool} />
      </div>

      {tool.notes && tool.notes.length > 0 && (
        <ul className="mt-5 list-disc space-y-1 pl-5 text-sm text-[var(--muted)]">
          {tool.notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      )}

      <p className="mt-8 text-xs text-[var(--muted)]">
        Your file is validated, processed in an isolated worker, and deleted immediately after the
        download. Nothing is stored. See our{" "}
        <Link href="/privacy" className="underline hover:text-brand-600">
          privacy policy
        </Link>
        .
      </p>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </div>
  );
}
