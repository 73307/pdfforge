"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import type { ToolDef, ToolField } from "@/lib/tools";
import { uploadWithProgress } from "@/lib/api";
import { formatBytes } from "@/lib/format";
import { setResult } from "@/lib/resultStore";
import { Dropzone } from "./Dropzone";
import { ArrowDown, ArrowUp, Alert, Spinner, Trash } from "./icons";

type Status = "idle" | "working" | "error";

function initialValues(tool: ToolDef): Record<string, string> {
  const v: Record<string, string> = {};
  for (const f of tool.fields) v[f.name] = f.default ?? "";
  return v;
}

export function ToolRunner({ tool }: { tool: ToolDef }) {
  const router = useRouter();
  const [files, setFiles] = React.useState<File[]>([]);
  const [values, setValues] = React.useState<Record<string, string>>(() => initialValues(tool));
  const [status, setStatus] = React.useState<Status>("idle");
  const [error, setError] = React.useState("");
  const [progress, setProgress] = React.useState(0);
  const [phase, setPhase] = React.useState<"upload" | "process">("upload");

  function addFiles(incoming: File[]) {
    setError("");
    setStatus("idle");
    setFiles((prev) => (tool.multiple ? [...prev, ...incoming] : incoming.slice(0, 1)));
  }

  function removeAt(i: number) {
    setFiles((prev) => prev.filter((_, idx) => idx !== i));
  }

  function move(i: number, dir: -1 | 1) {
    setFiles((prev) => {
      const next = [...prev];
      const j = i + dir;
      if (j < 0 || j >= next.length) return prev;
      [next[i], next[j]] = [next[j], next[i]];
      return next;
    });
  }

  function reset() {
    setFiles([]);
    setValues(initialValues(tool));
    setStatus("idle");
    setError("");
    setProgress(0);
    setPhase("upload");
  }

  async function run() {
    setError("");

    if (files.length < tool.minFiles) {
      setError(`Please add at least ${tool.minFiles} file${tool.minFiles > 1 ? "s" : ""}.`);
      return;
    }
    for (const f of tool.fields) {
      if (f.required && !(values[f.name] ?? "").trim()) {
        setError(`${f.label} is required.`);
        return;
      }
    }

    const form = new FormData();
    const field = tool.multiple ? "files" : "file";
    files.forEach((file) => form.append(field, file));
    for (const f of tool.fields) {
      const value = values[f.name] ?? "";
      if (value !== "") form.append(f.name, value);
    }

    setStatus("working");
    setProgress(0);
    setPhase("upload");
    try {
      const { blob, filename, headers } = await uploadWithProgress(tool.endpoint, form, (pct) => {
        setProgress(pct);
        if (pct >= 100) setPhase("process");
      });
      const name = filename || tool.resultName;

      let note = "";
      if (tool.slug === "compress-pdf") {
        const reduced = headers.get("X-Reduced") === "1";
        const orig = Number(headers.get("X-Original-Bytes"));
        const comp = Number(headers.get("X-Compressed-Bytes"));
        note =
          reduced && orig > 0
            ? `Reduced from ${formatBytes(orig)} to ${formatBytes(comp)} (−${Math.round(
                (1 - comp / orig) * 100,
              )}%).`
            : "This PDF was already well optimized, so we returned the original unchanged.";
      }

      setResult({
        blob,
        filename: name,
        type: blob.type || "application/octet-stream",
        toolName: tool.name,
        toolSlug: tool.slug,
        note,
      });
      router.push("/preview");
    } catch (e) {
      setStatus("error");
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
    }
  }

  const disabled = status === "working";

  return (
    <div className="rounded-3xl border border-[var(--border)] bg-white p-5 shadow-card sm:p-6">
      <Dropzone accept={tool.accept} multiple={tool.multiple} onFiles={addFiles} />

      {files.length > 0 && (
        <ul className="mt-4 space-y-2">
          {files.map((file, i) => (
            <li
              key={`${file.name}-${i}`}
              className="flex items-center gap-2 rounded-xl border border-[var(--border)] px-3 py-2 text-sm"
            >
              <span className="min-w-0 flex-1 truncate">{file.name}</span>
              <span className="shrink-0 text-xs text-slate-400">{formatBytes(file.size)}</span>
              {tool.reorderable && files.length > 1 && (
                <span className="flex shrink-0 gap-1">
                  <button
                    type="button"
                    aria-label="Move up"
                    disabled={i === 0 || disabled}
                    onClick={() => move(i, -1)}
                    className="rounded-md p-1 hover:bg-violet-50 disabled:opacity-30"
                  >
                    <ArrowUp className="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    aria-label="Move down"
                    disabled={i === files.length - 1 || disabled}
                    onClick={() => move(i, 1)}
                    className="rounded-md p-1 hover:bg-violet-50 disabled:opacity-30"
                  >
                    <ArrowDown className="h-4 w-4" />
                  </button>
                </span>
              )}
              <button
                type="button"
                aria-label={`Remove ${file.name}`}
                disabled={disabled}
                onClick={() => removeAt(i)}
                className="shrink-0 rounded-md p-1 text-rose-500 hover:bg-rose-50 disabled:opacity-30"
              >
                <Trash className="h-4 w-4" />
              </button>
            </li>
          ))}
        </ul>
      )}

      {tool.fields.length > 0 && (
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          {tool.fields.map((f) => (
            <Field
              key={f.name}
              field={f}
              value={values[f.name] ?? ""}
              disabled={disabled}
              onChange={(v) => setValues((prev) => ({ ...prev, [f.name]: v }))}
            />
          ))}
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={run}
          disabled={disabled || files.length < tool.minFiles}
          className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 px-6 py-2.5 font-semibold text-white shadow-md transition hover:shadow-glow disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
        >
          {status === "working" && <Spinner className="h-5 w-5" />}
          {status === "working" ? (phase === "upload" ? "Uploading…" : "Processing…") : tool.name}
        </button>
        {(files.length > 0 || status === "error") && (
          <button
            type="button"
            onClick={reset}
            disabled={disabled}
            className="rounded-full border border-[var(--border)] px-4 py-2.5 text-sm font-medium hover:border-violet-300 disabled:opacity-50"
          >
            Start over
          </button>
        )}
      </div>

      <div aria-live="polite" className="mt-4">
        {status === "working" && (
          <div className="mb-1">
            <div className="mb-1.5 flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>{phase === "upload" ? "Uploading your file…" : "Processing…"}</span>
              {phase === "upload" && <span>{progress}%</span>}
            </div>
            <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-violet-100">
              {phase === "upload" ? (
                <div
                  className="h-full rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 transition-all duration-150"
                  style={{ width: `${progress}%` }}
                />
              ) : (
                <div className="animate-indeterminate inset-y-0 w-1/3 rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500" />
              )}
            </div>
          </div>
        )}
        {status === "error" && (
          <div className="flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
            <Alert className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function Field({
  field,
  value,
  onChange,
  disabled,
}: {
  field: ToolField;
  value: string;
  onChange: (v: string) => void;
  disabled: boolean;
}) {
  const id = `field-${field.name}`;
  const base =
    "w-full rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm focus:border-violet-500";
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium">
        {field.label}
      </label>
      {field.kind === "select" ? (
        <select
          id={id}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          className={base}
        >
          {field.options?.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={id}
          type={field.kind === "password" ? "password" : field.kind === "number" ? "number" : "text"}
          value={value}
          placeholder={field.placeholder}
          min={field.min}
          max={field.max}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          className={base}
        />
      )}
      {field.help && <p className="mt-1 text-xs text-slate-400">{field.help}</p>}
    </div>
  );
}
