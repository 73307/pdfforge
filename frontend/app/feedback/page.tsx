import type { Metadata } from "next";
import { FeedbackForm } from "@/components/workspace/FeedbackForm";

export const metadata: Metadata = {
  title: "Feedback",
  description: "Rate PDFForge and tell us how to make it better — anonymous, no account needed.",
  alternates: { canonical: "/feedback" },
};

export default async function FeedbackPage({
  searchParams,
}: {
  searchParams: Promise<{ tool?: string }>;
}) {
  const tool = (await searchParams).tool ?? "";
  return (
    <div className="mx-auto max-w-xl px-4 py-10 sm:px-6">
      <header className="mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--text)]">Rate us</h1>
        <p className="mt-1.5 text-[var(--muted)]">
          Tell us what you think — it takes a few seconds and helps us improve.
        </p>
      </header>
      <FeedbackForm tool={tool} />
    </div>
  );
}
