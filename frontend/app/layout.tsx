import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

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
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#4f46e5",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col font-sans">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
