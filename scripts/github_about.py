#!/usr/bin/env python3
"""Update and verify GitHub About metadata without qualifying Website targets."""

from __future__ import annotations

import argparse
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
COMMIT_SHA = re.compile(r"[0-9a-f]{40}")
ABOUT_MARKER = '"sidebarAbout":'
USER_AGENT = "project-steward-github-about/1"


class AboutError(RuntimeError):
    """A safe operational error from the About metadata transaction."""


@dataclass(frozen=True)
class RepositorySnapshot:
    repository: str
    visibility: str
    default_branch: str
    head: str
    description: str
    website: str
    can_push: bool


@dataclass(frozen=True)
class ApplyResult:
    action: str
    repository: str
    visibility: str
    default_branch: str
    head: str
    previous_description: str
    target_description: str
    description: str
    previous_website: str
    target_website: str
    website: str
    changed: bool
    api_verified: bool
    github_page_description: str
    github_page_website: str
    github_page_verified: bool
    website_destination_validation: str
    metadata_verified: bool


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
            raise AboutError(
                "GitHub CLI was not found; install and authenticate gh first"
            ) from error
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            if len(detail) > 600:
                detail = detail[:600] + "..."
            raise AboutError(
                "gh api failed for {} {}: {}".format(
                    method,
                    endpoint,
                    detail or "unknown error",
                )
            )
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise AboutError(
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


def validate_description(value: str) -> str:
    if any(ord(character) < 32 for character in value):
        raise ValueError("description must be single-line plain text")
    normalized = value.strip()
    if not normalized:
        raise ValueError("description must be a non-empty public definition")
    return normalized


def validate_website(value: str) -> str:
    if any(character.isspace() for character in value):
        raise ValueError("website contains unsupported whitespace")
    normalized = value.strip()
    if not normalized:
        raise ValueError("website must be a non-empty URL; use clear-website instead")
    try:
        parsed = urllib.parse.urlsplit(normalized)
        _ = parsed.port
    except ValueError as error:
        raise ValueError("website is not a valid URL") from error
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("website must be an absolute http or https URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("website must not contain credentials")
    return normalized


def _repository_endpoint(repository: str, suffix: str = "") -> str:
    owner, name = parse_repository(repository)
    root = "repos/{}/{}".format(
        urllib.parse.quote(owner, safe=""),
        urllib.parse.quote(name, safe=""),
    )
    return root + suffix


def _required_string(source: Mapping[str, Any], key: str, context: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise AboutError("GitHub returned invalid {} {}".format(context, key))
    return value


def _optional_string(source: Mapping[str, Any], key: str, context: str) -> str:
    value = source.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise AboutError("GitHub returned invalid {} {}".format(context, key))
    return value


def inspect_repository(client: GhClient, repository: str) -> RepositorySnapshot:
    requested = "/".join(parse_repository(repository))
    metadata = client.request("GET", _repository_endpoint(requested))
    if not isinstance(metadata, dict):
        raise AboutError("GitHub returned invalid repository metadata")
    full_name = _required_string(metadata, "full_name", "repository")
    if full_name.casefold() != requested.casefold():
        raise AboutError(
            "GitHub resolved {} to unexpected repository {}".format(
                requested,
                full_name,
            )
        )
    visibility = metadata.get("visibility")
    if not isinstance(visibility, str):
        private = metadata.get("private")
        if not isinstance(private, bool):
            raise AboutError("GitHub returned invalid repository visibility")
        visibility = "private" if private else "public"
    default_branch = _required_string(metadata, "default_branch", "repository")
    encoded_branch = urllib.parse.quote(default_branch, safe="")
    commit = client.request(
        "GET",
        _repository_endpoint(full_name, "/commits/{}".format(encoded_branch)),
    )
    if not isinstance(commit, dict):
        raise AboutError("GitHub returned invalid default-branch commit data")
    head = _required_string(commit, "sha", "default-branch commit").lower()
    if not COMMIT_SHA.fullmatch(head):
        raise AboutError("GitHub returned an invalid default-branch commit SHA")
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
        description=_optional_string(metadata, "description", "repository"),
        website=_optional_string(metadata, "homepage", "repository"),
        can_push=can_push,
    )


def extract_homepage_about(source: str) -> tuple[str, str]:
    marker_index = source.find(ABOUT_MARKER)
    if marker_index < 0:
        raise AboutError("GitHub homepage did not expose repository About data")
    value_index = marker_index + len(ABOUT_MARKER)
    try:
        payload, _ = json.JSONDecoder().raw_decode(source, value_index)
    except json.JSONDecodeError as error:
        raise AboutError("GitHub homepage exposed invalid About data") from error
    if not isinstance(payload, dict):
        raise AboutError("GitHub homepage exposed invalid About data")
    description = payload.get("description")
    website = payload.get("website")
    if description is None:
        description = ""
    if website is None:
        website = ""
    if not isinstance(description, str) or not isinstance(website, str):
        raise AboutError("GitHub homepage exposed invalid About fields")
    return description, website


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
        raise AboutError(
            "could not read the GitHub repository homepage: {}".format(error)
        ) from error


def verify_homepage_about(
    repository: str,
    expected_description: str,
    expected_website: str,
    *,
    attempts: int,
    delay: float,
    loader: Callable[[str], str] = load_homepage,
) -> tuple[str, str]:
    if attempts < 1:
        raise ValueError("homepage attempts must be at least 1")
    if delay < 0:
        raise ValueError("homepage delay cannot be negative")
    observed = ("", "")
    for attempt in range(attempts):
        observed = extract_homepage_about(loader(repository))
        if observed == (expected_description, expected_website):
            return observed
        if attempt + 1 < attempts:
            time.sleep(delay)
    raise AboutError(
        "GitHub homepage About did not match the API result: expected {!r}, observed {!r}".format(
            (expected_description, expected_website),
            observed,
        )
    )


def apply_about(
    client: GhClient,
    repository: str,
    description: str,
    website: str,
    *,
    expected_head: str,
    homepage_attempts: int = 6,
    homepage_delay: float = 2.0,
    homepage_loader: Callable[[str], str] = load_homepage,
) -> ApplyResult:
    target_description = validate_description(description)
    target_website = validate_website(website) if website else ""
    expected = validate_head(expected_head)
    before = inspect_repository(client, repository)
    if before.visibility != "public":
        raise AboutError("README About automation only applies to public repositories")
    if not before.can_push:
        raise AboutError("the authenticated GitHub identity lacks repository write permission")
    if before.head != expected:
        raise AboutError(
            "default-branch HEAD changed before About write: expected {}, observed {}".format(
                expected,
                before.head,
            )
        )
    changed = (
        before.description != target_description or before.website != target_website
    )
    if changed:
        response = client.request(
            "PATCH",
            _repository_endpoint(before.repository),
            payload={
                "description": target_description,
                "homepage": target_website,
            },
        )
        if not isinstance(response, dict):
            raise AboutError("GitHub returned invalid repository metadata after update")

    after = inspect_repository(client, before.repository)
    if after.default_branch != before.default_branch or after.head != expected:
        raise AboutError(
            "default-branch identity changed during About verification; re-derive the target values"
        )
    if after.description != target_description or after.website != target_website:
        raise AboutError(
            "GitHub About readback mismatch: expected {!r}, observed {!r}".format(
                (target_description, target_website),
                (after.description, after.website),
            )
        )
    homepage_description, homepage_website = verify_homepage_about(
        after.repository,
        target_description,
        target_website,
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
        previous_description=before.description,
        target_description=target_description,
        description=after.description,
        previous_website=before.website,
        target_website=target_website,
        website=after.website,
        changed=changed,
        api_verified=True,
        github_page_description=homepage_description,
        github_page_website=homepage_website,
        github_page_verified=True,
        website_destination_validation=(
            "caller_qualified_not_checked" if target_website else "not_applicable"
        ),
        metadata_verified=True,
    )


def _snapshot_output(snapshot: RepositorySnapshot) -> dict[str, Any]:
    output = asdict(snapshot)
    output["action"] = "inspect"
    return output


def _result_output(result: ApplyResult) -> dict[str, Any]:
    return asdict(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="read repository identity, default-branch HEAD, and current About fields",
    )
    inspect_parser.add_argument("--repository", required=True, help="OWNER/REPOSITORY")
    apply_parser = subparsers.add_parser(
        "apply",
        help=(
            "update Description and Website once, then verify the API and "
            "GitHub repository page; Website qualification remains caller-owned"
        ),
    )
    apply_parser.add_argument("--repository", required=True, help="OWNER/REPOSITORY")
    apply_parser.add_argument(
        "--expected-head",
        required=True,
        help="full default-branch commit SHA observed after README publication",
    )
    apply_parser.add_argument(
        "--description",
        required=True,
        help="project-fact-derived single-line public definition",
    )
    website_group = apply_parser.add_mutually_exclusive_group(required=True)
    website_group.add_argument(
        "--website",
        help=(
            "official public project URL already qualified by the caller; "
            "this tool does not open or validate the destination"
        ),
    )
    website_group.add_argument(
        "--clear-website",
        action="store_true",
        help="explicitly keep Website empty or clear a stale value",
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
            target_website = "" if arguments.clear_website else arguments.website
            output = _result_output(
                apply_about(
                    client,
                    arguments.repository,
                    arguments.description,
                    target_website,
                    expected_head=arguments.expected_head,
                    homepage_attempts=arguments.homepage_attempts,
                    homepage_delay=arguments.homepage_delay,
                )
            )
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (AboutError, ValueError) as error:
        print("error: {}".format(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
