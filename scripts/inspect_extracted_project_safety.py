#!/usr/bin/env python3
"""Statically collect high-impact safety evidence from an extracted project.

The scanner never imports or executes project content. Its findings are
candidates for the semantic gate in references/archive-safety-screening.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = 1
MAX_FILES = 100_000
MAX_BYTES_PER_FILE = 16 * 1024 * 1024
SAMPLE_BYTES = 8 * 1024 * 1024

TEXT_SUFFIXES = {
    ".bat", ".bash", ".c", ".cc", ".cmd", ".conf", ".cpp", ".cs",
    ".go", ".h", ".hpp", ".ini", ".java", ".js", ".json", ".jsx",
    ".kt", ".lua", ".mjs", ".php", ".pl", ".ps1", ".py", ".rb",
    ".rs", ".sh", ".swift", ".toml", ".ts", ".tsx", ".vbs", ".xml",
    ".yaml", ".yml", ".zsh",
}
NATIVE_SUFFIXES = {".com", ".dll", ".dylib", ".exe", ".msi", ".pyd", ".so", ".sys"}
NON_RUNTIME_PARTS = {
    ".venv", "doc", "docs", "documentation", "example", "examples",
    "fixture", "fixtures", "node_modules", "sample", "samples",
    "site-packages", "test", "tests", "vendor", "venv",
}
LIFECYCLE_NAMES = {
    "bootstrap", "install", "installer", "postinstall", "preinstall",
    "prepare", "setup", "startup", "update", "updater",
}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    path: str
    evidence: tuple[str, ...]
    lines: tuple[int, ...] = ()

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "rule_id": self.rule_id,
            "path": self.path,
            "evidence": list(self.evidence),
        }
        if self.lines:
            result["lines"] = list(self.lines)
        return result


REMOTE_PIPE = re.compile(
    r"(?is)(?:curl|wget)\b[^\r\n|]{0,500}\|\s*(?:sh|bash|zsh|powershell|pwsh)\b"
    r"|(?:invoke-webrequest|\biwr\b|downloadstring)\b[^\r\n|]{0,500}\|\s*"
    r"(?:invoke-expression|\biex\b)\b"
)
ENCODED_LOADER = re.compile(
    r"(?is)(?:powershell|pwsh)\b[^\r\n]{0,300}(?:-enc(?:odedcommand)?\b)"
    r"|frombase64string\s*\([^)]{0,500}\).{0,500}(?:invoke-expression|\biex\b|assembly\.load)"
)
DOWNLOADER = re.compile(
    r"(?is)invoke-webrequest|\biwr\b|download(?:file|string)|urlretrieve|"
    r"requests\s*\.\s*get|urllib[^\r\n]{0,80}urlopen|https?\s*\.\s*get|"
    r"\bcurl\b|\bwget\b|internetopenurl|urldownloadtofile"
)
EXECUTOR = re.compile(
    r"(?is)start-process|subprocess\s*\.\s*(?:run|popen|call)|os\s*\.\s*system|"
    r"child_process\s*\.\s*(?:exec|spawn)|exec\s*\.\s*command|"
    r"getruntime\s*\(\s*\)\s*\.\s*exec|createprocess|shellexecute|\bwinexec\b|"
    r"process\s*\.\s*start"
)
PERSISTENCE = re.compile(
    r"(?is)schtasks\b[^\r\n]{0,300}/create|"
    r"(?:reg\s+add|regsetvalue|set-itemproperty)[^\r\n]{0,500}currentversion[\\/]run|"
    r"\bnew-service\b|\bsc(?:\.exe)?\s+create\b|\bcreateservice[aw]?\b|"
    r"systemctl\s+enable\b|crontab\s+(?:-|\w)|[\\/]startup[\\/]"
)
NETWORK_SEND = re.compile(
    r"(?is)requests\s*\.\s*post|https?\s*\.\s*post|upload(?:data|file|string)|"
    r"socket\s*\.\s*(?:send|sendall|sendto)|\b(?:send|sendto)\s*\(|"
    r"winhttpsendrequest|httpsendrequest|\bcurl\b[^\r\n]{0,300}(?:-d|--data|--upload-file)"
)
CREDENTIAL_ACCESS = re.compile(
    r"(?is)cryptunprotectdata|browser[^\r\n]{0,120}(?:cookie|password|credential)|"
    r"(?:login data|local state|keychain|credential manager)|"
    r"[\\/]\.ssh[\\/](?:id_rsa|id_ed25519)|wallet\.dat"
)
KEY_INPUT = re.compile(r"(?is)getasynckeystate|setwindowshookex|keyboard\s*hook|keylog")
DESTRUCTIVE_SCOPE = re.compile(
    r"(?im)^\s*rm\s+-[^\r\n]*rf[^\r\n]*(?:\s/\s*$|\$home|~[\\/])|"
    r"remove-item[^\r\n]{0,200}-recurse[^\r\n]{0,200}(?:userprofile|systemdrive|windows)|"
    r"(?:format|mkfs(?:\.[a-z0-9]+)?)\s+(?:[a-z]:|[\\/]dev[\\/])"
)
MINING_CONTROL = re.compile(r"(?is)stratum\+tcp|\bxmrig\b|cryptonight|randomx")
WALLET_SIGNAL = re.compile(r"(?is)wallet|pool_address|pool\.supportxmr|nanopool")

INJECTION_TERMS = (
    re.compile(r"(?i)virtualallocex"),
    re.compile(r"(?i)writeprocessmemory"),
    re.compile(r"(?i)createremotethread|ntcreatethreadex"),
)


def is_within(child: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((str(child), str(root))) == str(root)
    except ValueError:
        return False


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def looks_native(data: bytes, suffix: str) -> bool:
    if suffix in NATIVE_SUFFIXES:
        return True
    return data.startswith(b"MZ") or data.startswith(b"\x7fELF") or data[:4] in {
        b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe"
    }


def read_sample(path: Path) -> tuple[bytes, bool]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size <= MAX_BYTES_PER_FILE:
            return handle.read(), False
        first = handle.read(SAMPLE_BYTES)
        handle.seek(max(0, size - SAMPLE_BYTES))
        return first + handle.read(SAMPLE_BYTES), True


def binary_strings(data: bytes) -> str:
    ascii_values = (match.group().decode("ascii", "ignore") for match in re.finditer(rb"[\x20-\x7e]{4,}", data))
    wide_values = (
        match.group().decode("utf-16le", "ignore")
        for match in re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", data)
    )
    return "\n".join((*ascii_values, *wide_values))


def line_numbers(text: str, patterns: Iterable[re.Pattern[str]]) -> tuple[int, ...]:
    lines: set[int] = set()
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            lines.add(text.count("\n", 0, match.start()) + 1)
    return tuple(sorted(lines))


def is_runtime_candidate(path: Path, root: Path, native: bool) -> bool:
    if native:
        return True
    parts = {part.lower() for part in path.relative_to(root).parts[:-1]}
    return path.suffix.lower() in TEXT_SUFFIXES and not (parts & NON_RUNTIME_PARTS)


def is_lifecycle(path: Path) -> bool:
    stem = path.stem.lower().replace("-", "_")
    return any(name in stem for name in LIFECYCLE_NAMES)


def analyze_content(path: Path, root: Path, text: str, native: bool) -> list[Finding]:
    if not is_runtime_candidate(path, root, native):
        return []

    rel = relative(path, root)
    findings: list[Finding] = []
    downloader = bool(DOWNLOADER.search(text))
    executor = bool(EXECUTOR.search(text))
    persistence = bool(PERSISTENCE.search(text))
    network_send = bool(NETWORK_SEND.search(text))
    credentials = bool(CREDENTIAL_ACCESS.search(text))
    key_input = bool(KEY_INPUT.search(text))

    if REMOTE_PIPE.search(text):
        findings.append(Finding(
            "remote_payload_pipeline", rel,
            ("remote content acquisition", "direct shell or expression execution"),
            line_numbers(text, (REMOTE_PIPE,)),
        ))
    if ENCODED_LOADER.search(text) and (downloader or network_send):
        findings.append(Finding(
            "encoded_network_loader", rel,
            ("encoded or in-memory loader", "network capability"),
            line_numbers(text, (ENCODED_LOADER, DOWNLOADER, NETWORK_SEND)),
        ))
    if all(pattern.search(text) for pattern in INJECTION_TERMS):
        findings.append(Finding(
            "process_injection_chain", rel,
            ("remote allocation", "cross-process write", "remote thread creation"),
            line_numbers(text, INJECTION_TERMS),
        ))
    if DESTRUCTIVE_SCOPE.search(text):
        findings.append(Finding(
            "destructive_system_scope", rel,
            ("recursive or device-level destructive operation",),
            line_numbers(text, (DESTRUCTIVE_SCOPE,)),
        ))
    if persistence and downloader and executor:
        findings.append(Finding(
            "remote_execution_with_persistence", rel,
            ("remote content acquisition", "process execution", "persistent startup"),
            line_numbers(text, (DOWNLOADER, EXECUTOR, PERSISTENCE)),
        ))
    elif downloader and executor and is_lifecycle(path):
        findings.append(Finding(
            "lifecycle_download_and_execute", rel,
            ("automatic lifecycle entry", "remote content acquisition", "process execution"),
            line_numbers(text, (DOWNLOADER, EXECUTOR)),
        ))
    if credentials and network_send:
        findings.append(Finding(
            "credential_collection_and_transfer", rel,
            ("credential-store access", "outbound transfer"),
            line_numbers(text, (CREDENTIAL_ACCESS, NETWORK_SEND)),
        ))
    if key_input and network_send:
        findings.append(Finding(
            "input_capture_and_transfer", rel,
            ("keyboard or input capture", "outbound transfer"),
            line_numbers(text, (KEY_INPUT, NETWORK_SEND)),
        ))
    if MINING_CONTROL.search(text) and WALLET_SIGNAL.search(text):
        findings.append(Finding(
            "mining_control_chain", rel,
            ("mining protocol or engine", "pool or wallet configuration"),
            line_numbers(text, (MINING_CONTROL, WALLET_SIGNAL)),
        ))
    return findings


def package_lifecycle_findings(path: Path, root: Path, text: str) -> list[Finding]:
    if path.name.lower() != "package.json":
        return []
    parent_parts = {part.lower() for part in path.relative_to(root).parts[:-1]}
    if parent_parts & NON_RUNTIME_PARTS:
        return []
    try:
        payload = json.loads(text)
    except (TypeError, ValueError):
        return []
    scripts = payload.get("scripts") if isinstance(payload, dict) else None
    if not isinstance(scripts, dict):
        return []

    findings: list[Finding] = []
    for name in ("preinstall", "install", "postinstall", "prepare"):
        command = scripts.get(name)
        if not isinstance(command, str):
            continue
        if REMOTE_PIPE.search(command) or (
            DOWNLOADER.search(command) and EXECUTOR.search(command)
        ):
            findings.append(Finding(
                "package_lifecycle_remote_execution",
                relative(path, root),
                (f"package lifecycle: {name}", "remote content acquisition", "process execution"),
            ))
    return findings


def scan(root: Path) -> dict[str, object]:
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise ValueError(f"project root is not a directory: {resolved_root}")

    findings: list[Finding] = []
    scanned_files = 0
    sampled_large_files = 0
    native_files = 0
    errors: list[dict[str, str]] = []
    truncated = False

    for current, dirnames, filenames in os.walk(resolved_root, followlinks=False):
        current_path = Path(current)
        for name in list(dirnames) + list(filenames):
            candidate = current_path / name
            if not candidate.is_symlink():
                continue
            target = candidate.resolve(strict=False)
            if not is_within(target, resolved_root):
                findings.append(Finding(
                    "archive_escape_link",
                    relative(candidate, resolved_root),
                    ("symbolic link resolves outside extracted project root",),
                ))

        dirnames[:] = [
            name
            for name in dirnames
            if name != ".git" and not (current_path / name).is_symlink()
        ]
        for name in filenames:
            path = current_path / name
            if path.is_symlink() or not path.is_file():
                continue
            if scanned_files >= MAX_FILES:
                truncated = True
                break
            scanned_files += 1
            try:
                data, sampled = read_sample(path)
            except (OSError, PermissionError) as error:
                errors.append({"path": relative(path, resolved_root), "error": type(error).__name__})
                continue
            sampled_large_files += int(sampled)
            suffix = path.suffix.lower()
            native = looks_native(data, suffix)
            native_files += int(native)
            if native:
                text = binary_strings(data)
            elif suffix in TEXT_SUFFIXES or path.name.lower() == "package.json":
                text = data.decode("utf-8", "replace")
            else:
                continue
            findings.extend(analyze_content(path, resolved_root, text, native))
            findings.extend(package_lifecycle_findings(path, resolved_root, text))
        if truncated:
            break

    unique: dict[tuple[str, str], Finding] = {}
    for finding in findings:
        unique[(finding.rule_id, finding.path)] = finding
    ordered = sorted(unique.values(), key=lambda item: (item.path, item.rule_id))

    incomplete = truncated or bool(errors)
    if ordered:
        status = "high_impact_evidence"
    elif incomplete:
        status = "incomplete"
    else:
        status = "no_high_impact_evidence"

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_root": str(resolved_root),
        "coverage": {
            "scanned_files": scanned_files,
            "native_files": native_files,
            "sampled_large_files": sampled_large_files,
            "file_limit_reached": truncated,
            "read_errors": errors,
        },
        "high_impact_findings": [finding.as_dict() for finding in ordered],
        "interpretation": "Candidate evidence only; apply references/archive-safety-screening.md before user-visible reporting.",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = scan(args.project_root)
    except (OSError, ValueError) as error:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION,
            "status": "incomplete",
            "error": type(error).__name__,
            "message": str(error),
        }, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
