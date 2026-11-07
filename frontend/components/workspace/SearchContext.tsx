"use client";

import * as React from "react";
import type { CategoryId } from "@/lib/tools";

// "home" = top view (nothing filtered), "all" = every tool, or one category.
export type CatKey = "home" | "all" | CategoryId;

interface WorkspaceState {
  query: string;
  setQuery: (v: string) => void;
  cat: CatKey;
  setCat: (c: CatKey) => void;
}

const Ctx = React.createContext<WorkspaceState>({
  query: "",
  setQuery: () => {},
  cat: "home",
  setCat: () => {},
});

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const [query, setQuery] = React.useState("");
  const [cat, setCat] = React.useState<CatKey>("home");
  const value = React.useMemo(() => ({ query, setQuery, cat, setCat }), [query, cat]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useWorkspace(): WorkspaceState {
  return React.useContext(Ctx);
}
