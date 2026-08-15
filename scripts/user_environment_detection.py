"""Detect tools, machine facts, preferences, and storage roots."""

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
from collections.abc import Iterable
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
