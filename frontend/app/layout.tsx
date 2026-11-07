import type { Metadata, Viewport } from "next";
import "./globals.css";
import { WorkspaceProvider } from "@/components/workspace/SearchContext";
import { Sidebar } from "@/components/workspace/Sidebar";
import { Topbar } from "@/components/workspace/Topbar";
import { WorkspaceFooter } from "@/components/workspace/WorkspaceFooter";

export const metadata: Metadata = {
  metadataBase: new URL("https://pdfforge.example"),
  title: {
    default: "PDFForge — Free, private PDF tools",
    template: "%s · PDFForge",
  },
  description:
    "Merge, split, rotate, compress, protect and convert PDFs right in your browser. Files are processed securely and deleted automatically — no account needed.",
  applicationName: "PDFForge",
  keywords: [
    "pdf tools",
    "merge pdf",
    "split pdf",
    "compress pdf",
    "rotate pdf",
    "jpg to pdf",
    "pdf to jpg",
    "protect pdf",
  ],
  openGraph: {
    title: "PDFForge — Free, private PDF tools",
    description:
      "Merge, split, rotate, compress, protect and convert PDFs in your browser. Secure by design.",
    type: "website",
    siteName: "PDFForge",
    images: [{ url: "/logo.webp", width: 2000, height: 667, alt: "PDFForge" }],
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#ef5a1f",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans">
        <WorkspaceProvider>
          <Sidebar />
          <div className="flex min-h-screen flex-col lg:pl-[264px]">
            <Topbar />
            <main className="flex-1">{children}</main>
            <WorkspaceFooter />
          </div>
        </WorkspaceProvider>
      </body>
    </html>
  );
}
