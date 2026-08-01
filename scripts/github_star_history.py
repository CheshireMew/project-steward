#!/usr/bin/env python3
"""Generate and atomically publish a repository's GitHub star history SVGs."""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from xml.sax.saxutils import escape


API_VERSION = "2026-03-10"
STAR_ACCEPT = "application/vnd.github.star+json"
JSON_ACCEPT = "application/vnd.github+json"
USER_AGENT = "project-steward-star-history/1"


class GitHubApiError(RuntimeError):
    """An error returned by GitHub without exposing authentication material."""


@dataclass(frozen=True)
class StarSnapshot:
    repository: str
    created_on: date
    star_dates: Tuple[date, ...]

    @property
    def star_count(self) -> int:
        return len(self.star_dates)


@dataclass(frozen=True)
class PublishResult:
    changed: bool
    star_count: int
    branch: str
    light_url: str
    dark_url: str


class GitHubClient:
    def __init__(self, token: str, api_url: str = "https://api.github.com") -> None:
        if not token:
            raise ValueError("GitHub token is required")
        self._token = token
        self._api_url = api_url.rstrip("/")

    def request(
        self,
        method: str,
        path_or_url: str,
        *,
        payload: Optional[Mapping[str, Any]] = None,
        accept: str = JSON_ACCEPT,
        allow_not_found: bool = False,
    ) -> Tuple[Any, Mapping[str, str], int]:
        url = (
            path_or_url
            if path_or_url.startswith("https://") or path_or_url.startswith("http://")
            else self._api_url + path_or_url
        )
        data = None
        if payload is not None:
            data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": accept,
                "Authorization": "Bearer " + self._token,
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": USER_AGENT,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                parsed = json.loads(raw.decode("utf-8")) if raw else None
                return parsed, dict(response.headers.items()), response.status
        except urllib.error.HTTPError as error:
            raw = error.read()
            if allow_not_found and error.code == 404:
                return None, dict(error.headers.items()), 404
            message = ""
            if raw:
                try:
                    body = json.loads(raw.decode("utf-8"))
                    message = str(body.get("message", ""))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    message = raw.decode("utf-8", errors="replace")[:300]
            resource = urllib.parse.urlsplit(url).path
            detail = (": " + message) if message else ""
            raise GitHubApiError(
                "GitHub API returned {} for {} {}{}".format(
                    error.code, method, resource, detail
                )
            ) from None
        except urllib.error.URLError as error:
            raise GitHubApiError("Could not reach GitHub API: {}".format(error.reason)) from None


def parse_repository(value: str) -> Tuple[str, str]:
    parts = value.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("repository must use the OWNER/REPOSITORY form")
    if any(any(character in part for character in "\r\n?#") for part in parts):
        raise ValueError("repository contains unsupported characters")
    return parts[0], parts[1]


def validate_branch(value: str) -> str:
    if (
        not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", value)
        or ".." in value
        or "//" in value
        or value.endswith(("/", ".", ".lock"))
    ):
        raise ValueError("output branch is not a valid Git reference name")
    return value


def validate_svg_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if (
        normalized.startswith("/")
        or not normalized.endswith(".svg")
        or any(part in ("", ".", "..") for part in parts)
        or any(character in normalized for character in "\r\n?#")
    ):
        raise ValueError("output path must be a relative .svg path")
    return normalized


def parse_github_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _repo_path(owner: str, repository: str) -> str:
    return "/repos/{}/{}".format(
        urllib.parse.quote(owner, safe=""), urllib.parse.quote(repository, safe="")
    )


def _fetch_repository_metadata(
    client: GitHubClient, owner: str, repository: str
) -> Mapping[str, Any]:
    result, _, _ = client.request("GET", _repo_path(owner, repository))
    if not isinstance(result, dict):
        raise GitHubApiError("GitHub returned invalid repository metadata")
    return result


def _fetch_star_dates(client: GitHubClient, owner: str, repository: str) -> List[date]:
    dates: List[date] = []
    page = 1
    while True:
        path = "{}/stargazers?per_page=100&page={}".format(
            _repo_path(owner, repository), page
        )
        result, _, _ = client.request("GET", path, accept=STAR_ACCEPT)
        if not isinstance(result, list):
            raise GitHubApiError("GitHub returned invalid stargazer data")
        for item in result:
            if not isinstance(item, dict) or not isinstance(item.get("starred_at"), str):
                raise GitHubApiError(
                    "GitHub did not return star timestamps; check Metadata read permission"
                )
            dates.append(parse_github_datetime(item["starred_at"]).date())
        if len(result) < 100:
            break
        page += 1
    return dates


def fetch_snapshot(
    client: GitHubClient, repository: str, *, attempts: int = 3
) -> StarSnapshot:
    owner, name = parse_repository(repository)
    for attempt in range(attempts):
        before = _fetch_repository_metadata(client, owner, name)
        star_dates = _fetch_star_dates(client, owner, name)
        after = _fetch_repository_metadata(client, owner, name)
        before_count = int(before.get("stargazers_count", -1))
        after_count = int(after.get("stargazers_count", -1))
        if before_count == after_count == len(star_dates):
            created_at = after.get("created_at")
            full_name = after.get("full_name")
            if not isinstance(created_at, str) or not isinstance(full_name, str):
                raise GitHubApiError("GitHub returned incomplete repository metadata")
            return StarSnapshot(
                repository=full_name,
                created_on=parse_github_datetime(created_at).date(),
                star_dates=tuple(sorted(star_dates)),
            )
        if attempt + 1 == attempts:
            raise GitHubApiError(
                "Star count changed while reading the history; rerun the workflow"
            )
    raise AssertionError("unreachable")


def _nice_maximum(value: int) -> int:
    if value <= 1:
        return 1
    exponent = 10 ** math.floor(math.log10(value))
    fraction = value / exponent
    for candidate in (1, 2, 5, 10):
        if fraction <= candidate:
            return int(candidate * exponent)
    return int(10 * exponent)


def _format_date_tick(value: date, span_days: int) -> str:
    if span_days >= 730:
        return value.strftime("%Y")
    if span_days >= 90:
        return value.strftime("%Y-%m")
    return value.strftime("%m-%d")


def _cumulative_points(snapshot: StarSnapshot) -> Tuple[List[Tuple[date, int]], date, date]:
    counts = Counter(snapshot.star_dates)
    start = min([snapshot.created_on] + list(counts.keys()))
    points: List[Tuple[date, int]] = [(start, 0)]
    total = 0
    for day in sorted(counts):
        total += counts[day]
        points.append((day, total))
    final_event = points[-1][0]
    end = max(final_event, start + timedelta(days=1))
    return points, start, end


def render_svg(snapshot: StarSnapshot, theme: str) -> str:
    palettes = {
        "light": {
            "background": "#ffffff",
            "panel": "#f6f8fa",
            "grid": "#d8dee4",
            "text": "#1f2328",
            "muted": "#59636e",
            "line": "#1f883d",
            "fill": "#2da44e",
        },
        "dark": {
            "background": "#0d1117",
            "panel": "#161b22",
            "grid": "#30363d",
            "text": "#f0f6fc",
            "muted": "#8b949e",
            "line": "#3fb950",
            "fill": "#238636",
        },
    }
    if theme not in palettes:
        raise ValueError("theme must be 'light' or 'dark'")
    colors = palettes[theme]
    width, height = 880, 520
    left, right, top, bottom = 78, 32, 82, 62
    plot_width = width - left - right
    plot_height = height - top - bottom
    points, start, end = _cumulative_points(snapshot)
    span_days = max((end - start).days, 1)
    y_max = _nice_maximum(snapshot.star_count)

    def x_position(day: date) -> float:
        return left + ((day - start).days / span_days) * plot_width

    def y_position(value: int) -> float:
        return top + plot_height - (value / y_max) * plot_height

    path_parts = [
        "M {:.2f} {:.2f}".format(x_position(points[0][0]), y_position(points[0][1]))
    ]
    for day, count in points[1:]:
        path_parts.append("H {:.2f} V {:.2f}".format(x_position(day), y_position(count)))
    path_parts.append("H {:.2f}".format(left + plot_width))
    line_path = " ".join(path_parts)
    fill_path = "{} V {:.2f} H {:.2f} Z".format(
        line_path, top + plot_height, left
    )

    y_ticks = sorted(set(round(index * y_max / 4) for index in range(5)))
    x_dates = []
    for index in range(6):
        candidate = start + timedelta(days=round(index * span_days / 5))
        if not x_dates or candidate != x_dates[-1]:
            x_dates.append(candidate)

    repository_label = escape(snapshot.repository)
    through_label = end if snapshot.star_count == 0 else max(snapshot.star_dates)
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" viewBox="0 0 {} {}" role="img" aria-labelledby="title description">'.format(
            width, height, width, height
        ),
        "  <title id=\"title\">Star history for {}</title>".format(repository_label),
        "  <desc id=\"description\">Cumulative GitHub stars through {}. Total: {}.</desc>".format(
            through_label.isoformat(), snapshot.star_count
        ),
        '  <rect width="100%" height="100%" rx="12" fill="{}"/>'.format(
            colors["background"]
        ),
        '  <rect x="{}" y="{}" width="{}" height="{}" rx="8" fill="{}"/>'.format(
            left, top, plot_width, plot_height, colors["panel"]
        ),
        '  <g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">',
        '    <text x="{}" y="36" fill="{}" font-size="20" font-weight="600">GitHub Star History</text>'.format(
            left, colors["text"]
        ),
        '    <text x="{}" y="60" fill="{}" font-size="13">{}</text>'.format(
            left, colors["muted"], repository_label
        ),
        '    <text x="{}" y="39" text-anchor="end" fill="{}" font-size="26" font-weight="700">{}</text>'.format(
            left + plot_width, colors["text"], snapshot.star_count
        ),
        '    <text x="{}" y="60" text-anchor="end" fill="{}" font-size="12">stars</text>'.format(
            left + plot_width, colors["muted"]
        ),
    ]
    for tick in y_ticks:
        y = y_position(tick)
        elements.append(
            '    <line x1="{}" y1="{:.2f}" x2="{}" y2="{:.2f}" stroke="{}" stroke-width="1"/>'.format(
                left, y, left + plot_width, y, colors["grid"]
            )
        )
        elements.append(
            '    <text x="{}" y="{:.2f}" text-anchor="end" dominant-baseline="middle" fill="{}" font-size="11">{}</text>'.format(
                left - 10, y, colors["muted"], tick
            )
        )
    for index, tick_date in enumerate(x_dates):
        x = x_position(tick_date)
        anchor = "start" if index == 0 else "end" if index == len(x_dates) - 1 else "middle"
        elements.append(
            '    <text x="{:.2f}" y="{}" text-anchor="{}" fill="{}" font-size="11">{}</text>'.format(
                x,
                top + plot_height + 28,
                anchor,
                colors["muted"],
                _format_date_tick(tick_date, span_days),
            )
        )
    elements.extend(
        [
            '    <path d="{}" fill="{}" opacity="0.14"/>'.format(
                fill_path, colors["fill"]
            ),
            '    <path d="{}" fill="none" stroke="{}" stroke-width="3" stroke-linejoin="round"/>'.format(
                line_path, colors["line"]
            ),
        ]
    )
    if snapshot.star_count:
        elements.append(
            '    <circle cx="{:.2f}" cy="{:.2f}" r="4.5" fill="{}" stroke="{}" stroke-width="2"/>'.format(
                left + plot_width,
                y_position(snapshot.star_count),
                colors["line"],
                colors["background"],
            )
        )
    elements.extend(["  </g>", "</svg>", ""])
    return "\n".join(elements)


def _get_ref(
    client: GitHubClient, owner: str, repository: str, branch: str
) -> Optional[Mapping[str, Any]]:
    path = "{}/git/ref/heads/{}".format(
        _repo_path(owner, repository), urllib.parse.quote(branch, safe="/")
    )
    result, _, status = client.request("GET", path, allow_not_found=True)
    if status == 404:
        return None
    if not isinstance(result, dict):
        raise GitHubApiError("GitHub returned invalid branch data")
    return result


def _get_file(
    client: GitHubClient,
    owner: str,
    repository: str,
    branch: str,
    path: str,
) -> Optional[bytes]:
    request_path = "{}/contents/{}?ref={}".format(
        _repo_path(owner, repository),
        urllib.parse.quote(path, safe="/"),
        urllib.parse.quote(branch, safe=""),
    )
    result, _, status = client.request("GET", request_path, allow_not_found=True)
    if status == 404:
        return None
    if not isinstance(result, dict) or result.get("encoding") != "base64":
        raise GitHubApiError("GitHub returned invalid file data for {}".format(path))
    try:
        return base64.b64decode(str(result["content"]), validate=False)
    except (KeyError, ValueError) as error:
        raise GitHubApiError("GitHub returned invalid file content for {}".format(path)) from error


def _object_sha(ref: Mapping[str, Any]) -> str:
    value = ref.get("object")
    if not isinstance(value, dict) or not isinstance(value.get("sha"), str):
        raise GitHubApiError("GitHub branch data did not include a commit SHA")
    return value["sha"]


def _raw_url(repository: str, branch: str, path: str) -> str:
    owner, name = parse_repository(repository)
    return "https://raw.githubusercontent.com/{}/{}/{}/{}".format(
        urllib.parse.quote(owner, safe=""),
        urllib.parse.quote(name, safe=""),
        urllib.parse.quote(branch, safe="/"),
        urllib.parse.quote(path, safe="/"),
    )


def publish_snapshot(
    client: GitHubClient,
    snapshot: StarSnapshot,
    *,
    branch: str,
    light_path: str,
    dark_path: str,
    commit_message: str,
) -> PublishResult:
    branch = validate_branch(branch)
    light_path = validate_svg_path(light_path)
    dark_path = validate_svg_path(dark_path)
    if light_path == dark_path:
        raise ValueError("light and dark output paths must be different")
    owner, repository_name = parse_repository(snapshot.repository)
    light = render_svg(snapshot, "light").encode("utf-8")
    dark = render_svg(snapshot, "dark").encode("utf-8")
    output_ref = _get_ref(client, owner, repository_name, branch)
    if output_ref is not None:
        current_light = _get_file(
            client, owner, repository_name, branch, light_path
        )
        current_dark = _get_file(client, owner, repository_name, branch, dark_path)
        if current_light == light and current_dark == dark:
            return PublishResult(
                changed=False,
                star_count=snapshot.star_count,
                branch=branch,
                light_url=_raw_url(snapshot.repository, branch, light_path),
                dark_url=_raw_url(snapshot.repository, branch, dark_path),
            )
        base_commit_sha = _object_sha(output_ref)
    else:
        metadata = _fetch_repository_metadata(client, owner, repository_name)
        default_branch = metadata.get("default_branch")
        if not isinstance(default_branch, str):
            raise GitHubApiError("GitHub repository metadata did not include a default branch")
        default_ref = _get_ref(client, owner, repository_name, default_branch)
        if default_ref is None:
            raise GitHubApiError("The repository default branch does not exist")
        base_commit_sha = _object_sha(default_ref)

    commit, _, _ = client.request(
        "GET",
        "{}/git/commits/{}".format(
            _repo_path(owner, repository_name),
            urllib.parse.quote(base_commit_sha, safe=""),
        ),
    )
    if not isinstance(commit, dict) or not isinstance(commit.get("tree"), dict):
        raise GitHubApiError("GitHub returned invalid commit data")
    base_tree_sha = commit["tree"].get("sha")
    if not isinstance(base_tree_sha, str):
        raise GitHubApiError("GitHub commit data did not include a tree SHA")

    tree_entries = []
    for path, content in ((light_path, light), (dark_path, dark)):
        blob, _, _ = client.request(
            "POST",
            "{}/git/blobs".format(_repo_path(owner, repository_name)),
            payload={"content": content.decode("utf-8"), "encoding": "utf-8"},
        )
        if not isinstance(blob, dict) or not isinstance(blob.get("sha"), str):
            raise GitHubApiError("GitHub did not create the {} blob".format(path))
        tree_entries.append(
            {"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]}
        )
    tree, _, _ = client.request(
        "POST",
        "{}/git/trees".format(_repo_path(owner, repository_name)),
        payload={"base_tree": base_tree_sha, "tree": tree_entries},
    )
    if not isinstance(tree, dict) or not isinstance(tree.get("sha"), str):
        raise GitHubApiError("GitHub did not create the output tree")
    new_commit, _, _ = client.request(
        "POST",
        "{}/git/commits".format(_repo_path(owner, repository_name)),
        payload={
            "message": commit_message,
            "tree": tree["sha"],
            "parents": [base_commit_sha],
        },
    )
    if not isinstance(new_commit, dict) or not isinstance(new_commit.get("sha"), str):
        raise GitHubApiError("GitHub did not create the output commit")
    if output_ref is None:
        client.request(
            "POST",
            "{}/git/refs".format(_repo_path(owner, repository_name)),
            payload={"ref": "refs/heads/" + branch, "sha": new_commit["sha"]},
        )
    else:
        client.request(
            "PATCH",
            "{}/git/refs/heads/{}".format(
                _repo_path(owner, repository_name),
                urllib.parse.quote(branch, safe="/"),
            ),
            payload={"sha": new_commit["sha"], "force": False},
        )
    return PublishResult(
        changed=True,
        star_count=snapshot.star_count,
        branch=branch,
        light_url=_raw_url(snapshot.repository, branch, light_path),
        dark_url=_raw_url(snapshot.repository, branch, dark_path),
    )


def _write_github_outputs(path: str, result: PublishResult) -> None:
    values = {
        "changed": str(result.changed).lower(),
        "star_count": str(result.star_count),
        "branch": result.branch,
        "light_url": result.light_url,
        "dark_url": result.dark_url,
    }
    with open(path, "a", encoding="utf-8", newline="\n") as output:
        for key, value in values.items():
            output.write("{}={}\n".format(key, value))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish deterministic GitHub star history SVGs to a dedicated branch."
    )
    parser.add_argument(
        "--repository", default=os.environ.get("GITHUB_REPOSITORY", ""), help="OWNER/REPOSITORY"
    )
    parser.add_argument("--branch", default="star-history")
    parser.add_argument("--light-path", default="star-history.svg")
    parser.add_argument("--dark-path", default="star-history-dark.svg")
    parser.add_argument("--commit-message", default="chore: update star history")
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        repository = "/".join(parse_repository(arguments.repository))
        token = os.environ.get(arguments.token_env, "")
        client = GitHubClient(token, arguments.api_url)
        snapshot = fetch_snapshot(client, repository)
        result = publish_snapshot(
            client,
            snapshot,
            branch=arguments.branch,
            light_path=arguments.light_path,
            dark_path=arguments.dark_path,
            commit_message="{} ({} stars)".format(
                arguments.commit_message, snapshot.star_count
            ),
        )
        if arguments.github_output:
            _write_github_outputs(arguments.github_output, result)
        print(
            json.dumps(
                {
                    "changed": result.changed,
                    "star_count": result.star_count,
                    "branch": result.branch,
                    "light_url": result.light_url,
                    "dark_url": result.dark_url,
                },
                sort_keys=True,
            )
        )
        return 0
    except (GitHubApiError, ValueError) as error:
        print("error: {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
