import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center">
      <p className="text-sm font-semibold text-brand-600">404</p>
      <h1 className="mt-2 text-3xl font-bold">Page not found</h1>
      <p className="mt-3 text-[var(--muted)]">
        That tool or page doesn&apos;t exist. Let&apos;s get you back to the tools.
      </p>
      <Link
        href="/"
        className="mt-6 inline-block rounded-xl bg-brand-600 px-5 py-2.5 font-medium text-white hover:bg-brand-700"
      >
        Back to home
      </Link>
    </div>
  );
}
