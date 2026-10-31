import Link from "next/link";
import { Logo } from "./icons";

export function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[var(--surface)]/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
          <Logo />
          <span>
            PDF<span className="text-brand-600 dark:text-brand-400">Forge</span>
          </span>
        </Link>
        <nav className="flex items-center gap-1 text-sm sm:gap-4">
          <Link href="/#tools" className="rounded-lg px-3 py-1.5 hover:text-brand-600">
            All tools
          </Link>
          <Link
            href="/privacy"
            className="hidden rounded-lg px-3 py-1.5 hover:text-brand-600 sm:inline"
          >
            Privacy
          </Link>
          <Link
            href="/#tools"
            className="rounded-lg bg-brand-600 px-3 py-1.5 font-medium text-white hover:bg-brand-700"
          >
            Start
          </Link>
        </nav>
      </div>
    </header>
  );
}
