"""License catalog, source rendering, and plan data structures."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PLAN_VERSION = 2
YEAR_PATTERN = re.compile(r"^\d{4}(?:-\d{4})?$")
PLACEHOLDER_PATTERN = re.compile(r"\{\{([a-z_]+)\}\}")
HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
GIT_HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{40,64}$")
REPOSITORY_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


@dataclass(frozen=True)
class RenderedSource:
    source_id: str
    source_name: str
    source_url: str | None
    source_sha256: str | None
    content: bytes


@dataclass(frozen=True)
class PlannedAction:
    path: str
    action: str
    rendered: RenderedSource
    expected_sha256: str | None
    preserve_as: str | None


@dataclass
class PreparedProject:
    project_id: str
    disposition: str
    reason: str
    target_kind: str
    target_label: str
    root: Path | None
    repository: str | None
    branch: str | None
    base_head: str | None
    base_tree: str | None
    expected_result_head: str | None
    commit_message: str | None
    actions: list[PlannedAction]
    existing: dict[str, bytes]
def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path, label: str) -> dict:
    try:
        text = sys.stdin.read() if label == "plan" and str(path) == "-" else path.read_text(
            encoding="utf-8"
        )
        data = json.loads(text)
    except FileNotFoundError:
        fail(f"{label} not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid {label} JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{label} must be a JSON object")
    return data


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def resolve_governance_path(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        fail("every file action needs a non-empty relative path")
    normalized = value.strip().replace("\\", "/")
    candidate = Path(normalized)
    if candidate.is_absolute() or normalized.startswith("/"):
        fail(f"governance path must be repository-relative: {value}")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        fail(f"invalid governance path: {value}")

    basename = parts[-1].upper()
    allowed_prefixes = (
        "LICENSE",
        "LICENCE",
        "LICENSING",
        "COPYING",
        "NOTICE",
        "COPYRIGHT",
        "THIRD_PARTY",
        "THIRD-PARTY",
        "ASSET-LICENSE",
    )
    inside_license_directory = any(
        part.casefold() in {"license", "licenses", "licence", "licences"}
        for part in parts[:-1]
    )
    allowed_suffix = Path(parts[-1]).suffix.casefold() in {"", ".md", ".rst", ".txt"}
    if not basename.startswith(allowed_prefixes) and not (
        inside_license_directory and allowed_suffix
    ):
        fail(
            f"path is outside the license-governance boundary: {normalized}"
        )
    return "/".join(parts)


def resolve_local_file(root: Path, relative: str) -> Path:
    candidate = root.joinpath(*relative.split("/"))
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"local governance path escapes repository through a symlink: {relative}")
    return resolved


def validate_common_fields(plan: dict) -> dict[str, str]:
    year = plan.get("year")
    holder = plan.get("copyright_holder")
    project_name = plan.get("project_name")

    if not isinstance(year, str) or not YEAR_PATTERN.fullmatch(year.strip()):
        fail("year must use YYYY or YYYY-YYYY")
    if (
        not isinstance(holder, str)
        or not holder.strip()
        or "\n" in holder
        or "\r" in holder
    ):
        fail("copyright_holder must be one non-empty line")
    if (
        not isinstance(project_name, str)
        or not project_name.strip()
        or "\n" in project_name
        or "\r" in project_name
    ):
        fail("project_name must be one non-empty line")

    return {
        "year": year.strip(),
        "copyright_holder": holder.strip(),
        "project_name": project_name.strip(),
    }


def load_template(catalog_root: Path, entry: dict) -> tuple[str, str]:
    text_path = entry.get("text_path")
    expected_hash = entry.get("sha256")
    if not isinstance(text_path, str) or not text_path:
        fail("catalog entry is missing text_path")
    if not isinstance(expected_hash, str) or not re.fullmatch(
        r"[0-9a-fA-F]{64}", expected_hash
    ):
        fail(f"catalog entry has invalid sha256: {text_path}")

    path = (catalog_root / text_path).resolve()
    try:
        path.relative_to(catalog_root)
    except ValueError:
        fail(f"catalog text_path escapes catalog directory: {text_path}")
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"catalog text file not found: {path}")
    actual_hash = sha256_text(text)
    if actual_hash.lower() != expected_hash.lower():
        fail(
            f"catalog integrity check failed for {text_path}: "
            f"expected {expected_hash.lower()}, got {actual_hash}"
        )
    return text, actual_hash


def render_template(
    text: str,
    required_fields: object,
    values: dict[str, str],
    extra_values: dict[str, str] | None = None,
) -> str:
    if not isinstance(required_fields, list) or not all(
        isinstance(field, str) for field in required_fields
    ):
        fail("catalog template_fields must be a list of strings")
    render_values = dict(values)
    if extra_values:
        render_values.update(extra_values)
    for field in required_fields:
        if not render_values.get(field):
            fail(f"plan is missing required template field: {field}")
    result = text
    for field in required_fields:
        result = result.replace("{{" + field + "}}", render_values[field])
    unresolved = sorted(set(PLACEHOLDER_PATTERN.findall(result)))
    if unresolved:
        fail(f"unresolved template fields: {', '.join(unresolved)}")
    return result


def gnu_notice(
    license_id: str,
    license_name: str,
    mode: str,
    values: dict[str, str],
    license_path: str,
) -> str:
    for field in ("project_name", "year", "copyright_holder"):
        if not values[field]:
            fail(f"{license_id} notice requires {field}")
    if mode not in {"only", "or-later"}:
        fail(f"invalid GNU notice mode for {license_id}: {mode}")

    family = (
        "GNU Affero General Public License"
        if license_id.startswith("AGPL")
        else "GNU General Public License"
    )
    version = (
        "version 3 of the License"
        if mode == "only"
        else "either version 3 of the License, or (at your option) any later version"
    )
    return (
        f"# License notice for {values['project_name']}\n\n"
        f"Copyright (c) {values['year']} {values['copyright_holder']}\n\n"
        f"{values['project_name']} is free software: you can redistribute it "
        f"and/or modify it under the terms of the {family} as published by the "
        f"Free Software Foundation, {version}.\n\n"
        f"{values['project_name']} is distributed in the hope that it will be "
        "useful, but WITHOUT ANY WARRANTY; without even the implied warranty "
        "of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
        f"{family} for more details.\n\n"
        f"SPDX license expression: `{license_id}`  \n"
        f"Full license text: `{license_path}`  \n"
        f"License name: {license_name}\n"
    )


def load_catalog(catalog_path: Path) -> dict:
    catalog = read_json(catalog_path, "catalog")
    if catalog.get("schema_version") != 1:
        fail("unsupported catalog schema_version")
    if not isinstance(catalog.get("licenses"), dict) or not isinstance(
        catalog.get("notices"), dict
    ):
        fail("catalog must contain licenses and notices objects")
    return catalog


def render_source(
    source: object,
    values: dict[str, str],
    catalog: dict,
    catalog_path: Path,
) -> RenderedSource:
    if not isinstance(source, dict):
        fail("every file action needs a source object")
    kind = source.get("kind")
    if not isinstance(kind, str):
        fail("source.kind must be a string")

    if kind == "text":
        content = source.get("content")
        if not isinstance(content, str) or not content:
            fail("text source content must be a non-empty string")
        source_id = source.get("id", "approved-inline-text")
        if not isinstance(source_id, str) or not source_id.strip():
            fail("text source id must be a non-empty string when supplied")
        return RenderedSource(
            source_id=source_id.strip(),
            source_name="Approved inline governance text",
            source_url=None,
            source_sha256=None,
            content=content.encode("utf-8"),
        )

    catalog_key = (
        "licenses"
        if kind in {"catalog-license", "gnu-notice"}
        else "notices"
        if kind == "catalog-notice"
        else None
    )
    if catalog_key is None:
        fail(f"unsupported source kind: {kind!r}")
    source_id = source.get("id")
    entries = catalog[catalog_key]
    if not isinstance(source_id, str) or source_id not in entries:
        fail(f"unsupported {kind} id: {source_id!r}")
    entry = entries[source_id]
    if not isinstance(entry, dict):
        fail(f"invalid catalog entry for {source_id}")

    source_url = entry.get("source_url")
    if source_url is not None and not isinstance(source_url, str):
        fail(f"catalog source_url must be a string for {source_id}")
    if kind == "gnu-notice":
        mode = entry.get("gnu_notice_mode")
        if mode not in {"only", "or-later"}:
            fail(f"{source_id} is not a GNU only/or-later catalog entry")
        license_path = resolve_governance_path(source.get("license_path"))
        rendered_text = gnu_notice(
            source_id,
            str(entry.get("name", source_id)),
            str(mode),
            values,
            license_path,
        )
        return RenderedSource(
            source_id=f"{source_id}-project-notice",
            source_name=f"Project notice for {source_id}",
            source_url=source_url,
            source_sha256=None,
            content=rendered_text.encode("utf-8"),
        )

    template, source_hash = load_template(catalog_path.parent.resolve(), entry)
    raw_extra = source.get("values", {})
    if not isinstance(raw_extra, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in raw_extra.items()
    ):
        fail("source.values must be an object of string fields")
    overridden = sorted(set(raw_extra).intersection(values))
    if overridden:
        fail(
            "source.values cannot override project fields: "
            + ", ".join(overridden)
        )
    extra_values = {key: value.strip() for key, value in raw_extra.items()}
    rendered_text = render_template(
        template,
        entry.get("template_fields", []),
        values,
        extra_values,
    )
    return RenderedSource(
        source_id=source_id,
        source_name=str(entry.get("name", source_id)),
        source_url=source_url,
        source_sha256=source_hash,
        content=rendered_text.encode("utf-8"),
    )
