import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTool, TOOLS } from "@/lib/tools";
import { ToolRunner } from "@/components/ToolRunner";

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
    <div className="mx-auto max-w-3xl px-4 py-10">
      <nav aria-label="Breadcrumb" className="mb-4 text-sm text-[var(--muted)]">
        <Link href="/" className="hover:text-brand-600">
          Home
        </Link>{" "}
        <span aria-hidden="true">/</span> <span className="text-[var(--text)]">{tool.name}</span>
      </nav>

      <h1 className="text-3xl font-bold tracking-tight">{tool.name}</h1>
      <p className="mt-2 text-[var(--muted)]">{tool.description}</p>

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
