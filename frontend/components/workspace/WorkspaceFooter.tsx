import Link from "next/link";
import { Shield, ArrowRight } from "@/components/icons";

export function WorkspaceFooter() {
  return (
    <footer className="mt-10 border-t border-[var(--border)] bg-[var(--surface)]">
      <div className="flex flex-col gap-3 px-4 py-5 text-sm text-[var(--muted)] sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-ink-500" />
          <span>Clear tools. Straightforward workflows. Files auto-deleted after each job.</span>
        </div>
        <Link
          href="/privacy"
          className="inline-flex items-center gap-1 font-semibold text-ink-600 hover:text-brand-600"
        >
          How we protect files
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </footer>
  );
}
