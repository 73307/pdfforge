import Link from "next/link";
import { Logo } from "./icons";

export function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-white/75 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 text-lg font-extrabold tracking-tight">
          <Logo />
          <span>
            PDF
            <span className="bg-gradient-to-r from-violet-600 to-fuchsia-500 bg-clip-text text-transparent">
              Forge
            </span>
          </span>
        </Link>
        <nav className="flex items-center gap-1 text-sm font-medium sm:gap-2">
          <Link href="/#tools" className="rounded-full px-3 py-1.5 text-slate-600 hover:bg-violet-50 hover:text-violet-700">
            All tools
          </Link>
          <Link
            href="/privacy"
            className="hidden rounded-full px-3 py-1.5 text-slate-600 hover:bg-violet-50 hover:text-violet-700 sm:inline"
          >
            Privacy
          </Link>
          <Link
            href="/#tools"
            className="rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 px-4 py-1.5 font-semibold text-white shadow-sm transition hover:shadow-glow"
          >
            Start free
          </Link>
        </nav>
      </div>
    </header>
  );
}
