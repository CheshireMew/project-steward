#!/usr/bin/env python3
"""Measure Project Steward active text and root-router budgets."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_OUTER_TOOL_TOKENS = 9_000
BYTES_PER_OUTER_TOOL_TOKEN = 4
MAX_SKILL_LINES = 220
MAX_SKILL_CHARACTERS = 14_000
SKILL_ROUTER_PATH = Path("SKILL.md")
# Repository-local diagnostic evidence, matching the root-only .gitignore entry.
IGNORED_ROOT_DIRECTORY_NAMES = {".qa"}
IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "archive",
    "artifacts",
    "build",
    "dist",
    "node_modules",
    "output",
    "outputs",
    "venv",
}
TEXT_ASSET_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".toml",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class FileBudget:
    """One active UTF-8 text file and every applicable size measure."""

    path: Path
    byte_count: int
    estimated_tokens: int
    line_count: int
    character_count: int


def estimate_outer_tool_tokens(byte_count: int) -> int:
    """Return the outer tool's approximate token count for UTF-8 bytes.

    @param byte_count: Number of UTF-8 bytes emitted for the file.
    @returns: Approximate output tokens, rounded up.
    """

    return (byte_count + BYTES_PER_OUTER_TOOL_TOKEN - 1) // BYTES_PER_OUTER_TOOL_TOKEN


def _is_budgeted_path(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    if len(relative.parts) > 1 and relative.parts[0] in IGNORED_ROOT_DIRECTORY_NAMES:
        return False
    if any(part in IGNORED_DIRECTORY_NAMES for part in relative.parts[:-1]):
        return False
    if relative.parts and relative.parts[0] == "assets":
        return path.suffix.lower() in TEXT_ASSET_SUFFIXES
    return True


def collect_file_budgets(root: Path) -> list[FileBudget]:
    """Collect every active UTF-8 text file covered by the Skill budget.

    @param root: Skill directory to inspect.
    @returns: Stable path-sorted file budget records.
    """

    records: list[FileBudget] = []
    for current, directories, files in os.walk(root):
        current_path = Path(current)
        directories[:] = sorted(
            name
            for name in directories
            if name not in IGNORED_DIRECTORY_NAMES
            and not (current_path == root and name in IGNORED_ROOT_DIRECTORY_NAMES)
        )
        for name in sorted(files):
            path = current_path / name
            if not _is_budgeted_path(root, path):
                continue
            data = path.read_bytes()
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
            byte_count = len(data)
            records.append(
                FileBudget(
                    path=path.relative_to(root),
                    byte_count=byte_count,
                    estimated_tokens=estimate_outer_tool_tokens(byte_count),
                    line_count=len(normalized_text.splitlines()),
                    character_count=len(normalized_text),
                )
            )
    return sorted(records, key=lambda record: record.path.as_posix())


def validate_budget_records(records: list[FileBudget]) -> list[str]:
    """Report every active-text or root-router budget violation."""

    errors: list[str] = []
    for record in records:
        if record.estimated_tokens > MAX_OUTER_TOOL_TOKENS:
            errors.append(
                "active text file exceeds the outer-tool budget: "
                f"{record.path.as_posix()} "
                f"({record.estimated_tokens} estimated tokens, "
                f"{record.byte_count} UTF-8 bytes, limit {MAX_OUTER_TOOL_TOKENS})"
            )
        if record.path != SKILL_ROUTER_PATH:
            continue
        if record.line_count > MAX_SKILL_LINES:
            errors.append(
                "SKILL.md exceeds the root-router line budget: "
                f"{record.line_count} lines (limit {MAX_SKILL_LINES})"
            )
        if record.character_count > MAX_SKILL_CHARACTERS:
            errors.append(
                "SKILL.md exceeds the root-router character budget: "
                f"{record.character_count} characters "
                f"(limit {MAX_SKILL_CHARACTERS})"
            )
    return errors


def validate_file_budgets(root: Path) -> list[str]:
    """Collect and validate every budget owned by this public checker.

    @param root: Skill directory to inspect.
    @returns: Validation errors for every applicable hard limit.
    """

    return validate_budget_records(collect_file_budgets(root))


def main(argv: list[str]) -> int:
    """Print the complete active-file ledger and fail on an oversized file."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_folder",
        nargs="?",
        default=".",
        help="Skill directory to inspect; defaults to the current directory",
    )
    args = parser.parse_args(argv[1:])
    root = Path(args.skill_folder).resolve()
    records = collect_file_budgets(root)
    for record in sorted(
        records,
        key=lambda item: (-item.estimated_tokens, item.path.as_posix()),
    ):
        line = (
            f"{record.estimated_tokens:>6} tokens  "
            f"{MAX_OUTER_TOOL_TOKENS - record.estimated_tokens:>5} remaining  "
            f"{record.byte_count:>7} bytes  {record.path.as_posix()}"
        )
        if record.path == SKILL_ROUTER_PATH:
            line += (
                f"  {record.line_count}/{MAX_SKILL_LINES} lines "
                f"({MAX_SKILL_LINES - record.line_count} remaining)"
                f"  {record.character_count}/{MAX_SKILL_CHARACTERS} characters "
                f"({MAX_SKILL_CHARACTERS - record.character_count} remaining)"
            )
        print(line)

    errors = validate_budget_records(records)
    if errors:
        print("FILE BUDGET FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"FILE BUDGET PASS {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
