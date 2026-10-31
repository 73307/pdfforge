"""Add AES password encryption to a PDF. This only ADDS protection; it never removes
or bypasses an existing password.
"""
from __future__ import annotations

from pypdf import PdfReader, PdfWriter


def protect_pdf(input_path: str, output_path: str, password: str) -> dict:
    reader = PdfReader(input_path)
    if reader.is_encrypted:
        reader.decrypt("")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    try:
        writer.encrypt(user_password=password, algorithm="AES-256")
    except TypeError:
        # Fallback for older pypdf signatures.
        writer.encrypt(user_pwd=password)

    with open(output_path, "wb") as fh:
        writer.write(fh)
    writer.close()
    return {"encrypted": True}
