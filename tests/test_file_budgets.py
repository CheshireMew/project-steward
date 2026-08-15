from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_file_budgets import (
    BYTES_PER_OUTER_TOOL_TOKEN,
    MAX_OUTER_TOOL_TOKENS,
    collect_file_budgets,
    estimate_outer_tool_tokens,
    validate_file_budgets,
)


class FileBudgetTests(unittest.TestCase):
    def test_estimate_rounds_utf8_bytes_up(self) -> None:
        self.assertEqual(estimate_outer_tool_tokens(0), 0)
        self.assertEqual(estimate_outer_tool_tokens(1), 1)
        self.assertEqual(estimate_outer_tool_tokens(4), 1)
        self.assertEqual(estimate_outer_tool_tokens(5), 2)

    def test_exact_limit_passes_and_one_more_byte_fails(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            exact_size = MAX_OUTER_TOOL_TOKENS * BYTES_PER_OUTER_TOOL_TOKEN
            target = root / "reference.md"
            target.write_bytes(b"a" * exact_size)
            self.assertEqual(validate_file_budgets(root), [])

            target.write_bytes(b"a" * (exact_size + 1))
            errors = validate_file_budgets(root)

        self.assertEqual(len(errors), 1)
        self.assertIn("reference.md", errors[0])
        self.assertIn("9001 estimated tokens", errors[0])

    def test_inactive_directories_and_binary_assets_are_excluded(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for relative_path in (
                "archive/old.md",
                "artifacts/runtime.txt",
                "node_modules/dependency.md",
                "assets/preview.png",
            ):
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("inactive", encoding="utf-8")

            records = collect_file_budgets(root)

        self.assertEqual(records, [])

    def test_active_text_and_model_readable_assets_are_budgeted(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            expected = (root / "SKILL.md", root / "assets" / "catalog.json")
            for path in expected:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("active", encoding="utf-8")
            (root / "binary.dat").write_bytes(b"\xff\xfe")

            records = collect_file_budgets(root)

        self.assertEqual(
            [record.path.as_posix() for record in records],
            ["SKILL.md", "assets/catalog.json"],
        )


if __name__ == "__main__":
    unittest.main()
