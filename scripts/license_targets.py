"""Local and GitHub target operations for approved license plans."""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote

from license_content import (
    GIT_HASH_PATTERN,
    HASH_PATTERN,
    PLAN_VERSION,
    REPOSITORY_PATTERN,
    PlannedAction,
    PreparedProject,
    fail,
    git_blob_sha,
    render_source,
    resolve_governance_path,
    resolve_local_file,
    sha256_bytes,
    validate_common_fields,
)


def parse_actions(
    project: dict,
    values: dict[str, str],
    catalog: dict,
    catalog_path: Path,
) -> list[PlannedAction]:
    raw_files = project.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        fail("an apply project must contain a non-empty files array")
    actions: list[PlannedAction] = []
    occupied: set[str] = set()
    for raw in raw_files:
        if not isinstance(raw, dict):
            fail("every files entry must be an object")
        path = resolve_governance_path(raw.get("path"))
        action = raw.get("action")
        if action not in {"create", "replace-preserve"}:
            fail(f"unsupported file action for {path}: {action!r}")
        expected_hash: str | None = None
        preserve_as: str | None = None
        if action == "replace-preserve":
            expected_hash = raw.get("expected_sha256")
            if not isinstance(expected_hash, str) or not HASH_PATTERN.fullmatch(
                expected_hash
            ):
                fail(f"{path} replace-preserve needs a 64-character expected_sha256")
            expected_hash = expected_hash.lower()
            preserve_as = resolve_governance_path(raw.get("preserve_as"))
            if preserve_as.casefold() == path.casefold():
                fail(f"{path} cannot preserve its history over itself")
        elif raw.get("expected_sha256") is not None or raw.get("preserve_as") is not None:
            fail(f"{path} create cannot declare expected_sha256 or preserve_as")

        for occupied_path in [path, *([preserve_as] if preserve_as else [])]:
            key = occupied_path.casefold()
            if key in occupied:
                fail(f"duplicate planned path: {occupied_path}")
            occupied.add(key)
        actions.append(
            PlannedAction(
                path=path,
                action=action,
                rendered=render_source(
                    raw.get("source"), values, catalog, catalog_path
                ),
                expected_sha256=expected_hash,
                preserve_as=preserve_as,
            )
        )
    required_gnu_notices: set[tuple[str, str]] = set()
    declared_gnu_notices: set[tuple[str, str]] = set()
    for raw in raw_files:
        source = raw.get("source")
        if not isinstance(source, dict):
            continue
        source_kind = source.get("kind")
        source_id = source.get("id")
        if source_kind == "catalog-license" and isinstance(source_id, str):
            entry = catalog["licenses"].get(source_id)
            if isinstance(entry, dict) and entry.get("gnu_notice_mode"):
                required_gnu_notices.add(
                    (source_id, resolve_governance_path(raw.get("path")))
                )
        elif source_kind == "gnu-notice" and isinstance(source_id, str):
            declared_gnu_notices.add(
                (
                    source_id,
                    resolve_governance_path(source.get("license_path")),
                )
            )
    missing_notices = sorted(required_gnu_notices - declared_gnu_notices)
    if missing_notices:
        rendered_missing = ", ".join(
            f"{license_id} for {license_path}"
            for license_id, license_path in missing_notices
        )
        fail(
            "GNU catalog licenses require matching gnu-notice actions: "
            + rendered_missing
        )
    return actions


def run_git(root: Path, *arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            capture_output=True,
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.rstrip("\r\n")


def require_authenticated_gh() -> None:
    if shutil.which("gh") is None:
        fail("GitHub CLI 'gh' is not installed; this script does not install tools")
    completed = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        fail(
            "GitHub CLI is not authenticated; authenticate it outside this script. "
            f"Details: {detail}"
        )


def gh_api(
    endpoint: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    allow_not_found: bool = False,
) -> object | None:
    arguments = ["gh", "api", "--method", method, endpoint]
    input_text: str | None = None
    if payload is not None:
        arguments.extend(["--input", "-"])
        input_text = json.dumps(payload, ensure_ascii=False)
    completed = subprocess.run(
        arguments,
        input=input_text,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        if allow_not_found and any(
            marker in detail for marker in ("HTTP 404", "HTTP 409", "Not Found")
        ):
            return None
        fail(f"GitHub API {method} {endpoint} failed: {detail}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        fail(f"GitHub API returned invalid JSON for {method} {endpoint}: {exc}")


def github_state(
    repository: str, branch: str, requested_paths: set[str]
) -> tuple[str, str, dict[str, bytes]]:
    encoded_branch = quote(branch, safe="")
    reference = gh_api(f"repos/{repository}/git/ref/heads/{encoded_branch}")
    if not isinstance(reference, dict) or not isinstance(reference.get("object"), dict):
        fail(f"cannot resolve {repository} branch {branch}")
    head = reference["object"].get("sha")
    if not isinstance(head, str):
        fail(f"cannot resolve {repository} branch HEAD")
    commit = gh_api(f"repos/{repository}/git/commits/{head}")
    if not isinstance(commit, dict) or not isinstance(commit.get("tree"), dict):
        fail(f"cannot resolve {repository} commit tree")
    tree_sha = commit["tree"].get("sha")
    if not isinstance(tree_sha, str):
        fail(f"cannot resolve {repository} tree SHA")
    tree = gh_api(f"repos/{repository}/git/trees/{tree_sha}?recursive=1")
    if not isinstance(tree, dict) or not isinstance(tree.get("tree"), list):
        fail(f"cannot read {repository} tree")
    if tree.get("truncated"):
        fail(f"{repository} Git tree is truncated; use a narrower manual preflight")
    entries = {
        item["path"]: item
        for item in tree["tree"]
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    existing: dict[str, bytes] = {}
    for path in requested_paths:
        entry = entries.get(path)
        if entry is None:
            continue
        if (
            entry.get("type") != "blob"
            or entry.get("mode") not in {"100644", "100755"}
            or not isinstance(entry.get("sha"), str)
        ):
            fail(f"{repository}:{path} exists but is not a regular file")
        blob = gh_api(f"repos/{repository}/git/blobs/{entry['sha']}")
        if (
            not isinstance(blob, dict)
            or blob.get("encoding") != "base64"
            or not isinstance(blob.get("content"), str)
        ):
            fail(f"cannot read exact blob bytes for {repository}:{path}")
        try:
            existing[path] = base64.b64decode(blob["content"], validate=False)
        except (ValueError, TypeError) as exc:
            fail(f"invalid base64 blob for {repository}:{path}: {exc}")
    return head, tree_sha, existing


def local_state(
    root: Path, requested_paths: set[str]
) -> tuple[str | None, dict[str, bytes]]:
    existing: dict[str, bytes] = {}
    for relative in requested_paths:
        cursor = root
        for part in relative.split("/"):
            cursor = cursor / part
            if cursor.is_symlink():
                fail(f"local governance path uses a symlink: {relative}")
        target = resolve_local_file(root, relative)
        if target.exists():
            if not target.is_file():
                fail(f"local governance target is not a regular file: {target}")
            existing[relative] = target.read_bytes()
        elif not target.parent.is_dir():
            fail(f"local governance parent directory does not exist: {target.parent}")
    return run_git(root, "rev-parse", "HEAD"), existing


def requested_paths(actions: list[PlannedAction]) -> set[str]:
    return {
        path
        for action in actions
        for path in [action.path, *([action.preserve_as] if action.preserve_as else [])]
    }


def check_action_state(
    target_label: str,
    actions: list[PlannedAction],
    existing: dict[str, bytes],
    operation: str,
) -> None:
    for action in actions:
        target_content = existing.get(action.path)
        if operation == "verify":
            if target_content is None:
                fail(f"verification target is missing: {target_label}:{action.path}")
            actual = sha256_bytes(target_content)
            expected = sha256_bytes(action.rendered.content)
            if actual != expected:
                fail(
                    f"verification hash mismatch for {target_label}:{action.path}: "
                    f"expected {expected}, got {actual}"
                )
            if action.action == "replace-preserve":
                historical = existing.get(str(action.preserve_as))
                if historical is None:
                    fail(
                        f"historical license is missing: "
                        f"{target_label}:{action.preserve_as}"
                    )
                actual_historical = sha256_bytes(historical)
                if actual_historical != action.expected_sha256:
                    fail(
                        f"historical hash mismatch for "
                        f"{target_label}:{action.preserve_as}: expected "
                        f"{action.expected_sha256}, got {actual_historical}"
                    )
            continue

        if action.action == "create":
            if target_content is not None:
                fail(f"create target already exists: {target_label}:{action.path}")
            continue
        if target_content is None:
            fail(f"replace target is missing: {target_label}:{action.path}")
        actual = sha256_bytes(target_content)
        if actual != action.expected_sha256:
            fail(
                f"replace precondition failed for {target_label}:{action.path}: "
                f"expected {action.expected_sha256}, got {actual}"
            )
        if str(action.preserve_as) in existing:
            fail(
                f"historical preservation target already exists: "
                f"{target_label}:{action.preserve_as}"
            )


def validate_line(value: object, label: str, *, required: bool = True) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        fail(f"{label} must be one non-empty line")
    return value.strip()


def prepare_projects(
    plan: dict,
    catalog: dict,
    catalog_path: Path,
    plan_path: Path,
    operation: str,
) -> list[PreparedProject]:
    if plan.get("schema_version") != PLAN_VERSION:
        fail(f"plan schema_version must be {PLAN_VERSION}")
    raw_projects = plan.get("projects")
    if not isinstance(raw_projects, list) or not raw_projects:
        fail("plan.projects must be a non-empty array")

    github_needed = any(
        isinstance(project, dict)
        and isinstance(project.get("target"), dict)
        and project["target"].get("kind") == "github"
        for project in raw_projects
    )
    if github_needed:
        require_authenticated_gh()

    prepared: list[PreparedProject] = []
    project_ids: set[str] = set()
    target_ids: set[str] = set()
    base_directory = Path.cwd() if str(plan_path) == "-" else plan_path.parent
    for raw_project in raw_projects:
        if not isinstance(raw_project, dict):
            fail("every projects entry must be an object")
        project_id = validate_line(raw_project.get("id"), "project id")
        assert project_id is not None
        if project_id.casefold() in project_ids:
            fail(f"duplicate project id: {project_id}")
        project_ids.add(project_id.casefold())
        disposition = raw_project.get("disposition")
        if disposition not in {"apply", "retain"}:
            fail(f"{project_id} disposition must be apply or retain")
        reason = validate_line(raw_project.get("reason"), f"{project_id} reason")
        assert reason is not None
        raw_target = raw_project.get("target")
        if not isinstance(raw_target, dict):
            fail(f"{project_id} target must be an object")
        target_kind = raw_target.get("kind")
        if target_kind not in {"local", "github"}:
            fail(f"{project_id} target.kind must be local or github")

        if disposition == "retain":
            raw_files = raw_project.get("files", [])
            if raw_files not in (None, []):
                fail(f"{project_id} retain projects cannot contain file actions")
            actions: list[PlannedAction] = []
        else:
            values = validate_common_fields(raw_project)
            actions = parse_actions(raw_project, values, catalog, catalog_path)

        paths = requested_paths(actions)
        root: Path | None = None
        repository: str | None = None
        branch: str | None = None
        base_tree: str | None = None
        expected_result_head = raw_target.get("expected_result_head")
        if expected_result_head is not None and (
            not isinstance(expected_result_head, str)
            or not GIT_HASH_PATTERN.fullmatch(expected_result_head)
        ):
            fail(f"{project_id} expected_result_head is invalid")

        if target_kind == "local":
            raw_path = raw_target.get("path")
            if not isinstance(raw_path, str) or not raw_path.strip():
                fail(f"{project_id} local target needs path")
            candidate = Path(raw_path).expanduser()
            if not candidate.is_absolute():
                candidate = base_directory / candidate
            root = candidate.resolve()
            if not root.is_dir():
                fail(f"{project_id} local target directory not found: {root}")
            target_label = str(root)
            target_key = f"local:{str(root).casefold()}"
            base_head, existing = local_state(root, paths)
            expected_head = raw_target.get("expected_head")
            if expected_head is not None and (
                not isinstance(expected_head, str)
                or not GIT_HASH_PATTERN.fullmatch(expected_head)
            ):
                fail(f"{project_id} expected_head is invalid")
            if operation != "verify" and expected_head is not None and base_head != expected_head:
                fail(
                    f"{project_id} local HEAD changed: expected {expected_head}, "
                    f"got {base_head}"
                )
        else:
            repository = raw_target.get("repository")
            if not isinstance(repository, str) or not REPOSITORY_PATTERN.fullmatch(
                repository
            ):
                fail(f"{project_id} github target needs owner/repository")
            expected_visibility = raw_target.get("expected_visibility")
            if expected_visibility not in {"public", "private", "internal"}:
                fail(
                    f"{project_id} GitHub target needs expected_visibility "
                    "public, private, or internal"
                )
            expected_is_fork = raw_target.get("expected_is_fork")
            if not isinstance(expected_is_fork, bool):
                fail(f"{project_id} GitHub target needs boolean expected_is_fork")
            metadata = gh_api(f"repos/{repository}")
            if not isinstance(metadata, dict):
                fail(f"{project_id} cannot read GitHub repository metadata")
            actual_visibility = str(metadata.get("visibility") or "").lower()
            if actual_visibility != expected_visibility:
                fail(
                    f"{project_id} visibility changed: expected "
                    f"{expected_visibility}, got {actual_visibility or 'unknown'}"
                )
            actual_is_fork = bool(metadata.get("fork"))
            if actual_is_fork != expected_is_fork:
                fail(
                    f"{project_id} fork status changed: expected "
                    f"{expected_is_fork}, got {actual_is_fork}"
                )
            raw_parent = metadata.get("parent")
            actual_parent = (
                raw_parent.get("full_name")
                if isinstance(raw_parent, dict)
                and isinstance(raw_parent.get("full_name"), str)
                else None
            )
            expected_parent = raw_target.get("expected_parent")
            if expected_is_fork:
                if (
                    not isinstance(expected_parent, str)
                    or not REPOSITORY_PATTERN.fullmatch(expected_parent)
                ):
                    fail(f"{project_id} fork target needs expected_parent")
                if (
                    actual_parent is None
                    or actual_parent.casefold() != expected_parent.casefold()
                ):
                    fail(
                        f"{project_id} fork parent changed: expected "
                        f"{expected_parent}, got {actual_parent}"
                    )
            elif expected_parent is not None:
                fail(f"{project_id} non-fork target cannot declare expected_parent")
            branch = validate_line(
                raw_target.get("branch"), f"{project_id} target branch"
            )
            assert branch is not None
            target_label = f"{repository}@{branch}"
            target_key = f"github:{target_label.casefold()}"
            expected_head = raw_target.get("expected_head")
            if operation != "verify" and (
                not isinstance(expected_head, str)
                or not GIT_HASH_PATTERN.fullmatch(expected_head)
            ):
                fail(f"{project_id} GitHub target needs an exact expected_head")
            base_head, base_tree, existing = github_state(repository, branch, paths)
            if operation != "verify" and base_head != expected_head:
                fail(
                    f"{project_id} remote HEAD changed: expected {expected_head}, "
                    f"got {base_head}"
                )
        if target_key in target_ids:
            fail(f"duplicate target in plan: {target_label}")
        target_ids.add(target_key)

        commit_message = validate_line(
            raw_project.get("commit_message"),
            f"{project_id} commit_message",
            required=target_kind == "github" and disposition == "apply",
        )
        check_action_state(target_label, actions, existing, operation)
        prepared.append(
            PreparedProject(
                project_id=project_id,
                disposition=disposition,
                reason=reason,
                target_kind=target_kind,
                target_label=target_label,
                root=root,
                repository=repository,
                branch=branch,
                base_head=base_head,
                base_tree=base_tree,
                expected_result_head=expected_result_head,
                commit_message=commit_message,
                actions=actions,
                existing=existing,
            )
        )
    return prepared


def action_report(action: PlannedAction, existing: dict[str, bytes]) -> dict:
    content = action.rendered.content
    try:
        first_line = content.decode("utf-8").splitlines()[0] if content else ""
    except UnicodeDecodeError:
        first_line = "<binary>"
    report = {
        "path": action.path,
        "action": action.action,
        "source_id": action.rendered.source_id,
        "source_name": action.rendered.source_name,
        "source_url": action.rendered.source_url,
        "source_sha256": action.rendered.source_sha256,
        "rendered_sha256": sha256_bytes(content),
        "rendered_git_blob_sha": git_blob_sha(content),
        "bytes": len(content),
        "first_line": first_line,
        "current_sha256": (
            sha256_bytes(existing[action.path])
            if action.path in existing
            else None
        ),
    }
    if action.action == "replace-preserve":
        report.update(
            expected_sha256=action.expected_sha256,
            preserve_as=action.preserve_as,
        )
    return report


def project_report(project: PreparedProject, status: str) -> dict:
    return {
        "id": project.project_id,
        "target": project.target_label,
        "target_kind": project.target_kind,
        "disposition": project.disposition,
        "reason": project.reason,
        "status": status,
        "base_head": project.base_head,
        "files": [
            action_report(action, project.existing) for action in project.actions
        ],
    }


def write_exclusive(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def replace_file(path: Path, content: bytes) -> None:
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile("wb", dir=path.parent, delete=False) as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            temporary_path = Path(stream.name)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def verify_local_project(
    project: PreparedProject, expected_head: str | None = None
) -> dict:
    assert project.root is not None
    current_head, current = local_state(
        project.root, requested_paths(project.actions)
    )
    if expected_head is not None and current_head != expected_head:
        fail(
            f"{project.target_label} verification HEAD mismatch: expected "
            f"{expected_head}, got {current_head}"
        )
    check_action_state(project.target_label, project.actions, current, "verify")
    return {
        "head": current_head,
        "files": {
            path: sha256_bytes(content) for path, content in sorted(current.items())
        },
    }


def apply_local_project(project: PreparedProject) -> dict:
    assert project.root is not None
    current_head, current = local_state(
        project.root, requested_paths(project.actions)
    )
    if current_head != project.base_head:
        fail(
            f"{project.target_label} changed after preflight: expected HEAD "
            f"{project.base_head}, got {current_head}"
        )
    check_action_state(project.target_label, project.actions, current, "write")
    project.existing = current
    for action in project.actions:
        if action.action == "replace-preserve":
            historical_path = resolve_local_file(project.root, str(action.preserve_as))
            write_exclusive(historical_path, project.existing[action.path])
    for action in project.actions:
        if action.action == "create":
            write_exclusive(
                resolve_local_file(project.root, action.path),
                action.rendered.content,
            )
    for action in project.actions:
        if action.action == "replace-preserve":
            replace_file(
                resolve_local_file(project.root, action.path),
                action.rendered.content,
            )
    return verify_local_project(project)


def create_remote_blob(repository: str, content: bytes) -> str:
    response = gh_api(
        f"repos/{repository}/git/blobs",
        method="POST",
        payload={
            "content": base64.b64encode(content).decode("ascii"),
            "encoding": "base64",
        },
    )
    if not isinstance(response, dict) or not isinstance(response.get("sha"), str):
        fail(f"GitHub did not return a blob SHA for {repository}")
    expected = git_blob_sha(content)
    if response["sha"] != expected:
        fail(
            f"GitHub blob SHA mismatch for {repository}: expected {expected}, "
            f"got {response['sha']}"
        )
    return response["sha"]


def github_license_detection(repository: str, branch: str) -> dict | None:
    response = gh_api(
        f"repos/{repository}/license?ref={quote(branch, safe='')}",
        allow_not_found=True,
    )
    if not isinstance(response, dict):
        return None
    license_info = response.get("license")
    if not isinstance(license_info, dict):
        return None
    return {
        "spdx_id": license_info.get("spdx_id"),
        "name": license_info.get("name"),
        "key": license_info.get("key"),
    }


def verify_remote_project(
    project: PreparedProject, expected_head: str | None = None
) -> dict:
    assert project.repository is not None and project.branch is not None
    head, _, current = github_state(
        project.repository, project.branch, requested_paths(project.actions)
    )
    required_head = expected_head or project.expected_result_head
    if required_head is not None and head != required_head:
        fail(
            f"{project.target_label} verification HEAD mismatch: "
            f"expected {required_head}, got {head}"
        )
    check_action_state(project.target_label, project.actions, current, "verify")
    return {
        "head": head,
        "files": {
            path: {
                "sha256": sha256_bytes(content),
                "git_blob_sha": git_blob_sha(content),
            }
            for path, content in sorted(current.items())
        },
        "github_license_detection": github_license_detection(
            project.repository, project.branch
        ),
    }


def publish_remote_project(project: PreparedProject) -> dict:
    assert (
        project.repository is not None
        and project.branch is not None
        and project.base_head is not None
        and project.base_tree is not None
        and project.commit_message is not None
    )
    current_head, _, _ = github_state(project.repository, project.branch, set())
    if current_head != project.base_head:
        fail(
            f"{project.target_label} changed after preflight: expected "
            f"{project.base_head}, got {current_head}"
        )

    changes: dict[str, bytes] = {}
    for action in project.actions:
        changes[action.path] = action.rendered.content
        if action.action == "replace-preserve":
            changes[str(action.preserve_as)] = project.existing[action.path]
    blob_cache: dict[str, str] = {}
    tree_entries: list[dict[str, str]] = []
    for path, content in sorted(changes.items()):
        content_hash = sha256_bytes(content)
        blob_sha = blob_cache.get(content_hash)
        if blob_sha is None:
            blob_sha = create_remote_blob(project.repository, content)
            blob_cache[content_hash] = blob_sha
        tree_entries.append(
            {
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha,
            }
        )
    tree = gh_api(
        f"repos/{project.repository}/git/trees",
        method="POST",
        payload={"base_tree": project.base_tree, "tree": tree_entries},
    )
    if not isinstance(tree, dict) or not isinstance(tree.get("sha"), str):
        fail(f"GitHub did not return a tree SHA for {project.repository}")
    commit = gh_api(
        f"repos/{project.repository}/git/commits",
        method="POST",
        payload={
            "message": project.commit_message,
            "tree": tree["sha"],
            "parents": [project.base_head],
        },
    )
    if not isinstance(commit, dict) or not isinstance(commit.get("sha"), str):
        fail(f"GitHub did not return a commit SHA for {project.repository}")
    new_head = commit["sha"]
    gh_api(
        f"repos/{project.repository}/git/refs/heads/"
        f"{quote(project.branch, safe='')}",
        method="PATCH",
        payload={"sha": new_head, "force": False},
    )
    verification = verify_remote_project(project, new_head)
    return {
        "commit": new_head,
        "tree": tree["sha"],
        "verification": verification,
    }


def ensure_mode_targets(projects: list[PreparedProject], operation: str) -> None:
    expected_kind = "local" if operation == "write" else "github"
    mismatched = [
        project.target_label
        for project in projects
        if project.disposition == "apply" and project.target_kind != expected_kind
    ]
    if mismatched:
        fail(
            f"--{operation} only accepts {expected_kind} apply targets; mismatched: "
            + ", ".join(mismatched)
        )
