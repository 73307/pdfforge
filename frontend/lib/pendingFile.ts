// Holds file(s) the user added on the home "Start with your document" card so the
// tool they pick next can pick them up without re-selecting. Module singleton:
// it survives client-side navigation in the same tab.
//
// A tool page reads with peekPendingFiles() during state init (so the value is
// captured even under React's dev double-render) and clears it once mounted.

let pending: File[] | null = null;

export function setPendingFiles(files: File[]): void {
  pending = files.length ? files : null;
}

export function hasPendingFiles(): boolean {
  return !!pending && pending.length > 0;
}

/** Read the stashed files without removing them. */
export function peekPendingFiles(): File[] | null {
  return pending;
}

/** Drop the stashed files (call once the destination tool has captured them). */
export function clearPendingFiles(): void {
  pending = null;
}
