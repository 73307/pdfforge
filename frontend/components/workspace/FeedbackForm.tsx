"use client";

import * as React from "react";
import Link from "next/link";
import { Star, Check, Spinner, Alert, ArrowRight } from "@/components/icons";

const BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(/\/+$/, "");

const LABELS = ["", "Poor", "Fair", "Good", "Great", "Excellent"];

export function FeedbackForm({ tool = "" }: { tool?: string }) {
  const [rating, setRating] = React.useState(0);
  const [hover, setHover] = React.useState(0);
  const [message, setMessage] = React.useState("");
  const [status, setStatus] = React.useState<"idle" | "sending" | "done" | "error">("idle");
  const [error, setError] = React.useState("");

  async function submit() {
    if (rating < 1) {
      setError("Please pick a star rating first.");
      return;
    }
    setStatus("sending");
    setError("");
    try {
      const form = new FormData();
      form.append("rating", String(rating));
      form.append("message", message.trim());
      if (tool) form.append("tool", tool);
      const res = await fetch(`${BASE}/api/feedback`, { method: "POST", body: form });
      if (!res.ok) throw new Error("bad status");
      setStatus("done");
    } catch {
      setStatus("error");
      setError("Couldn’t send your feedback — please try again.");
    }
  }

  if (status === "done") {
    return (
      <div className="rounded-3xl border border-[var(--border)] bg-white p-8 text-center shadow-card">
        <div className="mx-auto inline-flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
          <Check className="h-7 w-7" />
        </div>
        <h2 className="mt-4 text-xl font-extrabold tracking-tight text-[var(--text)]">Thank you! 🙏</h2>
        <p className="mt-1 text-[var(--muted)]">
          Your feedback helps us make PDFForge better. We read every one.
        </p>
        <Link
          href="/"
          className="mt-6 inline-flex items-center gap-1 rounded-full bg-brand-600 px-6 py-2.5 font-semibold text-white shadow-brand transition hover:bg-brand-700"
        >
          Back to tools
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  const active = hover || rating;
  const sending = status === "sending";

  return (
    <div className="rounded-3xl border border-[var(--border)] bg-white p-6 shadow-card sm:p-8">
      <h2 className="text-xl font-extrabold tracking-tight text-[var(--text)]">How was your experience?</h2>
      <p className="mt-1 text-sm text-[var(--muted)]">
        {tool ? `You used ${tool}. ` : ""}Your rating is anonymous — no account, no email needed.
      </p>

      {/* Stars */}
      <div className="mt-5 flex items-center gap-2" onMouseLeave={() => setHover(0)}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            aria-label={`${n} star${n > 1 ? "s" : ""}`}
            disabled={sending}
            onMouseEnter={() => setHover(n)}
            onClick={() => {
              setRating(n);
              setError("");
            }}
            className={`transition ${n <= active ? "text-amber-400" : "text-slate-300"} hover:scale-110 disabled:opacity-60`}
          >
            <Star filled={n <= active} className="h-9 w-9" />
          </button>
        ))}
        <span className="ml-2 text-sm font-semibold text-[var(--muted)]">{LABELS[active]}</span>
      </div>

      {/* Message */}
      <label htmlFor="fb-msg" className="mt-6 block text-sm font-medium text-[var(--text)]">
        Anything we can improve? <span className="font-normal text-[var(--muted)]">(optional)</span>
      </label>
      <textarea
        id="fb-msg"
        value={message}
        onChange={(e) => setMessage(e.target.value.slice(0, 1000))}
        disabled={sending}
        rows={4}
        placeholder="What did you like, what was confusing, or what would make it better?"
        className="mt-2 w-full rounded-2xl border border-[var(--border)] bg-white px-4 py-3 text-sm text-[var(--text)] outline-none transition placeholder:text-[var(--muted)]/70 focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
      />
      <div className="mt-1 text-right text-xs text-[var(--muted)]">{message.length}/1000</div>

      {error && (
        <div className="mt-3 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
          <Alert className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button
        type="button"
        onClick={submit}
        disabled={sending}
        className="mt-5 inline-flex items-center gap-2 rounded-full bg-brand-600 px-6 py-2.5 font-semibold text-white shadow-brand transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {sending && <Spinner className="h-5 w-5" />}
        {sending ? "Sending…" : "Send feedback"}
      </button>
    </div>
  );
}
