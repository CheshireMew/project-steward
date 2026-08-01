#!/usr/bin/env python3
"""Archived inactive project-experience-store implementation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


PROJECT_SCHEMA_VERSION = 1
SHARED_SCHEMA_VERSION = 1
CONFIG_SCHEMA_VERSION = 1
EVENT_SCHEMA_VERSION = 1
PROJECT_KIND = "project-experience"
SHARED_KIND = "shared-experience"
CONFIG_KIND = "project-steward-config"
PROJECT_CATALOG_RELATIVE = Path(".project-steward/experience/catalog.json")
PROJECT_HISTORY_RELATIVE = Path(".project-steward/experience/history.jsonl")
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROJECT_STATUSES = {"candidate", "validated", "retired"}
SHARED_STAGES = {"candidate", "registered", "retired"}
ADOPTION_OUTCOMES = {"adopted", "adapted", "ruled-out"}
CLOSURE_DISPOSITIONS = {
    "discarded",
    "project-current",
    "shared-candidate",
    "shared-registered",
    "history-pointer",
}
SKILL_ROOT = Path(__file__).resolve().parent.parent


class ExperienceError(ValueError):
    """Raised when experience state violates the public contract."""


def fail(message: str) -> None:
    raise ExperienceError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value.strip()


def clean_string_list(
    value: object,
    label: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    cleaned: list[str] = []
    for index, item in enumerate(value):
        cleaned.append(clean_text(item, f"{label}[{index}]"))
    if not allow_empty and not cleaned:
        fail(f"{label} must contain at least one item")
    if len(set(cleaned)) != len(cleaned):
        fail(f"{label} contains duplicate items")
    return cleaned


def validate_id(value: object, label: str) -> str:
    identifier = clean_text(value, label)
    if not ID_PATTERN.fullmatch(identifier):
        fail(
            f"{label} must use lowercase letters, numbers, and single hyphens: "
            f"{identifier}"
        )
    return identifier


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    if slug and ID_PATTERN.fullmatch(slug):
        return slug
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"project-{digest}"


def canonical_hash(payload: dict[str, Any]) -> str:
    content = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def require_directory(path: Path, label: str) -> Path:
    root = path.expanduser().resolve()
    if not root.is_dir():
        fail(f"{label} directory not found: {root}")
    return root


def ensure_outside_skill(path: Path, label: str) -> None:
    resolved = path.expanduser().resolve(strict=False)
    try:
        resolved.relative_to(SKILL_ROOT)
    except ValueError:
        return
    fail(f"{label} must be outside the Project Steward skill source: {resolved}")


def ensure_within(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        fail(f"{label} escapes its storage root: {path}")
    return resolved


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"{label} not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid {label} JSON at {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{label} must be a JSON object: {path}")
    return payload


def read_json_lines(path: Path, label: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        fail(f"{label} must be a regular file: {path}")
    events: list[dict[str, Any]] = []
    for number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            fail(f"invalid {label} JSON at {path}:{number}: {exc}")
        if not isinstance(payload, dict):
            fail(f"{label} entry must be an object at {path}:{number}")
        events.append(payload)
    return events


def atomic_write_text(
    root: Path,
    target: Path,
    content: str,
    *,
    label: str,
) -> None:
    target = ensure_within(root, target, label)
    target.parent.mkdir(parents=True, exist_ok=True)
    ensure_within(root, target, label)
    temporary: Path | None = None
    try:
        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=target.parent,
            delete=False,
        ) as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            temporary = Path(stream.name)
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def atomic_write_json(
    root: Path,
    target: Path,
    payload: dict[str, Any],
    *,
    label: str,
) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    atomic_write_text(root, target, content, label=label)


def append_event(
    root: Path,
    target: Path,
    event: dict[str, Any],
    *,
    label: str,
) -> None:
    existing = ""
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    rendered = json.dumps(event, ensure_ascii=False, sort_keys=True)
    atomic_write_text(root, target, existing + rendered + "\n", label=label)


def project_catalog_path(root: Path) -> Path:
    return root / PROJECT_CATALOG_RELATIVE


def project_history_path(root: Path) -> Path:
    return root / PROJECT_HISTORY_RELATIVE


def shared_catalog_path(store: Path) -> Path:
    return store / "catalog.json"


def shared_history_path(store: Path) -> Path:
    return store / "history.jsonl"


def default_config_path() -> Path:
    explicit = os.environ.get("PROJECT_STEWARD_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "project-steward" / "config.json"
    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "project-steward"
            / "config.json"
        )
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "project-steward" / "config.json"


def config_path_from_args(args: argparse.Namespace) -> Path:
    value = getattr(args, "config", None)
    return (value if value is not None else default_config_path()).expanduser()


def validate_config(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    if payload.get("schema_version") != CONFIG_SCHEMA_VERSION:
        fail(
            f"unsupported config schema at {path}: "
            f"{payload.get('schema_version')!r}"
        )
    if payload.get("kind") != CONFIG_KIND:
        fail(f"invalid config kind at {path}: {payload.get('kind')!r}")
    store_value = clean_text(payload.get("experience_store"), "experience_store")
    store = Path(store_value).expanduser()
    if not store.is_absolute():
        fail(f"experience_store must be an absolute path in {path}")
    ensure_outside_skill(store, "experience store")
    return payload


def resolve_store(
    args: argparse.Namespace,
    *,
    required: bool,
) -> Path | None:
    explicit = getattr(args, "store", None)
    if explicit is not None:
        store = explicit.expanduser().resolve(strict=False)
        ensure_outside_skill(store, "experience store")
        return store

    environment = os.environ.get("PROJECT_STEWARD_EXPERIENCE_STORE")
    if environment:
        store = Path(environment).expanduser().resolve(strict=False)
        ensure_outside_skill(store, "experience store")
        return store

    config_path = config_path_from_args(args)
    if config_path.exists():
        config = validate_config(
            read_json(config_path, "Project Steward config"),
            config_path,
        )
        return Path(config["experience_store"]).expanduser().resolve(
            strict=False
        )

    if required:
        fail(
            "shared experience store is not configured; run "
            "`project_experience.py configure --store <path>` or pass --store"
        )
    return None


def validate_project_topic(
    root: Path,
    topic: dict[str, Any],
    *,
    index: int,
) -> dict[str, Any]:
    label = f"topics[{index}]"
    identifier = validate_id(topic.get("id"), f"{label}.id")
    clean_text(topic.get("title"), f"{label}.title")
    clean_text(topic.get("summary"), f"{label}.summary")
    clean_string_list(topic.get("applicability"), f"{label}.applicability")
    clean_string_list(topic.get("tags"), f"{label}.tags", allow_empty=True)
    clean_string_list(topic.get("evidence"), f"{label}.evidence")
    status = topic.get("status")
    if status not in PROJECT_STATUSES:
        fail(f"{label}.status must be one of {sorted(PROJECT_STATUSES)}")
    revision = topic.get("revision")
    if not isinstance(revision, int) or revision < 1:
        fail(f"{label}.revision must be a positive integer")
    clean_text(topic.get("created_at_utc"), f"{label}.created_at_utc")
    clean_text(topic.get("updated_at_utc"), f"{label}.updated_at_utc")
    expected_path = f"topics/{identifier}.md"
    if topic.get("body_path") != expected_path:
        fail(f"{label}.body_path must be {expected_path!r}")
    ensure_within(
        root / PROJECT_CATALOG_RELATIVE.parent,
        root / PROJECT_CATALOG_RELATIVE.parent / expected_path,
        f"{label}.body_path",
    )
    shared_id = topic.get("shared_note_id")
    if shared_id is not None:
        validate_id(shared_id, f"{label}.shared_note_id")
    return topic


def validate_project_catalog(
    root: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    path = project_catalog_path(root)
    if payload.get("schema_version") != PROJECT_SCHEMA_VERSION:
        fail(
            f"unsupported project experience schema at {path}: "
            f"{payload.get('schema_version')!r}"
        )
    if payload.get("kind") != PROJECT_KIND:
        fail(f"invalid project experience kind at {path}")
    validate_id(payload.get("project_id"), "project_id")
    clean_text(payload.get("project_name"), "project_name")
    topics = payload.get("topics")
    if not isinstance(topics, list):
        fail("topics must be a list")
    identifiers: set[str] = set()
    for index, raw_topic in enumerate(topics):
        if not isinstance(raw_topic, dict):
            fail(f"topics[{index}] must be an object")
        topic = validate_project_topic(root, raw_topic, index=index)
        identifier = topic["id"]
        if identifier in identifiers:
            fail(f"duplicate project topic id: {identifier}")
        identifiers.add(identifier)
    return payload


def validate_shared_source(
    source: dict[str, Any],
    *,
    label: str,
) -> None:
    validate_id(source.get("project_id"), f"{label}.project_id")
    clean_text(source.get("project_name"), f"{label}.project_name")
    validate_id(source.get("topic_id"), f"{label}.topic_id")
    revision = source.get("topic_revision")
    if not isinstance(revision, int) or revision < 1:
        fail(f"{label}.topic_revision must be a positive integer")
    clean_text(source.get("first_seen_at_utc"), f"{label}.first_seen_at_utc")
    clean_text(source.get("last_seen_at_utc"), f"{label}.last_seen_at_utc")


def validate_shared_validation(
    validation: dict[str, Any],
    *,
    label: str,
) -> None:
    clean_text(validation.get("event_id"), f"{label}.event_id")
    validate_id(validation.get("project_id"), f"{label}.project_id")
    clean_text(validation.get("project_name"), f"{label}.project_name")
    revision = validation.get("shared_revision")
    if not isinstance(revision, int) or revision < 1:
        fail(f"{label}.shared_revision must be a positive integer")
    if validation.get("outcome") not in ADOPTION_OUTCOMES:
        fail(f"{label}.outcome must be one of {sorted(ADOPTION_OUTCOMES)}")
    clean_text(validation.get("applied_to"), f"{label}.applied_to")
    clean_text(validation.get("decision"), f"{label}.decision")
    clean_text(validation.get("confirmed_by"), f"{label}.confirmed_by")
    clean_text(validation.get("recorded_at_utc"), f"{label}.recorded_at_utc")


def validate_shared_note(
    store: Path,
    note: dict[str, Any],
    *,
    index: int,
) -> dict[str, Any]:
    label = f"notes[{index}]"
    identifier = validate_id(note.get("id"), f"{label}.id")
    clean_text(note.get("title"), f"{label}.title")
    clean_text(note.get("summary"), f"{label}.summary")
    clean_string_list(note.get("applicability"), f"{label}.applicability")
    clean_string_list(note.get("tags"), f"{label}.tags", allow_empty=True)
    stage = note.get("stage")
    if stage not in SHARED_STAGES:
        fail(f"{label}.stage must be one of {sorted(SHARED_STAGES)}")
    revision = note.get("revision")
    if not isinstance(revision, int) or revision < 1:
        fail(f"{label}.revision must be a positive integer")
    clean_text(note.get("created_at_utc"), f"{label}.created_at_utc")
    clean_text(note.get("updated_at_utc"), f"{label}.updated_at_utc")
    expected_path = f"notes/{identifier}.md"
    if note.get("body_path") != expected_path:
        fail(f"{label}.body_path must be {expected_path!r}")
    ensure_within(store, store / expected_path, f"{label}.body_path")
    sources = note.get("sources")
    if not isinstance(sources, list) or not sources:
        fail(f"{label}.sources must contain at least one source")
    source_keys: set[tuple[str, str]] = set()
    for source_index, source in enumerate(sources):
        if not isinstance(source, dict):
            fail(f"{label}.sources[{source_index}] must be an object")
        validate_shared_source(
            source,
            label=f"{label}.sources[{source_index}]",
        )
        key = (source["project_id"], source["topic_id"])
        if key in source_keys:
            fail(f"{label}.sources contains duplicate project/topic: {key}")
        source_keys.add(key)
    validations = note.get("validations")
    if not isinstance(validations, list):
        fail(f"{label}.validations must be a list")
    event_ids: set[str] = set()
    for validation_index, validation in enumerate(validations):
        if not isinstance(validation, dict):
            fail(f"{label}.validations[{validation_index}] must be an object")
        validate_shared_validation(
            validation,
            label=f"{label}.validations[{validation_index}]",
        )
        event_id = validation["event_id"]
        if event_id in event_ids:
            fail(f"{label}.validations contains duplicate event: {event_id}")
        event_ids.add(event_id)
    return note


def validate_shared_catalog(
    store: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    path = shared_catalog_path(store)
    if payload.get("schema_version") != SHARED_SCHEMA_VERSION:
        fail(
            f"unsupported shared experience schema at {path}: "
            f"{payload.get('schema_version')!r}"
        )
    if payload.get("kind") != SHARED_KIND:
        fail(f"invalid shared experience kind at {path}")
    notes = payload.get("notes")
    if not isinstance(notes, list):
        fail("notes must be a list")
    identifiers: set[str] = set()
    for index, raw_note in enumerate(notes):
        if not isinstance(raw_note, dict):
            fail(f"notes[{index}] must be an object")
        note = validate_shared_note(store, raw_note, index=index)
        identifier = note["id"]
        if identifier in identifiers:
            fail(f"duplicate shared note id: {identifier}")
        identifiers.add(identifier)
    return payload


def load_project_catalog(
    root: Path,
    *,
    required: bool,
) -> dict[str, Any] | None:
    path = project_catalog_path(root)
    if not path.exists():
        if required:
            fail(
                f"project experience is not initialized: {path}; "
                "run the init command first"
            )
        return None
    if path.is_symlink() or not path.is_file():
        fail(f"project experience catalog must be a regular file: {path}")
    return validate_project_catalog(
        root,
        read_json(path, "project experience catalog"),
    )


def load_shared_catalog(
    store: Path,
    *,
    required: bool,
) -> dict[str, Any] | None:
    path = shared_catalog_path(store)
    if not path.exists():
        if required:
            fail(
                f"shared experience store is not initialized: {path}; "
                "run the configure command first"
            )
        return None
    if path.is_symlink() or not path.is_file():
        fail(f"shared experience catalog must be a regular file: {path}")
    return validate_shared_catalog(
        store,
        read_json(path, "shared experience catalog"),
    )


def topic_by_id(
    catalog: dict[str, Any],
    identifier: str,
) -> dict[str, Any] | None:
    return next(
        (topic for topic in catalog["topics"] if topic["id"] == identifier),
        None,
    )


def note_by_id(
    catalog: dict[str, Any],
    identifier: str,
) -> dict[str, Any] | None:
    return next(
        (note for note in catalog["notes"] if note["id"] == identifier),
        None,
    )


def read_body_file(path: Path, label: str) -> str:
    try:
        content = path.expanduser().read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"{label} not found: {path}")
    if not content.strip():
        fail(f"{label} must not be empty: {path}")
    return content.rstrip() + "\n"


def make_event(
    event_type: str,
    payload: dict[str, Any],
    *,
    event_id: str | None = None,
) -> dict[str, Any]:
    identity = event_id or canonical_hash(
        {
            "event_type": event_type,
            "recorded_at_utc": utc_now(),
            "payload": payload,
        }
    )[:20]
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_id": identity,
        "event_type": event_type,
        "recorded_at_utc": utc_now(),
        **payload,
    }


def configure_store(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    store = args.store.expanduser().resolve(strict=False)
    ensure_outside_skill(store, "experience store")
    config_path = config_path_from_args(args).resolve(strict=False)
    ensure_outside_skill(config_path, "Project Steward config")

    if config_path.exists():
        current = validate_config(
            read_json(config_path, "Project Steward config"),
            config_path,
        )
        current_store = Path(current["experience_store"]).resolve(
            strict=False
        )
        if current_store != store and not args.replace:
            fail(
                f"config already points to {current_store}; pass --replace "
                "after confirming the new shared store"
            )

    store.mkdir(parents=True, exist_ok=True)
    if store.is_symlink() or not store.is_dir():
        fail(f"experience store must be a regular directory: {store}")

    catalog_path = shared_catalog_path(store)
    if catalog_path.exists():
        catalog = load_shared_catalog(store, required=True)
        assert catalog is not None
        store_status = "existing"
    else:
        catalog = {
            "schema_version": SHARED_SCHEMA_VERSION,
            "kind": SHARED_KIND,
            "notes": [],
        }
        atomic_write_json(
            store,
            catalog_path,
            catalog,
            label="shared experience catalog",
        )
        store_status = "created"

    config_root = config_path.parent.resolve(strict=False)
    config_root.mkdir(parents=True, exist_ok=True)
    config_payload = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "kind": CONFIG_KIND,
        "experience_store": str(store),
    }
    atomic_write_json(
        config_root,
        config_path,
        config_payload,
        label="Project Steward config",
    )
    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "mode": "configure",
        "status": "configured",
        "config": str(config_path),
        "experience_store": str(store),
        "store_status": store_status,
        "registered_notes": len(catalog["notes"]),
    }, 0


def init_project(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    target = project_catalog_path(root)
    if target.exists():
        fail(f"project experience is already initialized: {target}")
    experience_root = root / PROJECT_CATALOG_RELATIVE.parent
    if experience_root.exists() and any(experience_root.iterdir()):
        fail(
            "project experience directory contains unindexed files; inspect "
            f"or migrate them before initialization: {experience_root}"
        )
    project_name = args.project_name or root.name
    project_id = args.project_id or slugify(project_name)
    validate_id(project_id, "project_id")
    now = utc_now()
    catalog = {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "kind": PROJECT_KIND,
        "project_id": project_id,
        "project_name": project_name,
        "created_at_utc": now,
        "updated_at_utc": now,
        "topics": [],
    }
    atomic_write_json(
        root,
        target,
        catalog,
        label="project experience catalog",
    )
    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "mode": "init",
        "status": "initialized",
        "project": str(root),
        "catalog": str(target),
        "project_id": project_id,
    }, 0


def inspect_state(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    project = load_project_catalog(root, required=False)
    store = resolve_store(args, required=False)
    shared: dict[str, Any] | None = None
    if store is not None:
        shared = load_shared_catalog(store, required=False)

    project_summary: dict[str, Any]
    if project is None:
        project_summary = {
            "status": "uninitialized",
            "catalog": str(project_catalog_path(root)),
        }
    else:
        project_summary = {
            "status": "ready",
            "catalog": str(project_catalog_path(root)),
            "project_id": project["project_id"],
            "project_name": project["project_name"],
            "topics": {
                status: sum(
                    1
                    for topic in project["topics"]
                    if topic["status"] == status
                )
                for status in sorted(PROJECT_STATUSES)
            },
        }

    if store is None:
        shared_summary = {"status": "not-configured"}
    elif shared is None:
        shared_summary = {
            "status": "uninitialized",
            "path": str(store),
        }
    else:
        shared_summary = {
            "status": "ready",
            "path": str(store),
            "notes": {
                stage: sum(
                    1 for note in shared["notes"] if note["stage"] == stage
                )
                for stage in sorted(SHARED_STAGES)
            },
        }

    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "mode": "inspect",
        "project": str(root),
        "project_experience": project_summary,
        "shared_experience": shared_summary,
    }, 0


def upsert_project_topic(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    catalog = load_project_catalog(root, required=True)
    assert catalog is not None
    identifier = validate_id(args.topic, "topic")
    body = read_body_file(args.body_file, "topic body")
    existing = topic_by_id(catalog, identifier)
    now = utc_now()

    if existing is None:
        if args.expected_revision is not None:
            fail("expected_revision is only valid when updating an existing topic")
        revision = 1
        created_at = now
        action = "project-topic-created"
        shared_note_id = None
    else:
        if args.expected_revision is None:
            fail(
                "updating an existing topic requires --expected-revision "
                f"{existing['revision']}"
            )
        if args.expected_revision != existing["revision"]:
            fail(
                f"topic revision changed: expected {args.expected_revision}, "
                f"found {existing['revision']}"
            )
        revision = existing["revision"] + 1
        created_at = existing["created_at_utc"]
        action = "project-topic-updated"
        shared_note_id = existing.get("shared_note_id")

    topic: dict[str, Any] = {
        "id": identifier,
        "title": clean_text(args.title, "title"),
        "summary": clean_text(args.summary, "summary"),
        "applicability": clean_string_list(
            args.applicability,
            "applicability",
        ),
        "tags": clean_string_list(args.tag, "tags", allow_empty=True),
        "status": args.status,
        "evidence": clean_string_list(args.evidence, "evidence"),
        "body_path": f"topics/{identifier}.md",
        "revision": revision,
        "created_at_utc": created_at,
        "updated_at_utc": now,
    }
    if shared_note_id is not None:
        topic["shared_note_id"] = shared_note_id

    event = make_event(
        action,
        {
            "project_id": catalog["project_id"],
            "topic_id": identifier,
            "topic_revision": revision,
            "status": args.status,
            "change_note": clean_text(args.change_note, "change_note"),
            "evidence": topic["evidence"],
        },
    )
    append_event(
        root,
        project_history_path(root),
        event,
        label="project experience history",
    )

    if existing is None:
        catalog["topics"].append(topic)
    else:
        index = catalog["topics"].index(existing)
        catalog["topics"][index] = topic
    catalog["topics"].sort(key=lambda item: item["id"])
    catalog["updated_at_utc"] = now

    body_path = (
        root / PROJECT_CATALOG_RELATIVE.parent / topic["body_path"]
    )
    atomic_write_text(root, body_path, body, label="project topic body")
    atomic_write_json(
        root,
        project_catalog_path(root),
        catalog,
        label="project experience catalog",
    )
    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "mode": "upsert",
        "status": "created" if existing is None else "updated",
        "project": str(root),
        "topic": {
            "id": identifier,
            "revision": revision,
            "status": args.status,
            "body": str(body_path),
        },
        "history_event": event["event_id"],
    }, 0


def promote_topic(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    project = load_project_catalog(root, required=True)
    assert project is not None
    topic_id = validate_id(args.topic, "topic")
    topic = topic_by_id(project, topic_id)
    if topic is None:
        fail(f"project topic not found: {topic_id}")
    if args.stage != "retired" and topic["status"] != "validated":
        fail(
            "only a validated project topic can enter the shared store; "
            f"{topic_id} is {topic['status']}"
        )

    store = resolve_store(args, required=True)
    assert store is not None
    shared = load_shared_catalog(store, required=True)
    assert shared is not None
    shared_id = validate_id(args.shared_id, "shared_id")
    existing = note_by_id(shared, shared_id)
    linked_id = topic.get("shared_note_id")
    if linked_id is not None and linked_id != shared_id:
        fail(
            f"project topic {topic_id} already promotes to {linked_id}; "
            "update that shared note instead of creating a second latest version"
        )

    now = utc_now()
    if existing is None:
        if args.stage == "retired":
            fail("a new shared note cannot start in the retired stage")
        if args.expected_revision is not None:
            fail(
                "expected_revision is only valid when updating an existing "
                "shared note"
            )
        revision = 1
        created_at = now
        sources: list[dict[str, Any]] = []
        validations: list[dict[str, Any]] = []
        action = "shared-note-created"
    else:
        if args.expected_revision is None:
            fail(
                "updating an existing shared note requires --expected-revision "
                f"{existing['revision']}"
            )
        if args.expected_revision != existing["revision"]:
            fail(
                f"shared note revision changed: expected "
                f"{args.expected_revision}, found {existing['revision']}"
            )
        revision = existing["revision"] + 1
        created_at = existing["created_at_utc"]
        sources = [dict(source) for source in existing["sources"]]
        validations = [dict(item) for item in existing["validations"]]
        action = "shared-note-updated"

    source = next(
        (
            item
            for item in sources
            if item["project_id"] == project["project_id"]
            and item["topic_id"] == topic_id
        ),
        None,
    )
    if source is None:
        sources.append(
            {
                "project_id": project["project_id"],
                "project_name": project["project_name"],
                "topic_id": topic_id,
                "topic_revision": topic["revision"],
                "first_seen_at_utc": now,
                "last_seen_at_utc": now,
            }
        )
    else:
        source["project_name"] = project["project_name"]
        source["topic_revision"] = topic["revision"]
        source["last_seen_at_utc"] = now
    sources.sort(key=lambda item: (item["project_id"], item["topic_id"]))

    note = {
        "id": shared_id,
        "title": clean_text(args.title, "title"),
        "summary": clean_text(args.summary, "summary"),
        "applicability": clean_string_list(
            args.applicability,
            "applicability",
        ),
        "tags": clean_string_list(args.tag, "tags", allow_empty=True),
        "stage": args.stage,
        "body_path": f"notes/{shared_id}.md",
        "revision": revision,
        "created_at_utc": created_at,
        "updated_at_utc": now,
        "sources": sources,
        "validations": validations,
    }
    body = read_body_file(args.body_file, "shared note body")
    event = make_event(
        action,
        {
            "shared_id": shared_id,
            "shared_revision": revision,
            "stage": args.stage,
            "source_project_id": project["project_id"],
            "source_topic_id": topic_id,
            "source_topic_revision": topic["revision"],
            "confirmed_by": clean_text(args.confirmed_by, "confirmed_by"),
            "change_note": clean_text(args.change_note, "change_note"),
        },
    )
    append_event(
        store,
        shared_history_path(store),
        event,
        label="shared experience history",
    )

    if existing is None:
        shared["notes"].append(note)
    else:
        index = shared["notes"].index(existing)
        shared["notes"][index] = note
    shared["notes"].sort(key=lambda item: item["id"])
    shared_body_path = store / note["body_path"]
    atomic_write_text(
        store,
        shared_body_path,
        body,
        label="shared experience body",
    )
    atomic_write_json(
        store,
        shared_catalog_path(store),
        shared,
        label="shared experience catalog",
    )

    topic["shared_note_id"] = shared_id
    topic["updated_at_utc"] = now
    project["updated_at_utc"] = now
    project_event = make_event(
        "project-topic-promoted",
        {
            "project_id": project["project_id"],
            "topic_id": topic_id,
            "topic_revision": topic["revision"],
            "shared_id": shared_id,
            "shared_revision": revision,
            "stage": args.stage,
            "confirmed_by": args.confirmed_by.strip(),
        },
    )
    append_event(
        root,
        project_history_path(root),
        project_event,
        label="project experience history",
    )
    atomic_write_json(
        root,
        project_catalog_path(root),
        project,
        label="project experience catalog",
    )

    return {
        "schema_version": SHARED_SCHEMA_VERSION,
        "mode": "promote",
        "status": "created" if existing is None else "updated",
        "project": str(root),
        "experience_store": str(store),
        "shared_note": {
            "id": shared_id,
            "revision": revision,
            "stage": args.stage,
            "body": str(shared_body_path),
            "source": {
                "project_id": project["project_id"],
                "topic_id": topic_id,
                "topic_revision": topic["revision"],
            },
        },
        "history_event": event["event_id"],
    }, 0


def search_terms(value: str) -> set[str]:
    normalized = value.casefold()
    terms = set(re.findall(r"[a-z0-9][a-z0-9_-]*", normalized))
    for sequence in re.findall(r"[\u3400-\u9fff]+", normalized):
        if len(sequence) == 1:
            terms.add(sequence)
        else:
            terms.update(sequence[index : index + 2] for index in range(len(sequence) - 1))
            if len(sequence) <= 8:
                terms.add(sequence)
    return {term for term in terms if term}


def score_record(query: str, record: dict[str, Any], body: str) -> tuple[int, list[str]]:
    query_folded = query.casefold().strip()
    query_tokens = search_terms(query)
    fields: list[tuple[str, str, int]] = [
        ("id", record["id"], 10),
        ("title", record["title"], 8),
        ("summary", record["summary"], 5),
        ("applicability", " ".join(record["applicability"]), 5),
        ("tags", " ".join(record["tags"]), 4),
        ("body", body, 1),
    ]
    score = 0
    matched: list[str] = []
    for name, value, weight in fields:
        folded = value.casefold()
        tokens = search_terms(value)
        overlap = query_tokens & tokens
        field_score = len(overlap) * weight
        if query_folded and query_folded in folded:
            field_score += weight * 4
        if field_score:
            score += field_score
            matched.append(name)
    return score, matched


def search_experience(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    query = clean_text(args.query, "query")
    project = load_project_catalog(root, required=False)
    store = resolve_store(args, required=False)
    shared = (
        load_shared_catalog(store, required=True)
        if store is not None
        else None
    )
    candidates: list[dict[str, Any]] = []

    if project is not None:
        project_state_root = root / PROJECT_CATALOG_RELATIVE.parent
        for topic in project["topics"]:
            if topic["status"] == "retired":
                continue
            body_path = ensure_within(
                project_state_root,
                project_state_root / topic["body_path"],
                "project topic body",
            )
            body = read_body_file(body_path, "project topic body")
            score, matched = score_record(query, topic, body)
            if score:
                candidates.append(
                    {
                        "source": "project",
                        "id": topic["id"],
                        "revision": topic["revision"],
                        "state": topic["status"],
                        "title": topic["title"],
                        "summary": topic["summary"],
                        "applicability": topic["applicability"],
                        "tags": topic["tags"],
                        "score": score + 2,
                        "matched_fields": matched,
                        "path": str(body_path),
                        "body": body,
                    }
                )

    if shared is not None and store is not None:
        allowed_stages = {"registered"}
        if args.include_candidates:
            allowed_stages.add("candidate")
        for note in shared["notes"]:
            if note["stage"] not in allowed_stages:
                continue
            body_path = ensure_within(
                store,
                store / note["body_path"],
                "shared experience body",
            )
            body = read_body_file(body_path, "shared experience body")
            score, matched = score_record(query, note, body)
            if score:
                candidates.append(
                    {
                        "source": "shared",
                        "id": note["id"],
                        "revision": note["revision"],
                        "state": note["stage"],
                        "title": note["title"],
                        "summary": note["summary"],
                        "applicability": note["applicability"],
                        "tags": note["tags"],
                        "score": score,
                        "matched_fields": matched,
                        "path": str(body_path),
                        "body": body,
                        "source_count": len(note["sources"]),
                        "validation_count": len(note["validations"]),
                    }
                )

    candidates.sort(
        key=lambda item: (
            -item["score"],
            0 if item["source"] == "project" else 1,
            item["id"],
        )
    )
    results = candidates[: args.limit]
    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "mode": "search",
        "project": str(root),
        "query": query,
        "shared_store": (
            {"status": "not-configured"}
            if store is None
            else {"status": "ready", "path": str(store)}
        ),
        "selection_rule": (
            "keyword retrieval only; read each returned body and judge whether "
            "its mechanism, conditions, decision point, and expected result "
            "match the current change"
        ),
        "result_count": len(results),
        "results": results,
    }, 0


def adopt_shared_note(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    project = load_project_catalog(root, required=True)
    assert project is not None
    store = resolve_store(args, required=True)
    assert store is not None
    shared = load_shared_catalog(store, required=True)
    assert shared is not None
    shared_id = validate_id(args.shared_id, "shared_id")
    note = note_by_id(shared, shared_id)
    if note is None:
        fail(f"shared experience not found: {shared_id}")
    if note["stage"] != "registered":
        fail(
            f"only registered shared experience can be adopted; "
            f"{shared_id} is {note['stage']}"
        )
    if args.expected_revision != note["revision"]:
        fail(
            f"shared note revision changed: expected {args.expected_revision}, "
            f"found {note['revision']}"
        )

    identity_payload = {
        "project_id": project["project_id"],
        "shared_id": shared_id,
        "shared_revision": note["revision"],
        "outcome": args.outcome,
        "applied_to": clean_text(args.applied_to, "applied_to"),
        "decision": clean_text(args.decision, "decision"),
    }
    event_id = canonical_hash(identity_payload)[:20]
    if any(
        validation["event_id"] == event_id
        for validation in note["validations"]
    ):
        fail(
            "this project already recorded the same adoption decision for "
            f"{shared_id}: {event_id}"
        )
    validation = {
        "event_id": event_id,
        "project_id": project["project_id"],
        "project_name": project["project_name"],
        "shared_revision": note["revision"],
        "outcome": args.outcome,
        "applied_to": args.applied_to.strip(),
        "decision": args.decision.strip(),
        "confirmed_by": clean_text(args.confirmed_by, "confirmed_by"),
        "recorded_at_utc": utc_now(),
    }
    note["validations"].append(validation)
    note["validations"].sort(
        key=lambda item: (item["recorded_at_utc"], item["event_id"])
    )
    note["updated_at_utc"] = utc_now()

    shared_event = make_event(
        "shared-note-adopted",
        {
            "shared_id": shared_id,
            **validation,
        },
        event_id=event_id,
    )
    project_event = make_event(
        "shared-note-adopted",
        {
            "project_id": project["project_id"],
            "shared_id": shared_id,
            "shared_revision": note["revision"],
            "outcome": args.outcome,
            "applied_to": args.applied_to.strip(),
            "decision": args.decision.strip(),
            "confirmed_by": args.confirmed_by.strip(),
        },
        event_id=event_id,
    )
    append_event(
        store,
        shared_history_path(store),
        shared_event,
        label="shared experience history",
    )
    append_event(
        root,
        project_history_path(root),
        project_event,
        label="project experience history",
    )
    atomic_write_json(
        store,
        shared_catalog_path(store),
        shared,
        label="shared experience catalog",
    )
    return {
        "schema_version": SHARED_SCHEMA_VERSION,
        "mode": "adopt",
        "status": "recorded",
        "project": str(root),
        "shared_note": {
            "id": shared_id,
            "revision": note["revision"],
        },
        "outcome": args.outcome,
        "applied_to": args.applied_to.strip(),
        "decision": args.decision.strip(),
        "event_id": event_id,
    }, 0


def validate_closure_plan(
    plan: dict[str, Any],
    *,
    project: dict[str, Any],
    shared: dict[str, Any] | None,
) -> dict[str, Any]:
    clean_text(plan.get("summary"), "closure plan summary")
    items = plan.get("items")
    if not isinstance(items, list) or not items:
        fail("closure plan items must contain at least one item")
    for index, item in enumerate(items):
        label = f"closure plan items[{index}]"
        if not isinstance(item, dict):
            fail(f"{label} must be an object")
        clean_text(item.get("label"), f"{label}.label")
        disposition = item.get("disposition")
        if disposition not in CLOSURE_DISPOSITIONS:
            fail(
                f"{label}.disposition must be one of "
                f"{sorted(CLOSURE_DISPOSITIONS)}"
            )
        clean_text(item.get("reason"), f"{label}.reason")
        target_id = item.get("target_id")
        pointer = item.get("pointer")
        if disposition == "project-current":
            identifier = validate_id(target_id, f"{label}.target_id")
            topic = topic_by_id(project, identifier)
            if topic is None or topic["status"] == "retired":
                fail(
                    f"{label} points to a missing or retired project topic: "
                    f"{identifier}"
                )
        elif disposition in {"shared-candidate", "shared-registered"}:
            identifier = validate_id(target_id, f"{label}.target_id")
            if shared is None:
                fail(
                    f"{label} requires a configured shared experience store"
                )
            note = note_by_id(shared, identifier)
            expected = disposition.removeprefix("shared-")
            if note is None or note["stage"] != expected:
                fail(
                    f"{label} requires shared note {identifier} in stage "
                    f"{expected}"
                )
        elif disposition == "history-pointer":
            clean_text(pointer, f"{label}.pointer")
    return plan


def close_branch(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    project = load_project_catalog(root, required=True)
    assert project is not None
    plan = read_json(args.plan_file.expanduser(), "branch closure plan")
    needs_shared = any(
        isinstance(item, dict)
        and item.get("disposition")
        in {"shared-candidate", "shared-registered"}
        for item in plan.get("items", [])
    )
    store = resolve_store(args, required=needs_shared)
    shared = (
        load_shared_catalog(store, required=True)
        if store is not None
        else None
    )
    validate_closure_plan(plan, project=project, shared=shared)
    work_id = clean_text(args.work_id, "work_id")
    identity_payload = {
        "project_id": project["project_id"],
        "work_id": work_id,
        "plan": plan,
    }
    event_id = canonical_hash(identity_payload)[:20]
    existing_events = read_json_lines(
        project_history_path(root),
        "project experience history",
    )
    if any(event.get("event_id") == event_id for event in existing_events):
        fail(f"this branch closure is already recorded: {event_id}")
    event = make_event(
        "branch-closed",
        {
            "project_id": project["project_id"],
            "work_id": work_id,
            "confirmed_by": clean_text(args.confirmed_by, "confirmed_by"),
            "summary": plan["summary"].strip(),
            "items": plan["items"],
        },
        event_id=event_id,
    )
    append_event(
        root,
        project_history_path(root),
        event,
        label="project experience history",
    )
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "mode": "close-branch",
        "status": "recorded",
        "project": str(root),
        "work_id": work_id,
        "event_id": event_id,
        "dispositions": {
            disposition: sum(
                1
                for item in plan["items"]
                if item["disposition"] == disposition
            )
            for disposition in sorted(CLOSURE_DISPOSITIONS)
        },
    }, 0


def validate_history_events(
    events: list[dict[str, Any]],
    *,
    label: str,
) -> list[str]:
    errors: list[str] = []
    event_ids: set[str] = set()
    for index, event in enumerate(events):
        prefix = f"{label}[{index}]"
        if event.get("schema_version") != EVENT_SCHEMA_VERSION:
            errors.append(f"{prefix} has unsupported schema")
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            errors.append(f"{prefix} has no event_id")
        elif event_id in event_ids:
            errors.append(f"{prefix} duplicates event_id {event_id}")
        else:
            event_ids.add(event_id)
        if not isinstance(event.get("event_type"), str):
            errors.append(f"{prefix} has no event_type")
        if not isinstance(event.get("recorded_at_utc"), str):
            errors.append(f"{prefix} has no recorded_at_utc")
    return errors


def verify_state(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    errors: list[str] = []
    checks: list[str] = []
    try:
        project = load_project_catalog(root, required=True)
        assert project is not None
        checks.append("project catalog parsed")
    except ExperienceError as exc:
        return {
            "schema_version": PROJECT_SCHEMA_VERSION,
            "mode": "verify",
            "status": "failed",
            "project": str(root),
            "checks": checks,
            "errors": [str(exc)],
        }, 1

    project_state_root = root / PROJECT_CATALOG_RELATIVE.parent
    for topic in project["topics"]:
        body_path = ensure_within(
            project_state_root,
            project_state_root / topic["body_path"],
            "project topic body",
        )
        if not body_path.is_file() or body_path.is_symlink():
            errors.append(f"project topic body is missing: {body_path}")
        elif not body_path.read_text(encoding="utf-8").strip():
            errors.append(f"project topic body is empty: {body_path}")
    if not errors:
        checks.append("project topic bodies resolved")

    project_events = read_json_lines(
        project_history_path(root),
        "project experience history",
    )
    errors.extend(
        validate_history_events(
            project_events,
            label="project history",
        )
    )
    checks.append("project history parsed")

    store = resolve_store(args, required=False)
    shared: dict[str, Any] | None = None
    if store is not None:
        try:
            shared = load_shared_catalog(store, required=True)
            assert shared is not None
            checks.append("shared catalog parsed")
            for note in shared["notes"]:
                body_path = ensure_within(
                    store,
                    store / note["body_path"],
                    "shared experience body",
                )
                if not body_path.is_file() or body_path.is_symlink():
                    errors.append(
                        f"shared experience body is missing: {body_path}"
                    )
                elif not body_path.read_text(encoding="utf-8").strip():
                    errors.append(
                        f"shared experience body is empty: {body_path}"
                    )
            shared_events = read_json_lines(
                shared_history_path(store),
                "shared experience history",
            )
            errors.extend(
                validate_history_events(
                    shared_events,
                    label="shared history",
                )
            )
            checks.append("shared bodies and history parsed")
        except ExperienceError as exc:
            errors.append(str(exc))

    promoted_topics = [
        topic for topic in project["topics"] if topic.get("shared_note_id")
    ]
    if promoted_topics and shared is None:
        errors.append(
            "project topics point to shared experience but no shared store "
            "is configured"
        )
    elif shared is not None:
        for topic in promoted_topics:
            note = note_by_id(shared, topic["shared_note_id"])
            if note is None:
                errors.append(
                    f"project topic {topic['id']} points to missing shared "
                    f"note {topic['shared_note_id']}"
                )
                continue
            source_exists = any(
                source["project_id"] == project["project_id"]
                and source["topic_id"] == topic["id"]
                for source in note["sources"]
            )
            if not source_exists:
                errors.append(
                    f"shared note {note['id']} has no provenance for project "
                    f"topic {topic['id']}"
                )
        shared_validation_ids = {
            validation["event_id"]
            for note in shared["notes"]
            for validation in note["validations"]
        }
        project_adoption_ids = {
            event["event_id"]
            for event in project_events
            if event.get("event_type") == "shared-note-adopted"
        }
        missing = sorted(project_adoption_ids - shared_validation_ids)
        if missing:
            errors.append(
                "project adoption events missing from shared validations: "
                + ", ".join(missing)
            )
        checks.append("promotion and adoption links resolved")

    status = "passed" if not errors else "failed"
    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "mode": "verify",
        "status": status,
        "project": str(root),
        "experience_store": str(store) if store is not None else None,
        "checks": checks,
        "errors": errors,
        "counts": {
            "project_topics": len(project["topics"]),
            "project_events": len(project_events),
            "shared_notes": len(shared["notes"]) if shared else 0,
        },
    }, 0 if status == "passed" else 1


def upgrade_state(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = require_directory(args.project, "project")
    project = load_project_catalog(root, required=False)
    store = resolve_store(args, required=False)
    shared = (
        load_shared_catalog(store, required=False)
        if store is not None
        else None
    )
    state = {
        "project": (
            "uninitialized"
            if project is None
            else f"schema-{project['schema_version']}"
        ),
        "shared": (
            "not-configured"
            if store is None
            else (
                "uninitialized"
                if shared is None
                else f"schema-{shared['schema_version']}"
            )
        ),
    }
    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "mode": "upgrade",
        "status": "current",
        "write_requested": args.write,
        "project": str(root),
        "experience_store": str(store) if store is not None else None,
        "state": state,
        "changes": [],
        "message": (
            "all initialized experience state already uses the current schema; "
            "no files were changed"
        ),
    }, 0


def add_config_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=Path,
        help=(
            "User config path. Defaults to PROJECT_STEWARD_CONFIG or the "
            "platform config directory."
        ),
    )


def add_store_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--store",
        type=Path,
        help=(
            "Shared experience store. Overrides "
            "PROJECT_STEWARD_EXPERIENCE_STORE and user config."
        ),
    )
    add_config_option(parser)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    configure = subparsers.add_parser(
        "configure",
        help="Configure and initialize the user-selected shared store",
    )
    configure.add_argument("--store", type=Path, required=True)
    configure.add_argument(
        "--replace",
        action="store_true",
        help="Replace an existing config that points to another store.",
    )
    add_config_option(configure)

    init = subparsers.add_parser(
        "init",
        help="Initialize project-local experience without empty topic files",
    )
    init.add_argument("project", type=Path)
    init.add_argument("--project-id")
    init.add_argument("--project-name")

    inspect = subparsers.add_parser(
        "inspect",
        help="Inspect project and shared experience without writing",
    )
    inspect.add_argument("project", type=Path)
    add_store_options(inspect)

    upsert = subparsers.add_parser(
        "upsert",
        help="Create or replace the current conclusion for one project topic",
    )
    upsert.add_argument("project", type=Path)
    upsert.add_argument("--topic", required=True)
    upsert.add_argument("--title", required=True)
    upsert.add_argument("--summary", required=True)
    upsert.add_argument("--applicability", action="append", required=True)
    upsert.add_argument("--tag", action="append", default=[])
    upsert.add_argument(
        "--status",
        choices=sorted(PROJECT_STATUSES),
        required=True,
    )
    upsert.add_argument("--evidence", action="append", required=True)
    upsert.add_argument("--body-file", type=Path, required=True)
    upsert.add_argument("--change-note", required=True)
    upsert.add_argument("--expected-revision", type=int)

    promote = subparsers.add_parser(
        "promote",
        help="Create or update one cross-project experience from a project topic",
    )
    promote.add_argument("project", type=Path)
    promote.add_argument("--topic", required=True)
    promote.add_argument("--shared-id", required=True)
    promote.add_argument("--title", required=True)
    promote.add_argument("--summary", required=True)
    promote.add_argument("--applicability", action="append", required=True)
    promote.add_argument("--tag", action="append", default=[])
    promote.add_argument(
        "--stage",
        choices=sorted(SHARED_STAGES),
        required=True,
    )
    promote.add_argument("--body-file", type=Path, required=True)
    promote.add_argument("--confirmed-by", required=True)
    promote.add_argument("--change-note", required=True)
    promote.add_argument("--expected-revision", type=int)
    add_store_options(promote)

    search = subparsers.add_parser(
        "search",
        help="Retrieve relevant project and registered shared experience",
    )
    search.add_argument("project", type=Path)
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=8)
    search.add_argument("--include-candidates", action="store_true")
    add_store_options(search)

    adopt = subparsers.add_parser(
        "adopt",
        help="Record how registered shared experience changed a project decision",
    )
    adopt.add_argument("project", type=Path)
    adopt.add_argument("--shared-id", required=True)
    adopt.add_argument("--expected-revision", type=int, required=True)
    adopt.add_argument(
        "--outcome",
        choices=sorted(ADOPTION_OUTCOMES),
        required=True,
    )
    adopt.add_argument("--applied-to", required=True)
    adopt.add_argument("--decision", required=True)
    adopt.add_argument("--confirmed-by", required=True)
    add_store_options(adopt)

    close = subparsers.add_parser(
        "close-branch",
        help="Record a validated branch or exploration closure plan",
    )
    close.add_argument("project", type=Path)
    close.add_argument("--work-id", required=True)
    close.add_argument("--plan-file", type=Path, required=True)
    close.add_argument("--confirmed-by", required=True)
    add_store_options(close)

    verify = subparsers.add_parser(
        "verify",
        help="Verify bodies, histories, provenance, and adoption links",
    )
    verify.add_argument("project", type=Path)
    add_store_options(verify)

    upgrade = subparsers.add_parser(
        "upgrade",
        help="Plan or apply registered experience-schema migrations",
    )
    upgrade.add_argument("project", type=Path)
    upgrade.add_argument("--write", action="store_true")
    add_store_options(upgrade)

    return parser.parse_args()


def output_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def run_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    commands = {
        "configure": configure_store,
        "init": init_project,
        "inspect": inspect_state,
        "upsert": upsert_project_topic,
        "promote": promote_topic,
        "search": search_experience,
        "adopt": adopt_shared_note,
        "close-branch": close_branch,
        "verify": verify_state,
        "upgrade": upgrade_state,
    }
    return commands[args.command](args)


def main() -> int:
    args = parse_args()
    if hasattr(args, "limit") and args.limit < 1:
        print("ERROR: limit must be at least 1", file=sys.stderr)
        return 2
    try:
        payload, exit_code = run_command(args)
        output_json(payload)
        return exit_code
    except (ExperienceError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
