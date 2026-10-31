"use client";

import * as React from "react";
import { Upload } from "./icons";

interface Props {
  accept: string;
  multiple: boolean;
  onFiles: (files: File[]) => void;
}

export function Dropzone({ accept, multiple, onFiles }: Props) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [drag, setDrag] = React.useState(false);

  function handle(list: FileList | null) {
    if (list && list.length) onFiles(Array.from(list));
  }

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Upload ${multiple ? "files" : "a file"}`}
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
        handle(e.dataTransfer.files);
      }}
      className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition ${
        drag
          ? "border-brand-500 bg-brand-50 dark:bg-brand-900/30"
          : "border-[var(--border)] bg-[var(--surface)] hover:border-brand-300"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        className="sr-only"
        onChange={(e) => {
          handle(e.target.files);
          e.target.value = "";
        }}
      />
      <div className="mx-auto mb-3 inline-flex rounded-full bg-brand-50 p-3 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300">
        <Upload className="h-6 w-6" />
      </div>
      <p className="font-medium">Drag &amp; drop {multiple ? "files" : "a file"} here</p>
      <p className="mt-1 text-sm text-[var(--muted)]">or click to choose</p>
    </div>
  );
}
