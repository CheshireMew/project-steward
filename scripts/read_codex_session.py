#!/usr/bin/env python3
"""Capture and project a stable Codex JSONL session record."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable, Iterator
import ctypes
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Sequence


THREAD_ID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
CHUNK_SIZE = 1024 * 1024
PUBLIC_ITEM_TYPES = {"UserMessage", "AgentMessage"}
CONTEXT_ROLES = {"developer", "system", "user"}


class SessionReadError(RuntimeError):
    """A stable, user-facing session acquisition failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Capture the exact current Codex session through a writer-compatible "
            "shared read and return a verified immutable JSONL snapshot."
        )
    )
    parser.add_argument(
        "--thread-id",
        help="Exact Codex thread/session UUID; defaults to the Codex environment.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="Codex data root; defaults to CODEX_HOME or the user .codex directory.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Explicit session JSONL source, primarily for deterministic verification.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Parent for the unique snapshot directory; defaults to the system temp root.",
    )
    return parser.parse_args(argv)


def resolve_thread_id(explicit: str | None) -> str:
    candidates = (
        explicit,
        os.environ.get("CODEX_THREAD_ID"),
        os.environ.get("CODEX_SESSION_ID"),
    )
    thread_id = next((value.strip() for value in candidates if value and value.strip()), "")
    if not thread_id:
        raise SessionReadError(
            "thread_identity_missing",
            "Codex did not expose CODEX_THREAD_ID or CODEX_SESSION_ID; pass --thread-id.",
        )
    if not THREAD_ID_PATTERN.fullmatch(thread_id):
        raise SessionReadError(
            "thread_identity_invalid",
            f"The Codex thread identity is not a UUID: {thread_id!r}.",
        )
    return thread_id.lower()


def resolve_codex_home(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def locate_session_record(
    thread_id: str,
    codex_home: Path,
    explicit_source: Path | None,
) -> Path:
    if explicit_source is not None:
        source = explicit_source.expanduser().resolve()
        if not source.is_file():
            raise SessionReadError(
                "session_record_missing",
                f"The explicit Codex session record does not exist: {source}",
            )
        return source

    sessions_root = codex_home / "sessions"
    if not sessions_root.is_dir():
        raise SessionReadError(
            "sessions_root_missing",
            f"The Codex sessions directory does not exist: {sessions_root}",
        )
    matches = sorted(
        path.resolve()
        for path in sessions_root.glob(f"*/*/*/*-{thread_id}.jsonl")
        if path.is_file()
    )
    if not matches:
        raise SessionReadError(
            "session_record_missing",
            f"No Codex session record matches the exact thread identity {thread_id}.",
        )
    if len(matches) != 1:
        raise SessionReadError(
            "session_record_ambiguous",
            f"Expected one Codex session record for {thread_id}, found {len(matches)}.",
        )
    return matches[0]


def open_shared_read(path: Path) -> BinaryIO:
    if os.name != "nt":
        return path.open("rb")

    import msvcrt
    from ctypes import wintypes

    generic_read = 0x80000000
    file_share_read = 0x00000001
    file_share_write = 0x00000002
    file_share_delete = 0x00000004
    open_existing = 3
    file_attribute_normal = 0x00000080
    invalid_handle_value = ctypes.c_void_p(-1).value

    create_file = ctypes.WinDLL("kernel32", use_last_error=True).CreateFileW
    create_file.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    create_file.restype = wintypes.HANDLE
    handle = create_file(
        str(path),
        generic_read,
        file_share_read | file_share_write | file_share_delete,
        None,
        open_existing,
        file_attribute_normal,
        None,
    )
    if handle == invalid_handle_value:
        error = ctypes.get_last_error()
        raise SessionReadError(
            "session_shared_read_failed",
            f"Windows could not open the Codex session with shared read access (error {error}).",
        )
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except Exception:
        ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(handle)
        raise
    return os.fdopen(descriptor, "rb", closefd=True)


def copy_frozen_source(source: Path, destination: Path) -> tuple[int, int]:
    try:
        stream = open_shared_read(source)
    except SessionReadError:
        raise
    except OSError as error:
        raise SessionReadError(
            "session_shared_read_failed",
            f"Could not open the Codex session record with shared read access: {error}",
        ) from error

    try:
        frozen_bytes = os.fstat(stream.fileno()).st_size
        remaining = frozen_bytes
        copied = 0
        last_newline = -1
        with destination.open("wb") as snapshot:
            while remaining:
                chunk = stream.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                snapshot.write(chunk)
                newline = chunk.rfind(b"\n")
                if newline >= 0:
                    last_newline = copied + newline
                copied += len(chunk)
                remaining -= len(chunk)
    finally:
        stream.close()

    if copied != frozen_bytes:
        raise SessionReadError(
            "session_short_read",
            f"The frozen session expected {frozen_bytes} bytes but returned {copied}.",
        )
    if last_newline < 0:
        raise SessionReadError(
            "session_has_no_complete_record",
            "The frozen Codex session contains no complete newline-terminated JSONL record.",
        )
    complete_bytes = last_newline + 1
    with destination.open("r+b") as snapshot:
        snapshot.truncate(complete_bytes)
    return frozen_bytes, complete_bytes


def validate_snapshot(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    complete_records = 0
    try:
        with path.open("rb") as snapshot:
            for line_number, raw_line in enumerate(snapshot, start=1):
                digest.update(raw_line)
                try:
                    text = raw_line.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise SessionReadError(
                        "session_utf8_invalid",
                        f"Codex session record {line_number} is not valid UTF-8.",
                    ) from error
                try:
                    json.loads(text)
                except json.JSONDecodeError as error:
                    raise SessionReadError(
                        "session_json_invalid",
                        f"Codex session record {line_number} is not valid JSON: {error.msg}.",
                    ) from error
                complete_records += 1
    except OSError as error:
        raise SessionReadError(
            "snapshot_read_failed",
            f"Could not validate the captured Codex snapshot: {error}",
        ) from error
    return complete_records, digest.hexdigest().upper()


def read_snapshot_records(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    try:
        with path.open("r", encoding="utf-8") as snapshot:
            for line_number, line in enumerate(snapshot, start=1):
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise SessionReadError(
                        "session_projection_invalid",
                        f"Codex session record {line_number} is not a JSON object.",
                    )
                yield line_number, record
    except SessionReadError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SessionReadError(
            "snapshot_projection_failed",
            f"Could not project the captured Codex snapshot: {error}",
        ) from error


def require_mapping(value: object, line_number: int, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SessionReadError(
            "session_projection_invalid",
            f"Codex session record {line_number} has no valid {label} object.",
        )
    return value


def require_identity(value: object, line_number: int, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SessionReadError(
            "session_projection_invalid",
            f"Codex session record {line_number} has no stable {label}.",
        )
    return value


def public_message_ids(path: Path) -> set[str]:
    identities: set[str] = set()
    for line_number, record in read_snapshot_records(path):
        if record.get("type") != "event_msg":
            continue
        payload = require_mapping(record.get("payload"), line_number, "event payload")
        if payload.get("type") != "item_completed":
            continue
        item = require_mapping(payload.get("item"), line_number, "completed item")
        if item.get("type") not in PUBLIC_ITEM_TYPES:
            continue
        identity = require_identity(item.get("id"), line_number, "public message identity")
        if identity in identities:
            raise SessionReadError(
                "session_projection_invalid",
                f"Codex public message identity is duplicated at record {line_number}: {identity}",
            )
        if not isinstance(item.get("content"), (dict, list)):
            raise SessionReadError(
                "session_projection_invalid",
                f"Codex public message {identity} has no structured content at record {line_number}.",
            )
        identities.add(identity)
    return identities


def project_public_dialogue(
    path: Path,
) -> Iterator[dict[str, Any]]:
    for line_number, record in read_snapshot_records(path):
        if record.get("type") != "event_msg":
            continue
        payload = require_mapping(record.get("payload"), line_number, "event payload")
        if payload.get("type") != "item_completed":
            continue
        item = require_mapping(payload.get("item"), line_number, "completed item")
        item_type = item.get("type")
        if item_type not in PUBLIC_ITEM_TYPES:
            continue
        identity = require_identity(item.get("id"), line_number, "public message identity")
        content = item.get("content")
        if not isinstance(content, (dict, list)):
            raise SessionReadError(
                "session_projection_invalid",
                f"Codex public message {identity} has no structured content at record {line_number}.",
            )
        yield {
            "record_line": line_number,
            "timestamp": record.get("timestamp"),
            "message_id": identity,
            "speaker": "user" if item_type == "UserMessage" else "assistant",
            "phase": item.get("phase"),
            "content": content,
        }


def project_context_sources(
    path: Path,
    public_ids: set[str],
) -> Iterator[dict[str, Any]]:
    for line_number, record in read_snapshot_records(path):
        if record.get("type") != "response_item":
            continue
        payload = require_mapping(record.get("payload"), line_number, "response payload")
        if payload.get("type") != "message":
            continue
        role = payload.get("role")
        identity = payload.get("id")
        if role == "user" and isinstance(identity, str) and identity in public_ids:
            continue
        if role not in CONTEXT_ROLES:
            continue
        if not isinstance(payload.get("content"), list):
            raise SessionReadError(
                "session_projection_invalid",
                f"Codex context message at record {line_number} has no content list.",
            )
        yield {
            "record_line": line_number,
            "timestamp": record.get("timestamp"),
            "message_id": identity,
            "transport_role": role,
            "classification": "host_context",
            "content": payload["content"],
        }


def project_process_events(path: Path) -> Iterator[dict[str, Any]]:
    for line_number, record in read_snapshot_records(path):
        if record.get("type") != "event_msg":
            continue
        payload = require_mapping(record.get("payload"), line_number, "event payload")
        event_type = payload.get("type")
        if event_type == "token_count":
            continue
        if event_type == "item_completed":
            item = require_mapping(payload.get("item"), line_number, "completed item")
            if item.get("type") in PUBLIC_ITEM_TYPES | {"Reasoning"}:
                continue
            yield {
                "record_line": line_number,
                "timestamp": record.get("timestamp"),
                "event_type": event_type,
                "item_type": item.get("type"),
                "item_id": item.get("id"),
                "status": item.get("status"),
                "item": item,
            }
            continue
        yield {
            "record_line": line_number,
            "timestamp": record.get("timestamp"),
            "event_type": event_type,
            "payload": payload,
        }


def write_projection(
    path: Path,
    records: Iterable[dict[str, Any]],
    *count_fields: str,
) -> dict[str, object]:
    digest = hashlib.sha256()
    count = 0
    first_record_line: int | None = None
    last_record_line: int | None = None
    dimensions = {field: Counter[str]() for field in count_fields}
    try:
        with path.open("wb") as output:
            for record in records:
                record_line = record.get("record_line")
                if not isinstance(record_line, int) or record_line < 1:
                    raise SessionReadError(
                        "session_projection_invalid",
                        f"Codex session projection {path.name} has no valid record cursor.",
                    )
                if last_record_line is not None and record_line <= last_record_line:
                    raise SessionReadError(
                        "session_projection_invalid",
                        f"Codex session projection {path.name} has an unordered record cursor.",
                    )
                if first_record_line is None:
                    first_record_line = record_line
                last_record_line = record_line
                encoded = (
                    json.dumps(
                        record,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                    + b"\n"
                )
                output.write(encoded)
                digest.update(encoded)
                count += 1
                for field, counter in dimensions.items():
                    counter[str(record.get(field))] += 1
    except OSError as error:
        raise SessionReadError(
            "session_projection_write_failed",
            f"Could not write Codex session projection {path.name}: {error}",
        ) from error
    result: dict[str, object] = {
        "path": str(path),
        "records": count,
        "sha256": digest.hexdigest().upper(),
        "source_record_cursor": {
            "first_line": first_record_line,
            "last_line": last_record_line,
        },
    }
    for field, counter in dimensions.items():
        result[f"{field}_counts"] = dict(sorted(counter.items()))
    return result


def project_snapshot(path: Path) -> dict[str, object]:
    public_ids = public_message_ids(path)
    root = path.parent
    public_path = root / "public-dialogue.jsonl"
    context_path = root / "context-sources.jsonl"
    process_path = root / "process-events.jsonl"
    return {
        "public_dialogue": write_projection(
            public_path,
            project_public_dialogue(path),
            "speaker",
            "phase",
        ),
        "context_sources": write_projection(
            context_path,
            project_context_sources(path, public_ids),
            "transport_role",
        ),
        "process_events": write_projection(
            process_path,
            project_process_events(path),
            "event_type",
            "item_type",
            "status",
        ),
    }


def capture_session(
    thread_id: str,
    source: Path,
    output_root: Path | None,
) -> dict[str, object]:
    if output_root is not None:
        output_root = output_root.expanduser().resolve()
        output_root.mkdir(parents=True, exist_ok=True)
    snapshot_dir = Path(
        tempfile.mkdtemp(prefix=f"codex-session-{thread_id}-", dir=output_root)
    )
    snapshot_path = snapshot_dir / "session.jsonl"
    try:
        frozen_bytes, complete_bytes = copy_frozen_source(source, snapshot_path)
        complete_records, sha256 = validate_snapshot(snapshot_path)
        manifest: dict[str, object] = {
            "thread_id": thread_id,
            "source": str(source),
            "snapshot": str(snapshot_path),
            "cutoff_bytes": frozen_bytes,
            "complete_bytes": complete_bytes,
            "complete_records": complete_records,
            "trailing_incomplete_bytes": frozen_bytes - complete_bytes,
            "parse_errors": 0,
            "sha256": sha256,
            "projections": project_snapshot(snapshot_path),
        }
        manifest_path = snapshot_dir / "manifest.json"
        manifest["manifest"] = str(manifest_path)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return manifest
    except Exception:
        shutil.rmtree(snapshot_dir, ignore_errors=True)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        thread_id = resolve_thread_id(arguments.thread_id)
        source = locate_session_record(
            thread_id,
            resolve_codex_home(arguments.codex_home),
            arguments.source,
        )
        manifest = capture_session(thread_id, source, arguments.output_dir)
    except SessionReadError as error:
        print(
            json.dumps(
                {"error": {"code": error.code, "message": str(error)}},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
