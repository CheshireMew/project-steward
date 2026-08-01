from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "apply_license.py"
CATALOG_ROOT = SKILL_ROOT / "assets" / "licenses"


def run(command: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def initialize_repository(repository: Path, old_license: bytes) -> str:
    repository.mkdir()
    run(["git", "init", "-b", "legacy"], repository)
    run(["git", "config", "user.name", "Project Steward Test"], repository)
    run(
        ["git", "config", "user.email", "project-steward@example.invalid"],
        repository,
    )
    (repository / "LICENSE").write_bytes(old_license)
    (repository / "README.md").write_text("# Fixture\n", encoding="utf-8")
    run(["git", "add", "."], repository)
    run(["git", "commit", "-m", "test: publish old license"], repository)
    return run(["git", "rev-parse", "HEAD"], repository).stdout.strip()


def approved_plan(repository: Path, old_license: bytes, head: str) -> dict:
    return {
        "schema_version": 2,
        "projects": [
            {
                "id": "fixture",
                "disposition": "apply",
                "reason": "The approved fixture migrates from MIT to MPL.",
                "target": {
                    "kind": "local",
                    "path": str(repository),
                    "expected_head": head,
                },
                "project_name": "Fixture",
                "year": "2026",
                "copyright_holder": "Project Steward Test",
                "commit_message": "docs: establish licensing",
                "files": [
                    {
                        "path": "LICENSE",
                        "action": "replace-preserve",
                        "expected_sha256": sha256(old_license),
                        "preserve_as": "LICENSE-MIT-HISTORICAL",
                        "source": {
                            "kind": "catalog-license",
                            "id": "MPL-2.0",
                        },
                    },
                    {
                        "path": "NOTICE",
                        "action": "create",
                        "source": {
                            "kind": "catalog-notice",
                            "id": "MPL-2.0-Notice",
                        },
                    },
                    {
                        "path": "LICENSING.md",
                        "action": "create",
                        "source": {
                            "kind": "text",
                            "id": "approved-scope-map",
                            "content": (
                                "# Licensing\n\n"
                                "Current code: MPL-2.0 in `LICENSE`.\n\n"
                                "Historical releases through the recorded base commit "
                                "remain under `LICENSE-MIT-HISTORICAL`.\n"
                            ),
                        },
                    },
                ],
            }
        ],
    }


class ApplyLicenseTests(unittest.TestCase):
    def test_dry_run_write_verify_commit_push_and_clone_consumer(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-rollout-") as temporary:
            root = Path(temporary)
            repository = root / "producer"
            old_license = b"MIT License\r\n\r\nCopyright (c) 2024 Fixture\r\n"
            base_head = initialize_repository(repository, old_license)
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps(
                    approved_plan(repository, old_license, base_head),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            preview = run(
                [sys.executable, str(SCRIPT), "--plan", str(plan_path)],
                root,
            )
            preview_data = json.loads(preview.stdout)
            self.assertEqual("dry-run", preview_data["mode"])
            self.assertEqual("passed", preview_data["preflight"])
            self.assertEqual("ready", preview_data["projects"][0]["status"])
            self.assertFalse((repository / "NOTICE").exists())

            written = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--plan",
                    str(plan_path),
                    "--write",
                ],
                root,
            )
            written_data = json.loads(written.stdout)
            self.assertEqual("written", written_data["mode"])
            self.assertEqual("written", written_data["projects"][0]["status"])
            self.assertEqual(
                old_license,
                (repository / "LICENSE-MIT-HISTORICAL").read_bytes(),
            )
            self.assertEqual(
                (CATALOG_ROOT / "MPL-2.0.txt").read_bytes(),
                (repository / "LICENSE").read_bytes(),
            )
            notice = (repository / "NOTICE").read_text(encoding="utf-8")
            self.assertIn("Fixture", notice)
            self.assertIn("Project Steward Test", notice)
            self.assertNotIn("{{", notice)

            verified = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--plan",
                    str(plan_path),
                    "--verify",
                ],
                root,
            )
            verified_data = json.loads(verified.stdout)
            self.assertEqual("verified", verified_data["mode"])
            self.assertEqual("verified", verified_data["projects"][0]["status"])

            run(["git", "add", "."], repository)
            run(["git", "commit", "-m", "docs: establish licensing"], repository)
            remote = root / "remote.git"
            run(["git", "init", "--bare", str(remote)], root)
            run(["git", "remote", "add", "origin", str(remote)], repository)
            run(["git", "push", "-u", "origin", "legacy"], repository)
            consumer = root / "consumer"
            run(
                [
                    "git",
                    "clone",
                    "--branch",
                    "legacy",
                    str(remote),
                    str(consumer),
                ],
                root,
            )
            self.assertEqual(
                old_license.decode("utf-8").replace("\r\n", "\n"),
                (consumer / "LICENSE-MIT-HISTORICAL")
                .read_text(encoding="utf-8")
                .replace("\r\n", "\n"),
            )
            self.assertEqual(
                (repository / "LICENSE")
                .read_text(encoding="utf-8")
                .replace("\r\n", "\n"),
                (consumer / "LICENSE")
                .read_text(encoding="utf-8")
                .replace("\r\n", "\n"),
            )
            self.assertIn(
                "Current code: MPL-2.0",
                (consumer / "LICENSING.md").read_text(encoding="utf-8"),
            )

    def test_full_preflight_prevents_partial_local_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-preflight-") as temporary:
            root = Path(temporary)
            repository = root / "producer"
            old_license = b"Existing license\n"
            base_head = initialize_repository(repository, old_license)
            plan = approved_plan(repository, old_license, base_head)
            files = plan["projects"][0]["files"]
            files[0] = {
                "path": "LICENSE",
                "action": "create",
                "source": {"kind": "catalog-license", "id": "MPL-2.0"},
            }
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            completed = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--plan",
                    str(plan_path),
                    "--write",
                ],
                root,
                check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("create target already exists", completed.stderr)
            self.assertFalse((repository / "NOTICE").exists())
            self.assertFalse((repository / "LICENSING.md").exists())
            self.assertEqual(old_license, (repository / "LICENSE").read_bytes())

    def test_schema_v1_has_no_compatibility_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-schema-") as temporary:
            root = Path(temporary)
            plan_path = root / "plan.json"
            plan_path.write_text(
                json.dumps({"schema_version": 1, "licenses": []}),
                encoding="utf-8",
            )
            completed = run(
                [sys.executable, str(SCRIPT), "--plan", str(plan_path)],
                root,
                check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("schema_version must be 2", completed.stderr)

    def test_gnu_license_requires_matching_project_notice(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-gnu-") as temporary:
            root = Path(temporary)
            repository = root / "producer"
            repository.mkdir()
            plan = {
                "schema_version": 2,
                "projects": [
                    {
                        "id": "gnu-fixture",
                        "disposition": "apply",
                        "reason": "Exercise the explicit GNU version boundary.",
                        "target": {"kind": "local", "path": str(repository)},
                        "project_name": "GNU Fixture",
                        "year": "2026",
                        "copyright_holder": "Project Steward Test",
                        "files": [
                            {
                                "path": "LICENSE",
                                "action": "create",
                                "source": {
                                    "kind": "catalog-license",
                                    "id": "AGPL-3.0-or-later",
                                },
                            }
                        ],
                    }
                ],
            }
            plan_path = root / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            completed = run(
                [sys.executable, str(SCRIPT), "--plan", str(plan_path)],
                root,
                check=False,
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("require matching gnu-notice", completed.stderr)
            self.assertFalse((repository / "LICENSE").exists())


if __name__ == "__main__":
    unittest.main()
