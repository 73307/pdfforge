// Holds the most recent tool result in memory so the /preview page can show it.
// Lives only in the current tab session (module singleton); a full page reload clears it.

export interface ToolResult {
  blob: Blob;
  filename: string;
  type: string; // mime type
  toolName: string;
  toolSlug: string;
  note?: string;
}

let current: ToolResult | null = null;
const listeners = new Set<() => void>();

export function setResult(result: ToolResult): void {
  current = result;
  listeners.forEach((l) => l());
}

export function getResult(): ToolResult | null {
  return current;
}

export function clearResult(): void {
  current = null;
  listeners.forEach((l) => l());
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}
