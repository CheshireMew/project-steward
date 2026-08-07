#!/usr/bin/env python3
"""Validate, render, and verify a profile-driven GitHub README header."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlparse


START_MARKER = "<!-- readme-header:start -->"
END_MARKER = "<!-- readme-header:end -->"
ALLOWED_BADGE_STYLES = {
    "flat",
    "flat-square",
    "plastic",
    "for-the-badge",
    "social",
}
ALLOWED_REPOSITORY_BADGES = {"stars", "forks", "license"}
ALLOWED_NAVIGATION_LINK_KINDS = {
    "existing_path",
    "project_path",
    "repository_path",
}
OWNER_PATTERN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$"
)
REPOSITORY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
LANGUAGE_CODE_PATTERN = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})?$")
LINK_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
IDENTITY_IMAGE_SUFFIXES = {".gif", ".png", ".svg", ".webp"}
IDENTITY_IMAGE_WIDTH_PATTERN = re.compile(r"(?:[1-9]\d{0,3}|100%)")


class HeaderProfileError(ValueError):
    """Raised when the profile or its target cannot produce a valid header."""


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise HeaderProfileError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HeaderProfileError(f"{field} must be a non-empty string")
    return value


def _require_https_url(value: object, field: str) -> str:
    url = _require_string(value, field)
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise HeaderProfileError(f"{field} must be an absolute HTTPS URL")
    return url


def _require_relative_path(value: object, field: str) -> str:
    raw = _require_string(value, field)
    if "\\" in raw:
        raise HeaderProfileError(f"{field} must use forward slashes")
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or path.as_posix() in {"", "."}:
        raise HeaderProfileError(f"{field} must be a repository-relative path")
    return path.as_posix()


def _require_relative_markdown_path(value: object, field: str) -> str:
    path = _require_relative_path(value, field)
    if PurePosixPath(path).suffix.lower() != ".md":
        raise HeaderProfileError(f"{field} must point to a Markdown file")
    return path


def _require_exact_keys(
    value: dict, *, required: set[str], optional: set[str], field: str
) -> None:
    missing = required - value.keys()
    extra = value.keys() - required - optional
    if missing:
        raise HeaderProfileError(
            f"{field} is missing fields: {', '.join(sorted(missing))}"
        )
    if extra:
        raise HeaderProfileError(
            f"{field} has unsupported fields: {', '.join(sorted(extra))}"
        )


def validate_profile(profile: object) -> dict:
    if not isinstance(profile, dict):
        raise HeaderProfileError("profile root must be an object")
    _require_exact_keys(
        profile,
        required={
            "schema_version",
            "applies_to",
            "badge_style",
            "languages",
            "navigation_links",
            "social_links",
            "repository_badges",
        },
        optional={"$schema"},
        field="profile",
    )
    if type(profile["schema_version"]) is not int or profile["schema_version"] != 4:
        raise HeaderProfileError("schema_version must be 4")

    applies_to = profile["applies_to"]
    if not isinstance(applies_to, dict):
        raise HeaderProfileError("applies_to must be an object")
    _require_exact_keys(
        applies_to,
        required={"github_owners"},
        optional=set(),
        field="applies_to",
    )
    owners = applies_to["github_owners"]
    if not isinstance(owners, list) or not owners:
        raise HeaderProfileError("applies_to.github_owners must be non-empty")
    normalized_owners: set[str] = set()
    for index, owner_value in enumerate(owners):
        owner = _require_string(
            owner_value, f"applies_to.github_owners[{index}]"
        )
        if not OWNER_PATTERN.fullmatch(owner):
            raise HeaderProfileError(f"invalid GitHub owner: {owner}")
        folded = owner.casefold()
        if folded in normalized_owners:
            raise HeaderProfileError(f"duplicate GitHub owner: {owner}")
        normalized_owners.add(folded)

    style = _require_string(profile["badge_style"], "badge_style")
    if style not in ALLOWED_BADGE_STYLES:
        raise HeaderProfileError(f"unsupported badge_style: {style}")

    languages = profile["languages"]
    if not isinstance(languages, list) or not languages:
        raise HeaderProfileError("languages must be a non-empty array")
    language_codes: set[str] = set()
    language_paths: set[str] = set()
    default_count = 0
    for index, language in enumerate(languages):
        field = f"languages[{index}]"
        if not isinstance(language, dict):
            raise HeaderProfileError(f"{field} must be an object")
        _require_exact_keys(
            language,
            required={"code", "label", "path", "default"},
            optional=set(),
            field=field,
        )
        code = _require_string(language["code"], f"{field}.code")
        if not LANGUAGE_CODE_PATTERN.fullmatch(code):
            raise HeaderProfileError(f"invalid language code: {code}")
        folded_code = code.casefold()
        if folded_code in language_codes:
            raise HeaderProfileError(f"duplicate language code: {code}")
        language_codes.add(folded_code)
        _require_string(language["label"], f"{field}.label")
        path = _require_relative_markdown_path(
            language["path"], f"{field}.path"
        )
        folded_path = path.casefold()
        if folded_path in language_paths:
            raise HeaderProfileError(f"duplicate language path: {path}")
        language_paths.add(folded_path)
        if not isinstance(language["default"], bool):
            raise HeaderProfileError(f"{field}.default must be a boolean")
        if language["default"]:
            default_count += 1
    if default_count != 1:
        raise HeaderProfileError("languages must contain exactly one default")

    navigation_links = profile["navigation_links"]
    if not isinstance(navigation_links, list):
        raise HeaderProfileError("navigation_links must be an array")
    navigation_ids: set[str] = set()
    for index, link in enumerate(navigation_links):
        field = f"navigation_links[{index}]"
        if not isinstance(link, dict):
            raise HeaderProfileError(f"{field} must be an object")
        _require_exact_keys(
            link,
            required={"id", "label", "kind"},
            optional={"path"},
            field=field,
        )
        link_id = _require_string(link["id"], f"{field}.id")
        if not LINK_ID_PATTERN.fullmatch(link_id):
            raise HeaderProfileError(f"invalid navigation link id: {link_id}")
        if link_id in navigation_ids:
            raise HeaderProfileError(
                f"duplicate navigation link id: {link_id}"
            )
        navigation_ids.add(link_id)
        _require_string(link["label"], f"{field}.label")
        kind = _require_string(link["kind"], f"{field}.kind")
        if kind not in ALLOWED_NAVIGATION_LINK_KINDS:
            raise HeaderProfileError(
                f"unsupported navigation link kind: {kind}"
            )
        if kind == "project_path":
            if "path" in link:
                raise HeaderProfileError(
                    f"{field}.path must be supplied by the target project"
                )
        else:
            if "path" not in link:
                raise HeaderProfileError(f"{field} is missing fields: path")
            _require_relative_path(link["path"], f"{field}.path")

    social_links = profile["social_links"]
    if not isinstance(social_links, list):
        raise HeaderProfileError("social_links must be an array")
    link_ids: set[str] = set()
    for index, link in enumerate(social_links):
        field = f"social_links[{index}]"
        if not isinstance(link, dict):
            raise HeaderProfileError(f"{field} must be an object")
        _require_exact_keys(
            link,
            required={"id", "label", "value", "url"},
            optional=set(),
            field=field,
        )
        link_id = _require_string(link["id"], f"{field}.id")
        if not LINK_ID_PATTERN.fullmatch(link_id):
            raise HeaderProfileError(f"invalid social link id: {link_id}")
        if link_id in link_ids:
            raise HeaderProfileError(f"duplicate social link id: {link_id}")
        link_ids.add(link_id)
        _require_string(link["label"], f"{field}.label")
        _require_string(link["value"], f"{field}.value")
        _require_https_url(link["url"], f"{field}.url")

    badges = profile["repository_badges"]
    if not isinstance(badges, list):
        raise HeaderProfileError("repository_badges must be an array")
    badge_names: set[str] = set()
    for index, badge_value in enumerate(badges):
        badge = _require_string(badge_value, f"repository_badges[{index}]")
        if badge not in ALLOWED_REPOSITORY_BADGES:
            raise HeaderProfileError(f"unsupported repository badge: {badge}")
        if badge in badge_names:
            raise HeaderProfileError(f"duplicate repository badge: {badge}")
        badge_names.add(badge)
    return profile


def load_profile(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HeaderProfileError(f"cannot read profile {path}: {exc}") from exc
    try:
        profile = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise HeaderProfileError(f"invalid profile JSON: {exc}") from exc
    return validate_profile(profile)


def parse_repository(value: str) -> tuple[str, str]:
    parts = value.split("/")
    if len(parts) != 2:
        raise HeaderProfileError("repository must use OWNER/REPOSITORY")
    owner, name = parts
    if not OWNER_PATTERN.fullmatch(owner) or not REPOSITORY_NAME_PATTERN.fullmatch(
        name
    ):
        raise HeaderProfileError(f"invalid GitHub repository: {value}")
    return owner, name


def ensure_profile_applies(profile: dict, repository: str) -> None:
    owner, _ = parse_repository(repository)
    owners = {
        candidate.casefold()
        for candidate in profile["applies_to"]["github_owners"]
    }
    if owner.casefold() not in owners:
        raise HeaderProfileError(
            f"profile does not apply to GitHub owner {owner}"
        )


def _available_languages(
    profile: dict, readme_root: Path, *, allow_missing: bool
) -> list[dict]:
    available: list[dict] = []
    missing: list[str] = []
    for language in profile["languages"]:
        target = readme_root / PurePosixPath(language["path"])
        if target.is_file():
            available.append(language)
        else:
            missing.append(language["path"])
    if missing and not allow_missing:
        raise HeaderProfileError(
            "configured README translations are missing: " + ", ".join(missing)
        )
    return available


def parse_navigation_targets(values: list[str] | None) -> dict[str, str]:
    targets: dict[str, str] = {}
    for value in values or []:
        link_id, separator, raw_path = value.partition("=")
        if not separator or not LINK_ID_PATTERN.fullmatch(link_id):
            raise HeaderProfileError(
                "navigation target must use LINK_ID=REPOSITORY_RELATIVE_MARKDOWN_PATH"
            )
        if link_id in targets:
            raise HeaderProfileError(f"duplicate navigation target: {link_id}")
        targets[link_id] = _require_relative_markdown_path(
            raw_path,
            f"navigation target {link_id}",
        )
    return targets


def _resolve_navigation_links(
    profile: dict,
    *,
    repository: str,
    readme_root: Path,
    navigation_targets: dict[str, str],
) -> list[tuple[str, str]]:
    quoted_repository = _quoted_repository(repository)
    github_root = f"https://github.com/{quoted_repository}"
    resolved: list[tuple[str, str]] = []
    project_link_ids = {
        link["id"]
        for link in profile["navigation_links"]
        if link["kind"] == "project_path"
    }
    unknown_targets = navigation_targets.keys() - project_link_ids
    if unknown_targets:
        raise HeaderProfileError(
            "navigation targets do not match project_path links: "
            + ", ".join(sorted(unknown_targets))
        )
    for link in profile["navigation_links"]:
        if link["kind"] == "project_path":
            path = navigation_targets.get(link["id"])
            if path is None:
                continue
            if not (readme_root / PurePosixPath(path)).is_file():
                raise HeaderProfileError(
                    f"project navigation target is missing: {path}"
                )
            href = f"./{quote(path, safe='/')}"
        elif link["kind"] == "existing_path":
            path = _require_relative_path(
                link["path"], f"navigation_links.{link['id']}.path"
            )
            if not (readme_root / PurePosixPath(path)).exists():
                raise HeaderProfileError(
                    f"configured navigation target is missing: {path}"
                )
            href = f"./{quote(path, safe='/')}"
        else:
            path = _require_relative_path(
                link["path"], f"navigation_links.{link['id']}.path"
            )
            href = f"{github_root}/{quote(path, safe='/')}"
        resolved.append((link["label"], href))
    return resolved


def _render_language_row(
    languages: list[dict],
    current_language: str,
    navigation_links: list[tuple[str, str]],
) -> str:
    if not any(language["code"] == current_language for language in languages):
        raise HeaderProfileError(
            f"current language is not available: {current_language}"
        )
    items: list[str] = []
    for language in languages:
        label = html.escape(language["label"])
        if language["code"] == current_language:
            items.append(f"<strong>{label}</strong>")
        else:
            href = html.escape(f"./{language['path']}", quote=True)
            items.append(f'<a href="{href}">{label}</a>')
    content = " · ".join(items)
    if navigation_links:
        navigation = " | ".join(
            f'<a href="{html.escape(href, quote=True)}">'
            f"{html.escape(label)}</a>"
            for label, href in navigation_links
        )
        content += " | " + navigation
    return '<p align="center">\n  ' + content + "\n</p>"


def _render_identity(
    *,
    project_name: str,
    tagline: str,
    identity_image: str,
    identity_image_width: str,
    readme_root: Path,
) -> list[str]:
    name = _require_string(project_name, "project_name")
    description = _require_string(tagline, "tagline")
    image_path = _require_relative_path(identity_image, "identity_image")
    suffix = PurePosixPath(image_path).suffix.lower()
    if suffix not in IDENTITY_IMAGE_SUFFIXES:
        raise HeaderProfileError(
            "identity_image must be an SVG, PNG, WebP, or GIF file"
        )
    if not (readme_root / PurePosixPath(image_path)).is_file():
        raise HeaderProfileError(
            f"configured identity image is missing: {image_path}"
        )
    width = _require_string(identity_image_width, "identity_image_width")
    if not IDENTITY_IMAGE_WIDTH_PATTERN.fullmatch(width):
        raise HeaderProfileError(
            "identity_image_width must be 100% or an integer from 1 to 9999"
        )
    src = html.escape(f"./{quote(image_path, safe='/')}", quote=True)
    rows = [
        '<p align="center">\n'
        f'  <img src="{src}" width="{width}" '
        f'alt="{html.escape(name, quote=True)}">\n'
        "</p>"
    ]
    rows.extend(
        [
            f'<h1 align="center">{html.escape(name)}</h1>',
            '<p align="center">\n'
            f"  <strong>{html.escape(description)}</strong>\n"
            "</p>",
        ]
    )
    return rows


def _render_social_row(profile: dict) -> str | None:
    if not profile["social_links"]:
        return None
    items: list[str] = []
    for link in profile["social_links"]:
        url = html.escape(link["url"], quote=True)
        label = html.escape(link["label"])
        value = html.escape(link["value"])
        items.append(
            f'<a href="{url}">{label}：{value}</a>'
        )
    return '<p align="center">\n  ' + " · ".join(items) + "\n</p>"


def _quoted_repository(repository: str) -> str:
    owner, name = parse_repository(repository)
    return f"{quote(owner, safe='')}/{quote(name, safe='')}"


def _render_repository_row(
    profile: dict,
    repository: str,
    *,
    branch: str,
    license_path: str,
    readme_root: Path,
) -> str | None:
    badges = profile["repository_badges"]
    if not badges:
        return None
    if not branch.strip():
        raise HeaderProfileError("branch must be non-empty")
    normalized_license_path = _require_relative_path(license_path, "license_path")
    if "license" in badges and not (readme_root / normalized_license_path).is_file():
        raise HeaderProfileError(
            f"configured license file is missing: {normalized_license_path}"
        )

    quoted_repository = _quoted_repository(repository)
    github_root = f"https://github.com/{quoted_repository}"
    shields_root = f"https://img.shields.io/github"
    style = quote(profile["badge_style"], safe="")
    rows: dict[str, tuple[str, str, str]] = {
        "stars": (
            f"{github_root}/stargazers",
            f"{shields_root}/stars/{quoted_repository}?style={style}",
            "GitHub Stars",
        ),
        "forks": (
            f"{github_root}/forks",
            f"{shields_root}/forks/{quoted_repository}?style={style}",
            "GitHub Forks",
        ),
        "license": (
            f"{github_root}/blob/{quote(branch, safe='')}/"
            f"{quote(normalized_license_path, safe='/')}",
            f"{shields_root}/license/{quoted_repository}?style={style}",
            "Repository License",
        ),
    }
    lines = ['<p align="center">']
    for badge in badges:
        url, src, alt = rows[badge]
        lines.append(
            f'  <a href="{html.escape(url, quote=True)}">'
            f'<img src="{html.escape(src, quote=True)}" '
            f'alt="{html.escape(alt, quote=True)}"></a>'
        )
    lines.append("</p>")
    return "\n".join(lines)


def render_header(
    profile: dict,
    *,
    repository: str,
    readme_root: Path,
    current_language: str,
    project_name: str,
    tagline: str,
    identity_image: str,
    identity_image_width: str = "160",
    branch: str,
    license_path: str,
    allow_missing_languages: bool = False,
    navigation_targets: dict[str, str] | None = None,
) -> str:
    validate_profile(profile)
    ensure_profile_applies(profile, repository)
    root = readme_root.resolve()
    languages = _available_languages(
        profile, root, allow_missing=allow_missing_languages
    )
    navigation_links = _resolve_navigation_links(
        profile,
        repository=repository,
        readme_root=root,
        navigation_targets=navigation_targets or {},
    )
    rows = _render_identity(
        project_name=project_name,
        tagline=tagline,
        identity_image=identity_image,
        identity_image_width=identity_image_width,
        readme_root=root,
    )
    rows.append(
        _render_language_row(
            languages,
            current_language,
            navigation_links,
        )
    )
    social_row = _render_social_row(profile)
    if social_row:
        rows.append(social_row)
    repository_row = _render_repository_row(
        profile,
        repository,
        branch=branch,
        license_path=license_path,
        readme_root=root,
    )
    if repository_row:
        rows.append(repository_row)
    return "\n\n".join([START_MARKER, *rows, END_MARKER])


def extract_header(text: str) -> str:
    if text.count(START_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise HeaderProfileError(
            "README must contain exactly one managed header marker pair"
        )
    start = text.index(START_MARKER)
    end_start = text.index(END_MARKER)
    if end_start <= start:
        raise HeaderProfileError("README header markers are out of order")
    end = end_start + len(END_MARKER)
    return text[start:end]


def verify_readme_header(
    readme: Path,
    profile: dict,
    *,
    repository: str,
    current_language: str,
    project_name: str,
    tagline: str,
    identity_image: str,
    identity_image_width: str = "160",
    branch: str,
    license_path: str,
    allow_missing_languages: bool = False,
    navigation_targets: dict[str, str] | None = None,
) -> None:
    try:
        text = readme.read_text(encoding="utf-8")
    except OSError as exc:
        raise HeaderProfileError(f"cannot read README {readme}: {exc}") from exc
    actual = extract_header(text)
    expected = render_header(
        profile,
        repository=repository,
        readme_root=readme.parent,
        current_language=current_language,
        project_name=project_name,
        tagline=tagline,
        identity_image=identity_image,
        identity_image_width=identity_image_width,
        branch=branch,
        license_path=license_path,
        allow_missing_languages=allow_missing_languages,
        navigation_targets=navigation_targets,
    )
    if actual != expected:
        raise HeaderProfileError(
            "README managed header does not match the active profile and repository"
        )


def _add_render_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--repository", required=True, help="OWNER/REPOSITORY")
    parser.add_argument("--language", required=True, help="current language code")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--tagline", required=True)
    parser.add_argument("--identity-image", required=True)
    parser.add_argument("--identity-image-width", default="160")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--license-path", default="LICENSE")
    parser.add_argument("--allow-missing-languages", action="store_true")
    parser.add_argument(
        "--navigation-target",
        action="append",
        default=[],
        metavar="LINK_ID=PATH",
        help="resolve one project_path link to an existing Markdown file",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--profile", type=Path, required=True)

    render_parser = subparsers.add_parser("render")
    _add_render_arguments(render_parser)
    render_parser.add_argument("--readme-root", type=Path, required=True)

    verify_parser = subparsers.add_parser("verify")
    _add_render_arguments(verify_parser)
    verify_parser.add_argument("--readme", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile = load_profile(args.profile.resolve())
        if args.command == "validate":
            print(f"OK: README header profile is valid: {args.profile.resolve()}")
            return 0
        navigation_targets = parse_navigation_targets(args.navigation_target)
        if args.command == "render":
            print(
                render_header(
                    profile,
                    repository=args.repository,
                    readme_root=args.readme_root,
                    current_language=args.language,
                    project_name=args.project_name,
                    tagline=args.tagline,
                    identity_image=args.identity_image,
                    identity_image_width=args.identity_image_width,
                    branch=args.branch,
                    license_path=args.license_path,
                    allow_missing_languages=args.allow_missing_languages,
                    navigation_targets=navigation_targets,
                )
            )
            return 0
        verify_readme_header(
            args.readme.resolve(),
            profile,
            repository=args.repository,
            current_language=args.language,
            project_name=args.project_name,
            tagline=args.tagline,
            identity_image=args.identity_image,
            identity_image_width=args.identity_image_width,
            branch=args.branch,
            license_path=args.license_path,
            allow_missing_languages=args.allow_missing_languages,
            navigation_targets=navigation_targets,
        )
        print(f"OK: README header matches profile: {args.readme.resolve()}")
        return 0
    except HeaderProfileError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
