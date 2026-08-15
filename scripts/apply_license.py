#!/usr/bin/env python3
"""Safely preview or create approved repository license files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from license_content import PLAN_VERSION, PreparedProject, load_catalog, read_json
from license_targets import (
    apply_local_project,
    ensure_mode_targets,
    prepare_projects,
    project_report,
    publish_remote_project,
    verify_local_project,
    verify_remote_project,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight an approved schema v2 license plan, then optionally write "
            "local targets, publish GitHub targets, or verify final state."
        )
    )
    parser.add_argument(
        "--plan",
        required=True,
        type=Path,
        help="Approved JSON plan, or - to read the plan from stdin",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--write",
        action="store_true",
        help="Apply every local project after full-plan preflight.",
    )
    modes.add_argument(
        "--publish",
        action="store_true",
        help="Publish every GitHub project as one atomic commit per repository.",
    )
    modes.add_argument(
        "--verify",
        action="store_true",
        help="Read current targets and verify the plan's final file state.",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        help="Override the bundled license catalog (for catalog maintenance only)",
    )
    return parser.parse_args()
def execute(
    projects: list[PreparedProject],
    operation: str,
    plan_path: Path,
) -> tuple[dict, int]:
    result = {
        "schema_version": PLAN_VERSION,
        "mode": {
            "preview": "dry-run",
            "write": "written",
            "publish": "published",
            "verify": "verified",
        }[operation],
        "plan": str(plan_path),
        "preflight": "passed",
        "projects": [],
    }
    if operation == "preview":
        result["projects"] = [
            project_report(
                project,
                "retained" if project.disposition == "retain" else "ready",
            )
            for project in projects
        ]
        return result, 0

    if operation == "verify":
        for project in projects:
            report = project_report(
                project,
                "retained" if project.disposition == "retain" else "verified",
            )
            if project.disposition == "apply":
                report["verification"] = (
                    verify_local_project(project, project.expected_result_head)
                    if project.target_kind == "local"
                    else verify_remote_project(project)
                )
            result["projects"].append(report)
        return result, 0

    ensure_mode_targets(projects, operation)
    partial_failure = False
    for project in projects:
        report = project_report(
            project,
            "retained" if project.disposition == "retain" else "pending",
        )
        if project.disposition == "retain":
            result["projects"].append(report)
            continue
        try:
            if operation == "write":
                report["verification"] = apply_local_project(project)
                report["status"] = "written"
            else:
                report.update(publish_remote_project(project))
                report["status"] = "published"
        except (ValueError, OSError) as exc:
            partial_failure = True
            report["status"] = "failed"
            report["error"] = str(exc)
        result["projects"].append(report)
    if partial_failure:
        result["outcome"] = (
            "partial-failure; successful projects were not rolled back"
        )
        return result, 3
    result["outcome"] = "complete"
    return result, 0


def main() -> int:
    args = parse_args()
    try:
        plan_path = (
            Path("-") if str(args.plan) == "-" else args.plan.expanduser().resolve()
        )
        catalog_path = (
            args.catalog.expanduser().resolve()
            if args.catalog
            else (
                Path(__file__).resolve().parent.parent
                / "assets"
                / "licenses"
                / "catalog.json"
            )
        )
        plan = read_json(plan_path, "plan")
        catalog = load_catalog(catalog_path)
        operation = (
            "write"
            if args.write
            else "publish"
            if args.publish
            else "verify"
            if args.verify
            else "preview"
        )
        projects = prepare_projects(
            plan, catalog, catalog_path, plan_path, operation
        )
        result, exit_code = execute(projects, operation, plan_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return exit_code
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
