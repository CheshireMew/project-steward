"""Validate, persist, verify, and resolve user environment profiles."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Iterable
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from user_environment_detection import (
    FORBIDDEN_KEY_PARTS,
    LARGE_CONTENT_CATEGORY_KEYS,
    PROFILE_SCHEMA_PATH,
    ProfileError,
    normalized_path,
    storage_volume,
)


def forbidden_key_paths(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            lowered = key.lower()
            if any(part in lowered for part in FORBIDDEN_KEY_PARTS):
                found.append(path)
            found.extend(forbidden_key_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_key_paths(child, f"{prefix}[{index}]"))
    return found


def load_profile_schema() -> dict[str, Any]:
    try:
        schema = json.loads(PROFILE_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileError(f"cannot read environment profile schema: {error}") from error
    if not isinstance(schema, dict):
        raise ProfileError("environment profile schema must be an object")
    return schema


def resolve_schema_reference(
    root_schema: dict[str, Any],
    reference: str,
) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ProfileError(f"unsupported schema reference: {reference}")
    value: Any = root_schema
    for part in reference[2:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or key not in value:
            raise ProfileError(f"unresolved schema reference: {reference}")
        value = value[key]
    if not isinstance(value, dict):
        raise ProfileError(f"schema reference is not an object: {reference}")
    return value


def value_matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ProfileError(f"unsupported schema type: {expected}")


def validate_schema_value(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str,
) -> None:
    if "$ref" in schema:
        validate_schema_value(
            value,
            resolve_schema_reference(root_schema, schema["$ref"]),
            root_schema,
            path,
        )
        return

    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                validate_schema_value(value, option, root_schema, path)
            except ProfileError:
                continue
            matches += 1
        if matches != 1:
            raise ProfileError(f"{path} must match exactly one schema option")
        return

    if "const" in schema and value != schema["const"]:
        raise ProfileError(f"{path} must equal {schema['const']!r}")

    expected_types = schema.get("type")
    if expected_types is not None:
        choices = (
            expected_types
            if isinstance(expected_types, list)
            else [expected_types]
        )
        if not any(value_matches_type(value, expected) for expected in choices):
            joined = ", ".join(choices)
            raise ProfileError(f"{path} must have type {joined}")

    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = sorted(required - set(value))
        if missing:
            raise ProfileError(f"{path} is missing required fields: {missing}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                child_schema = properties[key]
            elif additional is False:
                raise ProfileError(f"{child_path} is not allowed")
            elif isinstance(additional, dict):
                child_schema = additional
            else:
                continue
            validate_schema_value(child, child_schema, root_schema, child_path)

    if isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, child in enumerate(value):
                validate_schema_value(
                    child,
                    item_schema,
                    root_schema,
                    f"{path}[{index}]",
                )
        if schema.get("uniqueItems"):
            serialized = [
                json.dumps(item, sort_keys=True, ensure_ascii=False)
                for item in value
            ]
            if len(serialized) != len(set(serialized)):
                raise ProfileError(f"{path} must contain unique items")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            raise ProfileError(f"{path} must be at least {minimum}")

    if isinstance(value, str) and schema.get("format") == "date-time":
        candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            datetime.fromisoformat(candidate)
        except ValueError as error:
            raise ProfileError(f"{path} must be an ISO date-time") from error


def large_content_policy(profile: dict[str, Any]) -> dict[str, Any] | None:
    return profile.get("preferences", {}).get("large_content_storage")


def configured_large_content_roots(
    policy: dict[str, Any],
) -> Iterable[tuple[str, str]]:
    for category, values in policy["roots"].items():
        for value in values:
            yield category, value


def validate_large_content_policy(profile: dict[str, Any]) -> None:
    policy = large_content_policy(profile)
    if not policy or not policy["avoid_system_drive"]:
        return
    system_drive = profile.get("machine", {}).get("system_drive")
    system_volume = storage_volume(system_drive) if system_drive else None
    if not system_volume:
        return
    conflicts = [
        f"{category}={value}"
        for category, value in configured_large_content_roots(policy)
        if storage_volume(value) == system_volume
    ]
    if conflicts:
        raise ProfileError(
            "large content roots conflict with the system-drive avoidance policy: "
            + ", ".join(conflicts)
        )


def validate_profile(profile: Any) -> dict[str, Any]:
    schema = load_profile_schema()
    validate_schema_value(profile, schema, schema, "profile")
    forbidden = forbidden_key_paths(profile)
    if forbidden:
        raise ProfileError(
            "profile contains forbidden sensitive keys: "
            + ", ".join(forbidden)
        )
    validate_large_content_policy(profile)
    return profile


def read_profile(path: Path, *, required: bool) -> dict[str, Any] | None:
    if not path.is_file():
        if required:
            raise ProfileError(f"environment profile does not exist: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileError(f"cannot read environment profile: {error}") from error
    return validate_profile(value)


def stable_view(profile: dict[str, Any] | None) -> dict[str, Any] | None:
    if profile is None:
        return None
    result = deepcopy(profile)
    result.pop("updated_at", None)
    result.pop("provenance", None)
    return result


def diff_values(
    before: Any,
    after: Any,
    prefix: str = "",
) -> list[dict[str, Any]]:
    if isinstance(before, dict) and isinstance(after, dict):
        changes: list[dict[str, Any]] = []
        for key in sorted(set(before) | set(after)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in before:
                changes.append({"path": path, "before": None, "after": after[key]})
            elif key not in after:
                changes.append({"path": path, "before": before[key], "after": None})
            else:
                changes.extend(diff_values(before[key], after[key], path))
        return changes
    if before != after:
        return [{"path": prefix, "before": before, "after": after}]
    return []


def write_profile(path: Path, profile: dict[str, Any]) -> None:
    validate_profile(profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(profile, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    try:
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def all_tool_records(profile: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for name, record in profile["shells"].items():
        yield f"shells.{name}", record
    for name, records in profile["tools"].items():
        if isinstance(records, list):
            for index, record in enumerate(records):
                yield f"tools.{name}[{index}]", record
        else:
            yield f"tools.{name}", records


def verify_profile(profile: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    for label, record in all_tool_records(profile):
        path = Path(record["executable"])
        if record["available"] and not path.is_file():
            issues.append(
                {
                    "path": label,
                    "issue": "recorded executable is missing",
                    "value": str(path),
                }
            )
    for section in ("package_locations", "caches"):
        for key, value in profile[section].items():
            values = value if isinstance(value, list) else [value]
            for item in values:
                if not Path(item).exists():
                    issues.append(
                        {
                            "path": f"{section}.{key}",
                            "issue": "recorded path is missing",
                            "value": item,
                        }
                    )
    policy = large_content_policy(profile)
    if policy:
        for category, value in configured_large_content_roots(policy):
            path = Path(value)
            if not path.is_dir():
                issues.append(
                    {
                        "path": f"preferences.large_content_storage.roots.{category}",
                        "issue": "recorded large content root is missing or not a directory",
                        "value": value,
                    }
                )
    return {"valid": not issues, "issues": issues}


def select_large_content_root(
    profile: dict[str, Any],
    category: str,
) -> tuple[str, dict[str, Any]]:
    policy = large_content_policy(profile)
    if not policy:
        raise ProfileError(
            "large content storage policy is not configured; run plan and apply first"
        )
    key = LARGE_CONTENT_CATEGORY_KEYS[category]
    candidates = list(policy["roots"][key])
    if key != "default":
        candidates.extend(policy["roots"]["default"])
    candidates = list(dict.fromkeys(candidates))
    if not candidates:
        raise ProfileError(f"no large content root is configured for: {category}")

    system_drive = profile.get("machine", {}).get("system_drive")
    system_volume = storage_volume(system_drive) if system_drive else None
    if (
        policy["avoid_system_drive"]
        and profile["machine"]["system"] == "Windows"
        and not system_volume
    ):
        raise ProfileError(
            "system drive is unknown; cannot enforce large content storage policy"
        )

    rejected: list[dict[str, str]] = []
    for candidate in candidates:
        path = Path(candidate)
        if not path.is_dir():
            rejected.append({"root": candidate, "reason": "missing-or-not-directory"})
            continue
        if (
            policy["avoid_system_drive"]
            and system_volume
            and storage_volume(candidate) == system_volume
        ):
            rejected.append({"root": candidate, "reason": "system-drive"})
            continue
        return normalized_path(path), {
            "avoid_system_drive": policy["avoid_system_drive"],
            "system_drive": system_drive,
            "rejected": rejected,
        }
    raise ProfileError(
        "no configured large content root satisfies the active policy: "
        + json.dumps(rejected, ensure_ascii=False)
    )


def select_tool_record(
    profile: dict[str, Any],
    capability: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    if capability == "shell":
        preferred = profile["preferences"].get("preferred_shell")
        if not preferred:
            raise ProfileError("no preferred shell is configured")
        record = profile["shells"].get(preferred)
        if not record:
            raise ProfileError(f"preferred shell is unavailable: {preferred}")
        return record, {}

    records = profile["tools"].get(capability)
    if records is None:
        raise ProfileError(f"capability is not recorded: {capability}")
    candidates = records if isinstance(records, list) else [records]
    preferred_path = profile["preferences"]["default_tools"].get(capability)
    selected: dict[str, Any] | None = None
    if preferred_path:
        preferred_key = os.path.normcase(normalized_path(preferred_path))
        selected = next(
            (
                record
                for record in candidates
                if os.path.normcase(record["executable"]) == preferred_key
            ),
            None,
        )
        if selected is None:
            raise ProfileError(
                f"default {capability} is not present in detected tools: "
                f"{preferred_path}"
            )
    else:
        selected = next(
            (record for record in candidates if record["available"]),
            None,
        )
    if selected is None:
        raise ProfileError(f"no available tool for capability: {capability}")

    environment: dict[str, str] = {}
    if capability in {"cargo", "rustc", "rustup"}:
        environment = dict(
            profile["environment_requirements"].get("rust", {})
        )
    return selected, environment
