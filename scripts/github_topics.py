#!/usr/bin/env python3
"""Inspect, replace, and verify GitHub repository Topics through ``gh``."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Callable, Mapping, Sequence


API_ACCEPT = "application/vnd.github+json"
API_VERSION = "2022-11-28"
TOPIC = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,48}[a-z0-9])?")
COMMIT_SHA = re.compile(r"[0-9a-f]{40}")
TOPIC_LINK = re.compile(r"href=[\"']/topics/([^\"'?#]+)", re.I)
USER_AGENT = "project-steward-github-topics/1"


class TopicsError(RuntimeError):
    """A safe operational error from the Topics transaction."""


@dataclass(frozen=True)
class RepositorySnapshot:
    repository: str
    visibility: str
    default_branch: str
    head: str
    topics: tuple[str, ...]
    can_push: bool


@dataclass(frozen=True)
class ApplyResult:
    action: str
    repository: str
    visibility: str
    default_branch: str
    head: str
    previous_topics: tuple[str, ...]
    target_topics: tuple[str, ...]
    topics: tuple[str, ...]
    changed: bool
    api_verified: bool
    homepage_topics: tuple[str, ...]
    homepage_verified: bool
    verified: bool


class GhClient:
    """Use the authenticated GitHub CLI without reading or printing its token."""

    def __init__(self, executable: str = "gh") -> None:
        self._executable = executable

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        command = [
            self._executable,
            "api",
            "--method",
            method,
            endpoint,
            "-H",
            "Accept: {}".format(API_ACCEPT),
            "-H",
            "X-GitHub-Api-Version: {}".format(API_VERSION),
        ]
        request_body = None
        if payload is not None:
            command.extend(("--input", "-"))
            request_body = json.dumps(
                payload,
                ensure_ascii=True,
                separators=(",", ":"),
            )
        try:
            completed = subprocess.run(
                command,
                input=request_body,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except FileNotFoundError as error:
            raise TopicsError(
                "GitHub CLI was not found; install and authenticate gh first"
            ) from error
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            if len(detail) > 600:
                detail = detail[:600] + "..."
            raise TopicsError(
                "gh api failed for {} {}: {}".format(
                    method,
                    endpoint,
                    detail or "unknown error",
                )
            )
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise TopicsError(
                "gh api returned invalid JSON for {} {}".format(method, endpoint)
            ) from error


def parse_repository(value: str) -> tuple[str, str]:
    parts = value.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("repository must use the OWNER/REPOSITORY form")
    if any(any(character in part for character in "\r\n?#%") for part in parts):
        raise ValueError("repository contains unsupported characters")
    return parts[0], parts[1]


def validate_head(value: str) -> str:
    normalized = value.strip().lower()
    if not COMMIT_SHA.fullmatch(normalized):
        raise ValueError("expected head must be a full 40-character commit SHA")
    return normalized


def validate_topics(values: Sequence[str]) -> tuple[str, ...]:
    if not values:
        raise ValueError("at least one final topic is required")
    if len(values) > 20:
        raise ValueError("GitHub accepts at most 20 repository topics")
    topics = tuple(values)
    for topic in topics:
        if not TOPIC.fullmatch(topic):
            raise ValueError(
                "topic {!r} must be canonical lowercase letters, numbers, or hyphens "
                "and contain at most 50 characters".format(topic)
            )
    if len(set(topics)) != len(topics):
        raise ValueError("final topics must not contain duplicates")
    return tuple(sorted(topics))


def _repository_endpoint(repository: str, suffix: str = "") -> str:
    owner, name = parse_repository(repository)
    root = "repos/{}/{}".format(
        urllib.parse.quote(owner, safe=""),
        urllib.parse.quote(name, safe=""),
    )
    return root + suffix


def _string_field(source: Mapping[str, Any], key: str, context: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise TopicsError("GitHub returned invalid {} {}".format(context, key))
    return value


def inspect_repository(client: GhClient, repository: str) -> RepositorySnapshot:
    requested = "/".join(parse_repository(repository))
    metadata = client.request("GET", _repository_endpoint(requested))
    if not isinstance(metadata, dict):
        raise TopicsError("GitHub returned invalid repository metadata")
    full_name = _string_field(metadata, "full_name", "repository")
    if full_name.casefold() != requested.casefold():
        raise TopicsError(
            "GitHub resolved {} to unexpected repository {}".format(
                requested, full_name
            )
        )
    visibility = metadata.get("visibility")
    if not isinstance(visibility, str):
        private = metadata.get("private")
        if not isinstance(private, bool):
            raise TopicsError("GitHub returned invalid repository visibility")
        visibility = "private" if private else "public"
    default_branch = _string_field(metadata, "default_branch", "repository")
    encoded_branch = urllib.parse.quote(default_branch, safe="")
    commit = client.request(
        "GET",
        _repository_endpoint(full_name, "/commits/{}".format(encoded_branch)),
    )
    if not isinstance(commit, dict):
        raise TopicsError("GitHub returned invalid default-branch commit data")
    head = _string_field(commit, "sha", "default-branch commit").lower()
    if not COMMIT_SHA.fullmatch(head):
        raise TopicsError("GitHub returned an invalid default-branch commit SHA")
    response = client.request("GET", _repository_endpoint(full_name, "/topics"))
    if not isinstance(response, dict) or not isinstance(response.get("names"), list):
        raise TopicsError("GitHub returned invalid Topics data")
    try:
        topics = validate_topics(response["names"]) if response["names"] else ()
    except ValueError as error:
        raise TopicsError("GitHub returned non-canonical Topics: {}".format(error)) from error
    permissions = metadata.get("permissions")
    can_push = False
    if isinstance(permissions, dict):
        can_push = any(
            permissions.get(permission) is True
            for permission in ("push", "maintain", "admin")
        )
    return RepositorySnapshot(
        repository=full_name,
        visibility=visibility,
        default_branch=default_branch,
        head=head,
        topics=topics,
        can_push=can_push,
    )


def extract_homepage_topics(source: str) -> tuple[str, ...]:
    topics = {
        urllib.parse.unquote(html.unescape(match)).casefold()
        for match in TOPIC_LINK.findall(source)
    }
    return tuple(sorted(topic for topic in topics if TOPIC.fullmatch(topic)))


def load_homepage(repository: str, *, timeout: float = 30.0) -> str:
    owner, name = parse_repository(repository)
    url = "https://github.com/{}/{}".format(
        urllib.parse.quote(owner, safe=""),
        urllib.parse.quote(name, safe=""),
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as error:
        raise TopicsError("could not read the GitHub repository homepage: {}".format(error)) from error


def verify_homepage_topics(
    repository: str,
    expected: tuple[str, ...],
    *,
    attempts: int,
    delay: float,
    loader: Callable[[str], str] = load_homepage,
) -> tuple[str, ...]:
    if attempts < 1:
        raise ValueError("homepage attempts must be at least 1")
    if delay < 0:
        raise ValueError("homepage delay cannot be negative")
    observed: tuple[str, ...] = ()
    for attempt in range(attempts):
        observed = extract_homepage_topics(loader(repository))
        if observed == expected:
            return observed
        if attempt + 1 < attempts:
            time.sleep(delay)
    raise TopicsError(
        "GitHub homepage Topics did not match the API result: expected {}, observed {}".format(
            list(expected), list(observed)
        )
    )


def apply_topics(
    client: GhClient,
    repository: str,
    topics: Sequence[str],
    *,
    expected_head: str,
    homepage_attempts: int = 6,
    homepage_delay: float = 2.0,
    homepage_loader: Callable[[str], str] = load_homepage,
) -> ApplyResult:
    target = validate_topics(topics)
    expected = validate_head(expected_head)
    before = inspect_repository(client, repository)
    if before.visibility != "public":
        raise TopicsError("README Topics automation only applies to public repositories")
    if not before.can_push:
        raise TopicsError("the authenticated GitHub identity lacks repository write permission")
    if before.head != expected:
        raise TopicsError(
            "default-branch HEAD changed before Topics write: expected {}, observed {}".format(
                expected, before.head
            )
        )
    changed = before.topics != target
    if changed:
        response = client.request(
            "PUT",
            _repository_endpoint(before.repository, "/topics"),
            payload={"names": list(target)},
        )
        if not isinstance(response, dict) or not isinstance(response.get("names"), list):
            raise TopicsError("GitHub returned invalid Topics data after replacement")

    after = inspect_repository(client, before.repository)
    if after.default_branch != before.default_branch or after.head != expected:
        raise TopicsError(
            "default-branch identity changed during Topics verification; re-derive the final set"
        )
    if after.topics != target:
        raise TopicsError(
            "GitHub Topics readback mismatch: expected {}, observed {}".format(
                list(target), list(after.topics)
            )
        )
    homepage_topics = verify_homepage_topics(
        after.repository,
        target,
        attempts=homepage_attempts,
        delay=homepage_delay,
        loader=homepage_loader,
    )
    return ApplyResult(
        action="apply",
        repository=after.repository,
        visibility=after.visibility,
        default_branch=after.default_branch,
        head=after.head,
        previous_topics=before.topics,
        target_topics=target,
        topics=after.topics,
        changed=changed,
        api_verified=True,
        homepage_topics=homepage_topics,
        homepage_verified=True,
        verified=True,
    )


def _snapshot_output(snapshot: RepositorySnapshot) -> dict[str, Any]:
    return {
        "action": "inspect",
        "repository": snapshot.repository,
        "visibility": snapshot.visibility,
        "default_branch": snapshot.default_branch,
        "head": snapshot.head,
        "topics": list(snapshot.topics),
        "can_push": snapshot.can_push,
    }


def _result_output(result: ApplyResult) -> dict[str, Any]:
    output = asdict(result)
    for key in ("previous_topics", "target_topics", "topics", "homepage_topics"):
        output[key] = list(output[key])
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser(
        "inspect", help="read repository identity, default-branch HEAD, and current Topics"
    )
    inspect_parser.add_argument("--repository", required=True, help="OWNER/REPOSITORY")
    apply_parser = subparsers.add_parser(
        "apply", help="replace Topics once, read them back, and verify the GitHub homepage"
    )
    apply_parser.add_argument("--repository", required=True, help="OWNER/REPOSITORY")
    apply_parser.add_argument(
        "--expected-head",
        required=True,
        help="full default-branch commit SHA observed after README publication",
    )
    apply_parser.add_argument(
        "--topic",
        action="append",
        required=True,
        help="one project-fact-derived final Topic; repeat for the complete set",
    )
    apply_parser.add_argument("--homepage-attempts", type=int, default=6)
    apply_parser.add_argument("--homepage-delay", type=float, default=2.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    client = GhClient()
    try:
        if arguments.command == "inspect":
            output = _snapshot_output(inspect_repository(client, arguments.repository))
        else:
            output = _result_output(
                apply_topics(
                    client,
                    arguments.repository,
                    arguments.topic,
                    expected_head=arguments.expected_head,
                    homepage_attempts=arguments.homepage_attempts,
                    homepage_delay=arguments.homepage_delay,
                )
            )
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (TopicsError, ValueError) as error:
        print("error: {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
