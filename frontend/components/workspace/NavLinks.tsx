"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CATEGORIES, TOOLS, type CategoryId } from "@/lib/tools";
import { useWorkspace, type CatKey } from "./SearchContext";
import { Home, Grid, Layers, Swap, Shield } from "@/components/icons";

type Item = {
  key: CatKey;
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
};

const CAT_ICON: Record<CategoryId, React.ReactNode> = {
  organize: <Layers className="h-[18px] w-[18px]" />,
  convert: <Swap className="h-[18px] w-[18px]" />,
  optimize: <Shield className="h-[18px] w-[18px]" />,
};

const ITEMS: Item[] = [
  { key: "home", label: "Home", href: "/", icon: <Home className="h-[18px] w-[18px]" /> },
  {
    key: "all",
    label: "All tools",
    href: "/#find",
    icon: <Grid className="h-[18px] w-[18px]" />,
    badge: String(TOOLS.length),
  },
  ...CATEGORIES.map((c) => ({
    key: c.id as CatKey,
    label: c.label,
    href: "/#find",
    icon: CAT_ICON[c.id],
  })),
];

export function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { cat, setCat } = useWorkspace();
  const onHome = pathname === "/";

  return (
    <nav className="flex flex-col gap-1">
      {ITEMS.map((item) => {
        const active = onHome && cat === item.key;
        return (
          <Link
            key={item.key}
            href={item.href}
            onClick={() => {
              setCat(item.key);
              onNavigate?.();
            }}
            aria-current={active ? "page" : undefined}
            className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
              active
                ? "bg-[var(--sidebar-3)] text-white"
                : "text-[var(--sidebar-ink)] hover:bg-[var(--sidebar-2)] hover:text-white"
            }`}
          >
            {active && (
              <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-brand-500" />
            )}
            <span className={active ? "text-white" : "text-[var(--sidebar-ink)] group-hover:text-white"}>
              {item.icon}
            </span>
            <span className="flex-1">{item.label}</span>
            {item.badge && (
              <span
                className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                  active ? "bg-white/20 text-white" : "bg-white/10 text-[var(--sidebar-ink)]"
                }`}
              >
                {item.badge}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
