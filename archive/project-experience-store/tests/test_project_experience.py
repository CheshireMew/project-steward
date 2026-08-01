"""Archived regression suite for the inactive experience-store implementation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "project_experience.py"
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
README_TEXT = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
NOTICES_TEXT = (SKILL_ROOT / "THIRD_PARTY_NOTICES.md").read_text(
    encoding="utf-8"
)


class ProjectExperienceTests(unittest.TestCase):
    def run_cli(
        self,
        *arguments: object,
        expected_code: int = 0,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object] | None]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *(str(item) for item in arguments)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(
            expected_code,
            completed.returncode,
            msg=f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}",
        )
        payload = (
            json.loads(completed.stdout)
            if completed.stdout.strip()
            else None
        )
        return completed, payload

    def test_project_a_promotes_and_project_b_consumes_real_body(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_a = root / "project-a"
            project_b = root / "project-b"
            project_a.mkdir()
            project_b.mkdir()
            store = root / "shared-experience"
            config = root / "config" / "project-steward.json"

            self.run_cli(
                "configure",
                "--store",
                store,
                "--config",
                config,
            )
            self.run_cli(
                "init",
                project_a,
                "--project-id",
                "project-a",
                "--project-name",
                "Project A",
            )
            self.run_cli(
                "init",
                project_b,
                "--project-id",
                "project-b",
                "--project-name",
                "Project B",
            )

            project_body = root / "project-body.md"
            project_body.write_text(
                "# Export truth\n\n"
                "Project A exports the original file, while preview data "
                "remains display-only.\n",
                encoding="utf-8",
            )
            self.run_cli(
                "upsert",
                project_a,
                "--topic",
                "export-source",
                "--title",
                "Export source",
                "--summary",
                "Exports use original content instead of preview data.",
                "--applicability",
                "projects with derived previews and file export",
                "--tag",
                "export",
                "--status",
                "validated",
                "--evidence",
                "A real export reopened with the original bytes.",
                "--body-file",
                project_body,
                "--change-note",
                "Verified after replacing the preview-backed export.",
            )

            shared_body = root / "shared-body.md"
            first_shared_text = (
                "# Keep display data out of export truth\n\n"
                "When a product derives a preview from source content, "
                "export reads the original content boundary. The preview "
                "exists only for display.\n"
            )
            shared_body.write_text(first_shared_text, encoding="utf-8")
            self.run_cli(
                "promote",
                project_a,
                "--topic",
                "export-source",
                "--shared-id",
                "original-content-for-export",
                "--title",
                "Export from original content",
                "--summary",
                "Derived previews do not become the source for export.",
                "--applicability",
                "projects with source content, previews, and export",
                "--tag",
                "export",
                "--stage",
                "registered",
                "--body-file",
                shared_body,
                "--confirmed-by",
                "user",
                "--change-note",
                "Promoted the verified boundary for cross-project use.",
                "--config",
                config,
            )

            _, search = self.run_cli(
                "search",
                project_b,
                "--query",
                "batch export preview original content",
                "--config",
                config,
            )
            assert search is not None
            results = search["results"]
            self.assertEqual(1, len(results))
            result = results[0]
            self.assertEqual("shared", result["source"])
            self.assertEqual("original-content-for-export", result["id"])
            self.assertEqual(first_shared_text, result["body"])
            self.assertEqual(1, result["revision"])

            self.run_cli(
                "adopt",
                project_b,
                "--shared-id",
                "original-content-for-export",
                "--expected-revision",
                "1",
                "--outcome",
                "adopted",
                "--applied-to",
                "the source boundary for batch export",
                "--decision",
                "Batch export reads original files; preview records stay UI-only.",
                "--confirmed-by",
                "user",
                "--config",
                config,
            )

            _, verify_a = self.run_cli(
                "verify",
                project_a,
                "--config",
                config,
            )
            _, verify_b = self.run_cli(
                "verify",
                project_b,
                "--config",
                config,
            )
            assert verify_a is not None and verify_b is not None
            self.assertEqual("passed", verify_a["status"])
            self.assertEqual("passed", verify_b["status"])

            project_body.write_text(
                "# Export truth\n\n"
                "Project A exports original files and records the source "
                "revision used for every batch.\n",
                encoding="utf-8",
            )
            self.run_cli(
                "upsert",
                project_a,
                "--topic",
                "export-source",
                "--title",
                "Export source",
                "--summary",
                "Exports use original content and identify its revision.",
                "--applicability",
                "projects with derived previews and file export",
                "--tag",
                "export",
                "--status",
                "validated",
                "--evidence",
                "A real batch export recorded and reopened source revisions.",
                "--body-file",
                project_body,
                "--change-note",
                "A later batch workflow proved revision identity is required.",
                "--expected-revision",
                "1",
            )
            second_shared_text = (
                "# Keep display data out of export truth\n\n"
                "Export reads original content and records the source revision. "
                "Derived previews remain display-only.\n"
            )
            shared_body.write_text(second_shared_text, encoding="utf-8")
            self.run_cli(
                "promote",
                project_a,
                "--topic",
                "export-source",
                "--shared-id",
                "original-content-for-export",
                "--title",
                "Export from identified original content",
                "--summary",
                "Export uses original content and identifies its revision.",
                "--applicability",
                "projects with source content, previews, and export",
                "--tag",
                "export",
                "--stage",
                "registered",
                "--body-file",
                shared_body,
                "--confirmed-by",
                "user",
                "--change-note",
                "Revalidated and added source revision identity.",
                "--expected-revision",
                "1",
                "--config",
                config,
            )

            shared_catalog = json.loads(
                (store / "catalog.json").read_text(encoding="utf-8")
            )
            self.assertEqual(1, len(shared_catalog["notes"]))
            note = shared_catalog["notes"][0]
            self.assertEqual(2, note["revision"])
            self.assertEqual(1, len(note["sources"]))
            self.assertEqual(1, len(note["validations"]))

            _, second_search = self.run_cli(
                "search",
                project_b,
                "--query",
                "batch export original source revision preview",
                "--config",
                config,
            )
            assert second_search is not None
            updated = second_search["results"][0]
            self.assertEqual(2, updated["revision"])
            self.assertEqual(second_shared_text, updated["body"])

            retired_text = (
                "# Retired\n\n"
                "Later evidence showed that this boundary is replaced by a "
                "different source contract. Keep this note for provenance.\n"
            )
            shared_body.write_text(retired_text, encoding="utf-8")
            self.run_cli(
                "promote",
                project_a,
                "--topic",
                "export-source",
                "--shared-id",
                "original-content-for-export",
                "--title",
                "Export from identified original content",
                "--summary",
                "Retired after the source contract changed.",
                "--applicability",
                "projects with source content, previews, and export",
                "--tag",
                "export",
                "--stage",
                "retired",
                "--body-file",
                shared_body,
                "--confirmed-by",
                "user",
                "--change-note",
                "Retired after verified replacement by another source contract.",
                "--expected-revision",
                "2",
                "--config",
                config,
            )
            _, hidden_search = self.run_cli(
                "search",
                project_b,
                "--query",
                "original-content-for-export",
                "--config",
                config,
            )
            assert hidden_search is not None
            self.assertEqual([], hidden_search["results"])
            _, retired_verify = self.run_cli(
                "verify",
                project_b,
                "--config",
                config,
            )
            assert retired_verify is not None
            self.assertEqual("passed", retired_verify["status"])

            _, upgrade = self.run_cli(
                "upgrade",
                project_b,
                "--config",
                config,
            )
            assert upgrade is not None
            self.assertEqual("current", upgrade["status"])
            self.assertEqual([], upgrade["changes"])

    def test_branch_closure_resolves_every_declared_target(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            store = root / "shared"
            config = root / "config.json"
            body = root / "body.md"
            body.write_text("A validated current conclusion.\n", encoding="utf-8")

            self.run_cli(
                "configure",
                "--store",
                store,
                "--config",
                config,
            )
            self.run_cli(
                "init",
                project,
                "--project-id",
                "closure-project",
            )
            self.run_cli(
                "upsert",
                project,
                "--topic",
                "stable-boundary",
                "--title",
                "Stable boundary",
                "--summary",
                "The current project boundary is established.",
                "--applicability",
                "this project",
                "--status",
                "validated",
                "--evidence",
                "The formal consumer read the produced result.",
                "--body-file",
                body,
                "--change-note",
                "Established during the exploration.",
            )
            self.run_cli(
                "promote",
                project,
                "--topic",
                "stable-boundary",
                "--shared-id",
                "formal-consumer-boundary",
                "--title",
                "Verify the formal consumer boundary",
                "--summary",
                "A result is complete when its formal consumer reads it.",
                "--applicability",
                "cross-layer changes",
                "--stage",
                "registered",
                "--body-file",
                body,
                "--confirmed-by",
                "user",
                "--change-note",
                "Confirmed as reusable.",
                "--config",
                config,
            )

            plan = root / "closure.json"
            plan.write_text(
                json.dumps(
                    {
                        "summary": "Kept the validated boundary and discarded "
                        "the abandoned adapter.",
                        "items": [
                            {
                                "label": "Current project boundary",
                                "disposition": "project-current",
                                "reason": "It remains the project truth.",
                                "target_id": "stable-boundary",
                            },
                            {
                                "label": "Reusable consumer rule",
                                "disposition": "shared-registered",
                                "reason": "It applies beyond this project.",
                                "target_id": "formal-consumer-boundary",
                            },
                            {
                                "label": "Abandoned adapter",
                                "disposition": "discarded",
                                "reason": "It produced no lasting conclusion.",
                            },
                            {
                                "label": "Raw benchmark",
                                "disposition": "history-pointer",
                                "reason": "It is useful only as source evidence.",
                                "pointer": "docs/benchmark-notes.md",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            _, closure = self.run_cli(
                "close-branch",
                project,
                "--work-id",
                "exploration-formal-boundary",
                "--plan-file",
                plan,
                "--confirmed-by",
                "user",
                "--config",
                config,
            )
            assert closure is not None
            self.assertEqual("recorded", closure["status"])
            self.assertEqual(1, closure["dispositions"]["discarded"])
            self.assertEqual(1, closure["dispositions"]["project-current"])
            self.assertEqual(
                1,
                closure["dispositions"]["shared-registered"],
            )
            self.assertEqual(1, closure["dispositions"]["history-pointer"])

            completed, _ = self.run_cli(
                "close-branch",
                project,
                "--work-id",
                "exploration-formal-boundary",
                "--plan-file",
                plan,
                "--confirmed-by",
                "user",
                "--config",
                config,
                expected_code=2,
            )
            self.assertIn("already recorded", completed.stderr)

    def test_new_resources_are_owned_by_the_main_router(self) -> None:
        for name in (
            "project-experience-continuity.md",
            "branch-experience-closure.md",
            "experience-store-upgrades.md",
        ):
            with self.subTest(name=name):
                path = SKILL_ROOT / "references" / name
                self.assertTrue(path.is_file())
                self.assertIn(f"references/{name}", SKILL_TEXT)
                self.assertNotIn("references/", path.read_text(encoding="utf-8"))
        self.assertIn("scripts/project_experience.py", SKILL_TEXT)

    def test_project_cairn_method_is_credited_with_exact_scope(self) -> None:
        source = "https://github.com/iBlinkQ/project-cairn"
        self.assertIn(source, README_TEXT)
        self.assertIn(source, NOTICES_TEXT)
        self.assertIn("Copyright (c) 2026 iBlinkQ", NOTICES_TEXT)
        self.assertIn("scripts/project_experience.py", NOTICES_TEXT)
        self.assertIn("roadmap and per-progress logging", NOTICES_TEXT)


if __name__ == "__main__":
    unittest.main()
