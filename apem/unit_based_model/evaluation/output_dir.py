"""Helpers for creating evaluation output directories with Windows-safe name lengths."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re

DEFAULT_OUTPUT_DIR_NAME_MAX_LENGTH = 64
_NON_ALNUM_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")


def create_timestamped_output_dir(
    evaluation_root: Path,
    *name_parts: str,
    max_dir_name_length: int = DEFAULT_OUTPUT_DIR_NAME_MAX_LENGTH,
) -> Path:
    """
    Create a timestamped output directory with bounded folder-name length.

    On Windows, long absolute paths can fail around the default 260-character
    limit. This helper keeps the timestamped folder segment compact and appends
    a stable hash when truncation is required.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sanitized_parts = [_sanitize_part(part) for part in name_parts if str(part).strip()]
    descriptor = "_".join(part for part in sanitized_parts if part)

    folder_name = timestamp
    if descriptor:
        folder_name = _truncate_with_hash(f"{timestamp}_{descriptor}", max_dir_name_length)

    output_dir = evaluation_root / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _sanitize_part(value: str) -> str:
    cleaned = _NON_ALNUM_PATTERN.sub("_", str(value).strip())
    return cleaned.strip("_.-")


def _truncate_with_hash(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value

    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    separator = "_"
    head_budget = max_length - len(separator) - len(digest)
    if head_budget <= 0:
        return digest[:max_length]

    head = value[:head_budget].rstrip("_.-")
    if not head:
        return digest[:max_length]
    return f"{head}{separator}{digest}"
