"use client";

import * as React from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getTool } from "@/lib/tools";
import { useWorkspace } from "./SearchContext";
import { NavLinks } from "./NavLinks";
import { BrandMark } from "./BrandMark";
import { Search, Help, Menu, Close } from "@/components/icons";

function pageLabel(pathname: string): string {
  if (pathname === "/") return "Home";
  if (pathname === "/privacy") return "Privacy";
  if (pathname === "/terms") return "Terms";
  if (pathname === "/preview") return "Result";
  const tool = getTool(pathname.replace(/^\//, ""));
  return tool ? tool.name : "Not found";
}

export function Topbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { query, setQuery } = useWorkspace();
  const [menuOpen, setMenuOpen] = React.useState(false);
  const crumb = pageLabel(pathname);

  function onSearchKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && pathname !== "/") router.push("/#find");
  }

  return (
    <>
    <header className="sticky top-0 z-20 border-b border-[var(--border)] bg-[var(--bg)]/85 backdrop-blur-xl">
      <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
        {/* Mobile: menu + brand */}
        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          aria-label="Open menu"
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-[var(--muted)] hover:bg-black/5 lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>
        <Link href="/" className="lg:hidden" aria-label="PDFForge home">
          <Image src="/logo.webp" alt="PDFForge" width={2000} height={667} className="h-6 w-auto" priority />
        </Link>

        {/* Desktop breadcrumb */}
        <nav aria-label="Breadcrumb" className="hidden min-w-0 items-center gap-1.5 text-sm lg:flex">
          <span className="text-[var(--muted)]">Workspace</span>
          <span className="text-[var(--muted)]/50" aria-hidden="true">
            /
          </span>
          <span className="truncate font-semibold text-[var(--text)]">{crumb}</span>
        </nav>

        {/* Search */}
        <div className="relative ml-auto w-full max-w-md">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onSearchKey}
            placeholder="Search PDF tools…"
            aria-label="Search PDF tools"
            className="h-10 w-full rounded-full border border-[var(--border)] bg-white pl-10 pr-4 text-sm text-[var(--text)] shadow-sm outline-none transition placeholder:text-[var(--muted)]/70 focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
          />
        </div>

        <Link
          href="/privacy"
          aria-label="How PDFForge works"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-white text-[var(--muted)] shadow-sm transition hover:border-brand-300 hover:text-brand-600"
        >
          <Help className="h-5 w-5" />
        </Link>
      </div>
    </header>

      {/* Mobile drawer — rendered outside the blurred header so `fixed` maps to the viewport */}
      {menuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setMenuOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute inset-y-0 left-0 flex w-[280px] max-w-[85%] flex-col bg-[var(--sidebar)] px-4 py-5">
            <div className="flex items-center justify-between">
              <Link
                href="/"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-2.5 px-1"
                aria-label="PDFForge home"
              >
                <BrandMark className="h-8 w-8" />
                <span className="text-lg font-extrabold tracking-tight text-white">
                  PDF<span className="text-brand-400">Forge</span>
                </span>
              </Link>
              <button
                type="button"
                onClick={() => setMenuOpen(false)}
                aria-label="Close menu"
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-[var(--sidebar-ink)] hover:bg-[var(--sidebar-2)] hover:text-white"
              >
                <Close className="h-5 w-5" />
              </button>
            </div>
            <p className="mb-2 mt-6 px-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--sidebar-ink)]/70">
              Workspace
            </p>
            <NavLinks onNavigate={() => setMenuOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
}
