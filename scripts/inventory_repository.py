#!/usr/bin/env python3
"""Create a read-only repository inventory for license and stewardship review."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


SCHEMA_VERSION = 2
LICENSE_BASENAMES = {
    "copying",
    "copying.md",
    "copying.txt",
    "license",
    "license.md",
    "license.rst",
    "license.txt",
    "licence",
    "licence.md",
    "licence.txt",
    "licensing",
    "licensing.md",
    "licensing.rst",
    "licensing.txt",
    "notice",
    "notice.md",
    "notice.txt",
    "third_party_notices",
    "third_party_notices.md",
    "third-party-notices",
    "third-party-notices.md",
}
README_PATTERN = re.compile(r"^readme(?:\.[^.]+)?\.(?:md|markdown|rst|txt)$", re.I)
SPDX_PATTERN = re.compile(
    r"SPDX-License-Identifier:\s*([A-Za-z0-9.+\-()\s]+)", re.I
)
MANIFEST_NAMES = {
    "cargo.toml",
    "composer.json",
    "deno.json",
    "deno.jsonc",
    "gemfile",
    "go.mod",
    "mix.exs",
    "package.json",
    "pom.xml",
    "pubspec.yaml",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
}
LOCK_NAMES = {
    "bun.lock",
    "bun.lockb",
    "cargo.lock",
    "composer.lock",
    "deno.lock",
    "gemfile.lock",
    "go.sum",
    "package-lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
}
THIRD_PARTY_DIRS = {
    ".venv",
    "env",
    "externals",
    "node_modules",
    "site-packages",
    "third-party",
    "third_party",
    "vendor",
    "vendored",
    "venv",
}
GENERATED_DIRS = {
    ".cache",
    ".next",
    "build",
    "coverage",
    "dist",
    "generated",
    "out",
    "output",
    "outputs",
    "target",
    "tmp",
}
CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".dart",
    ".ex",
    ".exs",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".lua",
    ".m",
    ".php",
    ".ps1",
    ".py",
    ".r",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
DOCUMENT_EXTENSIONS = {
    ".adoc",
    ".doc",
    ".docx",
    ".epub",
    ".md",
    ".markdown",
    ".pdf",
    ".ppt",
    ".pptx",
    ".rst",
    ".tex",
    ".txt",
}
DATA_EXTENSIONS = {
    ".arrow",
    ".avro",
    ".csv",
    ".db",
    ".feather",
    ".geojson",
    ".jsonl",
    ".ndjson",
    ".parquet",
    ".sqlite",
    ".sqlite3",
    ".tsv",
}
MODEL_EXTENSIONS = {
    ".bin",
    ".ckpt",
    ".gguf",
    ".onnx",
    ".pt",
    ".pth",
    ".safetensors",
    ".tflite",
}
MEDIA_EXTENSIONS = {
    ".apng",
    ".avif",
    ".bmp",
    ".flac",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".m4a",
    ".mov",
    ".mp3",
    ".mp4",
    ".ogg",
    ".png",
    ".svg",
    ".wav",
    ".webm",
    ".webp",
}
FONT_EXTENSIONS = {".eot", ".otf", ".ttf", ".woff", ".woff2"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect local repositories or an authenticated GitHub portfolio "
            "without choosing or applying a license."
        )
    )
    subparsers = parser.add_subparsers(dest="source_kind", required=True)

    local_parser = subparsers.add_parser("local", help="Inventory one local directory")
    local_parser.add_argument("repository", type=Path)

    github_parser = subparsers.add_parser(
        "github", help="Inventory repositories through the authenticated GitHub CLI"
    )
    github_parser.add_argument("--owner", required=True)
    github_parser.add_argument(
        "--visibility",
        choices=("public", "private", "all"),
        default="public",
        help="Repository visibility scope; public is the safe default.",
    )
    github_parser.add_argument(
        "--repository",
        action="append",
        default=[],
        help="Limit the inventory to one repository name; repeat as needed.",
    )

    for child in (local_parser, github_parser):
        child.add_argument(
            "--output",
            type=Path,
            help="Write JSON to this file instead of stdout; existing files are refused.",
        )
        child.add_argument(
            "--compact",
            action="store_true",
            help="Emit compact JSON instead of indented JSON.",
        )
    return parser.parse_args()


def is_license_or_notice_path(relative: str) -> bool:
    path = Path(relative)
    name = path.name
    lowered = name.lower()
    if lowered in LICENSE_BASENAMES:
        return True
    if (
        path.parent.name.lower() in {"license", "licenses", "licence", "licences"}
        and path.suffix.lower() in {"", ".md", ".rst", ".txt"}
    ):
        return True
    for suffix in (".md", ".rst", ".txt"):
        if lowered.endswith(suffix):
            lowered = lowered[: -len(suffix)]
            break
    variant = (
        lowered.startswith(
            ("license-", "licence-", "licensing-", "copying-", "notice-")
        )
        or lowered.endswith(("-license", "-licence", "-licensing", "-notice"))
        or lowered
        in {
            "asset-license",
            "licensing",
            "third-party-notices",
            "third_party_notices",
        }
    )
    if not variant:
        return False
    if len(path.parts) == 1:
        return True
    unsuffixed = name[: -len(path.suffix)] if path.suffix else name
    return any(character.isalpha() for character in unsuffixed) and unsuffixed.upper() == unsuffixed


def run_git(root: Path, *arguments: str, check: bool = False) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.rstrip("\r\n")


def git_root(path: Path) -> Path | None:
    value = run_git(path, "rev-parse", "--show-toplevel")
    return Path(value).resolve() if value else None


def tracked_files(root: Path, is_git: bool) -> list[str]:
    if is_git:
        output = run_git(root, "ls-files", "-z")
        if output is not None:
            return sorted(item.replace("\\", "/") for item in output.split("\0") if item)

    excluded = {".git", *THIRD_PARTY_DIRS, *GENERATED_DIRS}
    results: list[str] = []
    for current, directories, filenames in os.walk(root):
        directories[:] = sorted(
            name for name in directories if name.lower() not in excluded
        )
        current_path = Path(current)
        for filename in sorted(filenames):
            results.append((current_path / filename).relative_to(root).as_posix())
    return sorted(results)


def observed_special_directories(root: Path) -> tuple[list[str], list[str]]:
    third_party: set[str] = set()
    generated: set[str] = set()
    skipped = {".git", *THIRD_PARTY_DIRS, *GENERATED_DIRS}
    for current, directories, _ in os.walk(root):
        current_path = Path(current)
        next_directories: list[str] = []
        for name in directories:
            lowered = name.lower()
            relative = (current_path / name).relative_to(root).as_posix()
            if lowered in THIRD_PARTY_DIRS:
                third_party.add(relative)
            elif lowered in GENERATED_DIRS:
                generated.add(relative)
            if lowered not in skipped:
                next_directories.append(name)
        directories[:] = sorted(next_directories)
    return sorted(third_party), sorted(generated)


def tracked_special_directories(paths: list[Path]) -> tuple[list[str], list[str]]:
    third_party: set[str] = set()
    generated: set[str] = set()
    for path in paths:
        for index, part in enumerate(path.parts[:-1]):
            relative = Path(*path.parts[: index + 1]).as_posix()
            if part.lower() in THIRD_PARTY_DIRS:
                third_party.add(relative)
            if part.lower() in GENERATED_DIRS:
                generated.add(relative)
    return sorted(third_party), sorted(generated)


def classify_file(relative: str) -> str:
    path = Path(relative)
    suffix = path.suffix.lower()
    if is_license_or_notice_path(relative):
        return "license_or_notice"
    if suffix in CODE_EXTENSIONS:
        return "code"
    if suffix in DOCUMENT_EXTENSIONS:
        return "documentation"
    if suffix in DATA_EXTENSIONS:
        return "data"
    if suffix in MODEL_EXTENSIONS:
        return "model"
    if suffix in MEDIA_EXTENSIONS:
        return "media"
    if suffix in FONT_EXTENSIONS:
        return "font"
    return "other"


def scan_spdx(root: Path, files: list[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    text_candidates = {
        ".c",
        ".cc",
        ".cpp",
        ".css",
        ".go",
        ".h",
        ".hpp",
        ".html",
        ".java",
        ".js",
        ".jsx",
        ".md",
        ".php",
        ".ps1",
        ".py",
        ".rb",
        ".rs",
        ".sh",
        ".ts",
        ".tsx",
        ".vue",
        ".yaml",
        ".yml",
    }
    for relative in files:
        path = root / relative
        if path.suffix.lower() not in text_candidates or not path.is_file():
            continue
        try:
            if path.stat().st_size > 512 * 1024:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        matches = {match.strip() for match in SPDX_PATTERN.findall(text)}
        if matches:
            found[relative] = sorted(matches)
    return found


def repository_state(root: Path, is_git: bool) -> dict:
    if not is_git:
        return {
            "current_branch": None,
            "default_branch": None,
            "default_branch_source": None,
            "head_sha": None,
            "origin": None,
            "upstream": None,
            "dirty_entry_count": None,
            "contributors": [],
            "submodules": [],
        }

    current_branch = run_git(root, "branch", "--show-current") or None
    default_ref = run_git(
        root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"
    )
    if default_ref and "/" in default_ref:
        default_branch = default_ref.split("/", 1)[1]
        default_branch_source = "origin/HEAD"
    else:
        default_branch = current_branch
        default_branch_source = "current-branch" if current_branch else None
    status = run_git(root, "status", "--porcelain=v1", "-z") or ""
    contributors_output = run_git(root, "log", "--format=%aN") or ""
    contributors = sorted({name.strip() for name in contributors_output.splitlines() if name.strip()})
    submodule_output = run_git(root, "submodule", "status", "--recursive") or ""

    return {
        "current_branch": current_branch,
        "default_branch": default_branch,
        "default_branch_source": default_branch_source,
        "head_sha": run_git(root, "rev-parse", "HEAD") or None,
        "origin": run_git(root, "remote", "get-url", "origin") or None,
        "upstream": run_git(root, "remote", "get-url", "upstream") or None,
        "dirty_entry_count": len([item for item in status.split("\0") if item]),
        "contributors": contributors,
        "submodules": [
            line.lstrip(" +-").split(" ", 1)[1].split(" ", 1)[0]
            for line in submodule_output.splitlines()
            if " " in line
        ],
    }


def build_local_inventory(repository: Path) -> dict:
    requested = repository.expanduser().resolve()
    if not requested.is_dir():
        raise ValueError(f"repository directory not found: {requested}")

    detected_root = git_root(requested)
    root = detected_root or requested
    is_git = detected_root is not None
    files = tracked_files(root, is_git)
    paths = [Path(relative) for relative in files]

    license_files = sorted(
        relative for relative in files if is_license_or_notice_path(relative)
    )
    readmes = sorted(
        relative
        for relative in files
        if README_PATTERN.match(Path(relative).name)
        or Path(relative).name.lower() in {"readme", "readme.md", "readme.rst", "readme.txt"}
    )
    manifests = sorted(
        relative for relative in files if Path(relative).name.lower() in MANIFEST_NAMES
    )
    locks = sorted(relative for relative in files if Path(relative).name.lower() in LOCK_NAMES)
    if is_git:
        third_party_directories, generated_directories = tracked_special_directories(
            paths
        )
    else:
        third_party_directories, generated_directories = observed_special_directories(
            root
        )
    nested_license_files = [
        relative for relative in license_files if len(Path(relative).parts) > 1
    ]
    licensing_scope_files = [
        relative
        for relative in license_files
        if Path(relative).name.lower()
        in {"licensing", "licensing.md", "licensing.rst", "licensing.txt"}
    ]
    state = repository_state(root, is_git)
    content_counts = Counter(classify_file(relative) for relative in files)
    spdx_identifiers = scan_spdx(root, files)

    signals: list[dict[str, object]] = []
    if state["upstream"]:
        signals.append({"kind": "upstream_remote", "value": state["upstream"]})
    if state["submodules"]:
        signals.append({"kind": "git_submodules", "value": state["submodules"]})
    if third_party_directories:
        signals.append(
            {"kind": "third_party_directories", "value": third_party_directories}
        )
    if nested_license_files:
        signals.append({"kind": "nested_license_files", "value": nested_license_files})
    if len(state["contributors"]) > 1:
        signals.append(
            {"kind": "multiple_git_authors", "value": len(state["contributors"])}
        )
    if content_counts["media"] or content_counts["font"] or content_counts["model"]:
        signals.append(
            {
                "kind": "non_code_assets",
                "value": {
                    key: content_counts[key]
                    for key in ("media", "font", "model")
                    if content_counts[key]
                },
            }
        )
    if content_counts["data"]:
        signals.append({"kind": "data_files", "value": content_counts["data"]})

    repository_record = {
        "repository": {
            "requested_path": str(requested),
            "root": str(root),
            "name": root.name,
            "name_with_owner": None,
            "url": None,
            "visibility": None,
            "is_fork": None,
            "parent": None,
            "license_detection": None,
            "is_git_repository": is_git,
            **state,
        },
        "file_basis": "git-tracked" if is_git else "filesystem-scan-with-exclusions",
        "file_count": len(files),
        "content_counts": dict(sorted(content_counts.items())),
        "readme_files": readmes,
        "license_and_notice_files": license_files,
        "licensing_scope_files": licensing_scope_files,
        "manifest_files": manifests,
        "lock_files": locks,
        "third_party_directories": third_party_directories,
        "generated_directories": generated_directories,
        "spdx_identifiers_in_files": spdx_identifiers,
        "review_signals": signals,
        "limitations": [
            "This inventory reports repository evidence and does not choose a license.",
            "Git author names do not prove current copyright ownership or relicensing authority.",
            "Absence of a detected signal does not prove that all content is original.",
            "For non-Git directories, dependency and generated directories are reported but not traversed.",
        ],
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "kind": "local",
            "requested_path": str(requested),
        },
        "repository_count": 1,
        "repositories": [repository_record],
    }


class GitHubCommandError(ValueError):
    """Raised when an authenticated GitHub CLI read fails."""


def run_gh_json(
    arguments: list[str], *, allow_empty_repository: bool = False
) -> object | None:
    try:
        completed = subprocess.run(
            ["gh", *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise GitHubCommandError(
            "GitHub CLI 'gh' is not installed; install and authenticate it outside "
            "this script before using the github inventory."
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        if allow_empty_repository and any(
            marker in detail for marker in ("HTTP 404", "HTTP 409", "Git Repository is empty")
        ):
            return None
        raise GitHubCommandError(
            f"GitHub CLI read failed ({' '.join(arguments)}): {detail}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise GitHubCommandError(
            f"GitHub CLI returned invalid JSON for {' '.join(arguments)}"
        ) from exc


def require_authenticated_gh() -> None:
    if shutil.which("gh") is None:
        raise GitHubCommandError(
            "GitHub CLI 'gh' is not installed; this script does not install tools."
        )
    completed = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise GitHubCommandError(
            "GitHub CLI is not authenticated; run 'gh auth login' yourself before "
            f"using this read-only inventory. Details: {detail}"
        )


def normalized_repository_name(owner: str, value: str) -> str:
    candidate = value.strip().strip("/")
    if not candidate:
        raise ValueError("--repository cannot be empty")
    if "/" not in candidate:
        return f"{owner}/{candidate}"
    parts = candidate.split("/")
    if len(parts) != 2 or parts[0].casefold() != owner.casefold() or not parts[1]:
        raise ValueError(
            f"repository '{value}' must belong to the requested owner '{owner}'"
        )
    return f"{parts[0]}/{parts[1]}"


def github_repository_names(
    owner: str, visibility: str, selected: list[str]
) -> list[str]:
    if selected:
        names = [normalized_repository_name(owner, value) for value in selected]
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError("--repository contains duplicates")
        return sorted(names, key=str.casefold)

    arguments = [
        "repo",
        "list",
        owner,
        "--limit",
        "1000",
        "--json",
        "nameWithOwner",
    ]
    if visibility != "all":
        arguments.extend(["--visibility", visibility])
    data = run_gh_json(arguments)
    if not isinstance(data, list):
        raise GitHubCommandError("GitHub repository list must be a JSON array")
    names = [
        item.get("nameWithOwner")
        for item in data
        if isinstance(item, dict) and isinstance(item.get("nameWithOwner"), str)
    ]
    return sorted(set(names), key=str.casefold)


def remote_special_directories(paths: list[str]) -> tuple[list[str], list[str]]:
    return tracked_special_directories([Path(path) for path in paths])


def github_repository_record(full_name: str, visibility_scope: str) -> dict:
    metadata = run_gh_json(["api", f"repos/{full_name}"])
    if not isinstance(metadata, dict):
        raise GitHubCommandError(f"invalid GitHub metadata for {full_name}")
    actual_visibility = str(metadata.get("visibility") or "").lower()
    if visibility_scope != "all" and actual_visibility != visibility_scope:
        raise ValueError(
            f"{full_name} is {actual_visibility or 'unknown'}, outside the "
            f"requested {visibility_scope} scope"
        )

    branch = metadata.get("default_branch")
    branch = branch if isinstance(branch, str) and branch else None
    head_sha: str | None = None
    tree_sha: str | None = None
    tree_items: list[dict] = []
    tree_truncated = False
    if branch:
        encoded_branch = quote(branch, safe="")
        reference = run_gh_json(
            ["api", f"repos/{full_name}/git/ref/heads/{encoded_branch}"],
            allow_empty_repository=True,
        )
        if isinstance(reference, dict):
            reference_object = reference.get("object")
            if isinstance(reference_object, dict) and isinstance(
                reference_object.get("sha"), str
            ):
                head_sha = reference_object["sha"]
        if head_sha:
            commit = run_gh_json(
                ["api", f"repos/{full_name}/git/commits/{head_sha}"]
            )
            if isinstance(commit, dict) and isinstance(commit.get("tree"), dict):
                value = commit["tree"].get("sha")
                tree_sha = value if isinstance(value, str) else None
        if tree_sha:
            tree = run_gh_json(
                ["api", f"repos/{full_name}/git/trees/{tree_sha}?recursive=1"]
            )
            if isinstance(tree, dict):
                raw_items = tree.get("tree")
                if isinstance(raw_items, list):
                    tree_items = [item for item in raw_items if isinstance(item, dict)]
                tree_truncated = bool(tree.get("truncated"))

    files = sorted(
        item["path"]
        for item in tree_items
        if item.get("type") == "blob" and isinstance(item.get("path"), str)
    )
    license_files = sorted(
        relative for relative in files if is_license_or_notice_path(relative)
    )
    readmes = sorted(
        relative
        for relative in files
        if README_PATTERN.match(Path(relative).name)
        or Path(relative).name.lower()
        in {"readme", "readme.md", "readme.rst", "readme.txt"}
    )
    manifests = sorted(
        relative for relative in files if Path(relative).name.lower() in MANIFEST_NAMES
    )
    locks = sorted(
        relative for relative in files if Path(relative).name.lower() in LOCK_NAMES
    )
    licensing_scope_files = [
        relative
        for relative in license_files
        if Path(relative).name.lower()
        in {"licensing", "licensing.md", "licensing.rst", "licensing.txt"}
    ]
    third_party_directories, generated_directories = remote_special_directories(files)
    submodules = sorted(
        item["path"]
        for item in tree_items
        if item.get("type") == "commit" and isinstance(item.get("path"), str)
    )
    content_counts = Counter(classify_file(relative) for relative in files)

    contributor_data = run_gh_json(
        [
            "api",
            "--paginate",
            "--slurp",
            f"repos/{full_name}/contributors?anon=1&per_page=100",
        ],
        allow_empty_repository=True,
    )
    contributor_entries: list[dict] = []
    if isinstance(contributor_data, list):
        pages = (
            contributor_data
            if contributor_data and isinstance(contributor_data[0], list)
            else [contributor_data]
        )
        contributor_entries = [
            entry
            for page in pages
            if isinstance(page, list)
            for entry in page
            if isinstance(entry, dict)
        ]
    contributors = sorted(
        {
            str(entry.get("login") or entry.get("name")).strip()
            for entry in contributor_entries
            if entry.get("login") or entry.get("name")
        },
        key=str.casefold,
    )

    parent = metadata.get("parent")
    parent_name = (
        parent.get("full_name")
        if isinstance(parent, dict) and isinstance(parent.get("full_name"), str)
        else None
    )
    detected_license = metadata.get("license")
    license_detection = None
    if isinstance(detected_license, dict):
        license_detection = {
            "spdx_id": detected_license.get("spdx_id"),
            "name": detected_license.get("name"),
            "key": detected_license.get("key"),
        }

    signals: list[dict[str, object]] = []
    if metadata.get("fork"):
        signals.append({"kind": "fork", "value": parent_name})
    if submodules:
        signals.append({"kind": "git_submodules", "value": submodules})
    if third_party_directories:
        signals.append(
            {"kind": "third_party_directories", "value": third_party_directories}
        )
    nested_license_files = [
        relative for relative in license_files if len(Path(relative).parts) > 1
    ]
    if nested_license_files:
        signals.append({"kind": "nested_license_files", "value": nested_license_files})
    if len(contributors) > 1:
        signals.append({"kind": "multiple_contributors", "value": len(contributors)})
    if content_counts["media"] or content_counts["font"] or content_counts["model"]:
        signals.append(
            {
                "kind": "non_code_assets",
                "value": {
                    key: content_counts[key]
                    for key in ("media", "font", "model")
                    if content_counts[key]
                },
            }
        )
    if content_counts["data"]:
        signals.append({"kind": "data_files", "value": content_counts["data"]})
    if tree_truncated:
        signals.append({"kind": "github_tree_truncated", "value": True})

    return {
        "repository": {
            "requested_path": None,
            "root": None,
            "name": metadata.get("name"),
            "name_with_owner": metadata.get("full_name") or full_name,
            "url": metadata.get("html_url"),
            "visibility": actual_visibility or None,
            "is_fork": bool(metadata.get("fork")),
            "parent": parent_name,
            "is_archived": bool(metadata.get("archived")),
            "is_disabled": bool(metadata.get("disabled")),
            "license_detection": license_detection,
            "is_git_repository": True,
            "current_branch": None,
            "default_branch": branch,
            "default_branch_source": "github",
            "head_sha": head_sha,
            "origin": metadata.get("clone_url"),
            "upstream": parent_name,
            "dirty_entry_count": None,
            "contributors": contributors,
            "submodules": submodules,
        },
        "file_basis": "github-default-branch-git-tree",
        "file_count": len(files),
        "content_counts": dict(sorted(content_counts.items())),
        "readme_files": readmes,
        "license_and_notice_files": license_files,
        "licensing_scope_files": licensing_scope_files,
        "manifest_files": manifests,
        "lock_files": locks,
        "third_party_directories": third_party_directories,
        "generated_directories": generated_directories,
        "spdx_identifiers_in_files": {},
        "review_signals": signals,
        "limitations": [
            "This inventory reports repository evidence and does not choose a license.",
            "GitHub contributor records do not prove copyright ownership or relicensing authority.",
            "Remote file bodies are not downloaded, so SPDX headers inside source files are not scanned.",
            "Absence of a detected signal does not prove that all content is original.",
            "A truncated GitHub tree requires a narrower follow-up inventory before a licensing decision.",
        ],
    }


def build_github_inventory(
    owner: str, visibility: str, selected: list[str]
) -> dict:
    clean_owner = owner.strip().strip("/")
    if not clean_owner or "/" in clean_owner:
        raise ValueError("--owner must be one GitHub login or organization name")
    require_authenticated_gh()
    names = github_repository_names(clean_owner, visibility, selected)
    records = [
        github_repository_record(name, visibility)
        for name in names
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "kind": "github",
            "owner": clean_owner,
            "visibility": visibility,
            "selected_repositories": [
                normalized_repository_name(clean_owner, item) for item in selected
            ],
            "transport": "authenticated-gh",
        },
        "repository_count": len(records),
        "repositories": records,
    }


def main() -> int:
    args = parse_args()
    try:
        if args.source_kind == "local":
            inventory = build_local_inventory(args.repository)
        else:
            inventory = build_github_inventory(
                args.owner, args.visibility, args.repository
            )
    except (ValueError, GitHubCommandError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    indent = None if args.compact else 2
    rendered = json.dumps(inventory, ensure_ascii=False, indent=indent, sort_keys=False) + "\n"
    if args.output:
        output = args.output.expanduser().resolve()
        if output.exists():
            print(f"ERROR: output already exists: {output}", file=sys.stderr)
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Inventory: {output}")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
