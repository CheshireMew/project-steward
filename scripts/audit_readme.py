#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 oil-oil
# SPDX-License-Identifier: MIT
#
# Migrated from oil-oil/beautify-github-readme. See THIRD_PARTY_NOTICES.md.
"""Audit README structure, section order, prose density, images, SVGs, and managed headers."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from readme_header import (
    HeaderProfileError,
    load_profile,
    parse_navigation_targets,
    verify_readme_header,
)


MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I)
HTML_ALT = re.compile(r"\balt=[\"']([^\"']*)[\"']", re.I)
UNSAFE_SVG_TAGS = {"script", "foreignObject"}
SCOPE_MESSAGE = (
    "Scope: structural and prose-density checks only; source currency, factual accuracy, "
    "remote endpoint availability, visual relevance, and rendered quality "
    "are not evaluated."
)
STRUCTURAL_BLOCK = re.compile(
    r"^(?:#{1,6}\s|[-*+]\s|\d+[.)]\s|>|\||<|!\[|```|~~~)"
)
MARKDOWN_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
STAR_HISTORY_HEADING = re.compile(r"\bstar\s+history\b", re.I)
LEGAL_HEADING = re.compile(
    r"(?:licen[cs](?:e|ing)|许可证|授[權权]|ライセンス|"
    r"third[\s-]*party|acknowledg|attribution|credits?|notices?|"
    r"第三方|第三者|致谢|謝辞)",
    re.I,
)


def local_target(src: str, base: Path) -> Path | None:
    if src.startswith(("http://", "https://", "data:", "#")):
        return None
    clean = src.split("#", 1)[0].split("?", 1)[0]
    return (base / clean).resolve()


def audit_svg(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"invalid SVG XML: {exc}"]

    if "viewBox" not in root.attrib:
        issues.append("missing viewBox")

    title_found = False
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "title":
            title_found = True
        if tag in UNSAFE_SVG_TAGS:
            issues.append(f"contains unsupported <{tag}>")
    if not title_found:
        issues.append("missing <title>")
    return issues


def content_blocks(text: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    current: list[str] = []
    current_line = 0
    in_fence = False

    def flush() -> None:
        nonlocal current, current_line
        if current:
            blocks.append((current_line, " ".join(part.strip() for part in current)))
            current = []
            current_line = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            flush()
            blocks.append((line_number, stripped))
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not stripped:
            flush()
            continue
        if not current:
            current_line = line_number
        current.append(stripped)
    flush()
    return blocks


def is_prose_block(block: str) -> bool:
    return not STRUCTURAL_BLOCK.match(block)


def visible_character_count(block: str) -> int:
    without_links = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", block)
    without_markup = re.sub(r"[`*_~]", "", without_links)
    return len(without_markup)


def audit_prose_density(
    text: str,
    *,
    max_characters: int,
    max_consecutive: int,
) -> tuple[int, list[str]]:
    issues: list[str] = []
    prose_count = 0
    run: list[tuple[int, str]] = []

    def flush_run() -> None:
        nonlocal run
        if len(run) > max_consecutive:
            start = run[0][0]
            end = run[-1][0]
            issues.append(
                "prose wall from lines {}-{}: {} consecutive paragraphs "
                "(maximum {})".format(start, end, len(run), max_consecutive)
            )
        run = []

    for line_number, block in content_blocks(text):
        if not is_prose_block(block):
            flush_run()
            continue
        prose_count += 1
        run.append((line_number, block))
        length = visible_character_count(block)
        if length > max_characters:
            issues.append(
                "prose paragraph at line {} has {} characters (maximum {})".format(
                    line_number,
                    length,
                    max_characters,
                )
            )
    flush_run()
    return prose_count, issues


def markdown_headings(text: str) -> list[tuple[int, int, str]]:
    headings: list[tuple[int, int, str]] = []
    in_fence = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = MARKDOWN_HEADING.match(stripped)
        if match:
            headings.append((line_number, len(match.group(1)), match.group(2)))
    return headings


def audit_terminal_section_order(text: str) -> list[str]:
    headings = markdown_headings(text)
    star_sections = [
        (line, level, heading)
        for line, level, heading in headings
        if STAR_HISTORY_HEADING.search(heading)
    ]
    legal_sections = [
        (line, level, heading)
        for line, level, heading in headings
        if LEGAL_HEADING.search(heading)
    ]
    if not star_sections or not legal_sections:
        return []

    first_star = min(star_sections, key=lambda item: item[0])
    first_legal = min(legal_sections, key=lambda item: item[0])
    if first_star[0] < first_legal[0]:
        return []
    return [
        "Star History section must appear before license and third-party "
        "acknowledgements: Star History is at line {} and the first legal "
        "section is at line {}".format(first_star[0], first_legal[0])
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", type=Path)
    parser.add_argument("--header-profile", type=Path)
    parser.add_argument("--repository", help="OWNER/REPOSITORY")
    parser.add_argument("--language", help="current README language code")
    parser.add_argument("--project-name")
    parser.add_argument("--tagline")
    parser.add_argument("--identity-image")
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
    parser.add_argument("--max-prose-characters", type=int, default=360)
    parser.add_argument("--max-consecutive-prose", type=int, default=3)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    readme = args.readme.expanduser().resolve()
    if not readme.is_file():
        print(f"ERROR: README not found: {readme}")
        return 2

    if args.header_profile and (
        not args.repository
        or not args.language
        or not args.project_name
        or not args.tagline
        or not args.identity_image
    ):
        print(
            "ERROR: --header-profile requires --repository, --language, "
            "--project-name, --tagline and --identity-image",
            file=sys.stderr,
        )
        return 2
    if not args.header_profile and (
        args.repository
        or args.language
        or args.project_name
        or args.tagline
        or args.identity_image
        or args.navigation_target
    ):
        print(
            "ERROR: header identity, repository, language and navigation options "
            "require --header-profile",
            file=sys.stderr,
        )
        return 2
    if args.max_prose_characters < 1 or args.max_consecutive_prose < 1:
        print(
            "ERROR: prose density limits must be positive integers",
            file=sys.stderr,
        )
        return 2

    text = readme.read_text(encoding="utf-8")
    markdown_images = MARKDOWN_IMAGE.findall(text)
    sources = [src for _, src in markdown_images]
    html_tags = re.findall(r"<img\b[^>]*>", text, flags=re.I)
    sources.extend(HTML_IMAGE.findall(text))

    warnings: list[str] = []
    warnings.extend(audit_terminal_section_order(text))
    prose_checked, prose_issues = audit_prose_density(
        text,
        max_characters=args.max_prose_characters,
        max_consecutive=args.max_consecutive_prose,
    )
    warnings.extend(prose_issues)
    for alt, src in markdown_images:
        if not alt.strip():
            warnings.append(f"Markdown image missing useful alt text: {src}")
    for tag in html_tags:
        match = HTML_ALT.search(tag)
        if not match or not match.group(1).strip():
            warnings.append(f"HTML image missing useful alt text: {tag[:100]}")

    checked = 0
    for src in dict.fromkeys(sources):
        target = local_target(src, readme.parent)
        if target is None:
            continue
        checked += 1
        if not target.is_file():
            warnings.append(f"missing image: {src}")
            continue
        if target.suffix.lower() == ".svg":
            for issue in audit_svg(target):
                warnings.append(f"{src}: {issue}")

    header_checked = False
    if args.header_profile:
        header_checked = True
        try:
            profile = load_profile(args.header_profile.expanduser().resolve())
            navigation_targets = parse_navigation_targets(args.navigation_target)
            verify_readme_header(
                readme,
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
        except HeaderProfileError as exc:
            warnings.append(f"managed README header: {exc}")

    print(f"README: {readme}")
    print(f"Local images checked: {checked}")
    print(f"Prose blocks checked: {prose_checked}")
    print(f"Managed header checked: {'yes' if header_checked else 'no'}")
    print(SCOPE_MESSAGE)
    if warnings:
        print("Issues:")
        for warning in warnings:
            print(f"- {warning}")
        return 1
    print("OK: structural README checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
