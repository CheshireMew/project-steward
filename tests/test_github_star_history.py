from __future__ import annotations

import base64
import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "github_star_history.py"
SPEC = importlib.util.spec_from_file_location("github_star_history", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
STAR_HISTORY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = STAR_HISTORY
SPEC.loader.exec_module(STAR_HISTORY)

SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
REFERENCE_TEXT = (SKILL_ROOT / "references" / "github-star-history.md").read_text(
    encoding="utf-8"
)
ACTION_TEXT = (
    SKILL_ROOT / ".github" / "actions" / "star-history" / "action.yml"
).read_text(encoding="utf-8")
WORKFLOW_TEXT = (
    SKILL_ROOT / ".github" / "workflows" / "star-history.yml"
).read_text(encoding="utf-8")


class MatchingFilesClient:
    def __init__(self, light: bytes, dark: bytes) -> None:
        self.light = light
        self.dark = dark
        self.calls = []

    def request(self, method, path, **kwargs):
        self.calls.append((method, path))
        if path.endswith("/git/ref/heads/star-history"):
            return {"object": {"sha": "existing-commit"}}, {}, 200
        if "/contents/star-history.svg?" in path:
            return {
                "encoding": "base64",
                "content": base64.b64encode(self.light).decode("ascii"),
            }, {}, 200
        if "/contents/star-history-dark.svg?" in path:
            return {
                "encoding": "base64",
                "content": base64.b64encode(self.dark).decode("ascii"),
            }, {}, 200
        raise AssertionError("unexpected request: {} {}".format(method, path))


class GitHubStarHistoryTests(unittest.TestCase):
    def make_snapshot(self):
        return STAR_HISTORY.StarSnapshot(
            repository="CheshireMew/example",
            created_on=date(2024, 1, 1),
            star_dates=(
                date(2024, 1, 2),
                date(2024, 1, 2),
                date(2024, 2, 20),
            ),
        )

    def test_renderer_is_deterministic_valid_and_theme_specific(self) -> None:
        snapshot = self.make_snapshot()
        light = STAR_HISTORY.render_svg(snapshot, "light")
        dark = STAR_HISTORY.render_svg(snapshot, "dark")

        self.assertEqual(light, STAR_HISTORY.render_svg(snapshot, "light"))
        ET.fromstring(light)
        ET.fromstring(dark)
        self.assertIn("Total: 3", light)
        self.assertIn("#ffffff", light)
        self.assertIn("#0d1117", dark)
        self.assertNotEqual(light, dark)

    def test_zero_star_repository_still_has_a_complete_chart(self) -> None:
        snapshot = STAR_HISTORY.StarSnapshot(
            repository="CheshireMew/new-repository",
            created_on=date(2026, 7, 31),
            star_dates=(),
        )
        rendered = STAR_HISTORY.render_svg(snapshot, "light")

        ET.fromstring(rendered)
        self.assertIn("Total: 0", rendered)
        self.assertIn(">0</text>", rendered)
        self.assertNotIn("<circle", rendered)

    def test_matching_outputs_do_not_create_a_commit(self) -> None:
        snapshot = self.make_snapshot()
        light = STAR_HISTORY.render_svg(snapshot, "light").encode("utf-8")
        dark = STAR_HISTORY.render_svg(snapshot, "dark").encode("utf-8")
        client = MatchingFilesClient(light, dark)

        result = STAR_HISTORY.publish_snapshot(
            client,
            snapshot,
            branch="star-history",
            light_path="star-history.svg",
            dark_path="star-history-dark.svg",
            commit_message="test",
        )

        self.assertFalse(result.changed)
        self.assertEqual(result.star_count, 3)
        self.assertEqual(len(client.calls), 3)
        self.assertTrue(all(method == "GET" for method, _ in client.calls))

    def test_skill_routes_diagnosis_and_implementation_to_one_reference(self) -> None:
        readme_section = SKILL_TEXT.split("### 11. README 与主页", 1)[1].split(
            "### 12.", 1
        )[0]
        self.assertIn("references/github-star-history.md", readme_section)
        self.assertIn("只读", readme_section)
        self.assertIn("真实链路", readme_section)
        self.assertIn("github.token", REFERENCE_TEXT)
        self.assertIn("60", REFERENCE_TEXT)

    def test_public_workflow_keeps_credentials_in_the_caller_boundary(self) -> None:
        combined = ACTION_TEXT + "\n" + WORKFLOW_TEXT
        self.assertIn("${{ github.token }}", WORKFLOW_TEXT)
        self.assertIn("contents: write", WORKFLOW_TEXT)
        self.assertIn("scripts/github_star_history.py", ACTION_TEXT)
        self.assertNotIn("api.star-history.com", combined)
        self.assertNotIn("personal access token", combined.lower())


if __name__ == "__main__":
    unittest.main()
