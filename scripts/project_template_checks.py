"""Project capability and template verification checks."""

from __future__ import annotations

import fnmatch
import json
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from project_template_core import (
    FRONTEND_EXCLUDED_DIRECTORIES,
    FRONTEND_SUFFIXES,
    dotted_value,
    fail,
    merged_decisions,
    package_facts,
    project_path_exists,
    resolve_template_stack,
    validate_profile,
)


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
            (
                "window permissions are present only in unstructured capability "
                "sources and require target-window review"
            ),
            details,
        )
    if destroy_used:
        return (
            "manual",
            (
                "destroy() has a matching permission, but its force-close intent and "
                "completed shutdown chain require runtime review"
            ),
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
