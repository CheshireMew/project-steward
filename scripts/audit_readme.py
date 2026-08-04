#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 oil-oil
# SPDX-License-Identifier: MIT
#
# Migrated from oil-oil/beautify-github-readme. See THIRD_PARTY_NOTICES.md.
"""Audit README images, SVG compatibility, and an optional managed header."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from readme_header import HeaderProfileError, load_profile, verify_readme_header


MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I)
HTML_ALT = re.compile(r"\balt=[\"']([^\"']*)[\"']", re.I)
UNSAFE_SVG_TAGS = {"script", "foreignObject"}
SCOPE_MESSAGE = (
    "Scope: structural checks only; source currency, factual accuracy, "
    "remote endpoint availability, visual relevance, and rendered quality "
    "are not evaluated."
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", type=Path)
    parser.add_argument("--header-profile", type=Path)
    parser.add_argument("--repository", help="OWNER/REPOSITORY")
    parser.add_argument("--language", help="current README language code")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--license-path", default="LICENSE")
    parser.add_argument("--allow-missing-languages", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    readme = args.readme.expanduser().resolve()
    if not readme.is_file():
        print(f"ERROR: README not found: {readme}")
        return 2

    if args.header_profile and (not args.repository or not args.language):
        print(
            "ERROR: --header-profile requires --repository and --language",
            file=sys.stderr,
        )
        return 2
    if not args.header_profile and (args.repository or args.language):
        print(
            "ERROR: --repository and --language require --header-profile",
            file=sys.stderr,
        )
        return 2

    text = readme.read_text(encoding="utf-8")
    markdown_images = MARKDOWN_IMAGE.findall(text)
    sources = [src for _, src in markdown_images]
    html_tags = re.findall(r"<img\b[^>]*>", text, flags=re.I)
    sources.extend(HTML_IMAGE.findall(text))

    warnings: list[str] = []
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
            verify_readme_header(
                readme,
                profile,
                repository=args.repository,
                current_language=args.language,
                branch=args.branch,
                license_path=args.license_path,
                allow_missing_languages=args.allow_missing_languages,
            )
        except HeaderProfileError as exc:
            warnings.append(f"managed README header: {exc}")

    print(f"README: {readme}")
    print(f"Local images checked: {checked}")
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
