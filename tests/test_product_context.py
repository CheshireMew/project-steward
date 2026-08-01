from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "context.mjs"
NODE = os.environ.get("PROJECT_STEWARD_NODE") or shutil.which("node")


def run_context(cwd: Path, *arguments: str) -> tuple[dict, str]:
    if not NODE:
        raise unittest.SkipTest("Node.js is required for context.mjs tests")
    completed = subprocess.run(
        [NODE, str(SCRIPT), *arguments],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    prefix = "RESOLVED_CONTEXT:\n"
    start = completed.stdout.index(prefix) + len(prefix)
    separator = completed.stdout.find("\n\n---\n\n", start)
    metadata_text = (
        completed.stdout[start:]
        if separator == -1
        else completed.stdout[start:separator]
    )
    return json.loads(metadata_text), completed.stdout


class ProductContextTests(unittest.TestCase):
    def test_parent_git_marker_only_sets_shared_context_boundary(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-context-"
        ) as temporary:
            context_root = Path(temporary)
            (context_root / ".git").mkdir()
            (context_root / "PRODUCT.md").write_text(
                "# Shared product\n", encoding="utf-8"
            )
            project = context_root / "apps" / "editor"
            project.mkdir(parents=True)
            (project / "package.json").write_text(
                '{"name":"editor"}\n', encoding="utf-8"
            )
            (project / "DESIGN.md").write_text(
                "# Editor design\n", encoding="utf-8"
            )

            metadata, output = run_context(
                context_root,
                "--target",
                str(project),
            )

            self.assertEqual(str(project), metadata["projectRoot"])
            self.assertEqual(str(context_root), metadata["contextRoot"])
            self.assertEqual(
                "parent-git-context", metadata["contextRootReason"]
            )
            self.assertFalse(metadata["contextRootGrantsGitCapability"])
            self.assertNotIn("repoRoot", metadata)
            self.assertEqual("project", metadata["designScope"])
            self.assertEqual(
                "shared-context-fallback", metadata["productScope"]
            )
            self.assertIn("# Shared product", output)
            self.assertIn("# Editor design", output)

    def test_missing_context_is_reported_without_creating_files(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-no-context-"
        ) as temporary:
            project = Path(temporary)
            (project / "package.json").write_text(
                '{"name":"plain"}\n', encoding="utf-8"
            )

            metadata, output = run_context(project)

            self.assertEqual(str(project), metadata["projectRoot"])
            self.assertEqual(str(project), metadata["contextRoot"])
            self.assertEqual("task-context", metadata["contextRootReason"])
            self.assertIn("NO_PROJECT_CONTEXT", output)
            self.assertFalse((project / "DESIGN.md").exists())
            self.assertFalse((project / "PRODUCT.md").exists())


if __name__ == "__main__":
    unittest.main()
