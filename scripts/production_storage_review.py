#!/usr/bin/env python3
"""Review a production project's owned storage contract without writing it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PROTOCOL = "project-steward-production-storage-contract"
VERSION = 1
DEFAULT_CONTRACT = Path(".project-steward/storage-contract.json")
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
REQUIRED_POLICY = {
    "unknown_peak": "block",
    "outside_owned_roots": "block",
    "over_budget": "block",
    "cleanup_without_authorization": "report-only",
}
ALLOWED_ROOT_KINDS = {"project-relative", "runtime-config", "user-environment-policy"}
ALLOWED_ARTIFACT_CLASSES = {"truth", "deliverable", "cache", "temporary", "evidence"}


class ReviewError(ValueError):
    pass


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReviewError(f"{label} must be an object")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{label} must be a non-empty string")
    return value.strip()


def _identifier(value: Any, label: str) -> str:
    selected = _string(value, label)
    if not ID_PATTERN.fullmatch(selected):
        raise ReviewError(f"{label} must use a stable lowercase identifier")
    return selected


def _relative_path(root: Path, value: Any, label: str) -> Path:
    raw = _string(value, label).replace("\\", "/")
    candidate = Path(raw)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ReviewError(f"{label} must stay project-relative: {raw}")
    resolved = (root / candidate).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ReviewError(f"{label} escapes the project root: {raw}") from error
    return resolved


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ReviewError(f"{label} must be a non-empty array")
    result = [_string(item, f"{label}[{index}]") for index, item in enumerate(value)]
    if len(result) != len(set(result)):
        raise ReviewError(f"{label} contains duplicates")
    return result


def _read_contract(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ReviewError(f"storage contract not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ReviewError(f"invalid storage contract JSON at {path}: {error}") from error
    return _object(payload, "storage contract")


def _review_producer(root: Path, value: Any, index: int) -> dict[str, Any]:
    producer = _object(value, f"producers[{index}]")
    producer_id = _identifier(producer.get("id"), f"producers[{index}].id")
    root_source = _object(producer.get("root_source"), f"producer {producer_id}.root_source")
    root_kind = _string(root_source.get("kind"), f"producer {producer_id}.root_source.kind")
    if root_kind not in ALLOWED_ROOT_KINDS:
        raise ReviewError(f"producer {producer_id} uses unsupported root kind {root_kind!r}")
    root_value = _string(root_source.get("value"), f"producer {producer_id}.root_source.value")
    if re.search(r"(^|[\\/])[A-Za-z]:|^[A-Za-z]:", root_value):
        raise ReviewError(f"producer {producer_id} stores a machine drive in the project contract")

    artifact_classes = set(
        _string_list(producer.get("artifact_classes"), f"producer {producer_id}.artifact_classes")
    )
    unsupported = sorted(artifact_classes - ALLOWED_ARTIFACT_CLASSES)
    if unsupported:
        raise ReviewError(f"producer {producer_id} has unsupported artifact classes: {', '.join(unsupported)}")

    estimate = _object(producer.get("peak_estimate"), f"producer {producer_id}.peak_estimate")
    if _string(estimate.get("unknown_behavior"), f"producer {producer_id}.peak_estimate.unknown_behavior") != "block":
        raise ReviewError(f"producer {producer_id} must block unknown peak estimates")
    _string(estimate.get("source"), f"producer {producer_id}.peak_estimate.source")

    budget = _object(producer.get("budget"), f"producer {producer_id}.budget")
    _string(budget.get("maximum_managed_bytes_source"), f"producer {producer_id}.budget.maximum_managed_bytes_source")
    _string(budget.get("minimum_free_bytes_source"), f"producer {producer_id}.budget.minimum_free_bytes_source")

    reuse = _object(producer.get("reuse"), f"producer {producer_id}.reuse")
    if not isinstance(reuse.get("required"), bool):
        raise ReviewError(f"producer {producer_id}.reuse.required must be boolean")
    if reuse["required"]:
        _string(reuse.get("identity"), f"producer {producer_id}.reuse.identity")

    lifecycle = _object(producer.get("lifecycle"), f"producer {producer_id}.lifecycle")
    for field in ("preflight", "finalization", "interruption"):
        _string(lifecycle.get(field), f"producer {producer_id}.lifecycle.{field}")

    implementation_files = _string_list(
        producer.get("implementation_files"), f"producer {producer_id}.implementation_files"
    )
    test_files = _string_list(producer.get("test_files"), f"producer {producer_id}.test_files")
    enforcement = _object(producer.get("enforcement"), f"producer {producer_id}.enforcement")
    enforcement_file = _string(enforcement.get("file"), f"producer {producer_id}.enforcement.file")
    tokens = _string_list(enforcement.get("tokens"), f"producer {producer_id}.enforcement.tokens")

    missing: list[str] = []
    for relative in [*implementation_files, *test_files, enforcement_file]:
        resolved = _relative_path(root, relative, f"producer {producer_id} path")
        if not resolved.is_file():
            missing.append(relative)
    if missing:
        raise ReviewError(f"producer {producer_id} references missing files: {', '.join(sorted(set(missing)))}")

    enforcement_path = _relative_path(root, enforcement_file, f"producer {producer_id}.enforcement.file")
    try:
        enforcement_text = enforcement_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ReviewError(f"producer {producer_id} enforcement file must be UTF-8 text") from error
    absent_tokens = [token for token in tokens if token not in enforcement_text]
    if absent_tokens:
        raise ReviewError(f"producer {producer_id} enforcement tokens are absent: {', '.join(absent_tokens)}")

    return {
        "id": producer_id,
        "root_kind": root_kind,
        "artifact_classes": sorted(artifact_classes),
        "implementation_files": implementation_files,
        "test_files": test_files,
        "enforcement_file": enforcement_file,
        "enforcement_tokens": tokens,
    }


def review(project: Path, contract_relative: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    root = project.expanduser().resolve()
    if not root.is_dir():
        raise ReviewError(f"project directory not found: {root}")
    contract_path = _relative_path(root, contract_relative.as_posix(), "contract path")
    contract = _read_contract(contract_path)
    if contract.get("protocol") != PROTOCOL or contract.get("version") != VERSION:
        raise ReviewError(f"storage contract must use {PROTOCOL} v{VERSION}")
    project_id = _identifier(contract.get("project_id"), "project_id")
    policy = _object(contract.get("policy"), "policy")
    for field, expected in REQUIRED_POLICY.items():
        if policy.get(field) != expected:
            raise ReviewError(f"policy.{field} must be {expected!r}")
    producers = contract.get("producers")
    if not isinstance(producers, list) or not producers:
        raise ReviewError("producers must be a non-empty array")
    reviewed = [_review_producer(root, item, index) for index, item in enumerate(producers)]
    ids = [item["id"] for item in reviewed]
    if len(ids) != len(set(ids)):
        raise ReviewError("producer ids must be unique")
    return {
        "schema": "project-steward-production-storage-review/v1",
        "status": "passed",
        "project": str(root),
        "project_id": project_id,
        "contract": str(contract_path),
        "producer_count": len(reviewed),
        "producers": reviewed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = review(args.project, args.contract)
        print(json.dumps(payload, ensure_ascii=False, indent=None if args.compact else 2))
        return 0
    except (OSError, ReviewError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
