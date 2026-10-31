// Thin API client. Sends multipart form data and returns the processed file as a Blob.
// Errors from the backend are already generic/safe; we surface the message as-is.

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export interface ProcessResult {
  blob: Blob;
  filename: string;
  headers: Headers;
}

export async function processRequest(endpoint: string, form: FormData): Promise<ProcessResult> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${endpoint}`, { method: "POST", body: form });
  } catch {
    throw new Error("Could not reach the server. Check your connection and try again.");
  }

  if (!res.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const data = await res.json();
      if (data?.error?.message) message = data.error.message;
    } catch {
      /* non-JSON error body: keep the generic message */
    }
    throw new Error(message);
  }

  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition") ?? "";
  const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(disposition);
  const filename = match ? decodeURIComponent(match[1]) : "download";
  return { blob, filename, headers: res.headers };
}

export function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // Give the browser time to start the download before releasing the URL.
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}
