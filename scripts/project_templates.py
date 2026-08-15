#!/usr/bin/env python3
"""Inspect, adopt, upgrade, and verify Project Steward template profiles."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from project_template_checks import verify_profile_data
from project_template_core import (
    CATALOG_SCHEMA_VERSION,
    DEFAULT_CATALOG,
    PROFILE_SCHEMA_VERSION,
    StewardError,
    build_target_profile,
    detect_templates,
    fail,
    inspect_project,
    load_catalog,
    load_profile,
    merged_decisions,
    package_facts,
    parse_decisions,
    profile_path,
    require_project_root,
    resolve_template_stack,
)


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
