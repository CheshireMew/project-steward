"""Catalog, detection, and profile foundations for Project Steward templates."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
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
