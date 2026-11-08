import Link from "next/link";
import { BrandMark } from "./BrandMark";
import { NavLinks } from "./NavLinks";
import { Help } from "@/components/icons";

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[264px] flex-col bg-[var(--sidebar)] px-4 py-5 lg:flex">
      <Link href="/" className="flex items-center gap-2.5 px-2" aria-label="PDFForge home">
        <BrandMark className="h-9 w-9" />
        <span className="text-[19px] font-extrabold tracking-tight text-white">
          PDF<span className="text-brand-400">Forge</span>
        </span>
      </Link>

      <p className="mb-2 mt-7 px-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--sidebar-muted)]">
        Workspace
      </p>
      <NavLinks />

      <div className="mt-auto border-t border-[var(--sidebar-line)] pt-4">
        <Link
          href="/privacy"
          className="flex items-start gap-3 rounded-xl px-3 py-2.5 text-[var(--sidebar-ink)] transition hover:bg-[var(--sidebar-2)] hover:text-white"
        >
          <Help className="mt-0.5 h-[18px] w-[18px]" />
          <span className="text-sm">
            Need a hand?
            <span className="block text-xs text-[var(--sidebar-muted)]">How we protect your files</span>
          </span>
        </Link>
        <div className="mt-2 flex gap-4 px-3 text-xs text-[var(--sidebar-muted)]">
          <Link href="/privacy" className="hover:text-white">
            Privacy
          </Link>
          <Link href="/terms" className="hover:text-white">
            Terms
          </Link>
        </div>
      </div>
    </aside>
  );
}
