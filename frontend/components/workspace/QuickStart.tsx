"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { getTool } from "@/lib/tools";
import { formatBytes } from "@/lib/format";
import { setPendingFiles, clearPendingFiles } from "@/lib/pendingFile";
import { ToolIcon, Upload, ArrowRight, Trash } from "@/components/icons";

type Kind = "pdf" | "image" | "word" | "excel" | "other";

const ACCEPT =
  "application/pdf,.pdf,image/jpeg,image/png,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx";

// Which tools to suggest for each file kind, in a sensible order.
const SUGGEST: Record<Kind, string[]> = {
  pdf: ["compress-pdf", "merge-pdf", "split-pdf", "pdf-to-word", "rotate-pdf", "protect-pdf"],
  image: ["remove-background", "images-to-pdf"],
  word: ["word-to-pdf"],
  excel: ["excel-to-pdf"],
  other: [],
};

function kindOf(file: File): Kind {
  const n = file.name.toLowerCase();
  const t = file.type;
  if (t === "application/pdf" || n.endsWith(".pdf")) return "pdf";
  if (t.startsWith("image/") || /\.(jpe?g|png)$/.test(n)) return "image";
  if (/\.docx?$/.test(n) || t.includes("word")) return "word";
  if (/\.xlsx?$/.test(n) || t.includes("excel") || t.includes("spreadsheet")) return "excel";
  return "other";
}

export function QuickStart() {
  const router = useRouter();
  const [files, setFiles] = React.useState<File[]>([]);
  const [drag, setDrag] = React.useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Clear any leftover handoff when the user is back on the home screen.
  React.useEffect(() => clearPendingFiles(), []);

  function add(list: FileList | null) {
    if (!list || !list.length) return;
    setFiles(Array.from(list));
  }

  function go(slug: string) {
    setPendingFiles(files);
    router.push(`/${slug}`);
  }

  const kind = files.length ? kindOf(files[0]) : "other";
  const suggestions = SUGGEST[kind].map(getTool).filter(Boolean);

  return (
    <section className="overflow-hidden rounded-3xl border border-[var(--border)] bg-white shadow-card">
      <div className="flex flex-col gap-5 border-l-4 border-brand-500 p-5 sm:p-6 lg:flex-row lg:items-center lg:justify-between lg:gap-8">
        <div className="flex items-start gap-4">
          <span className="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-ink-50 text-ink-600">
            <ToolIcon name="merge" className="h-6 w-6" />
          </span>
          <div>
            <h2 className="text-lg font-extrabold tracking-tight text-[var(--text)]">
              Start with your document
            </h2>
            <p className="mt-1 text-sm text-[var(--muted)]">
              Add a file and pick what to do next — it carries straight into the tool.
            </p>
          </div>
        </div>

        <div
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              inputRef.current?.click();
            }
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            add(e.dataTransfer.files);
          }}
          className={`flex w-full cursor-pointer flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed px-6 py-5 text-center transition lg:w-[380px] ${
            drag ? "border-brand-500 bg-brand-50" : "border-[var(--border)] bg-[var(--bg)] hover:border-brand-300"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT}
            multiple
            className="sr-only"
            onChange={(e) => {
              add(e.target.files);
              e.target.value = "";
            }}
          />
          <span className="inline-flex items-center gap-2 rounded-full bg-brand-600 px-5 py-2.5 font-semibold text-white shadow-brand transition hover:bg-brand-700">
            <Upload className="h-5 w-5" />
            Choose file
          </span>
          <span className="text-xs text-[var(--muted)]">or drag and drop here</span>
        </div>
      </div>

      {files.length > 0 && (
        <div className="border-t border-[var(--border)] bg-[var(--bg)] p-5 sm:p-6">
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-[var(--text)]">
              {files.length === 1 ? files[0].name : `${files.length} files selected`}
            </span>
            <span className="text-xs text-[var(--muted)]">
              {formatBytes(files.reduce((s, f) => s + f.size, 0))}
            </span>
            <button
              type="button"
              onClick={() => setFiles([])}
              className="ml-auto inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium text-[var(--muted)] hover:bg-rose-50 hover:text-rose-600"
            >
              <Trash className="h-3.5 w-3.5" />
              Clear
            </button>
          </div>

          {suggestions.length > 0 ? (
            <>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">
                What would you like to do?
              </p>
              <div className="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
                {suggestions.map((tool) => (
                  <button
                    key={tool!.slug}
                    type="button"
                    onClick={() => go(tool!.slug)}
                    className="group flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-white px-4 py-3 text-left transition hover:border-brand-300 hover:shadow-card"
                  >
                    <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-ink-50 text-ink-600">
                      <ToolIcon name={tool!.icon} className="h-5 w-5" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-semibold text-[var(--text)]">
                        {tool!.name}
                      </span>
                      <span className="block truncate text-xs text-[var(--muted)]">{tool!.tagline}</span>
                    </span>
                    <ArrowRight className="h-4 w-4 shrink-0 text-[var(--muted)] transition group-hover:translate-x-0.5 group-hover:text-brand-600" />
                  </button>
                ))}
              </div>
            </>
          ) : (
            <p className="text-sm text-[var(--muted)]">
              We can work with PDF, image, Word and Excel files. Try one of those, or browse all tools below.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
