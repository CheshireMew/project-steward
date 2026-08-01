from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "inventory_repository.py"


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


class LocalInventoryTests(unittest.TestCase):
    def test_cli_inventories_real_git_producer_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-inventory-") as temporary:
            root = Path(temporary)
            repository = root / "sample"
            repository.mkdir()
            run(["git", "init", "-b", "audit-root"], repository)
            run(["git", "config", "user.name", "Project Steward Test"], repository)
            run(
                ["git", "config", "user.email", "project-steward@example.invalid"],
                repository,
            )

            (repository / "src").mkdir()
            (repository / "assets").mkdir()
            (repository / "data").mkdir()
            (repository / "vendor" / "dependency").mkdir(parents=True)
            (repository / "README.md").write_text(
                "# Sample\n\nA real inventory fixture.\n", encoding="utf-8"
            )
            (repository / "LICENSING.md").write_text(
                "# Licensing\n\nScope truth.\n", encoding="utf-8"
            )
            (repository / "src" / "app.py").write_text(
                "print('sample')\n", encoding="utf-8"
            )
            (repository / "assets" / "logo.svg").write_text(
                "<svg xmlns=\"http://www.w3.org/2000/svg\"/>\n", encoding="utf-8"
            )
            (repository / "data" / "sample.csv").write_text(
                "value\n1\n", encoding="utf-8"
            )
            (repository / "vendor" / "dependency" / "LICENSE").write_text(
                "Dependency license\n", encoding="utf-8"
            )
            run(["git", "add", "."], repository)
            run(["git", "commit", "-m", "test: create inventory fixture"], repository)

            completed = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "local",
                    str(repository),
                    "--compact",
                ],
                root,
            )
            inventory = json.loads(completed.stdout)
            self.assertEqual(2, inventory["schema_version"])
            self.assertEqual("local", inventory["source"]["kind"])
            self.assertEqual(1, inventory["repository_count"])
            record = inventory["repositories"][0]
            self.assertEqual("audit-root", record["repository"]["current_branch"])
            self.assertEqual("audit-root", record["repository"]["default_branch"])
            self.assertEqual(
                "current-branch", record["repository"]["default_branch_source"]
            )
            self.assertEqual(["LICENSING.md"], record["licensing_scope_files"])
            self.assertIn(
                "vendor/dependency/LICENSE", record["license_and_notice_files"]
            )
            self.assertGreaterEqual(record["content_counts"]["code"], 1)
            self.assertGreaterEqual(record["content_counts"]["data"], 1)
            self.assertGreaterEqual(record["content_counts"]["media"], 1)
            signal_kinds = {
                signal["kind"] for signal in record["review_signals"]
            }
            self.assertIn("third_party_directories", signal_kinds)
            self.assertIn("nested_license_files", signal_kinds)

    def test_removed_positional_cli_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-inventory-cli-") as temporary:
            root = Path(temporary)
            completed = run(
                [sys.executable, str(SCRIPT), str(root)],
                root,
                check=False,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("invalid choice", completed.stderr)


if __name__ == "__main__":
    unittest.main()
