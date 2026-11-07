"use client";

import * as React from "react";
import Link from "next/link";
import { getResult, subscribe, type ToolResult } from "@/lib/resultStore";
import { triggerDownload } from "@/lib/api";
import { formatBytes } from "@/lib/format";
import { Download, Check } from "@/components/icons";

export default function PreviewPage() {
  const [result, setResult] = React.useState<ToolResult | null>(() => getResult());
  const [url, setUrl] = React.useState("");
  const [text, setText] = React.useState("");

  React.useEffect(() => subscribe(() => setResult(getResult())), []);

  React.useEffect(() => {
    if (!result) return;
    const objUrl = URL.createObjectURL(result.blob);
    setUrl(objUrl);
    if (result.type.startsWith("text/")) {
      result.blob.text().then((t) => setText(t.slice(0, 50000)));
    }
    return () => URL.revokeObjectURL(objUrl);
  }, [result]);

  if (!result) {
    return (
      <div className="mx-auto max-w-xl px-4 py-24 text-center">
        <h1 className="text-2xl font-extrabold text-slate-900">Nothing to preview</h1>
        <p className="mt-2 text-slate-600">
          Run a tool first — your result will appear here before you download it. (A page refresh
          clears it.)
        </p>
        <Link
          href="/#find"
          className="mt-6 inline-block rounded-full bg-brand-600 px-6 py-3 font-semibold text-white shadow-brand transition hover:bg-brand-700"
        >
          Browse tools
        </Link>
      </div>
    );
  }

  const isPdf = result.type.includes("pdf");
  const isText = result.type.startsWith("text/");
  const isImage = result.type.startsWith("image/");
  const sizeLabel = formatBytes(result.blob.size);

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <div className="flex flex-wrap items-center gap-3">
        <div className="inline-flex rounded-2xl bg-emerald-100 p-3 text-emerald-700">
          <Check className="h-6 w-6" />
        </div>
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-2xl font-extrabold tracking-tight text-slate-900">
            Your file is ready
          </h1>
          <p className="text-sm text-slate-500">
            {result.toolName} · {result.filename} · {sizeLabel}
          </p>
        </div>
      </div>

      {result.note && (
        <p className="mt-3 rounded-xl border border-brand-100 bg-brand-50 px-3 py-2 text-sm text-brand-800">
          {result.note}
        </p>
      )}

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => triggerDownload(result.blob, result.filename)}
          className="inline-flex items-center gap-2 rounded-full bg-brand-600 px-6 py-2.5 font-semibold text-white shadow-brand transition hover:bg-brand-700"
        >
          <Download className="h-5 w-5" />
          Download
        </button>
        {(isPdf || isText) && (
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="rounded-full border border-[var(--border)] bg-white px-5 py-2.5 font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-700"
          >
            Open in new tab
          </a>
        )}
        <Link
          href={`/${result.toolSlug}`}
          className="rounded-full border border-[var(--border)] bg-white px-5 py-2.5 font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-700"
        >
          Do another
        </Link>
      </div>

      {/* Preview */}
      <div className="mt-6 overflow-hidden rounded-3xl border border-[var(--border)] bg-white shadow-card">
        {isPdf && url && (
          <iframe title="PDF preview" src={url} className="h-[75vh] w-full" />
        )}
        {isText && (
          <pre className="max-h-[75vh] overflow-auto whitespace-pre-wrap p-5 text-sm text-slate-700">
            {text || "Loading text…"}
          </pre>
        )}
        {isImage && url && (
          <div
            className="flex items-center justify-center p-6"
            style={{
              backgroundImage:
                "repeating-conic-gradient(#e5e7eb 0% 25%, #ffffff 0% 50%)",
              backgroundSize: "20px 20px",
            }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={url}
              alt={result.filename}
              className="max-h-[70vh] max-w-full rounded-xl object-contain shadow-sm"
            />
          </div>
        )}
        {!isPdf && !isText && !isImage && (
          <div className="flex flex-col items-center justify-center gap-3 p-16 text-center">
            <div className="inline-flex rounded-2xl bg-ink-50 p-4 text-ink-600">
              <Download className="h-7 w-7" />
            </div>
            <p className="font-semibold text-slate-800">{result.filename}</p>
            <p className="max-w-sm text-sm text-slate-500">
              This file type can&apos;t be previewed in the browser — download it to open with your
              usual app.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
