#!/usr/bin/env python3
"""Detect, plan, write, verify, and consume a user environment profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from user_environment_detection import (
    LARGE_CONTENT_CATEGORY_KEYS,
    ProfileError,
    default_profile_path,
    detect_profile,
    preferences_from,
)
from user_environment_schema import (
    diff_values,
    read_profile,
    select_large_content_root,
    select_tool_record,
    stable_view,
    validate_profile,
    verify_profile,
    write_profile,
)


def add_profile_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        type=Path,
        default=default_profile_path(),
        help="Environment profile path",
    )


def add_detection_arguments(parser: argparse.ArgumentParser) -> None:
    add_profile_argument(parser)
    parser.add_argument("--preferred-shell")
    parser.add_argument("--install-root", action="append", default=[])
    parser.add_argument(
        "--scan-root",
        action="append",
        default=[],
        help="Additional read-only discovery root; not stored as an install preference",
    )
    parser.add_argument("--download-root")
    parser.add_argument("--temp-root")
    parser.add_argument(
        "--default-tool",
        action="append",
        default=[],
        help="Preferred capability path in capability=path syntax",
    )
    storage_policy = parser.add_mutually_exclusive_group()
    storage_policy.add_argument(
        "--avoid-system-drive-for-large-content",
        dest="avoid_system_drive_for_large_content",
        action="store_true",
        default=None,
        help="Reject system-drive roots for large application content, projects, media, and generated outputs",
    )
    storage_policy.add_argument(
        "--allow-system-drive-for-large-content",
        dest="avoid_system_drive_for_large_content",
        action="store_false",
        help="Allow explicitly configured system-drive roots for large content",
    )
    parser.add_argument(
        "--large-content-root",
        action="append",
        default=[],
        help="Preferred root in category=path syntax; category is default, application-content, project, media, or generated-output",
    )
    parser.add_argument(
        "--clear-large-content-root",
        action="append",
        choices=tuple(LARGE_CONTENT_CATEGORY_KEYS),
        default=[],
        help="Clear every configured root for one large-content category",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    add_profile_argument(inspect_parser)

    plan_parser = subparsers.add_parser("plan")
    add_detection_arguments(plan_parser)

    apply_parser = subparsers.add_parser("apply")
    add_detection_arguments(apply_parser)
    apply_parser.add_argument(
        "--write",
        action="store_true",
        help="Required acknowledgement for creating or updating the profile",
    )

    verify_parser = subparsers.add_parser("verify")
    add_profile_argument(verify_parser)

    resolve_parser = subparsers.add_parser("resolve")
    add_profile_argument(resolve_parser)
    resolve_parser.add_argument("--capability", required=True)

    resolve_storage_parser = subparsers.add_parser("resolve-storage")
    add_profile_argument(resolve_storage_parser)
    resolve_storage_parser.add_argument(
        "--category",
        required=True,
        choices=tuple(
            category
            for category in LARGE_CONTENT_CATEGORY_KEYS
            if category != "default"
        ),
    )

    return parser.parse_args()


def output(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()
    path = args.profile.expanduser().resolve(strict=False)
    try:
        if args.command == "inspect":
            output(read_profile(path, required=True))
            return 0

        if args.command in {"plan", "apply"}:
            existing = read_profile(path, required=False)
            preferences = preferences_from(existing, args)
            proposed = validate_profile(
                detect_profile(preferences, args.scan_root)
            )
            changes = diff_values(stable_view(existing), stable_view(proposed))
            action = (
                "create"
                if existing is None
                else ("update" if changes else "none")
            )
            result = {
                "profile": str(path),
                "action": action,
                "changes": changes,
                "proposed": proposed,
            }
            if args.command == "plan":
                output(result)
                return 0
            if not args.write:
                raise ProfileError("apply requires --write")
            write_profile(path, proposed)
            result["written"] = True
            output(result)
            return 0

        profile = read_profile(path, required=True)
        if args.command == "verify":
            result = verify_profile(profile)
            result["profile"] = str(path)
            output(result)
            return 0 if result["valid"] else 1

        if args.command == "resolve":
            record, environment = select_tool_record(
                profile,
                args.capability,
            )
            output(
                {
                    "profile": str(path),
                    "capability": args.capability,
                    "tool": record,
                    "environment": environment,
                }
            )
            return 0

        if args.command == "resolve-storage":
            root, policy = select_large_content_root(profile, args.category)
            output(
                {
                    "profile": str(path),
                    "category": args.category,
                    "root": root,
                    "policy": policy,
                }
            )
            return 0
    except ProfileError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
