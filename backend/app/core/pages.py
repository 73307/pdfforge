"""Parse and validate user-supplied page specs like "1-3,5,8-10"."""
from __future__ import annotations

from app.core.errors import ValidationAppError

_MAX_PARTS = 200  # guard against absurd specs


def parse_ranges(spec: str, max_pages: int) -> list[tuple[int, int]]:
    spec = (spec or "").strip()
    if not spec:
        raise ValidationAppError("Specify at least one page or range (e.g. 1-3,5).")

    parts = [p.strip() for p in spec.split(",") if p.strip()]
    if len(parts) > _MAX_PARTS:
        raise ValidationAppError("Too many page ranges specified.")

    ranges: list[tuple[int, int]] = []
    for part in parts:
        if "-" in part:
            a, _, b = part.partition("-")
            try:
                start, end = int(a), int(b)
            except ValueError:
                raise ValidationAppError(f"Invalid range: {part!r}.")
        else:
            try:
                start = end = int(part)
            except ValueError:
                raise ValidationAppError(f"Invalid page: {part!r}.")
        if start < 1 or end < 1 or start > end or end > max_pages:
            raise ValidationAppError(f"Range {part!r} is out of bounds (valid pages: 1-{max_pages}).")
        ranges.append((start, end))

    if not ranges:
        raise ValidationAppError("Specify at least one page or range.")
    return ranges


def parse_pages(spec: str, max_pages: int) -> list[int]:
    """Return a sorted, de-duplicated list of 1-based page numbers."""
    pages: set[int] = set()
    for start, end in parse_ranges(spec, max_pages):
        pages.update(range(start, end + 1))
    return sorted(pages)
