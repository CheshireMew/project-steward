#!/usr/bin/env python3
"""Report read-only evidence about the immediate children of a project root."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from typing import Iterable


SCHEMA_VERSION = 1
MAX_REPORTED_ERRORS = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect top-level project paths, sizes, and Git state without changing "
            "the project. The report does not decide whether a path is used or safe "
            "to delete."
        )
    )
    parser.add_argument("root", type=Path, help="Project directory to inspect")
    parser.add_argument(
        "--no-sizes",
        action="store_true",
        help="Skip recursive size and file-count scans for large projects.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON instead of indented JSON.",
    )
    return parser.parse_args()


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    if shutil.which("git") is None:
        return None
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def git_text(root: Path, *args: str) -> str | None:
    completed = run_git(root, *args)
    if completed is None or completed.returncode != 0:
        return None
    return completed.stdout.rstrip("\r\n")


def git_root(path: Path) -> Path | None:
    value = git_text(path, "rev-parse", "--show-toplevel")
    return Path(value).resolve() if value else None


def nul_paths(root: Path, *args: str) -> list[str]:
    value = git_text(root, *args)
    if value is None:
        return []
    return [item.replace("\\", "/") for item in value.split("\0") if item]


def is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def scan_directory(path: Path) -> tuple[int, int, bool, list[str]]:
    file_count = 0
    size_bytes = 0
    complete = True
    errors: list[str] = []
    stack = [path]

    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as iterator:
                entries = list(iterator)
        except OSError as error:
            complete = False
            if len(errors) < MAX_REPORTED_ERRORS:
                errors.append(f"{current}: {error}")
            continue

        for entry in entries:
            try:
                entry_path = Path(entry.path)
                entry_stat = entry.stat(follow_symlinks=False)
                entry_reparse = entry.is_symlink() or bool(
                    getattr(entry_stat, "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
                )
                if entry.is_dir(follow_symlinks=False) and not entry_reparse:
                    stack.append(entry_path)
                else:
                    file_count += 1
                    size_bytes += entry_stat.st_size
                    if entry_reparse:
                        complete = False
            except OSError as error:
                complete = False
                if len(errors) < MAX_REPORTED_ERRORS:
                    errors.append(f"{entry.path}: {error}")

    return file_count, size_bytes, complete, errors


def path_metrics(path: Path, no_sizes: bool) -> dict[str, object]:
    reparse = is_reparse_point(path)
    if no_sizes:
        return {
            "file_count": None,
            "size_bytes": None,
            "size_complete": False,
            "scan_errors": [],
        }
    try:
        if path.is_dir() and not reparse:
            file_count, size_bytes, complete, errors = scan_directory(path)
            return {
                "file_count": file_count,
                "size_bytes": size_bytes,
                "size_complete": complete,
                "scan_errors": errors,
            }
        path_stat = path.lstat()
        return {
            "file_count": 1,
            "size_bytes": path_stat.st_size,
            "size_complete": not reparse,
            "scan_errors": [],
        }
    except OSError as error:
        return {
            "file_count": None,
            "size_bytes": None,
            "size_complete": False,
            "scan_errors": [f"{path}: {error}"],
        }


def relative_to_scan_root(path: str, prefix: str) -> str | None:
    normalized = path.strip("/")
    if not prefix:
        return normalized
    if normalized == prefix:
        return ""
    marker = f"{prefix}/"
    if normalized.startswith(marker):
        return normalized[len(marker) :]
    return None


def top_level_counts(paths: Iterable[str], prefix: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in paths:
        relative = relative_to_scan_root(path, prefix)
        if not relative:
            continue
        top = relative.split("/", 1)[0]
        counts[top] = counts.get(top, 0) + 1
    return counts


def ignore_rule(git_repository: Path, git_relative: str) -> str | None:
    completed = run_git(
        git_repository,
        "check-ignore",
        "-v",
        "--no-index",
        "--",
        git_relative,
    )
    if completed is None or completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def git_disposition(
    name: str,
    tracked_count: int,
    untracked_count: int,
    matched_ignore_rule: str | None,
) -> str:
    if name == ".git":
        return "repository_metadata"
    if tracked_count and untracked_count:
        return "mixed"
    if tracked_count:
        return "tracked"
    if matched_ignore_rule:
        return "ignored"
    if untracked_count:
        return "untracked"
    return "not_reported_by_git"


def porcelain_v1_record_count(value: str) -> int:
    fields = [field for field in value.split("\0") if field]
    count = 0
    index = 0
    while index < len(fields):
        status = fields[index][:2]
        count += 1
        index += 2 if "R" in status or "C" in status else 1
    return count


def build_report(requested_root: Path, no_sizes: bool) -> dict[str, object]:
    root = requested_root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"project root is not a directory: {root}")

    detected_git_root = git_root(root)
    git_available = shutil.which("git") is not None
    prefix = ""
    tracked_counts: dict[str, int] = {}
    untracked_counts: dict[str, int] = {}
    changed_counts: dict[str, int] = {}
    branch = None
    head = None
    dirty_entry_count = None

    if detected_git_root is not None:
        prefix_path = root.relative_to(detected_git_root)
        prefix = "" if str(prefix_path) == "." else prefix_path.as_posix()
        tracked = nul_paths(detected_git_root, "ls-files", "-z")
        untracked = nul_paths(
            detected_git_root,
            "ls-files",
            "-z",
            "--others",
            "--exclude-standard",
        )
        changed = set(nul_paths(detected_git_root, "diff", "--name-only", "-z"))
        changed.update(
            nul_paths(detected_git_root, "diff", "--cached", "--name-only", "-z")
        )
        changed.update(nul_paths(detected_git_root, "ls-files", "--deleted", "-z"))
        tracked_counts = top_level_counts(tracked, prefix)
        untracked_counts = top_level_counts(untracked, prefix)
        changed_counts = top_level_counts(changed, prefix)
        branch = git_text(detected_git_root, "branch", "--show-current") or None
        head = git_text(detected_git_root, "rev-parse", "HEAD") or None
        status = git_text(
            detected_git_root,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=normal",
        )
        dirty_entry_count = (
            porcelain_v1_record_count(status) if status is not None else None
        )

    entries: list[dict[str, object]] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name.casefold()):
        reparse = is_reparse_point(child)
        if child.is_symlink():
            kind = "symlink"
        elif child.is_dir():
            kind = "directory"
        elif child.is_file():
            kind = "file"
        else:
            kind = "other"

        matched_ignore_rule = None
        if detected_git_root is not None and child.name != ".git":
            relative = f"{prefix}/{child.name}" if prefix else child.name
            matched_ignore_rule = ignore_rule(detected_git_root, relative)

        tracked_count = tracked_counts.get(child.name, 0)
        untracked_count = untracked_counts.get(child.name, 0)
        entry = {
            "name": child.name,
            "path": str(child),
            "kind": kind,
            "is_reparse_point": reparse,
            **path_metrics(child, no_sizes),
            "git": {
                "disposition": git_disposition(
                    child.name,
                    tracked_count,
                    untracked_count,
                    matched_ignore_rule,
                ),
                "tracked_path_count": tracked_count,
                "changed_tracked_path_count": changed_counts.get(child.name, 0),
                "untracked_path_count": untracked_count,
                "ignore_rule_match": matched_ignore_rule,
            },
        }
        entries.append(entry)

    return {
        "schema_version": SCHEMA_VERSION,
        "root": {
            "requested_path": str(requested_root),
            "resolved_path": str(root),
            "git_root": str(detected_git_root) if detected_git_root else None,
            "requested_is_git_root": detected_git_root == root,
        },
        "scan": {
            "size_mode": "skipped" if no_sizes else "recursive",
            "follows_reparse_points": False,
            "top_level_entry_count": len(entries),
        },
        "git": {
            "available": git_available,
            "is_repository": detected_git_root is not None,
            "branch": branch,
            "head": head,
            "dirty_entry_count": dirty_entry_count,
        },
        "entries": entries,
        "limitations": [
            "Git state, path names, age, and size do not prove whether a path is used.",
            "Ignored and untracked paths are not automatically safe to delete.",
            (
                "The report does not inspect runtime producers, consumers, "
                "or manual workflows."
            ),
            "Reparse points are reported but never traversed.",
        ],
    }


def main() -> int:
    args = parse_args()
    try:
        report = build_report(args.root, args.no_sizes)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    indent = None if args.compact else 2
    print(json.dumps(report, ensure_ascii=False, indent=indent, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
