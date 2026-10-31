// Thin API client. Sends multipart form data and returns the processed file as a Blob.
// Errors from the backend are already generic/safe; we surface the message as-is.

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export interface ProcessResult {
  blob: Blob;
  filename: string;
  headers: Headers;
}

function filenameFrom(disposition: string): string {
  const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(disposition);
  return match ? decodeURIComponent(match[1]) : "download";
}

/**
 * Upload via XMLHttpRequest so we can report REAL upload progress (fetch can't).
 * `onProgress` receives the upload percentage 0–100; it reaches 100 once the whole
 * file has been sent and the server starts processing.
 */
export function uploadWithProgress(
  endpoint: string,
  form: FormData,
  onProgress: (percent: number) => void,
): Promise<ProcessResult> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${BASE}${endpoint}`);
    xhr.responseType = "blob";

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress(Math.min(100, Math.round((e.loaded / e.total) * 100)));
    };
    xhr.upload.onload = () => onProgress(100);

    xhr.onload = () => {
      const blob = xhr.response as Blob;
      if (xhr.status >= 200 && xhr.status < 300) {
        const headers = new Headers();
        for (const h of ["content-disposition", "x-original-bytes", "x-compressed-bytes", "x-reduced"]) {
          const v = xhr.getResponseHeader(h);
          if (v) headers.set(h, v);
        }
        resolve({
          blob,
          filename: filenameFrom(xhr.getResponseHeader("content-disposition") ?? ""),
          headers,
        });
        return;
      }
      // Error: the body is a JSON blob with { error: { message } }.
      blob
        .text()
        .then((t) => {
          let message = "Something went wrong. Please try again.";
          try {
            const data = JSON.parse(t);
            if (data?.error?.message) message = data.error.message;
          } catch {
            /* keep generic */
          }
          reject(new Error(message));
        })
        .catch(() => reject(new Error("Something went wrong. Please try again.")));
    };

    xhr.onerror = () =>
      reject(new Error("Could not reach the server. Check your connection and try again."));

    xhr.send(form);
  });
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
