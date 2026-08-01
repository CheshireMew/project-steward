#!/usr/bin/env python3
"""Inspect, adopt, upgrade, and verify Project Steward template profiles."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


PROFILE_SCHEMA_VERSION = 1
CATALOG_SCHEMA_VERSION = 1
TEMPLATE_SCHEMA_VERSION = 1
MANAGED_BY = "project-steward"
DEFAULT_CATALOG = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "project-templates"
    / "catalog.json"
)
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
DECISION_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
EXCLUDED_DIRECTORIES = {
    ".git",
    ".gradle",
    ".idea",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
    "venv",
}
FRONTEND_SUFFIXES = {".html", ".js", ".jsx", ".ts", ".tsx", ".vue"}
FRONTEND_EXCLUDED_DIRECTORIES = EXCLUDED_DIRECTORIES | {
    "__tests__",
    "e2e",
    "fixtures",
    "generated",
    "spec",
    "test",
    "tests",
}
PACKAGE_GROUPS = (
    "dependencies",
    "devDependencies",
    "peerDependencies",
    "optionalDependencies",
)


class StewardError(ValueError):
    """Raised when a catalog, profile, or project violates the public contract."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG,
        help="Template catalog path; intended for catalog maintenance and tests.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List registered templates")
    add_output_options(list_parser)

    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect a project without writing it"
    )
    inspect_parser.add_argument("project", type=Path)
    add_output_options(inspect_parser)

    for command, help_text in (
        ("plan", "Plan template adoption or upgrade without writing"),
        ("adopt", "Create a new project template profile"),
        ("upgrade", "Upgrade an existing project template profile"),
    ):
        child = subparsers.add_parser(command, help=help_text)
        child.add_argument("project", type=Path)
        child.add_argument(
            "--template",
            action="append",
            default=[],
            help="Select a registered template; repeat to combine templates.",
        )
        child.add_argument(
            "--decision",
            action="append",
            default=[],
            help="Explicit project decision in key=value form; repeat as needed.",
        )
        add_output_options(child)

    verify_parser = subparsers.add_parser(
        "verify", help="Verify a project's pinned templates and checks"
    )
    verify_parser.add_argument("project", type=Path)
    add_output_options(verify_parser)
    return parser.parse_args()


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--compact", action="store_true", help="Emit compact JSON"
    )


def fail(message: str) -> None:
    raise StewardError(message)


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"{label} not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid {label} JSON at {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"{label} must be a JSON object: {path}")
    return data


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def safe_relative_path(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty relative path")
    normalized = value.strip().replace("\\", "/")
    candidate = Path(normalized)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        fail(f"{label} must stay project-relative: {value}")
    resolved = (root / candidate).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"{label} escapes its root: {value}")
    return resolved


def require_project_root(path: Path) -> Path:
    root = path.expanduser().resolve()
    if not root.is_dir():
        fail(f"project directory not found: {root}")
    return root


def validate_template(
    template: dict[str, Any],
    *,
    template_id: str,
    entry: dict[str, Any],
    layer_order: list[str],
) -> None:
    required_types: dict[str, type] = {
        "id": str,
        "version": str,
        "layer": str,
        "name": str,
        "description": str,
        "requires": list,
        "detection": dict,
        "defaults": dict,
        "invariants": list,
        "checks": list,
        "manual_verification": list,
    }
    if template.get("schema_version") != TEMPLATE_SCHEMA_VERSION:
        fail(f"template {template_id} schema_version must be {TEMPLATE_SCHEMA_VERSION}")
    allowed_fields = {"schema_version", "evidence_sources", *required_types}
    unsupported_fields = sorted(set(template) - allowed_fields)
    if unsupported_fields:
        fail(
            f"template {template_id} has unsupported fields: "
            f"{', '.join(unsupported_fields)}"
        )
    for key, expected_type in required_types.items():
        if not isinstance(template.get(key), expected_type):
            fail(f"template {template_id} field {key} must be {expected_type.__name__}")
    if template["id"] != template_id:
        fail(f"template id mismatch: catalog {template_id}, file {template['id']}")
    if template["version"] != entry.get("version"):
        fail(f"template {template_id} version does not match its catalog entry")
    if template["layer"] != entry.get("layer"):
        fail(f"template {template_id} layer does not match its catalog entry")
    if not VERSION_PATTERN.fullmatch(template["version"]):
        fail(f"template {template_id} version must use semantic x.y.z form")
    if template["layer"] not in layer_order:
        fail(f"template {template_id} has unregistered layer {template['layer']}")
    if not all(isinstance(item, str) and item for item in template["requires"]):
        fail(f"template {template_id} requires must contain template ids")
    validate_detection(template_id, template["detection"])
    validate_named_records(template_id, "invariants", template["invariants"])
    validate_named_records(template_id, "checks", template["checks"])
    validate_named_records(
        template_id, "manual_verification", template["manual_verification"]
    )
    decisions = template["defaults"].get("decisions", {})
    if not isinstance(decisions, dict):
        fail(f"template {template_id} defaults.decisions must be an object")
    for key in decisions:
        if not isinstance(key, str) or not DECISION_KEY_PATTERN.fullmatch(key):
            fail(f"template {template_id} has invalid decision key {key!r}")


def validate_named_records(
    template_id: str, field: str, records: list[Any]
) -> None:
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            fail(f"template {template_id} {field}[{index}] must be an object")
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            fail(f"template {template_id} {field}[{index}] needs an id")
        if record_id in seen:
            fail(f"template {template_id} has duplicate {field} id {record_id}")
        seen.add(record_id)


def validate_detection(template_id: str, detection: dict[str, Any]) -> None:
    active = [
        key
        for key in ("always", "all", "any", "explicit_only")
        if key in detection
    ]
    if len(active) != 1:
        fail(
            f"template {template_id} detection must use exactly one of "
            "always/all/any/explicit_only"
        )
    if "always" in detection:
        if detection["always"] is not True:
            fail(f"template {template_id} detection.always must be true")
        return
    if "explicit_only" in detection:
        if detection["explicit_only"] is not True:
            fail(f"template {template_id} detection.explicit_only must be true")
        return
    key = active[0]
    rules = detection[key]
    if not isinstance(rules, list) or not rules:
        fail(f"template {template_id} detection.{key} must be a non-empty array")
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict) or not isinstance(rule.get("type"), str):
            fail(f"template {template_id} detection.{key}[{index}] is invalid")


def load_catalog(
    catalog_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    path = catalog_path.expanduser().resolve()
    catalog = read_json(path, "template catalog")
    if catalog.get("schema_version") != CATALOG_SCHEMA_VERSION:
        fail(f"template catalog schema_version must be {CATALOG_SCHEMA_VERSION}")
    if not isinstance(catalog.get("catalog_version"), str) or not VERSION_PATTERN.fullmatch(
        catalog["catalog_version"]
    ):
        fail("template catalog catalog_version must use semantic x.y.z form")
    if not isinstance(catalog.get("profile_path"), str):
        fail("template catalog profile_path must be a string")
    layer_order = catalog.get("layer_order")
    defaults = catalog.get("default_templates")
    entries = catalog.get("templates")
    if (
        not isinstance(layer_order, list)
        or not layer_order
        or not all(isinstance(item, str) and item for item in layer_order)
    ):
        fail("template catalog layer_order must be a non-empty string array")
    if len(layer_order) != len(set(layer_order)):
        fail("template catalog layer_order contains duplicates")
    if not isinstance(defaults, list) or not all(
        isinstance(item, str) and item for item in defaults
    ):
        fail("template catalog default_templates must be a string array")
    if not isinstance(entries, dict) or not entries:
        fail("template catalog templates must be a non-empty object")

    template_root = path.parent.resolve()
    templates: dict[str, dict[str, Any]] = {}
    for template_id, raw_entry in entries.items():
        if not isinstance(template_id, str) or not template_id:
            fail("template catalog contains an invalid template id")
        if not isinstance(raw_entry, dict):
            fail(f"catalog entry {template_id} must be an object")
        entry_path = safe_relative_path(
            template_root, raw_entry.get("path"), f"template {template_id} path"
        )
        expected_hash = raw_entry.get("sha256")
        if not isinstance(expected_hash, str) or not HASH_PATTERN.fullmatch(expected_hash):
            fail(f"template {template_id} catalog sha256 is invalid")
        try:
            content = entry_path.read_bytes()
        except FileNotFoundError:
            fail(f"template file not found: {entry_path}")
        actual_hash = sha256_bytes(content)
        if actual_hash != expected_hash:
            fail(
                f"template {template_id} integrity mismatch: expected "
                f"{expected_hash}, got {actual_hash}"
            )
        try:
            template = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail(f"template {template_id} is invalid JSON: {exc}")
        if not isinstance(template, dict):
            fail(f"template {template_id} must be a JSON object")
        validate_template(
            template,
            template_id=template_id,
            entry=raw_entry,
            layer_order=layer_order,
        )
        template["_catalog"] = {
            "sha256": actual_hash,
            "path": raw_entry["path"],
        }
        templates[template_id] = template

    for template_id in defaults:
        if template_id not in templates:
            fail(f"default template is not registered: {template_id}")
    for template_id, template in templates.items():
        for requirement in template["requires"]:
            if requirement not in templates:
                fail(f"template {template_id} requires unknown template {requirement}")
            if requirement == template_id:
                fail(f"template {template_id} cannot require itself")
    validate_template_graph(templates, layer_order)
    return catalog, templates


def validate_template_graph(
    templates: dict[str, dict[str, Any]], layer_order: list[str]
) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()
    layer_index = {layer: index for index, layer in enumerate(layer_order)}

    def visit(template_id: str) -> None:
        if template_id in visited:
            return
        if template_id in visiting:
            fail(f"template dependency cycle includes {template_id}")
        visiting.add(template_id)
        template = templates[template_id]
        for requirement in template["requires"]:
            if layer_index[templates[requirement]["layer"]] > layer_index[template["layer"]]:
                fail(
                    f"template {template_id} requires later-layer template {requirement}"
                )
            visit(requirement)
        visiting.remove(template_id)
        visited.add(template_id)

    for template_id in templates:
        visit(template_id)


def package_facts(root: Path) -> dict[str, Any]:
    package_path = root / "package.json"
    if not package_path.is_file():
        return {
            "path": None,
            "name": None,
            "dependencies": [],
            "scripts": [],
            "parse_error": None,
        }
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "path": "package.json",
            "name": None,
            "dependencies": [],
            "scripts": [],
            "parse_error": str(exc),
        }
    if not isinstance(package, dict):
        return {
            "path": "package.json",
            "name": None,
            "dependencies": [],
            "scripts": [],
            "parse_error": "package.json must contain an object",
        }
    dependencies: set[str] = set()
    for group in PACKAGE_GROUPS:
        values = package.get(group, {})
        if isinstance(values, dict):
            dependencies.update(
                key for key in values if isinstance(key, str) and key
            )
    scripts = package.get("scripts", {})
    return {
        "path": "package.json",
        "name": package.get("name") if isinstance(package.get("name"), str) else None,
        "dependencies": sorted(dependencies, key=str.casefold),
        "scripts": sorted(scripts) if isinstance(scripts, dict) else [],
        "parse_error": None,
    }


def project_path_exists(root: Path, relative: object) -> bool:
    path = safe_relative_path(root, relative, "project check path")
    return path.exists()


def evaluate_signal(
    root: Path, package: dict[str, Any], signal: dict[str, Any]
) -> tuple[bool, str]:
    signal_type = signal.get("type")
    if signal_type == "path_exists":
        value = signal.get("path")
        return project_path_exists(root, value), f"path {value}"
    if signal_type == "any_path_exists":
        paths = signal.get("paths")
        if not isinstance(paths, list) or not paths:
            fail("any_path_exists signal needs paths")
        matches = [value for value in paths if project_path_exists(root, value)]
        return bool(matches), f"paths {matches or paths}"
    if signal_type == "package_dependency":
        name = signal.get("name")
        if not isinstance(name, str) or not name:
            fail("package_dependency signal needs name")
        return name in package["dependencies"], f"package dependency {name}"
    fail(f"unsupported detection signal type: {signal_type!r}")


def template_matches(
    root: Path, package: dict[str, Any], template: dict[str, Any]
) -> tuple[bool, list[dict[str, Any]]]:
    detection = template["detection"]
    if detection.get("always") is True:
        return True, [{"signal": "always", "matched": True}]
    if detection.get("explicit_only") is True:
        return False, [
            {
                "signal": "explicit_only",
                "matched": False,
                "detail": "select this template explicitly or pin it in a project profile",
            }
        ]
    operator = "all" if "all" in detection else "any"
    observations: list[dict[str, Any]] = []
    for signal in detection[operator]:
        matched, detail = evaluate_signal(root, package, signal)
        observations.append(
            {"type": signal["type"], "matched": matched, "detail": detail}
        )
    result = (
        all(item["matched"] for item in observations)
        if operator == "all"
        else any(item["matched"] for item in observations)
    )
    return result, observations


def exact_root_git(root: Path) -> dict[str, Any] | None:
    marker = root / ".git"
    if not marker.exists():
        return None
    try:
        top = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        return {
            "exact_root": False,
            "marker": ".git",
            "error": "git command not found",
        }
    if top.returncode != 0:
        return {
            "exact_root": False,
            "marker": ".git",
            "error": top.stderr.strip() or top.stdout.strip(),
        }
    try:
        detected = Path(top.stdout.strip()).resolve()
    except OSError:
        detected = Path(top.stdout.strip())
    if detected != root:
        return {
            "exact_root": False,
            "marker": ".git",
            "detected_root": str(detected),
            "error": "the .git marker did not resolve to the exact project root",
        }

    def git_value(*arguments: str) -> str | None:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return completed.stdout.strip() if completed.returncode == 0 else None

    status = git_value("status", "--porcelain=v1", "-z") or ""
    return {
        "exact_root": True,
        "marker": ".git",
        "branch": git_value("branch", "--show-current"),
        "head": git_value("rev-parse", "HEAD"),
        "origin": git_value("remote", "get-url", "origin"),
        "dirty_entry_count": len([item for item in status.split("\0") if item]),
        "error": None,
    }


def filesystem_facts(root: Path) -> dict[str, Any]:
    file_count = 0
    directory_count = 0
    manifests: list[str] = []
    manifest_names = {
        "Cargo.toml",
        "go.mod",
        "package.json",
        "pom.xml",
        "pubspec.yaml",
        "pyproject.toml",
    }
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept: list[str] = []
        for name in sorted(directories):
            candidate = current_path / name
            if name in EXCLUDED_DIRECTORIES or candidate.is_symlink():
                continue
            kept.append(name)
        directories[:] = kept
        directory_count += len(kept)
        for filename in files:
            path = current_path / filename
            if path.is_symlink():
                continue
            file_count += 1
            if filename in manifest_names:
                manifests.append(path.relative_to(root).as_posix())
    return {
        "file_count": file_count,
        "directory_count": directory_count,
        "manifests": sorted(manifests),
    }


def profile_path(root: Path, catalog: dict[str, Any]) -> Path:
    return safe_relative_path(root, catalog["profile_path"], "profile_path")


def load_profile(path: Path, *, required: bool) -> dict[str, Any] | None:
    if not path.exists():
        if required:
            fail(f"project profile not found: {path}")
        return None
    if path.is_symlink() or not path.is_file():
        fail(f"project profile must be a regular file: {path}")
    profile = read_json(path, "project profile")
    validate_profile(profile)
    return profile


def validate_profile(profile: dict[str, Any]) -> None:
    if profile.get("schema_version") != PROFILE_SCHEMA_VERSION:
        fail(f"project profile schema_version must be {PROFILE_SCHEMA_VERSION}")
    if profile.get("managed_by") != MANAGED_BY:
        fail(f"project profile managed_by must be {MANAGED_BY}")
    for key in (
        "catalog_version",
        "project_name",
        "adopted_at_utc",
        "updated_at_utc",
    ):
        if not isinstance(profile.get(key), str) or not profile[key]:
            fail(f"project profile {key} must be a non-empty string")
    pins = profile.get("templates")
    if not isinstance(pins, list) or not pins:
        fail("project profile templates must be a non-empty array")
    seen: set[str] = set()
    for pin in pins:
        if not isinstance(pin, dict):
            fail("every project profile template pin must be an object")
        template_id = pin.get("id")
        version = pin.get("version")
        digest = pin.get("sha256")
        if not isinstance(template_id, str) or not template_id:
            fail("project profile template pin needs an id")
        if template_id in seen:
            fail(f"project profile contains duplicate template {template_id}")
        seen.add(template_id)
        if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
            fail(f"project profile template {template_id} has invalid version")
        if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
            fail(f"project profile template {template_id} has invalid sha256")
    if not isinstance(profile.get("decisions"), dict):
        fail("project profile decisions must be an object")
    if not isinstance(profile.get("overrides"), dict):
        fail("project profile overrides must be an object")
    for key in profile["overrides"]:
        if not isinstance(key, str) or not DECISION_KEY_PATTERN.fullmatch(key):
            fail(f"project profile has invalid override key {key!r}")
    deviations = profile.get("deviations")
    if not isinstance(deviations, list) or not all(
        isinstance(item, dict) for item in deviations
    ):
        fail("project profile deviations must be an array of objects")


def resolve_template_stack(
    selected: list[str],
    catalog: dict[str, Any],
    templates: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    requested: list[str] = []
    for template_id in [*catalog["default_templates"], *selected]:
        if template_id not in requested:
            requested.append(template_id)
    unknown = [template_id for template_id in requested if template_id not in templates]
    if unknown:
        fail("unknown template ids: " + ", ".join(unknown))

    resolved: set[str] = set()

    def include(template_id: str) -> None:
        if template_id in resolved:
            return
        for requirement in templates[template_id]["requires"]:
            include(requirement)
        resolved.add(template_id)

    for template_id in requested:
        include(template_id)
    layer_index = {
        layer: index for index, layer in enumerate(catalog["layer_order"])
    }
    return sorted(
        (templates[template_id] for template_id in resolved),
        key=lambda template: (layer_index[template["layer"]], template["id"]),
    )


def detect_templates(
    root: Path,
    catalog: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    package: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    matched: list[str] = []
    observations: dict[str, Any] = {}
    for template_id, template in templates.items():
        result, details = template_matches(root, package, template)
        observations[template_id] = {
            "matched": result,
            "details": details,
        }
        if result:
            matched.append(template_id)
    stack = resolve_template_stack(matched, catalog, templates)
    return [template["id"] for template in stack], observations


def inspect_project(
    root: Path,
    catalog: dict[str, Any],
    templates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    package = package_facts(root)
    suggested, observations = detect_templates(root, catalog, templates, package)
    target_profile = profile_path(root, catalog)
    existing = load_profile(target_profile, required=False)
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "mode": "inspect",
        "project": {
            "root": str(root),
            "name": root.name,
            **filesystem_facts(root),
        },
        "git": exact_root_git(root),
        "package": package,
        "profile": {
            "path": str(target_profile),
            "exists": existing is not None,
            "templates": (
                [pin["id"] for pin in existing["templates"]] if existing else []
            ),
            "catalog_version": existing.get("catalog_version") if existing else None,
        },
        "detection": observations,
        "suggested_templates": suggested,
    }


def parse_decisions(items: list[str]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            fail(f"invalid decision {item!r}; use key=value")
        key, raw_value = (part.strip() for part in item.split("=", 1))
        if not DECISION_KEY_PATTERN.fullmatch(key):
            fail(f"invalid decision key: {key!r}")
        if not raw_value:
            fail(f"decision {key} cannot be empty")
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            value = raw_value
        if isinstance(value, (dict, list)):
            fail(f"decision {key} must be a scalar value")
        overrides[key] = value
    return overrides


def merged_decisions(stack: list[dict[str, Any]]) -> dict[str, Any]:
    decisions: dict[str, Any] = {}
    for template in stack:
        for key, value in template["defaults"].get("decisions", {}).items():
            decisions[key] = deepcopy(value)
    return decisions


def pin_stack(stack: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "id": template["id"],
            "version": template["version"],
            "sha256": template["_catalog"]["sha256"],
        }
        for template in stack
    ]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_target_profile(
    root: Path,
    catalog: dict[str, Any],
    stack: list[dict[str, Any]],
    existing: dict[str, Any] | None,
    requested_overrides: dict[str, Any],
) -> dict[str, Any]:
    defaults = merged_decisions(stack)
    inherited_overrides = deepcopy(existing["overrides"]) if existing else {}
    inherited_overrides.update(requested_overrides)
    unknown_overrides = sorted(set(inherited_overrides) - set(defaults))
    if unknown_overrides:
        fail(
            "project overrides do not belong to the selected template stack: "
            + ", ".join(unknown_overrides)
        )
    decisions = deepcopy(defaults)
    decisions.update(inherited_overrides)
    now = utc_now()
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "managed_by": MANAGED_BY,
        "catalog_version": catalog["catalog_version"],
        "project_name": (
            existing["project_name"] if existing else root.name
        ),
        "templates": pin_stack(stack),
        "decisions": decisions,
        "overrides": inherited_overrides,
        "deviations": deepcopy(existing["deviations"]) if existing else [],
        "adopted_at_utc": existing["adopted_at_utc"] if existing else now,
        "updated_at_utc": now,
    }


def dotted_value(source: dict[str, Any], dotted_path: object) -> tuple[bool, Any]:
    if not isinstance(dotted_path, str) or not dotted_path:
        fail("profile_value check needs a dotted path")
    cursor: Any = source
    for part in dotted_path.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return False, None
        cursor = cursor[part]
    return True, cursor


def collect_frontend_text(root: Path) -> tuple[str, list[str]]:
    chunks: list[str] = []
    paths: list[str] = []
    total_bytes = 0
    limit = 8 * 1024 * 1024
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            name
            for name in sorted(directories)
            if name not in FRONTEND_EXCLUDED_DIRECTORIES
            and not (current_path / name).is_symlink()
        ]
        for filename in sorted(files):
            path = current_path / filename
            if path.suffix.lower() not in FRONTEND_SUFFIXES or path.is_symlink():
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > 1024 * 1024 or total_bytes + size > limit:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            chunks.append(text)
            paths.append(path.relative_to(root).as_posix())
            total_bytes += size
    return "\n".join(chunks), paths


def collect_capability_facts(root: Path, window_label: str) -> dict[str, Any]:
    paths: list[str] = []
    chunks: list[str] = []
    target_permissions: set[str] = set()
    structured_records: list[dict[str, Any]] = []
    unstructured_paths: list[str] = []
    capability_root = root / "src-tauri" / "capabilities"
    if capability_root.is_dir() and not capability_root.is_symlink():
        for path in sorted(capability_root.rglob("*")):
            if (
                path.is_file()
                and not path.is_symlink()
                and path.suffix.lower() in {".json", ".toml"}
            ):
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                    chunks.append(text)
                    paths.append(path.relative_to(root).as_posix())
                except OSError:
                    continue
                if path.suffix.lower() != ".json":
                    unstructured_paths.append(path.relative_to(root).as_posix())
                    continue
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    unstructured_paths.append(path.relative_to(root).as_posix())
                    continue
                records = data if isinstance(data, list) else [data]
                for record in records:
                    if not isinstance(record, dict):
                        continue
                    windows = record.get("windows")
                    patterns = (
                        windows
                        if isinstance(windows, list)
                        and all(isinstance(item, str) for item in windows)
                        else []
                    )
                    applies = not patterns or any(
                        fnmatch.fnmatchcase(window_label, pattern)
                        for pattern in patterns
                    )
                    raw_permissions = record.get("permissions", [])
                    permissions: set[str] = set()
                    if isinstance(raw_permissions, list):
                        for item in raw_permissions:
                            if isinstance(item, str):
                                permissions.add(item)
                            elif (
                                isinstance(item, dict)
                                and isinstance(item.get("identifier"), str)
                            ):
                                permissions.add(item["identifier"])
                    structured_records.append(
                        {
                            "path": path.relative_to(root).as_posix(),
                            "identifier": record.get("identifier"),
                            "windows": patterns,
                            "applies_to_target": applies,
                            "permissions": sorted(permissions),
                        }
                    )
                    if applies:
                        target_permissions.update(permissions)
    config_path = root / "src-tauri" / "tauri.conf.json"
    if config_path.is_file() and not config_path.is_symlink():
        try:
            chunks.append(config_path.read_text(encoding="utf-8", errors="replace"))
            paths.append(config_path.relative_to(root).as_posix())
        except OSError:
            pass
    return {
        "text": "\n".join(chunks),
        "paths": paths,
        "target_permissions": sorted(target_permissions),
        "structured_records": structured_records,
        "unstructured_paths": unstructured_paths,
    }


def tauri_window_shell_check(
    root: Path, profile: dict[str, Any]
) -> tuple[str, str, dict[str, Any]]:
    json_path = root / "src-tauri" / "tauri.conf.json"
    json5_path = root / "src-tauri" / "tauri.conf.json5"
    if not json_path.is_file():
        if json5_path.is_file():
            return (
                "manual",
                "tauri.conf.json5 requires manual configuration inspection",
                {"config": "src-tauri/tauri.conf.json5"},
            )
        return "fail", "Tauri configuration is missing", {}
    try:
        config = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "fail", f"Tauri configuration is not valid JSON: {exc}", {}
    if not isinstance(config, dict):
        return "fail", "Tauri configuration must contain an object", {}
    app = config.get("app", {})
    windows = app.get("windows", []) if isinstance(app, dict) else []
    if not isinstance(windows, list) or not windows:
        return "fail", "Tauri app.windows must explicitly define the primary window", {}
    primary = next(
        (
            item
            for item in windows
            if isinstance(item, dict) and item.get("label") == "main"
        ),
        windows[0] if isinstance(windows[0], dict) else {},
    )
    if not isinstance(primary, dict):
        return "fail", "Tauri primary window configuration is invalid", {}

    strategy = profile["decisions"].get("window_shell")
    decorations = primary.get("decorations", True)
    window_label = (
        primary.get("label")
        if isinstance(primary.get("label"), str) and primary.get("label")
        else "main"
    )
    frontend_text, frontend_paths = collect_frontend_text(root)
    if strategy == "native-explicit":
        if decorations is False:
            return (
                "fail",
                "native-explicit conflicts with decorations=false",
                {"window_label": primary.get("label"), "decorations": decorations},
            )
        duplicate_signals: list[str] = []
        if "data-tauri-drag-region" in frontend_text or re.search(
            r"\bstartDragging\s*\(", frontend_text
        ):
            duplicate_signals.append("custom drag region")
        if re.search(r"\.(?:minimize|maximize|toggleMaximize)\s*\(", frontend_text):
            duplicate_signals.append("custom minimize or maximize controls")
        if duplicate_signals:
            return (
                "fail",
                "native-explicit cannot keep a second integrated window shell",
                {
                    "window_label": window_label,
                    "decorations": decorations,
                    "duplicate_signals": duplicate_signals,
                    "frontend_files_scanned": frontend_paths,
                },
            )
        return (
            "pass",
            "native window decorations are explicitly retained",
            {
                "window_label": window_label,
                "decorations": decorations,
                "frontend_files_scanned": frontend_paths,
            },
        )
    if strategy != "integrated":
        return "fail", f"unsupported window_shell decision: {strategy!r}", {}
    if decorations is not False:
        return (
            "fail",
            "integrated window shell requires decorations=false",
            {"window_label": primary.get("label"), "decorations": decorations},
        )

    capability_facts = collect_capability_facts(root, window_label)
    capability_text = capability_facts["text"]
    target_permissions = set(capability_facts["target_permissions"])
    missing_features: list[str] = []
    missing_permissions: list[str] = []
    manual_permissions: list[str] = []

    def require_permission(permission: str) -> None:
        if permission in target_permissions:
            return
        if capability_facts["structured_records"]:
            missing_permissions.append(permission)
        elif permission in capability_text:
            manual_permissions.append(permission)
        else:
            missing_permissions.append(permission)

    window_api_signal = (
        "@tauri-apps/api/window" in frontend_text
        or "getCurrentWindow" in frontend_text
    )
    if not window_api_signal:
        missing_features.append("Tauri current-window API boundary")
    uses_drag_attribute = "data-tauri-drag-region" in frontend_text
    uses_start_dragging = re.search(r"\bstartDragging\s*\(", frontend_text) is not None
    if not uses_drag_attribute and not uses_start_dragging:
        missing_features.append("drag region or startDragging()")

    calls: list[tuple[str, str, tuple[str, ...]]] = [
        (
            "minimize()",
            "core:window:allow-minimize",
            (r"\.minimize\s*\(",),
        ),
        (
            "maximize or toggleMaximize",
            "core:window:allow-toggle-maximize",
            (r"\.toggleMaximize\s*\(",),
        ),
    ]
    detected_calls: dict[str, bool] = {}
    for label, permission, patterns in calls:
        used = any(re.search(pattern, frontend_text) for pattern in patterns)
        detected_calls[label] = used
        if not used:
            missing_features.append(label)
        else:
            require_permission(permission)

    maximize_used = re.search(r"\.maximize\s*\(", frontend_text) is not None
    if not detected_calls["maximize or toggleMaximize"] and maximize_used:
        missing_features = [
            item for item in missing_features if item != "maximize or toggleMaximize"
        ]
        detected_calls["maximize or toggleMaximize"] = True
        require_permission("core:window:allow-maximize")

    close_used = re.search(r"\.close\s*\(", frontend_text) is not None
    destroy_used = re.search(r"\.destroy\s*\(", frontend_text) is not None
    if not close_used and not destroy_used:
        missing_features.append("close() or explicitly justified destroy()")
    if close_used:
        require_permission("core:window:allow-close")
    if destroy_used:
        require_permission("core:window:allow-destroy")
    if uses_start_dragging:
        require_permission("core:window:allow-start-dragging")

    details = {
        "config": "src-tauri/tauri.conf.json",
        "window_label": window_label,
        "decorations": decorations,
        "frontend_files_scanned": frontend_paths,
        "capability_files_scanned": capability_facts["paths"],
        "target_permissions": capability_facts["target_permissions"],
        "capability_records": capability_facts["structured_records"],
        "drag_attribute": uses_drag_attribute,
        "start_dragging_call": uses_start_dragging,
        "close_call": close_used,
        "destroy_call": destroy_used,
        "missing_features": sorted(set(missing_features)),
        "missing_permissions": sorted(set(missing_permissions)),
        "manual_permission_binding": sorted(set(manual_permissions)),
        "target_window_binding_requires_runtime_review": True,
    }
    if missing_features or missing_permissions:
        message_parts = []
        if missing_features:
            message_parts.append("missing shell features: " + ", ".join(sorted(set(missing_features))))
        if missing_permissions:
            message_parts.append(
                "missing matching permissions: "
                + ", ".join(sorted(set(missing_permissions)))
            )
        return "fail", "; ".join(message_parts), details
    if manual_permissions:
        return (
            "manual",
            "window permissions are present only in unstructured capability "
            "sources and require target-window review",
            details,
        )
    if destroy_used:
        return (
            "manual",
            "destroy() has a matching permission, but its force-close intent and "
            "completed shutdown chain require runtime review",
            details,
        )
    return (
        "pass",
        "integrated Tauri shell and explicit method permissions are present",
        details,
    )


def evaluate_check(
    root: Path,
    profile: dict[str, Any],
    package: dict[str, Any],
    check: dict[str, Any],
    *,
    virtual_profile: bool,
    expected_profile_relative: str,
) -> dict[str, Any]:
    check_id = check["id"]
    check_type = check.get("type")
    severity = check.get("severity", "error")
    if severity not in {"error", "warning", "info"}:
        fail(f"check {check_id} has unsupported severity {severity!r}")
    status = "fail"
    detail = check.get("message", "")
    evidence: dict[str, Any] = {}

    if check_type == "profile_value":
        found, value = dotted_value(profile, check.get("path"))
        allowed = check.get("allowed")
        if not isinstance(allowed, list) or not allowed:
            fail(f"check {check_id} profile_value needs allowed")
        status = "pass" if found and value in allowed else "fail"
        evidence = {"found": found, "value": value, "allowed": allowed}
    elif check_type == "path_exists":
        relative = check.get("path")
        exists = (
            virtual_profile and relative == expected_profile_relative
        ) or project_path_exists(root, relative)
        status = "pass" if exists else "fail"
        evidence = {"path": relative, "exists": exists}
    elif check_type == "any_path_exists":
        paths = check.get("paths")
        if not isinstance(paths, list) or not paths:
            fail(f"check {check_id} any_path_exists needs paths")
        matches = [value for value in paths if project_path_exists(root, value)]
        status = "pass" if matches else "fail"
        evidence = {"paths": paths, "matches": matches}
    elif check_type == "package_dependency":
        name = check.get("name")
        if not isinstance(name, str) or not name:
            fail(f"check {check_id} package_dependency needs name")
        present = name in package["dependencies"]
        status = "pass" if present else "fail"
        evidence = {"name": name, "present": present}
    elif check_type == "tauri_window_shell":
        status, detail, evidence = tauri_window_shell_check(root, profile)
    else:
        fail(f"unsupported check type {check_type!r} in {check_id}")

    effective_failure = status == "fail" and severity == "error"
    return {
        "id": check_id,
        "type": check_type,
        "severity": severity,
        "status": status,
        "effective_failure": effective_failure,
        "message": detail,
        "evidence": evidence,
    }


def verify_profile_data(
    root: Path,
    catalog: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    profile: dict[str, Any],
    *,
    virtual_profile: bool,
) -> dict[str, Any]:
    validate_profile(profile)
    pins = profile["templates"]
    drift: list[dict[str, Any]] = []
    selected: list[str] = []
    for pin in pins:
        template_id = pin["id"]
        selected.append(template_id)
        current = templates.get(template_id)
        if current is None:
            drift.append(
                {
                    "id": template_id,
                    "kind": "unregistered",
                    "pinned_version": pin["version"],
                }
            )
            continue
        if pin["version"] != current["version"]:
            drift.append(
                {
                    "id": template_id,
                    "kind": "version",
                    "pinned": pin["version"],
                    "current": current["version"],
                }
            )
        if pin["sha256"] != current["_catalog"]["sha256"]:
            drift.append(
                {
                    "id": template_id,
                    "kind": "content",
                    "pinned": pin["sha256"],
                    "current": current["_catalog"]["sha256"],
                }
            )
    if profile["catalog_version"] != catalog["catalog_version"]:
        drift.append(
            {
                "kind": "catalog",
                "pinned": profile["catalog_version"],
                "current": catalog["catalog_version"],
            }
        )

    available_selected = [
        template_id for template_id in selected if template_id in templates
    ]
    stack = resolve_template_stack(available_selected, catalog, templates)
    resolved_ids = [template["id"] for template in stack]
    if resolved_ids != selected:
        drift.append(
            {
                "kind": "dependency-order",
                "pinned": selected,
                "current": resolved_ids,
            }
        )

    expected_decisions = merged_decisions(stack)
    unknown_overrides = sorted(set(profile["overrides"]) - set(expected_decisions))
    if unknown_overrides:
        drift.append(
            {
                "kind": "unknown-overrides",
                "keys": unknown_overrides,
            }
        )
    for key, value in profile["overrides"].items():
        if key in expected_decisions:
            expected_decisions[key] = value
    if profile["decisions"] != expected_decisions:
        drift.append(
            {
                "kind": "decisions",
                "pinned": profile["decisions"],
                "expected": expected_decisions,
            }
        )

    package = package_facts(root)
    checks: list[dict[str, Any]] = []
    check_ids: set[str] = set()
    manual: list[dict[str, Any]] = []
    manual_ids: set[str] = set()
    for template in stack:
        for check in template["checks"]:
            if check["id"] in check_ids:
                fail(f"template stack has duplicate check id {check['id']}")
            check_ids.add(check["id"])
            result = evaluate_check(
                root,
                profile,
                package,
                check,
                virtual_profile=virtual_profile,
                expected_profile_relative=catalog["profile_path"],
            )
            result["template"] = template["id"]
            checks.append(result)
        for item in template["manual_verification"]:
            if item["id"] in manual_ids:
                fail(
                    f"template stack has duplicate manual verification id {item['id']}"
                )
            manual_ids.add(item["id"])
            manual.append({"template": template["id"], **deepcopy(item)})
    failed = [item for item in checks if item["effective_failure"]]
    status = "failed" if drift or failed else "passed"
    return {
        "status": status,
        "profile_mode": "preview" if virtual_profile else "on-disk",
        "templates": selected,
        "drift": drift,
        "checks": checks,
        "failed_check_ids": [item["id"] for item in failed],
        "manual_verification": manual,
        "manual_verification_required": bool(manual),
    }


def plan_project(
    root: Path,
    catalog: dict[str, Any],
    templates: dict[str, dict[str, Any]],
    selected_args: list[str],
    decision_args: list[str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    target_path = profile_path(root, catalog)
    existing = load_profile(target_path, required=False)
    package = package_facts(root)
    if selected_args:
        selected = selected_args
        selection_source = "explicit"
    elif existing:
        selected = [pin["id"] for pin in existing["templates"]]
        selection_source = "existing-profile"
    else:
        selected, _ = detect_templates(root, catalog, templates, package)
        selection_source = "detected"
    stack = resolve_template_stack(selected, catalog, templates)
    requested_overrides = parse_decisions(decision_args)

    if existing:
        expected_existing = merged_decisions(stack)
        for key, value in existing["overrides"].items():
            if key in expected_existing:
                expected_existing[key] = value
        # New minor-version defaults are added by upgrade. Existing decision
        # values still require an explicit choice when they differ, so a
        # hand-edited project decision cannot be silently overwritten.
        decision_keys = set(existing["decisions"])
        unresolved = sorted(
            key
            for key in decision_keys
            if existing["decisions"].get(key) != expected_existing.get(key)
            and key not in requested_overrides
        )
        if unresolved:
            fail(
                "existing profile decisions differ from the selected current "
                "template defaults; explicitly preserve or accept each value with "
                "--decision before upgrade: "
                + ", ".join(unresolved)
            )

    target = build_target_profile(
        root, catalog, stack, existing, requested_overrides
    )
    preflight = verify_profile_data(
        root,
        catalog,
        templates,
        target,
        virtual_profile=existing is None,
    )
    current_pins = existing["templates"] if existing else []
    changes = {
        "profile_exists": existing is not None,
        "templates_changed": current_pins != target["templates"],
        "decisions_changed": (
            existing["decisions"] != target["decisions"] if existing else True
        ),
        "overrides_changed": (
            existing["overrides"] != target["overrides"] if existing else bool(target["overrides"])
        ),
        "catalog_changed": (
            existing["catalog_version"] != target["catalog_version"]
            if existing
            else True
        ),
    }
    changed = any(
        changes[key]
        for key in (
            "templates_changed",
            "decisions_changed",
            "overrides_changed",
            "catalog_changed",
        )
    )
    action = "adopt" if existing is None else "upgrade" if changed else "current"
    plan = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "mode": "plan",
        "project": str(root),
        "profile": str(target_path),
        "selection_source": selection_source,
        "action": action,
        "selected_templates": [template["id"] for template in stack],
        "changes": changes,
        "target_profile": target,
        "preflight": preflight,
    }
    return plan, target, existing


def ensure_profile_parent(root: Path, target: Path) -> None:
    try:
        target.relative_to(root)
    except ValueError:
        fail(f"project profile escapes project root: {target}")
    parent = target.parent
    cursor = root
    for part in parent.relative_to(root).parts:
        cursor = cursor / part
        if cursor.exists() and cursor.is_symlink():
            fail(f"project profile parent uses a symlink: {cursor}")
    parent.mkdir(parents=True, exist_ok=True)


def render_profile(profile: dict[str, Any]) -> str:
    return json.dumps(profile, ensure_ascii=False, indent=2) + "\n"


def write_new_profile(root: Path, target: Path, profile: dict[str, Any]) -> None:
    ensure_profile_parent(root, target)
    if target.exists():
        fail(f"project profile already exists: {target}")
    try:
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(render_profile(profile))
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        fail(f"project profile already exists: {target}")


def replace_profile(root: Path, target: Path, profile: dict[str, Any]) -> None:
    ensure_profile_parent(root, target)
    if target.is_symlink() or not target.is_file():
        fail(f"project profile must be an existing regular file: {target}")
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=target.parent,
            delete=False,
        ) as stream:
            stream.write(render_profile(profile))
            stream.flush()
            os.fsync(stream.fileno())
            temporary_path = Path(stream.name)
        os.replace(temporary_path, target)
        temporary_path = None
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def output_json(payload: dict[str, Any], *, compact: bool) -> None:
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=None if compact else 2,
            separators=(",", ":") if compact else None,
        )
    )


def list_templates(
    catalog: dict[str, Any], templates: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    layer_index = {
        layer: index for index, layer in enumerate(catalog["layer_order"])
    }
    ordered = sorted(
        templates.values(),
        key=lambda template: (layer_index[template["layer"]], template["id"]),
    )
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "mode": "list",
        "catalog_version": catalog["catalog_version"],
        "profile_path": catalog["profile_path"],
        "templates": [
            {
                "id": template["id"],
                "version": template["version"],
                "layer": template["layer"],
                "name": template["name"],
                "description": template["description"],
                "requires": template["requires"],
                "selection": (
                    "explicit-only"
                    if template["detection"].get("explicit_only") is True
                    else "detectable"
                ),
                "sha256": template["_catalog"]["sha256"],
            }
            for template in ordered
        ],
    }


def run_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    catalog, templates = load_catalog(args.catalog)
    if args.command == "list":
        return list_templates(catalog, templates), 0

    root = require_project_root(args.project)
    if args.command == "inspect":
        return inspect_project(root, catalog, templates), 0
    if args.command == "verify":
        target = profile_path(root, catalog)
        profile = load_profile(target, required=True)
        assert profile is not None
        verification = verify_profile_data(
            root, catalog, templates, profile, virtual_profile=False
        )
        return {
            "schema_version": PROFILE_SCHEMA_VERSION,
            "mode": "verify",
            "project": str(root),
            "profile": str(target),
            "verification": verification,
        }, 0 if verification["status"] == "passed" else 1

    plan, target_profile, existing = plan_project(
        root,
        catalog,
        templates,
        args.template,
        args.decision,
    )
    if args.command == "plan":
        return plan, 0

    target_path = profile_path(root, catalog)
    preflight = plan["preflight"]
    if preflight["status"] != "passed":
        return {
            "schema_version": PROFILE_SCHEMA_VERSION,
            "mode": args.command,
            "project": str(root),
            "profile": str(target_path),
            "status": "blocked",
            "reason": "deterministic preflight failed; no profile was written",
            "plan": plan,
        }, 1

    if args.command == "adopt":
        if existing is not None:
            fail(
                f"project profile already exists: {target_path}; use plan or upgrade"
            )
        write_new_profile(root, target_path, target_profile)
        mode = "adopted"
    else:
        if existing is None:
            fail(f"project profile does not exist: {target_path}; use adopt")
        if plan["action"] == "current":
            verification = verify_profile_data(
                root,
                catalog,
                templates,
                existing,
                virtual_profile=False,
            )
            return {
                "schema_version": PROFILE_SCHEMA_VERSION,
                "mode": args.command,
                "status": "current",
                "project": str(root),
                "profile": str(target_path),
                "templates": [pin["id"] for pin in existing["templates"]],
                "verification": verification,
            }, 0 if verification["status"] == "passed" else 1
        replace_profile(root, target_path, target_profile)
        mode = "upgraded"

    written = load_profile(target_path, required=True)
    assert written is not None
    verification = verify_profile_data(
        root, catalog, templates, written, virtual_profile=False
    )
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "mode": args.command,
        "status": mode,
        "project": str(root),
        "profile": str(target_path),
        "templates": [pin["id"] for pin in written["templates"]],
        "verification": verification,
    }, 0 if verification["status"] == "passed" else 1


def main() -> int:
    args = parse_args()
    try:
        payload, exit_code = run_command(args)
        output_json(payload, compact=args.compact)
        return exit_code
    except (OSError, StewardError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
