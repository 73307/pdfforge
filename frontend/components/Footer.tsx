import Link from "next/link";
import { Shield } from "./icons";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-[var(--border)]">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 text-sm text-[var(--muted)] sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-brand-600" />
          <span>Files are processed securely and deleted automatically. We never store them.</span>
        </div>
        <nav className="flex gap-4">
          <Link href="/privacy" className="hover:text-brand-600">
            Privacy
          </Link>
          <Link href="/terms" className="hover:text-brand-600">
            Terms
          </Link>
          <Link href="/#tools" className="hover:text-brand-600">
            Tools
          </Link>
        </nav>
      </div>
    </footer>
  );
}
