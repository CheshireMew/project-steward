#!/usr/bin/env python3
"""Review whether one local Git branch is contained in another without mutating Git."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class ReviewError(ValueError):
    pass


def _git(repo: Path, *args: str, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode not in allowed:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise ReviewError(f"git {' '.join(args)} failed: {detail}")
    return completed


def _branch_name(repo: Path, value: str, label: str) -> str:
    selected = value.strip()
    if not selected:
        raise ReviewError(f"{label} must be a non-empty local branch name")
    checked = _git(repo, "check-ref-format", "--branch", selected, allowed=(0, 128))
    if checked.returncode != 0:
        raise ReviewError(f"{label} is not a valid local branch name: {selected}")
    return selected


def _branch_sha(repo: Path, name: str, label: str) -> str:
    ref = f"refs/heads/{name}^{{commit}}"
    completed = _git(repo, "rev-parse", "--verify", ref, allowed=(0, 128))
    if completed.returncode != 0:
        raise ReviewError(f"{label} local branch does not exist: {name}")
    return completed.stdout.strip()


def _current_branch(repo: Path) -> str | None:
    completed = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", allowed=(0, 1))
    return completed.stdout.strip() if completed.returncode == 0 else None


def _worktrees(repo: Path) -> list[dict[str, str]]:
    output = _git(repo, "worktree", "list", "--porcelain").stdout
    result: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in [*output.splitlines(), ""]:
        if not line:
            if current:
                result.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key in {"worktree", "HEAD", "branch"}:
            if key == "worktree":
                value = str(Path(value).resolve())
            current[key.lower()] = value
    return result


def review(repository: Path, source: str, destination: str) -> dict[str, Any]:
    requested = repository.expanduser().resolve()
    if not requested.is_dir():
        raise ReviewError(f"repository directory not found: {requested}")
    root_text = _git(requested, "rev-parse", "--show-toplevel").stdout.strip()
    root = Path(root_text).resolve()
    source_name = _branch_name(root, source, "source")
    destination_name = _branch_name(root, destination, "destination")
    source_sha = _branch_sha(root, source_name, "source")
    destination_sha = _branch_sha(root, destination_name, "destination")

    ancestor = _git(
        root,
        "merge-base",
        "--is-ancestor",
        source_sha,
        destination_sha,
        allowed=(0, 1),
    ).returncode == 0
    counts = _git(root, "rev-list", "--left-right", "--count", f"{destination_sha}...{source_sha}")
    count_parts = counts.stdout.split()
    if len(count_parts) != 2:
        raise ReviewError("git rev-list did not return destination/source unique counts")
    destination_unique, source_unique = (int(value) for value in count_parts)
    base = _git(root, "merge-base", destination_sha, source_sha, allowed=(0, 1))
    merge_base = base.stdout.strip() or None

    source_ref = f"refs/heads/{source_name}"
    checked_out = [
        item["worktree"]
        for item in _worktrees(root)
        if item.get("branch") == source_ref and "worktree" in item
    ]
    current_branch = _current_branch(root)
    blockers: list[str] = []
    if source_name == destination_name:
        blockers.append("source-is-destination")
    if not ancestor or source_unique != 0:
        blockers.append("source-has-commits-not-contained-in-destination")
    if current_branch == source_name:
        blockers.append("source-is-current-branch")
    if checked_out:
        blockers.append("source-is-checked-out-in-worktree")

    return {
        "schema": "project-steward-repository-branch-containment/v1",
        "status": "reviewed",
        "scope": "local-refs-and-worktrees",
        "repository": str(root),
        "source": {"name": source_name, "sha": source_sha},
        "destination": {"name": destination_name, "sha": destination_sha},
        "same_tip": source_sha == destination_sha,
        "merge_base": merge_base,
        "contained_in_current_graph": ancestor and source_unique == 0,
        "source_unique_commits": source_unique,
        "destination_unique_commits": destination_unique,
        "current_branch": current_branch,
        "source_checked_out_worktrees": checked_out,
        "technically_eligible_for_local_delete": not blockers,
        "deletion_blockers": blockers,
        "authorization": "not-evaluated-by-read-only-review",
        "remote_state": "not-queried",
        "historical_merge_mechanism": "not-inferred-from-containment",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = review(args.repository, args.source, args.destination)
        print(json.dumps(payload, ensure_ascii=False, indent=None if args.compact else 2))
        return 0
    except (OSError, ReviewError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
