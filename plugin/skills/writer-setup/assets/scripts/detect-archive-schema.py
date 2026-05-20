#!/usr/bin/env python3
"""
detect-archive-schema.py — eis-content-builder v0.6.0

Deterministic detector for the YAML frontmatter schema of an author's
article archive. Called by the `/writer-setup` skill during first-time
setup. Returns a JSON document on stdout that the calling skill consumes.

Falls back to the `archive-detector` LLM agent when this script fails
(non-zero exit, exception, malformed JSON).

USAGE
    python3 detect-archive-schema.py --path /absolute/path/to/archive

OUTPUT
    JSON on stdout. Exit code 0 on success, non-zero on failure with
    structured error JSON on stderr (so the caller can still parse the
    reason).

DESIGN
    - No external dependencies (uses only the Python stdlib).
    - YAML parsing is implemented as a minimal frontmatter-only parser
      that handles scalars, lists, and one level of nesting — enough for
      the use case. We do NOT depend on PyYAML.
    - Read-only: never writes anywhere.
    - Refuses ephemeral paths.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EPHEMERAL_PREFIXES = (
    "/sessions/",
    "/tmp/",
    "/private/tmp/",
    "/var/folders/",
)
EPHEMERAL_CONTAINS = ("/worktrees/",)

# Top-level /mnt/ is ephemeral too, but only when it's the IMMEDIATE root.
# /mnt/foo/... → ephemeral. /home/user/mnt/foo → fine.
EPHEMERAL_TOP_LEVEL = ("/mnt/",)

FILE_GLOB_ORDER = ("**/*.md", "**/*.mdx", "**/*.markdown", "**/*.html", "**/*.txt")

ROLE_LOOKUPS: dict[str, tuple[str, ...]] = {
    "title_property":   ("title", "headline", "name"),
    "tags_property":    ("tags", "categories", "category", "topics", "tag"),
    "status_property":  ("status", "state", "draft", "published"),
    "date_property":    ("date", "created", "created_at", "publishedat",
                         "published_date", "pubdate", "created time"),
    "url_property":     ("permalink", "url", "link", "canonical_url", "slug"),
    "excerpt_property": ("excerpt", "summary", "description", "subtitle"),
}

MAX_SAMPLES = 5
MAX_LINES_PER_FILE = 80


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_ephemeral(p: str) -> bool:
    """Return True if the path points to an ephemeral OS location."""
    real = os.path.realpath(p)
    for prefix in EPHEMERAL_PREFIXES:
        if real.startswith(prefix):
            return True
    for needle in EPHEMERAL_CONTAINS:
        if needle in real:
            return True
    for prefix in EPHEMERAL_TOP_LEVEL:
        # Top-level /mnt/foo but not /home/user/mnt/foo
        if real.startswith(prefix):
            return True
    return False


def detect_toolchain(archive_path: Path) -> str:
    """Walk up from archive_path looking for .obsidian/."""
    current = archive_path.resolve()
    root = Path(current.anchor or "/")
    while True:
        if (current / ".obsidian").is_dir():
            return "obsidian"
        if current == root:
            return "generic"
        parent = current.parent
        if parent == current:  # safety net
            return "generic"
        current = parent


def pick_glob(archive_path: Path) -> tuple[str | None, list[Path]]:
    """Try globs in order; return (pattern, matched_files) for the first
    pattern that yields results. (None, []) if nothing matches."""
    for pattern in FILE_GLOB_ORDER:
        matches = list(archive_path.glob(pattern))
        # Filter to real files (skip directories that happen to end in .md/etc.)
        matches = [m for m in matches if m.is_file()]
        if matches:
            return pattern, matches
    return None, []


def pick_sample_files(matches: list[Path], n: int = MAX_SAMPLES) -> list[Path]:
    """Pick up to n files from the matches. Prefer recently modified."""
    try:
        matches_sorted = sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        matches_sorted = sorted(matches)
    return matches_sorted[:n]


def read_head(path: Path, max_lines: int = MAX_LINES_PER_FILE) -> str:
    """Read the first N lines of a file, returning the text content.
    Returns empty string on any read error (caller decides how to handle)."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            lines: list[str] = []
            for i, line in enumerate(fh):
                if i >= max_lines:
                    break
                lines.append(line)
            return "".join(lines)
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Minimal frontmatter parser
# ---------------------------------------------------------------------------

FRONTMATTER_FENCE = re.compile(r"^---\s*$")
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_\-\s]+?):\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")


def extract_frontmatter(text: str) -> dict[str, Any]:
    """Extract YAML frontmatter from the start of `text`.

    Supports:
      - Scalars:  key: value
      - Inline lists: key: [a, b, c]
      - Block lists:
            key:
              - a
              - b
      - Nested objects are NOT supported (the use case is flat).

    Returns {} if no frontmatter or malformed.
    """
    lines = text.splitlines()
    if not lines or not FRONTMATTER_FENCE.match(lines[0]):
        return {}

    # Find closing fence
    end = None
    for i in range(1, len(lines)):
        if FRONTMATTER_FENCE.match(lines[i]):
            end = i
            break
    if end is None:
        return {}

    body = lines[1:end]
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    current_list: list[str] = []

    def commit_list() -> None:
        nonlocal current_list_key, current_list
        if current_list_key is not None:
            result[current_list_key.strip().lower()] = current_list
        current_list_key = None
        current_list = []

    for raw in body:
        # Skip empty / comment lines
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List continuation
        list_match = LIST_ITEM_RE.match(raw)
        if list_match and current_list_key is not None:
            current_list.append(_clean_scalar(list_match.group(1)))
            continue

        # Otherwise commit any pending list and parse a key:value
        commit_list()

        kv = KEY_VALUE_RE.match(raw)
        if not kv:
            continue
        key_raw, value_raw = kv.group(1), kv.group(2).strip()
        key = key_raw.strip().lower()

        if value_raw == "" or value_raw == "|" or value_raw == ">":
            # Either an empty value or the start of a block list (next lines)
            current_list_key = key
            current_list = []
            continue

        # Inline list  [a, b, c]
        if value_raw.startswith("[") and value_raw.endswith("]"):
            inner = value_raw[1:-1].strip()
            items = [_clean_scalar(x) for x in inner.split(",")] if inner else []
            result[key] = items
            continue

        # Plain scalar
        result[key] = _clean_scalar(value_raw)

    commit_list()
    return result


def _clean_scalar(s: str) -> str:
    """Strip surrounding quotes and whitespace from a scalar string."""
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


# ---------------------------------------------------------------------------
# Role mapping
# ---------------------------------------------------------------------------

def map_roles(field_frequency: Counter[str]) -> tuple[dict[str, str | None], list[str]]:
    """Map known frontmatter keys to roles. Returns (schema, warnings)."""
    schema: dict[str, str | None] = {}
    warnings: list[str] = []

    for role, candidates in ROLE_LOOKUPS.items():
        matched_key: str | None = None
        for candidate in candidates:
            if field_frequency.get(candidate, 0) > 0:
                # Tie-break: if a later (less preferred) key has higher freq
                # we still take the first match (preference order > freq).
                matched_key = candidate
                break

        # Inconsistency warning: another candidate also appears
        if matched_key is not None:
            others = [
                c for c in candidates
                if c != matched_key and field_frequency.get(c, 0) > 0
            ]
            if others:
                detail = ", ".join(
                    f"{c} ({field_frequency[c]})" for c in [matched_key] + others
                )
                warnings.append(f"inconsistent-{role}: {detail}")

        schema[role] = matched_key

    return schema, warnings


def published_values_observed(
    samples: list[dict[str, Any]], status_property: str | None
) -> list[str]:
    """If status_property is set, collect distinct values for it across samples."""
    if status_property is None:
        return []
    seen: list[str] = []
    for fm in samples:
        v = fm.get(status_property)
        if v is None:
            continue
        if isinstance(v, list):
            for x in v:
                if isinstance(x, str) and x not in seen:
                    seen.append(x)
        elif isinstance(v, str) and v not in seen:
            seen.append(v)
    return seen


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(archive_path_str: str) -> dict[str, Any]:
    # 1. Validate path
    if not os.path.isabs(archive_path_str):
        return {"ok": False, "error": "archive-path-not-absolute", "path": archive_path_str}

    archive_path = Path(archive_path_str).expanduser()
    if not archive_path.exists():
        return {"ok": False, "error": "archive-path-not-found", "path": str(archive_path)}
    if not archive_path.is_dir():
        return {"ok": False, "error": "archive-path-not-directory", "path": str(archive_path)}

    # 2. Ephemeral guard (realpath-aware)
    if is_ephemeral(str(archive_path)):
        return {"ok": False, "error": "ephemeral-archive-path", "path": str(archive_path)}

    # 3. Toolchain
    toolchain = detect_toolchain(archive_path)

    # 4. Pick glob
    file_pattern, matches = pick_glob(archive_path)
    if file_pattern is None:
        return {
            "ok": False,
            "error": "no-content-files",
            "archive_path": str(archive_path),
            "toolchain": toolchain,
        }

    # 5. Sample
    chosen = pick_sample_files(matches)
    samples_frontmatter: list[dict[str, Any]] = []
    read_failures: list[str] = []

    for path in chosen:
        text = read_head(path)
        if not text:
            read_failures.append(str(path))
            continue
        fm = extract_frontmatter(text)
        samples_frontmatter.append(fm)

    if not samples_frontmatter:
        return {
            "ok": False,
            "error": "all-reads-failed-or-no-frontmatter",
            "archive_path": str(archive_path),
            "toolchain": toolchain,
            "file_pattern": file_pattern,
            "samples_attempted": len(chosen),
            "read_failures": read_failures,
        }

    # 6. Field frequency
    freq: Counter[str] = Counter()
    for fm in samples_frontmatter:
        for key in fm.keys():
            freq[key] += 1

    # 7. Role mapping
    schema, warnings = map_roles(freq)

    # 8. published_values_observed
    pub_vals = published_values_observed(samples_frontmatter, schema.get("status_property"))

    if read_failures:
        warnings.append(f"read-failures-count: {len(read_failures)}")

    return {
        "ok": True,
        "method": "python-script",
        "archive_path": str(archive_path),
        "toolchain": toolchain,
        "file_pattern": file_pattern,
        "samples_analyzed": len(samples_frontmatter),
        "schema": schema,
        "published_values_observed": pub_vals,
        "field_frequency": dict(freq),
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect the YAML frontmatter schema of an article archive."
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Absolute path to the archive folder.",
    )
    args = parser.parse_args()

    try:
        result = run(args.path)
    except Exception as exc:
        err = {
            "ok": False,
            "error": "uncaught-exception",
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
        print(json.dumps(err), file=sys.stderr)
        return 2

    print(json.dumps(result))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
