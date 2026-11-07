// Single source of truth for every tool: used by the homepage, the dynamic tool
// pages, SEO metadata, and the sitemap.

export type FieldKind = "text" | "password" | "number" | "select";

export interface ToolField {
  kind: FieldKind;
  name: string;
  label: string;
  placeholder?: string;
  help?: string;
  required?: boolean;
  min?: number;
  max?: number;
  default?: string;
  options?: { value: string; label: string }[];
}

export interface ToolDef {
  slug: string;
  name: string;
  tagline: string;
  description: string;
  icon: string;
  accept: string;
  multiple: boolean;
  reorderable?: boolean;
  minFiles: number;
  endpoint: string;
  fields: ToolField[];
  resultName: string;
  notes?: string[];
}

export const TOOLS: ToolDef[] = [
  {
    slug: "merge-pdf",
    name: "Merge PDF",
    tagline: "Combine several PDFs into one",
    description:
      "Upload two or more PDF files, arrange them in the order you want, and download a single merged PDF.",
    icon: "merge",
    accept: "application/pdf,.pdf",
    multiple: true,
    reorderable: true,
    minFiles: 2,
    endpoint: "/api/merge",
    fields: [],
    resultName: "merged.pdf",
    notes: ["Drag to reorder is done with the ↑ ↓ buttons.", "Files are deleted right after processing."],
  },
  {
    slug: "split-pdf",
    name: "Split PDF",
    tagline: "Extract pages or page ranges",
    description:
      "Pull out the pages you need. One range gives you a single PDF; multiple ranges are returned as a ZIP.",
    icon: "split",
    accept: "application/pdf,.pdf",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/split",
    fields: [
      {
        kind: "text",
        name: "ranges",
        label: "Pages / ranges",
        placeholder: "e.g. 1-3,5,8-10",
        help: "Comma-separated. Ranges use a dash. Pages are 1-based.",
        required: true,
      },
    ],
    resultName: "split.pdf",
  },
  {
    slug: "rotate-pdf",
    name: "Rotate PDF",
    tagline: "Turn pages 90°, 180° or 270°",
    description: "Rotate every page or only the pages you choose.",
    icon: "rotate",
    accept: "application/pdf,.pdf",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/rotate",
    fields: [
      {
        kind: "select",
        name: "angle",
        label: "Rotation",
        default: "90",
        options: [
          { value: "90", label: "90° clockwise" },
          { value: "180", label: "180°" },
          { value: "270", label: "270° (90° counter-clockwise)" },
        ],
      },
      {
        kind: "text",
        name: "pages",
        label: "Pages (optional)",
        placeholder: "Leave empty for all, or e.g. 1,3-4",
        help: "Only these pages are rotated. Empty = all pages.",
      },
    ],
    resultName: "rotated.pdf",
  },
  {
    slug: "images-to-pdf",
    name: "JPG/PNG to PDF",
    tagline: "Turn images into a PDF",
    description: "Combine JPG and PNG images into a single PDF, one image per page.",
    icon: "image",
    accept: "image/jpeg,image/png,.jpg,.jpeg,.png",
    multiple: true,
    reorderable: true,
    minFiles: 1,
    endpoint: "/api/images-to-pdf",
    fields: [
      {
        kind: "select",
        name: "page_size",
        label: "Page size",
        default: "fit",
        options: [
          { value: "fit", label: "Fit page to image" },
          { value: "a4", label: "A4 page (image centered)" },
        ],
      },
      {
        kind: "select",
        name: "orientation",
        label: "Orientation (A4 only)",
        default: "auto",
        options: [
          { value: "auto", label: "Auto" },
          { value: "portrait", label: "Portrait" },
          { value: "landscape", label: "Landscape" },
        ],
      },
    ],
    resultName: "images.pdf",
  },
  {
    slug: "pdf-to-images",
    name: "PDF to JPG/PNG",
    tagline: "Render pages as images",
    description: "Convert each PDF page into a PNG or JPEG image, delivered as a ZIP.",
    icon: "fileImage",
    accept: "application/pdf,.pdf",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/pdf-to-images",
    fields: [
      {
        kind: "select",
        name: "format",
        label: "Image format",
        default: "png",
        options: [
          { value: "png", label: "PNG (lossless)" },
          { value: "jpeg", label: "JPEG (smaller)" },
        ],
      },
      {
        kind: "number",
        name: "dpi",
        label: "Resolution (DPI)",
        default: "150",
        min: 72,
        max: 200,
        help: "Higher = sharper and larger. Clamped to 72–200.",
      },
    ],
    resultName: "pages.zip",
  },
  {
    slug: "compress-pdf",
    name: "Compress PDF",
    tagline: "Make PDFs smaller",
    description:
      "Shrink a PDF where possible. Some files (already optimized or image-heavy) may not get much smaller — we tell you honestly.",
    icon: "compress",
    accept: "application/pdf,.pdf",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/compress",
    fields: [
      {
        kind: "select",
        name: "level",
        label: "Compression",
        default: "light",
        options: [
          { value: "light", label: "Light (lossless, keeps quality)" },
          { value: "strong", label: "Strong (downsamples images)" },
        ],
      },
    ],
    resultName: "compressed.pdf",
    notes: ["If we can't reduce the size, you'll get the original back unchanged."],
  },
  {
    slug: "protect-pdf",
    name: "Protect PDF",
    tagline: "Add a password (AES)",
    description:
      "Encrypt a PDF with a password using AES. Anyone opening it will need the password. We never remove or bypass passwords.",
    icon: "lock",
    accept: "application/pdf,.pdf",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/protect",
    fields: [
      {
        kind: "password",
        name: "password",
        label: "Password",
        placeholder: "4–128 characters",
        required: true,
        help: "Choose something you'll remember — it can't be recovered.",
      },
    ],
    resultName: "protected.pdf",
  },
  {
    slug: "pdf-to-word",
    name: "PDF to Word",
    tagline: "Convert PDF to editable .docx",
    description:
      "Turn a text-based PDF into an editable Word document. Works best on digital (non-scanned) PDFs; complex layouts may shift.",
    icon: "word",
    accept: "application/pdf,.pdf",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/pdf-to-word",
    fields: [],
    resultName: "converted.docx",
    notes: [
      "Scanned / image-only PDFs won't become editable text — that needs OCR.",
      "Fonts, tables and exact layout may not match the original perfectly.",
    ],
  },
  {
    slug: "word-to-pdf",
    name: "Word to PDF",
    tagline: "Convert .doc / .docx to PDF",
    description:
      "Convert a Word document into a high-fidelity PDF. This runs on the server using LibreOffice.",
    icon: "word",
    accept:
      ".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/word-to-pdf",
    fields: [],
    resultName: "converted.pdf",
    notes: ["Requires LibreOffice on the server; you'll get a clear message if it isn't installed."],
  },
  {
    slug: "excel-to-pdf",
    name: "Excel to PDF",
    tagline: "Convert .xls / .xlsx to PDF",
    description:
      "Convert an Excel spreadsheet into a PDF. This runs on the server using LibreOffice.",
    icon: "excel",
    accept:
      ".xls,.xlsx,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/excel-to-pdf",
    fields: [],
    resultName: "converted.pdf",
    notes: ["Requires LibreOffice on the server; you'll get a clear message if it isn't installed."],
  },
  {
    slug: "ocr-pdf",
    name: "OCR PDF",
    tagline: "Make scanned PDFs searchable",
    description:
      "Run OCR on a PDF (including scans) to add a selectable text layer, or extract the plain text. Runs on the server using Tesseract.",
    icon: "ocr",
    accept: "application/pdf,.pdf",
    multiple: false,
    minFiles: 1,
    endpoint: "/api/ocr-pdf",
    fields: [
      {
        kind: "select",
        name: "output",
        label: "Output",
        default: "pdf",
        options: [
          { value: "pdf", label: "Searchable PDF" },
          { value: "text", label: "Plain text (.txt)" },
        ],
      },
      {
        kind: "text",
        name: "lang",
        label: "Language(s)",
        default: "eng",
        placeholder: "eng",
        help: "Tesseract codes, e.g. 'eng' or 'eng+hin'. Extra languages need packs installed on the server.",
      },
    ],
    resultName: "searchable.pdf",
    notes: [
      "Requires Tesseract on the server (brew install tesseract).",
      "Accuracy depends on scan quality; big files may hit the time limit.",
    ],
  },
];

export function getTool(slug: string): ToolDef | undefined {
  return TOOLS.find((t) => t.slug === slug);
}

// --- Categories & grouping (used by the sidebar, home and tool finder) ---

export type CategoryId = "organize" | "convert" | "optimize";

export interface Category {
  id: CategoryId;
  label: string;
  blurb: string;
}

export const CATEGORIES: Category[] = [
  { id: "organize", label: "Organize", blurb: "Arrange, combine and tidy up pages." },
  { id: "convert", label: "Convert", blurb: "Move between PDF, images and Office files." },
  { id: "optimize", label: "Optimize & protect", blurb: "Shrink files and lock them down." },
];

export const TOOL_CATEGORY: Record<string, CategoryId> = {
  "merge-pdf": "organize",
  "split-pdf": "organize",
  "rotate-pdf": "organize",
  "images-to-pdf": "convert",
  "pdf-to-images": "convert",
  "pdf-to-word": "convert",
  "word-to-pdf": "convert",
  "excel-to-pdf": "convert",
  "ocr-pdf": "convert",
  "compress-pdf": "optimize",
  "protect-pdf": "optimize",
};

// Shown in the "Popular tools" row on the home page, in this order.
export const POPULAR_SLUGS = ["merge-pdf", "compress-pdf", "pdf-to-word"];

export function toolsByCategory(id: CategoryId): ToolDef[] {
  return TOOLS.filter((t) => TOOL_CATEGORY[t.slug] === id);
}

export function categoryOf(slug: string): CategoryId | undefined {
  return TOOL_CATEGORY[slug];
}

export function categoryLabel(id: CategoryId): string {
  return CATEGORIES.find((c) => c.id === id)?.label ?? "";
}
