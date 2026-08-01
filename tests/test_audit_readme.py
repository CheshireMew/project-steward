from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "audit_readme.py"


def run(
    command: list[str], cwd: Path, *, check: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class ReadmeAuditTests(unittest.TestCase):
    def test_real_readme_reference_is_resolved_and_svg_is_consumed(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-"
        ) as temporary:
            root = Path(temporary)
            assets = root / "assets" / "readme"
            assets.mkdir(parents=True)
            readme = root / "README.md"
            svg = assets / "hero.svg"
            readme.write_text(
                (
                    "# Fixture\n\n"
                    '<img src="./assets/readme/hero.svg" '
                    'alt="Fixture result and workflow">\n'
                ),
                encoding="utf-8",
            )
            svg.write_text(
                (
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'viewBox="0 0 1200 320">'
                    "<title>Fixture result</title>"
                    '<rect width="1200" height="320"/>'
                    "</svg>\n"
                ),
                encoding="utf-8",
            )

            completed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
            )
            self.assertIn("Local images checked: 1", completed.stdout)
            self.assertIn("Scope: structural checks only", completed.stdout)
            self.assertIn("source currency", completed.stdout)
            self.assertIn("factual accuracy", completed.stdout)
            self.assertIn("visual relevance", completed.stdout)
            self.assertIn("rendered quality are not evaluated", completed.stdout)
            self.assertIn(
                "OK: structural image reference and SVG checks passed",
                completed.stdout,
            )

            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"></svg>\n',
                encoding="utf-8",
            )
            failed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
                check=False,
            )
            self.assertEqual(1, failed.returncode)
            self.assertIn("missing viewBox", failed.stdout)
            self.assertIn("missing <title>", failed.stdout)

            svg.write_text(
                (
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'viewBox="0 0 1200 320">'
                    "<title>Fixture result</title>"
                    "</svg>\n"
                ),
                encoding="utf-8",
            )
            readme.write_text(
                "# Fixture\n\n![](./assets/readme/hero.svg)\n",
                encoding="utf-8",
            )
            missing_alt = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
                check=False,
            )
            self.assertEqual(1, missing_alt.returncode)
            self.assertIn(
                "Markdown image missing useful alt text",
                missing_alt.stdout,
            )


if __name__ == "__main__":
    unittest.main()
