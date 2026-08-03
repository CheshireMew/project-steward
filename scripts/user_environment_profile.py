#!/usr/bin/env python3
"""Detect, plan, write, verify, and consume a user environment profile."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
DETECTOR_VERSION = 1
PROFILE_KIND = "project-steward-user-environment"
PROFILE_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "user-environment"
    / "profile.schema.json"
)
FORBIDDEN_KEY_PARTS = (
    "auth",
    "cookie",
    "credential",
    "password",
    "secret",
    "token",
)
LARGE_CONTENT_CATEGORY_KEYS = {
    "default": "default",
    "application-content": "application_content",
    "project": "projects",
    "media": "media",
    "generated-output": "generated_outputs",
}
LARGE_CONTENT_ROOT_KEYS = tuple(LARGE_CONTENT_CATEGORY_KEYS.values())


class ProfileError(ValueError):
    """Raised when profile input or detected state is invalid."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_profile_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    root = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
    return root / "project-steward" / "environment-profile.json"


def normalized_path(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve(strict=False))


def storage_volume(value: str | Path) -> str | None:
    text = str(value).strip()
    windows_drive = re.match(r"^([A-Za-z]):(?:[\\/]|$)", text)
    if windows_drive:
        return windows_drive.group(1).lower()
    drive = os.path.splitdrive(text)[0].rstrip("\\/")
    return os.path.normcase(drive) if drive else None


def empty_large_content_roots() -> dict[str, list[str]]:
    return {key: [] for key in LARGE_CONTENT_ROOT_KEYS}


def existing_paths(values: Iterable[str | Path]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        path = normalized_path(value)
        key = os.path.normcase(path)
        if key in seen or not Path(path).exists():
            continue
        seen.add(key)
        result.append(path)
    return result


def run_command(
    command: list[str],
    *,
    environment: dict[str, str] | None = None,
    timeout: int = 8,
) -> tuple[int, str, str]:
    env = os.environ.copy()
    if environment:
        env.update(environment)
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return 1, "", str(error)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def first_output_line(stdout: str, stderr: str) -> str | None:
    for text in (stdout, stderr):
        for line in text.splitlines():
            value = line.strip()
            if value:
                return value
    return None


def executable_record(
    executable: str | Path,
    version_arguments: list[str],
    *,
    environment: dict[str, str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = normalized_path(executable)
    available = Path(path).is_file()
    version: str | None = None
    if available:
        code, stdout, stderr = run_command(
            [path, *version_arguments],
            environment=environment,
        )
        if code == 0:
            version = first_output_line(stdout, stderr)
    record: dict[str, Any] = {
        "executable": path,
        "version": version,
        "available": available,
    }
    if details:
        record["details"] = details
    return record


def command_paths(name: str) -> list[str]:
    suffixes = ("", ".exe", ".cmd", ".bat") if os.name == "nt" else ("",)
    return existing_paths(
        shutil.which(f"{name}{suffix}") or "" for suffix in suffixes
    )


def scan_candidates(
    roots: list[str],
    relative_patterns: Iterable[str],
) -> list[str]:
    candidates: list[str] = []
    for root_value in roots:
        root = Path(root_value)
        for pattern in relative_patterns:
            candidates.extend(str(path) for path in root.glob(pattern))
    return existing_paths(candidates)


def detect_shells() -> dict[str, dict[str, Any]]:
    definitions: dict[str, tuple[list[str], list[str]]] = {
        "pwsh": (command_paths("pwsh"), ["--version"]),
        "powershell": (
            command_paths("powershell"),
            ["-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
        ),
        "bash": (command_paths("bash"), ["--version"]),
        "wsl": (command_paths("wsl"), ["--version"]),
        "sh": (command_paths("sh"), ["--version"]),
    }
    if os.name == "nt":
        definitions["bash"][0].extend(
            existing_paths([r"C:\Program Files\Git\bin\bash.exe"])
        )

    shells: dict[str, dict[str, Any]] = {}
    for name, (paths, arguments) in definitions.items():
        if not paths:
            continue
        record = executable_record(paths[0], arguments)
        if name == "wsl":
            code, _, _ = run_command([paths[0], "--status"], timeout=5)
            record.setdefault("details", {})["subsystem_ready"] = code == 0
        shells[name] = record
    return shells


def detect_python_launcher() -> dict[str, Any] | None:
    launcher = shutil.which("py")
    if not launcher:
        return None
    record = executable_record(launcher, ["--version"])
    code, stdout, _ = run_command(
        [launcher, "-c", "import sys;print(sys.executable)"]
    )
    if code == 0 and stdout:
        record.setdefault("details", {})["default_python"] = normalized_path(
            stdout.splitlines()[-1]
        )
    return record


def python_launcher_paths() -> list[str]:
    paths: list[str] = []
    launcher = shutil.which("py")
    if not launcher:
        return paths
    code, stdout, _ = run_command([launcher, "-0p"])
    if code != 0:
        return paths
    for line in stdout.splitlines():
        match = re.search(r"([A-Za-z]:\\.+?python\.exe|/.+?/python[0-9.]*)\s*$", line)
        if match:
            paths.append(match.group(1))
    return paths


def python_details(executable: str) -> dict[str, Any]:
    program = (
        "import json,site,sys;"
        "print(json.dumps({"
        "'version':sys.version.split()[0],"
        "'prefix':sys.prefix,"
        "'site_packages':site.getsitepackages(),"
        "'user_site':site.getusersitepackages()"
        "},ensure_ascii=False))"
    )
    code, stdout, _ = run_command([executable, "-c", program])
    if code != 0:
        return {}
    try:
        details = json.loads(stdout.splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {}
    pip_code, pip_stdout, _ = run_command(
        [executable, "-m", "pip", "cache", "dir"]
    )
    if pip_code == 0 and pip_stdout:
        details["pip_cache"] = normalized_path(pip_stdout.splitlines()[-1])
    scripts = Path(details.get("prefix", "")).joinpath(
        "Scripts" if os.name == "nt" else "bin"
    )
    for name in ("pip.exe", "pip3", "pip"):
        candidate = scripts / name
        if candidate.is_file():
            details["pip_executable"] = normalized_path(candidate)
            break
    return details


def detect_python(roots: list[str]) -> list[dict[str, Any]]:
    candidates = [
        sys.executable,
        *command_paths("python"),
        *command_paths("python3"),
        *python_launcher_paths(),
        *scan_candidates(
            roots,
            (
                "Python*/python.exe",
                "Python*/bin/python",
                "Python*/bin/python3",
            ),
        ),
    ]
    records: list[dict[str, Any]] = []
    for executable in existing_paths(candidates):
        details = python_details(executable)
        version = details.pop("version", None)
        records.append(
            {
                "executable": executable,
                "version": version,
                "available": Path(executable).is_file(),
                "details": details,
            }
        )
    return records


def detect_node(roots: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates = [
        *command_paths("node"),
        *scan_candidates(roots, ("NodeJS/node.exe", "node/bin/node")),
    ]
    node_records = [
        executable_record(path, ["--version"])
        for path in existing_paths(candidates)
    ]

    npm_paths = command_paths("npm")
    for record in node_records:
        parent = Path(record["executable"]).parent
        npm_paths.extend(existing_paths([parent / "npm.cmd", parent / "npm"]))
    npm_paths = existing_paths(npm_paths)
    npm: dict[str, Any] = {}
    if npm_paths:
        executable = npm_paths[0]
        npm = executable_record(executable, ["--version"])
        for key, arguments in (
            ("prefix", ["config", "get", "prefix"]),
            ("global_root", ["root", "-g"]),
            ("cache", ["config", "get", "cache"]),
        ):
            code, stdout, _ = run_command([executable, *arguments])
            if code == 0 and stdout:
                npm.setdefault("details", {})[key] = normalized_path(
                    stdout.splitlines()[-1]
                )
    return node_records, npm


def rust_environment(roots: list[str], cargo_paths: list[str]) -> dict[str, str]:
    cargo_home_candidates = scan_candidates(roots, ("Rust/cargo", ".cargo"))
    rustup_home_candidates = scan_candidates(roots, ("Rust/rustup", ".rustup"))
    for cargo_path in cargo_paths:
        path = Path(cargo_path)
        if path.parent.name.lower() == "bin":
            cargo_home_candidates.extend(existing_paths([path.parent.parent]))
    environment: dict[str, str] = {}
    if cargo_home_candidates:
        environment["CARGO_HOME"] = cargo_home_candidates[0]
    if rustup_home_candidates:
        environment["RUSTUP_HOME"] = rustup_home_candidates[0]
    return environment


def detect_rust(
    roots: list[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    cargo_paths = existing_paths(
        [
            *command_paths("cargo"),
            *scan_candidates(roots, ("Rust/cargo/bin/cargo.exe", ".cargo/bin/cargo")),
        ]
    )
    environment = rust_environment(roots, cargo_paths)
    tools: dict[str, list[dict[str, Any]]] = {}
    definitions = {
        "cargo": (cargo_paths, ["--version"]),
        "rustc": (
            existing_paths(
                [
                    *command_paths("rustc"),
                    *scan_candidates(
                        roots,
                        ("Rust/cargo/bin/rustc.exe", ".cargo/bin/rustc"),
                    ),
                ]
            ),
            ["--version"],
        ),
        "rustup": (
            existing_paths(
                [
                    *command_paths("rustup"),
                    *scan_candidates(
                        roots,
                        ("Rust/cargo/bin/rustup.exe", ".cargo/bin/rustup"),
                    ),
                ]
            ),
            ["show", "active-toolchain"],
        ),
    }
    for name, (paths, arguments) in definitions.items():
        if paths:
            tools[name] = [
                executable_record(
                    path,
                    arguments,
                    environment=environment,
                )
                for path in paths
            ]
    return tools, environment


def detect_java(roots: list[str]) -> list[dict[str, Any]]:
    paths = existing_paths(
        [
            *command_paths("java"),
            *scan_candidates(
                roots,
                (
                    "*/bin/java.exe",
                    "*/*/bin/java.exe",
                    "*/bin/java",
                    "*/*/bin/java",
                ),
            ),
        ]
    )
    return [executable_record(path, ["-version"]) for path in paths]


def detect_android_and_gradle(
    roots: list[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str], dict[str, str]]:
    package_locations: dict[str, str] = {}
    caches: dict[str, str] = {}
    tools: dict[str, list[dict[str, Any]]] = {}

    sdk_candidates = existing_paths(
        [
            os.environ.get("ANDROID_HOME", ""),
            os.environ.get("ANDROID_SDK_ROOT", ""),
            *scan_candidates(roots, ("Android/Sdk", "Android/sdk")),
        ]
    )
    if sdk_candidates:
        sdk = Path(sdk_candidates[0])
        package_locations["android_sdk"] = str(sdk)
        for name in ("build-tools", "platforms", "ndk", "platform-tools"):
            candidate = sdk / name
            if candidate.is_dir():
                package_locations[f"android_{name.replace('-', '_')}"] = str(
                    candidate
                )
        adb = sdk / "platform-tools" / (
            "adb.exe" if os.name == "nt" else "adb"
        )
        if adb.is_file():
            tools["adb"] = [executable_record(adb, ["version"])]

    gradle_candidates = existing_paths(
        [
            os.environ.get("GRADLE_USER_HOME", ""),
            *scan_candidates(roots, ("Gradle", ".gradle")),
        ]
    )
    if gradle_candidates:
        caches["gradle_user_home"] = gradle_candidates[0]
    return tools, package_locations, caches


def package_and_cache_locations(
    python_records: list[dict[str, Any]],
    npm: dict[str, Any],
    rust_environment_values: dict[str, str],
) -> tuple[dict[str, Any], dict[str, str]]:
    packages: dict[str, Any] = {}
    caches: dict[str, str] = {}

    python_sites: list[str] = []
    python_user_sites: list[str] = []
    pip_executables: list[str] = []
    for record in python_records:
        details = record.get("details", {})
        python_sites.extend(details.get("site_packages", []))
        if details.get("user_site"):
            python_user_sites.append(details["user_site"])
        if details.get("pip_executable"):
            pip_executables.append(details["pip_executable"])
        if details.get("pip_cache"):
            caches["pip"] = details["pip_cache"]
    if python_sites:
        packages["python_site_packages"] = existing_paths(python_sites)
    if python_user_sites:
        existing_user_sites = existing_paths(python_user_sites)
        if existing_user_sites:
            packages["python_user_site"] = existing_user_sites
    if pip_executables:
        packages["pip_executables"] = existing_paths(pip_executables)

    npm_details = npm.get("details", {})
    if npm_details.get("global_root"):
        packages["npm_global_root"] = npm_details["global_root"]
    if npm_details.get("prefix"):
        packages["npm_prefix"] = npm_details["prefix"]
    if npm_details.get("cache"):
        caches["npm"] = npm_details["cache"]

    cargo_home = rust_environment_values.get("CARGO_HOME")
    if cargo_home:
        registry = Path(cargo_home) / "registry"
        if registry.is_dir():
            packages["cargo_registry"] = normalized_path(registry)
    return packages, caches


def parse_default_tools(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise ProfileError(
                f"default tool must use capability=path syntax: {item}"
            )
        capability, value = item.split("=", 1)
        capability = capability.strip()
        value = value.strip()
        if not capability or not value:
            raise ProfileError(f"invalid default tool: {item}")
        result[capability] = normalized_path(value)
    return result


def parse_large_content_roots(
    values: list[str],
    existing: dict[str, Any],
    cleared_categories: list[str],
) -> dict[str, list[str]]:
    roots = empty_large_content_roots()
    for key in roots:
        roots[key] = [normalized_path(value) for value in existing.get(key, [])]
    for category in cleared_categories:
        roots[LARGE_CONTENT_CATEGORY_KEYS[category]] = []

    replacements: dict[str, list[str]] = {}
    for item in values:
        if "=" not in item:
            raise ProfileError(
                "large content root must use category=path syntax: " + item
            )
        category, value = item.split("=", 1)
        category = category.strip()
        value = value.strip()
        if category not in LARGE_CONTENT_CATEGORY_KEYS or not value:
            raise ProfileError(f"invalid large content root: {item}")
        key = LARGE_CONTENT_CATEGORY_KEYS[category]
        replacements.setdefault(key, []).append(normalized_path(value))
    for key, values_for_key in replacements.items():
        roots[key] = list(dict.fromkeys(values_for_key))
    return roots


def preferences_from(
    existing: dict[str, Any] | None,
    args: argparse.Namespace,
) -> dict[str, Any]:
    current = deepcopy((existing or {}).get("preferences", {}))
    install_roots = list(current.get("install_roots", []))
    if getattr(args, "install_root", None):
        install_roots = [normalized_path(value) for value in args.install_root]
    preferred_shell = (
        args.preferred_shell
        if getattr(args, "preferred_shell", None) is not None
        else current.get("preferred_shell")
    )
    download_root = (
        normalized_path(args.download_root)
        if getattr(args, "download_root", None)
        else current.get("download_root")
    )
    temp_root = (
        normalized_path(args.temp_root)
        if getattr(args, "temp_root", None)
        else current.get("temp_root")
    )
    default_tools = dict(current.get("default_tools", {}))
    default_tools.update(parse_default_tools(getattr(args, "default_tool", [])))
    current_storage = deepcopy(current.get("large_content_storage", {}))
    avoid_system_drive = getattr(
        args,
        "avoid_system_drive_for_large_content",
        None,
    )
    if avoid_system_drive is None:
        avoid_system_drive = bool(current_storage.get("avoid_system_drive", False))
    large_content_roots = parse_large_content_roots(
        getattr(args, "large_content_root", []),
        current_storage.get("roots", {}),
        getattr(args, "clear_large_content_root", []),
    )
    return {
        "preferred_shell": preferred_shell,
        "install_roots": list(dict.fromkeys(install_roots)),
        "download_root": download_root,
        "temp_root": temp_root,
        "default_tools": default_tools,
        "large_content_storage": {
            "avoid_system_drive": avoid_system_drive,
            "roots": large_content_roots,
        },
    }


def detect_profile(
    preferences: dict[str, Any],
    scan_roots: list[str],
) -> dict[str, Any]:
    roots = list(
        dict.fromkeys(
            [
                *preferences["install_roots"],
                *(normalized_path(value) for value in scan_roots),
            ]
        )
    )
    python_records = detect_python(roots)
    node_records, npm_record = detect_node(roots)
    rust_tools, rust_environment_values = detect_rust(roots)
    java_records = detect_java(roots)
    android_tools, android_packages, android_caches = (
        detect_android_and_gradle(roots)
    )
    package_locations, caches = package_and_cache_locations(
        python_records,
        npm_record,
        rust_environment_values,
    )
    package_locations.update(android_packages)
    caches.update(android_caches)

    tools: dict[str, Any] = {
        "python": python_records,
        "node": node_records,
    }
    python_launcher = detect_python_launcher()
    if python_launcher:
        tools["py_launcher"] = python_launcher
    if npm_record:
        tools["npm"] = npm_record
    tools.update(rust_tools)
    if java_records:
        tools["java"] = java_records
    tools.update(android_tools)

    detected_at = utc_now()
    return {
        "schema_version": SCHEMA_VERSION,
        "profile_kind": PROFILE_KIND,
        "updated_at": detected_at,
        "preferences": preferences,
        "machine": detect_machine(),
        "shells": detect_shells(),
        "tools": tools,
        "package_locations": package_locations,
        "caches": caches,
        "environment_requirements": (
            {"rust": rust_environment_values}
            if rust_environment_values
            else {}
        ),
        "provenance": {
            "detector_version": DETECTOR_VERSION,
            "detected_at": detected_at,
        },
    }


def detect_machine() -> dict[str, str]:
    system = platform.system()
    release = platform.release()
    version = platform.version()
    if system == "Windows":
        version_parts = re.findall(r"\d+", version)
        build = int(version_parts[2]) if len(version_parts) >= 3 else 0
        if build >= 22000:
            release = "11"
    result = {
        "hostname": socket.gethostname(),
        "system": system,
        "release": release,
        "version": version,
        "architecture": platform.machine(),
    }
    if system == "Windows":
        system_drive = os.environ.get("SystemDrive")
        if not system_drive:
            system_drive = os.path.splitdrive(
                os.environ.get("SystemRoot", "")
            )[0]
        if system_drive:
            result["system_drive"] = system_drive.rstrip("\\/")
    return result


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
    if policy["avoid_system_drive"] and profile["machine"]["system"] == "Windows":
        if not system_volume:
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
